#!/usr/bin/env python3
"""
distill_sessions.py — Extract key insights from session logs for better semantic search.

Creates distilled insight files with 3-5 bullet summaries per session.
Reduces noise in vector search by embedding only high-signal content.

Usage:
    python3 distill_sessions.py           # Distill all sessions
    python3 distill_sessions.py --recent  # Only last 10 sessions
    python3 distill_sessions.py --dry-run # Preview without writing
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
SESSION_LOGS_DIR = WORKSPACE / ".context" / "memories" / "session_logs"
ARCHIVE_DIR = SESSION_LOGS_DIR / "archive"
OUTPUT_DIR = WORKSPACE / ".context" / "memories" / "session_insights"

def extract_existing_insights(content: str) -> list[str] | None:
    """Extract existing ### Key Insights or ### Learnings section."""
    patterns = [
        r"###\s*Key Insights?\s*\n((?:[-*]\s*.+\n?)+)",
        r"###\s*Learnings?\s*\n((?:[-*]\s*.+\n?)+)",
        r"###\s*Key Decisions?\s*\n((?:[-*]\s*.+\n?)+)",
        r"##\s*\d+\.\s*Key Insights?\s*\n((?:[-*]\s*.+\n?)+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            bullets = match.group(1)
            items = re.findall(r"[-*]\s*(.+)", bullets)
            if items:
                return items[:5]  # Max 5 insights
    return None

def extract_checkpoints(content: str) -> list[str]:
    """Extract checkpoint summaries as fallback insights."""
    checkpoints = re.findall(r"###\s*⚡\s*Checkpoint\s*\[.+\]\s*\n(.+)", content)
    return checkpoints[:5]

def generate_insights_via_gemini(content: str, session_name: str) -> list[str]:
    """Generate insights using Gemini."""
    try:
        sys.path.insert(0, str(WORKSPACE / ".agent" / "scripts"))
        from gemini_client import get_client
        
        prompt = f"""Extract 3-5 key insights from this session log.
Focus on: Learnings, decisions made, patterns detected, new frameworks applied.
Output as bullet points, each max 100 chars.

Session: {session_name}
Content (last 4000 chars):
{content[-4000:]}

Key Insights (3-5 bullets):"""
        
        client = get_client()
        response = client.generate(prompt).strip()
        
        # Parse bullets from response
        items = re.findall(r"[-*•]\s*(.+)", response)
        return items[:5] if items else ["Session processed."]
        
    except Exception as e:
        print(f"   ⚠️ Gemini failed: {e}")
        # Fallback to checkpoints
        return extract_checkpoints(content) or ["Session processed."]

def parse_session_filename(filename: str) -> tuple[str, int] | tuple[None, None]:
    """Parse session log filename."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md", filename)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def main():
    dry_run = "--dry-run" in sys.argv
    recent_only = "--recent" in sys.argv
    
    print("🔍 SESSION DISTILLATION")
    print("=" * 50)
    
    # Ensure output directory exists
    if not dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect session files
    session_files = list(SESSION_LOGS_DIR.glob("*-session-*.md"))
    if ARCHIVE_DIR.exists():
        session_files.extend(list(ARCHIVE_DIR.glob("*-session-*.md")))
    
    # Sort by date/session number
    session_files = sorted(session_files, 
        key=lambda f: (parse_session_filename(f.name) or ("", 0)),
        reverse=True)
    
    if recent_only:
        session_files = session_files[:10]
    
    print(f"   Found {len(session_files)} session files")
    
    distilled = 0
    skipped = 0
    extracted = 0
    generated = 0
    
    for file_path in session_files:
        date_str, session_num = parse_session_filename(file_path.name)
        if not date_str:
            skipped += 1
            continue
        
        output_name = f"{date_str}-session-{session_num:02d}-insights.md"
        output_path = OUTPUT_DIR / output_name
        
        # Skip if already distilled
        if output_path.exists():
            skipped += 1
            continue
        
        content = file_path.read_text(encoding="utf-8")
        
        # Try to extract existing insights first
        insights = extract_existing_insights(content)
        
        if insights:
            source = "extracted"
            extracted += 1
            print(f"   ✓ {file_path.name}: Extracted {len(insights)} insights")
        else:
            if dry_run:
                insights = ["[WOULD GENERATE]"]
                print(f"   ⏭️ {file_path.name}: Would generate")
            else:
                insights = generate_insights_via_gemini(content, file_path.name)
                source = "generated"
                generated += 1
                print(f"   🤖 {file_path.name}: Generated {len(insights)} insights")
        
        # Build distilled file
        distilled_content = f"""# Session Insights: {date_str} (Session {session_num})

> **Distilled**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Source**: {file_path.name}

## Key Insights

"""
        for insight in insights:
            distilled_content += f"- {insight}\n"
        
        distilled_content += f"""
---

#session-insights #distilled
"""
        
        if not dry_run:
            output_path.write_text(distilled_content, encoding="utf-8")
        
        distilled += 1
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"   Distilled: {distilled}")
    print(f"   Extracted: {extracted}")
    print(f"   Generated: {generated}")
    print(f"   Skipped: {skipped}")
    
    if not dry_run:
        print(f"\n✅ Insights saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
