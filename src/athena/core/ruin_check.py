"""
athena.core.ruin_check
======================
Mechanical Kill-Switch (Law #1: No Irreversible Ruin).
Scans for destructive patterns before execution using StructuredRuinCheck + regex fallback.
"""

import re
import sys

from athena.core.ruin_structured import StructuredRuinCheck

RUINOUS_PATTERNS = [
    r"rm -rf \.context",
    r"rm -rf \.agent",
    r"rm -rf /",
    r"truncate -s 0 \.context",
    r"delete_file.*\.context",
    r"overwrite_file.*\.context.*empty=True",
    r"find\s+.*\.context.*\-(?:delete|exec\s+rm)",
    r"mv\s+.*\.context\b",
]

def check_command(command: str) -> bool:
    """
    Returns True if safe, False if Ruinous.
    Combines legacy regex checks with StructuredRuinCheck.
    """
    # 1. Regex check
    for pattern in RUINOUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False

    # 2. Structured check
    checker = StructuredRuinCheck()
    allowed, _ = checker.check_command(command)
    return allowed


def main():
    if len(sys.argv) < 2:
        print('Usage: ruin_check.py "<proposed_command>"')
        sys.exit(0)

    cmd = " ".join(sys.argv[1:])
    if not check_command(cmd):
        print("🚨 RUIN CHECK FAIL: Action blocked by Law #1 (No Irreversible Ruin).")
        sys.exit(1)

    print("✅ Action safe.")
    sys.exit(0)


if __name__ == "__main__":
    main()
