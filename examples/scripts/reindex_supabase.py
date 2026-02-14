#!/usr/bin/env python3
"""
reindex_supabase.py — Optimize Supabase Vector Indexes
======================================================
Re-indexes pgvector (ivfflat) columns for all memory tables.
Run after significant data additions to maintain search performance.

Usage:
    python3 reindex_supabase.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup Path to import athena
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from athena.memory.vectors import get_client
except ImportError:
    print("❌ Error: athena package not found in src/")
    sys.exit(1)

# Index Mapping based on schema variations
# Core: idx_{table}_embedding
# Expansion: {table}_embedding_idx
INDEX_MAP = {
    # Core Tables
    "sessions": "idx_sessions_embedding",
    "protocols": "idx_protocols_embedding",
    "case_studies": "idx_case_studies_embedding",
    
    # Expansion Tables
    "playbooks": "playbooks_embedding_idx",
    "capabilities": "capabilities_embedding_idx",
    "references": "references_embedding_idx",
    "frameworks": "frameworks_embedding_idx",
    "workflows": "workflows_embedding_idx",
    
    # Others (Confirmed via 003_full_workspace_sync.sql)
    "user_profile": "user_profile_embedding_idx",
    "system_docs": "system_docs_embedding_idx",
    "entities": "entities_embedding_idx"
}

INDEX_SQL = [
    f"REINDEX INDEX {index_name};" for table, index_name in INDEX_MAP.items()
]

# Addition metadata-based indexes
OTHER_INDEX_SQL = [
    "REINDEX INDEX idx_sessions_date;",
    "REINDEX INDEX idx_case_studies_code;",
    "REINDEX INDEX idx_protocols_code;",
    "REINDEX INDEX idx_protocols_category;"
]

def main():
    print("=" * 60)
    print("🚀 SUPABASE RE-INDEXING ORCHESTRATOR")
    print("=" * 60)
    
    # 1. Generate SQL
    full_sql = "-- RE-INDEXING SCRIPT\n"
    full_sql += "\n".join(INDEX_SQL) + "\n\n"
    full_sql += "-- Standard Indexes\n"
    full_sql += "\n".join(OTHER_INDEX_SQL)
    
    print(f"\n📋 SQL GENERATED ({len(INDEX_MAP)} vector tables):")
    print("-" * 30)
    print(full_sql)
    print("-" * 30)
    
    # 2. Attempt Execution (if possible)
    # Note: Supabase Python client doesn't support REINDEX via PostgREST.
    # We check if direct postgres connection is configured or suggest Dashboard.
    
    print("\n⚠️  Supabase PostgREST (Python Client) does not support DDL (REINDEX).")
    print("   Please execute the SQL above in the Supabase Dashboard SQL Editor:")
    print("   → https://supabase.com/dashboard/project/_/sql")
    
    # Optional: Save to a temp .sql file for easy copy-paste
    sql_file = PROJECT_ROOT / "supabase" / "migrations" / "999_manual_reindex.sql"
    sql_file.parent.mkdir(parents=True, exist_ok=True)
    sql_file.write_text(full_sql)
    
    print(f"\n💾 SQL saved to: {sql_file.relative_to(PROJECT_ROOT)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
