#!/usr/bin/env python3
"""
hook_io.py — Shared Stdlib Dual-Harness Hook Adapter & Fast Security Primitives
================================================================================

Normalizes stdin payloads, tool-call schemas, transcript turn extraction,
exit/JSON response contracts, fast taint checks, and audited non-safety waivers
across Claude Code and Google Antigravity hooks.

Constraints:
  - Stdlib only (zero `athena` package imports -> ~45ms cold-start latency).
  - Zero URL substring checks (CodeQL CWE-20 clean).
  - Never allow break-glass waivers for safety-critical gates
    (block_secrets, block_ruin, crisis_referral, protocol_509, egress_gate).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn

ANTIGRAVITY_KEYS = frozenset(
    {
        "toolCall",
        "transcriptPath",
        "hookEventName",
        "terminationReason",
        "conversationId",
        "workspacePaths",
        "lastUserInput",
    }
)

WRITE_TOOL_NAMES = frozenset(
    {
        "Edit",
        "Write",
        "MultiEdit",
        "NotebookEdit",
        "edit_file",
        "write_file",
        "write_to_file",
        "replace_file_content",
        "multi_replace_file_content",
    }
)

SHELL_TOOL_NAMES = frozenset({"Bash", "run_command"})

SAFETY_NON_WAIVABLE = frozenset(
    {
        "block_secrets",
        "block_ruin",
        "crisis_referral",
        "protocol_509",
        "egress_gate",
    }
)

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


def detect_harness(payload: dict[str, Any] | None) -> str:
    """Return 'antigravity' when Antigravity camelCase fields appear, else 'claude'."""
    if isinstance(payload, dict) and any(k in payload for k in ANTIGRAVITY_KEYS):
        return "antigravity"
    return "claude"


def read_hook_stdin(
    *, fail_closed_on_empty: bool = False
) -> tuple[dict[str, Any] | None, str | None]:
    """Read and parse JSON payload from hook stdin.

    Returns (payload_dict, error_reason). When stdin is a TTY, returns (None, None).
    """
    try:
        if sys.stdin.isatty():
            return None, None
        raw = sys.stdin.read()
    except Exception as exc:
        return None, f"failed reading stdin: {exc}"

    if not raw.strip():
        if fail_closed_on_empty:
            return None, "empty stdin payload"
        return None, None

    try:
        data = json.loads(raw)
    except Exception as exc:
        return None, f"malformed stdin JSON: {exc}"

    if not isinstance(data, dict):
        return None, "Expected JSON object on stdin"

    return data, None


def extract_tool_call(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Extract normalized (tool_name, tool_args) from Claude Code or Antigravity payload."""
    if "toolCall" in payload:
        tc = payload.get("toolCall")
        if not isinstance(tc, dict):
            raise ValueError("Expected toolCall JSON object")
        args = tc.get("args")
        if args is None:
            args = {}
        elif not isinstance(args, dict):
            raise ValueError("Expected toolCall.args JSON object")
        return str(tc.get("name") or ""), args

    tool_input = payload.get("tool_input")
    if tool_input is None:
        tool_input = {}
    elif not isinstance(tool_input, dict):
        raise ValueError("Expected tool_input JSON object")
    return str(payload.get("tool_name") or ""), tool_input


def extract_file_path(tool_args: dict[str, Any]) -> str:
    """Extract target file path across Claude Code and Antigravity tool arg schemas."""
    for key in (
        "file_path",
        "path",
        "Path",
        "target_file",
        "TargetFile",
        "AbsolutePath",
    ):
        val = tool_args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def extract_shell_command(tool_args: dict[str, Any]) -> str:
    """Extract shell command string across Claude Code and Antigravity schemas."""
    for key in ("command", "cmd", "CommandLine"):
        val = tool_args.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def parse_iso_timestamp(raw: Any) -> float | None:
    """Parse ISO-8601 string or numeric timestamp into UTC epoch seconds."""
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str) or not raw.strip():
        return None
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


def _extract_claude_message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in (None, "text"):
                txt = item.get("text")
                if isinstance(txt, str) and txt:
                    parts.append(txt)
        return "\n".join(parts)
    return ""


def _parse_user_step(rec: dict[str, Any]) -> tuple[bool, str, float | None]:
    """Identify a genuine user prompt record (ignoring Claude tool_result wrappers)."""
    if rec.get("type") == "USER_INPUT":
        ts = parse_iso_timestamp(rec.get("created_at") or rec.get("timestamp"))
        return True, str(rec.get("content") or ""), ts

    msg = rec.get("message")
    if isinstance(msg, dict) and msg.get("role") == "user":
        content = msg.get("content", "")
        if isinstance(content, list) and any(
            isinstance(item, dict) and item.get("type") == "tool_result"
            for item in content
        ):
            return False, "", None
        ts = parse_iso_timestamp(rec.get("timestamp") or rec.get("created_at"))
        return True, _extract_claude_message_text(content), ts

    return False, "", None


def _extract_assistant_step_text(rec: dict[str, Any]) -> str:
    if rec.get("source") == "MODEL" and rec.get("type") == "PLANNER_RESPONSE":
        content = rec.get("content", "")
        return content if isinstance(content, str) else ""

    msg = rec.get("message")
    if isinstance(msg, dict) and msg.get("role") == "assistant":
        return _extract_claude_message_text(msg.get("content", ""))

    return ""


def _read_transcript_records(transcript_path: str, max_lines: int = 250) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as tf:
            lines = tf.readlines()[-max_lines:]
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
                if isinstance(rec, dict):
                    records.append(rec)
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return records


def extract_turn_texts_universal(payload: dict[str, Any] | None) -> tuple[str, str]:
    """Extract (user_prompt, assistant_reply) across Claude Code and Antigravity."""
    if not payload or not isinstance(payload, dict):
        return "", ""

    user_prompt = ""
    assistant_reply = ""

    transcript_path = payload.get("transcript_path") or payload.get("transcriptPath")
    if isinstance(transcript_path, str) and transcript_path and os.path.exists(transcript_path):
        records = _read_transcript_records(transcript_path)
        last_user_idx = -1
        for idx, rec in enumerate(records):
            is_user, text, _ = _parse_user_step(rec)
            if is_user:
                last_user_idx = idx
                if text:
                    user_prompt = text

        reply_slice = records[last_user_idx + 1 :] if last_user_idx >= 0 else records
        for rec in reversed(reply_slice):
            txt = _extract_assistant_step_text(rec)
            if txt:
                assistant_reply = txt
                break

    if not user_prompt:
        raw_prompt = (
            payload.get("prompt")
            or payload.get("user_prompt")
            or payload.get("lastUserInput")
            or ""
        )
        user_prompt = raw_prompt if isinstance(raw_prompt, str) else ""

    if not assistant_reply:
        raw_reply = (
            payload.get("assistant_reply")
            or payload.get("text")
            or payload.get("reply")
            or ""
        )
        assistant_reply = raw_reply if isinstance(raw_reply, str) else ""

    return user_prompt, assistant_reply


def _normalize_repo_rel(raw_path: str, repo_root: Path) -> str:
    cleaned = raw_path.strip().replace("\\", "/")
    if not cleaned:
        return ""
    p = Path(cleaned)
    if p.is_absolute():
        try:
            return p.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return cleaned
    return cleaned.lstrip("./")


def _iter_step_tool_calls(rec: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    calls: list[tuple[str, dict[str, Any]]] = []
    # Antigravity PLANNER_RESPONSE tool_calls
    ag_calls = rec.get("tool_calls")
    if isinstance(ag_calls, list):
        for tc in ag_calls:
            if isinstance(tc, dict) and tc.get("name"):
                args = tc.get("args")
                calls.append((str(tc["name"]), args if isinstance(args, dict) else {}))

    # Claude Code message.content tool_use blocks
    msg = rec.get("message")
    if isinstance(msg, dict) and msg.get("role") == "assistant":
        content = msg.get("content")
        if isinstance(content, list):
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name")
                ):
                    inp = block.get("input")
                    calls.append((str(block["name"]), inp if isinstance(inp, dict) else {}))

    return calls


def extract_turn_write_context(
    payload: dict[str, Any] | None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Return current-turn file modification context from Claude/Antigravity transcript."""
    empty = {
        "has_transcript": False,
        "turn_start_ts": None,
        "written_files": set(),
        "had_shell_exec": False,
    }
    if not payload or not isinstance(payload, dict):
        return empty

    transcript_path = payload.get("transcript_path") or payload.get("transcriptPath")
    if not isinstance(transcript_path, str) or not transcript_path or not os.path.exists(transcript_path):
        return empty

    records = _read_transcript_records(transcript_path, max_lines=400)
    if not records:
        return empty

    root = (repo_root or Path.cwd()).resolve()
    last_user_idx = -1
    turn_start_ts: float | None = None
    for idx, rec in enumerate(records):
        is_user, _, ts = _parse_user_step(rec)
        if is_user:
            last_user_idx = idx
            turn_start_ts = ts

    turn_records = records[last_user_idx + 1 :] if last_user_idx >= 0 else records
    written_files: set[str] = set()
    had_shell_exec = False

    for rec in turn_records:
        for tool_name, args in _iter_step_tool_calls(rec):
            if tool_name in WRITE_TOOL_NAMES:
                fp = extract_file_path(args)
                if fp:
                    rel = _normalize_repo_rel(fp, root)
                    if rel:
                        written_files.add(rel)
            elif tool_name in SHELL_TOOL_NAMES:
                had_shell_exec = True

    return {
        "has_transcript": True,
        "turn_start_ts": turn_start_ts,
        "written_files": written_files,
        "had_shell_exec": had_shell_exec,
    }


def emit_pretool_block(reason: str, harness: str) -> NoReturn:
    """Emit PreToolUse block response for Antigravity (JSON deny) or Claude Code (exit 2)."""
    if harness == "antigravity":
        print(json.dumps({"decision": "deny", "reason": reason}))
        print(reason, file=sys.stderr)
        sys.exit(0)
    print(reason, file=sys.stderr)
    sys.exit(2)


def emit_pretool_allow(harness: str) -> NoReturn:
    """Emit PreToolUse allow response for Antigravity or Claude Code."""
    if harness == "antigravity":
        print(json.dumps({"decision": "allow"}))
    sys.exit(0)


def emit_stop_block(
    reason: str, harness: str, *, extra: dict[str, Any] | None = None
) -> NoReturn:
    """Emit Stop block response for Antigravity (continue) or Claude Code (block + exit 2)."""
    extras = dict(extra or {})
    if harness == "antigravity":
        payload = {"decision": "continue", "reason": reason, **extras}
        print(json.dumps(payload))
        sys.exit(0)

    payload = {"decision": "block", "reason": reason, **extras}
    print(json.dumps(payload, indent=2))
    print(reason, file=sys.stderr)
    sys.exit(2)


def emit_stop_allow(
    harness: str, *, extra: dict[str, Any] | None = None
) -> NoReturn:
    """Emit Stop allow response for both Antigravity and Claude Code."""
    payload = {"decision": "allow", **(extra or {})}
    print(json.dumps(payload))
    sys.exit(0)


def _log_waiver_decision(repo_root: Path, gate_name: str, reason: str) -> None:
    try:
        log_path = repo_root / ".athena" / "gate_decisions.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "check": gate_name,
            "decision": "waived",
            "reason": reason,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def check_hook_waiver(gate_name: str, repo_root: Path) -> str | None:
    """Return an audited waiver reason for non-safety gates, or None.

    Safety-critical gates in SAFETY_NON_WAIVABLE are never waivable.
    """
    if gate_name in SAFETY_NON_WAIVABLE:
        return None

    env_reason = (os.environ.get("ATHENA_HOOK_WAIVER") or "").strip()
    if len(env_reason) >= 8:
        _log_waiver_decision(repo_root, gate_name, env_reason)
        return env_reason

    waivers_path = repo_root / ".athena" / "hook_waivers.jsonl"
    if not waivers_path.exists():
        return None

    now_ts = datetime.now(timezone.utc).timestamp()
    try:
        lines = waivers_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-50:]
        for line in reversed(lines):
            raw = line.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            target_gate = rec.get("gate")
            if target_gate not in (gate_name, "*"):
                continue
            reason = str(rec.get("reason") or "").strip()
            if len(reason) < 8:
                continue
            exp_ts = parse_iso_timestamp(rec.get("expires_at"))
            if exp_ts is None or exp_ts <= now_ts:
                continue
            _log_waiver_decision(repo_root, gate_name, reason)
            return reason
    except OSError:
        return None

    return None


def is_tainted_fast(project_root: Path) -> bool:
    """Stdlib-only monotonic taint check mirroring athena.core.taint (fail-closed on corrupt state)."""
    env_raw = (os.environ.get("ATHENA_TAINTED") or "").strip().lower()
    if env_raw in _ENV_TRUTHY:
        return True

    env_path = (os.environ.get("ATHENA_TAINT_STATE_PATH") or "").strip()
    state_path = (
        Path(env_path)
        if env_path
        else (project_root / ".athena" / "runtime" / "taint_state.json")
    )
    if not state_path.exists():
        return False

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return True

    if not isinstance(data, dict):
        return True

    sessions = data.get("sessions")
    if sessions is None:
        return False
    if not isinstance(sessions, dict):
        return True

    sid = (os.environ.get("ATHENA_SESSION_ID") or "active").strip() or "active"
    entry = sessions.get(sid)
    return isinstance(entry, dict) and bool(entry.get("tainted"))


def is_protected_memory_path_fast(
    file_path: str | Path, project_root: Path | None = None
) -> bool:
    """Stdlib-only check matching athena.core.taint.is_protected_memory_path."""
    raw = str(file_path or "").strip()
    if not raw:
        return False

    posix = raw.replace("\\", "/")
    if project_root is not None:
        try:
            posix = Path(raw).resolve().relative_to(Path(project_root).resolve()).as_posix()
        except (OSError, ValueError):
            pass

    if Path(posix).name in PROTECTED_MEMORY_FILENAMES:
        return True

    return any(
        posix.startswith(seg) or f"/{seg}" in posix
        for seg in PROTECTED_MEMORY_SEGMENTS
    )
