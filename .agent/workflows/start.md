---
description: Activate Athena MinMax v2.0 boot sequence and JIT contextual routing
created: 2025-12-09
last_updated: 2026-11-14
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /start — Fast MinMax Execution Boot

> **Default Protocol**: MinMax v2.0 ([minmax.md](minmax.md)) — minimize boot tokens (~2K) and latency (`< 1.0s`), preserve full safety & quality floors. Use `/ultrastart` for MaxMax deep boot.

## Phase 1: Instant Boot (~2K tokens)

1. **Tool-Read Core Identity & Surgical State** (mandatory before confirming):
   - `.context/memory_bank/userContext.md` — Core constraints & profile
   - `.context/memory_bank/productContext.md` — Mission & architecture
   - `.context/memory_bank/activeContext.md` — **Surgical load ONLY**: Header up to first `---`, latest `[[ S__` checkpoint block, and any unclosed session.
2. **Confirm** (emit `"⚡ Ready. (Core Identity loaded.)"` ONLY after actual tool reads above):
   - Scan `@pending` for 7+ session carryover -> neutral line `ℹ️ Long-pending: [TASK] — N sessions.` (Protocol 528 advisory).
3. **Single-Pass Parallel Status Telemetry** (`< 1.0s`, zero `RuntimeWarning`):
   ```bash
   .agent/scripts/athena-py scripts/boot_status.py
   ```
   *(Pass `--json` when parsing fields programmatically. Runs `accountability_render`, `maintenance_ratio`, `frame_ledger`, `decisions_due`, `index_health`, `context_summaries`, and `last_boot.log` in one concurrent process.)*
   - Surface exact output lines verbatim (never copy status templates without execution receipts).
   - **Accountability & Freeze Advisories (non-blocking)**: Saturday & `beh_601.last_completed` not this week -> `⚠️ Saturday — Solo session target. BEH-601 active.`; Sunday & `weekly_audit.last_audit_date` > 7d -> `📊 Weekly audit due.`; maintenance > 70% with zero open/awaiting-payment `beh_603` deals -> `⚠️ Freeze advisory (TD-045)`.

## Phase 1.5: Warm Boot (~500 tokens)

*Skip immediately if the user's opening prompt already states an explicit task topic (route straight to Phase 2/3).*
1. Check `@seeded` in latest checkpoint, fallback to `Current Focus`. If both absent, skip Phase 1.5.
2. Run ONE surgical recall query and read top result header (first 30 lines):
   ```bash
   .agent/scripts/athena-py .agent/scripts/smart_search.py "<inferred objective>" --limit 3 --include-personal
   ```

## Phase 2 & 3: Risk Classification & JIT Routing

- **SNIPER (Λ < 10)**: Direct response (`vector_mode="local"`).
- **STANDARD / ULTRA (Λ >= 10)**: Ground via `mcp_athena_context_gate(query)` or:
  ```bash
  .agent/scripts/athena-py .agent/scripts/smart_search.py "<query>" --limit 5 --include-personal
  ```
  Verify volatile facts via `search_web` / `read_url_content`; persist durable learnings post-output via `.agent/scripts/athena-py .agent/scripts/quicksave.py --stdin`.
- **Protocol 517 Homeostasis (`agent-discretion`)**: Context `> 80%` -> treat incoming queries as SNIPER; `> 90%` -> run `context-compactor` first; `>= 2` consecutive tool failures -> P514 circuit breaker halt; chain depth `> 4` -> Quality Gate exit.
- **Cluster & Tier Escalation**: Route via `CLUSTER_INDEX.md` and [references/_shared_extended.md](references/_shared_extended.md) (Adaptive Loading matrix, UI standards, Compute Tiers, Reflexion format). Silently weave matched cluster skills without announcing.

| Mode | Effect | Target Boot |
|:---|:---|:---|
| `/start` | MinMax v2.0 default + JIT routing | ~2K tokens / `< 1.0s` |
| `/think` | Escalate current turn (`Output_Standards.md`) | +2K tokens |
| `/ultrastart` | MaxMax deep load (~28-60K tokens) | Deep audit/strategy |

`#workflow` `#automation` `#start`
