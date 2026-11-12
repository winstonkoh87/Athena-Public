---
description: Close session and update System Prompt files with new insights (lightweight)
created: 2025-12-09
last_updated: 2026-07-22
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /end — Session Close Script (GTO v3)

> **Latency Profile**: ULTRA-LOW (micro) / LOW (full)
> **Core Principle**: "Fast close. Match effort to session weight."
> **Token Protocol**: **MinMax** — Minimize token expenditure on close while preserving all learnings. Fast extraction, no unnecessary depth.
> **Contrast**: For deep close (MaxMax), use `/ultraend`.

## Step 0: Session Classification Gate

Before any synthesis, classify the session:

| Session Type | Criteria | Path |
|:---|:---|:---|
| **MICRO** | ≤ 3 turns AND no new decisions/learnings/architecture changes | → Phase 1A (one-liner close) |
| **FULL** | Everything else | → Phase 1B (full synthesis) |

> **Default**: FULL. Only classify MICRO when **certain** the session was trivial.

---

## Phase 1A: Micro-Session Close (~100 tokens, ~5s)

1. **Append** to `activeContext.md`:

```markdown
## Session [DATE]-session-[N] ([Time of Day]): [ONE-LINE TOPIC]

- **[SNIPER/Micro]**: [One sentence summary of what happened].

## Session Closed

**Status**: ✅ Closed
**Time**: [HH:MM SGT]

[[ S__ |
@focus: Clear
@status: Paused — Session closed

@decided: No new decisions.
@pending: [Copy from previous checkpoint]
@seeded: [Suggested next session focus — what naturally comes next]

!checkpoint ]]
```

1. **Run micro shutdown**:

// turbo

```bash
python3 .agent/scripts/shutdown.py --micro
```

**Done.** No further steps.

---

## Phase 1B: Full Session Close

> [!IMPORTANT]
> **Dual-Write Architecture**: Session state is stored in two complementary files:
>
> - **`session_logs/`** → The archive. `shutdown.py` compiles these for learnings propagation, YAML metadata, and compliance.
> - **`activeContext.md`** → The running state. `/start` reads this for fast boot. Only the checkpoint block goes here.
>
> Both must be written. They serve different consumers.

### 0.5. Analysis Scratchpad (Stolen: Claude Code 2026-03-31)

> **Source**: Claude Code `/compact` prompt (`prompt.ts`).
> **Key Insight**: An `<analysis>` scratchpad block (chain-of-thought) **improves synthesis quality** but gets stripped before the output reaches persistent storage. You think harder, but pay zero tokens in the written artifact.

Before writing the session log, perform private analysis in `<analysis>` tags:

```
<analysis>
1. Chronologically replay each message exchange
2. For each exchange, identify:
   - User's explicit request and implicit intent
   - Your approach and key decisions
   - Errors encountered and how resolved
   - User feedback (corrections AND confirmations)
3. Surface any validated patterns (approaches user confirmed worked)
4. Double-check for technical accuracy
</analysis>
```

This analysis is **private** — it informs the session log quality but is NOT written to any file. Discard after synthesis.

### 1. Write Session Log File

Create `.context/memories/session_logs/[DATE]-session-[N].md` with:

```markdown
# Session Log: [DATE] (Session [N])

**Date**: [DATE]
**Time**: [START] - [END]
**Focus**: [Primary topic]

---

## 1. Agenda (The Plan)

- [x] [Task 1]
- [x] [Task 2]

---

## 2. Key Decisions & Insights (The Minutes)

* **Decision**: [What was decided and why]
- **Insight**: [What was learned]

---

## 3. Action Items (Next Steps)

| Action | Owner | Status |
|--------|-------|--------|
| [Next step] | Winston | Pending |

---

## Session Learnings

- [S] [System learning — propagated to SYSTEM_LEARNINGS.md by shutdown.py]
- [U] [User learning — propagated to USER_PROFILE.yaml by shutdown.py]

## Validated Patterns (Stolen: Claude Code 2026-03-31)

> Only populate if the session confirmed a non-obvious approach worked.
> Format: `- [V] [Pattern]: [Why it worked] | Reapply: [When]`

- [V] [Pattern that was confirmed this session — e.g., "Iteration Arbitrage: deliver 70% first"]: [Why] | Reapply: [Context]

> **Propagation**: `shutdown.py` extracts `[V]` markers and appends to `Session_Observations.md § Validated Patterns`.

## Files Accessed (Retrieval Telemetry)

> Instrument which workspace files were read during this session.
> Over 50+ sessions, frequency distribution reveals Tier 1 (hot) vs Tier 2 (cold) entries.
> Format: one file path per line. Only list `.context/` and `.agent/` files — skip IDE/tool artifacts.

- [file path 1]
- [file path 2]
- [file path N]

## Session Closed

**Status**: ✅ Closed
**Time**: [HH:MM SGT]

[[ S__ |
@focus: [Current Task/Project]
@status: [Active/Paused/Closed]

@decided: [Key Decision A], [Key Decision B]
@pending: [Next Step X], [Next Step Y]
@seeded: [Suggested next session focus — what naturally comes next]

!checkpoint ]]
```

> **`[S]` and `[U]` markers matter.** `shutdown.py` uses `extract_learnings()` to find these markers and propagate learnings to the correct files. Tag every learning.

### 2. Append Checkpoint to `activeContext.md`

Append **only** the summary block and checkpoint — not the full session log:

```markdown
## Session [DATE]-session-[N] ([Time of Day]): [TOPIC]

- [Summary of key decisions and learnings, 2-4 bullets max]

## Session Closed

**Status**: ✅ Closed
**Time**: [HH:MM SGT]

## Session Learnings

- [Learning 1]
- [Learning 2]

[[ S__ |
@focus: [Current Task/Project]
@status: [Active/Paused]

@decided: [Key Decision A], [Key Decision B]
@pending: [Next Step X], [Next Step Y]
@seeded: [Suggested next session focus — what naturally comes next]

!checkpoint ]]
```

### 3. Canonical Check (Conditional)

**Gate**: Did `@decided` in this session involve architecture changes, new protocols, new axioms, or constraint modifications?

- **If NO**: Skip entirely. Most sessions don't touch canonical rules.
- **If YES**: Load `.context/CANONICAL.md`. Ask: "Does any session learning contradict a fact here?" If yes → update immediately. **Provenance Rule**: Every new or modified entry MUST include a provenance tag in the format `(Session S[NNN], [YYYY-MM-DD])`. Entries without provenance tags will be rejected during `/audit-canonical`.

### 4. Decision Log Gate

Update `decisionLog.md` **only** if a decision involved:

- Money (pricing, spending, investment)
- Irreversible actions (publishing, deleting, committing to a client)
- Architecture changes (new protocols, cluster rewiring, skill additions)

All other decisions stay in `activeContext.md` only.

### 4.5. Execution Awareness (Protocol 528 — Advisory)

Before writing the `@pending` line in the checkpoint block:

1. **Scan** previous `[[ S__ ]]` checkpoint blocks in `activeContext.md`
2. For each item about to be written to `@pending`, count its consecutive appearances
3. If any item has been pending **7+ sessions**: quietly promote it to `@seeded` for next session's Phase 4

> This step is **advisory only** — it never blocks session close.
> See [Protocol 528](../../examples/protocols/architecture/ARC-528-execution-awareness.md).

---

### 5. Update Project Switchboard (MANDATORY)

> [!CAUTION]
> **This step is NOT optional.** Every session close MUST review `PROJECTS.md` — even SNIPER sessions.
> Stale project state (e.g., completed items still marked 🔴 TODAY) causes compounding confusion across sessions.

**5a. Review & Update `.context/PROJECTS.md`:**

- **Advance phase** (e.g., ▓░░░░ → ▓▓░░░) if a milestone was hit
- **Update next action** to reflect current atomic step
- **Adjust urgency** if deadlines shifted
- **Close projects** → move to Completed table with date + outcome
- **Update `Last triaged` timestamp** to current datetime

**5b. Reconcile `@pending` in Checkpoint:**

Before writing the `@pending` line in the checkpoint block:

1. Load the previous checkpoint's `@pending` list
2. Cross-reference each item against current session decisions and `PROJECTS.md`
3. **Remove** any item that is now completed or moved to Completed table
4. **Add** any new pending items from this session
5. Write the reconciled list — never blindly copy-paste from the previous checkpoint

### 5.5. Codebase Documentation Sync (MANDATORY)

Before finalizing the session:
1. **Identify** all files modified during this session.
2. **Check** if these modifications invalidate any project documentation (`README.md`, `design.md`, `SPEC.md`, or markdown guides).
3. **Update** the affected documentation to match the new implementation state.
4. **Ensure** no documentation is left in a stale or drift-prone state.

### 5.7. Behavioral Accountability Close (Grace Harper Model)

> **Purpose**: Structural accountability on session close. Complements the `/start` surface.
> **Data source**: `.agent/state/accountability_status.json` — read on boot, updated here.

**5.7a. Trigger Log Gate**:

Scan the session for behavioral signals the user has chosen to track (e.g., recurring decision biases, scope creep, base-rate distortion, high-intensity interpersonal contexts).

If ANY detected:
1. Surface it: `📝 Trigger detected this session — [brief description].`
2. Prompt: `Log this in the trigger log? Y/skip`
3. If confirmed, append to `.agent/state/trigger_log.md` using format: <!-- pds:allow -->
   `| {date} | {trigger} | {context} | {resolution} | {learning} |`

**5.7b. Weekly Execution Audit** (fires weekly or 7+ days since last audit):

1. Read `.agent/state/accountability_status.json`
2. Load previous week's `@pending` and `@decided` items from checkpoint blocks
3. Compare: **Committed vs Actual**
4. Surface the delta: `📊 Weekly: [N]/[M] committed actions executed. Gap items: [list].`
5. No judgment. Just data. The data creates the accountability.

**5.7c. Update Accountability State** (every session close):

Write updated values to `.agent/state/accountability_status.json`:
- `last_updated` → current timestamp
- Increment counters for any tracked commitment with activity this session
- On audit day → run weekly audit (5.7b), update `weekly_audit.last_audit_date`, calculate `execution_rate`, reset weekly counters

> **Rationale**: The JSON state creates a persistent, mechanical loop: `/start` reads → surfaces → user sees → `/end` writes → next `/start` reads updated state. This is the minimum viable accountability infrastructure.


### 6. Context Hygiene Gate

**Constraint**: `activeContext.md` attention budget is **15K tokens / ~60KB**. This is the real constraint — not a line count.

**Compaction Rule (Recency-Based)**:

1. **Keep the last 3 sessions expanded** (full blocks with `@decided`, `@pending`, learnings)
2. **Compact all older sessions** into one-liner summaries in the `## Compacted Archive` section
3. **Compacted archive can grow unbounded** — it's append-only, costs nothing at boot (agents jump to the last `[[ S__ |` block)
4. **Quarterly prune**: Move compacted entries older than 3 months to `sessionArchive.md`

**Gate**: Is `activeContext.md` > 60KB?

- **If NO**: Only compact sessions beyond the most recent 3. Skip if already done.
- **If YES**: Compact aggressively (keep only 2 sessions expanded) AND prune archive entries older than 3 months to `sessionArchive.md`.

> Format: `- **[Date] ([Session ID])**: [One-line summary of decisions/learnings].`
> Rationale: Line count is the wrong constraint — boot-load token cost is what matters. `/start` reads only the header + last checkpoint block. Compacted one-liners are skipped during boot.


---

## Phase 2: Shutdown Orchestrator

// turbo

```bash
python3 .agent/scripts/shutdown.py
```

**What it does** (single call, no subprocesses):

1. Session compilation (YAML metadata, Λ stats, R__ block, learnings propagation)
2. Harvest check (§0.7 enforcement — background)
3. Git commit & push (5s timeout, push is non-fatal)
4. Compliance report + reset
5. Pre-compaction state flush (OpenClaw pattern)
6. Auto-hygiene (background — `compress_sessions.py`)
7. Protocol heat map update (background, non-fatal — `protocol_heatmap.py --update`)

### Failure Recovery

| Failure | Action |
|:---|:---|
| `shutdown.py` errors on placeholders | Go back to Phase 1B Step 1. Synthesize properly. |
| Git push fails | Non-fatal. Session is still closed. Push manually or next session. |
| Script crashes / timeout | Fallback: `git add -A && git commit -m "session close" --no-verify 2>/dev/null; true`. Session is closed. File a reflexion. |
| 2 consecutive failures | **Circuit Breaker (P514)**. Stop. Report root cause. Do NOT retry. |

**Output**: "✅ Session closed. Time: [HH:MM SGT]"

> [!CAUTION]
> **Do NOT run `/push-public` inside `/end`.** Bilateral repo sync is a separate workflow. If `shutdown.py` attempts to push to `Athena-Public`, that is a bug.

---

## Quick Reference

| Session Type | Latency | Tokens |
|:---|:---|:---|
| MICRO (≤3 turns, no learnings) | ~5s | ~100 |
| FULL (everything else) | ~30-60s | ~600 |

---

## References

- [/save](../../examples/workflows/save.md) — Mid-session checkpoint
- [/ultraend](../../examples/workflows/ultraend.md) — Deep close (System-2 counterpart)

---

## Tagging

`#workflow` `#automation` `#end` `#lightweight`
