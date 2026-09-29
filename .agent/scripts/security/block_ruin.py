#!/usr/bin/env python3
"""
athena.security.block_ruin
==========================
PreToolUse hook for Bash tool execution in AI IDEs (Claude Code, etc.).
Blocks destructive or irreversible shell commands using StructuredRuinCheck (Law #1: No Ruin).
"""

import json
import sys

from athena.core.ruin_check import check_command


def main():
    # CLI / Interactive manual test mode
    if sys.stdin.isatty():
        if len(sys.argv) > 1:
            cmd = " ".join(sys.argv[1:])
            if not check_command(cmd):
                print(f"🚨 BLOCKED: Command '{cmd}' violates Law #1 (No Ruin).", file=sys.stderr)
                sys.exit(2)
        return

    # IDE Hook Mode (JSON via stdin)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
        tool_input = data.get("tool_input", {})
        command = tool_input.get("command") or tool_input.get("cmd") or ""

        if command and not check_command(command):
            print(
                f"🚨 BLOCKED by Athena Law #1 (No Irreversible Ruin):\n"
                f"   Destructive command detected and halted: {command}",
                file=sys.stderr,
            )
            sys.exit(2)  # Exit 2 tells IDE hook runner to abort tool execution
    except Exception:
        # Fail safe: don't crash session on unparseable JSON unless in debug
        pass


if __name__ == "__main__":
    main()
