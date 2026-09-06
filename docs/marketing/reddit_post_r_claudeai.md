# Reddit Post Draft — r/ClaudeAI

**Subreddit**: r/ClaudeAI  
**Flair**: `Claude Code Workflow` (or `Claude Workflow` / `Built with Claude`)  

---

## Title Options (Pick One)

1. **The architecture behind 1,900+ sessions in Claude Code: keeping state, memory, and verification outside the model (Open Source v9.9.9)**
2. **Stop overengineering agent harnesses from scratch. How Project Athena manages memory, sub-agents, and verification in Claude Code**

---

## Post Body

I’ve been following the harness discussions here lately—especially the recent post about spending 883 commits trying to build an agent harness from scratch before burning out on overengineering, alongside threads about sub-agents wreaking havoc on codebases and Claude Code token burn.

The intuition behind those experiments is 100% correct: **The LLM should be a replaceable worker, not the system that owns planning, durable state, and verification.**

If you leave context, memory, and quality assurance inside the model's transient context window:
- You pay a massive prompt cache penalty every time you pause or switch branches.
- Sub-agents run wild and hallucinate completed tasks because there's no independent verification layer checking their work.
- Every new session starts from amnesia, forcing you to re-teach Claude your architecture rules.

Two years ago, I started building **Project Athena**—a local-first memory, reasoning, and governance operating system designed to run on top of Claude Code, Cursor, and modern agent environments.

Today, it has run through **1,900+ real-world production sessions**, 400+ decision and engineering protocols, and I just open-sourced **v9.9.9** under MIT.

Here is the exact architecture that keeps Claude grounded across hundreds of commits without becoming an unmaintainable mess.

---

### 1. The Core Split: Keep State Outside the Model

Platforms want you to store memory in their cloud. Instead, Athena keeps all state as plain, git-versioned Markdown on your own drive:

```
[ Your Local Machine: Plain Git-Versioned Markdown ]
      ├── .context/CANONICAL.md    <-- Immutable tech stack rules, API contracts
      ├── .context/memory_bank/    <-- activeContext.md & session checkpoints
      ├── .agent/workflows/        <-- Deterministic slash commands (/start, /end, /plan)
      ├── .agent/skills/           <-- Isolated domain capabilities (loaded JIT)
      └── .agent/scripts/          <-- Verification scripts & red-green test runners
                  │
          [ Local MCP Server Bridge ]
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   [ Claude Code ]     [ Claude Desktop / Antigravity / Any LLM ]
```

- **Surgical MinMax Boot (<2K tokens)**: Instead of dumping hundreds of lines of chat history into Claude's prompt (which burns tokens and dilutes needle retrieval), `/start` loads only the active checkpoint block from `activeContext.md`. 90%+ of your context window stays open for actual code.
- **Session Lifecycle (`/start` and `/end`)**: `/start` mounts the exact active task list and open PR status. At the end of a work block, `/end` audits your git diff, extracts learnings, prunes dead context, and commits the state. Session 1,900 is faster and cleaner than Session 10.
- **Model Agnostic**: Claude 3.7 Sonnet / Opus is the engine on shift today. If you switch to another frontier model tomorrow, your project history, architecture rules, and test logs stay mounted.

---

### 2. Guardrails Against Rogue Sub-Agents

The biggest failure mode in agentic coding is trusting the model when it says *"I've refactored the module and verified the changes."*

Athena enforces mechanical verification before the model is allowed to mark a task complete:
- **Red Run or It Didn't Happen**: Any agent claiming to fix a test, gate, or bug must show the test failing on the pre-fix state, then passing on the fixed state. If it can't make it fail, it found a blind spot, not a fix.
- **Context Isolation**: Sub-agents work in scoped, isolated directories or parallel git worktrees rather than touching root configuration files or modifying files owned by peer tasks.
- **Adversarial Gate**: Built-in review protocols (like `red-team-review`) force an adversarial QA pass before code is staged.

---

### 3. Native Claude Code & MCP Integration

Athena includes a standalone MCP server (`mcp-athena-server`) that gives Claude native tools:
- `smart_search`: Local hybrid RAG (BM25 keyword + semantic vector search) across 1,900+ sessions of project memory.
- `quicksave`: Instant atomic saving of verified architectural facts.
- `context_gate`: Deterministic check ensuring Claude checks local documentation and dependencies before editing shared modules.

---

### Try It (100% Free & Open Source)

Zero external SaaS dependencies, no hosted vector databases, no subscriptions. Everything runs locally with Python and SQLite.

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git
cd Athena-Public
pip install -e .
athena init .
```

- **GitHub Repo**: https://github.com/winstonkoh87/Athena-Public
- **License**: MIT
- **Works with**: Claude Code, Claude Desktop (MCP), Cursor, Google Antigravity, and terminal CLI workflows.

Curious how other Claude Code users here are managing long-running project context and multi-agent verification—are you relying mostly on CLAUDE.md files, custom hooks, or local scripts? Happy to discuss the architecture or trade-offs in the comments!
