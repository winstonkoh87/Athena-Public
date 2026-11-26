#!/usr/bin/env python3
"""
athena.security.block_ruin
==========================
PreToolUse hook for Bash / run_command tool execution in AI IDEs (Claude Code, Antigravity).
Blocks destructive or irreversible shell commands using StructuredRuinCheck (Law #1: No Ruin).
"""

from __future__ import annotations

import re
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
    extract_shell_command,
    extract_tool_call,
    read_hook_stdin,
)

# 1. Resolve repo src directory relative to this hook script
_src_dir = SCRIPTS_DIR.parent.parent / "src"
if _src_dir.exists() and str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# 2. Inline stdlib regex floor fallback in case athena package import fails
RUINOUS_PATTERNS_FLOOR = [
    r"rm -rf \.context",
    r"rm -rf \.agent",
    r"rm -rf /",
    r"truncate -s 0 \.context",
    r"delete_file.*\.context",
    r"overwrite_file.*\.context.*empty=True",
    r"find\s+.*\.context.*\-(?:delete|exec\s+rm)",
    r"mv\s+.*\.context\b",
]

_check_command_fn = None
try:
    from athena.core.ruin_check import check_command as _check_command_fn
except ImportError:
    print(
        "⚠️  WARNING: Could not import athena.core.ruin_check. Using inline regex floor fallback.",
        file=sys.stderr,
    )


def check_command_safe(command: str) -> bool:
    if _check_command_fn is not None:
        return _check_command_fn(command)
    for pattern in RUINOUS_PATTERNS_FLOOR:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    return True


def main() -> None:
    # CLI / Interactive manual test mode
    if sys.stdin.isatty():
        if len(sys.argv) > 1:
            cmd = " ".join(sys.argv[1:])
            if not check_command_safe(cmd):
                print(f"🚨 BLOCKED: Command '{cmd}' violates Law #1 (No Ruin).", file=sys.stderr)
                sys.exit(2)
        return

    # IDE Hook Mode (JSON via stdin, fail-closed on empty/malformed stdin)
    data, err = read_hook_stdin(fail_closed_on_empty=True)
    if err is not None:
        print(
            f"🚨 BLOCKED (fail-closed) by Athena Law #1: Ruin gate failed to parse tool input: {err}",
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
            f"🚨 BLOCKED (fail-closed) by Athena Law #1: Ruin gate failed to parse tool input: {exc}",
            harness,
        )

    command = extract_shell_command(tool_args)
    if command and not check_command_safe(command):
        emit_pretool_block(
            f"🚨 BLOCKED by Athena Law #1 (No Irreversible Ruin):\n"
            f"   Destructive command detected and halted: {command}",
            harness,
        )

    emit_pretool_allow(harness)


if __name__ == "__main__":
    main()
