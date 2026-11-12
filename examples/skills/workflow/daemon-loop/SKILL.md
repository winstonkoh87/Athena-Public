---
name: daemon-loop
description: Autonomous recurring agent tasks — converts workflows into persistent background daemons that run on intervals. Stolen from Boris Cherny's Claude Code `/loop` pattern (2026-03-31).
vibe: "Infrastructure that works while you sleep."
context_trigger: "loop, daemon, background, autonomous, recurring, schedule, cron"
auto-invoke: false
model: default
---

# Daemon Loop — Autonomous Agent Infrastructure

> **Source:** Boris Cherny (Claude Code creator), X thread 2026-03-30 (CS-560)
> **Pattern:** "Turn workflows into skills, then loop them."

## Core Concept

Traditional Athena workflows are **pull-based** — user triggers `/start`, `/audit`, `/reindex` manually.
Daemon loops are **push-based** — they run autonomously at set intervals without user invocation.

This is the difference between a **tool** and **infrastructure**.

## When to Use

| Use Case | Interval | Workflow |
|----------|----------|----------|
| Memory consolidation (dream pass) | 24h (3-gate) | `/dream` |
| Memory sync to Supabase | 60m | `/reindex` |
| Workspace hygiene + dead file pruning | 24h | `/needful` |
| PR/commit review (if git-active) | 5m | `/check` |
| Stale context detection (`.context/` drift) | 12h | `/audit` (lightweight) |
| Client delivery queue check | 30m | Custom scan |

## Architecture

### Option A: Cron + Headless Agent (Current-Compatible)

For environments where the agent platform supports CLI invocation:

```bash
# Example: reindex every hour
0 * * * * cd ./project && claude --bare -p "/reindex" 2>&1 >> .agent/temp/daemon.log

# Example: workspace hygiene daily at 4am
0 4 * * * cd ./project && claude --bare -p "/needful" 2>&1 >> .agent/temp/daemon.log
```

**Key:** `--bare` flag skips full context loading for speed. Only load what the specific daemon needs.

### Option B: In-Session Loop (Manual Trigger)

When cron is unavailable, run a daemon within an active session:

```text
User: "Loop /reindex every 60 minutes for the next 8 hours"
Agent: [Executes /reindex, sleeps 60m, repeats 8x]
```

**Constraint:** Requires an active session. Prefer Option A for true autonomy.

### Option C: Async-Dev Integration

Combine with `/async-dev` (Sleeper Agent Protocol):

1. User sets up daemon tasks before sleeping
2. Agent executes loop overnight
3. Morning: user reads `STATUS.md` for results

## Daemon Registration

Track active daemons in `.agent/temp/daemons.json`:

```json
{
  "daemons": [
    {
      "name": "memory-sync",
      "workflow": "/reindex",
      "interval": "60m",
      "last_run": "2026-03-31T01:00:00+08:00",
      "status": "active",
      "bare": true
    }
  ]
}
```

## Safety Rules

- **CAN**: Run read-only or idempotent workflows (reindex, audit, check, dream)
- **CAN**: Write to `.agent/temp/` and `.context/` directories
- **CANNOT**: Commit, push, or mutate source code without explicit user pre-authorization
- **CANNOT**: Run workflows that require interactive user input
- **CANNOT**: Exceed 8-hour autonomous window without checkpoint
- **BLOCKING BUDGET**: Any single daemon action that would block for >15 seconds must be deferred (stolen from KAIROS)

## Boris Cherny's Live Examples (Reference)

| His Daemon | Interval | What It Does |
|------------|----------|--------------|
| `/babysit` | 5m | Code review, rebase, shepherd PRs to production |
| `/slack-feedback` | 30m | Create PRs from Slack feedback automatically |
| `/post-merge-sweeper` | on-event | Catch missed code review comments post-merge |
| `/pr-pruner` | 1h | Close stale PRs |

## Migration Path

1. **Phase 1 (Now):** Define which workflows are daemon-eligible
2. **Phase 2:** Write cron entries or use platform-native scheduling
3. **Phase 3:** Build `.agent/temp/daemons.json` registry for state tracking
4. **Phase 4:** Add `/daemon` workflow for CRUD operations on active daemons

## References

- [/async-dev](../../../workflows/async-dev.md) — Sleeper Agent Protocol
- [/needful](../../../workflows/needful.md) — Autonomous best-judgment action
- [/reindex](../../../workflows/_domain/reindex.md) — Supabase memory sync
