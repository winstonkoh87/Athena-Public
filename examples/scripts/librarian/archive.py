#!/usr/bin/env python3
"""
Athena Librarian - Unified Archiver Dispatcher
Routes URLs to the appropriate archiver (Article or YouTube).
"""

import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

LIBRARIAN_DIR = Path(__file__).resolve().parent


YOUTUBE_DOMAINS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def is_youtube(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname or ""
    return hostname in YOUTUBE_DOMAINS


def archive(url):
    print(f"📚 Librarian receiving: {url}")

    # Simple check: determine script based on URL domain
    if is_youtube(url):
        script_name = "archive_youtube.py"
        print("👉 Detected YouTube Video")
    else:
        script_name = "archive_article.py"
        print("👉 Detected Web Article")

    script_path = LIBRARIAN_DIR / script_name

    if not script_path.exists():
        print(f"❌ Error: Script {script_name} not found in {LIBRARIAN_DIR}")
        sys.exit(1)

    try:
        # Use sys.executable to ensure we use the same python interpreter
        subprocess.run([sys.executable, str(script_path), url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Archiving failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 .agent/scripts/librarian/archive.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    archive(url)
