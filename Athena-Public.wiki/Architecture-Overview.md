# 🏗️ Architecture Overview

Athena is the **Operating System for AI Agents** — a Hybrid RAG system that keeps your data locally (Markdown) and optionally syncs to the cloud (Supabase) for fast semantic retrieval.

*Last Updated: 2026-08-27 · v9.9.8*

---

## 🧠 The OS Analogy

> **Athena is not a coding assistant. It is the infrastructure that gives AI agents state, structured reasoning, and governed autonomy.**

| OS Layer | Linux | Athena |
|----------|-------|--------|
| **Kernel** | Hardware abstraction | Memory persistence + retrieval (Hybrid RAG, Supabase) |
| **File System** | ext4, NTFS | Markdown files, session logs, tag index |
| **Scheduler** | cron, systemd | Heartbeat daemon, auto-indexing |
| **Shell** | bash, zsh | MCP Tool Server, `/start`, `/end`, `/think` |
| **Permissions** | chmod, users/groups | 4-level capability tokens + Secret Mode |
| **Package Manager** | apt, yum | Protocols, skills, workflows |

---

## 🏛️ The Hub Architecture

Athena is a central brain that connects to external project folders.

```mermaid
graph TD
    subgraph "Your Desktop"
        CLIENT_A["📁 Client-A"]
        CLIENT_B["📁 Client-B"]
        SIDE["📁 Side Project"]
    end

    subgraph "The OS"
        ATHENA["🧠 Project Athena"]
    end

    subgraph "The Interface"
        IDE["⚡ Agentic IDE"]
        USER["👤 You"]
    end

    USER --> IDE
    IDE <--> ATHENA
    ATHENA <-.-> CLIENT_A
    ATHENA <-.-> CLIENT_B
    ATHENA <-.-> SIDE

    style ATHENA fill:#16a34a,stroke:#333,stroke-width:2px
    style IDE fill:#2563eb,stroke:#333,stroke-width:2px
```

| Component | Role |
|-----------|------|
| **Athena** | The OS — memory, scheduling, governance |
| **External Folders** | The Body — client projects, side projects |
| **Agentic IDE** | The Nervous System — compute & interface |

### Workspace Modes

| Mode | Setup | Best For |
|:-----|:------|:---------|
| **Standalone (Recommended)** | Open `Athena/` as your workspace | Personal brain, all-in-one users |
| **Multi-Root (Sidecar)** | Open your project → add `Athena/` folder | Devs with existing repos |
| **Nested** | Drop your project inside `Athena/` | Quick prototypes |

> **Tip**: Start with **Standalone**. Graduate to Multi-Root when you need your project visible in the same window.

---

## 🧩 System Layers

Three primary layers:

1. **The Soul (`.framework/`)**: Immutable laws, identity core, operating principles.
2. **The Brain (`.context/`)**: Long-term memory — session logs, case studies, user profile, active context.
3. **The Hands (`.agent/`)**: Executable scripts, tools, protocols, workflows.

### The Biological Stack (v9.9.1+)

Athena also models itself after the human body — built bottom-up by the creator, used top-down by the user:

| Biology | Athena | What It Does |
|---------|--------|-------------|
| Atom | Rule / Axiom | Smallest indivisible truth (`Law #1: No Irreversible Ruin`) |
| Molecule | Protocol (`.md`) | Rules composed into a reusable procedure |
| Cell | Skill | Self-contained executable unit |
| Organ | Cognitive Cluster | Multi-skill unit for one cognitive domain (15 clusters) |
| Organ System | Cognitive System | Multi-cluster orchestration for a human need archetype (8 systems) |
| Organism | Athena | The complete synthetic intelligence |

The **8 Cognitive Systems** (Survival, Life Decision, Trading, Social, Execution, Growth, Learning, Maintenance) are dispatched by an **Intent Classifier** (P508) that routes by *human need archetype*, not keywords. See [P507: Cognitive Systems](https://github.com/winstonkoh87/Athena-Public/blob/main/examples/protocols/architecture/507-cognitive-systems.md) for details.

```mermaid
graph TD
    subgraph Local_Filesystem ["Local: Your Machine"]
        Framework[".framework<br/>(Core Identity)"]
        Context[".context<br/>(Memories)"]
        Agent[".agent<br/>(Scripts & Tools)"]
    end

    subgraph Cloud_Infrastructure ["Cloud: Supabase (Optional)"]
        VectorDB[("pgvector<br/>Embeddings")]
    end

    subgraph Intelligence ["AI Models (Any)"]
        Gemini["Gemini 3.5 Pro"]
        Claude["Claude Fable 5"]
    end

    Agent -->|Reads| Framework
    Agent -->|Reads/Writes| Context
    Agent -->|Syncs| VectorDB
    VectorDB -->|Retrieves| Agent
    Agent -->|Infers| Gemini
    Agent -->|Infers| Claude
```

---

## 🔌 MCP Server

*As of v9.9.8.* 10 tools + 2 resources via [Model Context Protocol](https://modelcontextprotocol.io/). Dual transport (stdio + SSE).

| Tool | Permission | Description |
|------|-----------|-------------|
| `smart_search` | read | Hybrid RAG with RRF fusion |
| `agentic_search` | read | Multi-query decomposition + validation |
| `quicksave` | write | Save checkpoint to session log |
| `health_check` | read | System health audit |
| `recall_session` | read | Read session log content |
| `governance_status` | read | Triple-Lock compliance state |
| `list_memory_paths` | read | Memory directory inventory |
| `meta_awareness_check` | read | Structural act classification (T1–T5) + kernel injection |
| `set_secret_mode` | admin | Toggle demo mode |
| `permission_status` | read | Show access state & tool manifest |

> This table said "9 tools" and omitted `meta_awareness_check` until 2026-07-25.
> The tool had in fact been *defined twice* in `mcp_server.py`, and the later
> definition silently shadowed the earlier, permission-gated one — so the count
> was wrong in one direction and the governance behaviour wrong in the other.
> Both fixed in v9.9.8.

### 🚪 AgentGate (v9.9.8+)

A model-agnostic interception layer, so governance does not depend on any one
IDE's hook system. Two entry points:

| Call | What it does |
|:-----|:-------------|
| `AgentGate.intercept_prompt(prompt)` | Classifies the act (T1 inbound-narrative, T2 outbound-commit, T3 third-party-verdict, T4 resource-commitment, T5 felt-evidence) and returns a system-reminder to inject, or `None` |
| `AgentGate.intercept_tool(name, args)` | Runs `StructuredRuinCheck` over the proposed call and vetoes destructive ones — `rm -rf` against `.context`, `.agent/config`, or `/` |

`StructuredRuinCheck` returns a `(allowed, flags)` pair rather than a bare
boolean, so a refusal names *which* rule fired (`targets_context_memory`,
`targets_agent_config`, `targets_root_directory`) instead of failing opaquely.

---

## ⚡ The Retrieval Pipeline (Hybrid RAG)

Five live channels fused via Reciprocal Rank Fusion (RRF) — **Vector is the only semantic channel**; the rest are lexical (filename/keyword-based):

1. **Canonical Search**: Keyword match against `CANONICAL.md` (materialized decisions/frameworks).
2. **Vector Search** *(semantic)*: Chunk-level embeddings (`gemini-embedding-001`, 3072-dim) via Supabase pgvector, cosine similarity.
3. **SQLite Search**: Local file + tag index.
4. **Filename Search**: Project-root keyword matching.
5. **Framework Docs Search**: `.framework/` + memory-bank + `.context/` lookup.

Results are reranked using a **CrossEncoder** (`cross-encoder/ms-marco-MiniLM-L6-v2`) and scored by an **Adaptive Router** (query-complexity-based channel weighting).

> **Result**: Athena finds the *meaning*, not just the word — though semantic recall is currently bounded by what's embedded in Supabase (see [SEMANTIC_SEARCH.md](https://github.com/winstonkoh87/Athena-Public/blob/main/docs/SEMANTIC_SEARCH.md) for the honest breakdown).
>
> *Two channels — a Tags index and a GraphRAG knowledge-graph pass — were retired in June 2026 as dead weight (zero functional contribution). This page previously described them as active; corrected here.*

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:------|:----------|:--------|
| **SDK** | `athena` Python package (v9.9.8) | Core search, reranking, memory |
| **Reasoning** | Gemini 3.5 Pro (High) / Claude Fable 5 (High) / GPT-5.6 Sol (Max) | Multi-model reasoning |
| **Reranking** | Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`) | Second-stage reranking after RRF fusion |
| **IDE / Agent** | Antigravity, Cursor, Claude Code, Gemini CLI, VS Code | Agentic development environment |
| **Embeddings** | `gemini-embedding-001` (3072-dim) | Google embedding model |
| **Memory** | Supabase + pgvector (chunk-level, exact-scan) | Vector database |
| **Routing** | Risk-Proportional Triple-Lock (SNIPER / STANDARD / ULTRA) | Adaptive latency by query complexity |
| **File Watcher** | Watchdog (event-driven) | Auto-index on file change |

> *GraphRAG (NetworkX + Leiden + ChromaDB) was formally removed in June 2026 — dead 16 months, zero functional contribution. Removed from this table; previously listed here as active.*
