#!/usr/bin/env python3
"""
committer.py — Scoped Git Commit Helper
=========================================

Safety-first commit helper inspired by OpenClaw's `scripts/committer`.
Prevents dangerous mass-staging and enforces multi-agent safety.

Usage:
    python3 .agent/scripts/committer.py "commit message" file1 file2 ...
    python3 .agent/scripts/committer.py --force "commit message" file1  # clear stale lock

Safety guardrails:
    - Blocks "." (entire repo staging)
    - Blocks node_modules, .env, credentials/ paths
    - Restores staging area before adding (prevents cross-contamination)
    - Multi-agent safe: only stages specified files

Pattern credit: OpenClaw (openclaw/openclaw) scripts/committer
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ─── ANSI Colors ─────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ─── Blocked Patterns ────────────────────────────────────────
BLOCKED_PATHS = [
    "node_modules",
    ".env",
    "credentials",
    "__pycache__",
    ".venv",
    "venv",
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def run_git(*args, check=True) -> subprocess.CompletedProcess:
    """Run a git command."""
    cmd = ["git"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=check,
    )


def validate_files(files: list[str]) -> list[str]:
    """Validate file paths against safety rules."""
    errors = []

    for f in files:
        # Block "." — entire repo staging
        if f.strip() == ".":
            errors.append(
                f'{RED}Error: "." is not allowed — list specific paths instead{RESET}'
            )
            continue

        # Block dangerous paths
        for blocked in BLOCKED_PATHS:
            if blocked in f:
                errors.append(
                    f"{RED}Error: blocked path pattern ({blocked}): {f}{RESET}"
                )
                break

    return errors


def check_files_exist(files: list[str]) -> list[str]:
    """Verify files exist or are tracked by git."""
    errors = []
    for f in files:
        full = PROJECT_ROOT / f
        if not full.exists():
            # Check if git tracks it (might be a deletion)
            result = run_git("ls-files", "--error-unmatch", "--", f, check=False)
            if result.returncode != 0:
                errors.append(f"{RED}Error: file not found: {f}{RESET}")
    return errors


def clear_stale_lock() -> bool:
    """Remove stale .git/index.lock if present."""
    lock = PROJECT_ROOT / ".git" / "index.lock"
    if lock.exists():
        lock.unlink()
        print(f"   {YELLOW}🔓 Removed stale .git/index.lock{RESET}")
        return True
    return False


def check_agent_status() -> bool:
    """Check for other active agents (Protocol 413)."""
    status_file = Path.home() / ".athena" / "agent_status.json"
    if not status_file.exists():
        return True

    try:
        import json

        data = json.loads(status_file.read_text())
        active = [a for a in data.get("agents", []) if a.get("active", False)]
        if len(active) > 1:
            print(
                f"   {YELLOW}⚠️  {len(active)} agents active — committing only your specified files{RESET}"
            )
    except Exception:
        pass

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Scoped git commit with safety guardrails",
        usage='committer.py [--force] "commit message" file [file ...]',
    )
    parser.add_argument(
        "--force", action="store_true", help="Force clear stale git locks"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be committed without doing it",
    )
    parser.add_argument("message", help="Commit message")
    parser.add_argument("files", nargs="+", help="Files to commit")

    args = parser.parse_args()

    print(f"\n{BOLD}🔒 Scoped Commit Helper{RESET}")
    print(f"{'─' * 50}")

    # 1. Validate commit message
    if not args.message.strip():
        print(f"{RED}Error: commit message must not be empty{RESET}")
        return 1

    # Check if first arg looks like a file (common mistake)
    if os.path.exists(args.message) and "/" in args.message:
        print(
            f'{RED}Error: first argument looks like a file path ("{args.message}"); provide the commit message first{RESET}'
        )
        return 1

    # 2. Validate file paths
    errors = validate_files(args.files)
    if errors:
        for e in errors:
            print(f"   {e}")
        return 1

    # 3. Check files exist
    errors = check_files_exist(args.files)
    if errors:
        for e in errors:
            print(f"   {e}")
        return 1

    # 4. Multi-agent safety check
    check_agent_status()

    # 5. Dry run mode
    if args.dry_run:
        print(f"\n   {DIM}[DRY RUN] Would commit:{RESET}")
        print(f'   {DIM}Message: "{args.message}"{RESET}')
        for f in args.files:
            print(f"   {DIM}  → {f}{RESET}")
        return 0

    # 6. Restore staging area (prevent cross-contamination)
    run_git("restore", "--staged", ":/", check=False)

    # 7. Stage specified files only
    try:
        run_git("add", "--force", "--", *args.files)
    except subprocess.CalledProcessError as e:
        print(f"   {RED}Error staging files: {e.stderr}{RESET}")
        return 1

    # 8. Check for actual staged changes
    result = run_git("diff", "--staged", "--quiet", check=False)
    if result.returncode == 0:
        print(
            f"   {YELLOW}Warning: no staged changes detected for: {' '.join(args.files)}{RESET}"
        )
        return 1

    # 9. Commit
    try:
        result = run_git("commit", "-m", args.message, "--", *args.files)
        print(
            f'   {GREEN}✅ Committed "{args.message}" with {len(args.files)} file(s){RESET}'
        )
        return 0
    except subprocess.CalledProcessError as e:
        # Handle stale lock with --force
        if args.force and "index.lock" in e.stderr and clear_stale_lock():
            try:
                result = run_git("commit", "-m", args.message, "--", *args.files)
                print(
                    f'   {GREEN}✅ Committed "{args.message}" with {len(args.files)} file(s) (after lock clear){RESET}'
                )
                return 0
            except subprocess.CalledProcessError as e2:
                print(
                    f"   {RED}Error: commit failed after lock clear: {e2.stderr}{RESET}"
                )
                return 1

        print(f"   {RED}Error: commit failed: {e.stderr}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
