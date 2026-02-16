#!/usr/bin/env python3
"""
Athena Librarian - YouTube Archiver
Fetches YouTube transcripts, summarizes them with AI, and saves to the Library.
"""

import sys
import os
import re
import json
import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add parent directory to path to import gemini_client
sys.path.append(str(Path(__file__).resolve().parent.parent))
try:
    from gemini_client import get_client
except ImportError:
    print("❌ Error: Could not import gemini_client.")
    sys.exit(1)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print(
        "❌ Error: youtube-transcript-api not installed. Run: pip install youtube-transcript-api"
    )
    sys.exit(1)

LIBRARY_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / ".context"
    / "library"
    / "videos"
)


def clean_filename(title):
    """Convert title to valid filename slug."""
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:100]


def extract_video_id(url):
    """Extract 11-char video ID from URL."""
    parsed = urlparse(url)
    if parsed.hostname == "youtu.be":
        return parsed.path[1:]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            p = parse_qs(parsed.query)
            return p["v"][0]
        if parsed.path[:7] == "/embed/":
            return parsed.path.split("/")[2]
        if parsed.path[:3] == "/v/":
            return parsed.path.split("/")[2]
    return None


def get_transcript_text(video_id):
    """Fetch transcript and combine into text."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine text
        full_text = " ".join([t["text"] for t in transcript_list])
        return full_text
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return None


def enrich_video_metadata(transcript_text, video_id):
    """Uses Gemini to summarize and extract metadata."""
    client = get_client()

    prompt = f"""
    You are an expert Video Librarian. Analyze the following YouTube transcript.
    
    Video ID: {video_id}
    Transcript (truncated to first 15k chars):
    {transcript_text[:15000]}
    
    Extract the following metadata in strict JSON format:
    {{
        "title": "Inferred Video Title (make it descriptive)",
        "channel": "Inferred Channel/Speaker Name (if mentioned, else 'Unknown')",
        "summary": "A concise 3-sentence summary of the video content",
        "key_takeaways": ["point 1", "point 2", "point 3"],
        "tags": ["tag1", "tag2", "tag3"] (max 5),
        "topics": ["topic1", "topic2"]
    }}
    
    Return ONLY VALID JSON.
    """

    try:
        print("🧠 Analyzing transcript with Gemini...")
        response = client.generate(prompt)
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        return data
    except Exception as e:
        print(f"⚠️ AI Analysis failed: {e}")
        return {
            "title": f"YouTube Video {video_id}",
            "channel": "Unknown",
            "summary": "AI extraction failed.",
            "key_takeaways": [],
            "tags": ["video"],
            "topics": [],
        }


def save_video(url):
    print(f"📥 Archiving YouTube: {url}")

    video_id = extract_video_id(url)
    if not video_id:
        print("❌ Invalid YouTube URL")
        sys.exit(1)

    print(f"✅ Video ID: {video_id}")

    # 1. Fetch Transcript
    transcript = get_transcript_text(video_id)
    if not transcript:
        print("⚠️ No transcript found. Archiving metadata only not supported yet.")
        sys.exit(1)

    print(f"✅ Transcript fetched ({len(transcript)} chars)")

    # 2. Enrich
    meta = enrich_video_metadata(transcript, video_id)

    # 3. Format Markdown
    today = datetime.date.today().isoformat()
    frontmatter = f"""---
title: "{meta["title"]}"
url: {url}
video_id: {video_id}
channel: {meta["channel"]}
date: {today}
tags: {json.dumps(meta["tags"])}
category: video
summary: "{meta["summary"]}"
---

# {meta["title"]}

> **Channel**: {meta["channel"]}
> **Summary**: {meta["summary"]}

## Key Takeaways
{chr(10).join([f"- {t}" for t in meta["key_takeaways"]])}

---

## Transcript (Auto-Generated)

{transcript}
"""

    # 4. Save
    slug = clean_filename(meta["title"])
    filename = f"{today}-{slug}.md"

    LIBRARY_PATH.mkdir(parents=True, exist_ok=True)
    file_path = LIBRARY_PATH / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"💾 Saved to: {file_path}")
    return file_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 archive_youtube.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    save_video(url)
