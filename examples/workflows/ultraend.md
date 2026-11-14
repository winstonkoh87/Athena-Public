---
description: Deep close for cognitive/computationally intensive sessions (System-2) v3.2
created: 2026-03-10
last_updated: 2026-11-14
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultraend — Deep Session Close (MaxMax v3.2)

> **Latency Profile**: HIGH (~2-3 min) | **Default Contrasts**: Light close uses `/end` (MinMax).
> **Protocol**: **High-Assurance Extraction** — cross-session synthesis, calibration resolution (`CAL-###`), insight compounding, and surgical CANONICAL/PROJECTS reconciliation without blowing late-session ECL (`60-80%` full).

## Activation Gate

Invoke `/ultraend` when any holds: opened via `/ultrastart`, `>= 5` decisions made, new frameworks discovered, session `Lambda total >= 200`, or user request. Otherwise default to `/end`.

---

## Phase 0: Standard Close (Inherit `/end` Phase 1B)

Complete all 7 `/end` steps first (Phase 0 guarantees safe session preservation even if later synthesis aborts):
1. Session Log file -> 2. Checkpoint in `activeContext.md` -> 3. Conditional CANONICAL check -> 4. Decision Log Gate -> 5. Update active switchboard -> 6. Reflexion -> Skill-Compiler Gate -> 7. Context Hygiene Gate.

---

## Phase 1: Cross-Session Pattern & Calibration Scan (~60s)

1. Read `@decided`, `@pending`, `@learned` from the last 5 full session logs (not compacted `activeContext.md` summaries):
   ```bash
   ls -1t .context/memories/session_logs/ | head -5
   ```
2. Detect: **Recurring Topics** (`3+` of last 5), **Orphaned Pendings** (`3+` sessions stagnant), **Decision Reversals**, and **Velocity Trend** (`Lambda/session`).
3. **Step 2.5 Calibration Ledger Tracking (`CAL-###`)**: Compare `@decided` / registered probabilities `(p, observable_event, resolution_date)` from sessions `N-1..N-3` against observed outcomes (`Match ✅`, `Partial ⚠️`, `Miss ❌ -> update base-rate priors`, `Pending 🔄`) + check `@seeded` transition from `S[N-1]`. Append `## Decision Outcome & Calibration Tracking` table to session log.

---

## Phase 2: Surgical CANONICAL Reconciliation (~45s)

> **Late-Session Context Guard**: `CANONICAL.md` is `414 KB`. **Never full-read it at 70% ECL.** Search and slice surgically:

1. Query candidate collisions/updates via Exocortex or `grep -n`:
   ```bash
   .agent/scripts/athena-py .agent/scripts/smart_search.py "<key insight or framework keywords>" --limit 5
   ```
   Read surgical line ranges around `.context/CANONICAL.md` §3 (`L130-185`) and matched rows in §4 (`L186-380`).
2. Classify each session insight: **Already present** -> Skip; **Contradicts CANONICAL** -> Update truth; **New reusable framework** (`3+` connected insights -> bundle named framework in §4); **Session noise** -> Skip.

---

## Phase 2.5: Insight Compounding

Test pairs of **top 3 current-session insights x top 3 insights from recent 3 sessions** for non-obvious synthesis. File validated compounds: named framework (`3+` insights) -> `CANONICAL.md` §4; tactical pattern -> `Session_Observations.md`; single link -> session log `## Compound Insights` (write `None detected.` if absent — never force).

---

## Phase 3: Reflexion Archive & Propagation Matrix

Append `## Reflexion` (`Worked`, `Didn't`, `Counterfactual`) to the session log, then propagate **only reusable** findings:
- Reusable `"Worked"` -> `CANONICAL.md` §4
- Repeatable `"Didn't"` -> Target skill's `SKILL.md` `## Anti-Patterns`
- Reusable `"Counterfactual"` workflow improvement -> `.context/TECH_DEBT.md`
- Session-specific items -> stay in session log only.

---

## Phase 4: Surgical Portfolio & Deep Accountability Review

1. **PROJECTS.md Slice**: Read active switchboard tables **only** (`L1009-1067`; skip `L1-1008` archive history). Audit Priority Alignment, `7+ day` stale projects (park/kill), Internal:External ratio (target `<= 30%` internal / `>= 70%` external), and write concrete `@seeded:` next focus.
2. **Phase 4.5 Grace Harper Accountability Close**:
   - Classify weekly `BEH-602` triggers by schema (`#1 Effort = Worth`, `#2 Not Prioritized = Not Enough`, `#3 100% In = 100% Back`, `MP-16 Base Rate Distortion`); flag trends (`🚩 Escalating...`).
   - Run **Weekly Execution Audit** (`Committed vs Executed?` across past 7d checkpoints; flag `< 60%` as `DIAG-001 Knowledge-Action Gap`) and review `BEH-` calibration.

---

## Phase 5: Shutdown Orchestrator & Output

```bash
.agent/scripts/athena-py .agent/scripts/shutdown.py
```

On failure: report root cause after `2` failures (`P514` Circuit Breaker); emergency fallback git-save preserves `.context/`, `.agent/`, `.framework/`, `.claude/`, `AGENTS.md`.

```text
🧠 Deep Close Complete (MaxMax v3.2).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 0]   Standard Close          ✅
[Phase 1]   Pattern + Calibration   ✅  [N patterns, N outcomes tracked]
[Phase 2]   Surgical CANONICAL      ✅  [N updates, N new frameworks]
[Phase 2.5] Insight Compounding     ✅  [N compounds generated]
[Phase 3]   Reflexion + Propagate   ✅  [N findings propagated]
[Phase 4]   Portfolio + BEH Audit   ✅  [Next: "<seeded focus>"]
[Phase 5]   Shutdown                ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session closed. Seed Accuracy (prev): [Match/Partial/Miss]
```

- References: [/end](end.md), [/ultrastart](ultrastart.md), [/save](save.md)

`#workflow` `#automation` `#ultraend` `#system-2` `#deep-synthesis`
