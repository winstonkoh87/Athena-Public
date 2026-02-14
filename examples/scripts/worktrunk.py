#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
from pathlib import Path

# Configuration
SWARM_PREFIX = "swarm/"
WORKTREE_DIR_NAME = ".swarms"


def run_command(command, cwd=None, capture_output=True):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(
            command, cwd=cwd, shell=True, check=True, text=True, capture_output=capture_output
        )
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        if capture_output:
            print(f"Stderr: {e.stderr}")
        return None


def get_repo_root():
    """Returns the absolute path to the git repository root."""
    return run_command("git rev-parse --show-toplevel")


def get_swarms_dir(repo_root):
    """Returns the directory where swarm worktrees are stored."""
    # Strategy: sibling directory to keep main repo clean
    # e.g., /path/to/repo -> /path/to/repo-swarms
    repo_name = os.path.basename(repo_root)
    parent_dir = os.path.dirname(repo_root)
    return os.path.join(parent_dir, f"{repo_name}-swarms")


def list_swarms(repo_root):
    """Lists active swarm worktrees."""
    swarms_dir = get_swarms_dir(repo_root)
    if not os.path.exists(swarms_dir):
        print("No active swarms found (Swarm directory does not exist).")
        return

    print(f"Active Swarms in {swarms_dir}:\n")
    swarms = [d for d in os.listdir(swarms_dir) if os.path.isdir(os.path.join(swarms_dir, d))]

    if not swarms:
        print("  (None)")

    for swarm in swarms:
        path = os.path.join(swarms_dir, swarm)
        branch = run_command("git branch --show-current", cwd=path)
        print(f"  - {swarm} (Branch: {branch})")
        print(f"    Path: {path}")
        print("")


def add_swarm(repo_root, name):
    """Creates a new swarm worktree."""
    swarms_dir = get_swarms_dir(repo_root)
    target_path = os.path.join(swarms_dir, name)
    branch_name = f"{SWARM_PREFIX}{name}"

    if os.path.exists(target_path):
        print(f"Error: Swarm '{name}' already exists at {target_path}")
        return

    print(f"Creating swarm '{name}'...")
    print(f"  - Directory: {target_path}")
    print(f"  - Branch: {branch_name}")

    # 1. Create swarms directory if needed
    os.makedirs(swarms_dir, exist_ok=True)

    # 2. Create worktree
    # git worktree add -b <branch> <path> <base>
    cmd = f'git worktree add -b {branch_name} "{target_path}" HEAD'
    if run_command(cmd, cwd=repo_root, capture_output=False) is not None:
        print(f"✅ Swarm '{name}' ready.")
        print(f'👉 To use: cd "{target_path}"')


def nuke_swarm(repo_root, name):
    """Removes a swarm worktree."""
    swarms_dir = get_swarms_dir(repo_root)
    target_path = os.path.join(swarms_dir, name)

    if not os.path.exists(target_path):
        print(f"Error: Swarm '{name}' not found at {target_path}")
        return

    print(f"Nuking swarm '{name}'...")

    # 1. Remove worktree using git
    cmd = f'git worktree remove "{target_path}" --force'
    if run_command(cmd, cwd=repo_root, capture_output=False) is not None:
        print(f"✅ Swarm '{name}' removed.")

        # 2. Optional: Delete the branch?
        # For safety, we keep the branch. User can delete it manually if they want.
        print(f"ℹ️  Branch '{SWARM_PREFIX}{name}' was NOT deleted. Delete manually if needed:")
        print(f"   git branch -D {SWARM_PREFIX}{name}")


def merge_swarm(repo_root, name):
    """Merges a swarm branch back into the current branch (usually main)."""
    branch_name = f"{SWARM_PREFIX}{name}"

    print(f"Merging swarm '{name}' ({branch_name}) into current branch...")

    cmd = f"git merge {branch_name}"
    if run_command(cmd, cwd=repo_root, capture_output=False) is not None:
        print(f"✅ Swarm '{name}' merged.")


def main():
    parser = argparse.ArgumentParser(description="Athena Swarm Manager (Worktrunk)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List
    parser_list = subparsers.add_parser("list", help="List active swarms")

    # Add
    parser_add = subparsers.add_parser("add", help="Create a new swarm worktree")
    parser_add.add_argument("name", help="Name of the swarm agent (e.g. 'frontend')")

    # Nuke
    parser_nuke = subparsers.add_parser("nuke", help="Remove a swarm worktree")
    parser_nuke.add_argument("name", help="Name of the swarm agent to remove")

    # Merge
    parser_merge = subparsers.add_parser("merge", help="Merge a swarm branch into current")
    parser_merge.add_argument("name", help="Name of the swarm agent to merge")

    args = parser.parse_args()

    repo_root = get_repo_root()
    if not repo_root:
        print("Error: Not a git repository.")
        sys.exit(1)

    if args.command == "list":
        list_swarms(repo_root)
    elif args.command == "add":
        add_swarm(repo_root, args.name)
    elif args.command == "nuke":
        nuke_swarm(repo_root, args.name)
    elif args.command == "merge":
        merge_swarm(repo_root, args.name)


if __name__ == "__main__":
    main()
