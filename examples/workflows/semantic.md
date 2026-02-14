---created: 2025-12-23
last_updated: 2026-01-30
---

---description: Deep workspace semantic search — query Supabase + local protocols before answering
created: 2025-12-23
last_updated: 2026-01-11
---

# /semantic — Execution Script

> **Latency Profile**: MEDIUM (~5-10s)
> **Philosophy**: Search before you think. Context before reasoning.

---

## Execution

// turbo-all

### Step 1: Run Hybrid Triangulation Search

```bash
python3 .agent/scripts/smart_search.py "<keywords>" --limit 5
```

> **Mechanism**: Tier 1 (Exact Grep), Tier 2 (Semantic Vector), Tier 3 (Filename).

### Step 2: Inject Context Silently

- Surface top 3-5 relevant protocols/case studies
- Do NOT announce findings unless asked. Just use the context.

---

## Example

```
User: /semantic What patterns explain this LinkedIn post?

AI: (Runs smart_search.py)
→ Finds #LinkedIn_Strategy tag
→ Finds Protocol 131 (Vector match)
→ Responds with deep, contextual analysis
```

---

## Integration with /ultrathink

`/ultrathink` automatically triggers `/semantic` as Phase 0 before research.

---

## Tagging

# workflow #automation #semantic #memory #supabase #smart_search
