# Athena Spec Sheet

> **Version**: v10.0.6
> **Date**: 17 October 2026
> **Architect**: Winston Koh
> **Status**: Production (2,100+ sessions)

---

## 1. System Overview

**Athena** is a local-first memory, decision engine, and governance harness for AI agents — portable across IDEs. Own the state. Rent the intelligence.

| Attribute | Value |
|-----------|-------|
| **Type** | Local-first memory, decision engine, and governance harness for AI agents |
| **License** | MIT |
| **Runtime** | Python 3.13+ |
| **Primary Storage** | Markdown files (Git-versioned) |
| **Secondary Storage** | Supabase + pgvector (cloud backup + semantic search) |
| **Fallback Storage** | SQLite FTS5 / LanceDB (offline mode) |
| **Interface** | Any MCP-compatible IDE (Antigravity, Claude Code, Cursor, VS Code, Gemini CLI) |

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
| `embedding` | VECTOR(3072) | gemini-embedding-001 |
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

18 tools + 2 resources via Model Context Protocol (`src/athena/mcp_server.py`).

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
| `frame_open` | write | < 50ms |
| `frame_validate` | read | < 50ms |
| `frame_resolve` | write | < 50ms |
| `frame_status` | read | < 50ms |
| `decision_screen` | read | < 50ms |
| `context_gate` | read | < 50ms |
| `meta_awareness_check` | read | < 50ms |
| `classify_turn` | read | instant |
| `search_web` / `report_external_web_search` | read | < 1s |

**Transport**: stdio (IDE integration) or SSE (remote access, port 8765).

---

## 6. Search Architecture

```text
Query → [Keyword Search (Tag Index)] ──┐
                                        ├── RRF Fusion → Reranker → Results
Query → [Semantic Search (pgvector)] ──┘
```

| Metric | Value |
|--------|-------|
| **Search MRR** | 0.44 (vs 0.21 baseline, +105%) |
| **Latency** | < 200ms (p95) |
| **Index Size** | 8,079 tags, 78MB vectors |
| **Fusion Method** | Reciprocal Rank Fusion (RRF) with score-modulated weights |

---

## 7. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.13 |
| **Embeddings** | Google gemini-embedding-001 (3072d) |
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

→ Full benchmarks: [BENCHMARKS.md](./BENCHMARKS.md)

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
| [REQUIREMENTS.md](./REQUIREMENTS.md) | User stories, functional requirements, constraints |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, data flow, hub model |
| [BENCHMARKS.md](./BENCHMARKS.md) | Quantitative performance data |
| [FEATURES.md](./FEATURES.md) | User-facing feature descriptions |
| [CAPABILITIES.md](./CAPABILITIES.md) | Full automation catalog |
| [GLOSSARY.md](./GLOSSARY.md) | Term definitions |
