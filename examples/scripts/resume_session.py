#!/usr/bin/env python3
"""
resume_session.py — Recover interrupted session context

Usage:
    python3 .agent/scripts/resume_session.py

Returns context from the most recent incomplete session.
"""

import os
import re
import glob
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def parse_session_key(filepath):
    """Extracts (date, session_number) tuple for sorting."""
    filename = os.path.basename(filepath)
    match = re.match(r'(\d{4}-\d{2}-\d{2})-session-(\d+)\.md', filename)
    if match:
        return (match.group(1), int(match.group(2)))
    return ("0000-00-00", 0)


def find_incomplete_session() -> Path | None:
    """Find the most recent session that is still in progress."""
    if not LOGS_DIR.exists():
        return None
    
    files = [f for f in glob.glob(str(LOGS_DIR / "*.md")) 
             if "session" in os.path.basename(f).lower()]
    
    if not files:
        return None
    
    # Sort by recency
    files.sort(key=parse_session_key, reverse=True)
    
    # Check if most recent is incomplete
    latest_file = Path(files[0])
    content = latest_file.read_text(encoding='utf-8')
    
    # Check status
    if "**Status**: ⏳ In Progress" in content or "**Status**: ..." in content:
        return latest_file
    if "**Status**: ✅ Closed" in content:
        return None  # Session was properly closed
    
    # Default: assume incomplete if status line not found
    if "## Session Closed" in content and "✅ Closed" not in content:
        return latest_file
    
    return None


def extract_checkpoints(content: str, limit: int = 5) -> list:
    """Extract recent checkpoints from session content."""
    checkpoints = []
    pattern = r"### ⚡ Checkpoint \[([^\]]+)\]\n(.*?)(?=\n###|\n## |$)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for time_str, body in matches[-limit:]:
        summary = body.strip().split('\n')[0][:80]  # First line, truncated
        checkpoints.append((time_str, summary))
    
    return checkpoints


def extract_action_items(content: str) -> list:
    """Extract pending action items."""
    items = []
    
    # Look for Action Items section with Pending status
    in_action = False
    for line in content.split('\n'):
        if "Action Items" in line and line.startswith("#"):
            in_action = True
            continue
        if in_action and line.startswith("#"):
            break
        if in_action and "Pending" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1] and parts[1] != "Action":
                items.append(parts[1])
    
    return items


def count_exchanges(content: str) -> int:
    """Count number of checkpoint entries (proxy for exchanges)."""
    return content.count("### ⚡ Checkpoint")


def main():
    session_file = find_incomplete_session()
    
    if not session_file:
        print(f"\n{YELLOW}No interrupted session found.{RESET}")
        print(f"{DIM}All sessions are closed. Use /start to begin a new session.{RESET}\n")
        return 1
    
    content = session_file.read_text(encoding='utf-8')
    filename = session_file.name
    
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}🔄 RESUMING SESSION: {filename}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")
    
    # Extract Focus
    for line in content.split('\n'):
        if line.startswith("**Focus**:"):
            focus = line.replace("**Focus**:", "").strip()
            if focus and focus != "...":
                print(f"🎯 Focus: {focus}\n")
            break
    
    # Checkpoints
    checkpoints = extract_checkpoints(content, 3)
    if checkpoints:
        print(f"{BOLD}📋 Last {len(checkpoints)} Checkpoints:{RESET}")
        for time_str, summary in checkpoints:
            print(f"   [{time_str}] {summary}")
        print()
    
    # Action Items
    items = extract_action_items(content)
    if items:
        print(f"{BOLD}📌 Pending Action Items:{RESET}")
        for item in items[:5]:
            print(f"   - {item}")
        print()
    
    # Stats
    exchanges = count_exchanges(content)
    print(f"{DIM}⏰ Exchanges so far: {exchanges}{RESET}")
    
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{GREEN}✅ Context recovered. Continuing session.{RESET}")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
