#!/usr/bin/env python3
"""
populate_forward_lineage.py — Populate next_session field across all session logs
==================================================================================

Reads all session logs, builds a session graph, and populates the `next_session`
field to complete the bidirectional lineage chain.

Usage:
    python3 .agent/scripts/populate_forward_lineage.py
    python3 .agent/scripts/populate_forward_lineage.py --dry-run
"""

import os
import sys
import re
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
ARCHIVE_DIR = LOGS_DIR / "archive"

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def collect_all_sessions() -> list[Path]:
    """Collect all session files from main dir and archive."""
    files = []
    
    for f in LOGS_DIR.glob("*.md"):
        if re.match(r'\d{4}-\d{2}-\d{2}-session-\d+\.md', f.name):
            files.append(f)
    
    if ARCHIVE_DIR.exists():
        for f in ARCHIVE_DIR.glob("*.md"):
            if re.match(r'\d{4}-\d{2}-\d{2}-session-\d+\.md', f.name):
                files.append(f)
    
    return files


def parse_session_key(filename: str) -> tuple[str, int]:
    """Extract (date, session_num) from filename."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})-session-(\d+)\.md', filename)
    if match:
        return (match.group(1), int(match.group(2)))
    return ("", 0)


def build_lineage_graph(files: list[Path]) -> dict[str, str]:
    """
    Build a mapping of session_id -> next_session_id.
    Returns dict where key is session, value is the next session in sequence.
    """
    # Sort all sessions by date + number
    sessions = []
    for f in files:
        date, num = parse_session_key(f.name)
        if date:
            session_id = f"{date}-session-{num:02d}"
            sessions.append((date, num, session_id, f))
    
    sessions.sort(key=lambda x: (x[0], x[1]))
    
    # Build forward links
    next_map = {}
    for i in range(len(sessions) - 1):
        current_id = sessions[i][2]
        next_id = sessions[i + 1][2]
        next_map[current_id] = next_id
    
    return next_map, {s[2]: s[3] for s in sessions}


def update_next_session(filepath: Path, next_session: str, dry_run: bool = False) -> bool:
    """Update the next_session field in a session log."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return False
    
    # Check if file has YAML frontmatter
    if not content.startswith('---\n'):
        return False
    
    # Find the YAML frontmatter section
    yaml_end = content.find('\n---\n', 4)
    if yaml_end == -1:
        return False
    
    yaml_section = content[:yaml_end]
    body = content[yaml_end:]
    
    # Check if next_session is already populated with a real value
    current_match = re.search(r'^next_session:\s*(.*)$', yaml_section, re.MULTILINE)
    if current_match:
        current_value = current_match.group(1).strip()
        # Skip if already has a session value
        if current_value and current_value != 'null' and current_value.startswith('20'):
            return False
    
    # Replace empty next_session with the linked value
    new_yaml = re.sub(
        r'^next_session:\s*$',
        f'next_session: {next_session}',
        yaml_section,
        flags=re.MULTILINE
    )
    
    # Also handle null value
    new_yaml = re.sub(
        r'^next_session:\s*null\s*$',
        f'next_session: {next_session}',
        new_yaml,
        flags=re.MULTILINE
    )
    
    new_content = new_yaml + body
    
    if new_content == content:
        return False  # No change made
    
    if not dry_run:
        filepath.write_text(new_content, encoding='utf-8')
    
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}📊 FORWARD LINEAGE POPULATION{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")
    
    if dry_run:
        print(f"{YELLOW}[DRY-RUN MODE]{RESET}\n")
    
    # Collect files
    files = collect_all_sessions()
    print(f"Found {len(files)} session files\n")
    
    # Build graph
    next_map, id_to_path = build_lineage_graph(files)
    print(f"Built lineage graph with {len(next_map)} forward links\n")
    
    # Update files
    updated = 0
    skipped = 0
    
    for session_id, next_session in next_map.items():
        filepath = id_to_path.get(session_id)
        if not filepath:
            continue
        
        if update_next_session(filepath, next_session, dry_run=dry_run):
            updated += 1
            if updated <= 10 or updated % 50 == 0:
                print(f"{GREEN}[{updated}] {session_id} → {next_session}{RESET}")
        else:
            skipped += 1
    
    # Summary
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{BOLD}Forward Lineage Complete{RESET}")
    print(f"  ✅ Updated: {updated}")
    print(f"  ⏭️  Skipped: {skipped} (already populated or no frontmatter)")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
