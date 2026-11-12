---
description: Adversarial two-turn wargaming with context-isolated Red Cell generation and path-dependent ruin adjudication
created: 2026-11-13
last_updated: 2026-11-13
model: default
temperature: 0.4
tools:
  read: true
  write: true # Scoped to observable packets, .athena/wargame_runs.jsonl, and GTO receipts
  bash: true  # Scoped strictly to wargame_runner and athena.intelligence.wargame
  search: true
---

# /wargame — Adversarial Two-Turn Wargaming & Red Cell Engine

> **Philosophy**: Adversaries respond to your move, weak paths break at Turn-1 troughs before Turn-2 recovery arrives, and counterparty rule changes invalidate closed-game assumptions.
> **Use When**: Negotiations with responsive counterparties, competitive strategy, vendor/platform lock-in decisions, trading/risk scenarios with intra-period liquidation barriers, or stress-testing any `/gto` policy slate against an adaptive opponent.

> [!IMPORTANT]
> Run `python3 -m athena.intelligence.wargame --capabilities` before making formal claims.
> - **What this engine computes**: Two-turn absorbing barrier resolution (`resolve_two_turn_cell`), fail-closed Law #1 ruin vetting (`UnscreenedWargame` if `wealth` is missing or `<= 0`), Game-Mode maximin and minimax-regret ranking (`compute_robustness`), counterparty best-response (`red_best_responses`, `blue_at_red_br`, `red_br_winner`), sovereign rule-shock stress testing (`counterparty_writes_rules=True`), deciding-margin fragility detection (`FRAGILITY_THRESHOLD = 0.10`), field provenance auditing, and Red Cell independence verification.
> - **What it explicitly does NOT compute**: Formal Nash equilibrium solving, continuous stochastic intra-turn paths beyond `t1_worst`, counterparty responses that Red was not asked to generate, or calibrated probabilities. Payoffs remain estimates unless backed by verifiable `GTO-...` receipts or referenced files.

---

## Hard Constraints & Failure Modes

| Constraint | Value / Rule | Behavior if Violated |
| :--- | :--- | :--- |
| **Survival Vault** | `wealth` finite and `> 0`, `barrier >= 0` | Raises `UnscreenedWargame` (fail-closed) |
| **Slate Caps** | `MAX_POLICIES = 6`, `MAX_RESPONSES = 5` | Raises `ValueError`; keep slates focused |
| **Uniqueness & Baseline** | Unique names; `baseline_policy in policies` | Raises `ValueError` |
| **Information Barrier** | `ObservableActionPacket` forbids private utility/threshold keys (`FORBIDDEN_PACKET_KEYS`) | Raises `InformationBarrierViolationError` |
| **Independence Record** | `run_id` + `packet_sha256` verified in `.athena/wargame_runs.jsonl` | Missing/mismatched record stamps `[THEATER: unverified independence record]` |
| **Provenance Grounding** | `VALID_PROVENANCE_BASES`: `typed`, `computed`, `base-rate`, `agent-estimate` | Unverified sources fall back to `agent-estimate`; `> 50%` flags `[LOW GROUNDING]` |
| **Sovereign Rule Changes** | `counterparty_writes_rules=True` requires `shock_payoffs` for every policy | Injects `__unmodeled_rule_shock__` scenario across all policies |

---

## Phase 1: Context-Isolated Red Cell Generation

Never generate adversary counter-moves in the same prompt containing your private utility matrix, ruin barrier, or acceptable concession thresholds. Isolate what Red can actually observe:

1. Construct a JSON packet containing ONLY observable state:
   - `arena_facts`: Public institutional, contractual, or market environment facts.
   - `red_endowments`: Counterparty incentives, balance sheet, legal leverage, or outside options.
   - `blue_observable_moves`: List of candidate Blue policies visible to the counterparty (names/descriptions only — no payoffs or utilities).

2. Generate Red counter-moves via `examples/scripts/wargame_runner.py`:

```bash
python3 examples/scripts/wargame_runner.py \
  --input packet.json \
  --model gemini-2.5-flash \
  --class separate-context
```

3. `build_observable_packet` enforces `FORBIDDEN_PACKET_KEYS` (preventing private payoffs, utilities, heuristics, or barriers from leaking into the Red Cell prompt), `scan_outbound_packet` checks outbound content boundaries, and `record_wargame_run` writes `(run_id, packet_sha256, prompt_sha256, response_sha256)` to `.athena/wargame_runs.jsonl`.

---

## Phase 2: Two-Turn Payoff Matrix & Provenance

For every pair `(policy, red_response)` inside `cells`, populate a `WargameCell` payload:

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `t1_payoff` | Yes | Turn-1 net payoff for Blue |
| `t1_worst` | Recommended | Turn-1 intra-period trough excursion; if `wealth + t1_worst <= barrier * wealth`, liquidation triggers at Turn 1 and `t2_payoff` is zeroed |
| `t2_payoff` | Optional (`0.0`) | Turn-2 recovery/follow-through payoff (ignored if Turn-1 absorbing barrier triggers) |
| `red_payoff` | Optional | Counterparty utility score for Red Best-Response analysis (omission stamps `[RED_BR UNAVAILABLE: missing red_payoff]`) |
| `p_ruin_t1`, `p_ruin_t2` | Optional | Compounded across turns and scaled by `tail_factor=3.0` against `LAW1_MAX_RUIN` |
| `provenance` | Recommended | Per-field `{"basis": "...", "source": "..."}` referencing a valid `GTO-...` receipt ID or existing file path |

If the counterparty is a platform, regulator, landlord, sovereign, or monopolist able to change the game rules mid-flight, include `"counterparty_writes_rules": true` and `"shock_payoffs": {<policy>: <numeric_impact>}`.

---

## Phase 3: Deterministic Adjudication

Invoke the adjudication engine and persist a `GTO-...` calibration receipt:

```bash
python3 -m athena.intelligence.wargame \
  --input wargame_payload.json \
  --real \
  --review-date YYYY-MM-DD \
  --prediction "Policy X preserves maximin >= threshold without Turn-1 barrier breach" \
  --json
```

Payloads are archived to `.athena/receipts/wargame-<receipt_id>.json`.

---

## Phase 4: Verdict & Escalation

Inspect `verdict`, `to_ascii_table()`, `top_candidate`, `maximin_winner`, `minimax_regret_winner`, `red_br_winner`, and `fragility`:

- **`ALL POLICIES VETOED UNDER LAW #1`**: No submitted policy survives Turn-1/terminal barrier and compound ruin constraints; halt or add safer outside-option / barbell policies.
- **`ROBUST CONSENSUS`**: Maximin, minimax regret, and Red best-response converge on one feasible policy.
- **`CRITERIA DISAGREE`**: Different robustness lenses pick different survivors; inspect `fragility` (`deciding_margin` vs `0.10 * span`) and `blue_at_red_br` trade-offs before committing.
- **Unverified Warning Tags**: Treat `[THEATER]`, `[LOW GROUNDING]`, `[RED_BR UNAVAILABLE]`, or `[IIA-SENSITIVE]` as explicit audit gaps rather than silent passes.

### Related Workflows

- [`/osint`](osint.md) — Gather verified counterparty facts (`red_endowments`, registry/litigation records, UCDS knockouts) before building a wargame packet.
- [`/gto`](gto.md) — Single-agent or multi-criteria EEV/MCDA decision screening and calibration ledger (`frame_ledger`).
