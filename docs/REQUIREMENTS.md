# Athena Requirements Document (Reverse-Engineered)

> **Date**: 6 June 2026
> **Version**: v9.9.9
> **Methodology**: Reverse SDLC — requirements derived from 1,900+ sessions of production use, not written upfront.

> [!NOTE]
> This document was written **after the software was built**. Traditional SDLC writes requirements before code. Athena inverted this: Build → Observe → Extract Patterns → Document Post-Facto. The result is a requirements doc grounded in real usage, not speculation.

---

## 1. Problem Statement

AI assistants are **brilliant but amnesiac**. Every session starts from zero. Users repeatedly re-explain context, preferences, project history, and decision frameworks. Platform-hosted memory (ChatGPT Memory, Claude Projects) is vendor-locked, opaque, and non-portable.

**Core Need**: A local, persistent memory layer that survives across sessions, models, and IDEs — owned by the user.

---

## 2. User Personas

Derived from 662K+ Reddit views and 1,660+ comments across r/ChatGPT and r/GeminiAI.

| Persona | Description | Primary Need | Example Quote (Reddit) |
|---------|-------------|-------------|------------------------|
| **The Solo Dev** | Uses AI daily for coding, wants continuity | Session memory across 100+ sessions | *"So it remembers my codebase?"* |
| **The Researcher** | Manages large knowledge bases, needs retrieval | Semantic search across 1,000+ docs | *"Can it search my notes like Obsidian?"* |
| **The Forgetful User** | Frustrated by re-explaining context every chat | Zero-config persistent memory | *"I'm tired of ChatGPT forgetting everything"* |
| **The Privacy-Conscious** | Refuses to store data on third-party servers | Local-first, no cloud dependency | *"Does my data stay on my machine?"* |
| **The Model Switcher** | Uses Claude today, Gemini tomorrow | Model-agnostic memory layer | *"Does it work with Ollama?"* |

---

## 3. Functional Requirements

### FR-1: Session Lifecycle

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-1.1 | System SHALL boot with full context from last session via `/start` | P0 | ✅ Implemented |
| FR-1.2 | System SHALL persist all session data on `/end` (log, decisions, corrections) | P0 | ✅ Implemented |
| FR-1.3 | System SHALL auto-checkpoint every exchange (quicksave) | P0 | ✅ Implemented |
| FR-1.4 | System SHALL recover gracefully from mid-session crashes | P1 | ✅ Implemented |

### FR-2: Memory & Retrieval

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-2.1 | System SHALL store all memory as human-readable Markdown files | P0 | ✅ Implemented |
| FR-2.2 | System SHALL support semantic search via vector embeddings | P0 | ✅ Implemented |
| FR-2.3 | System SHALL support keyword search via tag index | P0 | ✅ Implemented |
| FR-2.4 | System SHALL combine semantic + keyword search via RRF fusion | P1 | ✅ Implemented |
| FR-2.5 | ~~System SHALL support knowledge graph queries (GraphRAG)~~ | P2 | ❌ REMOVED (S435, 6 June 2026) |

### FR-3: Autonomy

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-3.1 | System SHALL support scheduled background indexing (heartbeat) | P1 | ✅ Implemented |
| FR-3.2 | System SHALL enforce governance rules (Triple Lock) | P0 | ✅ Implemented |
| FR-3.3 | System SHALL support MCP protocol for external tool integration | P1 | ✅ Implemented |

### FR-4: Data Portability

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-4.1 | System SHALL NOT require any specific LLM provider | P0 | ✅ Implemented |
| FR-4.2 | System SHALL work across IDEs (Antigravity, Cursor, VS Code) | P0 | ✅ Implemented |
| FR-4.3 | System SHALL support import of ChatGPT/Gemini/Claude exports | P1 | ✅ Documented |
| FR-4.4 | All user data SHALL be Git-versionable | P0 | ✅ Implemented |

---

## 4. Non-Functional Requirements

| ID | Requirement | Target | Actual |
|----|------------|--------|--------|
| NFR-1 | **Boot Time** | < 2 minutes | **~1–2 minutes** |
| NFR-2 | **Search Latency** | < 500ms | **< 200ms** |
| NFR-3 | **Context Injection** | < 10K tokens | **~4K tokens** |
| NFR-4 | **Privacy** | No data leaves machine (without explicit cloud opt-in) | ✅ Local-first |
| NFR-5 | **Reliability** | Zero data loss across sessions | ✅ Git + Cloud backup |
| NFR-6 | **Extensibility** | Add skills without modifying core | ✅ Modular skill files |

---

## 5. Constraints

| Constraint | Description | Rationale |
|-----------|-------------|-----------|
| **C-1: Local-First** | Primary data store MUST be local filesystem | User data ownership; no vendor lock-in |
| **C-2: Markdown Truth** | Source of truth MUST be human-readable Markdown | Portability; works without any tooling |
| **C-3: No Monoliths** | 1 Skill = 1 File; no mega-config files | Maintainability at scale (431 protocols) |
| **C-4: Kill Switch** | If maintenance > 2 hrs/week for 4 weeks → graceful degradation | Prevent over-engineering (Protocol 106) |
| **C-5: Python 3.10+** | Runtime requirement | Minimum for modern async + type hints |
| **C-6: 16GB RAM** | Recommended for vector operations | pgvector + embedding models |

---

## 6. Acceptance Criteria

| Test | Description | Status |
|------|-------------|--------|
| **The Amnesia Test** | Start a new session. Does it remember the last session? | ✅ Pass |
| **The Crash Test** | Kill the IDE mid-session. Does `/start` recover? | ✅ Pass |
| **The Portability Test** | Switch from Claude to Gemini. Does memory persist? | ✅ Pass |
| **The Search Test** | Query a concept from 500 sessions ago. Is it found? | ✅ Pass (< 200ms) |
| **The Import Test** | Import a ChatGPT export. Is it indexed? | ✅ Pass |
| **The Scale Test** | 1,000+ session logs, 8,000+ tags. Does boot still < 2 min? | ✅ Pass |

---

## 7. Traceability Matrix

| Requirement | Implementing Component | Documentation |
|-------------|----------------------|---------------|
| FR-1.x (Session) | `boot.py`, `shutdown.py`, `quicksave.py` | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| FR-2.x (Memory) | `smart_search.py`, `supabase_sync.py`, `tag_index.py` | [SEMANTIC_SEARCH.md](docs/SEMANTIC_SEARCH.md), [VECTORRAG.md](docs/VECTORRAG.md) |
| FR-3.x (Autonomy) | `heartbeat.py`, `mcp_server.py`, `governance.py` | [MCP_SERVER.md](docs/MCP_SERVER.md) |
| FR-4.x (Portability) | Markdown filesystem, `.env` config | [GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| NFR-1–6 | Benchmarked | [BENCHMARKS.md](docs/BENCHMARKS.md) |

---

> *"The spec sheet I wrote after 1,900 sessions is more accurate than any spec I could have written at session 0."*
