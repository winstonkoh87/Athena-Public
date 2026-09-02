#!/usr/bin/env python3
"""
supabase_sync.py — Vector Syncer (v1.3)

Throughput model: the only rate-limited step is embedding generation, which is
Semaphore(1)-serialized inside vectors.get_embedding (+1s floor delay/call). Threads
therefore parallelize file I/O + DB upserts, NOT embeds. The speed win comes from
get_embeddings_batch(), which pre-warms the embedding cache in batched API calls so the
per-file pass below hits cache instantly. Upserts (not rate-limited) run across threads.
"""

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.memory.delta_manifest import DeltaManifest
from athena.memory.sync import delete_file_from_vector, sync_file_to_supabase

# Global counter for periodic saving
_processed_count = 0
_save_lock = threading.Lock()

# Target Configuration
MEMORY_DIR = PROJECT_ROOT / ".context" / "memories"
TARGET_DIRS = {
    "sessions": MEMORY_DIR / "session_logs",
    "case_studies": MEMORY_DIR / "case_studies",
    "protocols": PROJECT_ROOT / ".agent" / "skills" / "protocols",
    "capabilities": PROJECT_ROOT / ".agent" / "skills" / "capabilities",
    "workflows": PROJECT_ROOT / ".agent" / "workflows",
    "system_docs": PROJECT_ROOT / ".framework" / "v8.2-stable" / "modules",
    "playbooks": PROJECT_ROOT / ".context" / "playbooks",
    "references": PROJECT_ROOT / ".context" / "references",
    "frameworks": PROJECT_ROOT / ".framework",
    "user_profile": PROJECT_ROOT / ".context" / "memories" / "profile",
}

# Supplementary logic for siloed directories mapped to existing tables
EXTENDED_TARGETS = [
    (PROJECT_ROOT / "analysis", "insights"),
    (PROJECT_ROOT / "Marketing", "system_docs"),
    (PROJECT_ROOT / "proposals", "case_studies"),
    (PROJECT_ROOT / "notes", "system_docs"),
    (PROJECT_ROOT / "docs" / "audit", "system_docs"),
    (PROJECT_ROOT / "knowledge_base", "system_docs"),
    (PROJECT_ROOT / ".athena", "system_docs"),
    (PROJECT_ROOT / ".projects", "system_docs"),
    (PROJECT_ROOT / "journal", "case_studies"),
    (PROJECT_ROOT / ".context" / "brand_references", "references"),
]


def get_domain(file_path: Path) -> str:
    """Determine the domain of a file based on its path."""
    path_str = str(file_path)
    if "data_lake" in path_str:
        return "personal"
    return "technical"


def _rel_db_path(file_path: Path) -> str:
    """Path key used in DB rows + the indexed_files set (relative to project root)."""
    try:
        return str(file_path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(file_path)


def get_db_indexed_files() -> set:
    """Fetch set of (table, file_path) that already have non-null embeddings in DB."""
    try:
        from athena.memory.vectors import get_client
        client = get_client()
    except Exception as e:
        print(f"⚠️  Failed to initialize Supabase client for DB check: {e}")
        return set()

    indexed = set()
    tables = [
        "sessions", "case_studies", "protocols", "capabilities",
        "workflows", "system_docs", "playbooks", "references", "frameworks", "user_profile"
    ]
    print("🔌 Checking database for existing embeddings...")
    for table in tables:
        try:
            res = client.table(table).select("file_path").not_.is_("embedding", "null").execute()
            for row in res.data or []:
                fp = row.get("file_path")
                if fp:
                    indexed.add((table, fp))
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch indexed files for table {table}: {e}")
    print(f"📊 Found {len(indexed)} files with non-null embeddings in database.")
    return indexed


def sync_file_task(
    file_path: Path, table_name: str, manifest: DeltaManifest, force: bool, indexed_files: set
):
    """Worker task for a single file."""
    global _processed_count
    try:
        db_path = _rel_db_path(file_path)
        is_in_db = (table_name, db_path) in indexed_files
        needs_sync = force or manifest.should_sync(file_path) or not is_in_db

        if not needs_sync:
            return "skipped"

        domain = get_domain(file_path)
        success = sync_file_to_supabase(
            file_path, table_name, extra_metadata={"domain": domain}, manifest=manifest, force=needs_sync
        )

        if success:
            with _save_lock:
                _processed_count += 1
                if _processed_count % 50 == 0:
                    manifest.save()  # Periodic save
            return "synced"
        return "failed"
    except Exception as e:
        print(f"  ❌ Error syncing {file_path.name}: {e}")
        return "failed"


def sync_workspace(force: bool = False):
    """Main Orchestrator."""
    start_time = time.time()
    print(f"🔄 Athena Parallel Sync [Force={force}]")

    # Fetch DB indexed files
    indexed_files = get_db_indexed_files()

    manifest = DeltaManifest()
    all_tasks = []

    # scan standard targets
    for table, folder in TARGET_DIRS.items():
        if folder.exists():
            files = list(folder.glob("**/*.md"))
            for f in files:
                # Exclusion logic: do not sync system_docs files as frameworks
                if table == "frameworks" and "v8.2-stable/modules" in str(f):
                    continue
                # Archive pollution guard: never index dead/frozen content. Archived
                # material must not surface in live retrieval.
                if "/archive" in str(f).replace("\\", "/"):
                    continue
                all_tasks.append((f, table))

    # scan extended targets (silo elimination)
    for folder, table in EXTENDED_TARGETS:
        if folder.exists():
            files = list(folder.glob("**/*.md"))
            for f in files:
                if "/archive" in str(f).replace("\\", "/"):
                    continue
                all_tasks.append((f, table))

    # Batch pre-warm embeddings for files that need syncing. This collapses the
    # serialized per-file embed calls (the real bottleneck) into batched API calls,
    # warming the on-disk cache so the per-file pass below hits cache instantly.
    try:
        from athena.memory.vectors import get_embeddings_batch

        pending_texts = []
        for f, table in all_tasks:
            try:
                if (
                    force
                    or manifest.should_sync(f)
                    or (table, _rel_db_path(f)) not in indexed_files
                ):
                    pending_texts.append(f.read_text(encoding="utf-8")[:30000])
            except Exception:
                continue
        if pending_texts:
            print(f"⚡ Batch pre-warming embeddings for {len(pending_texts)} files...")
            get_embeddings_batch(pending_texts)
            print("✅ Embedding cache warmed.")
        else:
            print("⚡ Nothing to embed — all files current.")
    except Exception as e:
        print(f"⚠️  Batch pre-warm skipped ({e}); per-file embedding will be used.")

    stats = {
        "scanned": len(all_tasks),
        "skipped": 0,
        "synced": 0,
        "failed": 0,
        "deleted": 0,
    }

    # 2. Upsert pass: 5 threads parallelize file I/O + DB writes. Embeds are now cache
    #    hits (pre-warmed above) and remain Semaphore(1)-safe in vectors.get_embedding.
    print(f"🚀 Processing {len(all_tasks)} files using 5 threads (embeds pre-warmed)...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(sync_file_task, f, table, manifest, force, indexed_files): f
            for f, table in all_tasks
        }

        for future in as_completed(future_to_file):
            result = future.result()
            stats[result] += 1

    # 3. Cleanup Stale Entries
    flat_all_files = [t[0] for t in all_tasks]
    stale_files = manifest.get_stale_files(flat_all_files)
    if stale_files:
        print(f"🧹 Pruning {len(stale_files)} stale entries...")
        for rel_path in stale_files:
            abs_path = PROJECT_ROOT / rel_path
            if delete_file_from_vector(str(abs_path)):
                manifest.remove_entry(abs_path)
                stats["deleted"] += 1

    # 4. Finalize
    manifest.save()
    duration = time.time() - start_time

    print(f"\n✅ Sync Complete ({duration:.2f}s)")
    print(
        f"   [Scanned: {stats['scanned']} | Skipped: {stats['skipped']} | Synced: {stats['synced']} | Deleted: {stats['deleted']} | Failed: {stats['failed']}]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena High-Performance Sync")
    parser.add_argument(
        "--force", action="store_true", help="Ignore manifest and force re-sync"
    )
    args = parser.parse_args()

    sync_workspace(force=args.force)
