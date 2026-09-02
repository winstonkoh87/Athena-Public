#!/usr/bin/env python3
"""
boot_handoff.py — The Wake-Up Loop (Protocol 417)
=================================================
Manages the "wake-up.md" file which serves as the continuity bridge
between sessions.
"""

import sys
from datetime import datetime
from pathlib import Path

# Setup Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_DIR = PROJECT_ROOT / ".context"
WAKE_UP_FILE = CONTEXT_DIR / "wake_up.md"


def init_handoff():
    """Reads the handoff note at session start."""
    if not WAKE_UP_FILE.exists():
        print(f"⚠️  No wake-up file found at {WAKE_UP_FILE}. Creating empty...")
        WAKE_UP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(WAKE_UP_FILE, "w") as f:
            f.write("# Wake-Up Handoff Note\n\nNo pending items from previous session.")

    print("\n" + "=" * 60)
    print("🌅 WAKE-UP HANDOFF REPORT")
    print("=" * 60)

    with open(WAKE_UP_FILE) as f:
        content = f.read()
        print(content)

    print("=" * 60 + "\n")


def update_handoff(new_content):
    """Updates the handoff note at session end."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    template = f"""# Wake-Up Handoff Note
Last Updated: {timestamp}

{new_content}
"""
    with open(WAKE_UP_FILE, "w") as f:
        f.write(template)
        print("✅ Handoff note updated for next session.")


def main():
    if len(sys.argv) > 1:
        # If args provided, it's an update
        content = " ".join(sys.argv[1:])
        update_handoff(content)
    else:
        # If no args, it's a read (boot)
        init_handoff()


if __name__ == "__main__":
    main()
