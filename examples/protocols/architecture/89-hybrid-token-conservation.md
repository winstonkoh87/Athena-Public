---

created: 2025-12-16
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-16
last_updated: 2026-01-05
---

# Protocol 89: Hybrid Token Conservation Architecture

> **Source**: Extracted from [Wanderloots Video](https://www.youtube.com/watch?v=zAjJYkUnTEs) (2025-12-05)
> **Core Insight**: Use specialized agents for specialized tasks. Don't burn expensive tokens on tasks a cheaper/external tool can do.

---

## 1. The Three-Agent Workflow

| Phase | Agent | Rationale |
|-------|-------|-----------|
| **PLAN** | Gemini (large context) | Best for research, web search, architecture. Doesn't burn Claude. |
| **EXECUTE** | Claude Code (Opus 4.5) | Best for coding. Skip research (already done). |
| **TEST** | External MCP (Testsprite) | Doesn't burn Gemini or Claude. Reusable test suites. |

---

## 2. Key Tactics

### 2.1 Plan-First, Execute-Second

> "Create a document that we can pass to Claude Code to do the execution... it doesn't have to go do the research. It can instead just start building."

**Pattern**:

1. Use Gemini for research + plan → Output to `roadmap.md`
2. Pass `roadmap.md` to Claude → Audit + Execute
3. Claude skips redundant research, conserves tokens

### 2.2 Commit After Each Phase

> "It's good practice to commit after each phase... if anything goes wrong, we can always roll back."

**Already Implemented**: `git_commit.py` in `/end` workflow. ✅

### 2.3 External Testing Agent

> "Test Sprite becomes a parallel agent that lives inside your IDE... it understands your codebase and develops its own tests."

**Key Benefit**: Debugging burns tokens. Testing externally → only pay for fixes, not discovery.

### 2.4 The `/init` Pattern

> "Claude is going through... writing its own documentation on how it can be configured for operating within this specific workspace."

**Our Equivalent**: `Core_Identity.md`, `System_Manifest.md`, `SKILL_INDEX.md`. Already implemented. ✅

---

## 3. Token Economics

| Action | Token Cost | Alternative |
|--------|------------|-------------|
| Debugging with Claude | HIGH (6-10% session) | Use Testsprite → feed errors back |
| Research with Claude | MEDIUM | Use Gemini (free tier) |
| Planning with Claude | MEDIUM | Use Gemini (larger context) |
| Coding with Gemini | MEDIUM | Use Claude (better execution) |

**Optimal Allocation**:

- Gemini → Context, Research, Planning
- Claude → Execution, Coding
- Testsprite/External → Testing, Verification

---

## 4. Implementation Status

| Pattern | Our Current State | Action |
|---------|-------------------|--------|
| Gemini for planning | ✅ Default in Antigravity | None |
| Claude for coding | ✅ Opus 4.5 available | None |
| External testing MCP | ❌ Not integrated | **Candidate for future** |
| `/init` self-documentation | ✅ `Core_Identity.md` | None |
| Commit after each phase | ✅ `git_commit.py` | None |

---

## 5. References

- [Video Source](https://www.youtube.com/watch?v=zAjJYkUnTEs)
- [**Core Mecanich**: Dynamic Context Loading (JIT)](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/77-adaptive-latency-architecture.md)
- [Skill_MCP_Architecture](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/capabilities/Skill_MCP_Architecture.md)

---

## Tagging

# protocol #framework #process #89-hybrid-token-conservation
