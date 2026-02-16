#!/usr/bin/env python3
"""
Worktree Manager — Maestro-Style Parallel Development
======================================================
Enables isolated git worktrees for parallel AI agent execution.
Based on Protocol 100: Git Worktree Parallelism.

Commands:
  new <branch>   Create a new worktree for <branch>
  list           List all active worktrees for current project
  clean <branch> Remove worktree for <branch>
  clean-all      Remove all worktrees for current project
"""

import os
import subprocess
import sys
import hashlib
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKTREE_BASE = Path.home() / ".athena" / "worktrees"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def get_project_hash() -> str:
    """Generate a short hash for the project path to avoid conflicts."""
    return hashlib.md5(str(PROJECT_ROOT).encode()).hexdigest()[:8]


def get_project_name() -> str:
    """Get a clean project name for the worktree directory."""
    return PROJECT_ROOT.name


def get_worktree_dir() -> Path:
    """Get the worktree directory for this project."""
    return WORKTREE_BASE / f"{get_project_name()}-{get_project_hash()}"


def run_git(args: list, cwd: Path = None, check: bool = True) -> tuple:
    """Run a git command and return output."""
    cwd = cwd or PROJECT_ROOT
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return (
            e.stdout.strip() if e.stdout else "",
            e.stderr.strip() if e.stderr else "",
            e.returncode,
        )
    except FileNotFoundError:
        return "", "Git not installed", 1


def check_git_repo() -> bool:
    """Check if we're in a git repository."""
    stdout, stderr, code = run_git(["rev-parse", "--git-dir"], check=False)
    return code == 0


def cmd_new(branch_name: str) -> int:
    """Create a new worktree for the given branch."""
    if not check_git_repo():
        print(f"{RED}✗ Not a git repository.{RESET}")
        return 1

    worktree_path = get_worktree_dir() / branch_name

    # Check if worktree already exists
    if worktree_path.exists():
        print(f"{YELLOW}⚠️ Worktree already exists at: {worktree_path}{RESET}")
        print(
            f"{DIM}   Use 'worktree_manager.py clean {branch_name}' to remove it first.{RESET}"
        )
        return 1

    # Ensure base directory exists
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if branch exists
    stdout, stderr, code = run_git(
        ["rev-parse", "--verify", f"refs/heads/{branch_name}"], check=False
    )
    branch_exists = code == 0

    if branch_exists:
        # Use existing branch
        print(f"{DIM}Using existing branch: {branch_name}{RESET}")
        stdout, stderr, code = run_git(
            ["worktree", "add", str(worktree_path), branch_name], check=False
        )
    else:
        # Create new branch from current HEAD
        print(f"{DIM}Creating new branch: {branch_name}{RESET}")
        stdout, stderr, code = run_git(
            ["worktree", "add", "-b", branch_name, str(worktree_path)], check=False
        )

    if code != 0:
        print(f"{RED}✗ Failed to create worktree: {stderr}{RESET}")
        return 1

    print(f"{GREEN}✓ Worktree created!{RESET}")
    print(f"  {BOLD}Branch:{RESET} {branch_name}")
    print(f"  {BOLD}Path:{RESET}   {worktree_path}")
    print()
    print(f"{DIM}To work in this worktree:{RESET}")
    print(f"  cd {worktree_path}")
    return 0


def cmd_list() -> int:
    """List all worktrees for the current project."""
    if not check_git_repo():
        print(f"{RED}✗ Not a git repository.{RESET}")
        return 1

    stdout, stderr, code = run_git(["worktree", "list", "--porcelain"], check=False)
    if code != 0:
        print(f"{RED}✗ Failed to list worktrees: {stderr}{RESET}")
        return 1

    worktrees = []
    current = {}
    for line in stdout.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[9:]}
        elif line.startswith("HEAD "):
            current["head"] = line[5:8]
        elif line.startswith("branch "):
            current["branch"] = line[7:].replace("refs/heads/", "")
        elif line == "bare":
            current["bare"] = True
    if current:
        worktrees.append(current)

    print(
        f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════{RESET}"
    )
    print(
        f"{BOLD}{CYAN}              📂 GIT WORKTREES ({get_project_name()})                    {RESET}"
    )
    print(
        f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}\n"
    )

    project_worktree_dir = str(get_worktree_dir())

    for wt in worktrees:
        path = wt.get("path", "")
        branch = wt.get("branch", "(detached)")
        head = wt.get("head", "???")

        # Check if this is a project worktree or the main repo
        is_main = path == str(PROJECT_ROOT)
        is_project_wt = path.startswith(project_worktree_dir)

        if is_main:
            marker = f"{GREEN}[MAIN]{RESET}"
        elif is_project_wt:
            marker = f"{CYAN}[WORKTREE]{RESET}"
        else:
            marker = f"{DIM}[OTHER]{RESET}"

        print(f"  {marker} {BOLD}{branch}{RESET}")
        print(f"      {DIM}{path}{RESET}")
        print()

    return 0


def cmd_clean(branch_name: str, delete_branch: bool = False) -> int:
    """Remove a worktree."""
    if not check_git_repo():
        print(f"{RED}✗ Not a git repository.{RESET}")
        return 1

    worktree_path = get_worktree_dir() / branch_name

    if not worktree_path.exists():
        print(f"{YELLOW}⚠️ Worktree not found at: {worktree_path}{RESET}")
        return 1

    # Remove worktree
    stdout, stderr, code = run_git(
        ["worktree", "remove", str(worktree_path), "--force"], check=False
    )
    if code != 0:
        print(f"{RED}✗ Failed to remove worktree: {stderr}{RESET}")
        return 1

    print(f"{GREEN}✓ Worktree removed: {branch_name}{RESET}")

    # Optionally delete branch
    if delete_branch:
        stdout, stderr, code = run_git(["branch", "-D", branch_name], check=False)
        if code == 0:
            print(f"{GREEN}✓ Branch deleted: {branch_name}{RESET}")
        else:
            print(f"{YELLOW}⚠️ Could not delete branch: {stderr}{RESET}")

    return 0


def cmd_clean_all() -> int:
    """Remove all worktrees for the current project."""
    if not check_git_repo():
        print(f"{RED}✗ Not a git repository.{RESET}")
        return 1

    worktree_dir = get_worktree_dir()

    if not worktree_dir.exists():
        print(f"{GREEN}✓ No worktrees to clean.{RESET}")
        return 0

    # List all subdirectories
    branches = [d.name for d in worktree_dir.iterdir() if d.is_dir()]

    if not branches:
        print(f"{GREEN}✓ No worktrees to clean.{RESET}")
        return 0

    print(f"{YELLOW}Cleaning {len(branches)} worktree(s)...{RESET}")
    for branch in branches:
        cmd_clean(branch)

    # Prune stale worktree entries
    run_git(["worktree", "prune"], check=False)
    print(f"\n{GREEN}✓ All worktrees cleaned.{RESET}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    if command == "new":
        if len(sys.argv) < 3:
            print(f"{RED}✗ Usage: worktree_manager.py new <branch_name>{RESET}")
            return 1
        return cmd_new(sys.argv[2])

    elif command == "list":
        return cmd_list()

    elif command == "clean":
        if len(sys.argv) < 3:
            print(f"{RED}✗ Usage: worktree_manager.py clean <branch_name>{RESET}")
            return 1
        delete_branch = "--delete-branch" in sys.argv
        return cmd_clean(sys.argv[2], delete_branch)

    elif command == "clean-all":
        return cmd_clean_all()

    else:
        print(f"{RED}✗ Unknown command: {command}{RESET}")
        print(__doc__)
        return 1


if __name__ == "__main__":
    sys.exit(main())
