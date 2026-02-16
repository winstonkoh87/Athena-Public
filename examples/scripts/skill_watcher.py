#!/usr/bin/env python3
"""
skill_watcher.py — Auto-regenerate indices when protocols change.

Stolen from: Claude Code v2.1.0 "skill hot-reload" pattern.

Usage:
    python3 skill_watcher.py          # Watch mode (runs indefinitely)
    python3 skill_watcher.py --once   # Single pass (for cron/hooks)

Dependencies:
    pip install watchdog
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Try to import watchdog, provide helpful message if missing
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object  # Dummy base class

PROJECT_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "scripts"


class SkillChangeHandler(FileSystemEventHandler):
    """Handler for skill/protocol file changes."""

    def __init__(self):
        self.last_trigger = 0
        self.debounce_seconds = 2  # Prevent rapid-fire triggers

    def on_any_event(self, event):
        # Only care about .md files
        if not event.src_path.endswith(".md"):
            return

        # Ignore directory events
        if event.is_directory:
            return

        # Debounce
        now = time.time()
        if now - self.last_trigger < self.debounce_seconds:
            return
        self.last_trigger = now

        print(f"🔄 Change detected: {Path(event.src_path).name}")
        regenerate_indices()


def regenerate_indices():
    """Run index regeneration scripts."""
    print("📝 Regenerating TAG_INDEX.md...")

    tag_script = SCRIPTS_DIR / "generate_tag_index.py"
    if tag_script.exists():
        result = subprocess.run(
            [sys.executable, str(tag_script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ TAG_INDEX.md updated")
        else:
            print(f"❌ Error: {result.stderr}")
    else:
        print(f"⚠️  Script not found: {tag_script}")


def watch_mode():
    """Run in continuous watch mode."""
    if not WATCHDOG_AVAILABLE:
        print("❌ watchdog package required for watch mode")
        print("   Install: pip install watchdog")
        sys.exit(1)

    print(f"👁️  Watching: {SKILLS_DIR}")
    print("   Press Ctrl+C to stop")

    handler = SkillChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(SKILLS_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Watcher stopped")
    observer.join()


def single_pass():
    """Run a single regeneration pass."""
    print("🔄 Single pass mode")
    regenerate_indices()
    print("✅ Done")


def main():
    parser = argparse.ArgumentParser(
        description="Watch for skill/protocol changes and auto-regenerate indices"
    )
    parser.add_argument(
        "--once", action="store_true", help="Run single pass instead of watch mode"
    )
    args = parser.parse_args()

    if args.once:
        single_pass()
    else:
        watch_mode()


if __name__ == "__main__":
    main()
