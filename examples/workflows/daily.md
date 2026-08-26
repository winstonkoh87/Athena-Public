---
description: Daily curation standup — score matured predictions, log yesterday's irreversible decisions, check system lights, and ground today's live work
created: 2026-08-23
last_updated: 2026-08-23
model: default
temperature: 0.2
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /daily — Daily Curation Standup

> **Latency Profile**: ULTRA-LOW (<1.5K tokens total)  
> **Philosophy**: Residue over scaffolding. Compound curation over meta-engineering.  
> **Rule of Zero**: If lights are green and no live work is named, Athena gets **0 commits**. Do not open GTO sweeps, protocol edits, or "while we're here" refactors.

---

## Trigger & Input

- **Interactive**: User types `/daily` or `/daily <live task description>`
- **Scheduled (Unattended)**: Automated scheduler triggers with:
  ```text
  /daily
  Live work today: <one line or leave blank>
  ```

---

## Execution Protocol (Step-by-Step)

0. **Pre-load** `.agent/workflows/_shared.md` (inherits tool rules and ASCII-only math constraints).
1. **Clock & Timezone**: Check current timestamp in `Asia/Singapore` (SGT / UTC+8). Identify current day-of-week and date (`YYYY-MM-DD`).

### Phase 1: Matured Predictions Gate (CAL-001)

1. Read `.context/calibration/CALIBRATION_LEDGER.md` (or run `python3 .agent/scripts/calibration_score.py`).
2. Identify all predictions where `Outcome: pending` AND `Deadline <= today`.
3. **Scoring Rule**:
   - If empirical proof exists in workspace files/git/logs (e.g. statement CSVs, deployed commits, verifiable event): update ledger with outcome (`true` | `false` | `partial` | `void`), resolution date, and note.
   - If outcome requires external human knowledge or unrecorded facts: mark `UNSCORED (needs human: CAL-XXX)`.
   - ❌ **NEVER fabricate outcomes.** If unsure, it is `UNSCORED`.

### Phase 2: Yesterday Decision Ledger

1. Check `.context/memory_bank/activeContext.md` (recent session checkpoints) and `.context/memory_bank/decisionLog.md`.
2. Determine if an **irreversible decision** (capital deployment, signed client contract, banned asset/protocol, permanent structural pivot) occurred yesterday in SGT that is not yet in `decisionLog.md`.
3. If yes: append exactly 1 structured row to `decisionLog.md`.
4. If no irreversible event occurred: record `YESTERDAY: NOOP`. (Empty is complete. Routine tasks are not decisions.)

### Phase 3: System Lights & Freeze Gate

Execute surgical checks:

1. **`shutdown_help`**: Check basic system integrity / scripts / tests (`ok` or error summary).
2. **`vector`**: Exocortex index status (`ok` if reachable/valid, `UNKNOWN` if remote offline).
3. **`maint`**: Run `python3 .agent/scripts/maintenance_ratio.py --days 14` to get 14-day maintenance commit percentage (e.g. `92`).
4. **`deals`**: Read `beh_603.active_deals` from `.agent/state/accountability_status.json` (e.g. `0`).
5. **`FREEZE`**:
   - `FREEZE: yes` if `maint > 70%` AND `deals == 0` (TD-045 advisory: freeze internal scaffolding in favor of external/revenue output).
   - `FREEZE: no` otherwise.

### Phase 4: Sunday Eviction Check (Sundays Only)

- If today is **Sunday**: Run `python3 .agent/scripts/eviction_check.py --days 90`.
- Output the number of archive candidates and list top candidate names.
- ⚠️ **Advisory only**: Proposals only, never auto-delete or auto-move files.

### Phase 5: Live Work JIT Grounding

- If user/scheduler provided **Live work today**:
  - Run ONE surgical Exocortex search:
    ```bash
    python3 .agent/scripts/smart_search.py "<live work>" --limit 2
    ```
  - Cite the top relevant file path and output 1 crisp physical next action.
- If blank / none: output `USE: skipped — no live job`.

---

## Output Card Format

Output strictly the structured card below, followed by `STOP`. No chit-chat.

```text
DAILY YYYY-MM-DD DayOfWeek
DUE: <count of pending predictions due today, or '0' if none> [if >0: list IDs + status]
YESTERDAY: <NOOP | 1-line summary of decision logged>
LIGHTS: shutdown_help=<ok|err>  vector=<ok|UNKNOWN>  maint=<pct>  deals=<count>
FREEZE: <yes|no>
[SUNDAY_EVICTION: <count> candidates (<names...>) — if Sunday only]
USE: <skipped — no live job | cited file + next physical action>
ATHENA_COMMITS_TODAY: <count>
STOP
```

---

## Anti-Patterns

- ❌ Inventing prediction outcomes to clear the DUE list
- ❌ Committing new protocols, refactors, or tooling fixes during daily standup
- ❌ Long prose, pleasantries, or multi-paragraph status essays
- ❌ Running broad full-corpus reindexes during daily standup
- ❌ Using LaTeX math delimiters (`$`, `$$`) in any output (ASCII-only rule)
