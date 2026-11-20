---
description: Activate Athena MinMax v2.2 1-wave boot sequence and JIT contextual routing
created: 2025-12-09
last_updated: 2026-11-21
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /start — Fast MinMax v2.2 Execution Boot

> **Default Protocol**: MinMax v2.2 ([minmax.md](minmax.md)) — 1-wave parallel boot (`< 1.0s` local I/O, `<= 2` LLM round-trips), zero redundant file reads, full safety & quality floors. Use `/ultrastart` for MaxMax deep boot.

## Phase 1: 1-Wave Boot

1. **SNIPER Fast-Exit (`Lambda < 10`, greetings, `"Test"`, 1-line banter)**:
   - Execute **0 boot reads** and **0 MCP calls**. Respond immediately in 1 round-trip (bare greeting -> `"⚡ Ready."`).
2. **One-Shot Telemetry + Context Wave (`Lambda >= 10` or explicit `/start`)**:
   - Run ONE parallel wave combining local boot bundle + `context_gate(query, limit=8)` (when substantive):
     ```bash
     .agent/scripts/athena-py scripts/boot_status.py --bundle
     ```
   - `--bundle` returns compact telemetry, active alerts/advisories, latest `activeContext.md` checkpoint, and `userContext.md` in a single `< 1.0s` call (use bare `boot_status.py` only when full multi-line digest is requested; `--compact` for alerts only; `--json` for programmatic parsing).
   - **Do NOT read** `.agent/workflows/_shared.md`, `.agent/workflows/start.md`, or `.framework/` modules during fast boot (reserve deep loads for `/ultrastart`). Load `.context/memory_bank/productContext.md` only on explicit `/start` or product queries.
   - Surface exact `boot_status.py` output lines verbatim and scan `@pending` for 7+ session carryover -> `ℹ️ Long-pending: [TASK] — N sessions.` (Protocol 528 advisory).

## Phase 1.5: Warm Boot (Optional)

*Skip whenever Turn 1 already invokes `context_gate` or states an explicit task topic (route straight to Phase 2/3).*
1. Check `@seeded` in latest checkpoint, fallback to `Current Focus`. If both absent, skip Phase 1.5.
2. Run ONE surgical recall query and read top result header (first 30 lines):
   ```bash
   .agent/scripts/athena-py .agent/scripts/smart_search.py "<inferred objective>" --limit 3 --include-personal
   ```

## Phase 2 & 3: Risk Classification & JIT Routing

- **SNIPER (Λ < 10)**: Direct response (`vector_mode="local"`).
- **STANDARD / ULTRA (Λ >= 10)**: Ground via `context_gate(query, limit=8)` (signature in `AGENTS.md`) or:
  ```bash
  .agent/scripts/athena-py .agent/scripts/smart_search.py "<query>" --limit 5 --include-personal
  ```
  Verify volatile facts via `search_web` / `read_url_content`; reserve `quicksave.py` for durable decisions/writes (skip on exploratory Turn-1 Q&A).
- **Protocol 517 Homeostasis (`agent-discretion`)**: Context `> 80%` -> treat incoming queries as SNIPER; `> 90%` -> run `context-compactor` first; `>= 2` consecutive tool failures -> P514 circuit breaker halt; chain depth `> 4` -> Quality Gate exit.
- **Cluster & Tier Escalation**: Route via `CLUSTER_INDEX.md` and [references/_shared_extended.md](references/_shared_extended.md) (Adaptive Loading matrix, UI standards, Compute Tiers, Reflexion format). Silently weave matched cluster skills without announcing.

| Mode | Effect | Target Boot |
|:---|:---|:---|
| `/start` | MinMax v2.2 1-wave `--bundle` + JIT routing | `<= 2` rounds / `< 1.0s` local |
| `/think` | Escalate current turn (`Output_Standards.md`) | +2K tokens |
| `/ultrastart` | MaxMax deep load (~28-60K tokens) | Deep audit/strategy |

`#workflow` `#automation` `#start`
