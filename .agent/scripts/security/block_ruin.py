#!/usr/bin/env python3
"""
athena.security.block_ruin
==========================
PreToolUse hook for Bash tool execution in AI IDEs (Claude Code, etc.).
Blocks destructive or irreversible shell commands using StructuredRuinCheck (Law #1: No Ruin).
"""

import json
import re
import sys
from pathlib import Path

# 1. Resolve repo src directory relative to this hook script
_src_dir = Path(__file__).resolve().parents[3] / "src"
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


def main():
    # CLI / Interactive manual test mode
    if sys.stdin.isatty():
        if len(sys.argv) > 1:
            cmd = " ".join(sys.argv[1:])
            if not check_command_safe(cmd):
                print(f"🚨 BLOCKED: Command '{cmd}' violates Law #1 (No Ruin).", file=sys.stderr)
                sys.exit(2)
        return

    # IDE Hook Mode (JSON via stdin)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object on stdin")

        tool_input = data.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            raise ValueError("Expected tool_input JSON object")

        command = tool_input.get("command") or tool_input.get("cmd") or ""

        if command and not check_command_safe(command):
            print(
                f"🚨 BLOCKED by Athena Law #1 (No Irreversible Ruin):\n"
                f"   Destructive command detected and halted: {command}",
                file=sys.stderr,
            )
            sys.exit(2)  # Exit 2 tells IDE hook runner to abort tool execution
    except Exception as exc:
        print(
            f"🚨 BLOCKED (fail-closed) by Athena Law #1: Ruin gate failed to parse tool input: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
