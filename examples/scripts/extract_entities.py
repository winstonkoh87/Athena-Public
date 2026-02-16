#!/usr/bin/env python3
"""
extract_entities.py — High-Performance Async Entity Extraction (v3.0)

Scans all .md files and uses Gemini 3 Flash (Async) to extract entities/relationships.
Uses asyncio + semaphores to maximize throughput (Corporate-Grade Parallellism).

Features:
- AsyncIO / Await pattern for non-blocking API calls.
- Semaphore Concurrency Control (Default: 15 concurrent requests).
- Live Progress Reporting.
- Strict Gemini 3 Flash Enforcement.
"""

import os
import sys
import json
import re
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try to import google.generativeai
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# === Configuration ===
# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent
GRAPHRAG_DIR = ROOT_DIR / ".agent" / "graphrag"
OUTPUT_FILE = GRAPHRAG_DIR / "entities.json"
OUTPUT_JSONL = GRAPHRAG_DIR / "entities.jsonl"

# Directories to scan
SCAN_DIRS = [
    ROOT_DIR / ".context",
    ROOT_DIR / ".agent" / "skills",
    ROOT_DIR / ".framework",
]

# Chunking Config
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200
CONCURRENCY_LIMIT = 20

# Entity extraction prompt
EXTRACTION_PROMPT = """You are an expert knowledge graph engineer. Analyze the following document chunk and extract key entities and relationships.

Target:
1. **Entities**: Important concepts, protocols, people, systems, tags (hashtags), or unique terms.
2. **Relationships**: How these entities connect (e.g., "implements", "relates_to", "author_of", "part_of").

Strictly return a JSON object with this structure:
{
    "entities": [
        {"name": "Entity Name", "type": "concept|person|protocol|resource|tag", "description": "Concise definition"}
    ],
    "relationships": [
        {"source": "Entity A", "target": "Entity B", "type": "relationship_type"}
    ]
}

Rules:
- Filter out trivial words; focus on the Core Domain of this workspace.
- Normalize entity names (e.g., "GraphRAG System" -> "GraphRAG").
- If a chunk ends in the middle of a sentence, ignore the incomplete thought.
- Return ONLY valid JSON.

Document Chunk:
---
{content}
---

JSON Output:"""


def get_all_md_files(directories: list[Path]) -> list[Path]:
    """Recursively find all .md files in the given directories."""
    files = []
    for directory in directories:
        if directory.exists():
            for f in directory.rglob("*.md"):
                if not f.name.endswith("_INDEX.md") and f.name != "TAG_INDEX.md":
                    files.append(f)
    return files


class TextSplitter:
    """Simple recursive character text splitter."""

    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        final_chunks = []
        if len(text) <= self.chunk_size:
            return [text]

        separator = ""
        for sep in self.separators:
            if sep == "":
                break
            if sep in text:
                separator = sep
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        current_chunk = []
        current_length = 0

        for split in splits:
            split_len = len(split) + len(separator)
            if current_length + split_len > self.chunk_size:
                if current_chunk:
                    doc = separator.join(current_chunk)
                    final_chunks.append(doc)
                    overlap_len = 0
                    overlap_chunk = []
                    for s in reversed(current_chunk):
                        s_len = len(s) + len(separator)
                        if overlap_len + s_len > self.chunk_overlap:
                            break
                        overlap_chunk.insert(0, s)
                        overlap_len += s_len
                    current_chunk = overlap_chunk
                    current_length = overlap_len
            current_chunk.append(split)
            current_length += split_len

        if current_chunk:
            final_chunks.append(separator.join(current_chunk))
        return final_chunks


def clean_json_response(text: str) -> str:
    """Extract and clean JSON from LLM response."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1)

    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start : end + 1]
    return text


# STRICT GEMINI 3 FLASH ONLY
MODEL_ROSTER = [
    "gemini-3-flash-preview",
]


def get_model_name(index: int) -> str:
    return MODEL_ROSTER[index % len(MODEL_ROSTER)]


async def extract_chunk_async(chunk: str) -> Dict[str, Any]:
    """Async calling of Gemini API."""
    model_name = MODEL_ROSTER[0]  # Single model policy

    try:
        model = genai.GenerativeModel(model_name)
        prompt = EXTRACTION_PROMPT.replace("{content}", chunk)

        # ASYNC CALL
        response = await model.generate_content_async(prompt)

        cleaned_json = clean_json_response(response.text)
        if not cleaned_json:
            return {"entities": [], "relationships": []}

        data = json.loads(cleaned_json)

        if isinstance(data, list):
            return {"entities": data, "relationships": []}
        if isinstance(data, dict):
            entities_key = "Entities" if "Entities" in data else "entities"
            rels_key = "Relationships" if "Relationships" in data else "relationships"
            return {
                "entities": data.get(entities_key, []),
                "relationships": data.get(rels_key, []),
            }

    except Exception as e:
        return {"entities": [], "relationships": []}

    return {"entities": [], "relationships": []}


def is_already_extracted(content: str) -> bool:
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        if "graphrag_extracted: true" in match.group(1):
            return True
    return False


def mark_as_extracted(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        if is_already_extracted(content):
            return

        if content.startswith("---"):
            end_idx = content.find("\n---", 3)
            if end_idx != -1:
                frontmatter = content[3:end_idx]
                if "graphrag_extracted:" not in frontmatter:
                    new_frontmatter = (
                        frontmatter.rstrip() + "\ngraphrag_extracted: true"
                    )
                    new_content = "---\n" + new_frontmatter + content[end_idx:]
                    file_path.write_text(new_content, encoding="utf-8")
                    return

        new_content = "---\ngraphrag_extracted: true\n---\n\n" + content
        file_path.write_text(new_content, encoding="utf-8")
    except:
        pass


async def write_to_jsonl(data: dict):
    """Append a single result to the JSONL file."""
    async with asyncio.Lock():
        line = json.dumps(data)
        with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
            f.write(line + "\n")


async def process_file(
    file_path: Path, semaphore: asyncio.Semaphore
) -> tuple[List, List]:
    """Process a single file with semaphore lock."""
    async with semaphore:
        try:
            if not file_path.exists():
                return [], []

            content = file_path.read_text(encoding="utf-8")

            # Check skip logic
            force_mode = "--force" in sys.argv
            if not force_mode and is_already_extracted(content):
                # print(f"⏩ {file_path.name}")
                return [], []

            splitter = TextSplitter(CHUNK_SIZE, CHUNK_OVERLAP)
            chunks = splitter.split_text(content)

            relative_path = file_path.name
            file_entities = []
            file_rels = []

            for chunk in chunks:
                if len(chunk) < 100:
                    continue
                result = await extract_chunk_async(chunk)

                for e in result.get("entities", []):
                    e["source_file"] = relative_path
                    file_entities.append(e)
                for r in result.get("relationships", []):
                    r["source_file"] = relative_path
                    file_rels.append(r)

            # Save to JSONL immediately (Checkpoint)
            if file_entities or file_rels:
                await write_to_jsonl(
                    {
                        "file": relative_path,
                        "entities": file_entities,
                        "relationships": file_rels,
                    }
                )

            # Mark file
            # If force mode, we might be re-marking, which is fine
            mark_as_extracted(file_path)
            print(f"✅ {file_path.name} ({len(file_entities)} ents)")
            return file_entities, file_rels

        except Exception as e:
            print(f"❌ {file_path.name}: {e}")
            return [], []


# ... (Main function logic)


async def main_async():
    print("=" * 60)
    print("🚀 ASYNC ENTITY EXTRACTION (Gemini 3 Flash)")
    print(f"⚡ Concurrency Limit: {CONCURRENCY_LIMIT}")
    # Force Mode announcement
    if "--force" in sys.argv:
        print("🔥 FORCE MODE ACTIVE: Ignoring existing tags.")
    print("=" * 60)

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    # ... (API Key check)
    if not api_key:
        print("❌ No API Key found.")
        return
    genai.configure(api_key=api_key)

    # Scan Files
    print("🔍 Scanning directories...")
    md_files = get_all_md_files(SCAN_DIRS)
    print(f"   Found {len(md_files)} markdown files")

    # === SAFETY INTERLOCK & COST ESTIMATOR ===
    if "--yes" not in sys.argv and "-y" not in sys.argv:
        # 1. Calculate Volume
        total_chars = 0
        for f in md_files:
            try:
                total_chars += f.stat().st_size
            except Exception:
                pass

        # 3. Estimate Tokens (4 chars = 1 token approx)
        input_tokens = total_chars / 4
        # CORRECTION (2026-02-01): Empirical data shows Output is ~80% of Input (Translation Heavy), not 10%.
        # $1.70 estimate -> $30 actual. We must use 0.8 safety factor.
        output_tokens = input_tokens * 0.8

        # 3. Calculate Cost (Gemini 3 Flash Paid: $0.50/1M input, $3.00/1M output)
        cost_input = (input_tokens / 1_000_000) * 0.50
        cost_output = (output_tokens / 1_000_000) * 3.00
        total_cost = cost_input + cost_output

        # 4. Estimate Time (20 concurrent requests, ~2s latency per batch of 20)
        # 2400 files / 20 = 120 batches. 120 * 2s = 240s = 4 mins.
        est_seconds = (len(md_files) / CONCURRENCY_LIMIT) * 2.5
        est_mins = round(est_seconds / 60, 1)

        print("\n" + "=" * 50)
        print("💰 PRE-FLIGHT COST & TIME ESTIMATE (Gemini 3 Flash)")
        print("=" * 50)
        print(f"   📂 Files to Scan:  {len(md_files)}")
        print(f"   ⏱️  Estimated Time: ~{est_mins} Minutes")
        print(f"   💸 Estimated Cost: ${total_cost:.4f} USD")
        print(f"      (Input: ${cost_input:.4f} | Output: ${cost_output:.4f})")
        print("-" * 50)

        user_input = input("   Shall we proceed? (y/N): ").strip().lower()
        if user_input != "y":
            print("❌ Aborted by user.")
            sys.exit(0)
        print("✅ Proceeding...\n")
    # =========================================

    # OUTPUT_JSONL init
    GRAPHRAG_DIR.mkdir(parents=True, exist_ok=True)
    # If starting fresh (no resume logic yet), maybe clear JSONL?
    # For now, append is safer. We can dedup later.

    # Create Semaphore
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    tasks = []
    print("🌊 Starting Parallel Wave...")
    for f in md_files:
        tasks.append(process_file(f, sem))

    # Execute all
    # We don't strictly need to gather results into memory if we are writing to JSONL
    # But useful for stats
    results = await asyncio.gather(*tasks)

    # === ROBUST AGGREGATION PHASE ===
    print("\n📦 Aggregating Results...")

    # Read from JSONL to be sure we have everything (even from previous runs)
    all_entities = []
    all_rels = []
    seen_files = set()

    if OUTPUT_JSONL.exists():
        with open(OUTPUT_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # Simple dedup by file to avoid double counting if multiple runs
                    if data["file"] in seen_files and "--force" in sys.argv:
                        # logic to handle overwrite?
                        # Actually, complex. Let's just aggregate everything and entity-dedup.
                        pass

                    seen_files.add(data["file"])
                    all_entities.extend(data.get("entities", []))
                    all_rels.extend(data.get("relationships", []))
                except:
                    continue

    # Fallback to in-memory if JSONL failed? No, JSONL is primary now.

    # Deduplicate Entities
    seen = set()
    unique_entities = []
    for e in all_entities:
        # ROBUST KEY CHECK
        name = e.get("name", "").strip()
        if not name:
            continue

        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    output_data = {
        "entities": unique_entities,
        "relationships": all_rels,
        "stats": {
            "files_processed": len(seen_files),
            "total_entities": len(unique_entities),
        },
    }

    OUTPUT_FILE.write_text(json.dumps(output_data, indent=2))
    print("\n" + "=" * 60)
    print(f"💾 Saved {len(unique_entities)} entities to {OUTPUT_FILE}")
    print(f"✅ COMPLETE.")
    print("=" * 60)


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print("Dry run not implemented for async version yet.")
        sys.exit(0)
    asyncio.run(main_async())
