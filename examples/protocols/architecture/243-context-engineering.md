---

created: 2025-12-29
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-29
last_updated: 2026-01-05
---

# Protocol 243: Context Engineering (Dumb Zone Avoidance)

> **Source**: Dex Horthy, HumanLayer (AI Engineer 2025)  
> **Created**: 29 December 2025  
> **Tags**: #context-engineering #coding-agents #workflow #architecture

---

## Core Principle

> *"AI cannot replace thinking. It can only amplify the thinking you have done or the lack of thinking you have done."*

---

## The Dumb Zone

Past ~40% context window fill, model quality degrades exponentially.

```
┌─────────────────────────────────────────────────┐
│  CONTEXT WINDOW (168K tokens)                   │
├─────────────────────────────────────────────────┤
│  [████████░░░░░░░░░░░░░]  SMART ZONE (0-40%)   │
│  [░░░░░░░░████████░░░░░]  DIMINISHING (40-70%) │
│  [░░░░░░░░░░░░░░░░█████]  DUMB ZONE (70-100%)  │
└─────────────────────────────────────────────────┘
```

**Rule**: If working on complex tasks, stay in the Smart Zone. Compress and restart before hitting diminishing returns.

---

## RPI Framework (Research → Plan → Implement)

| Phase | Purpose | Athena Equivalent |
|-------|---------|-------------------|
| **Research** | Understand how system works. Find files. Stay objective. | Semantic search, file exploration |
| **Plan** | Outline exact steps with code snippets. Compression of intent. | `implementation_plan.md` |
| **Implement** | Execute plan. Keep context low. | EXECUTION mode |

**Critical**: Each phase should ideally start in a fresh context window with compressed handoff.

---

## Frequent Intentional Compaction

**What takes up context window:**

1. Searching for files
2. Understanding code flow
3. Editing files
4. Test/build output
5. MCP JSON dumps

**What to compact:**

- Exact files and line numbers relevant to the problem
- Decisions made and why
- Errors encountered and resolutions

**Athena Implementation:**

- `quicksave.py` → Session-level compaction
- `CANONICAL.md` → Cross-session compaction
- Session logs → Checkpoint compaction

---

## Trajectory Pollution

> *"If you yell at the model repeatedly, the next most likely token is: do something wrong so the human can yell at me again."*

**Anti-Pattern:**

```
User: Do X
AI: [Does wrong thing]
User: No, that's wrong! Do Y!
AI: [Does wrong thing]
User: You're still wrong! Do Z!
AI: [Predicts: I should do something wrong]
```

**Pattern:**

```
User: Do X
AI: [Does wrong thing]
User: [Recognizes trajectory pollution]
→ STARTS FRESH CONTEXT with corrected prompt
```

**Trigger**: After 2 corrections in same direction, restart fresh.

---

## Don't Outsource Thinking

| Level | Risk |
|-------|------|
| Bad line of code | 1 bad line |
| Bad part of a plan | 100 bad lines |
| Bad research (misunderstanding) | Entire task hosed |

**Rule**: Human effort should focus on highest-leverage points — validating research and plans, not reviewing generated code.

---

## When to Use Full RPI

| Complexity | Approach |
|------------|----------|
| **Button color change** | Just ask |
| **Small feature** | Quick plan, implement |
| **Medium feature (multi-file)** | Research → Plan → Implement |
| **Complex (multi-repo, architecture)** | Full RPI with explicit compaction |

---

## Integration with Athena

| Dex's Term | Athena Implementation |
|------------|----------------------|
| Research | Semantic search (`smart_search.py`) |
| Plan | `implementation_plan.md` artifact |
| Implement | EXECUTION mode |
| Compaction | `quicksave.py`, session logs, CANONICAL.md |
| Mental Alignment | `notify_user` with PathsToReview |

---

## References

- [Dex Horthy — No Vibes Allowed (AI Engineer 2025)](https://youtube.com/watch?v=...)
- [12 Factor Agents](https://github.com/humanlayer/12-factor-agents)
- [HumanLayer RPI Prompts](https://github.com/humanlayer/...)

---

# protocol #context-engineering #rpi #coding-agents
