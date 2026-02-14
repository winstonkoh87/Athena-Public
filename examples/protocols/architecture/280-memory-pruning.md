---
created: 2026-01-29
last_updated: 2026-01-30
graphrag_extracted: true
---

---id: 280
title: Memory Pruning Protocol
category: architecture
tags: [memory, optimization, vector, semantic]
created: 2026-01-29
last_updated: 2026-01-29
---

# Protocol 280: Memory Pruning

> **Purpose**: Prevent "Memory Bloat" by archiving old session logs while preserving semantic accessibility.
> **Trigger**: Automated (monthly) or manual (`/prune`)

## The Problem

- Session logs accumulate indefinitely in the "hot" vector index.
- Old sessions pollute semantic search results with outdated context.
- Context window bloat reduces reasoning quality.

## The Solution

**Tiered Memory Architecture**:

| Tier | Age | Location | Searchability |
|------|-----|----------|---------------|
| **Hot** | 0-30 days | `session_logs/` + Supabase vector | Full-text + Semantic |
| **Warm** | 31-90 days | `session_logs/archive/` | Summaries in vector only |
| **Cold** | 90+ days | Compressed `.gz` | Local grep only |

## Implementation

### Phase 1: Summarization

For each session > 30 days old:

1. Generate a **Semantic Summary** (3-5 bullet points of key insights).
2. Store summary in `session_summaries.md` (indexed).
3. Remove raw log from Supabase vector index.

### Phase 2: Archival

For each session > 90 days old:

1. Move raw log to `archive/cold/`.
2. Compress with `gzip`.
3. Delete from local `session_logs/`.

## Execution

```bash
# Manual trigger
python3 .agent/scripts/prune_sessions.py

# Automated (cron)
0 0 1 * * cd /path/to/athena && python3 .agent/scripts/prune_sessions.py
```

## Verification

- `supabase_search.py "old topic"` should return summary, not raw log.
- Total vector entries should decrease after pruning.

## Tags

# memory #optimization #architecture #protocol-280
