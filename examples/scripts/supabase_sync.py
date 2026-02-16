#!/usr/bin/env python3
"""
supabase_sync.py — High-Performance Vector Syncer (v1.2)
Robustness: Periodic Saves & Parallel Execution.
"""

import sys
import argparse
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.memory.sync import sync_file_to_supabase, delete_file_from_vector
from athena.memory.delta_manifest import DeltaManifest

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
    "system_docs": PROJECT_ROOT / ".framework" / "v8.0-alpha" / "modules",
}

# Supplementary logic for siloed directories mapped to existing tables
EXTENDED_TARGETS = [
    (PROJECT_ROOT / "analysis", "case_studies"),
    (PROJECT_ROOT / "Marketing", "system_docs"),
    (PROJECT_ROOT / "proposals", "case_studies"),
    (PROJECT_ROOT / "Winston", "system_docs"),
    (PROJECT_ROOT / "docs" / "audit", "system_docs"),
    (PROJECT_ROOT / "gem_knowledge_base", "system_docs"),
    (PROJECT_ROOT / ".athena", "system_docs"),
    (PROJECT_ROOT / ".projects", "system_docs"),
    (PROJECT_ROOT / "Reflection Essay", "case_studies"),
]


def get_domain(file_path: Path) -> str:
    """Determine the domain of a file based on its path."""
    path_str = str(file_path)
    if "data_lake" in path_str:
        return "personal"
    return "technical"


def sync_file_task(
    file_path: Path, table_name: str, manifest: DeltaManifest, force: bool
):
    """Worker task for a single file."""
    global _processed_count
    try:
        if not force and not manifest.should_sync(file_path):
            return "skipped"

        domain = get_domain(file_path)
        success = sync_file_to_supabase(
            file_path, table_name, extra_metadata={"domain": domain}, manifest=manifest
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

    manifest = DeltaManifest()
    all_tasks = []

    # scan standard targets
    for table, folder in TARGET_DIRS.items():
        if folder.exists():
            files = list(folder.glob("**/*.md"))
            for f in files:
                all_tasks.append((f, table))

    # scan extended targets (silo elimination)
    for folder, table in EXTENDED_TARGETS:
        if folder.exists():
            files = list(folder.glob("**/*.md"))
            for f in files:
                all_tasks.append((f, table))

    stats = {
        "scanned": len(all_tasks),
        "skipped": 0,
        "synced": 0,
        "failed": 0,
        "deleted": 0,
    }

    # 2. Execute Parallel Sync
    print(f"🚀 Processing {len(all_tasks)} files using 5 threads...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(sync_file_task, f, table, manifest, force): f
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
