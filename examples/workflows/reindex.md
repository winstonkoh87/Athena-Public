---created: 2025-12-15
last_updated: 2026-01-30
---

---description: Supabase-only reindex — sync memory to cloud without full refactor
created: 2025-12-15
last_updated: 2025-12-21
---

# /reindex — Supabase Memory Sync

> **Latency Profile**: LOW (~30s)  
> **Philosophy**: Refresh the cloud memory index without touching content.

---

## Execution

// turbo

```bash
python3 .agent/scripts/supabase_sync.py
```

---

## When to Use

- After adding many new protocols/case studies
- After bulk imports
- When semantic search feels stale
- After archiving or moving files

---

## Verification

```bash
python3 .agent/scripts/supabase_search.py "test query" --limit 3
```

Should return relevant results from recently added content.

---

## Legacy (Deprecated)

> **Note**: GraphRAG local indexing was deprecated in Session 14 (2025-12-21).
> If you ever need to rebuild local GraphRAG:
>
> 1. `python -m venv .agent/graphrag_env`
> 2. `pip install -r .agent/requirements.txt`
> 3. `python3 .agent/scripts/build_graph.py`

---

## Tagging

# workflow #automation #supabase #reindex
