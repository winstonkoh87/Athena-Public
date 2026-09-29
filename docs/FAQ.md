# Frequently Asked Questions (FAQ)

> **Last Updated**: 22 July 2026

---

## General

### What is Athena?

Athena is an **open-source framework** for building AI agents with persistent memory. Unlike ChatGPT or Claude's built-in memory, Athena stores everything in **Markdown files you own** — portable, version-controlled, and model-agnostic.

### Is this just a prompt library?

No. Athena is a **system architecture**:

- `.framework/` — Your AI's identity and operating principles
- `.context/` — Long-term memory (decisions, case studies, session logs)
- `.agent/` — Workflows, scripts, and automation

The prompts are part of it, but the real value is the **structure** that compounds over time.

### Which AI models does Athena support?

Athena separates the **IDE** from the **Reasoning Engine**, so you are never locked into a single platform or model.

**1. The IDE (Where you type):**

- **Antigravity** (Google)
- **Cursor** / **VS Code**
- **Claude Code** / **Gemini CLI**

**2. The Reasoning Engine (Who does the thinking):**

- **Gemini 3.1 Pro**
- **Claude Opus 4.6**
- **GPT-5.4**
- Any LLM that can read your local Markdown files

---

## Setup & Installation

### How long does setup take?

**5 minutes** for the basic install:

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git
cd Athena-Public
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

For full power features (vector search, semantic retrieval), budget 30-60 minutes.

### Do I need API keys?

**Minimal setup**: No API keys required. Works with local files only.

**Full setup** (recommended):

- `ANTHROPIC_API_KEY` — For Claude reasoning
- `GOOGLE_API_KEY` — For embeddings (text-embedding-004)
- `SUPABASE_URL` + `SUPABASE_ANON_KEY` — For vector database (optional)

### Does it work with Cursor? Windsurf?

Yes. Athena is IDE-agnostic. Use:

```bash
athena init --ide cursor    # Creates .cursor/rules.md
athena init --ide antigravity  # Creates AGENTS.md
```

### I already have a project — do I need to move it into Athena?

No. Three options:

| Mode | How | Best For |
|:-----|:----|:---------|
| **Standalone** | Open `Athena/` as your workspace. Navigate to your project from there. | All-in-one brain |
| **Multi-Root** | Open your project → `File → Add Folder to Workspace` → select `Athena/` | Existing repos |
| **Nested** | Drop your project folder inside `Athena/` | Quick prototypes |

All three work. Start with **Standalone** and adjust to taste.

### I work with clients — where does their data go?

Keep Athena as your **personal brain**. Create client folders **outside** the workspace (e.g., `~/Desktop/Client-A/`). When working on a client project, point Athena to that external folder. This keeps your personal context clean and prevents client data from polluting your memory bank.

When the engagement ends, archive the generalized learnings back into Athena (strip client-specific data) and archive or delete the external folder. **Athena keeps the wisdom. The client keeps the execution.**

---

## Cost & Performance

### How much does it cost to run?

| Component | Cost |
|-----------|------|
| **Basic usage** (local files only) | Free |
| **Embeddings** (Google API) | ~$0.001 per 1K tokens |
| **Claude API** (direct calls) | Depends on usage |
| **Supabase** (vector DB) | Free tier available |
| ~~**GraphRAG** (knowledge graph)~~ | ❌ Removed (S435, 6 June 2026) |

Most users spend **< $5/month** on API calls.

### What's the boot time?

| Mode | Time |
|------|------|
| Cold boot (first session) | ~1–2 minutes |
| Warm boot (cached) | < 5 seconds |

---

## Privacy & Security

### Where does my data go?

**Local Mode**: Everything stays on your machine. Zero data leaves.

**Cloud Mode**: Only embeddings (vectors) are sent to Supabase. Raw text stays local.

**Hybrid Mode** (default): Local files + cloud embeddings for search.

### Is it safe to use for work?

Yes, if you use **Local Mode**. For enterprise use, see [SECURITY.md](SECURITY.md) for RLS policies and key management.

---

## Troubleshooting

### "athena: command not found"

Ensure the SDK is installed from the cloned repo **inside a virtual environment**:

```bash
cd Athena-Public
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
pip install -e .
```

If you've already installed it, make sure your virtual environment is activated (`source .venv/bin/activate`).

### "error: externally-managed-environment" (PEP 668)

This error occurs on macOS (Homebrew Python) and Ubuntu 23.04+ when installing packages without a virtual environment. Fix:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Session logs not saving

Run `/start` at the beginning of your session. The agent needs to initialize before it can log.

### Context window errors

Athena auto-retrieves ~2K tokens of context. If you're hitting limits, your session may have drifted. Run `/save` to checkpoint and start fresh.

---

## Still stuck?

- **GitHub Issues**: [Report a bug](https://github.com/winstonkoh87/Athena-Public/issues)
- **Discussions**: [Ask a question](https://github.com/winstonkoh87/Athena-Public/discussions)

---

**[Back to README](../README.md)**
