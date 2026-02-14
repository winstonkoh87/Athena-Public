#!/usr/bin/env python3
"""
compress_protocols.py — Generate compressed protocol summaries for efficient loading.

Creates PROTOCOL_SUMMARIES.md with 2-line summaries for each protocol.
Uses existing @compressed: blocks if present, or generates via LLM.

Usage:
    python3 compress_protocols.py              # Generate with Ollama (default)
    python3 compress_protocols.py --gemini     # Use Gemini API instead
    python3 compress_protocols.py --dry-run    # Preview without writing
"""

import asyncio
import os
import re
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
PROTOCOLS_DIR = WORKSPACE / ".agent" / "skills" / "protocols"
PUBLIC_PROTOCOLS_DIR = WORKSPACE / "Athena-Public" / "examples" / "protocols"
OUTPUT_PATH = WORKSPACE / ".context" / "PROTOCOL_SUMMARIES.md"

# CONCURRENCY LIMIT
MAX_CONCURRENT_REQUESTS = 5  # Higher for Ollama (local)
OLLAMA_MODEL = "llama3.1:8b"  # Fast local model (qwen3 has slow thinking mode)


def extract_existing_compressed(content: str) -> str | None:
    """Extract @compressed: block if exists."""
    match = re.search(r"@compressed:\s*(.+?)(?:\n\n|\n@|\Z)", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_trigger(content: str) -> str:
    """Extract trigger/when-to-use from protocol."""
    patterns = [
        r"\*\*Trigger\*\*:?\s*(.+)",
        r"\*\*When to Use\*\*:?\s*(.+)",
        r"\*\*Use When\*\*:?\s*(.+)",
        r"Trigger:?\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:100]
    return "—"


def generate_summary_ollama(content: str, title: str, code: str) -> str:
    """Generate 2-line summary using local Ollama model."""
    prompt = f"""Summarize this protocol in exactly 2 lines (max 150 chars total).
Focus on: What it detects/solves, and the key mechanism.

Protocol: {title}
Content (first 2000 chars):
{content[:2000]}

2-line summary:"""

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, "--nowordwrap"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # Clean any thinking tags from qwen3
            output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
            print(f"   🦙 Protocol {code}: Generated via Ollama")
            return output[:200]
        else:
            raise Exception(result.stderr)
    except Exception as e:
        print(f"   ⚠️ Protocol {code}: Ollama failed: {e}")
        # Fallback to first paragraph
        paragraphs = content.split("\n\n")
        for p in paragraphs:
            if len(p) > 50 and not p.startswith("#"):
                return p[:150].replace("\n", " ").strip() + "..."
        return "Protocol summary pending."


def extract_title(content: str) -> str:
    """Extract title from markdown."""
    match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


async def generate_summary_async(
    semaphore, client, content: str, title: str, code: str
) -> str:
    """Generate 2-line summary using Gemini with concurrency limit."""
    async with semaphore:
        try:
            prompt = f"""Summarize this protocol in exactly 2 lines (max 150 chars total).
Focus on: What it detects/solves, and the key mechanism.

Protocol: {title}
Content (first 2000 chars):
{content[:2000]}

2-line summary:"""

            # Since gemini_client is synchronous, we use asyncio.to_thread
            result = await asyncio.to_thread(client.generate, prompt)
            print(f"   🤖 Protocol {code}: Generated via Gemini")
            return result.strip()[:200]
        except Exception as e:
            print(f"   ⚠️ Protocol {code}: Generation failed: {e}")
            # Fallback logic
            paragraphs = content.split("\n\n")
            for p in paragraphs:
                if len(p) > 50 and not p.startswith("#"):
                    return p[:150].replace("\n", " ").strip() + "..."
            return "Protocol summary pending."


def parse_protocol_code(filename: str) -> str | None:
    """Extract protocol code from filename."""
    match = re.match(r"(\d+)-", filename)
    return match.group(1) if match else None


async def main():
    dry_run = "--dry-run" in sys.argv
    use_gemini = True  # Default to Gemini (User Decree 2026-02-01)
    if "--ollama" in sys.argv:
        use_gemini = False

    mode = "Gemini API (V3 Flash)" if use_gemini else f"Ollama ({OLLAMA_MODEL})"
    print(f"📋 PROTOCOL COMPRESSION ({mode})")
    print("=" * 50)

    # Collect protocol files
    protocol_files = []
    for dir_path in [PROTOCOLS_DIR, PUBLIC_PROTOCOLS_DIR]:
        if dir_path.exists():
            protocol_files.extend(list(dir_path.rglob("*.md")))

    # Deduplicate by protocol code, prioritizing private over public
    id_to_file = {}
    for f in protocol_files:
        code = parse_protocol_code(f.name)
        if not code:
            continue

        # If ID already exists, only replace if current file is in the private directory
        if code not in id_to_file:
            id_to_file[code] = f
        else:
            # Check if current file is private (lives in .agent/)
            if ".agent" in str(f):
                id_to_file[code] = f

    # Convert back to list and sort
    protocol_files = sorted(
        id_to_file.values(), key=lambda f: int(parse_protocol_code(f.name) or 0)
    )

    print(f"   Found {len(protocol_files)} numbered protocols")

    # === SAFETY INTERLOCK & COST ESTIMATOR ===
    if not dry_run and ("--yes" not in sys.argv and "-y" not in sys.argv):
        count = len(protocol_files)
        # Estimate: 2000 chars per file input, 200 chars output
        est_input_tokens = (count * 2000) / 4
        est_output_tokens = (count * 200) / 4

        cost_input = (est_input_tokens / 1_000_000) * 0.50
        cost_output = (est_output_tokens / 1_000_000) * 3.00
        total_cost = cost_input + cost_output

        # Estimate time: 5 concurrent, 1s latency
        est_mins = round(((count / 5) * 1.5) / 60, 2)

        print("\n" + "=" * 50)
        print("💰 PRE-FLIGHT COST & TIME ESTIMATE (Gemini 3 Flash)")
        print("=" * 50)
        print(f"   📂 Protocols:  {count}")
        print(f"   ⏱️  Estimated Time: ~{est_mins} Minutes")
        print(f"   💸 Estimated Cost: ${total_cost:.4f} USD")
        print("-" * 50)

        user_input = input("   Shall we proceed? (y/N): ").strip().lower()
        if user_input != "y":
            print("❌ Aborted by user.")
            sys.exit(0)
        print("✅ Proceeding...\n")
    # ========================

    # Initialize Gemini client if needed
    client = None
    semaphore = None
    if use_gemini and not dry_run:
        sys.path.insert(0, str(WORKSPACE / ".agent" / "scripts"))
        from gemini_client import get_client

        client = get_client()
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    summaries = []
    tasks = []

    for file_path in protocol_files:
        code = parse_protocol_code(file_path.name)
        content = file_path.read_text(encoding="utf-8")
        title = extract_title(content)
        trigger = extract_trigger(content)

        # Check for existing @compressed block
        existing = extract_existing_compressed(content)

        if existing:
            print(f"   ✓ Protocol {code}: Extracted existing")
            summaries.append(
                {"code": code, "title": title, "trigger": trigger, "summary": existing}
            )
        elif dry_run:
            print(f"   ⏭️ Protocol {code}: Would generate")
            summaries.append(
                {
                    "code": code,
                    "title": title,
                    "trigger": trigger,
                    "summary": "[WOULD GENERATE]",
                }
            )
        elif use_gemini:
            # Async Gemini path
            async def get_existing(val):
                return val

            tasks.append(
                {
                    "code": code,
                    "title": title,
                    "trigger": trigger,
                    "coro": generate_summary_async(
                        semaphore, client, content, title, code
                    ),
                }
            )
        else:
            # Synchronous Ollama path (default)
            summary = generate_summary_ollama(content, title, code)
            summaries.append(
                {"code": code, "title": title, "trigger": trigger, "summary": summary}
            )

    # If using Gemini async, gather results
    if tasks:
        print(f"\n🚀 Processing {len(tasks)} protocols async...")
        results = await asyncio.gather(*(t["coro"] for t in tasks))
        for t, summary in zip(tasks, results):
            summaries.append(
                {
                    "code": t["code"],
                    "title": t["title"],
                    "trigger": t["trigger"],
                    "summary": summary,
                }
            )

    # Sort summaries by code
    summaries.sort(key=lambda s: int(s["code"]))

    print(f"\n🚀 Processed {len(summaries)} protocols...")

    # Clean summaries for markdown table
    for s in summaries:
        s["title"] = s["title"].replace("|", "—")
        s["trigger"] = s["trigger"].replace("|", "—")
        s["summary"] = s["summary"].replace("|", "—").replace("\n", " ")

    # Build output
    output = f"""# Protocol Summaries (Compressed)

> **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Total**: {len(summaries)} protocols
> **Purpose**: Quick-load context for protocol lookup. Full protocols loaded on-demand.

---

| Code | Title | Trigger | Summary |
|------|-------|---------|---------|
"""

    for s in summaries:
        output += f"| {s['code']} | {s['title'][:40]} | {s['trigger'][:50]} | {s['summary'][:100]} |\n"

    output += """
---

#index #protocols #compression
"""

    if dry_run:
        print(f"\n[DRY RUN] Would write {len(summaries)} entries to {OUTPUT_PATH}")
    else:
        OUTPUT_PATH.write_text(output, encoding="utf-8")
        print(f"\n✅ Wrote {len(summaries)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
