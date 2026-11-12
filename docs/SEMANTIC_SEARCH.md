# Semantic Search: 5-Channel Parallel Hybrid RAG

> **Last Updated**: 13 November 2026  
> **Purpose**: How Athena finds and retrieves relevant context using five parallel retrieval channels fused via Weighted RRF and cross-encoder reranking

---

## Executive Summary

Athena employs **5-Channel Parallel Hybrid RAG** (`src/athena/tools/search.py`, invoked via `.agent/scripts/smart_search.py`) to capture exact identifiers, canonical rules, semantic concepts, and full-text matches without relying on any single fragile index.

```text
                               USER QUERY
                                   │
                                   ▼
                 classify_query_intent() + Parallel Dispatch
       ┌──────────────┬──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼              ▼
 ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
 │ CANONICAL │  │  VECTOR   │  │ SQLite    │  │ FILENAME  │  │ FRAMEWORK │
 │ (Exact    │  │ (Supabase │  │ FTS5 BM25 │  │ MATCHING  │  │ / KB DOCS │
 │  truths)  │  │ pgvector) │  │ (Lexical) │  │ (Paths)   │  │ (Protocols│
 └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
       └──────────────┴──────────────┼──────────────┴──────────────┘
                                     ▼
                    Weighted RRF Fusion (k=60, intent weights)
                                     │
                                     ▼
                 Cross-Encoder Reranker (top-50 candidates)
                                     │
                                     ▼
                          TOP-K RANKED CONTEXT
```

---

## Why Multiple Channels?

| Channel | Implementation | Catches | Misses |
|:--------|:---------------|:--------|:-------|
| **Canonical** | `collect_canonical()` | High-priority rules & constraints in `.context/CANONICAL.md` | Long-tail history & code |
| **Vector** | `collect_vectors()` | Paraphrases, synonyms, cross-session concepts (`pgvector`) | Exact literals, newest offline edits |
| **FTS5 BM25** | `collect_fts_bm25()` | Exact phrases, symbols, IDs across indexed Markdown/code | Synonyms without keyword overlap |
| **Filename** | `collect_filenames()` | Protocol IDs, script names, workflow/skill paths | Body-only concepts |
| **Framework Docs** | `collect_framework_docs()` | Active protocols, skills, core modules | Session logs & case studies |
| **Web Search** *(opt-in)* | `collect_web_search_v2()` | External live facts (with privacy redaction on personal queries) | Private workspace state |

> **Retired Channels (June 2026)**: Legacy `TAG_INDEX.md` (`generate_tag_index.py`) and local GraphRAG / `exocortex.db` were retired because maintenance cost outweighed recall gains (see [TECH_DEBT.md](./TECH_DEBT.md) and [GRAPHRAG.md](./GRAPHRAG.md)). Local lexical recall is now handled automatically by SQLite FTS5 BM25 plus `PROTOCOL_SUMMARIES.md`.

---

## Pipeline Execution Flow

### 1. Intent Classification & Privacy Guard

`classify_query_intent(query)` routes fusion weights into one of three profiles:

- `PERSONALISED_DECISION`: Elevates `user_profile`, `canonical`, `session`, and `case_study` results (and applies `redact_query_for_web()` if `--web` is enabled).
- `SYSTEM_KNOWLEDGE`: Elevates `protocol`, `capability`, `workflow`, and `filename` while down-weighting already-booted `system_doc` / `framework` files (`1.2`).
- `GENERAL`: Balanced default weights across protocols, capabilities, case studies, and sessions.

### 2. Parallel Collection

All local channels execute concurrently via `ThreadPoolExecutor`, followed by `collect_vectors()` (using `gemini-embedding-001` 3072-dimension embeddings via Supabase RPC) and optional web search. Vector search **always fires** even when local channels hit, ensuring conceptual and synonym queries never short-circuit.

### 3. Weighted Reciprocal Rank Fusion (`k=60`)

Vector results are split by subtype (`protocol`, `case_study`, `session`, `user_profile`, etc.) so `weighted_rrf()` applies source-specific weights.

### 4. Cross-Encoder Reranking

`rerank_results()` scores the top **50** fused candidates (not just top 25) to rescue relevant documents that rank lower in pure RRF, then returns the final `top_k` results.

---

## Usage

```bash
# Standard hybrid search
python3 .agent/scripts/smart_search.py "<query>" --limit 10

# Suppress low-confidence results
python3 .agent/scripts/smart_search.py "<query>" --strict

# JSON output for programmatic consumers / MCP
python3 .agent/scripts/smart_search.py "<query>" --json

# Direct Python SDK entry point
python3 -m athena.tools.search "<query>" --limit 10
```

If Supabase or embedding APIs are unreachable or rate-limited (`429`/`402`/timeout), the CLI falls back gracefully to local channels (FTS5, Canonical, Filenames, Framework Docs) and flags `quality="degraded"` rather than failing silently.

---

## Related Documentation

- [VECTORRAG.md](./VECTORRAG.md) — Deep dive into Supabase pgvector embeddings and RPC design
- [ARCHITECTURE.md](../ARCHITECTURE.md) — Overall system design & MCP tool surface

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](./ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
