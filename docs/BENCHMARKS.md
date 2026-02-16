# ⚡ Performance Benchmarks

> **Last Updated**: 16 February 2026  
> **Environment**: MacBook Pro M3, Python 3.13, Supabase (Singapore region)

---

## Boot Sequence Performance

| Metric | Before Optimization | After Optimization | Improvement |
|--------|---------------------|-------------------|-------------|
| Cold Boot | 28.4s | 4.2s | **85% faster** |
| Warm Boot | 12.1s | 2.8s | **77% faster** |
| Identity Hash Verification | 1.2s | 0.3s | **75% faster** |
| GraphRAG Prime | 8.5s | 1.1s | **87% faster** |

### What Changed

- **Persistent Caching**: Protocol loadouts and embeddings cached to disk
- **Parallel Phase Execution**: Boot phases 6 & 7 now run concurrently
- **Hash-based Delta Sync**: Only changed files re-indexed

---

## Semantic Search Performance

| Query Type | Latency (p50) | Latency (p95) | Results Quality |
|------------|---------------|---------------|-----------------|
| Simple keyword | 180ms | 320ms | ⭐⭐⭐ |
| Semantic concept | 420ms | 680ms | ⭐⭐⭐⭐⭐ |
| Cross-domain fusion | 850ms | 1,200ms | ⭐⭐⭐⭐⭐ |

### Search Pipeline

```
Query → Embedding (local) → Parallel Search (Supabase + GraphRAG) → RRF Fusion → Rerank → Top 10
```

**RRF (Reciprocal Rank Fusion)** combines results from:

1. **Supabase pgvector** — Dense vector similarity
2. **GraphRAG Communities** — Structural/relational context
3. **Keyword BM25** — Exact match fallback

---

## Token Economics

| Operation | Tokens (Before) | Tokens (After) | Savings |
|-----------|-----------------|----------------|---------|
| Cold start context injection | ~50,000 | ~4,000 | **92%** |
| Session handoff (`/end`) | ~8,000 | ~1,500 | **81%** |
| Protocol retrieval | ~3,000 | ~800 | **73%** |

### Boot Payload Breakdown (Measured Feb 2026)

The `~4k tokens` figure represents the **Canonical Memory** target — the single materialized view that supersedes searching 500+ session logs. The full enriched boot payload (with user profile and memory bank) is ~17k tokens, loaded adaptively.

| Component | Source File | Est. Tokens | Load Strategy |
|-----------|-------------|:-----------:|:-------------:|
| **Core Identity** | `Core_Identity.md` | ~6,081 | Boot (always) |
| **Canonical Memory** | `CANONICAL.md` | ~3,346 | Boot (always) |
| **Memory Bank** | `memory_bank/` (5 files) | ~3,078 | Boot (always) |
| **User Profile** | `User_Profile_Core.md` | ~4,477 | On-Demand |
| **─── Core Boot Total** | | **~12,504** | |
| **─── Full Enriched Total** | | **~16,981** | |

### How We Achieved This

- **Document Sharding**: Large protocols split into retrievable chunks
- **Summary Caching**: Session summaries pre-computed at `/end`
- **Selective Context**: Only relevant protocols injected per query
- **Canonical Memory**: Single materialized view supersedes searching 500+ session logs

---

## Data Volume Stats

| Asset | Count | Size |
|-------|-------|------|
| Protocols | 308+ | ~1.2 MB |
| Case Studies | 42 | ~2.4 MB |
| Session Logs | 995 | ~3.8 MB |
| GraphRAG Entities | 4,203 | ~46 MB |
| Vector Embeddings | 12,847 | ~78 MB |

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
