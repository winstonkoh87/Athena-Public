#!/usr/bin/env python3
"""
self_optimize.py — Recursive Self-Optimization Engine
======================================================

Weekly meta-analysis of session logs to detect patterns and propose
new protocols, automations, or workflow improvements.

SAFETY: This script ONLY proposes changes. It NEVER auto-executes them.
All proposals are written to .context/self_optimization/ for human review.

Usage:
    python3 self_optimize.py                    # Full weekly analysis
    python3 self_optimize.py --dry-run          # Analysis without saving
    python3 self_optimize.py --days 3           # Analyze last 3 days
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
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
SESSIONS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
OPTIMIZATION_DIR = PROJECT_ROOT / ".context" / "self_optimization"
SKILL_INDEX = PROJECT_ROOT / ".context" / "SKILL_INDEX.md"

# Analysis parameters
DEFAULT_DAYS = 7
MIN_PATTERN_FREQUENCY = 2  # Minimum occurrences before something becomes a "pattern"


# ── Session Collector ─────────────────────────────────────────────────────────


def collect_recent_sessions(days: int = DEFAULT_DAYS) -> list[dict]:
    """Collect session logs from the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    sessions = []

    if not SESSIONS_DIR.exists():
        print("⚠️ Session logs directory not found", file=sys.stderr)
        return []

    # Scan current directory and archive
    scan_dirs = [SESSIONS_DIR]
    archive_dir = SESSIONS_DIR / "archive"
    if archive_dir.exists():
        scan_dirs.append(archive_dir)

    for scan_dir in scan_dirs:
        for md_file in scan_dir.rglob("*.md"):
            # Extract date from filename (YYYY-MM-DD-session-XX.md)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            if not date_match:
                continue

            file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            if file_date < cutoff:
                continue

            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                sessions.append(
                    {
                        "filename": md_file.name,
                        "date": date_match.group(1),
                        "content": content,
                        "path": str(md_file),
                        "size": len(content),
                    }
                )
            except Exception as e:
                print(f"⚠️ Failed to read {md_file.name}: {e}", file=sys.stderr)

    return sorted(sessions, key=lambda x: x["date"], reverse=True)


# ── Pattern Detection ─────────────────────────────────────────────────────────


def detect_recurring_queries(sessions: list[dict]) -> list[dict]:
    """Find topics/queries that appear across multiple sessions."""
    # Extract semantic search queries from quicksave markers
    query_pattern = re.compile(
        r'(?:searched|search|query|looking for|searched for)[:\s]+["\']?(.+?)["\']?(?:\n|$)',
        re.IGNORECASE,
    )
    topic_counter = Counter()

    for session in sessions:
        matches = query_pattern.findall(session["content"])
        for match in matches:
            # Normalize
            normalized = match.strip().lower()[:80]
            if len(normalized) > 3:
                topic_counter[normalized] += 1

    recurring = [
        {"query": q, "count": c}
        for q, c in topic_counter.most_common(20)
        if c >= MIN_PATTERN_FREQUENCY
    ]
    return recurring


def detect_recurring_friction(sessions: list[dict]) -> list[dict]:
    """Find errors, workarounds, or friction points that recur."""
    friction_patterns = [
        (
            re.compile(
                r"(?:error|failed|bug|issue|broke|broken)[:\s]+(.+)", re.IGNORECASE
            ),
            "error",
        ),
        (
            re.compile(
                r"(?:workaround|hack|hotfix|temp fix|manual)[:\s]+(.+)", re.IGNORECASE
            ),
            "workaround",
        ),
        (re.compile(r"(?:TODO|FIXME|HACK)[:\s]+(.+)", re.IGNORECASE), "todo"),
        (
            re.compile(
                r"(?:friction|annoying|tedious|repetitive)[:\s]+(.+)", re.IGNORECASE
            ),
            "friction",
        ),
    ]

    friction_counter = defaultdict(list)

    for session in sessions:
        for pattern, ftype in friction_patterns:
            matches = pattern.findall(session["content"])
            for match in matches:
                normalized = match.strip()[:100]
                friction_counter[f"{ftype}: {normalized}"].append(session["date"])

    recurring = [
        {"friction": k, "occurrences": len(v), "dates": v}
        for k, v in friction_counter.items()
        if len(v) >= MIN_PATTERN_FREQUENCY
    ]
    return sorted(recurring, key=lambda x: x["occurrences"], reverse=True)


def detect_topic_clusters(sessions: list[dict]) -> dict:
    """Identify dominant topic clusters across sessions."""
    # Simple keyword frequency analysis
    domain_keywords = {
        "trading": ["trade", "eurusd", "forex", "risk", "position", "pip", "chart"],
        "coding": ["script", "function", "bug", "deploy", "git", "code", "api"],
        "psychology": ["pattern", "schema", "attachment", "limerence", "boundary"],
        "strategy": ["protocol", "framework", "architecture", "roadmap", "plan"],
        "content": ["reddit", "post", "viral", "seo", "marketing", "audience"],
    }

    domain_scores = Counter()
    for session in sessions:
        content_lower = session["content"].lower()
        for domain, keywords in domain_keywords.items():
            score = sum(content_lower.count(k) for k in keywords)
            if score > 0:
                domain_scores[domain] += score

    return dict(domain_scores.most_common())


def detect_underutilized_tools(sessions: list[dict]) -> list[str]:
    """Find tools/scripts that exist but were never invoked."""
    scripts_dir = PROJECT_ROOT / ".agent" / "scripts"
    if not scripts_dir.exists():
        return []

    all_scripts = {f.stem for f in scripts_dir.glob("*.py")}

    # Check which scripts were referenced in sessions
    referenced = set()
    for session in sessions:
        for script in all_scripts:
            if script in session["content"]:
                referenced.add(script)

    unused = all_scripts - referenced
    # Filter out known utility scripts
    utility_scripts = {"__init__", "setup", "test", "lib", "__pycache__"}
    return sorted([s for s in unused if s not in utility_scripts])[:15]


# ── Gemini Synthesis ──────────────────────────────────────────────────────────


def generate_proposals(analysis: dict) -> str:
    """Use Gemini to synthesize actionable proposals from analysis data."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return _manual_proposals(analysis)

    prompt = f"""You are a meta-analysis engine for a personal AI system called Athena.
Analyze these patterns from the last {analysis["days"]} days of session logs and propose improvements.

DATA:
- Sessions analyzed: {analysis["session_count"]}
- Dominant topics: {json.dumps(analysis["topic_clusters"])}
- Recurring queries (searched 2+ times): {json.dumps(analysis["recurring_queries"][:10])}
- Recurring friction: {json.dumps(analysis["recurring_friction"][:10])}
- Underutilized tools: {json.dumps(analysis["underutilized"][:10])}

OUTPUT FORMAT (must be markdown):

## 🔄 Recurring Patterns
- List patterns that suggest a new protocol or automation

## 🛠️ Proposed Automations
- Specific scripts or workflow changes to reduce friction

## 📋 Protocol Candidates
- Topics searched 3+ times that should become a formal protocol

## 🧹 Cleanup Suggestions
- Underutilized tools to prune or promote

## 📊 Health Assessment
- Overall system health score (1-10) with reasoning

RULES:
- Be specific and actionable
- Reference actual file names when suggesting changes
- Under 400 words total
- Do NOT auto-execute anything — proposals only
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1200},
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print(f"   ⚠️ Gemini synthesis failed: {e}", file=sys.stderr)
        return _manual_proposals(analysis)


def _manual_proposals(analysis: dict) -> str:
    """Fallback proposals without LLM."""
    lines = ["## Analysis Results (Manual — No LLM)\n"]

    if analysis["recurring_queries"]:
        lines.append("### Recurring Queries (Protocol Candidates)")
        for q in analysis["recurring_queries"][:5]:
            lines.append(f"- **{q['query']}** — searched {q['count']} times")

    if analysis["recurring_friction"]:
        lines.append("\n### Recurring Friction (Automation Candidates)")
        for f in analysis["recurring_friction"][:5]:
            lines.append(f"- **{f['friction']}** — {f['occurrences']} occurrences")

    if analysis["underutilized"]:
        lines.append("\n### Underutilized Tools")
        for t in analysis["underutilized"][:10]:
            lines.append(f"- `{t}.py`")

    return "\n".join(lines)


# ── Main Pipeline ─────────────────────────────────────────────────────────────


def run_optimization(days: int = DEFAULT_DAYS, dry_run: bool = False) -> str:
    """Full self-optimization pipeline."""
    today = datetime.now().strftime("%Y-%m-%d")
    week_num = datetime.now().isocalendar()[1]

    print(f"🧬 Athena Self-Optimization — Week {week_num}, {today}")
    print(f"   📊 Analyzing last {days} days of sessions...")
    print("=" * 50)

    # 1. Collect
    sessions = collect_recent_sessions(days)
    print(f"   📂 Found {len(sessions)} sessions")

    if not sessions:
        print("   ⚠️ No sessions found. Nothing to analyze.")
        return ""

    # 2. Detect patterns
    print("   🔍 Detecting patterns...")
    recurring_queries = detect_recurring_queries(sessions)
    recurring_friction = detect_recurring_friction(sessions)
    topic_clusters = detect_topic_clusters(sessions)
    underutilized = detect_underutilized_tools(sessions)

    print(f"      • {len(recurring_queries)} recurring queries")
    print(f"      • {len(recurring_friction)} recurring friction points")
    print(f"      • {len(topic_clusters)} topic clusters")
    print(f"      • {len(underutilized)} underutilized tools")

    analysis = {
        "days": days,
        "session_count": len(sessions),
        "recurring_queries": recurring_queries,
        "recurring_friction": recurring_friction,
        "topic_clusters": topic_clusters,
        "underutilized": underutilized,
    }

    # 3. Generate proposals
    print("   🧠 Generating proposals...")
    proposals = generate_proposals(analysis)

    # 4. Assemble report
    header = f"""---
date: {today}
week: {week_num}
type: self_optimization
sessions_analyzed: {len(sessions)}
days_covered: {days}
---

# 🧬 Self-Optimization Report — Week {week_num}

> **Disclaimer**: These are proposals only. Nothing has been auto-executed.
> Review and approve before implementing any changes.

## 📊 Analysis Summary

| Metric | Value |
|--------|-------|
| Sessions Analyzed | {len(sessions)} |
| Days Covered | {days} |
| Recurring Queries | {len(recurring_queries)} |
| Friction Points | {len(recurring_friction)} |
| Topic Clusters | {len(topic_clusters)} |
| Underutilized Tools | {len(underutilized)} |

"""
    full_report = header + proposals

    # 5. Save
    if not dry_run:
        OPTIMIZATION_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OPTIMIZATION_DIR / f"{today}-W{week_num:02d}.md"
        output_path.write_text(full_report, encoding="utf-8")
        print(f"\n   ✅ Report saved: {output_path}")
    else:
        output_path = OPTIMIZATION_DIR / f"{today}-W{week_num:02d}.md"
        print(f"\n   🔍 [DRY RUN] Would save to: {output_path.name}")
        print(f"   📏 Report size: {len(full_report)} chars")
        print("   ℹ️  Run without --dry-run to save the full report.")

    return full_report


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Athena Self-Optimization Engine")
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS, help="Days to analyze"
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyze without saving")
    args = parser.parse_args()

    run_optimization(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
