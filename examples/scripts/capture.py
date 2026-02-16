#!/usr/bin/env python3
"""
capture.py — Shower Thought Capture Pipeline
=============================================

Zero-friction idea capture from CLI.
Auto-tags, appends to daily capture log, optionally syncs to Supabase.

Usage:
    python3 capture.py "my brilliant idea"              # Capture a thought
    python3 capture.py "trading insight" --tags trading  # With explicit tags
    python3 capture.py --list                            # Show today's captures
    python3 capture.py --sync                            # Sync captures to Supabase
    python3 capture.py --dry-run "test thought"          # Preview without saving

Alias suggestion:
    alias think='python3 ~/Desktop/Project\\ Athena/.agent/scripts/capture.py'
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPTURES_DIR = PROJECT_ROOT / ".context" / "inputs" / "captures"

# Auto-tag keyword map
AUTO_TAG_RULES = {
    "trading": [
        "trade",
        "eurusd",
        "forex",
        "pip",
        "risk",
        "position",
        "chart",
        "setup",
    ],
    "psychology": [
        "schema",
        "pattern",
        "attachment",
        "limerence",
        "trauma",
        "boundary",
    ],
    "coding": ["script", "bug", "api", "deploy", "function", "refactor", "code"],
    "strategy": ["protocol", "framework", "roadmap", "plan", "architecture"],
    "content": ["reddit", "post", "viral", "seo", "marketing", "audience"],
    "personal": ["feeling", "grateful", "frustrated", "insight", "realized", "learned"],
    "business": ["client", "pricing", "revenue", "consultancy", "service", "customer"],
    "idea": ["what if", "maybe", "could we", "interesting", "shower thought"],
}


# ── Auto-Tagger ───────────────────────────────────────────────────────────────


def auto_tag(text: str) -> list[str]:
    """Extract tags from text based on keyword matching."""
    text_lower = text.lower()
    tags = set()

    for tag, keywords in AUTO_TAG_RULES.items():
        if any(k in text_lower for k in keywords):
            tags.add(tag)

    # Always add 'capture' tag
    tags.add("capture")

    return sorted(tags)


# ── Capture Writer ────────────────────────────────────────────────────────────


def capture_thought(
    thought: str,
    tags: list[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Capture a thought to the daily log.

    Returns:
        dict with capture metadata
    """
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H:%M:%S")
    day_name = now.strftime("%A")

    # Auto-tag if no explicit tags
    detected_tags = auto_tag(thought)
    if tags:
        detected_tags = sorted(set(detected_tags) | set(tags))

    # Build capture entry
    tag_str = " ".join(f"#{t}" for t in detected_tags)
    entry = f"\n### ⚡ {timestamp}\n\n{thought}\n\n*Tags: {tag_str}*\n"

    # Target file
    capture_file = CAPTURES_DIR / f"{today}.md"
    result = {
        "thought": thought,
        "tags": detected_tags,
        "timestamp": timestamp,
        "file": str(capture_file),
        "is_new_file": not capture_file.exists(),
    }

    if dry_run:
        print(f"🔍 [DRY RUN] Would capture to: {capture_file}")
        print(f"   Tags: {tag_str}")
        print(f"   Entry:\n{entry}")
        return result

    # Create directory and file
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    if not capture_file.exists():
        # Create new daily file with header
        header = f"""---
date: {today}
type: capture_log
---

# 💡 Captures — {day_name}, {today}

"""
        capture_file.write_text(header, encoding="utf-8")

    # Append entry
    with open(capture_file, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"⚡ Captured! [{timestamp}] {tag_str}")
    print(f"   📁 {capture_file.name}")

    return result


# ── List Today's Captures ─────────────────────────────────────────────────────


def list_captures(date: str = None):
    """List all captures from a given date (default: today)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    capture_file = CAPTURES_DIR / f"{date}.md"

    if not capture_file.exists():
        print(f"📭 No captures for {date}")
        return

    content = capture_file.read_text(encoding="utf-8")
    entries = re.findall(
        r"### ⚡ (\d{2}:\d{2}:\d{2})\n\n(.+?)\n\n\*Tags:", content, re.DOTALL
    )

    print(f"💡 Captures for {date}:")
    print("-" * 40)
    for time, thought in entries:
        print(f"  ⚡ [{time}] {thought.strip()[:80]}")

    print(f"\nTotal: {len(entries)} captures")


# ── Sync to Supabase ──────────────────────────────────────────────────────────


def sync_captures():
    """Sync all capture files to Supabase."""
    try:
        # Add src to path for SDK imports
        src_path = PROJECT_ROOT / "Athena-Public" / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from athena.memory.sync import sync_directory

        if not CAPTURES_DIR.exists():
            print("📭 No captures directory found")
            return

        sync_directory(CAPTURES_DIR, "insights", recursive=False)
        print("✅ Captures synced to Supabase (insights table)")

    except ImportError:
        print(
            "⚠️ Athena SDK not available for sync. Captures saved locally only.",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"❌ Sync failed: {e}", file=sys.stderr)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Athena Shower Thought Capture",
        epilog="Alias: alias think='python3 ~/Desktop/Project\\ Athena/.agent/scripts/capture.py'",
    )
    parser.add_argument("thought", nargs="?", help="The thought to capture")
    parser.add_argument("--tags", nargs="+", help="Explicit tags")
    parser.add_argument("--list", action="store_true", help="List today's captures")
    parser.add_argument("--sync", action="store_true", help="Sync captures to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    args = parser.parse_args()

    if args.list:
        list_captures()
    elif args.sync:
        sync_captures()
    elif args.thought:
        capture_thought(args.thought, tags=args.tags, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
