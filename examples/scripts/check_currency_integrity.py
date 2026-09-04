#!/usr/bin/env python3
"""
check_currency_integrity.py — Pre-commit / CI Guard against Currency Truncation
==============================================================================
Ensures that no markdown file introduces corrupted currency signatures:
  - S,NNN (stripped S$)
  - ,NNN.NN without leading digits (stripped leading thousands)
  - Orphan decimals in financial context (.NN cash|margin)

Supports:
  python3 .agent/scripts/check_currency_integrity.py --staged
  python3 .agent/scripts/check_currency_integrity.py <file1> <file2>...
  python3 .agent/scripts/check_currency_integrity.py --test-red-run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Signatures indicating currency truncation
CORRUPT_PATTERNS = [
    (re.compile(r"\bS,[0-9]{3}(?:\.[0-9]{2})?"), "Stripped S$ prefix (e.g. S,181.03)"),
    (re.compile(r"(?<![0-9A-Za-z]),[0-9]{3}\.[0-9]{2}"), "Stripped leading thousands (e.g. ,034.32)"),
    (re.compile(r"(?<=\s)\.[0-9]{2}(?=\s*(?:cash|margin|balance|lot|USD|SGD|profit|EV|drop|net|drawn))\b"), "Orphan decimal in financial context"),
]


def check_content(text: str, filename: str = "<stdin>") -> list[str]:
    errors = []
    lines = text.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        for pattern, desc in CORRUPT_PATTERNS:
            match = pattern.search(line)
            if match:
                errors.append(
                    f"{filename}:L{line_idx}: Found corrupted currency '{match.group(0)}' ({desc}):\n  {line.strip()}"
                )
    return errors


def check_files(paths: list[Path]) -> int:
    total_errors = []
    for path in paths:
        if not path.is_file() or path.suffix != ".md":
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            errors = check_content(content, str(path))
            total_errors.extend(errors)
        except Exception as e:
            print(f"{YELLOW}⚠️ Error reading {path}: {e}{RESET}", file=sys.stderr)

    if total_errors:
        print(f"\n{RED}❌ CURRENCY INTEGRITY VIOLATIONS DETECTED ({len(total_errors)}):{RESET}")
        for err in total_errors:
            print(f"  {RED}✗{RESET} {err}")
        print(f"\n{YELLOW}Remediation: Restore the missing currency symbols and integer digits (e.g. S$1,181.03 instead of S,181.03).{RESET}")
        return 1

    print(f"{GREEN}✓ Currency integrity clean ({len(paths)} files scanned).{RESET}")
    return 0


def get_staged_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=True,
    )
    repo_root = Path(__file__).resolve().parents[2]
    files = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line and line.endswith(".md"):
            files.append(repo_root / line)
    return files


def run_red_run_test() -> int:
    print("🔬 RUNNING RED-RUN VERIFICATION (Red Run or It Didn't Happen)...")

    # 1. Corrupted specimen
    corrupted_sample = (
        "Updated ledger: bankroll USD 815.80 / S,035.25 SGD @ 1.2690.\n"
        "Active collision capital ceiling at ,000 USD (S,300 SGD).\n"
        "Floating cash margin requirement dropped to .85 cash."
    )
    errors = check_content(corrupted_sample, "corrupted_specimen.md")

    if not errors:
        print(f"{RED}❌ RED-RUN FAILED: Guard failed to catch known corrupted input!{RESET}")
        return 1

    print(f"{GREEN}✓ RED PHASE CONFIRMED:{RESET} Guard caught {len(errors)} corruption signatures on pre-fix state.")
    for err in errors:
        print(f"  {RED}•{RESET} {err.splitlines()[0]}")

    # 2. Clean specimen
    clean_sample = (
        "Updated ledger: bankroll USD 815.80 / S$1,035.25 SGD @ 1.2690.\n"
        "Active collision capital ceiling at $1,000 USD (S$1,300 SGD).\n"
        "Floating cash margin requirement dropped to $0.85 cash."
    )
    clean_errors = check_content(clean_sample, "clean_specimen.md")

    if clean_errors:
        print(f"{RED}❌ GREEN-RUN FAILED: Guard raised false positives on clean input!{RESET}")
        return 1

    print(f"{GREEN}✓ GREEN PHASE CONFIRMED:{RESET} Zero false positives on clean currency notation.")
    print(f"\n{GREEN}✅ RED-RUN VERIFICATION PASSED (Red: {len(errors)} catches -> Green: 0 errors).{RESET}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Currency integrity pre-commit guard.")
    parser.add_argument("--staged", action="store_true", help="Check git staged markdown files.")
    parser.add_argument("--test-red-run", action="store_true", help="Execute Red-Run demonstration test.")
    parser.add_argument("files", nargs="*", type=Path, help="Files to inspect.")

    args = parser.parse_args()

    if args.test_red_run:
        return run_red_run_test()

    if args.staged:
        files = get_staged_files()
        if not files:
            print(f"{GREEN}✓ No staged markdown files to scan.{RESET}")
            return 0
        return check_files(files)

    if args.files:
        return check_files(args.files)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
