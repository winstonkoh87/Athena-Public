"""
athena.core.taint
=================

Monotonic inbound taint quarantine for untrusted external inputs.

Once a session ingests untrusted input (emails, external URLs, attachments),
marking the session tainted persists monotonically until explicitly cleared
with human confirmation or a fresh session begins. While tainted:
- Durable memory writes (`append_checkpoint`, `quicksave`, `shutdown` learnings,
  and protected memory edits via `block_tainted_memory.py`) fail closed.
- `context_gate` suppresses personal profile recall (`include_personal=False`,
  `personalisation=None`, `user_state=None`) to prevent indirect injection
  exfiltration or persistence.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from athena.core import config
from athena.memory.learnings import atomic_write_text

logger = logging.getLogger(__name__)

_ENV_TRUTHY = frozenset({"1", "true", "yes", "on"})

PROTECTED_MEMORY_FILENAMES = frozenset(
    {
        "CANONICAL.md",
        "CANONICAL_TIER2.md",
        "CANONICAL_TIER3.md",
        "userContext.md",
        "User_Profile_Core.md",
        "USER_PROFILE.yaml",
        "SYSTEM_LEARNINGS.md",
        "decisionLog.md",
        "activeContext.md",
    }
)

PROTECTED_MEMORY_SEGMENTS = (
    ".context/memories/session_logs/",
    ".athena/memory/",
)


class TaintBlockedError(PermissionError):
    """Raised when a durable memory operation is attempted under taint quarantine."""


def _resolve_taint_path(project_root: Path | None = None) -> Path:
    env_override = (os.environ.get("ATHENA_TAINT_STATE_PATH") or "").strip()
    if env_override:
        return Path(env_override)
    base = Path(project_root) if project_root is not None else config.PROJECT_ROOT
    return base / ".athena" / "runtime" / "taint_state.json"


def _resolve_session_id(session_id: str | None = None) -> str:
    sid = (session_id or os.environ.get("ATHENA_SESSION_ID") or "active").strip()
    return sid or "active"


def _load_taint_state(path: Path) -> tuple[dict[str, Any], bool]:
    """Return `(state_dict, is_corrupt)`. Missing file returns empty clean state."""
    if not path.exists():
        return {"sessions": {}}, False
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}, True
        sessions = data.get("sessions")
        if sessions is None:
            data = {**data, "sessions": {}}
        elif not isinstance(sessions, dict):
            return {}, True
        return data, False
    except (OSError, ValueError, TypeError) as exc:
        logger.warning("Taint state file %s unreadable/corrupt: %s", path, exc)
        return {}, True


def mark_tainted(
    source: str,
    reason: str = "untrusted_input",
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Monotonically mark a session tainted and persist state with 0600 permissions."""
    sid = _resolve_session_id(session_id)
    state_path = _resolve_taint_path(project_root)
    state, is_corrupt = _load_taint_state(state_path)
    if is_corrupt or not isinstance(state.get("sessions"), dict):
        logger.warning("Resetting corrupt taint state container at %s during mark_tainted", state_path)
        state = {"sessions": {}}

    sessions: dict[str, Any] = dict(state["sessions"])
    existing = sessions.get(sid)
    if not isinstance(existing, dict):
        existing = {}
    sources = list(existing.get("sources") or [])
    now_iso = datetime.now(timezone.utc).isoformat()
    sources.append(
        {
            "source": str(source or "unknown").strip() or "unknown",
            "reason": str(reason or "untrusted_input").strip() or "untrusted_input",
            "at": now_iso,
        }
    )
    entry = {
        "tainted": True,
        "session_id": sid,
        "first_tainted_at": existing.get("first_tainted_at") or now_iso,
        "updated_at": now_iso,
        "sources": sources,
    }
    sessions[sid] = entry
    state["sessions"] = sessions
    atomic_write_text(state_path, json.dumps(state, indent=2, sort_keys=True) + "\n", mode=0o600)
    return entry


def get_taint_status(
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Return current session taint quarantine status (fail-closed on corrupt state)."""
    sid = _resolve_session_id(session_id)
    env_raw = (os.environ.get("ATHENA_TAINTED") or "").strip().lower()
    env_override = env_raw in _ENV_TRUTHY

    state_path = _resolve_taint_path(project_root)
    state, is_corrupt = _load_taint_state(state_path)
    if is_corrupt:
        sources = [{"source": "state_file", "reason": "corrupt_taint_state_fail_closed"}]
        if env_override:
            sources.append({"source": "env:ATHENA_TAINTED", "reason": "env_override"})
        return {
            "tainted": True,
            "session_id": sid,
            "sources": sources,
            "env_override": env_override,
            "state_path": str(state_path),
        }

    sessions = state.get("sessions") or {}
    entry = sessions.get(sid) if isinstance(sessions, dict) else None
    persisted_tainted = isinstance(entry, dict) and bool(entry.get("tainted"))
    sources = list(entry.get("sources") or []) if isinstance(entry, dict) else []
    if env_override:
        sources.append({"source": "env:ATHENA_TAINTED", "reason": "env_override"})

    return {
        "tainted": bool(env_override or persisted_tainted),
        "session_id": sid,
        "sources": sources,
        "env_override": env_override,
        "state_path": str(state_path),
    }


def is_tainted(
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> bool:
    """Return True if the session is currently under monotonic taint quarantine."""
    return bool(get_taint_status(session_id=session_id, project_root=project_root)["tainted"])


def assert_untainted(
    operation: str,
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> None:
    """Raise TaintBlockedError if session is tainted."""
    status = get_taint_status(session_id=session_id, project_root=project_root)
    if status["tainted"]:
        reasons = ", ".join(
            f"{s.get('source', 'unknown')}:{s.get('reason', 'tainted')}"
            for s in status.get("sources", [])[:3]
        ) or "untrusted_input"
        raise TaintBlockedError(
            f"Operation '{operation}' blocked: session '{status['session_id']}' "
            f"is under monotonic taint quarantine ({reasons})."
        )


def clear_taint(
    *,
    human_confirm: bool = False,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> bool:
    """Clear monotonic session taint only when human_confirm=True."""
    if not human_confirm:
        raise ValueError("Refusing to clear monotonic session taint without human_confirm=True")

    sid = _resolve_session_id(session_id)
    state_path = _resolve_taint_path(project_root)
    if not state_path.exists():
        return False

    state, is_corrupt = _load_taint_state(state_path)
    if is_corrupt:
        atomic_write_text(state_path, json.dumps({"sessions": {}}, indent=2) + "\n", mode=0o600)
        return True

    sessions = dict(state.get("sessions") or {})
    if sid not in sessions:
        return False

    del sessions[sid]
    state["sessions"] = sessions
    atomic_write_text(state_path, json.dumps(state, indent=2, sort_keys=True) + "\n", mode=0o600)
    return True


def is_protected_memory_path(
    file_path: str | Path,
    project_root: Path | None = None,
) -> bool:
    """Return True if `file_path` targets a durable memory store guarded under taint."""
    raw = str(file_path or "").strip()
    if not raw:
        return False

    posix = raw.replace("\\", "/")
    if project_root is not None:
        try:
            rel = Path(raw).resolve().relative_to(Path(project_root).resolve()).as_posix()
            posix = rel
        except (OSError, ValueError) as exc:
            logger.debug("Using raw normalized path for taint protection check (%s): %s", raw, exc)

    name = Path(posix).name
    if name in PROTECTED_MEMORY_FILENAMES:
        return True

    return any(
        posix.startswith(seg) or f"/{seg}" in posix
        for seg in PROTECTED_MEMORY_SEGMENTS
    )
