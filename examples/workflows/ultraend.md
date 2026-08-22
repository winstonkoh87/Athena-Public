---
description: Deep close for cognitive/computationally intensive sessions. System-2 counterpart to /end.
created: 2026-03-10
last_updated: 2026-06-06
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultraend — Deep Session Close (System-2) v3.1

> **Latency Profile**: HIGH (~2-3 min)
> **Philosophy**: Extract maximum learning value. Close once, close right.
> **Token Protocol**: **MaxMax** — Maximum depth extraction. Cross-session patterns, CANONICAL reconciliation, compound insights, decision outcome tracking. Full synthesis.
> **Contrast**: For lightweight close (MinMax), use `/end`.
> **Context Constraint**: After a deep session, the 200K ECL may be 60-80% consumed.
> Synthesize efficiently because the context window is nearly full — not because tokens cost money.
> **Use When**: After `/ultrastart` sessions, 5+ decision sessions, weekly reviews, or any session with high insight density.

> [!IMPORTANT]
> This is NOT the default close. Use `/end` for general sessions.
> `/ultraend` trades speed for epistemic depth. Only invoke when the session
> generated enough signal to justify deep synthesis.

---

## Activation Gate

**Auto-suggest `/ultraend`** when ANY of these are true:

| Trigger | Why |
|:--------|:----|
| Session opened with `/ultrastart` | Symmetrical pairing — deep boot deserves deep close |
| 5+ decisions made this session | High decision density = high extraction value |
| New frameworks/axioms discovered | Must propagate to CANONICAL before context is lost |
| Session Λ total ≥ 200 | Heavy cognitive session — lots of signal to compress |
| User explicitly requests | Direct invocation |

If NONE are true → default to `/end`. Don't burn tokens on shallow sessions.

---

## Phase 0: Standard Close (Inherit from /end)

Execute **all steps from `/end` Phase 1B** first:

1. ✅ Write Session Log file
2. ✅ Append Checkpoint to `activeContext.md`
3. ✅ Canonical Check (conditional)
4. ✅ Decision Log Gate
5. ✅ Update Project Switchboard (MANDATORY)
6. ✅ Context Hygiene Gate

> [!TIP]
> Phase 0 is just `/end`. Everything that follows is ADDITIVE.
> If `/ultraend` fails mid-synthesis, you still have a clean `/end` close.

---

## Phase 1: Cross-Session Pattern Scan (~60s)

**What**: Scan the last 5 session logs for recurring themes, unresolved threads, and behavioral patterns.

### Step 1: Load Recent Session Log Files

> **Source**: Always read from `.context/memories/session_logs/` (full session log files),
> NOT from compacted one-liner entries in `activeContext.md`. The log files contain
> the full `@decided`, `@pending`, `@learned` blocks needed for pattern detection.

// turbo

```bash
ls -1t .context/memories/session_logs/ | head -5
```

Read the `@decided` and `@pending` blocks from each.

### Step 2: Pattern Detection

Ask yourself these 4 questions:

1. **Recurring Topics**: What theme appeared in 3+ of the last 5 sessions? (Signal: user obsession or unresolved problem)
2. **Orphaned Pendings**: What appeared in `@pending` 3+ sessions ago but never moved to `@decided`? (Signal: stuck or deprioritized)
3. **Decision Reversals**: Did any `@decided` item in this session contradict a previous `@decided`? (Signal: learning or drift)
4. **Velocity Trend**: Are sessions getting more productive (higher Λ/session) or less? (Signal: system health)

### Step 2.5: Decision Outcome & Calibration Ledger Tracking (GTO v3.2)

> **Calibration Review**: Connect historical decisions and forecasts to observable outcomes and the calibration ledger (`CAL-###`).
> To maintain true Brier score integrity, verify against pre-registered probabilities `(p, observable_event, resolution_date)` from `Session_Observations.md`.

For each `@decided` or forecasted item from sessions **N-1 through N-3**:

1. **State the original decision / forecast** and the registered probability / expected outcome
2. **Ask**: _"Did this decision / forecast produce the expected observable outcome?"_
3. **Classify and ledger the result**:

| Result | Action |
|:-------|:-------|
| ✅ Outcome matched expectation | Record in calibration ledger (`CAL-###`). No model update needed. |
| ⚠️ Outcome partially matched | Record delta. Perform root-cause analysis on assumptions. |
| ❌ Outcome missed entirely | Log miscalibration. Update base-rate priors in `CANONICAL.md` or domain protocols. |
| 🔄 Outcome still pending | Carry forward to next review cycle. |

4. **Track `@seeded` transition**: Check whether the seeded priority from S[N-1] transitioned into execution in session S[N].

Append to session log:

```markdown
## Decision Outcome & Calibration Tracking

| Ref ID / Session | Decision / Forecast | Registered (p / Expectation) | Actual Observable Outcome | Resolution |
|:-----------------|:--------------------|:-----------------------------|:--------------------------|:-----------|
| CAL-XXX / S[N-1] | [decision/forecast] | [p% / expected state]        | [what actually happened]  | ✅/⚠️/❌/🔄 |
| CAL-YYY / S[N-2] | [decision/forecast] | [p% / expected state]        | [what actually happened]  | ✅/⚠️/❌/🔄 |

**Seed Transition**: S[N-1] seeded "[X]" → Session N executed "[Y]" → [Followed / Pivoted / Blocked]
```

---

## Phase 2: CANONICAL Deep Reconciliation (~60s)

**What**: `/end` does a conditional check ("did this session touch CANONICAL?"). `/ultraend` does a **mandatory deep scan**.

### Step 1: Load CANONICAL.md

Read the full Strategic Frameworks table (Section 4).

### Step 2: Reconciliation Questions

For each insight from this session:

1. **Is it already in CANONICAL?** → Skip
2. **Does it contradict something in CANONICAL?** → **UPDATE CANONICAL** (truth evolved)
3. **Is it a new framework worth preserving?** → **ADD to CANONICAL**
4. **Is it session-specific noise?** → Skip (not every insight is canonical)

### Step 3: Framework Bundling Check

> **Key Question**: Do the insights from this session form a coherent, named framework?

If 3+ related insights emerged in one session, they may constitute a new **named framework** worth bundling:

- Give it a name (e.g., "Pricing Thesis", "Distribution Physics")
- Write a one-liner that captures the core principle
- Add to CANONICAL Section 4

If insights are isolated, file individually.

---

## Phase 2.5: Insight Compounding (GTO v3.1 — NEW)

> **What**: The explicit "connect the dots" step. This is where the unlimited compute
> philosophy pays its highest dividend — generating compound insights that neither
> the current nor previous sessions had alone.

### Step 1: Cross-Pollination Question

Ask yourself:

> _"What insight from THIS session, combined with an insight from a PREVIOUS session,
> creates a NEW insight that neither had alone?"_

This is not a vague prompt — work through it systematically:

1. List the top 3 insights from this session (from `@decided` + `@learned`)
2. List the top 3 insights from the most recent 3 sessions (from Step 2 above)
3. For each pair (current × previous), ask: _"Is there a connection?"_
4. If yes → name the compound insight and write a one-liner

### Step 2: File Compound Insights

For each compound insight generated:

- If it's a **named framework** (3+ connected insights) → Add to `CANONICAL.md` Section 4
- If it's a **tactical pattern** → Add to `Session_Observations.md`
- If it's a **single connection** → Log in the session log under `## Compound Insights`

Append to session log:

```markdown
## Compound Insights

- **[Compound Insight Name]**: [Session N insight] + [Session N-X insight] → [New insight]
  Filed to: [CANONICAL §4 / Session_Observations / session log only]
```

> **No compound insights?** That's fine — not every session produces them. Log:
> `## Compound Insights: None detected.` and move on. Don't force connections.

---

## Phase 3: Reflexion Archive (~30s)

**What**: Explicit post-mortem. What went well, what didn't, what to repeat/avoid.

### Step 1: Ask These 3 Questions

1. **What worked?** — What approach, tool, or decision produced outsized value this session?
2. **What didn't?** — Where did I waste time, backtrack, or produce low-value output?
3. **What's the counterfactual?** — If I could redo this session, what one thing would I change?

### Step 2: File to Session Log

Append to the session log:

```markdown
## Reflexion

- **Worked**: [approach/decision that worked well]
- **Didn't**: [waste/backtrack/mistake]
- **Counterfactual**: [what I'd change if I could redo this session]
```

### Step 3: Explicit Propagation (GTO v3.1)

> **Close the learning loop.** Reflexion learnings must route to their correct destination,
> not just sit in the session log. Same tokens, higher signal extraction.

For each reflexion finding, apply the propagation matrix:

| Finding Type | Propagation Target | Action |
|:-------------|:-------------------|:-------|
| "Worked" reveals a **reusable technique** | `CANONICAL.md` Section 4 | Check if already exists. If not → add as named framework. |
| "Didn't" reveals a **repeatable mistake** | Relevant skill's `SKILL.md` | Add/update entry under `## Anti-Patterns` section. Include the real case and fix. |
| "Counterfactual" reveals a **better workflow** | `TECH_DEBT.md` | File as candidate optimization with effort estimate (S/M/L). |
| "Worked" is **session-specific** (not reusable) | Session log only | No propagation needed. |
| "Didn't" is a **one-off mistake** (not repeatable) | Session log only | No propagation needed. |

> **Gate**: Only propagate if the finding is REUSABLE across sessions. One-off mistakes
> and session-specific wins stay in the session log.

---

## Phase 4: Strategic Portfolio Review (~30s)

**What**: Zoom out. Are we working on the right things?

### Step 1: Load PROJECTS.md

### Step 2: Ask These Questions

1. **Priority Alignment**: Is the highest-EV project getting the most sessions? If not, why?
2. **Stale Projects**: Any project that hasn't been touched in 7+ days? Should it be parked or killed?
3. **Pipeline Health**: Is the ratio of Internal:External projects healthy? (Target: ≤30% internal, ≥70% external for revenue)
4. **Next Session Suggestion**: Based on everything above, what should the NEXT session focus on?

### Step 3: Update PROJECTS.md

- Advance or regress phases based on findings
- Park stale projects
- Update `Last triaged` timestamp

### Step 4: Seed Next Session

Add to the checkpoint `@pending`:

```
@seeded: [Suggested next session focus based on portfolio review]
```

This gives `/start` or `/ultrastart` a head start on context loading.

---

## Phase 4.5: Behavioral Accountability Deep Close (Grace Harper Model)

> **Purpose**: Deep counterpart to `/end`'s lightweight BEH check. Full execution audit and trigger synthesis.

### Step 1: BEH-602 Trigger Log Synthesis

1. Load the full BEH-602 trigger log for the current week
2. Classify triggers by pattern:
   - Schema #1 (Effort = Worth): effort-without-reciprocity frustration
   - Schema #2 (Not Prioritized = Not Enough): validation-seeking, cruising impulse
   - Schema #3 (100% In = 100% Back): over-investment, boundary erosion
   - Base Rate Distortion (MP-16): inflating/deflating probability
3. Surface: `📝 BEH-602 Weekly: [N] triggers. Top pattern: [Schema #X] ([N] instances).`
4. If pattern is escalating (week-over-week increase): `🚩 Escalating: [Schema #X] triggers trending up. Consider IFS session.`

### Step 2: Weekly Execution Audit (Deep)

1. Load all `@pending` and `@decided` from the past 7 days' checkpoints
2. Build the **Committed vs Actual** table:

```markdown
## Weekly Execution Audit

| Committed (from @pending/@decided) | Executed? | Gap Diagnosis |
|:-----------------------------------|:----------|:--------------|
| [Item 1] | ✅/❌ | [If ❌: Why not? INTJ-T pattern?] |
| [Item 2] | ✅/❌ | |

**Execution Rate**: [N]/[M] = [X]%
**Gap Pattern**: [Internal accountability failure / External blocker / Scope changed]
```

3. If execution rate < 60%: `⚠️ Execution rate below 60%. DIAG-001 Knowledge-Action Gap likely active.`
4. Append to session log.

### Step 3: BEH Commitment Review

- Are current BEH- protocols still calibrated? (e.g., Is BEH-601 Saturday AM still the right target?)
- Should any new BEH- protocol be created based on session patterns?
- Log any adjustments to the session log.

> **Rationale**: The deep close is the right time for accountability synthesis because the full session context is available. See TD-041.

---

## Phase 5: Shutdown Orchestrator

// turbo

```bash
python3 .agent/scripts/shutdown.py
```

Same as `/end` — session compilation, git commit, compliance report.

---

## Output Template

After all phases complete:

```
🧠 Deep Close Complete (GTO v3.1).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 0]   Standard Close          ✅
[Phase 1]   Cross-Session Scan      ✅  [N patterns, N decision outcomes tracked]
[Phase 2]   CANONICAL Reconcile     ✅  [N updates, N new frameworks]
[Phase 2.5] Insight Compounding     ✅  [N compound insights generated]
[Phase 3]   Reflexion + Propagation ✅  [N findings propagated]
[Phase 4]   Strategic Review        ✅  [Next: "<seeded focus>"]
[Phase 5]   Shutdown                ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session closed. Time: [HH:MM SGT]
Seed Accuracy (prev session): [Match/Partial/Miss]
```

---

## Failure Recovery

| Failure | Action |
|:--------|:-------|
| Phase 0 (/end) fails | Fix Phase 0 first. Do not proceed to synthesis. |
| Phase 1-4 fails mid-synthesis | Phase 0 already ran — session is safely closed. Report which synthesis phase failed. |
| `shutdown.py` fails | Same as `/end` fallback: `git add -A && git commit -m "session close" --no-verify`. |
| 2 consecutive failures | **Circuit Breaker (P514)**. Stop. Report root cause. |

---

## Quick Reference

| Close Type | Latency | When |
|:-----------|:--------|:-----|
| `/end` (admin) | ~60s | Most sessions |
| `/ultraend` (deep) | ~2-3 min | After /ultrastart, 5+ decisions, weekly reviews |

---

## References

- [/end](end.md) — Standard close (Phase 0 source)
- [/ultrastart](ultrastart.md) — Symmetric deep boot counterpart
- [/save](save.md) — Mid-session checkpoint

---

## Tagging

`#workflow` `#automation` `#ultraend` `#system-2` `#deep-synthesis`
