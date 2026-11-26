#!/usr/bin/env python3
"""PreToolUse (Read|Edit|Write / read_file|edit_file|write_file) security gate.

Enforces two fail-closed checks in a single stdlib-only process (~48ms):
  1. Blocks reads/writes to sensitive credential files (.env, .env.*, keys, cloud creds).
  2. Blocks writes to durable Athena memory when session taint quarantine is active.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
LIB_DIR = SCRIPTS_DIR / "lib"
for _p in (SCRIPTS_DIR, LIB_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from hook_io import (  # noqa: E402
    WRITE_TOOL_NAMES,
    detect_harness,
    emit_pretool_allow,
    emit_pretool_block,
    extract_file_path,
    extract_tool_call,
    is_protected_memory_path_fast,
    is_tainted_fast,
    read_hook_stdin,
)

REPO_ROOT = SCRIPTS_DIR.parent.parent

SENSITIVE_BASENAMES = frozenset(
    {
        ".env",
        "secrets.json",
        "id_rsa",
        "id_ed25519",
        "id_ecdsa",
        "id_dsa",
        ".npmrc",
        ".netrc",
        ".pypirc",
        "credentials.json",
        "service-account.json",
    }
)
SAFE_ENV_TEMPLATES = frozenset(
    {".env.example", ".env.sample", ".env.template", ".env.dist"}
)
SENSITIVE_EXTS = (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore")
SENSITIVE_SEGMENTS = ("/.aws/credentials", "/.ssh/id_", "/.gnupg/")


def is_sensitive_path(file_path: str) -> str | None:
    """Return block reason if file_path targets a sensitive credential file, else None."""
    name_lower = Path(file_path).name.lower()
    posix_lower = file_path.replace("\\", "/").lower()

    if name_lower == ".env" or (
        name_lower.startswith(".env.") and name_lower not in SAFE_ENV_TEMPLATES
    ):
        return f"BLOCKED: Access to {file_path} denied. Sensitive dotenv file detected."

    if name_lower in SENSITIVE_BASENAMES:
        return f"BLOCKED: Access to {file_path} denied. Sensitive credential file detected."

    if name_lower.endswith(SENSITIVE_EXTS):
        return f"BLOCKED: Access to {file_path} denied. Sensitive extension detected."

    if any(seg in posix_lower for seg in SENSITIVE_SEGMENTS):
        return f"BLOCKED: Access to {file_path} denied. Sensitive credential path detected."

    return None


def _resolve_project_root() -> Path:
    root_override = (
        os.environ.get("ATHENA_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or ""
    ).strip()
    return Path(root_override) if root_override else REPO_ROOT


def block_secrets() -> None:
    """Inspect hook stdin JSON; fail closed on sensitive access, tainted writes, or bad stdin."""
    data, err = read_hook_stdin(fail_closed_on_empty=True)
    if err is not None:
        print(
            f"BLOCKED (fail-closed): Secret protection gate error while inspecting input: {err}",
            file=sys.stderr,
        )
        sys.exit(2)

    if data is None:
        return

    harness = detect_harness(data)
    try:
        tool_name, tool_args = extract_tool_call(data)
    except Exception as exc:
        emit_pretool_block(
            f"BLOCKED (fail-closed): Secret protection gate error while inspecting input: {exc}",
            harness,
        )

    file_path = extract_file_path(tool_args)
    if not file_path:
        emit_pretool_allow(harness)

    sensitive_reason = is_sensitive_path(file_path)
    if sensitive_reason:
        emit_pretool_block(sensitive_reason, harness)

    # Merged taint quarantine gate on write tools (read-only remains allowed)
    if not tool_name or tool_name in WRITE_TOOL_NAMES:
        # Note: if tool_name is known to be Read/read_file/view_file, skip taint write block.
        # Only enforce taint quarantine when tool_name is explicitly a write tool.
        if tool_name in WRITE_TOOL_NAMES:
            project_root = _resolve_project_root()
            if is_tainted_fast(project_root) and is_protected_memory_path_fast(
                file_path, project_root=project_root
            ):
                emit_pretool_block(
                    f"BLOCKED (taint quarantine): Durable memory write to {file_path} "
                    "denied while session is tainted.",
                    harness,
                )

    emit_pretool_allow(harness)


if __name__ == "__main__":
    block_secrets()
