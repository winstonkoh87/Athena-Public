# Memory Bank Pattern

> **Purpose**: Give your AI agent persistent, structured memory across sessions.
> **Status**: Production (Used in 1,900+ sessions)

## Overview

The Memory Bank is a set of markdown files that serve as your agent's long-term memory. Unlike vector databases (which store embeddings), the Memory Bank stores **human-readable state** that gets loaded on every `/start` and updated on every `/end`.

Think of it as the difference between:

- **Vector DB**: "Where did I see something about X?" (search)
- **Memory Bank**: "What am I working on right now?" (state)

You need both. The Memory Bank handles state; the vector DB handles recall.

## The 4 Pillars

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `activeContext.md` | Current focus, active tasks, recent decisions | Every session |
| `userContext.md` | User profile, preferences, constraints | When user preferences change |
| `productContext.md` | Product philosophy, goals, positioning | When strategy changes |
| `systemPatterns.md` | Architecture decisions, patterns, tech debt | When architecture evolves |

## Extending Across Domains: Report-Up Digests

The Memory Bank above is single-workspace. But a life or business runs across **several** repos — finance, health, a travel/ops folder, a project journal — each its own source of truth. Loading every one into context by hand doesn't scale, and their state goes stale the moment you stop looking.

The **report-up digest** pattern bridges them. A small generator reads each external domain repo's state files and writes a compact, **freshness-stamped** digest into the hub's indexed memory (`.context/domains/<name>/`). The vector layer embeds those digests, so a cross-cutting question — *"can I afford this?"* — retrieves current finance state without ever loading that folder by hand.

Two failure modes it closes:

- **Staleness** — every digest stamps its source files' modification dates, so a retrieved answer shows its own age.
- **Evaporation** — state lands in the hub by *running the generator* (wire it into session close), not by remembering to.

It scales to the ~5–7 canonical life areas (Work, Health, Finance, Relationships, Growth) — one registry entry per domain. Reference implementation: `scripts/sync_domain_digest.py`.

## Setup

Create a `memory_bank/` directory in your `.context/` folder:

```bash
mkdir -p .context/memory_bank
```

Then create the 4 files from the templates below.

## Templates

### `activeContext.md`

```markdown
# Active Context

## Current Focus

**Primary**: [What you're working on right now]

## Session Mandates

- [Any rules or behaviors the AI should enforce this session]

## Active Tasks

- [ ] [Task 1]
- [ ] [Task 2]
- [x] [Completed task]

## System Status

- **Health**: [OK / Degraded / Error]
- **Architecture**: [Current stack description]

## Recent Context

- **Session YYYY-MM-DD**: [Key insight or decision]

## Next Steps

1. [Next priority]
2. [Second priority]
```

### `userContext.md`

```markdown
# User Context (Core Profile)

> **Identity**: [Who you are — role, expertise, style]
> **Mission**: [What you're building toward]

## Core Identity

* **Role**: [Your relationship with the AI]
* **Key Strength**: [What you do best]
* **Key Weakness**: [What to watch for]
* **Technical Level**: [Beginner / Intermediate / Advanced / Autonomic]

## Preferences & Constraints

* [Preference 1: e.g., "Prefer direct communication over diplomatic hedging"]
* [Constraint 1: e.g., "Never spend more than $X on API calls"]

## Recent Insights

* [Insight from a recent session worth remembering]
```

### `productContext.md`

```markdown
# Product Context

## Soul Purpose

[One sentence: what are you building and why?]

## Core Philosophy

1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

## Key Goals

- [Goal 1]
- [Goal 2]

## Product Positioning

- **External Metaphor**: [How you describe it to others]
- **Internal Reality**: [What it actually is]
```

### `systemPatterns.md`

```markdown
# System Patterns

## Architecture Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| [e.g., "Use Supabase for vectors"] | [e.g., "Free tier, pgvector, RPC functions"] | YYYY-MM-DD |

## Known Patterns

- [Pattern 1: e.g., "Boot sequence loads context in <2K tokens"]
- [Pattern 2: e.g., "Session logs are append-only, never edited"]

## Technical Debt

- [ ] [Debt item 1]
- [ ] [Debt item 2]
```

## How It Works

1. **On `/start`**: The boot script loads all 4 Memory Bank files into context.
2. **During session**: The AI references Memory Bank state for continuity.
3. **On `/end`**: The shutdown script updates `activeContext.md` with session outcomes.

This creates a **compound learning loop** — each session starts smarter than the last.

## Integration with Vector Search

The Memory Bank is **not** a replacement for semantic search. Use both:

| Need | Use |
|------|-----|
| "What am I working on?" | Memory Bank (`activeContext.md`) |
| "What did I say about X 3 weeks ago?" | Vector search (`smart_search.py`) |
| "What's my risk tolerance?" | Memory Bank (`userContext.md`) |
| "Find sessions about authentication" | Vector search |

## Token Efficiency

The Memory Bank is designed for **O(1) boot cost** — loading the same ~10K tokens whether it's Session 1 or Session 10,000.

### The 15K Hard Cap

Boot tokens are budgeted with a strict ceiling:

| Slot | Budget | Growth Rate |
|------|--------|-------------|
| `userContext.md` | ~3K | Near-zero (identity is stable) |
| `productContext.md` | ~2K | Near-zero (mission is stable) |
| `activeContext.md` | ~5K | Rolling (compacts automatically) |
| Boot script output | ~2K | Fixed |
| System instructions | ~3K | Fixed |
| **Total** | **~15K max** | |

When the total exceeds 15K tokens, `activeContext.md` auto-compacts — merging older session summaries into shorter entries until the budget is back under 10K.

### Why This Matters

Assuming 200K effective context length (the industry standard for SOTA models in 2026):

| Mode | Boot Cost | Workspace Left |
|------|-----------|---------------|
| `/start` (default) | ~10K | **190K** (95% free) |
| `/think` | ~15K | **185K** |
| `/ultrathink` | ~40K | **160K** |

Most "memory" solutions dump growing chat history into context. Athena keeps boot cost flat through **progressive distillation**:

```
Live conversation (100% fidelity)
  → Session log (~15% — key insights only)
    → activeContext.md entry (~5% — compressed summary)
      → Eventually compacted out (~0.1% — absorbed into userContext.md)
```

### The Operating Band

```
0K ██████████░░░░░ 15K
   ↑ ~10K target    ↑ hard cap (auto-compact triggers here)
```

The system oscillates between ~10K and ~15K naturally as sessions accumulate and then get compacted. The user never needs to manage this — it's automatic.

## Further Reading

- [Architecture](ARCHITECTURE.md) — How Memory Bank fits into the full system
- [Getting Started](GETTING_STARTED.md) — Setup guide
- [Semantic Search](SEMANTIC_SEARCH.md) — Vector search companion
