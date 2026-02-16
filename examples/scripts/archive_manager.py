#!/usr/bin/env python3
"""
archive_manager.py — The Cold Storage Janitor (Phase 2)

Purpose:
    Moves "stale" session logs (>30 days old) from the Hot Memory
    (.context/memories/session_logs) to Cold Storage (.context/archive/session_logs).

Physics:
    - Hot Memory: Active working set for Vector RAG.
    - Cold Storage: Accessible via grep/deep-search, but excluded from daily sync.
    - Hygiene: Prevents vector index bloat and improved query relevance.

Logic:
    1. Scan session_logs for YYYY-MM-DD pattern.
    2. Parse date.
    3. If (Now - Date) > 30 days:
       Move to .context/archive/session_logs/{YYYY}/{MM}/
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HOT_MEMORY_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
COLD_STORAGE_DIR = PROJECT_ROOT / ".context" / "archive" / "session_logs"


def get_session_date(filename: str) -> datetime:
    """Extract date from YYYY-MM-DD-session-XX.md filename."""
    try:
        # Assumes format starts with YYYY-MM-DD
        date_str = filename[:10]
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def archive_workspace(days: int = 30, dry_run: bool = False):
    """Execute the hygiene protocol."""
    print(f"🧹 Athena Archive Manager [Threshold={days} days] [DryRun={dry_run}]")

    if not HOT_MEMORY_DIR.exists():
        print("❌ Hot memory directory not found.")
        return

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"📅 Archiving logs from before: {cutoff_date.strftime('%Y-%m-%d')}")

    moved_count = 0
    errors = 0

    # Scan
    files = list(HOT_MEMORY_DIR.glob("*.md"))
    # Sort for cleaner logs
    files.sort(key=lambda x: x.name)

    for f in files:
        session_date = get_session_date(f.name)
        if not session_date:
            continue

        if session_date < cutoff_date:
            # Candidate for archival
            year = session_date.strftime("%Y")
            month = session_date.strftime("%m")

            target_dir = COLD_STORAGE_DIR / year / month
            target_file = target_dir / f.name

            if dry_run:
                print(
                    f"  🥶 [DRY] Would move {f.name} -> {target_dir.relative_to(PROJECT_ROOT)}"
                )
                moved_count += 1
            else:
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(f), str(target_file))
                    print(f"  🥶 Archived: {f.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to move {f.name}: {e}")
                    errors += 1

    print(f"\n✅ Hygiene Complete.")
    print(f"   Items Archived: {moved_count}")
    print(f"   Errors: {errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Archive Manager")
    parser.add_argument("--days", type=int, default=30, help="Age threshold in days")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without moving files"
    )
    args = parser.parse_args()

    archive_workspace(days=args.days, dry_run=args.dry_run)
