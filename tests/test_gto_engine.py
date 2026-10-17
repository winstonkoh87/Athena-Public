"""
Unit tests for athena.intelligence.gto_engine.
Ensures mathematical accuracy, analytical bounds, and ASCII-only output.
"""

import json

import pytest

from athena.intelligence.gto_engine import (
    compute_eev,
    compute_half_kelly,
    compute_ruin_probability,
    main,
    run_monte_carlo_simulation,
)


@pytest.fixture(autouse=True)
def _isolate_gto_receipts(tmp_path, monkeypatch):
    """T3.4: Prevent unit tests from appending to tracked .athena/*.jsonl files."""
    monkeypatch.setenv("ATHENA_RECEIPTS_PATH", str(tmp_path / "decision_receipts.jsonl"))
    monkeypatch.setenv("ATHENA_CAL_LEDGER_PATH", str(tmp_path / "CALIBRATION_LEDGER.md"))


def test_compute_eev_positive_asymmetry():
    res = compute_eev(mev=1000.0, eu=200.0, eo=100.0, skeptic_discount=0.15)
    # raw_ev = 1000 - 300 = 700
    # net_eev = 700 * 0.85 = 595.0
    assert res.raw_ev == 700.0
    assert res.net_eev == pytest.approx(595.0, 0.01)
    assert res.roi_percent > 50.0
    assert "APPROVE" in res.verdict


def test_compute_eev_negative():
    res = compute_eev(mev=200.0, eu=150.0, eo=100.0, skeptic_discount=0.10)
    # raw_ev = 200 - 250 = -50
    # F-04 fix: negative raw_ev is NOT discounted (losses at full face value)
    # net_eev = -50.0 (unchanged — discount only applies to positive EV)
    assert res.raw_ev == -50.0
    assert res.net_eev == -50.0
    assert "REJECT" in res.verdict


def test_compute_half_kelly_positive():
    # 60% win rate with 1.5:1 payoff
    # edge = (0.60 * 1.5) - 0.40 = 0.90 - 0.40 = 0.50
    # f* = 0.50 / 1.5 = 0.3333 (33.33%)
    # half_kelly = 0.1667 (16.67%)
    res = compute_half_kelly(win_rate=0.60, payoff_ratio=1.5, variance_drag=0.5)
    assert res.edge == pytest.approx(0.50, 0.001)
    assert res.full_kelly == pytest.approx(1.0 / 3.0, 0.001)
    assert res.half_kelly == pytest.approx(1.0 / 6.0, 0.001)
    assert "APPROVED" in res.verdict


def test_compute_half_kelly_negative():
    # 40% win rate with 1:1 payoff -> -EV
    res = compute_half_kelly(win_rate=0.40, payoff_ratio=1.0)
    assert res.edge < 0
    assert res.full_kelly == 0.0
    assert res.half_kelly == 0.0
    assert "NO BET" in res.verdict


def test_compute_ruin_probability_safe():
    # 55% win rate, 1.5:1 payoff, 1% risk per trade -> very low ruin
    res = compute_ruin_probability(
        win_rate=0.55,
        payoff_ratio=1.5,
        risk_per_trade_fraction=0.01,
        ruin_drawdown_threshold=0.50,
        trials_for_sim=2000,
        steps_for_sim=100,
    )
    assert res.analytical_ruin_prob < 0.01
    assert res.simulated_ruin_prob < 0.01
    assert "PASS" in res.verdict


def test_compute_ruin_probability_veto():
    # Negative EV or massive position size (25% risk) -> high ruin
    res = compute_ruin_probability(
        win_rate=0.45,
        payoff_ratio=1.0,
        risk_per_trade_fraction=0.25,
        ruin_drawdown_threshold=0.50,
        trials_for_sim=2000,
        steps_for_sim=100,
    )
    assert res.analytical_ruin_prob >= 0.50
    assert "VETO" in res.verdict


def test_run_monte_carlo_simulation():
    res = run_monte_carlo_simulation(
        initial_capital=10000.0,
        win_rate=0.55,
        payoff_ratio=1.5,
        risk_fraction=0.02,
        n_trials=1000,
        n_steps=50,
        seed=42,
    )
    assert res.n_trials == 1000
    assert res.ci_99_lower <= res.ci_95_lower
    assert res.ci_95_lower <= res.median_final_capital
    assert res.median_final_capital <= res.ci_95_upper
    assert res.ci_95_upper <= res.ci_99_upper
    assert 0.0 <= res.mean_max_drawdown_pct <= 100.0


def test_cli_json_and_ascii_no_latex(monkeypatch, capsys):
    # Test JSON mode
    exit_code = main(["--action", "eev", "--mev", "1000", "--eu", "200", "--eo", "100", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["net_eev"] == 595.0

    # Test ASCII table mode (assert no LaTeX delimiters)
    exit_code = main(["--action", "monte-carlo", "--trials", "100", "--steps", "20"])
    assert exit_code == 0
    captured = capsys.readouterr()
    output_text = captured.out
    assert "MONTE CARLO TRAJECTORY SIMULATION" in output_text
    assert "$" not in output_text.replace("S$", "")  # Only S$ allowed, no bare $ math delimiters
    assert "$$" not in output_text
    assert "\\(" not in output_text
    assert "\\[" not in output_text


def test_compute_mcda_stable_winner():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["Speed", "Cost", "Quality"]
    weights = [0.4, 0.3, 0.3]
    scores = {
        "Option A": [5, 5, 5],
        "Option B": [1, 2, 1],
    }
    veto_floors = {"Speed": 1.0, "Cost": 1.0, "Quality": 1.0}
    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict
    assert len(res.perturbation_flips) == 0


def test_compute_mcda_unstable_tie():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Tech Sales", "Cloud/SRE", "AML Compliance", "Commercial Brokerage"]
    criteria = ["C1", "C2", "C3", "C4", "C5"]
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    scores = {
        "Tech Sales": [4, 4, 3, 3, 3],
        "Cloud/SRE": [3, 4, 4, 3, 3],
        "AML Compliance": [3, 3, 4, 4, 3],
        "Commercial Brokerage": [5, 4, 2, 4, 2],
    }
    res = compute_mcda(candidates, criteria, weights, scores)
    assert res.is_stable is False
    assert "UNSTABLE" in res.stability_verdict
    assert "ROUTE TO PATH D" in res.verdict
    assert len(res.perturbation_flips) > 0


def test_cli_mcda_json_and_ascii(capsys):
    mcda_data = {
        "candidates": ["Option A", "Option B"],
        "criteria": ["Speed", "Cost"],
        "weights": [0.6, 0.4],
        "scores": {
            "Option A": [5, 3],
            "Option B": [2, 4],
        },
    }
    json_str = json.dumps(mcda_data)

    # Test ASCII output
    exit_code = main(["--action", "mcda", "--mcda-json", json_str])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MULTIPLE-CRITERIA DECISION ANALYSIS (MCDA) BUNDLE" in captured.out
    assert "Top Candidate             : Option A" in captured.out

    # Test JSON output
    exit_code = main(["--action", "mcda", "--mcda-json", json_str, "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["winner"] == "Option A"


def test_mcda_veto_blocks_ruinous_winner():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["ILLEGAL_BUT_LUCRATIVE", "LEGAL_DEFENSIVE"]
    criteria = ["Profit", "Speed", "MarketShare", "Regulatory"]
    weights = [0.25, 0.25, 0.25, 0.25]
    scores = {
        "ILLEGAL_BUT_LUCRATIVE": [10.0, 10.0, 10.0, 0.0],
        "LEGAL_DEFENSIVE": [6.0, 6.0, 6.0, 10.0],
    }
    veto_floors = {"Regulatory": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "LEGAL_DEFENSIVE"
    assert "ILLEGAL_BUT_LUCRATIVE" in res.vetoed_candidates
    assert res.veto_screen_applied is True
    assert res.is_stable is True
    assert "SOLE FEASIBLE PATH" in res.verdict
    assert "Breached Regulatory floor" in res.vetoed_candidates["ILLEGAL_BUT_LUCRATIVE"][0]


def test_mcda_all_candidates_vetoed():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Bad A", "Bad B"]
    criteria = ["Safety", "Budget"]
    weights = [0.5, 0.5]
    scores = {
        "Bad A": [0.0, 5.0],
        "Bad B": [5.0, 0.0],
    }
    veto_floors = {"Safety": 1.0, "Budget": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "NONE"
    assert res.is_stable is False
    assert "INFEASIBLE" in res.stability_verdict
    assert "NO FEASIBLE PATH" in res.verdict
    assert len(res.vetoed_candidates) == 2


def test_mcda_dominant_winner_is_stable():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Superior", "Inferior"]
    criteria = ["C1", "C2", "C3"]
    weights = [0.34, 0.33, 0.33]
    scores = {
        "Superior": [5.0, 5.0, 5.0],
        "Inferior": [4.9, 4.9, 4.9],  # strictly inferior, margin is ~2.04% < 5%
    }
    veto_floors = {"C1": 1.0, "C2": 1.0, "C3": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Superior"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict
    assert any("strictly dominates" in obs for obs in res.pairwise_dominance)


def test_mcda_single_criterion_stable():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["SingleScore"]
    weights = [1.0]
    scores = {
        "Option A": [9.4],
        "Option B": [9.0],  # 4.44% margin, strictly dominant
    }
    veto_floors = {"SingleScore": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict


def test_mcda_no_screen_is_advisory_only():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["Speed", "Cost"]
    weights = [0.6, 0.4]
    scores = {
        "Option A": [5, 5],
        "Option B": [2, 2],
    }
    # No veto_floors passed
    res = compute_mcda(candidates, criteria, weights, scores)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert res.veto_screen_applied is False
    assert "ADVISORY ONLY (NO VETO SCREEN)" in res.verdict
    assert "DECISION LOCKED" not in res.verdict


def test_ruin_result_violates_law1():
    from athena.intelligence.gto_engine import compute_ruin_probability

    # Safe: win_rate=0.60, payoff=1.5, risk=0.02 -> ruin < 1%
    safe_res = compute_ruin_probability(win_rate=0.60, payoff_ratio=1.5, risk_per_trade_fraction=0.02)
    assert safe_res.violates_law1 is False
    assert "Law #1 Violation (>5% Ruin)  : NO (Ergodic)" in safe_res.to_ascii_table()

    # Dangerous: win_rate=0.45, payoff=1.0, risk=0.10 -> ruin > 5%
    ruin_res = compute_ruin_probability(win_rate=0.45, payoff_ratio=1.0, risk_per_trade_fraction=0.10)
    assert ruin_res.violates_law1 is True
    assert "Law #1 Violation (>5% Ruin)  : YES (HARD VETO)" in ruin_res.to_ascii_table()


def test_gto_screen_without_floors_raises():
    from athena.intelligence.gto_engine import VetoFloorRequired, gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }

    # Calling gto_screen without veto floors MUST raise VetoFloorRequired (fail-closed)
    with pytest.raises(VetoFloorRequired, match="fail-closed and requires active veto_floors"):
        gto_screen(candidates, criteria, weights, scores)

    # Calling with empty dict must also raise
    with pytest.raises(VetoFloorRequired):
        gto_screen(candidates, criteria, weights, scores, veto_floors={})


def test_gto_screen_with_veto_floors_enforces_veto():
    from athena.intelligence.gto_engine import gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }

    # With veto floor on Robustness >= 5.0, PathA is vetoed despite higher raw composite score
    res = gto_screen(
        candidates,
        criteria,
        weights,
        scores,
        veto_floors={"Robustness": 5.0},
    )
    assert res.winner == "PathB_Safe"
    assert res.veto_screen_applied is True
    assert "PathA_Ruin40pct" in res.vetoed_candidates
    assert any("Breached Robustness floor" in b for b in res.vetoed_candidates["PathA_Ruin40pct"])


def test_derive_ruin_floors_and_gto_screen():
    from athena.intelligence.gto_engine import derive_ruin_floors, gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }
    ruin_inputs = {
        "PathA_Ruin40pct": {"win_rate": 0.45, "payoff_ratio": 1.0, "risk_per_trade_fraction": 0.10},
        "PathB_Safe": {"win_rate": 0.60, "payoff_ratio": 1.5, "risk_per_trade_fraction": 0.02},
    }

    # derive_ruin_floors produces floor on Robustness
    floors = derive_ruin_floors(candidates, ruin_inputs, target_criterion="Robustness", floor_value=5.0)
    assert floors == {"Robustness": 5.0}

    # gto_screen auto-derives from ruin_inputs and vetoes PathA
    res = gto_screen(
        candidates,
        criteria,
        weights,
        scores,
        ruin_inputs=ruin_inputs,
        ruin_criterion="Robustness",
        ruin_floor=5.0,
    )
    assert res.winner == "PathB_Safe"
    assert res.veto_screen_applied is True
    assert "PathA_Ruin40pct" in res.vetoed_candidates


def test_cli_require_veto():
    from athena.intelligence.gto_engine import main

    mcda_data = {
        "candidates": ["PathA", "PathB"],
        "criteria": ["Speed", "Robustness"],
        "weights": [0.8, 0.2],
        "scores": {"PathA": [9.0, 1.0], "PathB": [5.0, 8.0]},
    }

    # Without --require-veto, exits 0 (advisory mode)
    exit_code = main(["--action", "mcda", "--mcda-json", json.dumps(mcda_data)])
    assert exit_code == 0

    # With --require-veto but no veto_floors, exits non-zero (fail-closed)
    exit_code_fail = main(["--action", "mcda", "--require-veto", "--mcda-json", json.dumps(mcda_data)])
    assert exit_code_fail != 0

    # With --require-veto and veto_floors, exits 0
    mcda_data_with_veto = dict(mcda_data, veto_floors={"Robustness": 5.0})
    exit_code_vetoed = main(["--action", "mcda", "--require-veto", "--mcda-json", json.dumps(mcda_data_with_veto)])
    assert exit_code_vetoed == 0


def test_compute_dual_vault_barbell():
    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    # Healthy Barbell (90% fortress, 10% arena, 36 months runway)
    res = compute_dual_vault_barbell(fortress_capital=90000.0, arena_capital=10000.0, monthly_burn=2500.0)
    assert res.ruin_violation is False
    assert "PASS" in res.verdict
    assert res.fortress_runway_months == 36.0
    assert abs(res.arena_fraction - 0.10) < 1e-4

    # Ruin violation: arena exceeds 10% ceiling
    res_ruin = compute_dual_vault_barbell(fortress_capital=80000.0, arena_capital=20000.0, monthly_burn=2500.0)
    assert res_ruin.ruin_violation is True
    assert "VETO: Arena allocation" in res_ruin.verdict

    # Ruin violation: runway under 12 months
    res_runway = compute_dual_vault_barbell(fortress_capital=20000.0, arena_capital=2000.0, monthly_burn=2500.0)
    assert res_runway.ruin_violation is True
    assert "VETO: Fortress runway" in res_runway.verdict

    # Table formatting
    table = res.to_ascii_table()
    assert "DUAL-VAULT BARBELL RISK AUDIT" in table
    assert "S$90,000.00" in table


def test_compute_internal_devaluation():
    from athena.intelligence.gto_engine import compute_internal_devaluation

    # Finite expansion
    res = compute_internal_devaluation(
        current_burn=12000.0,
        reduced_burn=4000.0,
        liquid_reserves=48000.0,
        post_shock_income=0.0,
    )
    assert res.boxer_runway_months == 4.0
    assert res.sovereign_runway_months == 12.0
    assert res.runway_expansion_factor == 3.0
    assert res.is_infinite_runway is False
    assert "STABILIZED" in res.verdict

    # Infinite runway when income covers reduced burn
    res_inf = compute_internal_devaluation(
        current_burn=12000.0,
        reduced_burn=3500.0,
        liquid_reserves=50000.0,
        post_shock_income=4000.0,
    )
    assert res_inf.is_infinite_runway is True
    assert "SOVEREIGN ESCAPE" in res_inf.verdict

    # Table formatting
    table = res.to_ascii_table()
    assert "INTERNAL DEVALUATION AUDIT" in table
    assert "3.00x" in table


def test_compute_borrow_vulnerability():
    from athena.intelligence.gto_engine import compute_borrow_vulnerability

    # Safe / Contained (10% exposure, symmetric, gated credit, complete spec)
    res_safe = compute_borrow_vulnerability(
        counterparty_exposure=10000.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=False,
        unhedged_credit=False,
        upstream_spec_complete=True,
    )
    assert res_safe.ruin_violation is False
    assert res_safe.bvi_score == 20.0
    assert "CONTAINED" in res_safe.verdict

    # Critical Vulnerability (>60 score or >15% exposure with freeze power)
    res_crit = compute_borrow_vulnerability(
        counterparty_exposure=25000.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=True,
        unhedged_credit=True,
        upstream_spec_complete=False,
    )
    assert res_crit.ruin_violation is True
    assert res_crit.bvi_score == 100.0
    assert "CRITICAL VULNERABILITY" in res_crit.verdict

    # Table formatting
    table = res_crit.to_ascii_table()
    assert "BORROW VULNERABILITY INDEX" in table
    assert "CRITICAL HAZARD" in table


def test_cli_barbell_and_devaluation():
    from athena.intelligence.gto_engine import main

    assert main(["--action", "barbell", "--fortress", "90000", "--arena", "10000", "--burn", "2500"]) == 0
    assert main(["--action", "devaluation", "--current-burn", "10000", "--reduced-burn", "3000", "--capital", "30000"]) == 0
    assert main(["--action", "borrow-audit", "--exposure", "10000", "--capital", "100000"]) == 0


def test_json_output_barbell():
    """Verify --json output for barbell action produces valid JSON."""
    import io
    import sys

    from athena.intelligence.gto_engine import main

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        rc = main(["--action", "barbell", "--fortress", "90000", "--arena", "10000", "--burn", "2500", "--json"])
    finally:
        sys.stdout = old_stdout
    assert rc == 0
    data = json.loads(captured.getvalue())
    assert data["fortress_capital"] == 90000.0
    assert data["ruin_violation"] is False


def test_json_output_devaluation_infinite_runway():
    """CRITICAL: Verify --json with infinite runway (float('inf')) does not crash."""
    import io
    import sys

    from athena.intelligence.gto_engine import main

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        rc = main([
            "--action", "devaluation",
            "--current-burn", "12000",
            "--reduced-burn", "3500",
            "--capital", "50000",
            "--post-shock-income", "4000",
            "--json",
        ])
    finally:
        sys.stdout = old_stdout
    assert rc == 0
    data = json.loads(captured.getvalue())
    assert data["is_infinite_runway"] is True
    assert data["sovereign_runway_months"] == "Infinity"
    assert data["runway_expansion_factor"] == "Infinity"


def test_json_output_borrow_audit():
    """Verify --json output for borrow-audit action."""
    import io
    import sys

    from athena.intelligence.gto_engine import main

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        rc = main([
            "--action", "borrow-audit",
            "--exposure", "25000",
            "--capital", "100000",
            "--freeze-power",
            "--unhedged-credit",
            "--json",
        ])
    finally:
        sys.stdout = old_stdout
    assert rc == 0
    data = json.loads(captured.getvalue())
    assert data["ruin_violation"] is True
    assert data["bvi_score"] == 90.0


def test_serialize_for_json_handles_inf_and_nan():
    """Unit test for the _serialize_for_json helper."""
    from athena.intelligence.gto_engine import _serialize_for_json

    d = {
        "a": float("inf"),
        "b": float("-inf"),
        "c": float("nan"),
        "d": 42.0,
        "e": "hello",
        "f": True,
        "g": {"nested_inf": float("inf"), "normal": 1.0},
    }
    result = _serialize_for_json(d)
    assert result["a"] == "Infinity"
    assert result["b"] == "-Infinity"
    assert result["c"] == "NaN"
    assert result["d"] == 42.0
    assert result["e"] == "hello"
    assert result["f"] is True
    assert result["g"]["nested_inf"] == "Infinity"
    assert result["g"]["normal"] == 1.0


# =====================================================================
# Phase 0 Boundary & Mutation Hardening (F3, F4, T0.1, T0.2, T0.3, T0.4)
# =====================================================================


def test_compute_dual_vault_barbell_exact_10_pct_passes():
    """Verify that arena allocation at exactly 10.0% passes (inclusive ceiling)."""
    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    res = compute_dual_vault_barbell(
        fortress_capital=90000.0,
        arena_capital=10000.0,
        monthly_burn=2500.0,
    )
    assert res.arena_fraction == 0.10
    assert res.fortress_runway_months == 36.0
    assert res.ruin_violation is False
    assert "PASS" in res.verdict


def test_compute_dual_vault_barbell_11_pct_vetoes_kills_b1():
    """Verify veto when arena allocation is 11.0% (between 10% and 15%, kills mutant B1)."""
    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    res = compute_dual_vault_barbell(
        fortress_capital=89000.0,
        arena_capital=11000.0,
        monthly_burn=2500.0,
    )
    assert res.arena_fraction == 0.11
    assert res.ruin_violation is True
    assert "VETO: Arena allocation" in res.verdict
    assert "exceeds 10.0% ceiling" in res.verdict


def test_compute_dual_vault_barbell_exact_12mo_runway_passes():
    """Verify that fortress runway at exactly 12.0 months passes."""
    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    res = compute_dual_vault_barbell(
        fortress_capital=30000.0,
        arena_capital=3000.0,
        monthly_burn=2500.0,
    )
    assert res.fortress_runway_months == 12.0
    assert res.ruin_violation is False
    assert "PASS" in res.verdict


def test_compute_dual_vault_barbell_11mo_runway_vetoes_kills_b2():
    """Verify veto when fortress runway is 11.0 months (between 9 and 12 months, kills mutant B2)."""
    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    res = compute_dual_vault_barbell(
        fortress_capital=27500.0,
        arena_capital=2500.0,
        monthly_burn=2500.0,
    )
    assert res.fortress_runway_months == 11.0
    assert res.ruin_violation is True
    assert "VETO: Fortress runway" in res.verdict
    assert "under 12.0 mo buffer" in res.verdict


def test_compute_borrow_vulnerability_exact_60_score_vetoes_kills_v1():
    """Verify veto when BVI score is exactly 60.0 (kills mutant V1)."""
    from athena.intelligence.gto_engine import compute_borrow_vulnerability

    res = compute_borrow_vulnerability(
        counterparty_exposure=12500.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=False,
        unhedged_credit=True,
        upstream_spec_complete=False,
    )
    assert res.exposure_pct == 12.5
    assert res.bvi_score == 60.0
    assert res.ruin_violation is True
    assert "CRITICAL VULNERABILITY" in res.verdict


def test_compute_borrow_vulnerability_59_score_passes_veto():
    """Verify that BVI score 59.0 does not trigger Law #1 veto without freeze power."""
    from athena.intelligence.gto_engine import compute_borrow_vulnerability

    res = compute_borrow_vulnerability(
        counterparty_exposure=12000.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=False,
        unhedged_credit=True,
        upstream_spec_complete=False,
    )
    assert res.exposure_pct == 12.0
    assert res.bvi_score == 59.0
    assert res.ruin_violation is False
    assert "ELEVATED FRICTION" in res.verdict


def test_compute_borrow_vulnerability_freeze_power_16_pct_vetoes_kills_v2_v3():
    """Verify freeze power veto at 16.0% exposure with score 57.0 < 60.0 (kills mutants V2 and V3)."""
    from athena.intelligence.gto_engine import compute_borrow_vulnerability

    res = compute_borrow_vulnerability(
        counterparty_exposure=16000.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=True,
        unhedged_credit=False,
        upstream_spec_complete=True,
    )
    assert res.exposure_pct == 16.0
    assert res.bvi_score == 57.0
    assert res.ruin_violation is True
    assert "CRITICAL VULNERABILITY" in res.verdict


def test_compute_borrow_vulnerability_freeze_power_exact_15_pct_passes_veto():
    """Verify that 15.0% exposure with freeze power passes Law #1 veto (boundary inclusive)."""
    from athena.intelligence.gto_engine import compute_borrow_vulnerability

    res = compute_borrow_vulnerability(
        counterparty_exposure=15000.0,
        total_net_worth=100000.0,
        unilateral_freeze_power=True,
        unhedged_credit=False,
        upstream_spec_complete=True,
    )
    assert res.exposure_pct == 15.0
    assert res.bvi_score == 55.0
    assert res.ruin_violation is False
    assert "ELEVATED FRICTION" in res.verdict


def test_compute_internal_devaluation_with_income_kills_d1():
    """Verify boxer runway calculation accounts for post-shock income (kills mutant D1)."""
    from athena.intelligence.gto_engine import compute_internal_devaluation

    res = compute_internal_devaluation(
        current_burn=10000.0,
        reduced_burn=5000.0,
        liquid_reserves=50000.0,
        post_shock_income=2000.0,
    )
    assert res.boxer_runway_months == pytest.approx(6.25, 0.001)
    assert res.sovereign_runway_months == pytest.approx(16.6667, 0.001)
    assert res.runway_expansion_factor == pytest.approx(2.6667, 0.001)
    assert res.is_infinite_runway is False
    assert "STABILIZED" in res.verdict


def test_compute_dual_vault_barbell_decorative_parameters_warn():
    """Verify that non-default decorative parameters trigger DeprecationWarning (T0.3)."""
    import pytest

    from athena.intelligence.gto_engine import compute_dual_vault_barbell

    with pytest.deprecated_call():
        compute_dual_vault_barbell(100000.0, 10000.0, 2500.0, expected_arena_return=0.35)

    with pytest.deprecated_call():
        compute_dual_vault_barbell(100000.0, 10000.0, 2500.0, catastrophic_arena_loss_pct=0.80)


def test_cli_fail_closed_barbell():
    """Verify CLI exits 2 with error when balance flags are omitted for barbell (T0.1, F3)."""
    from athena.intelligence.gto_engine import main

    rc = main(["--action", "barbell"])
    assert rc == 2


def test_cli_fail_closed_devaluation():
    """Verify CLI exits 2 with error when flags are omitted for devaluation (T0.1)."""
    from athena.intelligence.gto_engine import main

    rc = main(["--action", "devaluation"])
    assert rc == 2


def test_cli_fail_closed_borrow_audit():
    """Verify CLI exits 2 with error when flags are omitted for borrow-audit (T0.1)."""
    from athena.intelligence.gto_engine import main

    rc = main(["--action", "borrow-audit"])
    assert rc == 2


def test_cli_flags_liquid_reserves_and_net_worth():
    """Verify --liquid-reserves and --net-worth flags work as first-class citizens (T0.1)."""
    from athena.intelligence.gto_engine import main

    rc_dev = main([
        "--action", "devaluation",
        "--current-burn", "10000",
        "--reduced-burn", "3000",
        "--liquid-reserves", "30000",
    ])
    assert rc_dev == 0

    rc_borrow = main([
        "--action", "borrow-audit",
        "--exposure", "10000",
        "--net-worth", "100000",
    ])
    assert rc_borrow == 0


def test_compute_robustness_unscreened_disclosure():
    """T2.1: compute_robustness discloses when ruin was not screened (Mutants M1, M2)."""
    from athena.intelligence.gto_engine import compute_robustness

    p = ["A_all_in", "B_hedged"]
    s = ["cooperate", "defect"]
    pay = {"A_all_in": {"cooperate": 100.0, "defect": -50.0}, "B_hedged": {"cooperate": 10.0, "defect": 0.0}}

    # When ruin is None: ruin_screened is False, marker appended
    res = compute_robustness(p, s, pay)
    assert res.ruin_screened is False
    assert "[UNSCREENED: no ruin labels; Law #1 not applied]" in res.verdict
    assert "[UNSCREENED: no ruin labels; Law #1 not applied]" in res.to_ascii_table()
    assert res.minimax_regret_winner == "A_all_in"

    # When ruin is supplied: ruin_screened is True, marker absent
    res_screened = compute_robustness(p, s, pay, ruin={"A_all_in": {"defect": True}})
    assert res_screened.ruin_screened is True
    assert "[UNSCREENED" not in res_screened.verdict
    assert res_screened.minimax_regret_winner == "B_hedged"


def test_compute_robustness_computed_ruin():
    """T2.2: Computed ruin when wealth is known (Mutants M3, M4, M5)."""
    import pytest

    from athena.intelligence.gto_engine import compute_robustness

    p = ["A_all_in", "B_hedged"]
    s = ["cooperate", "defect"]
    pay = {"A_all_in": {"cooperate": 100.0, "defect": -50.0}, "B_hedged": {"cooperate": 10.0, "defect": 0.0}}

    # Probe A1 / Mutant M5: wealth=50.0 makes A_all_in infeasible in defect scenario (50 + -50 <= 0.0)
    res = compute_robustness(p, s, pay, wealth=50.0)
    assert res.ruin_screened is True
    assert res.feasible_policies == ["B_hedged"]
    assert res.infeasible_policies == ["A_all_in"]
    assert res.minimax_regret_winner == "B_hedged"
    assert "[UNSCREENED" not in res.verdict

    # Mutant M3: exact wipeout boundary condition (wealth + payoff == barrier * wealth)
    # wealth=50.0, payoff=-50.0, barrier=0.0 -> exact wipeout must be ruin
    assert res.policy_stats["A_all_in"].is_feasible is False

    # Mutant M4: explicit label False must NOT override computed ruin (OR semantics)
    res_label_override = compute_robustness(
        p, s, pay,
        wealth=50.0,
        ruin={"A_all_in": {"defect": False}},
    )
    assert res_label_override.feasible_policies == ["B_hedged"]
    assert res_label_override.infeasible_policies == ["A_all_in"]

    # Parameter validation
    with pytest.raises(ValueError, match="wealth must be a positive finite number"):
        compute_robustness(p, s, pay, wealth=0.0)
    with pytest.raises(ValueError, match="wealth must be a positive finite number"):
        compute_robustness(p, s, pay, wealth=-10.0)
    with pytest.raises(ValueError, match="barrier cannot be lowered below 0.0"):
        compute_robustness(p, s, pay, wealth=50.0, barrier=-0.1)


def test_unreceipted_claim_patterns_widened():
    """T2.4: UNRECEIPTED_CLAIM_PATTERNS catches survival guarantees and P(ruin) claims (Mutants M8, M9)."""
    from pathlib import Path

    from athena.intelligence.gto_engine import find_unreceipted_engine_claims

    # Mutant M8: catches guarantee survival phrasing
    t_survival = "It selects the path while strictly guaranteeing survival under defection."
    claims_survival = find_unreceipted_engine_claims(t_survival, Path("/nonexistent"))
    assert any("guaranteeing survival" in c for c in claims_survival)

    # Mutant M9: catches P(ruin) <= X% phrasing
    t_pruin = "Maximum regret bounded, P(ruin) <= 5% under adversarial stress."
    claims_pruin = find_unreceipted_engine_claims(t_pruin, Path("/nonexistent"))
    assert any("P(ruin) <= 5%" in c for c in claims_pruin)

    # Catches unicode <= and fractions
    t_pruin_unicode = "We verify P(ruin) ≤ 2.5% strictly."
    claims_unicode = find_unreceipted_engine_claims(t_pruin_unicode, Path("/nonexistent"))
    assert any("P(ruin) ≤ 2.5%" in c for c in claims_unicode)

    # Probe A3 excerpt test
    excerpt = (
        "It selects the path that yields strong upside if the opponent cooperates, "
        "while strictly guaranteeing survival (maximum regret bounded, `P(ruin) <= 5%`) "
        "if the opponent plays an adversarial defection strategy.\n"
        "A strategy that scores 10/10 on financial upside but carries a >5% probability of "
        "non-ergodic ruin is hard-vetoed under Law #1."
    )
    claims_excerpt = find_unreceipted_engine_claims(excerpt, Path("/nonexistent"))
    assert "guaranteeing survival" in claims_excerpt
    assert "P(ruin) <= 5%" in claims_excerpt
    assert "hard-vetoed" in claims_excerpt






