#!/usr/bin/env python3
"""
Parallel Swarm Launcher (Native)
================================
Launches 4 Terminal windows, each running a sworn_agent.py in a dedicated worktree.
Implements Protocol 101: Native Swarm.
"""

import argparse
import sys
import os
import subprocess
import time
from pathlib import Path

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

SCRIPTS_DIR = Path(__file__).resolve().parent
WORKTREE_MANAGER = SCRIPTS_DIR / "worktree_manager.py"
SWARM_AGENT = SCRIPTS_DIR / "swarm_agent.py"

TRACKS = {
    "A": {"role": "A", "branch_suffix": "track-A-domain"},
    "B": {"role": "B", "branch_suffix": "track-B-adversarial"},
    "C": {"role": "C", "branch_suffix": "track-C-cross"},
    "D": {"role": "D", "branch_suffix": "track-D-zero"},
}


def create_worktree(branch_name):
    """Create a worktree using worktree_manager.py"""
    print(f"Creating worktree for {branch_name}...")
    result = subprocess.run(
        [sys.executable, str(WORKTREE_MANAGER), "new", branch_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"{RED}Failed to create worktree: {result.stderr}{RESET}")
        return None

    # Parse output to find path
    # Expected output: "Path:   /path/to/worktree"
    for line in result.stdout.splitlines():
        if "Path:" in line:
            return line.split("Path:")[1].strip()
    return None


def launch_terminal(worktree_path, role, goal, context):
    """Launch a new Terminal window running the agent."""
    cmd = f"""
    cd "{worktree_path}" && \
    clear && \
    python3 "{SWARM_AGENT}" {role} "{goal}" --context "{context}"
    """

    # AppleScript to open new window and run command
    apple_script = f"""
    tell application "Terminal"
        do script "{cmd}"
        activate
    end tell
    """

    subprocess.run(["osascript", "-e", apple_script])


def main():
    parser = argparse.ArgumentParser(description="Parallel Swarm Launcher")
    parser.add_argument("goal", help="The primary objective for the swarm")
    parser.add_argument(
        "base_branch", help="Base name for the branches (e.g., 'feature-login')"
    )
    parser.add_argument("--context", default="", help="Additional context")
    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}🚀 LAUNCHING NATIVE SWARM (Protocol 101){RESET}")
    print(f"Objective: {args.goal}")
    print(f"Base Branch: {args.base_branch}\n")

    worktrees = {}

    # 1. Create Worktrees
    for role, config in TRACKS.items():
        branch_name = f"{args.base_branch}-{config['branch_suffix']}"
        path = create_worktree(branch_name)
        if path:
            worktrees[role] = path
            print(f"{GREEN}✓ Track {role} prepared{RESET}")
        else:
            print(f"{RED}✗ Track {role} failed setup{RESET}")

    print(f"\n{YELLOW}Spawning Agents...{RESET}")
    time.sleep(1)

    # 2. Launch Terminals
    for role, path in worktrees.items():
        launch_terminal(path, role, args.goal, args.context)
        time.sleep(0.5)  # Stagger launch

    print(f"\n{GREEN}✅ Swarm Active. Check your Terminal windows.{RESET}\n")


if __name__ == "__main__":
    main()
