#!/usr/bin/env python3
"""PreToolUse (Edit|Write) hook blocking durable memory writes while session is tainted."""

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


def block_tainted_memory() -> None:
    """Inspect hook stdin JSON; exit 2 on tainted protected memory write or malformed/empty input."""
    data, err = read_hook_stdin(fail_closed_on_empty=True)
    if err is not None:
        print(
            f"BLOCKED (fail-closed): Taint memory gate error while inspecting input: {err}",
            file=sys.stderr,
        )
        sys.exit(2)

    if data is None:
        return

    harness = detect_harness(data)
    try:
        _, tool_args = extract_tool_call(data)
    except Exception as exc:
        emit_pretool_block(
            f"BLOCKED (fail-closed): Taint memory gate error while inspecting input: {exc}",
            harness,
        )

    file_path = extract_file_path(tool_args)
    if not file_path:
        emit_pretool_allow(harness)

    root_override = (
        os.environ.get("ATHENA_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or ""
    ).strip()
    project_root = Path(root_override) if root_override else REPO_ROOT

    if is_tainted_fast(project_root) and is_protected_memory_path_fast(
        str(file_path), project_root=project_root
    ):
        emit_pretool_block(
            f"BLOCKED (taint quarantine): Durable memory write to {file_path} "
            "denied while session is tainted.",
            harness,
        )

    emit_pretool_allow(harness)


if __name__ == "__main__":
    block_tainted_memory()
