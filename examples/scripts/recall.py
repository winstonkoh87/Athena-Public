#!/usr/bin/env python3
"""
recall.py — Local Recall Memory (SQLite FTS5)
=============================================
"The Heist" from Claudest.
Implements a local, sovereign, fast keyword search for session logs.
Uses SQLite FTS5 for efficient full-text indexing.

Usage:
  python3 recall.py --sync              # Index new sessions
  python3 recall.py "search query"      # Search specific terms
  python3 recall.py --stats             # Show index stats
"""

import argparse
import re
import sqlite3
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEMORY_DB_PATH = PROJECT_ROOT / ".athena" / "memory.db"
SESSION_LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"


def get_db():
    """Connect to SQLite database, initializing schema if needed."""
    MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row

    # Enable FTS5
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
            filename,
            date,
            content,
            tokenize='porter'
        );
    """)

    # Meta table to track indexed files
    conn.execute("""
        CREATE TABLE IF NOT EXISTS indexed_files (
            filename TEXT PRIMARY KEY,
            last_modified TIMESTAMP
        );
    """)

    return conn


def parse_frontmatter(content):
    """Extract date from frontmatter if present."""
    date_match = re.search(
        r"^date:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE | re.IGNORECASE
    )
    if date_match:
        return date_match.group(1)
    return None


def sync_memory(force=False):
    """Scan session logs and update the index."""
    conn = get_db()
    cursor = conn.cursor()

    print(f"🧠 Syncing Recall Memory from {SESSION_LOGS_DIR}...")

    # Get all markdown files
    files = list(SESSION_LOGS_DIR.rglob("*.md"))
    updated = 0

    for file_path in files:
        filename = file_path.name
        mtime = file_path.stat().st_mtime

        # Check if already indexed and unchanged
        cursor.execute(
            "SELECT last_modified FROM indexed_files WHERE filename = ?", (filename,)
        )
        row = cursor.fetchone()

        if row and not force and row[0] >= mtime:
            continue

        # Read content
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Failed to read {filename}: {e}")
            continue

        # Parse metadata
        date = parse_frontmatter(content)
        if not date:
            # Fallback to file creation date or filename if it contains date
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
            if date_match:
                date = date_match.group(1)
            else:
                date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        # Update FTS (Delete insert pattern to handle updates)
        cursor.execute("DELETE FROM sessions_fts WHERE filename = ?", (filename,))
        cursor.execute(
            "INSERT INTO sessions_fts (filename, date, content) VALUES (?, ?, ?)",
            (filename, date, content),
        )

        # Update meta table
        cursor.execute(
            "REPLACE INTO indexed_files (filename, last_modified) VALUES (?, ?)",
            (filename, mtime),
        )

        updated += 1
        print(f"  + Indexed: {filename} ({date})")

    conn.commit()
    conn.close()

    if updated > 0:
        print(f"✅ Indexed {updated} new/modified sessions.")
    else:
        print("✅ Index is up to date.")


def search_memory(query, limit=10):
    """Search the FTS index."""
    conn = get_db()
    cursor = conn.cursor()

    print(f"🔍 Recalling: '{query}'...")
    print("-" * 60)

    try:
        # FTS5 search with snippet
        cursor.execute(
            """
            SELECT 
                filename, 
                date, 
                snippet(sessions_fts, 2, '<b>', '</b>', '...', 15) as extract,
                rank
            FROM sessions_fts
            WHERE sessions_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """,
            (query, limit),
        )

        results = cursor.fetchall()

        if not results:
            print("No matching memories found.")
            return

        for row in results:
            clean_extract = row["extract"].replace("\n", " ").strip()
            print(f"📅 {row['date']} | 📄 {row['filename']}")
            print(f"   ...{clean_extract}...\n")

    except sqlite3.OperationalError as e:
        print(f"❌ Search Error: {e}")
        print("Tip: Use simple keywords. For complex queries, use quote marks.")

    conn.close()


def show_stats():
    """Show database statistics."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM sessions_fts")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT sum(length(content)) FROM sessions_fts")
    size = cursor.fetchone()[0] or 0

    print("📊 Recall Memory Stats")
    print(f"   Total Sessions: {count}")
    print(f"   Total Content:  {size / 1024:.2f} KB")
    print(f"   Database Path:  {MEMORY_DB_PATH}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Athena Recall Memory")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--sync", action="store_true", help="Sync index with files")
    parser.add_argument("--stats", action="store_true", help="Show index stats")

    args = parser.parse_args()

    if args.sync:
        sync_memory()
    elif args.stats:
        show_stats()
    elif args.query:
        search_memory(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
