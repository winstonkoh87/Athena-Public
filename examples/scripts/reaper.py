"""
Athena Reaper (Sunset Protocol)
Purpose: Enforces Protocol 106 by archiving unused skill files.
"""

import os
import shutil
import time
import datetime

# CONFIGURATION
SKILLS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".agent/skills"
    )
)
ARCHIVE_DIR = os.path.join(SKILLS_DIR, "archive")
LOG_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        ".context/maintenance_log.md",
    )
)
DAYS_LIMIT = 90
SECONDS_LIMIT = DAYS_LIMIT * 24 * 60 * 60


def ensure_dirs():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)


def log_action(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"- [{timestamp}] 💀 REAPER: {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry.strip())


def reap_souls():
    ensure_dirs()
    now = time.time()
    count = 0

    print(f"💀 Reaper scanning {SKILLS_DIR} for > {DAYS_LIMIT} day dormancy...")

    for root, dirs, files in os.walk(SKILLS_DIR):
        # Skip archive itself
        if "archive" in root:
            continue

        for file in files:
            if not file.endswith(".md"):
                continue

            filepath = os.path.join(root, file)
            try:
                stats = os.stat(filepath)
                # Check Last Accessed (atime) or Modified (mtime) - whichever is later
                last_active = max(stats.st_atime, stats.st_mtime)

                if now - last_active > SECONDS_LIMIT:
                    # Move to archive
                    relative_path = os.path.relpath(filepath, SKILLS_DIR)
                    target_path = os.path.join(ARCHIVE_DIR, os.path.basename(file))

                    # Avoid overwrite if possible, or force it
                    if os.path.exists(target_path):
                        base, ext = os.path.splitext(target_path)
                        target_path = f"{base}_{int(now)}{ext}"

                    shutil.move(filepath, target_path)
                    log_action(
                        f"Archived {relative_path} (Dormant {int((now - last_active) / 86400)} days)"
                    )
                    count += 1
            except Exception as e:
                print(f"Error checking {file}: {e}")

    if count == 0:
        print("✅ No souls to reap today.")
    else:
        print(f"💀 Reaped {count} files.")


if __name__ == "__main__":
    reap_souls()
