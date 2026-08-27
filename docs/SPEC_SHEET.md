# Athena Spec Sheet

> **Version**: v9.9.9
> **Date**: 6 June 2026
> **Architect**: Winston Koh
> **Status**: Production (1,900+ sessions)

---

## 1. System Overview

**Athena** is a local operating system for AI agents. It provides persistent memory, bounded autonomy, and time-awareness to any LLM.

| Attribute | Value |
|-----------|-------|
| **Type** | Local-first AI agent OS |
| **License** | MIT |
| **Runtime** | Python 3.13+ |
| **Primary Storage** | Markdown files (Git-versioned) |
| **Secondary Storage** | Supabase + pgvector (cloud backup + semantic search) |
| **Fallback Storage** | SQLite / LanceDB (offline mode) |
| **Interface** | Any MCP-compatible IDE (Antigravity, Cursor, VS Code) |

---

## 2. Architecture

```text
┌──────────────────────────────────────────────┐
│              Your Machine (Owned)             │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Markdown  │  │ Session  │  │  Tag Index  │  │
│  │  Files    │  │  Logs    │  │  (8K tags)  │  │
│  └────┬─────┘  └────┬─────┘  └──────┬─────┘  │
│       └──────────────┼───────────────┘        │
│                      ▼                        │
│            ┌──────────────────┐               │
│            │   Git (Versioned) │               │
│            └────────┬─────────┘               │
└─────────────────────┼────────────────────────┘
                      ▼
            ┌──────────────────┐
            │  Supabase Cloud   │
            │  (Insurance Copy) │
            └──────────────────┘
```

### Directory Structure

| Directory | Purpose | Analogy |
|-----------|---------|---------|
| `.framework/` | Core identity, laws, constitution | The DNA |
| `.context/` | Memories, session logs, tag indexes | The Brain |
| `.agent/` | Skills, workflows, scripts | The Hands |
| `src/athena/` | Python SDK (search, MCP, governance) | The Nervous System |
| `docs/` | Documentation | The Manual |
| `examples/` | Quickstart demos, protocols, templates | The Textbook |

---

## 3. Core Loop

```text
/start → Load Identity + Recall → Work Session → Quicksave (auto) → /end → Persist + Git Commit
```

| Phase | Compute Level | Operations |
|-------|--------------|------------|
| `/start` | **Maximum** | Load core identity, recall last session, create log, health check |
| Work | **Adaptive** | Responds at complexity-appropriate depth (Λ+5 to Λ+100) |
| `/end` | **Maximum** | Finalize log, harvest insights, sync memory, git commit |

---

## 4. Data Schema

### Session Logs (Markdown)

```yaml
# Frontmatter
date: 2026-02-13
session: 1085
version: v8.5.0
tags: [memory, search, mcp]

# Body
## Key Decisions
## Checkpoints (auto-appended)
## Synthetic RLHF (end-of-session calibration)
```

### Vector Embeddings (Supabase)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `content` | TEXT | Raw text chunk |
| `embedding` | VECTOR(768) | text-embedding-004 |
| `metadata` | JSONB | Source file, tags, timestamp |

### Tag Index (Markdown)

```text
#memory → 47 files
#search → 31 files
#protocol → 122 files
Total: 8,079 tags
```

---

## 5. API Surface (MCP Server)

9 tools + 2 resources via Model Context Protocol.

| Tool | Permission | Latency |
|------|-----------|---------|
| `smart_search` | read | < 200ms |
| `agentic_search` | read | < 2s (multi-step) |
| `quicksave` | write | < 100ms |
| `health_check` | read | < 500ms |
| `recall_session` | read | < 100ms |
| `governance_status` | read | < 100ms |
| `list_memory_paths` | read | < 100ms |
| `set_secret_mode` | admin | instant |
| `permission_status` | read | instant |

**Transport**: stdio (IDE integration) or SSE (remote access, port 8765).

---

## 6. Search Architecture

```text
 Query
   │
   ├── Canonical      (materialized-view keyword match)   · lexical
   ├── Vector         (Supabase pgvector, cosine)         · semantic
   ├── SQLite         (local file + tag index)            · lexical
   ├── Filename       (path/name keyword match)           · lexical
   ├── Framework Docs (docs + memory-bank grep)           · lexical
   │
   ▼
 Adaptive Router → RRF Fusion (k=60) → Cross-Encoder Reranker → Results
```

Reranking runs default-on via a local quantized ONNX cross-encoder (~0.4s cold load) with a `sentence_transformers` fallback; it degrades to raw RRF order only if both are unavailable.

| Metric | Value |
|--------|-------|
| **MRR@5** | 0.796 |
| **Hit@5** | 0.908 |
| **Coverage** | 0.639 |
| **Fusion Method** | Reciprocal Rank Fusion (RRF, k=60) with score-modulated weights |

> Retrieval metrics measured 18 Jul 2026 on the reference deployment (operator corpus: 4,000+ memory files, 2,000+ session logs) against a 65-query gold set. Your numbers will vary with corpus size and quality.

---

## 7. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.13 |
| **Embeddings** | Google text-embedding-004 (768d) |
| **Vector DB** | Supabase + pgvector (IVFFlat index) |
| **Graph** | ~~Microsoft GraphRAG~~ — REMOVED in S435 (6 June 2026) |
| **Packaging** | pyproject.toml (PEP 621) |
| **Version Control** | Git |
| **CI/CD** | None (single-user local tool) |
| **Hosting** | Local machine (primary), GitHub (remote backup) |

---

## 8. Governance & Constraints

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **Triple Lock** | Every session: Search → Save → Output | `governance.py` |
| **Doom Loop** | Same tool call 3x with identical args → halt | `governance.py` |
| **Granular Permissions** | allow/ask/deny per tool with glob patterns | `permissions.py` |
| **No Monoliths** | 1 Skill = 1 File | Convention + audit scripts |
| **Entropy Limit** | Maintenance > 2 hrs/week for 4 weeks → degrade gracefully | Protocol 106 |
| **Amnesia Failure** | Session restore fails 3x/month → system declared FAILED | Boot health check |
| **Secret Mode** | Demo mode blocks internal tools, redacts sensitive content | `permissions.py` |

---

## 9. Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Boot time | < 2 min | **~1m 45s (1–2 min)** |
| Search latency | < 500ms | **< 200ms** |
| Context injection | < 20K tokens (10% ECL) | **~10K tokens** |
| Quicksave overhead | < 500ms | **< 100ms** |
| Session log write | < 1s | **< 500ms** |

→ Full benchmarks: [BENCHMARKS.md](docs/BENCHMARKS.md)

---

## 10. Acceptance Criteria

| Test | Expected | Result |
|------|----------|--------|
| **Sunset Test** | Unused skills auto-archived after 90 days | ✅ Protocol 106 |
| **Sidecar Verify** | Agent queries vector index, not raw grep | ✅ pgvector + RRF |
| **Triple Lock** | Log entries exist for every session | ✅ Enforced by governance engine |
| **Crash Recovery** | `/start` after crash restores last checkpoint | ✅ Quicksave durability |
| **Model Swap** | Memory persists across LLM provider switch | ✅ Markdown-based |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | User stories, functional requirements, constraints |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, hub model |
| [BENCHMARKS.md](docs/BENCHMARKS.md) | Quantitative performance data |
| [FEATURES.md](docs/FEATURES.md) | User-facing feature descriptions |
| [CAPABILITIES.md](docs/CAPABILITIES.md) | Full automation catalog |
| [GLOSSARY.md](docs/GLOSSARY.md) | Term definitions |
