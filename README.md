![Athena Banner](./docs/athena_banner.png)

# 🏛️ Project Athena — The Linux OS for AI Agents

![GitHub Stars](https://img.shields.io/github/stars/winstonkoh87/Athena-Public?style=social)
![Last Updated](https://img.shields.io/badge/Last%20Updated-Feb%202026-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-9.0.0-10b981)
![Reddit Views](https://img.shields.io/badge/Reddit_Views-700k+-FF4500?logo=reddit&logoColor=white)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/winstonkoh87/Athena-Public)

> **Athena is not an AI Agent. It is the Linux OS they run on.**
> Open Source · Sovereign · Model-Agnostic

---

## What Is Athena?

Athena gives AI agents something they don't have: **persistent memory, structure, and governance**.

Most AI agents reset every session — brilliant but amnesiac. Athena provides the **state layer** that any agent (Claude, Gemini, GPT, Llama) reads on boot and writes to on shutdown. Think of it as a **memory card** that works in any game console.

| OS Concept | Linux | Athena |
|:-----------|:------|:-------|
| **Kernel** | Hardware abstraction | Memory persistence + retrieval (VectorRAG, Supabase) |
| **File System** | ext4, NTFS | Markdown files, session logs, tag index |
| **Scheduler** | cron, systemd | Heartbeat daemon, daily briefing, auto-indexing |
| **Shell** | bash, zsh | MCP Tool Server, `/start`, `/end`, `/think` |
| **Permissions** | chmod, users/groups | 4-level capability tokens + Secret Mode |
| **Package Manager** | apt, yum | Protocols, skills, workflows |

**You own the data** (Markdown files on your machine, git-versioned). You only **rent the intelligence** (LLM API calls). Switch models tomorrow and your memory stays exactly where it is.

<details>
<summary><strong>💡 "But I have ChatGPT Memory / Claude Projects"</strong></summary>

You're confusing **RAM** with a **Hard Drive**.

ChatGPT Memory and Claude Projects are context window tricks. They are RAM — fast, useful, but fragile. They get wiped, compressed, or hallucinated away.

Athena is a Hard Drive.

| | SaaS Memory (ChatGPT/Claude) | **Athena** |
|:--|:---|:---|
| **Ownership** | Rented (Vendor Lock-in) | **Owned (Local Files)** |
| **Lifespan** | Until session/project deleted | **Forever (Git Versioned)** |
| **Structure** | Opaque Blob | **Structured Knowledge Graph** |
| **Search** | Basic keyword | **Hybrid RAG (5 sources + RRF fusion)** |
| **Agency** | Zero (waits for you) | **Bounded Autonomy (Heartbeat, Cron)** |

| Tool | What It Does | How Athena Differs |
|:-----|:------------|:-------------------|
| **ChatGPT Memory** | Stores flat facts ("User likes Python") | Athena stores **structured state** — project context, decision logs, evolving architecture |
| **Claude Projects** | Single context file per project | Athena is a **multi-file system** with semantic search across 1,000+ documents |
| **Mem0** | SaaS memory layer | Athena is **local-first, MIT-licensed** — your data never leaves your machine |
| **Obsidian + MCP** | Note-taking with AI plugins | Complementary — Athena adds semantic search, auto-indexing, and session lifecycle |
| **Custom RAG** | DIY vector search | Athena includes RAG but adds governance, permissioning, scheduling, and sessions |

</details>

<details>
<summary><strong>📖 Jargon Decoder</strong></summary>

| Athena Term | What It Actually Is | Do You Need It? |
|:------------|:-------------------|:----------------|
| **"Memory"** | RAG — storing text in a database and retrieving it later | **Yes.** This is the core |
| **"Protocols"** | System prompts / reusable instructions | **Yes.** Saved templates for AI behavior |
| **"Cold Storage"** | Markdown files on your disk | **Yes.** Plain text you can read/edit anywhere |
| **"Hot Storage"** | Vector database (Supabase + pgvector) | **Optional.** Enables semantic search |
| **"Heartbeat"** | A background daemon that auto-indexes your files | **Optional.** Passive awareness without manual `/start` |
| **"Adaptive Latency"** | The AI uses more compute for hard tasks, less for easy ones | **Automatic.** You don't configure this |

> 👉 Full glossary: [docs/GLOSSARY.md](docs/GLOSSARY.md)

</details>

---

## ⚡ Quickstart (3 Steps)

| Step | Action |
|:-----|:-------|
| **1. Get an IDE** | [Antigravity](https://antigravity.google/) · [Cursor](https://cursor.com) · [VS Code + Copilot](https://code.visualstudio.com/) · [GitHub Codespaces](https://codespaces.new/winstonkoh87/Athena-Public) |
| **2. Clone this repo** | `git clone https://github.com/winstonkoh87/Athena-Public.git && cd Athena-Public` |
| **3. Open folder → Type `/start`** | The AI reads the repo structure and takes it from there |
| **4. Type `/brief interview`** | Athena asks about YOU — goals, style, domain — and builds your personal profile |

**That's it.** No config files. No API keys. No database setup. The folder *is* the product.

> [!TIP]
> When you're done, type `/end` to save. Next time you `/start`, the agent picks up exactly where you left off.
> Your first session takes ~30 minutes (mostly the interview). Every session after that boots in seconds.

<details>
<summary><strong>🔧 CLI Reference</strong></summary>

```bash
pip install -e .              # Install SDK
athena                        # Boot session
athena init .                 # Initialize workspace in current directory
athena init --ide cursor      # Init with IDE-specific config
athena check                  # System health check
athena save "summary"         # Quicksave checkpoint
athena --end                  # Close session and save
athena --version              # Show version (v9.0.0)
```

</details>

<details>
<summary><strong>📥 Import Existing Data (ChatGPT, Gemini, Claude)</strong></summary>

Athena's memory is just Markdown files. Any text you can export becomes part of your memory:

| Source | How to Import |
|:-------|:-------------|
| **ChatGPT** | Settings → Data Controls → Export → Copy `.md` files into `.context/memories/imports/` |
| **Gemini** | [Google Takeout](https://takeout.google.com/) → Select "Gemini Apps" → Extract into `.context/memories/imports/` |
| **Claude** | Settings → Export Data → Copy transcripts into `.context/memories/imports/` |
| **Any Markdown** | Drop `.md` files into `.context/memories/` — indexed on next `/start` |

After importing, run `athena check` to verify files are detected.

</details>

---

## 🪞 Your First Session

Athena is a **skeleton** — protocols, search, and infrastructure. **You** provide the soul.

On your first `/start`, run `/brief interview`. Athena will ask you about **everything** — your name, profession, goals, decision style, strengths, blind spots, even your life context. This isn't small talk. It's the foundation that makes every future session compound.

| What Athena Asks | Why |
|:----------------|:----|
| **Identity** — Name, age, nationality | Communication style, cultural context |
| **Professional** — Role, industry, salary range | Domain expertise, decision-making context |
| **Goals** — 3-month, 1-year, 5-year | Aligns every response to your actual trajectory |
| **Decision Style** — Risk appetite, speed vs quality | Calibrates how options and tradeoffs are framed |
| **Blind Spots** — Recurring mistakes, weak areas | Athena proactively flags these before they bite |
| **Communication** — Tone, verbosity, directness | Sets the default voice across all interactions |

> [!IMPORTANT]
> **Everything stays local.** Your profile is stored as a Markdown file on your machine (`user_profile.md`). No cloud. No tracking. Be as candid as you want — this is *your* private operating system.

**Pattern:** The more you share → the faster Athena stops being generic → the sooner it starts thinking like **you**.

> 👉 [Full First Session Guide](docs/YOUR_FIRST_SESSION.md) — detailed walkthrough with examples

---

## Core Features

### 🔄 The Loop

After you install Athena, you repeat one cycle: **`/start` → Work → `/end`**. Every cycle deposits training data into memory. Over hundreds of cycles, Athena stops being generic and starts thinking like *you*.

```mermaid
flowchart TD
    START["🟢 /start"] -->|"Load identity + recall"| WORK["🔧 Work Session"]
    WORK -->|"Auto-save every exchange"| WORK
    WORK -->|"Done for the day"| END["🔴 /end"]
    END -->|"Finalize, sync, commit"| MEMORY["🧠 Memory"]
    MEMORY -->|"Next session boots richer"| START

    style START fill:#22c55e,color:#fff,stroke:#333
    style END fill:#ef4444,color:#fff,stroke:#333
    style MEMORY fill:#8b5cf6,color:#fff,stroke:#333
    style WORK fill:#3b82f6,color:#fff,stroke:#333
```

| Sessions | What Happens |
|:---------|:------------|
| **1–50** | Basic recall. Remembers your name and project. |
| **50–200** | Pattern recognition. Anticipates your preferences. |
| **200–500** | Deep sync. Knows your frameworks, blind spots, style. |
| **500–1,000+** | Full context. Anticipates patterns before you state them. |

### 🧠 Persistent Memory

Your data lives in **Markdown files you own** — on your machine, git-versioned. Optionally backed up to Supabase (cloud insurance).

- **Local-first**: No vendor lock-in. Switch models anytime.
- **Hybrid search**: Canonical + GraphRAG + Tags + Vectors + Filenames, fused via RRF
- **Auto-quicksave**: Every exchange is logged without manual action

### 📚 120+ Starter Protocols

[Starter decision frameworks](examples/protocols/) across 13 categories — architecture, engineering, decision-making, reasoning, and more. These are **templates**, not prescriptions. The real value comes when you write your own protocols from your own friction and failures.

### 🔌 MCP Server (9 Tools)

Expose Athena's capabilities to any [MCP-compatible](https://modelcontextprotocol.io/) client:

| Tool | Description |
|:-----|:-----------|
| `smart_search` | Hybrid RAG search with RRF fusion |
| `agentic_search` | Multi-step query decomposition with parallel search |
| `quicksave` | Save checkpoint to session log |
| `health_check` | System health audit |
| `recall_session` | Read session log content |
| `governance_status` | Triple-Lock compliance state |
| `list_memory_paths` | Memory directory inventory |
| `set_secret_mode` | Toggle demo mode (blocks internal tools) |
| `permission_status` | Show access state & tool manifest |

> 👉 [Full MCP Documentation](docs/MCP_SERVER.md)

### ⚡ Slash Workflows

| Command | Purpose |
|:--------|:--------|
| `/start` | Boot system, load identity and context |
| `/end` | Close session, commit to memory |
| `/think` | Deep reasoning mode |
| `/ultrathink` | Maximum depth analysis |
| `/research` | Multi-source web research |
| `/save` | Mid-session checkpoint |
| `/refactor` | Workspace optimization |
| `/plan` | Structured planning with pre-mortem |
| `/vibe` | Ship at 70%, iterate fast |

> 👉 [Full Workflow Documentation](docs/WORKFLOWS.md) — all 20 workflows in [.agent/workflows/](.agent/workflows/)

### 🛡️ Permissioning & Governance

- **4 capability levels**: read → write → admin → system
- **3 sensitivity tiers**: public → internal → restricted
- **Secret Mode**: Toggle for demos — only public tools remain accessible
- **Evaluator Gate**: 50-query regression suite (MRR@5 = 0.44) to prevent search degradation

---

## Repository Structure

```
Athena-Public/
├── src/athena/              # SDK package (pip install -e .)
│   ├── core/                #   Config, governance, permissions, security
│   ├── tools/               #   Search, agentic search, reranker, heartbeat
│   ├── memory/              #   Vector DB, delta sync, schema
│   ├── boot/                #   Orchestrator, loaders, shutdown
│   ├── cli/                 #   init, save commands
│   └── mcp_server.py        #   MCP Tool Server (9 tools, 2 resources)
├── examples/
│   ├── protocols/           # 120+ starter frameworks (13 categories)
│   ├── scripts/             # 17 core OS scripts
│   ├── workflows/           # 20 slash commands
│   ├── templates/           # 36 starter templates
│   └── quickstart/          # Runnable demos
├── docs/                    # Architecture, benchmarks, security, guides
├── community/               # Contributing, roadmap
├── pyproject.toml           # Modern packaging (v9.0.0)
└── .env.example             # Environment template
```

---

## 📣 Community

> **"I gave Gemini a brain..."** — Viral on r/GeminiAI and r/ChatGPT ([700K+ views](https://www.reddit.com/r/ChatGPT/comments/1r1b3gl/))

---

## 📚 Further Reading

<details>
<summary><strong>🏗️ Architecture & Design</strong></summary>

| Document | Description |
|:---------|:-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, hub architecture |
| [SPEC_SHEET.md](docs/SPEC_SHEET.md) | Technical specification, data schema, API surface |
| [GRAPHRAG.md](docs/GRAPHRAG.md) | Knowledge graph layer ⚠️ **~$50 API cost** |
| [VECTORRAG.md](docs/VECTORRAG.md) | Semantic memory implementation |
| [SEMANTIC_SEARCH.md](docs/SEMANTIC_SEARCH.md) | Hybrid RAG implementation |
| [MCP_SERVER.md](docs/MCP_SERVER.md) | MCP architecture & IDE configuration |
| [KNOWLEDGE_GRAPH.md](docs/KNOWLEDGE_GRAPH.md) | Compressed concept index |

</details>

<details>
<summary><strong>🚀 Getting Started & Guides</strong></summary>

| Document | Description |
|:---------|:-----------|
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Step-by-step setup guide |
| [YOUR_FIRST_AGENT.md](docs/YOUR_FIRST_AGENT.md) | 5-minute quickstart |
| [WHAT_IS_AN_AI_AGENT.md](docs/WHAT_IS_AN_AI_AGENT.md) | Beginner primer |
| [DEMO.md](docs/DEMO.md) | Live walkthrough |
| [WORKFLOWS.md](docs/WORKFLOWS.md) | All 48 slash commands |
| [FAQ.md](docs/FAQ.md) | Common questions |
| [GLOSSARY.md](docs/GLOSSARY.md) | Key terms and definitions |

</details>

<details>
<summary><strong>📊 Performance & Case Studies</strong></summary>

| Document | Description |
|:---------|:-----------|
| [BENCHMARKS.md](docs/BENCHMARKS.md) | Boot time, search latency, token economics |
| [CS-001: Boot Optimization](examples/case_studies/CS-001-boot-optimization.md) | 85% boot time reduction |
| [CS-002: Search Quality](examples/case_studies/CS-002-search-quality.md) | RRF fusion results |
| [CS-003: Protocol Enforcement](examples/case_studies/CS-003-protocol-enforcement.md) | Governance engine |
| [TOP_10_PROTOCOLS.md](docs/TOP_10_PROTOCOLS.md) | MCDA-ranked essential protocols |
| [ENGINEERING_DEPTH.md](docs/ENGINEERING_DEPTH.md) | Technical depth overview |

</details>

<details>
<summary><strong>🔒 Security & Data</strong></summary>

| Mode | Where Data Lives | Best For |
|:-----|:----------------|:---------|
| **Local** | Your machine only | Sensitive data, air-gapped environments |
| **Cloud** | Supabase (your project) | Cross-device access |
| **Hybrid** | Local files + cloud embeddings | Best of both |

- Use `SUPABASE_ANON_KEY` for client-side. Never expose `SUPABASE_SERVICE_ROLE_KEY`.
- Enable Row-Level Security on Supabase tables.
- Restrict agent working directories — never grant access to `~/.ssh` or `.env`.

> 👉 [SECURITY.md](docs/SECURITY.md) · [LOCAL_MODE.md](docs/LOCAL_MODE.md)

</details>

<details>
<summary><strong>🧠 Philosophy & Deep Dives</strong></summary>

| Document | Description |
|:---------|:-----------|
| [MANIFESTO.md](docs/MANIFESTO.md) | The Bionic Unit philosophy |
| [USER_DRIVEN_RSI.md](docs/USER_DRIVEN_RSI.md) | How you and AI improve together |
| [TRILATERAL_FEEDBACK.md](docs/TRILATERAL_FEEDBACK.md) | Cross-model validation ("Watchmen") |
| [Quadrant IV](docs/concepts/Quadrant_IV.md) | How Athena surfaces unknown unknowns |
| [Adaptive Latency](examples/concepts/adaptive_latency.md) | Macro-Robust, Micro-Efficient (RETO) |
| [REFERENCES.md](docs/REFERENCES.md) | APA-formatted academic citations |
| [ABOUT_ME.md](docs/ABOUT_ME.md) | About the author |

</details>

<details>
<summary><strong>⚙️ Prerequisites (Optional)</strong></summary>

The quickstart needs **zero configuration**. These are only needed for advanced features:

```bash
# Required for cloud features
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
ANTHROPIC_API_KEY=your-anthropic-key

# Optional (for multi-model validation)
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-key
```

```bash
cp .env.example .env
# Add your keys
```

</details>

<details>
<summary><strong>🛠️ Tech Stack</strong></summary>

| Layer | Technology | Purpose |
|:------|:----------|:--------|
| **SDK** | `athena` Python package (v9.0.0) | Core search, reranking, memory |
| **Reasoning** | Claude Opus (primary) | Main reasoning engine |
| **Optimization** | DSPy | Prompt optimization & self-correction |
| **Reranking** | FlashRank | Lightweight cross-encoder RRF |
| **IDE** | Antigravity, Cursor, VS Code | Agentic development environment |
| **Embeddings** | `text-embedding-004` (768-dim) | Google embedding model |
| **GraphRAG** | NetworkX + Leiden + ChromaDB | Knowledge graph ⚠️ **~$50 API** |
| **Memory** | Supabase + pgvector / local ChromaDB | Vector database |
| **Routing** | CognitiveRouter | Adaptive latency by query complexity |

</details>

<details>
<summary><strong>📋 Changelog</strong></summary>

### February 2026

- **v9.0.0** (Feb 16 2026): **First-Principles Workspace Refactor** — Root directory cleaned (28→14 files), 114 stub session logs archived, build artifacts purged, dead `.framework/v7.0` archived, `.gitignore` hardened. Zero regressions (17/17 tests pass).
- **v8.6.0** (Feb 15 2026): **Massive Content Expansion** — 200 protocols (was 75), 535 scripts (was 16), 48 workflows (was 14), 36 templates. 23 protocol categories. Repo audit for recruiter readiness. Content sanitization pass.
- **v8.5.0** (Feb 12 2026): **Phase 1 Complete** — MCP Tool Server (9 tools, 2 resources), Permissioning Layer (4 levels + secret mode), Search MRR +105% (0.21→0.44), Evaluator Gate (50 queries). SDK v2.0.0.
- **v8.3.1** (Feb 11 2026): **Viral Validation Release** — 654K+ Reddit views, 1,660+ upvotes, 5,300+ shares. #1 All-Time r/ChatGPT, #2 All-Time r/GeminiAI.
- **v8.2.1** (Feb 9 2026): Metrics Sync — Fixed `batch_audit.py` automation, linked orphan files, reconciled tech debt, 8,079 tags indexed

👉 **[Full Changelog](docs/CHANGELOG.md)** — Complete version history from v1.0.0 (Dec 2025)

</details>

---

## License

MIT License — see [LICENSE](LICENSE)

---

*This is a starter kit. Your instance will reflect your domain, your decisions, your voice. Clone it, make it yours.*
