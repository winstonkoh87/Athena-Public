# 🏛️ Welcome to Project Athena

> **The open-source compounding context layer for AI coding agents, portable across IDEs.**
> Persistent memory, structured reasoning, and governed execution · Own the state, rent the intelligence · MIT Licensed

*Last Updated: 2026-10-10 · v10.0.5*

Athena gives any LLM persistent memory and your lived context across coding sessions. It is the **persistent compounding layer** that operates seamlessly across Claude Code, Antigravity, Cursor, Gemini CLI, and VS Code.

| Core Principle | What It Means | Engineering Implementation |
|:---|:---|:---|
| **Own the State** | Complete data sovereignty | Plain Markdown on your machine, git-versioned. No vendor lock-in. |
| **Rent the Intelligence** | Model-agnostic reasoning | Swap models anytime (Gemini 3.8, Claude, GPT). Your memory stays. |
| **Compounding Memory** | Longitudinal context accretion | Chunk-level hybrid RAG (BM25 + vector + RRF + cross-encoder rerank). |
| **Governed Autonomy** | Structural ruin prevention | Law #1 (No Irreversible Ruin), Stop Governance Gate, deterministic receipts. |
| **Zero Infrastructure Cost** | High-performance sovereignty | Local SQLite FTS5 + pgvector on Supabase free tier ($0/month). |

> [!TIP]
> **Before you begin, ask yourself**: *"How do I want Athena to best help me in my daily life and work?"* — This is the guiding principle. Everything else exists to serve your answer. See [Your First Session](../docs/YOUR_FIRST_SESSION.md) for the full onboarding guide.

---

## ⚡ The Core Loop

```
🟢 Lightweight:  Just chat → /end           (~2K tokens)
🔴 Full Boot:    /start → Work → /end       (~10K tokens)
⚫ Deep Boot:    /ultrastart → Work → /ultraend   (~20K tokens)
```

1. **Boot (`/start` or `/ultrastart`)**: Loads Core Identity (2K–20K tokens depending on mode) and relevant context.
2. **Work**: Collaborate with AI to solve problems. Every exchange auto-saves.
3. **Commit (`/end`)**: Summarizes the session, extracts decisions, updates long-term memory.
4. **Compounding**: Next boot starts *smarter*. By session 100, it stops being generic and starts thinking like **you**.

---

## 🚀 Quick Start (5 Minutes)

| Step | Action |
|:-----|:-------|
| **1. Get an IDE** | [Antigravity](https://antigravity.google/) · [Cursor](https://cursor.com) · [Kilo Code](https://kilocode.ai/) · [Zoo Code](https://github.com/Zoo-Code-Org/Zoo-Code) · [Claude Code](https://docs.anthropic.com/en/docs/claude-code) |
| **2. Clone** | `git clone https://github.com/winstonkoh87/Athena-Public.git && cd Athena-Public` |
| **3. Open & Type `/start`** | The AI reads the repo structure and boots |
| **4. Type `/tutorial`** | Athena gives you a guided walkthrough and builds your personal profile |

Or use [GitHub Codespaces](https://codespaces.new/winstonkoh87/Athena-Public) for zero-setup cloud boot.

> See [Getting Started](Getting-Started) for detailed instructions.

---

## 🗺️ Navigation

| Page | Description |
|:-----|:------------|
| **🚀 [Getting Started](Getting-Started)** | Installation, first boot, workspace modes, CLI commands |
| **📖 [Your First Session](../docs/YOUR_FIRST_SESSION.md)** | The intent-first onboarding guide |
| **🏗️ [Architecture](Architecture-Overview)** | OS layers, Hybrid RAG, MCP Server, Tech Stack |
| **⚡ [Workflows](Workflow-Reference)** | `/start`, `/end`, `/do`, `/osint`, `/gto` and 77 commands |
| **🎯 [Use Cases](Use-Cases)** | Decision-making, research, planning, meta-thinking |
| **📈 [The Compounding Effect](The-Compounding-Effect)** | Why Athena gets smarter over time |
| **🧠 [Philosophy](Philosophy)** | Own the state. Rent the intelligence. |
| **❓ [FAQ](FAQ)** | Privacy, cost, models, and comparisons |

---

## 📊 Community & Scale

- **1M+** Reddit Views · **#1 All-Time** on r/ChatGPT · **#2 All-Time** on r/GeminiAI
- **460** Protocols (**426** active across 26 categories) · **291** Scripts · **77** Slash Workflows · **44** Skills
- **2,100+** Sessions Logged · **MIT Licensed** · [Main Repository](https://github.com/winstonkoh87/Athena-Public)
