import os
import sys
import gzip
import sqlite3
import argparse
import time
import urllib.request
import re
from pathlib import Path
import bz2

# Configuration
DATA_DIR = Path(".context/knowledge")
DB_FILE = DATA_DIR / "exocortex.db"
# Using DBPedia Long Abstracts (2022.12.01) - Validated available version
# This file contains the lead paragraphs of Wikipedia articles.
DBPEDIA_URL = "https://databus.dbpedia.org/dbpedia/text/long-abstracts/2022.12.01/long-abstracts_lang=en.ttl.bz2"
LOCAL_FILE = DATA_DIR / "long-abstracts_lang=en.ttl.bz2"


def ensure_dir():
    if not DATA_DIR.exists():
        try:
            os.makedirs(DATA_DIR)
            print(f"✅ Created directory: {DATA_DIR}")
        except OSError as e:
            print(f"❌ Error creating directory: {e}")
            sys.exit(1)


def download_dump():
    """Downloads the DBPedia Long Abstracts dump."""
    ensure_dir()

    if LOCAL_FILE.exists():
        print(f"✅ Dump already exists at {LOCAL_FILE}")
        return

    print(f"⬇️  Downloading DBPedia Long Abstracts (~890MB)...")
    print(f"   Source: {DBPEDIA_URL}")
    print("   This may take a while. Please wait...")

    try:

        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 1e2 / totalsize
                sys.stdout.write(
                    f"\r   ⬇️  Downloading: {percent:.1f}% ({readsofar / 1024 / 1024:.1f} MB)"
                )
                sys.stdout.flush()
            else:
                sys.stdout.write(
                    f"\r   ⬇️  Downloading: {readsofar / 1024 / 1024:.1f} MB"
                )
                sys.stdout.flush()

        urllib.request.urlretrieve(DBPEDIA_URL, LOCAL_FILE, reporthook)
        print(f"\n✅ Download complete: {LOCAL_FILE}")
    except Exception as e:
        print(f"\n❌ Download Failed: {e}")
        if LOCAL_FILE.exists():
            os.remove(LOCAL_FILE)


def build_index():
    """Builds a SQLite FTS index from the DBPedia TTL dump."""
    if not LOCAL_FILE.exists():
        print(
            f"❌ Dump not found. Run 'python3 .agent/scripts/exocortex.py download' first."
        )
        return

    print(f"⚡ Building Exocortex Index from DBPedia (SQLite)...")

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS abstracts")
        c.execute("CREATE VIRTUAL TABLE abstracts USING fts5(title, abstract, url)")

        start_time = time.time()
        count = 0
        batch = []

        # Regex to parse TTL lines: <resource> <property> "abstract"@en .
        # Resource: http://dbpedia.org/resource/Title
        # We want "Title" and the "Abstract"
        pattern = re.compile(
            r'^<http://dbpedia.org/resource/([^>]+)> <http://dbpedia.org/ontology/abstract> "(.*)"@en \.$'
        )

        # Use bz2 to read the compressed file directly
        # encoding='utf-8' is default but explicit is good. errors='replace' to avoid crashing on partial bad bytes
        with bz2.open(LOCAL_FILE, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                # Skip comments or prefixes or empty lines
                if not line or line.startswith("@") or line.startswith("#"):
                    continue

                match = pattern.match(line)
                if match:
                    title_raw = match.group(1)
                    abstract = match.group(2)

                    # Clean title: Underscores to spaces, decode URL encoding if needed (usually raw is fine)
                    title = title_raw.replace("_", " ")
                    url = f"https://en.wikipedia.org/wiki/{title_raw}"

                    # Unescape unicode sequences if present in TTL? Usually python handles utf-8.
                    # DBPedia might have \" escaped quotes.
                    abstract = abstract.replace('\\"', '"')

                    batch.append((title, abstract, url))

                    if len(batch) >= 5000:
                        c.executemany(
                            "INSERT INTO abstracts (title, abstract, url) VALUES (?, ?, ?)",
                            batch,
                        )
                        conn.commit()
                        count += len(batch)
                        sys.stdout.write(f"\r   Indexed {count} articles...")
                        sys.stdout.flush()
                        batch = []

        # Insert remaining
        if batch:
            c.executemany(
                "INSERT INTO abstracts (title, abstract, url) VALUES (?, ?, ?)", batch
            )
            conn.commit()
            count += len(batch)

        print(f"\n   ✅ Formatting Index...")
        c.execute("INSERT INTO abstracts(abstracts) VALUES('optimize')")
        conn.commit()

        duration = time.time() - start_time
        print(f"   🎉 Indexed {count} articles in {duration:.1f}s")
        if DB_FILE.exists():
            print(f"   💾 Database size: {DB_FILE.stat().st_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"\n   ❌ Indexing Failed: {e}")
    finally:
        if "conn" in locals():
            conn.close()


def search_db(term):
    """Searches the SQLite index."""
    if not DB_FILE.exists():
        print(
            "❌ Index not built. Run 'python3 .agent/scripts/exocortex.py index' first."
        )
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    start_time = time.time()

    # Sanitize term for FTS5: Wrap in double quotes to treat as a phrase
    # and escape existing double quotes.
    clean_term = f'"{term.replace('"', '""')}"'

    # FTS query syntax: column matches phrase
    query = "SELECT title, abstract, url FROM abstracts WHERE title MATCH ? OR abstract MATCH ? ORDER BY rank LIMIT 5"

    try:
        c.execute(query, (clean_term, clean_term))
        results = c.fetchall()
        duration = time.time() - start_time

        print(f"🔍 Exocortex Query: '{term}'")
        print(f"   ⏱️  {duration:.4f}s")

        if results:
            for r in results:
                print(f"   📜 \033[1m{r[0]}\033[0m")  # Bold title
                print(f"      {r[1][:300]}...")  # Show slightly more context
                print(f"      🔗 {r[2]}\n")
        else:
            print("   🚫 No results found.")

    except Exception as e:
        print(f"   ❌ Search Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Exocortex: Wikipedia/DBPedia Knowledge Base"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Commands
    subparsers.add_parser("download")
    subparsers.add_parser("index")

    parser_search = subparsers.add_parser("search")
    parser_search.add_argument("term", help="Term to search for")

    args = parser.parse_args()

    if args.command == "download":
        download_dump()
    elif args.command == "index":
        build_index()
    elif args.command == "search":
        if not args.term:
            print("❌ Error: Search term required.")
        else:
            search_db(args.term)
    else:
        parser.print_help()
