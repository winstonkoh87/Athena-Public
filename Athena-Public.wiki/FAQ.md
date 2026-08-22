# ❓ Frequently Asked Questions

*Last Updated: 2026-08-23 · v9.9.8*

---

### 💰 Is this free?

**Yes.** Athena is open-source (MIT License). The only cost is your AI subscription — the LLM that reads your Athena workspace.

| Tier | Example Plans | Cost (USD) |
|:-----|:-------------|:-----------|
| **Free** | Google Antigravity (free tier) | **$0** |
| **Entry** | Claude Pro · Google AI Pro | ~$20/mo |
| **Power** | Claude Max 20× · Google AI Ultra | $200–250/mo |

**Start free with Antigravity.** Upgrade to $20/month when you hit daily limits.

### 🚀 How do I install it?

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git MyAgent
cd MyAgent
# Open in Antigravity, Cursor, or VS Code → type /start
```

Or use [GitHub Codespaces](https://codespaces.new/winstonkoh87/Athena-Public) for zero-setup.

See the [Getting Started](Getting-Started) page for full details.

### 🤖 How is this different from ChatGPT / Claude Memory?

**You're confusing RAM with a Hard Drive.**

| | SaaS Memory (ChatGPT/Claude) | **Athena** |
|:--|:---|:---|
| **Ownership** | Rented (Vendor Lock-in) | **Owned (Local Files)** |
| **Lifespan** | Until session/project deleted | **Forever (Git Versioned)** |
| **Structure** | Opaque Blob | **Structured Knowledge Graph** |
| **Search** | Basic keyword | **Hybrid RAG (5 sources + RRF fusion)** |
| **Portability** | Locked to one platform | **Model-agnostic, IDE-agnostic** |
| **Agency** | Zero (waits for you) | **Bounded Autonomy (Heartbeat, Cron)** |

### 🔒 Is my data private?

**Yes.**

- Your "Brain" lives in local Markdown files on your disk.
- Embeddings are sent to Supabase (if configured), but you control the keys.
- There is no middleman. No telemetry. No server.

### 🧠 Can I use other models (OpenAI, Llama)?

Athena is model-agnostic by design. It's optimized for **Gemini 3.5 Pro** and **Claude Fable 5** because of their large context windows, but the memory layer works with any LLM. That's the point — *own the state, rent the intelligence*.

### 📉 Does it hallucinate?

All LLMs hallucinate. Athena minimizes this via **Hybrid RAG** — forcing the model to read *your own notes* before answering. Agentic Search adds cosine validation to filter low-confidence results. Five live retrieval channels (Canonical, Vector/semantic, SQLite, Filename, Framework Docs) are fused via RRF, then reranked with a cross-encoder, for robust recall. (A Tags channel and a GraphRAG pass were retired in June 2026 — dead weight, zero functional contribution.)

### ❓ Won't this eat my subscription tokens?

**No.** The boot cost ranges from **2K–20K tokens** depending on session mode — that's per **context window** (1-10% of one session), not per subscription. Your subscription limits are based on **message count**, not token count — whether you send a 10K or 200K message, it counts as one message.

| User Type | Plan | Sessions/Day | Verdict |
|:----------|:-----|:-------------|:--------|
| **Casual** | Pro ($20/mo) | 1–2 | ✅ 95% of context stays free |
| **Daily Driver** | Max 5× ($100/mo) | 3–5 | ✅ Each session is independent |
| **Power User** | Max 20× ($200/mo) | 10+ parallel | ✅ Multiple agents, multiple projects |

### 📁 Should I put my project inside or outside the Athena folder?

**Start with Standalone** (Athena as its own workspace). If you need both visible, use **Multi-Root (Sidecar)**.

See [Architecture Overview — Workspace Modes](Architecture-Overview#workspace-modes) for details.

### 🔄 What IDE should I use?

Athena works with any agent that can read Markdown files. For first-class integrations with `athena init`:

- **Claude Code** — `athena init --ide claude`
- **Antigravity** — `athena init --ide antigravity`
- **Cursor** — `athena init --ide cursor`
- **Gemini CLI** — `athena init --ide gemini`
- **VS Code + Copilot** — `athena init --ide vscode`
- **Kilo Code** — `athena init --ide kilocode`
- **Zoo Code** — `athena init --ide zoocode`

See the [full compatibility guide](../docs/COMPATIBLE_IDES.md).

### 🎨 How do I customize the AI's personality?

Edit `.framework/v8.2-stable/modules/Core_Identity.md`. This file contains the **Laws** (non-negotiable rules), **Committee Seats** (reasoning perspectives), and **reasoning standards** that shape how Athena thinks and responds. Look for `[CUSTOMIZE]` markers to add your own rules.

For output formatting preferences, edit `.framework/v8.2-stable/modules/Output_Standards.md`.

See the [.framework README](../README.md) for a guide.

### 🎁 Why is this open-source and free?

**Because the value isn't in the code — it's in the data.**

The architecture is the storefront. Your sessions, decisions, case studies, and accumulated context — that's the IP. Anyone can fork Athena. Nobody can fork your 500+ sessions of calibrated history.

Publishing the framework doesn't create competitors — it creates **awareness**. Every clone is someone who sees the value of structured AI infrastructure. And anyone disciplined enough to build their own 500 sessions was going to build something regardless — your published architecture just saved them 2 months of engineering.

**Open-source the algorithm. Keep the data.** Same play as Linux (free kernel, $34B support business), Android (free OS, proprietary ecosystem), and Lao Gan Ma (public recipe, sovereign supply chain).

→ Read the full thesis: [The Compounding Effect](The-Compounding-Effect)
