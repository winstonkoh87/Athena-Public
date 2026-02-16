#!/usr/bin/env python3
"""
jit_inject.py - Preprocess prompts with live shell data.

Stolen from Claude Code's !`command` syntax.
Protocol 405: JIT Context Injection

Usage:
    python3 jit_inject.py template.md > hydrated_prompt.md
    cat template.md | python3 jit_inject.py - > hydrated_prompt.md

Example template:
    ## Current Branch
    !`git branch --show-current`

    ## Recent Commits
    !`git log -5 --oneline`
"""

import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Pattern: !`command` (backticks with ! prefix)
PATTERN = r"!\`([^`]+)\`"

# Audit log location
AUDIT_LOG = Path(__file__).parent.parent.parent / ".athena" / "jit_audit.log"


def log_execution(cmd: str, success: bool):
    """Log command execution for security audit."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    status = "OK" if success else "FAIL"
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{timestamp} [{status}] {cmd}\n")


def execute_command(cmd: str, timeout: int = 30) -> str:
    """Run shell command, return stdout or error message."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent.parent,  # Project root
        )
        success = result.returncode == 0
        log_execution(cmd, success)

        if success:
            return result.stdout.strip()
        else:
            return f"[ERROR: {result.stderr.strip()}]"

    except subprocess.TimeoutExpired:
        log_execution(cmd, False)
        return f"[ERROR: Command timed out after {timeout}s]"
    except Exception as e:
        log_execution(cmd, False)
        return f"[ERROR: {e}]"


def hydrate(template: str) -> str:
    """Replace all !`command` patterns with their output."""

    def replacer(match):
        cmd = match.group(1)
        output = execute_command(cmd)
        # Wrap output in code block if multi-line
        if "\n" in output:
            return f"```\n{output}\n```"
        return output

    return re.sub(PATTERN, replacer, template)


def main():
    if len(sys.argv) < 2:
        print("Usage: jit_inject.py <template.md | ->", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print(
            '  echo "Current branch: !`git branch --show-current`" | python3 jit_inject.py -',
            file=sys.stderr,
        )
        sys.exit(1)

    source = sys.argv[1]
    if source == "-":
        template = sys.stdin.read()
    else:
        path = Path(source)
        if not path.exists():
            print(f"Error: File not found: {source}", file=sys.stderr)
            sys.exit(1)
        template = path.read_text()

    hydrated = hydrate(template)
    print(hydrated)


if __name__ == "__main__":
    main()
