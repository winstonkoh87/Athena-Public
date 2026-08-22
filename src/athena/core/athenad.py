"""
Athena Daemon (athenad)
=======================
Role: The Active OS Kernel.
Responsibilities:
  1.  File System Watcher (Polling) -> Updates SQLite Metadata
  2.  Health Monitor -> Self-healing
"""

import logging
import logging.handlers
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/athena/core -> ROOT
DB_PATH = PROJECT_ROOT / ".agent" / "inputs" / "athena.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# Watch Configuration (Filter only existing directories)
WATCH_DIRS = [
    p
    for p in [
        PROJECT_ROOT,  # Broad watch for root-level drift
        PROJECT_ROOT / ".context",
        PROJECT_ROOT / ".agent" / "skills",
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "Athena-Public",
    ]
    if p.exists()
]

EXCLUDED_PATTERNS = [
    "/Winston/",
    "/archive/",
    "/history/",
    "/.venv/",
    "/__pycache__/",
    "/.git/",
    "/lightrag_store/",
    "athenad.log",
    ".semantic_audit_log.json",
]

POLL_INTERVAL = 5
LOG_LEVEL = logging.INFO

# --- LOGGING SETUP (Rotating: 5MB max, 3 backups) ---
_log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] (athenad) %(message)s")
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_log_formatter)
_file_handler = logging.handlers.RotatingFileHandler(
    PROJECT_ROOT / "athenad.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
)
_file_handler.setFormatter(_log_formatter)

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[_stream_handler, _file_handler],
)


# --- UTILITIES ---
def calculate_checksum(filepath):
    """Fast checksum of file stats to detect changes."""
    try:
        stats = os.stat(filepath)
        return f"{stats.st_size}-{stats.st_mtime}"
    except FileNotFoundError:
        return None


def extract_tags(filepath):
    """Extract tags from Markdown."""
    tags = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tags = re.findall(r"#([\w-]+)", content)
    except Exception as e:
        logging.warning(f"Failed to read tags from {filepath}: {e}")
    return list(set(tags))


# --- DAEMON CORE ---
class AthenaDaemon:
    def __init__(self):
        self._conn = None

    def start(self):
        logging.info("🛡️  Athena Daemon (Titanium) Starting...")

        # 1. Initialize DB
        if not DB_PATH.parent.exists():
            DB_PATH.parent.mkdir(parents=True)
        self.init_db()

        # 2. Main Loop

        logging.info(f"👀 Watching: {[str(d) for d in WATCH_DIRS]}")
        try:
            self.watch_loop()
        except KeyboardInterrupt:
            logging.info("Stopping...")

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        if not DB_PATH.exists() and SCHEMA_PATH.exists():
            conn = self.get_db_connection()
            with open(SCHEMA_PATH) as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()
            logging.info("Initialized Metadata DB.")

    def watch_loop(self):
        conn = self.get_db_connection()
        while True:
            changes = 0
            for watch_dir in WATCH_DIRS:
                if not watch_dir.exists():
                    continue

                for root, _, files in os.walk(watch_dir):
                    if any(p in root for p in EXCLUDED_PATTERNS):
                        continue

                    for file in files:
                        if not file.endswith(".md"):
                            continue

                        filepath = os.path.join(root, file)
                        if any(p in filepath for p in EXCLUDED_PATTERNS):
                            continue

                        if self.check_and_update(conn, filepath):
                            changes += 1

            if changes > 0:
                conn.commit()
                logging.info(f"Processed {changes} file updates.")

            time.sleep(POLL_INTERVAL)

    def check_and_update(self, conn, filepath):
        """Returns True if file updated."""
        checksum = calculate_checksum(filepath)
        if not checksum:
            return False

        cursor = conn.cursor()
        cursor.execute("SELECT checksum FROM files WHERE path = ?", (filepath,))
        row = cursor.fetchone()

        if not row or row["checksum"] != checksum:
            # Index Metadata
            cursor.execute(
                "INSERT OR REPLACE INTO files (path, last_modified, checksum, type) VALUES (?, ?, ?, ?)",
                (filepath, time.time(), checksum, "text/markdown"),
            )

            # Index Tags
            tags = extract_tags(filepath)
            cursor.execute("DELETE FROM file_tags WHERE file_path = ?", (filepath,))
            for tag in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT OR IGNORE INTO file_tags (file_path, tag_id) VALUES (?, ?)",
                    (filepath, tag_id),
                )
            return True
        return False


if __name__ == "__main__":
    daemon = AthenaDaemon()
    daemon.start()
