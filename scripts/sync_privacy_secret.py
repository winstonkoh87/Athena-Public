#!/usr/bin/env python3
"""
sync_privacy_secret.py — push private privacy patterns to the public repo secret
================================================================================

Athena-Public's privacy gate matches two pattern sources:

  1. `.github/privacy_blocklist.txt` — committed, therefore public. May hold
     shape-describing matchers only (email/phone/credential formats, paths).
  2. `PRIVACY_EXTRA_PATTERNS` — a repo secret. Holds everything with a literal
     word in it: people, clients, private folders, private topics.

Source of truth for (2) is `.agent/config/privacy_patterns.txt` in this
private workspace. Before this script existed, the secret was a write-only
black box — nobody could tell what the gate was actually enforcing, and
overwriting it risked silently dropping patterns. Now it is reproducible.

Usage:
    python3 scripts/sync_privacy_secret.py            # show what would change
    python3 scripts/sync_privacy_secret.py --push     # write the secret
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS_PATH = ROOT / ".agent" / "config" / "privacy_patterns.txt"
PUBLIC_REPO = "winstonkoh87/Athena-Public"
SECRET_NAME = "PRIVACY_EXTRA_PATTERNS"


def load_patterns() -> list[str]:
    """Non-comment, non-blank lines — each must compile as a regex."""
    if not PATTERNS_PATH.exists():
        print(f"ERROR: {PATTERNS_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    patterns, invalid = [], []
    for line in PATTERNS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            re.compile(line, re.IGNORECASE)
        except re.error as e:
            invalid.append(f"{line} — {e}")
            continue
        patterns.append(line)

    if invalid:
        print("ERROR: invalid regex in privacy_patterns.txt:", file=sys.stderr)
        for entry in invalid:
            print(f"  {entry}", file=sys.stderr)
        sys.exit(1)

    if not patterns:
        print("ERROR: no patterns loaded — refusing to overwrite the secret "
              "with an empty value.", file=sys.stderr)
        sys.exit(1)

    return patterns


def main() -> int:
    patterns = load_patterns()

    # Never print the patterns themselves — this script's output lands in
    # terminal scrollback, CI logs and session transcripts.
    print(f"Loaded {len(patterns)} pattern(s) from {PATTERNS_PATH.relative_to(ROOT)}")
    print(f"Target: {SECRET_NAME} @ {PUBLIC_REPO}")

    if "--push" not in sys.argv:
        print("\nDry run. Re-run with --push to write the secret.")
        return 0

    result = subprocess.run(
        ["gh", "secret", "set", SECRET_NAME, "-R", PUBLIC_REPO],
        input="\n".join(patterns),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"ERROR: gh secret set failed — {result.stderr.strip()}", file=sys.stderr)
        return 1

    print(f"✅ {SECRET_NAME} updated with {len(patterns)} pattern(s).")
    print("   The gate now enforces these without publishing them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
