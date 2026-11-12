#!/usr/bin/env python3
"""
Compound Asset Generator
Uses Gemini 3 Flash Preview to generate durable value assets.
Budget: 19 API calls total.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

# Configure Gemini
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

WORKSPACE = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = WORKSPACE / ".context" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

call_count = 0


def log_call(task: str):
    global call_count
    call_count += 1
    print(f"🔥 API Call #{call_count}/19: {task}")


def save_asset(name: str, content: str, subdir: str = ""):
    """Save generated asset to cache."""
    target_dir = CACHE_DIR / subdir if subdir else CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    filepath = target_dir / f"{name}.md"
    filepath.write_text(content)
    print(f"   ✅ Saved: {filepath.relative_to(WORKSPACE)}")
    return filepath


# ============================================================
# TASK 1: Protocol Summaries (5 calls)
# ============================================================
def generate_protocol_summaries():
    """Generate condensed summaries of hot protocols."""
    print("\n" + "=" * 60)
    print("📜 TASK 1: Protocol Summaries (5 calls)")
    print("=" * 60)

    hot_protocols = [
        WORKSPACE / ".agent/skills/protocols/meta/MTA-000-ultimate-auditor.md",
        WORKSPACE
        / ".agent/skills/protocols/decision/DEC-75-synthetic-parallel-reasoning.md",
        WORKSPACE / ".agent/skills/protocols/safety/SAF-001-law-of-ruin.md",
        WORKSPACE / ".agent/skills/protocols/decision/DEC-124-sdr-calculator.md",
        WORKSPACE
        / ".agent/skills/protocols/architecture/ARC-133-query-archetype-routing.md",
    ]

    for proto_path in hot_protocols:
        if not proto_path.exists():
            print(f"   ⚠️ Not found: {proto_path.name}")
            continue

        content = proto_path.read_text()[:8000]  # Limit input
        log_call(f"Summarizing {proto_path.name}")

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"""
Summarize this protocol in exactly 150 words. Focus on:
1. Core purpose (1 sentence)
2. When to invoke (triggers)
3. Key steps (bullet points)
4. Output format

Protocol:
{content}
""",
            )
            summary = response.text.strip()
            save_asset(f"summary_{proto_path.stem}", summary, "protocol_summaries")
        except Exception as e:
            print(f"   ❌ Error: {e}")


# ============================================================
# TASK 2: Session TL;DRs (5 calls)
# ============================================================
def generate_session_tldrs():
    """Generate TL;DRs for recent sessions."""
    print("\n" + "=" * 60)
    print("📋 TASK 2: Session TL;DRs (5 calls)")
    print("=" * 60)

    sessions = sorted(
        (WORKSPACE / ".context/memories/session_logs").glob("2026-01-*.md"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )[:5]

    for session_path in sessions:
        content = session_path.read_text()[:6000]
        log_call(f"TL;DR for {session_path.name}")

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"""
Create a TL;DR for this session in exactly 100 words:
1. Main topic/goal
2. Key decisions made
3. Deferred items
4. Notable insights

Session:
{content}
""",
            )
            tldr = response.text.strip()
            save_asset(f"tldr_{session_path.stem}", tldr, "session_tldrs")
        except Exception as e:
            print(f"   ❌ Error: {e}")


# ============================================================
# TASK 3: Entity Extraction (5 calls)
# ============================================================
def refresh_entity_extraction():
    """Extract entities from key documents."""
    print("\n" + "=" * 60)
    print("🧠 TASK 3: Entity Extraction (5 calls)")
    print("=" * 60)

    key_docs = [
        WORKSPACE / ".framework/v7.0/modules/Core_Identity.md",
        WORKSPACE / ".framework/v7.0/modules/System_Principles.md",
        WORKSPACE
        / ".context/memories/case_studies/CS-346-GEO-Pivot-Content-Agencies.md",
        WORKSPACE
        / ".context/memories/case_studies/CS-347-Digital-Marketing-Principles.md",
        WORKSPACE / "Winston/profile/User_Profile.md",
    ]

    all_entities = []

    for doc_path in key_docs:
        if not doc_path.exists():
            print(f"   ⚠️ Not found: {doc_path.name}")
            continue

        content = doc_path.read_text()[:8000]
        log_call(f"Extracting entities from {doc_path.name}")

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"""
Extract key entities from this document. Return JSON array with:
{{"name": "entity name", "type": "person|concept|protocol|framework|metric", "description": "one-line description"}}

Document:
{content}

Return ONLY valid JSON array, no markdown.
""",
            )
            # Try to parse JSON
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]

            entities = json.loads(text)
            all_entities.extend(entities)
            print(f"   📊 Extracted {len(entities)} entities")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Save consolidated entities
    save_asset("extracted_entities", json.dumps(all_entities, indent=2), "entities")


# ============================================================
# TASK 4: Stealable Prompts (4 calls)
# ============================================================
def generate_stealable_prompts():
    """Generate reusable meta-prompts for top workflows."""
    print("\n" + "=" * 60)
    print("🎯 TASK 4: Stealable Prompts (4 calls)")
    print("=" * 60)

    top_workflows = [
        WORKSPACE / ".agent/workflows/start.md",
        WORKSPACE / ".agent/workflows/ultrathink.md",
        WORKSPACE / ".agent/workflows/brief.md",
        WORKSPACE / ".agent/workflows/end.md",
    ]

    for wf_path in top_workflows:
        if not wf_path.exists():
            print(f"   ⚠️ Not found: {wf_path.name}")
            continue

        content = wf_path.read_text()[:6000]
        log_call(f"Generating stealable prompt for {wf_path.name}")

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"""
Convert this workflow into a "stealable prompt" — a standalone system instruction that could be copy-pasted into any AI to replicate this behavior.

Requirements:
1. Self-contained (no external file references)
2. Clear trigger conditions
3. Step-by-step execution logic
4. Output format specification
5. Under 500 words

Workflow:
{content}
""",
            )
            prompt = response.text.strip()
            save_asset(f"stealable_{wf_path.stem}", prompt, "stealable_prompts")
        except Exception as e:
            print(f"   ❌ Error: {e}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("⚡ COMPOUND ASSET GENERATOR")
    print("   Model: gemini-3-flash-preview")
    print("   Budget: 19 API calls")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    generate_protocol_summaries()  # 5 calls
    generate_session_tldrs()  # 5 calls
    refresh_entity_extraction()  # 5 calls
    generate_stealable_prompts()  # 4 calls

    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: {call_count} API calls used")
    print(f"   Assets saved to: {CACHE_DIR.relative_to(WORKSPACE)}")
    print("=" * 60)
