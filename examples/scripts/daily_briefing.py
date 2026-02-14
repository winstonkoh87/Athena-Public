#!/usr/bin/env python3
"""
daily_briefing.py — Morning Brief Generator
=============================================

Fetches configurable RSS/URL sources, filters by interest keywords,
synthesizes via Gemini Flash, and outputs a structured daily briefing.

Usage:
    python3 daily_briefing.py                  # Full run → saves to .context/briefings/
    python3 daily_briefing.py --dry-run        # Fetch + display, no save
    python3 daily_briefing.py --sources-only   # List configured sources
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / ".agent" / "config" / "briefing_config.yaml"
BRIEFINGS_DIR = PROJECT_ROOT / ".context" / "briefings"

# Default config (used if no YAML config exists)
DEFAULT_CONFIG = {
    "schedule": "06:00",
    "timezone": "Asia/Singapore",
    "sources": [
        {
            "name": "Hacker News - Top",
            "type": "rss",
            "url": "https://hnrss.org/frontpage?count=10",
            "category": "tech",
        },
        {
            "name": "Reddit r/ChatGPT",
            "type": "rss",
            "url": "https://www.reddit.com/r/ChatGPT/top/.rss?t=day&limit=5",
            "category": "ai",
        },
        {
            "name": "Reddit r/LocalLLaMA",
            "type": "rss",
            "url": "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day&limit=5",
            "category": "ai",
        },
    ],
    "interest_keywords": [
        "AI",
        "LLM",
        "Claude",
        "Gemini",
        "GPT",
        "agent",
        "RAG",
        "trading",
        "EURUSD",
        "forex",
        "market",
        "Singapore",
        "startup",
        "SaaS",
        "psychology",
        "productivity",
    ],
    "gemini_model": "gemini-2.0-flash",
    "max_items_per_source": 10,
    "notify_telegram": False,
}


def load_config() -> dict:
    """Load config from YAML file, falling back to defaults."""
    if CONFIG_PATH.exists():
        try:
            # Simple YAML-like parser (avoids pyyaml dependency)
            import yaml

            with open(CONFIG_PATH) as f:
                return yaml.safe_load(f)
        except ImportError:
            pass
    return DEFAULT_CONFIG


# ── RSS Fetcher ───────────────────────────────────────────────────────────────


def fetch_rss(url: str, max_items: int = 10) -> list[dict]:
    """Fetch and parse an RSS feed. Returns list of {title, link, description}."""
    items = []
    try:
        headers = {"User-Agent": "Athena-Briefing/1.0 (Personal Knowledge Agent)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # Parse XML (handle both RSS and Atom)
        root = ET.fromstring(resp.text)

        # RSS 2.0
        for item in root.findall(".//item")[:max_items]:
            items.append(
                {
                    "title": (item.findtext("title") or "").strip(),
                    "link": (item.findtext("link") or "").strip(),
                    "description": _clean_html(item.findtext("description") or "")[:300],
                }
            )

        # Atom (Reddit uses this)
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//atom:entry", ns)[:max_items]:
                title = entry.findtext("atom:title", default="", namespaces=ns)
                link_elem = entry.find("atom:link[@rel='alternate']", ns)
                link = link_elem.get("href", "") if link_elem is not None else ""
                content = entry.findtext("atom:content", default="", namespaces=ns)
                items.append(
                    {
                        "title": title.strip(),
                        "link": link.strip(),
                        "description": _clean_html(content)[:300],
                    }
                )

    except Exception as e:
        print(f"   ⚠️ RSS fetch failed for {url}: {e}", file=sys.stderr)

    return items


def _clean_html(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


# ── Interest Filter ───────────────────────────────────────────────────────────


def filter_by_interest(items: list[dict], keywords: list[str]) -> list[dict]:
    """Score and filter items by keyword relevance."""
    scored = []
    keyword_patterns = [re.compile(re.escape(k), re.IGNORECASE) for k in keywords]

    for item in items:
        text = f"{item['title']} {item.get('description', '')}"
        score = sum(1 for p in keyword_patterns if p.search(text))
        if score > 0:
            item["relevance_score"] = score
            scored.append(item)

    # Sort by relevance (highest first)
    return sorted(scored, key=lambda x: x.get("relevance_score", 0), reverse=True)


# ── Gemini Synthesis ──────────────────────────────────────────────────────────


def synthesize_briefing(categorized_items: dict, model: str = "gemini-2.0-flash") -> str:
    """Use Gemini to synthesize a morning briefing from collected items."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return _manual_briefing(categorized_items)

    # Build prompt
    items_text = ""
    for category, items in categorized_items.items():
        items_text += f"\n## {category.upper()}\n"
        for item in items[:5]:
            items_text += f"- {item['title']}: {item.get('description', '')[:150]}\n"

    prompt = f"""You are a personal intelligence briefing agent. Synthesize these items into a concise morning brief.

Rules:
- Be concise (under 500 words total)
- Group by theme, not source
- Highlight items most relevant to: AI/LLM development, trading/markets, Singapore
- Add a "🎯 Action Items" section if any items suggest actions
- Add a "⚠️ Watchlist" section for items to monitor
- Use markdown formatting

Today's raw feed:
{items_text}
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1500,
            },
        }

        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print(f"   ⚠️ Gemini synthesis failed: {e}", file=sys.stderr)
        return _manual_briefing(categorized_items)


def _manual_briefing(categorized_items: dict) -> str:
    """Fallback: manual briefing without LLM."""
    lines = []
    for category, items in categorized_items.items():
        lines.append(f"\n## {category.upper()}")
        for item in items[:5]:
            lines.append(f"- **{item['title']}**")
            if item.get("link"):
                lines.append(f"  [{item['link']}]({item['link']})")
    return "\n".join(lines)


# ── Main Pipeline ─────────────────────────────────────────────────────────────


def generate_briefing(config: dict = None, dry_run: bool = False) -> str:
    """Full briefing pipeline: Fetch → Filter → Synthesize → Save."""
    config = config or load_config()
    today = datetime.now().strftime("%Y-%m-%d")
    day_name = datetime.now().strftime("%A")

    print(f"📰 Athena Morning Brief — {day_name}, {today}")
    print("=" * 50)

    # 1. Fetch from all sources
    categorized = {}
    all_items = []

    for source in config.get("sources", []):
        category = source.get("category", "general")
        print(f"   📡 Fetching: {source['name']}...")

        if source["type"] == "rss":
            items = fetch_rss(
                source["url"],
                max_items=config.get("max_items_per_source", 10),
            )
            for item in items:
                item["source"] = source["name"]
                item["category"] = category
            all_items.extend(items)

    print(f"   📊 Fetched {len(all_items)} items total")

    # 2. Filter by interest
    keywords = config.get("interest_keywords", [])
    if keywords:
        relevant = filter_by_interest(all_items, keywords)
        print(f"   🎯 {len(relevant)} items match your interests")
    else:
        relevant = all_items

    # 3. Categorize
    for item in relevant:
        cat = item.get("category", "general")
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(item)

    # 4. Synthesize
    if relevant:
        print("   🧠 Synthesizing briefing...")
        briefing_content = synthesize_briefing(
            categorized,
            model=config.get("gemini_model", "gemini-2.0-flash"),
        )
    else:
        briefing_content = "*No items matched your interests today.*"

    # 5. Assemble full document
    header = f"""---
date: {today}
type: daily_briefing
sources: {len(config.get("sources", []))}
items_fetched: {len(all_items)}
items_relevant: {len(relevant)}
---

# 📰 Morning Brief — {day_name}, {today}

"""
    full_doc = header + briefing_content

    # 6. Save
    if not dry_run:
        BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = BRIEFINGS_DIR / f"{today}.md"
        output_path.write_text(full_doc, encoding="utf-8")
        print(f"\n   ✅ Saved: {output_path}")
    else:
        print(f"\n   🔍 [DRY RUN] Would save to: {BRIEFINGS_DIR / f'{today}.md'}")
        # Print only the summary header, not the full document content
        preview_lines = full_doc.split("\n")[:15]
        print("\n" + "\n".join(preview_lines))
        print(f"\n   ... ({len(full_doc)} chars total, use --save to persist)")

    return full_doc


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Athena Daily Briefing Agent")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and display only")
    parser.add_argument("--sources-only", action="store_true", help="List configured sources")
    args = parser.parse_args()

    config = load_config()

    if args.sources_only:
        print("📡 Configured Sources:")
        for s in config.get("sources", []):
            print(f"   • [{s['category']}] {s['name']}: {s['url']}")
        return

    generate_briefing(config=config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
