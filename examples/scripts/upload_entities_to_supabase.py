#!/usr/bin/env python3
"""
upload_entities_to_supabase.py — Upload GraphRAG entities to Supabase

Reads from .agent/graphrag/entities.json and upserts to the 'entities' table.
"""

import os
import sys
import json
from pathlib import Path

# Fix sys.path for SDK access
SDK_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.memory.vectors import get_client, get_embedding

ROOT_DIR = Path(__file__).parent.parent.parent
ENTITIES_FILE = ROOT_DIR / ".agent" / "graphrag" / "entities.json"


def main():
    print("=" * 60)
    print("🚀 UPLOADING ENTITIES TO SUPABASE")
    print("=" * 60)

    if not ENTITIES_FILE.exists():
        print(f"❌ Entity file not found: {ENTITIES_FILE}")
        print("   Run extract_entities.py first.")
        sys.exit(1)

    # Load entities
    data = json.loads(ENTITIES_FILE.read_text())
    entities = data.get("entities", [])
    print(f"📊 Found {len(entities)} entities to upload")

    # Connect to Supabase
    client = get_client()
    print("✅ Connected to Supabase")

    # Upload in batches
    BATCH_SIZE = 50
    uploaded = 0
    errors = 0

    for i in range(0, len(entities), BATCH_SIZE):
        batch = entities[i : i + BATCH_SIZE]

        for entity in batch:
            try:
                # Generate embedding for entity description
                desc = f"{entity['name']}: {entity.get('description', '')}"
                embedding = get_embedding(desc[:500])  # Cap at 500 chars

                # Prepare record
                record = {
                    "entity_name": entity["name"][:255],  # Truncate to fit field
                    "entity_type": entity.get("type", "concept"),
                    "content": entity.get("description", ""),
                    "metadata": {
                        "source_file": entity.get("source_file", ""),
                        "type": entity.get("type", "concept"),
                    },
                    "embedding": embedding,
                }

                # Upsert (insert or update based on entity_name)
                client.table("entities").upsert(record).execute()
                uploaded += 1

            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"   ⚠️  Error uploading {entity['name'][:30]}: {e}")

        print(f"   ⏳ Uploaded {min(i + BATCH_SIZE, len(entities))}/{len(entities)}...")

    print("\n" + "=" * 60)
    print("✅ UPLOAD COMPLETE")
    print(f"   Uploaded: {uploaded}")
    print(f"   Errors: {errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
