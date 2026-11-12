"""
tests.test_gto_engine_wargame
=============================

Regression, seam, and mutation tests for Athena Adversarial Wargaming Engine.
Covers probes P0-P15 and invariants from 2026-10-23-wargaming-engine-redteam-plan.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from wargame_runner import (
    InformationBarrierViolationError,
    build_observable_packet,
    execute_red_cell,
)

from athena.intelligence.wargame import (
    UnscreenedWargame,
    adjudicate_wargame,
)
from athena.intelligence.wargame import (
    main as wargame_main,
)


def make_cell(t1: float, t1_worst: float | None = None, t2: float = 0.0, red: float | None = 0.0, **kwargs) -> dict:
    worst = t1_worst if t1_worst is not None else min(0.0, t1)
    return {
        "t1_payoff": t1,
        "t1_worst": worst,
        "t2_payoff": t2,
        "red_payoff": red,
        **kwargs,
    }


def test_p0_import_and_capabilities_cli(capsys: pytest.CaptureFixture[str]) -> None:
    """P0/P11: Imports cleanly and CLI --capabilities outputs valid manifest."""
    rc = wargame_main(["--capabilities"])
    assert rc == 0
    captured = capsys.readouterr()
    manifest = json.loads(captured.out)
    assert "adjudicate_wargame" in manifest
    assert "resolve_two_turn_cell" in manifest
    assert "does_not" in manifest["adjudicate_wargame"]


def test_p1_fail_closed_when_wealth_none() -> None:
    """P1: Missing wealth raises UnscreenedWargame; never recommends ruinous loss."""
    cells = {
        "GridA": {"R1": make_cell(500, -5000)},
        "GridB": {"R1": make_cell(400, -6000)},
    }
    with pytest.raises(UnscreenedWargame) as exc_info:
        adjudicate_wargame(
            policies=["GridA", "GridB"],
            red_responses=["R1"],
            cells=cells,
            baseline_policy="GridA",
            wealth=None,
        )
    assert "wealth is required" in str(exc_info.value)


def test_p2_feasible_only_regret_benchmark() -> None:
    """P2: Regret benchmarked over feasible policies only (vetoed V does not inflate regret)."""
    # S1 (10, 2), S2 (2, 10), V (2000, -1500) on wealth 1000, barrier 0.0
    cells = {
        "S1": {"R1": make_cell(10, 0), "R2": make_cell(2, 0)},
        "S2": {"R1": make_cell(2, 0), "R2": make_cell(10, 0)},
        "V": {"R1": make_cell(2000, 0), "R2": make_cell(-1500, -1500)}, # V is ruined at R2
    }
    res = adjudicate_wargame(
        policies=["S1", "S2", "V"],
        red_responses=["R1", "R2"],
        cells=cells,
        baseline_policy="S1",
        wealth=1000.0,
    )
    assert "V" in res.vetoed_policies
    assert "S1" in res.feasible_policies
    assert "S2" in res.feasible_policies
    # Col best over feasible policies: R1=10 (S1), R2=10 (S2)
    # Regret for S1: R1=0, R2=8 -> max_regret=8.0
    # Regret for S2: R1=8, R2=0 -> max_regret=8.0
    s1_stats = res.robustness_result.policy_stats["S1"]
    s2_stats = res.robustness_result.policy_stats["S2"]
    assert s1_stats.max_regret == 8.0
    assert s2_stats.max_regret == 8.0


def test_p3_fragility_measured_on_deciding_criterion_over_feasible() -> None:
    """P3: Fragility calculated on deciding margin over feasible policies."""
    # A (50, 50), B (49, 200) -> A wins by floor 50 vs 49; margin=1; span=151; margin < 0.10*span -> fragile True
    cells = {
        "A": {"R1": make_cell(50, 0), "R2": make_cell(50, 0)},
        "B": {"R1": make_cell(49, 0), "R2": make_cell(200, 0)},
    }
    res = adjudicate_wargame(
        policies=["A", "B"],
        red_responses=["R1", "R2"],
        cells=cells,
        baseline_policy="A",
        wealth=1000.0,
    )
    assert res.top_candidate == "A"
    assert res.fragility["fragile"] is True
    assert res.fragility["deciding_margin"] == 1.0


def test_p4_provenance_downgraded_without_resolvable_source(tmp_path: Path) -> None:
    """P4: Claiming 'computed' without an existing GTO receipt or path stays agent-estimate."""
    cells = {
        "P": {
            "R1": make_cell(10, 0, provenance={"t1_payoff": {"basis": "computed", "source": "GTO-nonexistent"}}),
            "R2": make_cell(20, 0, provenance={"t1_payoff": {"basis": "computed", "source": "nonexistent_file.csv"}}),
        }
    }
    res = adjudicate_wargame(
        policies=["P"],
        red_responses=["R1", "R2"],
        cells=cells,
        baseline_policy="P",
        wealth=1000.0,
    )
    assert res.agent_estimate_share > 0.50
    assert "[LOW GROUNDING" in res.verdict


def test_p5_unverified_independence_class_stamps_theater() -> None:
    """P5: Claiming separate-model without verified run record in wargame_runs.jsonl stamps [THEATER]."""
    cells = {"P": {"R1": make_cell(10, 0)}}
    res = adjudicate_wargame(
        policies=["P"],
        red_responses=["R1"],
        cells=cells,
        baseline_policy="P",
        wealth=1000.0,
        independence_record={"run_id": "RUN-fake", "packet_sha256": "fakehash", "class": "separate-model"},
    )
    assert res.independence_class == "same-context (theater)"
    assert "[THEATER" in res.verdict


def test_p6_counterparty_writes_rules_requires_shock_payoffs() -> None:
    """P6: counterparty_writes_rules=True without shock_payoffs raises ValueError."""
    cells = {"P": {"R1": make_cell(10, 0)}}
    with pytest.raises(ValueError) as exc_info:
        adjudicate_wargame(
            policies=["P"],
            red_responses=["R1"],
            cells=cells,
            baseline_policy="P",
            wealth=1000.0,
            counterparty_writes_rules=True,
            shock_payoffs=None,
        )
    assert "counterparty_writes_rules=True requires shock_payoffs" in str(exc_info.value)


def test_p7_intra_turn_wick_liquidation() -> None:
    """P7: Terminal +100 whose intra-turn path touched -900 on 1000 wealth (barrier 200) liquidates at Turn 1."""
    # wealth=1000, barrier=0.20 -> barrier threshold = 200
    # wealth + t1_worst = 1000 - 900 = 100 <= 200 -> ruined at Turn 1!
    cells = {
        "SHORT_WICK": {
            "R1": make_cell(t1=100.0, t1_worst=-900.0, t2=500.0),
        }
    }
    res = adjudicate_wargame(
        policies=["SHORT_WICK"],
        red_responses=["R1"],
        cells=cells,
        baseline_policy="SHORT_WICK",
        wealth=1000.0,
        barrier=0.20,
    )
    assert "SHORT_WICK" in res.vetoed_policies
    assert res.top_candidate is None
    # Effective payoff is truncated to t1_worst (-900)
    assert res.effective_matrix["SHORT_WICK"]["R1"] == -900.0


def test_p8_decision_receipt_populates_verdict_and_top(tmp_path: Path) -> None:
    """P8: log_decision_receipt logs populated verdict and top_candidate."""
    receipts_file = tmp_path / "decision_receipts.jsonl"
    cells = {
        "A": {"R1": make_cell(10, 0), "R2": make_cell(15, 0)},
        "B": {"R1": make_cell(5, 0), "R2": make_cell(25, 0)},
    }
    res = adjudicate_wargame(
        policies=["A", "B"],
        red_responses=["R1", "R2"],
        cells=cells,
        baseline_policy="A",
        wealth=1000.0,
    )
    payload = {
        "policies": ["A", "B"],
        "red_responses": ["R1", "R2"],
        "cells": cells,
        "baseline_policy": "A",
        "wealth": 1000.0,
    }
    from athena.intelligence.gto_engine import log_decision_receipt
    rec_entry = log_decision_receipt(
        action="wargame",
        inputs=payload,
        result=res,
        receipts_path=receipts_file,
    )
    rec_id = rec_entry["receipt_id"] if isinstance(rec_entry, dict) else str(rec_entry)
    assert rec_id.startswith("GTO-")
    receipt_data = json.loads(receipts_file.read_text(encoding="utf-8").strip())
    assert receipt_data["verdict"] != "N/A"
    assert receipt_data["top"] == "A"


def test_p9_cli_real_flag_kwarg(tmp_path: Path) -> None:
    """P9: CLI --real executes cleanly without TypeError."""
    receipts_file = tmp_path / "decision_receipts.jsonl"
    payload = {
        "policies": ["A"],
        "red_responses": ["R1"],
        "cells": {"A": {"R1": make_cell(10, 0)}},
        "baseline_policy": "A",
        "wealth": 1000.0,
    }
    rc = wargame_main([
        "--input", json.dumps(payload),
        "--real",
        "--receipts-path", str(receipts_file),
    ])
    assert rc == 0
    content = receipts_file.read_text(encoding="utf-8")
    assert '"real_decision": true' in content


def test_p12_tail_factor_compound_ruin() -> None:
    """P12: Compound ruin p=0.0199 scaled by tail_factor 3.0 gives 0.0597 > 0.05, vetoing policy."""
    # p1 = 0.01, p2 = 0.01 -> p_comp = 1 - (0.99*0.99) = 0.0199
    # scaled = 3.0 * 0.0199 = 0.0597 > 0.05 ceiling -> RUIN
    cells = {
        "TAIL_RISK": {
            "R1": make_cell(10, 0, p_ruin_t1=0.01, p_ruin_t2=0.01),
        }
    }
    res = adjudicate_wargame(
        policies=["TAIL_RISK"],
        red_responses=["R1"],
        cells=cells,
        baseline_policy="TAIL_RISK",
        wealth=1000.0,
        tail_factor=3.0,
    )
    assert "TAIL_RISK" in res.vetoed_policies
    assert res.ruin_matrix["TAIL_RISK"]["R1"] is True


def test_p14_matrix_caps_enforced() -> None:
    """P14: Matrix caps enforced (max 6 policies, max 5 responses)."""
    p7 = [f"P{i}" for i in range(7)]
    cells = {p: {"R1": make_cell(10, 0)} for p in p7}
    with pytest.raises(ValueError) as exc:
        adjudicate_wargame(
            policies=p7,
            red_responses=["R1"],
            cells=cells,
            baseline_policy="P0",
            wealth=1000.0,
        )
    assert "Caps exceeded" in str(exc.value)


def test_p15_red_best_response_winner_and_criteria_disagree() -> None:
    """P15: Red Best Response winner reported side-by-side with maximin/regret."""
    # A (50, red=1), A (10, red=0) -> Red BR for A is R1 (blue=50)
    # B (9, red=0), B (500, red=1) -> Red BR for B is R2 (blue=500)
    # Floors: A=10, B=9 -> Maximin winner is A
    # Red BR: Blue payoff at Red BR for A is 50; for B is 500 -> Red BR winner is B!
    cells = {
        "A": {"R1": make_cell(50, 0, red=1.0), "R2": make_cell(10, 0, red=0.0)},
        "B": {"R1": make_cell(9, 0, red=0.0), "R2": make_cell(500, 0, red=1.0)},
    }
    res = adjudicate_wargame(
        policies=["A", "B"],
        red_responses=["R1", "R2"],
        cells=cells,
        baseline_policy="A",
        wealth=1000.0,
    )
    assert res.maximin_winner == "A"
    assert res.red_br_winner == "B"
    assert "CRITERIA DISAGREE" in res.verdict


def test_runner_information_barrier_and_egress(tmp_path: Path) -> None:
    """Runner enforces observable packet schema and blocks forbidden rationale keys."""
    # 1. Banned rationale key raises InformationBarrierViolationError
    with pytest.raises(InformationBarrierViolationError):
        build_observable_packet(
            arena_facts="Facts",
            red_endowments="Endowments",
            blue_observable_moves=[{"action": "quote", "amount": 2500}],
            blue_rationale="We want to build a long term relationship",
        )

    # 2. Valid observable packet builds cleanly
    packet = build_observable_packet(
        arena_facts="Facts",
        red_endowments="Endowments",
        blue_observable_moves=[{"action": "quote", "amount": 2500}],
    )
    assert packet.sha256() is not None

    # 3. Execution with mock responses writes verifiable run record
    runs_file = tmp_path / "wargame_runs.jsonl"
    responses, indep_rec = execute_red_cell(
        packet=packet,
        model="gemini-2.5-flash",
        independence_class="separate-context",
        runs_path=runs_file,
        mock_responses=["Counter 1", "Counter 2"],
    )
    assert responses == ["Counter 1", "Counter 2"]
    assert indep_rec["run_id"].startswith("RUN-")
    assert runs_file.exists()
