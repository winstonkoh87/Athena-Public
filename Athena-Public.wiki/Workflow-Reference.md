# ⚡ Workflow Reference

Athena uses a "Slash Command" interface to trigger complex agentic behaviors. These commands are defined in `.agent/workflows/`. There are **73 workflows** (55 root + 18 domain) available.

*Last Updated: 2026-08-26 · v9.9.8*

---

## 🖥️ CLI Commands

```bash
athena                        # Boot session
athena init .                 # Initialize workspace in current directory
athena init --ide claude      # Init with Claude Code agents + CLAUDE.md
athena init --ide cursor      # Init with Cursor-specific config
athena init --ide antigravity # Init with Antigravity config
athena check                  # Basic health check
athena doctor                 # Full 15-check system diagnostics
athena doctor --fix           # Auto-repair fixable issues
athena doctor --json          # Machine-readable output
athena save "summary"         # Quicksave checkpoint
athena --end                  # Close session and save
athena --version              # Show version (v9.9.8)
```

---

## 🟢 `/start` (The Boot Sequence)

> **Purpose**: Initialize a new work session.

**What it does:**

1. **Loads Core Identity**: Reads your constitution, laws, and identity (~2K tokens).
2. **Loads Context**: Reads user profile, product context, and active context.
3. **Priming**: Runs `boot.py` — recalls last session, creates new session log, primes semantic memory.
4. **Ready**: Confirms boot and hands control to you.

**Usage:** Type `/start` at the beginning of any new chat thread.

---

## 🔴 `/end` (The Commit Sequence)

> **Purpose**: Save progress and close the session.

**What it does:**

1. **Summarize**: Generates a bulleted list of what was accomplished.
2. **Extract**: Identifies new decisions, protocols, or technical debt.
3. **File**: Writes a session log to `.context/memories/session_logs/`.
4. **Sync**: Pushes new memories to the Vector DB (if configured).
5. **Commit**: Optionally commits and pushes to GitHub.

**Usage:** Type `/end` when you are done. *Never close a session without ending.*

---

## 🧠 `/think` (Deep Reasoning)

> **Purpose**: Force a high-latency, high-quality response.

**What it does:**

1. **Escalation**: Switches to deep reasoning mode.
2. **Constraint Check**: Validates against Core Identity laws.
3. **Parallel Reasoning**: Explores 3 concurrent solution paths (Graph of Thoughts).
4. **Synthesis**: Converges on the most robust answer.

**Usage:** Use for architectural decisions, risk analysis, or complex reasoning tasks.

---

## 🔬 `/research` (Deep Research Loop)

> **Purpose**: Structured multi-source research with citation tracking.

**What it does:**

1. **Decompose**: Breaks the research question into sub-queries.
2. **Search**: Runs queries across local memory, web, and knowledge graph.
3. **Cross-validate**: Compares findings across sources.
4. **Synthesize**: Produces cited output with confidence levels.

---

## 🧹 `/refactor` (System Maintenance)

> **Purpose**: Clean up the workspace and sync state.

**What it does:**

1. **Audit**: Checks for orphaned files and broken links.
2. **Sync**: Ensures cloud and local files are consistent.
3. **Format**: Standardizes Markdown formatting.

**Usage:** Run weekly or after a heavy coding sprint.

---

## Core Workflows

| Command | Purpose |
|:--------|:--------|
| `/start` | Boot session, load identity and context |
| `/ultrastart` | **Deep boot** — 20K-token System-2 cognitive priming for high-stakes work |
| `/end` | Save session, sync memory, commit |
| `/ultraend` | **Deep close** — cross-session synthesis, CANONICAL reconciliation, reflexion archive. Counterpart to `/ultrastart` |
| `/think` | Deep reasoning mode |
| `/ultrathink` | Maximum depth + full context stack |
| `/research` | Structured multi-source research |
| `/refactor` | Workspace cleanup and audit |
| `/brief interview` | Initial user profiling session |
| `/save` | Quick checkpoint during session |

> See [WORKFLOWS.md](../docs/WORKFLOWS.md) in the repo for the full list of all 73 commands.

---

## 🛡️ Protocol Usage

Protocols are reusable decision frameworks — "Standard Operating Procedures" for the AI. There are **448 protocols (414 active)** across 26 categories.

| Category | Examples |
|:---------|:---------|
| **Decision** | Graph of Thoughts, Skeptic Gate, Base Rate Audit |
| **Safety** | Risk of Ruin (Law #1), Constraints Master |
| **Research** | Cyborg Methodology, Deep Research Loop |
| **Strategy** | Min-Max Optimization, Red Team v4 |
| **Meta** | Ultimate Auditor, Silent Validator |

> See [`examples/protocols/`](https://github.com/winstonkoh87/Athena-Public/tree/main/examples/protocols) in the repo for the full registry.
