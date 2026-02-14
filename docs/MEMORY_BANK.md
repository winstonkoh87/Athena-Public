# Memory Bank Pattern

> **Purpose**: Give your AI agent persistent, structured memory across sessions.
> **Status**: Production (Used in 1,079+ sessions)

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

## Further Reading

- [Architecture](ARCHITECTURE.md) — How Memory Bank fits into the full system
- [Getting Started](GETTING_STARTED.md) — Setup guide
- [Semantic Search](SEMANTIC_SEARCH.md) — Vector search companion
