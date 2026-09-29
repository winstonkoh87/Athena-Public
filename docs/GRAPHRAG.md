# GraphRAG: Knowledge Graph Layer

> [!CAUTION]
> **DEPRECATED (6 June 2026)**: GraphRAG was formally removed from Athena in Session S435. The knowledge graph had been stale since February 2025 (16 months) and contributed 0% to retrieval quality. Athena now operates on **7 retrieval channels** without GraphRAG. This document is preserved as historical reference only. See [ARCHITECTURE.md](ARCHITECTURE.md) for the current retrieval stack.

> **Status**: ❌ **REMOVED** (S435, 6 June 2026)
> **Last Updated**: 22 July 2026
> **Weight**: N/A — no longer in RRF fusion

---

> [!CAUTION]
> **GraphRAG is EXPENSIVE.** Building this knowledge graph cost **~$50 in API fees** (using Gemini 3 Flash). Entity extraction requires calling an LLM for every single document chunk. For most use cases, **VectorRAG is FREE and sufficient**. See [VECTORRAG.md](VECTORRAG.md) for the recommended approach.

---

## Overview

Unlike flat vector search, GraphRAG extracts **entities** from your documents and clusters them into **communities** using the Leiden algorithm. This enables:

| Capability | Description |
|------------|-------------|
| **Cross-domain synthesis** | "How does X relate to Y?" queries |
| **Community detection** | Auto-discovers concept clusters |
| **Entity fan-out** | Expands queries to related concepts |

---

## Architecture

```
Documents → Entity Extraction → Knowledge Graph → Community Detection → Search
                                    ↓
                              ChromaDB Vectors
```

### Components

| Component | Format | Size | Purpose |
|-----------|--------|------|---------|
| `communities.json` | JSON | ~800KB | 1,460 auto-detected clusters |
| `entities.json` | JSON | ~2.3MB | Named entity index |
| `knowledge_graph.gpickle` | NetworkX | ~46MB | Graph structure |
| `chroma.sqlite3` | SQLite | ~78MB | Entity vector embeddings |

---

## Retrieval Weight

GraphRAG is weighted **2.0x** in the RRF fusion algorithm — at parity with Vector for balanced retrieval:

| Source | Weight | Rationale |
|--------|--------|-----------|
| **Canonical** | 3.0x | Curated single source of truth |
| **GraphRAG** | 2.0x | Structured knowledge clusters |
| **Vector** | 2.0x | Semantic similarity (parity with Graph) |
| Tags | 1.5x | Explicit keyword matches |
| Filename | 1.0x | Literal file matching |

---

## How It Works

### 1. Community Matching

When you query "sovereignty arbitrage":

```
Query → Tokenize → ["sovereignty", "arbitrage"]
                        ↓
    Search 1,460 communities for keyword matches
                        ↓
    Results: Community 1 (2 hits), Community 0 (1 hit)
```

### 2. ChromaDB Entity Search

Parallel to community matching, the system queries ChromaDB for semantically similar entities:

```
Query → Embed → Vector similarity search → Top 5 entities
```

### 3. RRF Fusion

Both GraphRAG results are fused with other sources using Reciprocal Rank Fusion:

```
Score = Σ (weight × 1/(k + rank))
```

Where `k = 60` (the RRF constant).

---

## Example Output

```
🔍 SMART SEARCH: "sovereignty arbitrage"
============================================================

🏆 TOP 3 RESULTS:

  1. [HIGH] [RRF:0.0574] Community 1 (1712 members, 2 hits)
     Signals: {"graphrag": {"rank": 1, "contrib": 0.05738}}
     📄 Matched: sovereignty, arbitrage | Cluster: #lmarena, #dismissive-avoidant...

  2. [HIGH] [RRF:0.0565] Community 0 (21 members, 1 hits)
     Signals: {"graphrag": {"rank": 2, "contrib": 0.05645}}
     📄 Matched: arbitrage | Cluster: #4, Last Updated, #5...

  3. [HIGH] [RRF:0.0556] Community 504 (13 members, 1 hits)
     Signals: {"graphrag": {"rank": 3, "contrib": 0.05556}}
     📄 Matched: arbitrage | Cluster: 1. Outcome Framing, outcome...
```

---

## When GraphRAG Helps Most

| Query Type | GraphRAG Value | Example |
|------------|----------------|---------|
| Cross-domain | ⭐⭐⭐ High | "How do trading and psychology connect?" |
| Concept clusters | ⭐⭐⭐ High | "What relates to sovereignty?" |
| Specific lookup | ⭐ Low | "Where is Agentic Engineering Strategy?" (use filename search) |
| Semantic match | ⭐⭐ Medium | "Find protocols about risk" (vector also works) |

---

## Re-indexing

To rebuild the knowledge graph after adding new content:

```bash
python3 .agent/scripts/index_graphrag.py
```

This regenerates:

- Entity extraction from all Markdown files
- Community detection via Leiden algorithm
- ChromaDB vector embeddings

---

## Related Documentation

- [VECTORRAG.md](VECTORRAG.md) — Semantic vector search layer
- [ARCHITECTURE.md](ARCHITECTURE.md) — Overall system design
- [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md) — Hybrid RAG implementation

---

## Cost Warning

> [!WARNING]
> **Real-World Cost**: Building the Athena knowledge graph cost **~$30-50 USD** using Gemini 3 Flash API.
>
> **The Hidden Cost Driver**: Output Verbosity.
> The extraction process often prompts the LLM to rewrite nearly 75% of the input text as structured JSON.
>
> - **Input**: 4M tokens (~$2.50)
> - **Output**: 3M tokens (~$12.00+)
>
> **Recommendation**: Unless you specifically need entity relationship mapping ("How does X relate to Y?"), use **VectorRAG** instead. It's free and handles 90% of semantic search use cases.

---

## The Free Alternative: Human-Driven API

> [!TIP]
> **You can build GraphRAG for FREE using the Decoupled Fetch-and-Reason pattern.**

The `$50 API cost` assumes you're running entity extraction programmatically. But the LLM call is the expensive part, not the orchestration. We can decouple them.

### The Pattern: Human as API

```
Athena (Orchestrator)  →  Generates Parsing Prompts  →  User
                                                          ↓
                                                        User pastes into FREE LLM UI
                                                        (Gemini 3.1 Pro on AI Studio, Claude, etc.)
                                                          ↓
User  ←  Pastes LLM Response Back  ←  Athena assembles results
```

**Result**: SOTA entity extraction (Gemini 3.1 Pro, Claude Fable 5) at **$0 cost**.

### Why This Works

| Component | Cost via API | Cost via Human | Notes |
|-----------|--------------|----------------|-------|
| **Orchestration** (splitting docs, generating prompts) | Free | Free | Athena handles this |
| **LLM Inference** (entity extraction) | **$30-50** | **$0** | User uses free web UI |
| **Assembly** (combining results into graph) | Free | Free | Athena handles this |

The only paid component (LLM inference) is replaced by **human bandwidth** — a free resource.

### How to Use It

1. **Athena generates extraction prompts** for each document chunk.
2. **User pastes** each prompt into Gemini/Claude web UI (free tier).
3. **User copies** the structured JSON response back.
4. **Athena assembles** the responses into `knowledge_graph.gpickle`.

> This is the **Decoupled Fetch-and-Reason** pattern from Protocol 404: Decoupled Fetch-and-Reason.

### Trade-offs

| Factor | API Approach | Human-Driven API |
|--------|--------------|------------------|
| **Speed** | Minutes | Hours (manual) |
| **Cost** | $30-50 | $0 |
| **Model Quality** | Flash (cheaper) | Pro (SOTA, free UI) |
| **Scalability** | High | Low (human bottleneck) |

**Verdict**: If you have more time than money, Human-Driven API is the optimal path. You get SOTA model quality (Gemini 3.1 Pro) for free — the same extraction quality that would cost 10x more via API.

---

## When GraphRAG Is Worth It

| Use Case | Worth It? | Why |
|----------|-----------|-----|
| Cross-domain synthesis | ✅ Yes | "How do trading psychology and schema therapy connect?" |
| Entity relationship mapping | ✅ Yes | Building a knowledge graph for research |
| Simple semantic search | ❌ No | VectorRAG is free and sufficient |
| Quick prototype | ❌ No | Too expensive for testing |

---

## Tags

# graphrag #knowledge-graph #rag #search #communities #entities #expensive

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
