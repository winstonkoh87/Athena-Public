"""
athena.intelligence.wargame
===========================

Adversarial Wargaming Simulation & Adjudication Module.
Thin adapter over athena.intelligence.gto_engine.compute_robustness.

Adjudicates 2-turn Blue vs. Red wargames with path-dependent intra-turn
trough ruin screening, evidence-gated provenance, open-game sovereign
rule-change protection, and side-by-side criteria ranking.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from athena.intelligence.gto_engine import (
    LAW1_MAX_RUIN,
    RobustnessResult,
    compute_robustness,
    get_receipts_path,
    iter_receipts,
    log_decision_receipt,
)

__all__ = [
    "WargameCell",
    "WargameResult",
    "UnscreenedWargame",
    "resolve_two_turn_cell",
    "adjudicate_wargame",
    "main",
    "WARGAME_CAPABILITIES",
]

WARGAME_CAPABILITIES: dict[str, dict[str, Any]] = {
    "adjudicate_wargame": {
        "computes": "Two-turn adversarial wargame adjudication with path-dependent trough ruin and Red best-response",
        "typed_inputs": [
            "policies",
            "red_responses",
            "cells",
            "baseline_policy",
            "wealth",
            "barrier",
            "counterparty_writes_rules",
            "shock_payoffs",
            "independence_record",
            "tail_factor",
        ],
        "defaults": {
            "wealth": None,
            "barrier": 0.0,
            "counterparty_writes_rules": False,
            "shock_payoffs": None,
            "independence_record": None,
            "tail_factor": 3.0,
        },
        "does_not": [
            "equilibrium solving",
            "intra-turn paths beyond t1_worst",
            "responses Red wasn't asked to generate",
            "calibrated probabilities",
        ],
    },
    "resolve_two_turn_cell": {
        "computes": "Path-dependent absorbing barrier resolution across Turn-1 excursion and Turn-2 payoff",
        "typed_inputs": ["wealth", "barrier", "t1_payoff", "t1_worst", "t2_payoff"],
        "defaults": {"barrier": 0.0, "t2_payoff": 0.0},
        "does_not": [
            "continuous stochastic path generation",
            "intra-turn paths beyond t1_worst",
        ],
    },
}

VALID_PROVENANCE_BASES: tuple[str, ...] = ("typed", "computed", "base-rate", "agent-estimate")
MAX_POLICIES: int = 6
MAX_RESPONSES: int = 5
FRAGILITY_THRESHOLD: float = 0.10  # Asserted, not calibrated


class UnscreenedWargame(ValueError):
    """Raised when wealth is missing or non-positive, failing closed on Law #1."""
    pass


@dataclass(frozen=True)
class WargameCell:
    """Represents a single (Blue Policy, Red Response) interaction cell."""
    t1_payoff: float
    t1_worst: float
    t2_payoff: float = 0.0
    red_payoff: float | None = None
    p_ruin_t1: float | None = None
    p_ruin_t2: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    note: str = ""

    def __post_init__(self) -> None:
        if not math.isfinite(self.t1_payoff):
            raise ValueError(f"t1_payoff must be finite, got {self.t1_payoff}")
        if not math.isfinite(self.t1_worst):
            raise ValueError(f"t1_worst must be finite, got {self.t1_worst}")
        if self.t1_worst > min(0.0, self.t1_payoff) + 1e-9:
            raise ValueError(
                f"t1_worst ({self.t1_worst}) must be <= min(0.0, t1_payoff={self.t1_payoff})"
            )
        if not math.isfinite(self.t2_payoff):
            raise ValueError(f"t2_payoff must be finite, got {self.t2_payoff}")
        if self.red_payoff is not None and not math.isfinite(self.red_payoff):
            raise ValueError(f"red_payoff must be finite, got {self.red_payoff}")
        for p_name, p_val in (("p_ruin_t1", self.p_ruin_t1), ("p_ruin_t2", self.p_ruin_t2)):
            if p_val is not None and (not math.isfinite(p_val) or not (0.0 <= p_val <= 1.0)):
                raise ValueError(f"{p_name} must be in [0.0, 1.0], got {p_val}")


@dataclass
class WargameResult:
    """Encapsulates wargame adjudication outcomes."""
    policies: list[str]
    red_responses: list[str]
    baseline_policy: str
    wealth: float
    barrier: float
    counterparty_writes_rules: bool
    independence_class: str
    effective_matrix: dict[str, dict[str, float]]
    ruin_matrix: dict[str, dict[str, bool]]
    robustness_result: RobustnessResult
    red_best_responses: dict[str, list[str]]
    blue_at_red_br: dict[str, float]
    red_br_winner: str | None
    maximin_winner: str | None
    minimax_regret_winner: str | None
    top_candidate: str | None
    verdict: str
    agent_estimate_share: float
    provenance_details: dict[str, Any]
    fragility: dict[str, Any]
    notes: list[str]

    @property
    def feasible_policies(self) -> list[str]:
        return self.robustness_result.feasible_policies

    @property
    def vetoed_policies(self) -> list[str]:
        return self.robustness_result.infeasible_policies

    def to_ascii_table(self) -> str:
        """Render plain ASCII results table."""
        lines = [
            "=" * 78,
            "ATHENA ADVERSARIAL WARGAME SCOREBOARD",
            "=" * 78,
            f"Verdict: {self.verdict}",
            f"Top Candidate (Maximin): {self.top_candidate or 'NONE'}",
            f"Independence: {self.independence_class}",
            f"Grounding: {(1.0 - self.agent_estimate_share) * 100:.1f}% grounded, "
            f"{self.agent_estimate_share * 100:.1f}% agent-estimate",
            "-" * 78,
            f"{'Policy':<20} | {'Maximin Floor':<14} | {'Max Regret':<12} | {'At Red BR':<12} | {'Status':<10}",
            "-" * 78,
        ]
        for p in self.policies:
            stats = self.robustness_result.policy_stats.get(p)
            floor_str = f"{stats.worst_outcome:+.2f}" if stats else "N/A"
            regret_str = f"{stats.max_regret:.2f}" if stats else "N/A"
            at_br = self.blue_at_red_br.get(p)
            br_str = f"{at_br:+.2f}" if at_br is not None else "N/A"
            status = "FEASIBLE" if p in self.robustness_result.feasible_policies else "VETOED"
            lines.append(f"{p:<20} | {floor_str:<14} | {regret_str:<12} | {br_str:<12} | {status:<10}")
        lines.append("=" * 78)
        return "\n".join(lines)


def resolve_two_turn_cell(
    wealth: float,
    barrier: float,
    t1_payoff: float,
    t1_worst: float,
    t2_payoff: float = 0.0,
) -> tuple[float, bool]:
    """Resolve path-dependent 2-turn absorbing barrier outcome.

    If Turn-1 intermediate excursion (t1_worst) hits the barrier:
      W_t1 = wealth + t1_worst <= barrier * wealth -> liquidated at Turn 1!
      Effective payoff is truncated to t1_worst; Turn 2 recovery is zeroed.
    Otherwise:
      Effective payoff is t1_payoff + t2_payoff; checked against terminal barrier.
    """
    if not math.isfinite(wealth) or wealth <= 0.0:
        raise ValueError(f"wealth must be finite and > 0, got {wealth}")
    if not math.isfinite(barrier) or barrier < 0.0:
        raise ValueError(f"barrier must be non-negative, got {barrier}")

    barrier_threshold = barrier * wealth
    w_t1 = wealth + t1_worst
    if w_t1 <= barrier_threshold:
        # Absorbing barrier hit during Turn 1
        return t1_worst, True

    eff = t1_payoff + t2_payoff
    w_term = wealth + eff
    if w_term <= barrier_threshold:
        return eff, True

    return eff, False


def _verify_provenance_basis(
    field_name: str,
    prov_dict: dict[str, Any],
    receipts_path: Path,
) -> str:
    """Verify claimed provenance basis against filesystem and receipt records."""
    basis = prov_dict.get("basis", "agent-estimate")
    source = str(prov_dict.get("source", "")).strip()

    if basis not in VALID_PROVENANCE_BASES:
        return "agent-estimate"
    if basis == "agent-estimate":
        return "agent-estimate"

    # Non-agent-estimate basis requires a verifiable source
    if not source:
        return "agent-estimate"

    # Check if source is a verified non-void GTO- receipt ID in receipts log
    if source.startswith("GTO-") and receipts_path.exists():
        try:
            valid_ids = {
                str(r["receipt_id"])
                for r in iter_receipts(receipts_path=receipts_path, include_void=False)
                if "receipt_id" in r
            }
            if source in valid_ids:
                return basis
        except Exception:
            pass

    # Check if source is an existing file path
    try:
        p = Path(source)
        if p.exists():
            return basis
    except Exception:
        pass

    return "agent-estimate"


def _verify_independence_record(
    independence_record: dict[str, str] | None,
    repo_root: Path,
) -> str:
    """Verify run_id and packet hash in .athena/wargame_runs.jsonl."""
    if not independence_record:
        return "same-context (theater)"

    run_id = independence_record.get("run_id")
    packet_hash = independence_record.get("packet_sha256")
    claimed_class = independence_record.get("class", "separate-context")

    if not run_id or not packet_hash:
        return "same-context (theater)"

    runs_file = repo_root / ".athena" / "wargame_runs.jsonl"
    if not runs_file.exists():
        return "same-context (theater)"

    try:
        for line in runs_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("run_id") == run_id and entry.get("packet_sha256") == packet_hash:
                return claimed_class
    except Exception:
        pass

    return "same-context (theater)"


def adjudicate_wargame(
    policies: list[str],
    red_responses: list[str],
    cells: dict[str, dict[str, WargameCell | dict[str, Any]]],
    *,
    baseline_policy: str,
    wealth: float | None = None,
    barrier: float = 0.0,
    counterparty_writes_rules: bool = False,
    shock_payoffs: dict[str, float] | None = None,
    independence_record: dict[str, str] | None = None,
    tail_factor: float = 3.0,
) -> WargameResult:
    """Adjudicate 2-turn adversarial wargame with fail-closed ruin and Red BR."""
    # 1. Validation & Caps
    if wealth is None or not math.isfinite(wealth) or wealth <= 0.0:
        raise UnscreenedWargame(
            f"wealth is required and must be finite > 0 for Law #1 wargame adjudication, got {wealth}"
        )
    if not policies or not red_responses:
        raise ValueError("policies and red_responses must be non-empty")
    if len(policies) > MAX_POLICIES or len(red_responses) > MAX_RESPONSES:
        raise ValueError(
            f"Caps exceeded: max {MAX_POLICIES} policies, {MAX_RESPONSES} responses. "
            f"Got ({len(policies)}, {len(red_responses)})"
        )
    if len(set(policies)) != len(policies):
        raise ValueError(f"policies must contain unique names, got {policies}")
    if len(set(red_responses)) != len(red_responses):
        raise ValueError(f"red_responses must contain unique names, got {red_responses}")
    if baseline_policy not in policies:
        raise ValueError(f"baseline_policy {baseline_policy!r} must be in policies {policies}")

    # 2. Open Game Sovereign Rule-Change Check
    effective_responses = list(red_responses)
    if counterparty_writes_rules:
        if shock_payoffs is None:
            raise ValueError(
                "counterparty_writes_rules=True requires shock_payoffs dict for all policies"
            )
        for p in policies:
            if p not in shock_payoffs or not math.isfinite(shock_payoffs[p]):
                raise ValueError(f"Missing or non-finite shock payoff for policy {p!r}")
        effective_responses.append("__unmodeled_rule_shock__")

    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        repo_root = Path(env_root).resolve()
    else:
        repo_root = Path.cwd().resolve()
        for parent in [repo_root, *repo_root.parents]:
            if (parent / ".context").exists() or (parent / ".athena").exists():
                repo_root = parent
                break
    receipts_path = get_receipts_path()

    # 3. Provenance & Cell Normalization
    normalized_cells: dict[str, dict[str, WargameCell]] = {}
    total_fields = 0
    agent_est_fields = 0

    for p in policies:
        if p not in cells:
            raise ValueError(f"Policy {p!r} missing from cells matrix")
        normalized_cells[p] = {}
        for r in red_responses:
            if r not in cells[p]:
                raise ValueError(f"Cell ({p!r}, {r!r}) missing from cells matrix")
            raw = cells[p][r]
            if isinstance(raw, WargameCell):
                cell_obj = raw
            else:
                prov_raw = raw.get("provenance", {})
                cell_obj = WargameCell(
                    t1_payoff=float(raw["t1_payoff"]),
                    t1_worst=float(raw.get("t1_worst", min(0.0, float(raw["t1_payoff"])))),
                    t2_payoff=float(raw.get("t2_payoff", 0.0)),
                    red_payoff=float(raw["red_payoff"]) if raw.get("red_payoff") is not None else None,
                    p_ruin_t1=float(raw["p_ruin_t1"]) if raw.get("p_ruin_t1") is not None else None,
                    p_ruin_t2=float(raw["p_ruin_t2"]) if raw.get("p_ruin_t2") is not None else None,
                    provenance=prov_raw if isinstance(prov_raw, dict) else {},
                    note=str(raw.get("note", "")),
                )
            normalized_cells[p][r] = cell_obj

            # Audit field provenance
            for f_name in ("t1_payoff", "t1_worst", "t2_payoff", "red_payoff"):
                total_fields += 1
                field_prov = cell_obj.provenance.get(f_name, {})
                accepted_basis = _verify_provenance_basis(f_name, field_prov, receipts_path)
                if accepted_basis == "agent-estimate":
                    agent_est_fields += 1

    agent_estimate_share = round(agent_est_fields / max(1, total_fields), 4)

    # 4. Resolve Path-Dependent Payoffs and Ruin Flags
    eff_matrix: dict[str, dict[str, float]] = {p: {} for p in policies}
    ruin_matrix: dict[str, dict[str, bool]] = {p: {} for p in policies}

    for p in policies:
        for r in red_responses:
            c = normalized_cells[p][r]
            eff, is_ruin = resolve_two_turn_cell(
                wealth=wealth,
                barrier=barrier,
                t1_payoff=c.t1_payoff,
                t1_worst=c.t1_worst,
                t2_payoff=c.t2_payoff,
            )
            # Evaluate compound typed ruin probability if provided
            if c.p_ruin_t1 is not None or c.p_ruin_t2 is not None:
                p1 = c.p_ruin_t1 or 0.0
                p2 = c.p_ruin_t2 or 0.0
                p_comp = 1.0 - (1.0 - p1) * (1.0 - p2)
                if min(1.0, tail_factor * p_comp) > LAW1_MAX_RUIN:
                    is_ruin = True

            eff_matrix[p][r] = eff
            ruin_matrix[p][r] = is_ruin

        if counterparty_writes_rules and shock_payoffs is not None:
            shock_val = float(shock_payoffs[p])
            eff_matrix[p]["__unmodeled_rule_shock__"] = shock_val
            shock_ruin = (wealth + shock_val <= barrier * wealth)
            ruin_matrix[p]["__unmodeled_rule_shock__"] = shock_ruin

    # 5. Delegate to compute_robustness (Game Mode only: no probs passed)
    rob_res = compute_robustness(
        policies=policies,
        scenarios=effective_responses,
        payoff=eff_matrix,
        ruin=ruin_matrix,
        wealth=wealth,
        barrier=barrier,
        tail_factor=tail_factor,
    )

    # 6. Red Best-Response Layer
    red_best_responses: dict[str, list[str]] = {}
    blue_at_red_br: dict[str, float] = {}
    has_full_red_utility = True

    for p in policies:
        red_u_list = [
            (r, normalized_cells[p][r].red_payoff)
            for r in red_responses
        ]
        if any(u is None for _, u in red_u_list):
            has_full_red_utility = False
            red_best_responses[p] = []
            blue_at_red_br[p] = rob_res.policy_stats[p].worst_outcome
        else:
            max_u = max(u for _, u in red_u_list if u is not None)
            br_tied = [
                r for r, u in red_u_list
                if u is not None and math.isclose(u, max_u, abs_tol=1e-9)
            ]
            red_best_responses[p] = br_tied
            # Conservative tie-breaking: worst for Blue
            blue_at_red_br[p] = min(eff_matrix[p][r] for r in br_tied)

    red_br_winner: str | None = None
    if has_full_red_utility and rob_res.feasible_policies:
        feasible_br = [
            (p, blue_at_red_br[p])
            for p in rob_res.feasible_policies
        ]
        feasible_br.sort(key=lambda x: x[1], reverse=True)
        red_br_winner = feasible_br[0][0]

    # 7. Independence Record Verification
    independence_class = _verify_independence_record(independence_record, repo_root)

    # 8. Fragility Analysis
    # Measured on the deciding criterion (maximin) over feasible policies
    fragile = False
    deciding_margin = 0.0
    if len(rob_res.feasible_policies) >= 2:
        feasible_floors = sorted(
            [rob_res.policy_stats[p].worst_outcome for p in rob_res.feasible_policies],
            reverse=True,
        )
        deciding_margin = feasible_floors[0] - feasible_floors[1]
        all_feasible_eff = [
            eff_matrix[p][r]
            for p in rob_res.feasible_policies
            for r in effective_responses
        ]
        span = max(all_feasible_eff) - min(all_feasible_eff)
        span = max(1.0, span)
        fragile = (deciding_margin < FRAGILITY_THRESHOLD * span)

    fragility_info = {
        "deciding_margin": round(deciding_margin, 4),
        "fragile": fragile,
        "threshold_fraction": FRAGILITY_THRESHOLD,
    }

    # 9. Format Verdict & Top Candidate
    if not rob_res.feasible_policies:
        consensus_text = "ALL POLICIES VETOED UNDER LAW #1"
        top_cand = None
    else:
        top_cand = rob_res.maximin_winner if rob_res.maximin_winner != "NONE" else None
        winners_set = {
            w for w in (rob_res.maximin_winner, rob_res.minimax_regret_winner, red_br_winner)
            if w is not None and w != "NONE"
        }
        if len(winners_set) == 1:
            consensus_text = f"ROBUST CONSENSUS: {next(iter(winners_set))} dominates across criteria"
        else:
            consensus_text = "CRITERIA DISAGREE: maximin, minimax regret, and Red-BR select different policies"

    verdict_parts = [consensus_text]
    if not has_full_red_utility:
        verdict_parts.append("[RED_BR UNAVAILABLE: missing red_payoff]")
    if independence_class == "same-context (theater)":
        verdict_parts.append("[THEATER: unverified independence record]")
    if agent_estimate_share > 0.50:
        verdict_parts.append(
            f"[LOW GROUNDING: {agent_est_fields}/{total_fields} cells ({agent_estimate_share*100:.1f}%) agent-estimate]"
        )
    if "[IIA-SENSITIVE]" in rob_res.verdict:
        verdict_parts.append("[IIA-SENSITIVE]")

    final_verdict = " ".join(verdict_parts)

    notes = [
        f"Independence class: {independence_class}",
        f"Grounded share: {(1.0 - agent_estimate_share)*100:.1f}%",
        f"Baseline policy: {baseline_policy}",
    ]

    return WargameResult(
        policies=policies,
        red_responses=effective_responses,
        baseline_policy=baseline_policy,
        wealth=wealth,
        barrier=barrier,
        counterparty_writes_rules=counterparty_writes_rules,
        independence_class=independence_class,
        effective_matrix=eff_matrix,
        ruin_matrix=ruin_matrix,
        robustness_result=rob_res,
        red_best_responses=red_best_responses,
        blue_at_red_br=blue_at_red_br,
        red_br_winner=red_br_winner,
        maximin_winner=rob_res.maximin_winner,
        minimax_regret_winner=rob_res.minimax_regret_winner,
        top_candidate=top_cand,
        verdict=final_verdict,
        agent_estimate_share=agent_estimate_share,
        provenance_details={
            "total_fields": total_fields,
            "agent_estimate_fields": agent_est_fields,
            "share": agent_estimate_share,
        },
        fragility=fragility_info,
        notes=notes,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI driver for wargame adjudication."""
    parser = argparse.ArgumentParser(
        description="Athena Adversarial Wargame Simulation & Adjudication Engine",
        prog="athena-wargame",
    )
    parser.add_argument("--input", type=str, help="JSON input string or path to JSON file")
    parser.add_argument("--capabilities", action="store_true", help="Print module capability manifest")
    parser.add_argument("--real", action="store_true", help="Mark decision receipt as real")
    parser.add_argument("--review-date", type=str, default=None, help="Calibration review date (YYYY-MM-DD)")
    parser.add_argument("--prediction", type=str, default=None, help="Falsifiable prediction claim")
    parser.add_argument("--receipts-path", type=str, default=None, help="Override receipts JSONL path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args(argv)

    if args.capabilities:
        print(json.dumps(WARGAME_CAPABILITIES, indent=2))
        return 0

    if not args.input:
        parser.print_help()
        return 2

    # Parse input payload
    input_str = args.input.strip()
    p_path = Path(input_str)
    if p_path.exists() and p_path.is_file():
        payload = json.loads(p_path.read_text(encoding="utf-8"))
    else:
        payload = json.loads(input_str)

    try:
        res = adjudicate_wargame(
            policies=payload["policies"],
            red_responses=payload["red_responses"],
            cells=payload["cells"],
            baseline_policy=payload["baseline_policy"],
            wealth=float(payload["wealth"]) if payload.get("wealth") is not None else None,
            barrier=float(payload.get("barrier", 0.0)),
            counterparty_writes_rules=bool(payload.get("counterparty_writes_rules", False)),
            shock_payoffs=payload.get("shock_payoffs"),
            independence_record=payload.get("independence_record"),
            tail_factor=float(payload.get("tail_factor", 3.0)),
        )
    except UnscreenedWargame as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error executing wargame engine: {e}", file=sys.stderr)
        return 1

    # Log receipt
    rec_entry = log_decision_receipt(
        action="wargame",
        inputs=payload,
        result=res,
        receipts_path=Path(args.receipts_path).resolve() if args.receipts_path else None,
        real_decision=args.real,
        review_date=args.review_date,
        prediction=args.prediction,
    )
    receipt_id = rec_entry.get("receipt_id", "GTO-unknown") if isinstance(rec_entry, dict) else str(rec_entry)

    # Archive payload to .athena/receipts/wargame-<receipt_id>.json
    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        repo_root = Path(env_root).resolve()
    else:
        repo_root = Path.cwd().resolve()
        for parent in [repo_root, *repo_root.parents]:
            if (parent / ".athena").exists():
                repo_root = parent
                break
    archive_dir = repo_root / ".athena" / "receipts"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_file = archive_dir / f"wargame-{receipt_id}.json"
    archive_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        out_data = {
            "receipt_id": receipt_id,
            "verdict": res.verdict,
            "top_candidate": res.top_candidate,
            "maximin_winner": res.maximin_winner,
            "minimax_regret_winner": res.minimax_regret_winner,
            "red_br_winner": res.red_br_winner,
            "independence_class": res.independence_class,
            "agent_estimate_share": res.agent_estimate_share,
            "fragility": res.fragility,
        }
        print(json.dumps(out_data, indent=2))
    else:
        print(res.to_ascii_table())
        print(f"\nDecision Receipt Logged: {receipt_id}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
