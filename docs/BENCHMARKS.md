# ⚡ Performance Benchmarks

> **Last Updated**: 1 September 2026  
> **Environment**: MacBook Pro M3, Python 3.13, Supabase (Singapore region)

---

## Boot Sequence Performance

| Metric | Measured |
|--------|----------|
| Cold Boot (full `/start` sequence) | ~1m 45s (1–2 minutes) |
| Warm Boot (cached, no script re-run) | ~30–60 seconds |
| Identity Hash Verification | ~0.3s |
| Search Index Prime | ~1–2s |

> [!NOTE]
> Boot time includes: loading 3 core identity files, running `boot.py` (session recall + creation + context capture + semantic prime), and the Athena daemon startup. The ~1m 45s figure is the end-to-end measured time on an M3 MacBook Pro.
>
> **Sovereign/Bionic Trade-off**: We consciously accept a ~1m 45s delay in exchange for system-wide robustness. This duration ensures the total cognitive surface (laws, identity, memory bank) is loaded, structured, and semantically primed before the first user query—preventing amnesia, context drift, and grounding failures that plague "fast-boot" stateless agents.

### Optimizations Applied

- **Persistent Caching**: Embeddings cached to disk, delta sync on changed files
- **Parallel Phase Execution**: Boot phases run concurrently where possible
- **Canonical Memory**: Single materialized view replaces querying 1,900+ session logs

---

## Semantic Search Performance

| Query Type | Latency (p50) | Latency (p95) | Results Quality |
|------------|---------------|---------------|-----------------|
| Simple keyword | 180ms | 320ms | ⭐⭐⭐ |
| Semantic concept | 420ms | 680ms | ⭐⭐⭐⭐⭐ |
| Cross-domain fusion | 850ms | 1,200ms | ⭐⭐⭐⭐⭐ |

### Search Pipeline

```
Query → Adaptive Router → 5 parallel channels → RRF Fusion (k=60) → Cross-Encoder Rerank (ONNX) → Top 10
```

**RRF (Reciprocal Rank Fusion)** combines results from five channels:

1. **Canonical** — materialized-view keyword match (lexical)
2. **Supabase pgvector** — dense vector similarity (the only semantic channel)
3. **SQLite** — local file + tag index (lexical)
4. **Filename** — path and name matching (lexical)
5. **Framework Docs** — docs + memory-bank grep (lexical)

**Retrieval quality (65-query gold set, 29 Aug 2026)**: MRR@5 **0.769** · Hit@5 **0.892** · Coverage **0.639** — measured end-to-end on the reference deployment with reranking on.

> **Note**: GraphRAG communities were removed as a search source in S435 (6 June 2026).

---

## Token Economics

| Operation | Tokens (Before) | Tokens (After) | Savings |
|-----------|-----------------|----------------|---------|
| Cold start context injection | ~50,000 | ~10,000 (core boot) | **80%** |
| Full enriched boot (with profile) | ~50,000 | ~14,500 | **71%** |
| Session handoff (`/end`) | ~8,000 | ~1,500 | **81%** |
| Protocol retrieval | ~3,000 | ~800 | **73%** |

### Boot Payload Breakdown (Measured Feb 2026)

The core boot payload is **~10K tokens** — always loaded on `/start`. The full enriched payload (with user profile and on-demand files) is **~14.5K tokens**, loaded adaptively. The Canonical Memory alone is ~4.3K tokens — a single materialized view that supersedes searching 1,900+ session logs.

| Component | Source File | Est. Tokens | Load Strategy |
|-----------|-------------|:-----------:|:-------------:|
| **Core Identity** | `Core_Identity.md` | ~3,800 | Boot (always) |
| **Canonical Memory** | `CANONICAL.md` | ~4,300 | Boot (always) |
| **User Context** | `userContext.md` | ~590 | Boot (always) |
| **Product Context** | `productContext.md` | ~345 | Boot (always) |
| **Active Context** | `activeContext.md` | ~930 | Boot (always) |
| **User Profile** | `User_Profile_Core.md` | ~4,477 | On-Demand |
| **─── Core Boot Total** | | **~9,965** | |
| **─── Full Enriched Total** | | **~14,442** | |

### How We Achieved This

- **Document Sharding**: Large protocols split into retrievable chunks
- **Summary Caching**: Session summaries pre-computed at `/end`
- **Selective Context**: Only relevant protocols injected per query
- **Canonical Memory**: Single materialized view supersedes searching 1,900+ session logs

---

## Data Volume Stats

| Asset | Count | Size |
|-------|-------|------|
| Protocols & Workflows | 452 protocols (418 active + 34 archived), 74 workflows | ~2.5 MB |
| Case Studies | 492 (15 domains) | ~4.8 MB |
| Session Logs | 2,100+ | ~8.5 MB |
| Memory Files | 4,361 | — |
| Vector Embeddings | 12,800+ | ~78 MB |

---

## Reliability Metrics

| Metric | Value |
|--------|-------|
| Boot Success Rate | 99.2% |
| Search Availability | 99.8% |
| Data Redundancy | 3-way (Local + GitHub + Supabase) |
| Recovery Time (from cloud) | < 5 minutes |

---

## Methodology

All benchmarks measured with:

```bash
time python3 .agent/scripts/boot.py
time python3 .agent/scripts/smart_search.py "test query"
```

Latency measurements averaged over 50 runs. Token counts measured via Anthropic/OpenAI token counters.

---

*These numbers are real production metrics from a live system, not synthetic benchmarks.*
