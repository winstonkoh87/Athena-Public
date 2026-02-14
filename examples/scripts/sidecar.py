"""
Athena Sidecar (The Watcher)
Purpose: Monitors local markdown files and updates the SQLite index.
Mode: Polling (Zero Dependency)
"""

import os
import time
import sqlite3
import hashlib
import re
import sys

# CONFIGURATION
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "inputs", "athena.db"
)
SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "inputs", "schema.sql"
)
WATCH_DIRS = [
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".context"
        )
    ),
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".agent/skills"
        )
    ),
]

# EXCLUSIONS: Directories to skip during indexing
# - Personal data: Winston/
# - Public repo clone: Athena-Public/ (indexed separately)
# - Archive: archive/ (deprecated scripts)
# - History: history/ (old implementation plans)
EXCLUDED_PATTERNS = [
    "/Winston/",
    "/Athena-Public/",
    "/archive/",
    "/history/",
    "/.venv/",
    "/__pycache__/",
    "/.git/",
]

POLL_INTERVAL = 5  # Seconds


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def calculate_checksum(filepath):
    """Fast checksum of file stats to detect changes"""
    try:
        stats = os.stat(filepath)
        return f"{stats.st_size}-{stats.st_mtime}"
    except FileNotFoundError:
        return None


def extract_metadata(filepath):
    """Extract tags and links from Markdown"""
    tags = []
    links = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Extract Hash Tags #tag
            # Simple regex, can be improved
            tags = re.findall(r"#([\w-]+)", content)

            # Extract Links [Link](pointer)
            # Not implementing full link graph yet, just placeholder
            pass

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return list(set(tags)), links


def index_file(conn, filepath):
    """Update DB with file metadata"""
    checksum = calculate_checksum(filepath)
    if not checksum:
        return  # File deleted during process

    print(f"Indexing: {os.path.basename(filepath)}")

    # 1. Update Files Table
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO files (path, last_modified, checksum, type)
        VALUES (?, ?, ?, ?)
    """,
        (filepath, time.time(), checksum, "text/markdown"),
    )

    # 2. Update Tags
    tags, _ = extract_metadata(filepath)

    # Clear old tags
    cursor.execute("DELETE FROM file_tags WHERE file_path = ?", (filepath,))

    for tag in tags:
        # Ensure tag exists
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        # Get tag ID
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cursor.fetchone()[0]
        # Link
        cursor.execute(
            "INSERT OR IGNORE INTO file_tags (file_path, tag_id) VALUES (?, ?)",
            (filepath, tag_id),
        )

    conn.commit()


def scan_and_index():
    conn = get_db_connection()
    changes_detected = 0

    for watch_dir in WATCH_DIRS:
        if not os.path.exists(watch_dir):
            continue

        for root, _, files in os.walk(watch_dir):
            # Skip excluded directories
            if any(pattern in root for pattern in EXCLUDED_PATTERNS):
                continue

            for file in files:
                if not file.endswith(".md"):
                    continue

                filepath = os.path.join(root, file)

                # Double-check exclusion at file level
                if any(pattern in filepath for pattern in EXCLUDED_PATTERNS):
                    continue

                current_checksum = calculate_checksum(filepath)

                # Check against DB
                cursor = conn.cursor()
                cursor.execute("SELECT checksum FROM files WHERE path = ?", (filepath,))
                row = cursor.fetchone()

                if not row or row["checksum"] != current_checksum:
                    try:
                        index_file(conn, filepath)
                        changes_detected += 1
                    except Exception as e:
                        print(f"Failed to index {filepath}: {e}")

    if changes_detected > 0:
        print(f"✅ Sidecar: Updated {changes_detected} files.")

    conn.close()


def main():
    print(f"🛡️ Athena Sidecar (Watcher) Online.")
    print(f"   Watching: {WATCH_DIRS}")

    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        print("Initializing DB...")
        init_db()

    while True:
        try:
            scan_and_index()
        except Exception as e:
            print(f"Sidecar Error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
