#!/usr/bin/env python3
"""
Athena Librarian - Unified Archiver Dispatcher
Routes URLs to the appropriate archiver (Article or YouTube).
"""

import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

LIBRARIAN_DIR = Path(__file__).resolve().parent


def is_youtube(url):
    hostname = urlparse(url).hostname or ""
    youtube_domains = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
    return hostname in youtube_domains


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
