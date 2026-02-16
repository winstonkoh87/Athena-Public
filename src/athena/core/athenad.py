"""
Athena Daemon (athenad)
=======================
Role: The Active OS Kernel.
Responsibilities:
  1.  File System Watcher (Polling) -> Updates SQLite Metadata
  2.  Background Worker (Threading) -> Vectors Content into GraphRAG
  3.  Health Monitor -> Self-healing

Architecture:
  [Main Thread] --(Queue)--> [Indexer Thread]
       ^                          |
       | (File Change)            v
  [File System] <-------- [GraphRAG Store]
"""

import os
import time
import sqlite3
import hashlib
import re
import sys
import threading
import queue
import logging
import subprocess
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/athena/core -> ROOT
DB_PATH = PROJECT_ROOT / ".agent" / "inputs" / "athena.db"
SCHEMA_PATH = PROJECT_ROOT / ".agent" / "inputs" / "schema.sql"

# Watch Configuration
WATCH_DIRS = [
    PROJECT_ROOT,  # Broad watch for root-level drift
    PROJECT_ROOT / ".context",
    PROJECT_ROOT / ".agent" / "skills",
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "Athena-Public",
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


# --- LOGGING SETUP ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] (athenad) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "athenad.log"),
    ],
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
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tags = re.findall(r"#([\w-]+)", content)
    except Exception as e:
        logging.warning(f"Failed to read tags from {filepath}: {e}")
    return list(set(tags))


# --- WORKER: BACKGROUND INDEXER ---
class BackgroundIndexer(threading.Thread):
    def __init__(self, task_queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.wrapper_path = PROJECT_ROOT / ".agent" / "scripts" / "lightrag_wrapper.py"

    def run(self):
        logging.info("🧠 BackgroundIndexer: Online (Waiting for tasks...)")
        while True:
            try:
                filepath = self.task_queue.get()
                if filepath is None:
                    break

                self.index_file_in_graph(filepath)
                self.task_queue.task_done()
            except Exception as e:
                logging.error(f"Indexer Worker Crash: {e}")

    def index_file_in_graph(self, filepath):
        """Calls lightrag_wrapper.py to index the file."""
        if not self.wrapper_path.exists():
            logging.error(f"Missing LightRAG wrapper: {self.wrapper_path}")
            return

        try:
            # Read content to verify it's valid
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) < 50:  # Skip empty/stub files
                    return

            logging.info(f"🕸️  Graph Vectorizing: {Path(filepath).name}")

            # Call wrapper via subprocess to ensure isolation
            # usage: python3 lightrag_wrapper.py --insert "CONTENT"
            # Note: This is a bit inefficient (reloads model every time).
            # Optimization: In V2, import LightRAG directly. For V1 (Robustness), isolation is better.

            cmd = [
                sys.executable,
                str(self.wrapper_path),
                "--insert",
                f"File: {filepath}\nContent:\n{content}",
            ]

            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True,
                timeout=120,
            )
            logging.info(f"✅ Graph Updated: {Path(filepath).name}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Graph Indexing Failed: {e.stderr.decode()}")
        except Exception as e:
            logging.error(f"Graph Indexing Error: {e}")


# --- DAEMON CORE ---
class AthenaDaemon:
    def __init__(self):
        self.indexer_queue = queue.Queue()
        self.indexer_thread = BackgroundIndexer(self.indexer_queue)
        self._conn = None

    def start(self):
        logging.info("🛡️  Athena Daemon (Titanium) Starting...")

        # 1. Initialize DB
        if not DB_PATH.parent.exists():
            DB_PATH.parent.mkdir(parents=True)
        self.init_db()

        # 2. Start Worker
        self.indexer_thread.start()

        # 3. Main Loop
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
            with open(SCHEMA_PATH, "r") as f:
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
                            # TRIGGER: Add to Indexer Queue
                            self.indexer_queue.put(filepath)

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
