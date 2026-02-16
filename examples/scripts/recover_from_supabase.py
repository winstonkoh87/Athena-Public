#!/usr/bin/env python3
"""
athena.scripts.recover_from_supabase
====================================
Disaster Recovery Script: Reconstruct workspace from Supabase.

This script proves the 3-way redundancy claim by downloading all content
from Supabase and reconstructing the local workspace structure.

Usage:
    python recover_from_supabase.py --dry-run          # Preview what would be recovered
    python recover_from_supabase.py --output ./backup  # Recover to specific directory
    python recover_from_supabase.py                    # Recover to default location
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Fix sys.path for SDK access
SDK_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.memory.vectors import get_client

# Table -> Directory mapping (reverse of sync.py)
TABLE_TO_PATH = {
    "sessions": ".context/memories/session_logs",
    "case_studies": ".context/memories/case_studies",
    "protocols": ".agent/skills/protocols",
    "capabilities": ".agent/skills/capabilities",
    "workflows": ".agent/workflows",
    "frameworks": ".framework",
    "references": ".context/references",
    "playbooks": ".context/playbooks",
    "entities": ".context/entities",
    "system_docs": "Athena-Public",
    "user_profile": ".context/profile",
    "insights": "analysis",
}


def get_table_row_count(client, table_name: str) -> int:
    """Get row count for a table."""
    try:
        result = client.table(table_name).select("id", count="exact").execute()
        return result.count or 0
    except Exception as e:
        print(f"  ⚠️  Error counting {table_name}: {e}")
        return 0


def fetch_table_contents(client, table_name: str) -> list:
    """Fetch all rows from a table."""
    try:
        # Select content and file_path (the key columns for recovery)
        result = client.table(table_name).select("content, file_path, title").execute()
        return result.data or []
    except Exception as e:
        print(f"  ❌ Error fetching {table_name}: {e}")
        return []


def recover_table(
    client, table_name: str, output_dir: Path, dry_run: bool = False
) -> dict:
    """Recover all files from a Supabase table."""
    stats = {"recovered": 0, "skipped": 0, "errors": 0}

    rows = fetch_table_contents(client, table_name)
    if not rows:
        return stats

    for row in rows:
        content = row.get("content")
        file_path = row.get("file_path")
        title = row.get("title", "unknown")

        if not content or not file_path:
            stats["skipped"] += 1
            continue

        # Construct output path
        full_path = output_dir / file_path

        if dry_run:
            print(f"    📄 Would create: {file_path}")
            stats["recovered"] += 1
            continue

        try:
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            full_path.write_text(content, encoding="utf-8")
            stats["recovered"] += 1
        except Exception as e:
            print(f"    ❌ Error writing {file_path}: {e}")
            stats["errors"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Recover Athena workspace from Supabase (Disaster Recovery)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview recovery without writing files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for recovered files (default: ./athena_recovery_TIMESTAMP)",
    )
    parser.add_argument(
        "--tables",
        type=str,
        nargs="+",
        default=list(TABLE_TO_PATH.keys()),
        help="Specific tables to recover (default: all)",
    )
    args = parser.parse_args()

    # Set output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"./athena_recovery_{timestamp}")

    print("=" * 60)
    print("🛡️  ATHENA DISASTER RECOVERY")
    print("=" * 60)
    print(f"📂 Output: {output_dir.absolute()}")
    print(
        f"🔧 Mode: {'DRY RUN (no files written)' if args.dry_run else 'LIVE RECOVERY'}"
    )
    print(f"📊 Tables: {', '.join(args.tables)}")
    print("=" * 60)

    # Initialize client
    try:
        client = get_client()
        print("✅ Supabase connection established")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Phase 1: Inventory
    print("\n📊 PHASE 1: INVENTORY")
    print("-" * 40)
    total_rows = 0
    table_counts = {}
    for table in args.tables:
        count = get_table_row_count(client, table)
        table_counts[table] = count
        total_rows += count
        print(f"  {table}: {count} rows")
    print(f"  TOTAL: {total_rows} rows")

    # Phase 2: Recovery
    print("\n🔧 PHASE 2: RECOVERY")
    print("-" * 40)

    total_stats = {"recovered": 0, "skipped": 0, "errors": 0}

    for table in args.tables:
        print(f"\n  📦 Recovering {table} ({table_counts[table]} rows)...")
        stats = recover_table(client, table, output_dir, args.dry_run)

        total_stats["recovered"] += stats["recovered"]
        total_stats["skipped"] += stats["skipped"]
        total_stats["errors"] += stats["errors"]

        print(
            f"     ✅ {stats['recovered']} files | ⏭️ {stats['skipped']} skipped | ❌ {stats['errors']} errors"
        )

    # Summary
    print("\n" + "=" * 60)
    print("📊 RECOVERY SUMMARY")
    print("=" * 60)
    print(f"  ✅ Files recovered: {total_stats['recovered']}")
    print(f"  ⏭️  Rows skipped: {total_stats['skipped']}")
    print(f"  ❌ Errors: {total_stats['errors']}")

    if not args.dry_run and total_stats["recovered"] > 0:
        print(f"\n  📂 Files written to: {output_dir.absolute()}")
        print("\n  🎉 DISASTER RECOVERY COMPLETE")
        print("     Your workspace has been reconstructed from Supabase.")
    elif args.dry_run:
        print("\n  ℹ️  DRY RUN complete. No files were written.")
        print("     Run without --dry-run to perform actual recovery.")

    print("=" * 60)


if __name__ == "__main__":
    main()
