#!/usr/bin/env python3
"""
Athena Librarian - Smart Link Archiver
Fetches a URL, extracts content, enriches with AI metadata, and saves to the Library.
"""

import sys
import os
import re
import json
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Add parent directory to path to import gemini_client
sys.path.append(str(Path(__file__).resolve().parent.parent))
try:
    from gemini_client import get_client
except ImportError:
    print(
        "❌ Error: Could not import gemini_client. Make sure you are running this from the correct environment."
    )
    sys.exit(1)

LIBRARY_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / ".context"
    / "library"
    / "articles"
)


def clean_filename(title):
    """Convert title to valid filename slug."""
    # Remove invalid chars
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    # Replace whitespace with hyphens
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:100]  # Cap length


def extract_content(url):
    """
    Heuristic extraction of content from URL.
    Returns (title, text, domain).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Title
        title = "Unknown Title"
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
        else:
            t = soup.find("title")
            if t:
                title = t.get_text(strip=True)

        # Extract Content (Simple Heuristic: generic <article> or <main>)
        # This is a simplified version of slurp_url.py logic

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "aside", "iframe", "ads"]):
            tag.decompose()

        article = soup.find("article")
        if not article:
            article = soup.find("main")

        if article:
            text = article.get_text(separator="\n\n", strip=True)
        else:
            # Fallback: largest localized text block
            text = ""
            max_len = 0
            for div in soup.find_all("div"):
                # Quick heuristic: text length of direct text nodes
                local_text = div.get_text(separator=" ", strip=True)
                if len(local_text) > max_len:
                    max_len = len(local_text)
                    text = local_text

            if not text:
                text = soup.get_text(separator="\n\n", strip=True)

        # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        domain = urlparse(url).netloc.replace("www.", "")

        return title, text, domain

    except Exception as e:
        print(f"❌ Error fetching URL: {e}")
        sys.exit(1)


def enrich_metadata(text, url, original_title):
    """
    Uses Gemini to extract structured metadata.
    """
    client = get_client()

    prompt = f"""
    You are an expert Librarian AI. Analyze the following text extracted from a webpage.
    
    URL: {url}
    Original Title: {original_title}
    
    Text Content (truncated):
    {text[:10000]}
    
    Extract the following metadata in strict JSON format:
    {{
        "title": "Clean, descriptive title",
        "author": "Author name or Organization (if available, else 'Unknown')",
        "date": "Publication date (YYYY-MM-DD or 'Unknown')",
        "summary": "A concise 2-sentence summary of the content",
        "tags": ["tag1", "tag2", "tag3"] (max 5 relevant tags, lowercase),
        "category": "article" (fixed value)
    }}
    
    Return ONLY VALID JSON. Do not include markdown formatting like ```json.
    """

    try:
        print("🧠 Analyzing content with Gemini...")
        response = client.generate(prompt)
        # Clean response if it contains markdown code blocks
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        return data
    except Exception as e:
        print(f"⚠️ AI Analysis failed: {e}")
        # Fallback
        return {
            "title": original_title,
            "author": "Unknown",
            "date": datetime.date.today().isoformat(),
            "summary": "AI extraction failed.",
            "tags": ["untagged"],
            "category": "article",
        }


def save_article(url):
    print(f"📥 Archiving: {url}")

    # 1. Fetch
    raw_title, text, domain = extract_content(url)
    print(f"✅ Fetched: {raw_title}")

    # 2. Enrich
    meta = enrich_metadata(text, url, raw_title)

    # 3. Format Markdown
    today = datetime.date.today().isoformat()
    frontmatter = f"""---
title: "{meta["title"]}"
url: {url}
author: {meta["author"]}
date: {meta["date"]}
archived_at: {today}
tags: {json.dumps(meta["tags"])}
category: article
source_domain: {domain}
summary: "{meta["summary"]}"
---

# {meta["title"]}

> **Summary**: {meta["summary"]}

---

{text}
"""

    # 4. Save
    slug = clean_filename(meta["title"])
    filename = f"{today}-{slug}.md"

    # Ensure directory exists
    LIBRARY_PATH.mkdir(parents=True, exist_ok=True)

    file_path = LIBRARY_PATH / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"💾 Saved to: {file_path}")

    # 5. Append to TAG_INDEX (Simple append for now, full regen later)
    # We won't implement full index regen here to save time, assume standard periodic re-index.

    return file_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 archive_article.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    save_article(url)
