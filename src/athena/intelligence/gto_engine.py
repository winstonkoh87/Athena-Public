"""
athena.intelligence.gto_engine
==============================

Deterministic Python numerical computation engine for Game-Theory Optimal (GTO)
decision-making, risk modeling, and capital allocation.

Zero external dependencies: uses Python standard library only.
Strictly emits ASCII-only formatting (no LaTeX delimiters).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

LAW1_MAX_RUIN: float = 0.05

# Asserted thresholds (CS-676 §6, not calibrated; user decision D2)
ARENA_MAX_FRACTION: float = 0.10
FORTRESS_MIN_RUNWAY_MONTHS: float = 12.0
BVI_RUIN_SCORE: float = 60.0
BVI_FREEZE_EXPOSURE_PCT: float = 15.0

__all__ = [
    "compute_eev",
    "compute_half_kelly",
    "compute_ruin_probability",
    "run_monte_carlo_simulation",
    "run_decision_monte_carlo",
    "compute_growth_rate",
    "compute_robustness",
    "compute_mcda",
    "derive_ruin_floors",
    "screen_ruin",
    "gto_screen",
    "compute_dual_vault_barbell",
    "compute_internal_devaluation",
    "compute_borrow_vulnerability",
    "log_decision_receipt",
    "execute_decision_action",
    "find_unreceipted_engine_claims",
    "get_receipts_path",
]

CAPABILITY_MANIFEST: dict[str, dict[str, Any]] = {
    "decision_screen": {
        "computes": "Unified strategic decision evaluation with verified decision receipt logging",
        "typed_inputs": ["action", "payload", "real", "review_date", "prediction"],
        "defaults": {"real": False, "review_date": None, "prediction": None},
        "does_not": ["unverified subjective claims"],
    },
    "execute_decision_action": {
        "computes": "Execution of GTO calculation actions with verified decision receipt logging",
        "typed_inputs": ["action", "payload", "real", "review_date", "prediction", "no_receipt", "receipts_path", "cal_ledger_path"],
        "defaults": {"real": False, "review_date": None, "prediction": None, "no_receipt": False, "cal_ledger_path": None},
        "does_not": ["uncalibrated claims", "unverified predictions"],
    },
    "log_decision_receipt": {
        "computes": "Append verified decision receipt with SHA-256 digest to decision_receipts.jsonl",
        "typed_inputs": ["action", "inputs", "result", "receipts_path", "real_decision", "review_date", "prediction", "cal_ledger_path"],
        "defaults": {"real_decision": False, "review_date": None, "prediction": None, "cal_ledger_path": None},
        "does_not": ["in-place mutation of existing receipts (append-only)"],
    },
    "find_unreceipted_engine_claims": {
        "computes": "Scan text for GTO assertions lacking a valid receipt ID or [agent-estimate] tag",
        "typed_inputs": ["text", "receipts_path"],
        "defaults": {},
        "does_not": ["arbitrary semantic validation"],
    },
    "get_receipts_path": {
        "computes": "Discovery of canonical path to decision_receipts.jsonl with environment overrides",
        "typed_inputs": [],
        "defaults": {},
        "does_not": ["network storage resolution"],
    },
    "compute_eev": {
        "computes": "Monetary Expected Value (MEV), Execution Drag (EU), Opportunity Cost (EO), and Net EEV",
        "typed_inputs": ["mev", "eu", "eo", "discount", "utility"],
        "defaults": {"discount": 0.15, "utility": 0.0},
        "does_not": ["multi-criteria scoring", "ruin probability calculation", "stochastic simulation"],
    },
    "compute_half_kelly": {
        "computes": "Full Kelly fraction, Half-Kelly fraction, and ruin-capped fraction",
        "typed_inputs": ["win_rate", "payoff", "max_ruin_pct", "drawdown_fraction"],
        "defaults": {"max_ruin_pct": 0.05, "drawdown_fraction": 0.50},
        "does_not": ["non-binary payoffs", "time-dependent risk", "parameter estimation error"],
    },
    "compute_ruin_probability": {
        "computes": "Analytical ruin probability via characteristic root under discrete repeated bets",
        "typed_inputs": ["win_rate", "payoff", "risk_fraction", "ruin_threshold"],
        "defaults": {"variance_drag": 0.50},
        "does_not": ["path-dependent drawdowns", "regime shifts", "continuous jump-diffusion"],
    },
    "compute_growth_rate": {
        "computes": "Expected log-wealth growth rate (time-average ergodicity) across states",
        "typed_inputs": ["wealth", "states"],
        "defaults": {},
        "does_not": ["continuous-time jump processes", "path-dependent correlation"],
    },
    "compute_robustness": {
        "computes": "Minimax regret, Maximin floor, EV, and CVaR tail risk across scenario matrix",
        "typed_inputs": ["policies", "scenarios", "payoff", "ruin", "probs", "cvar_alpha", "tail_factor"],
        "defaults": {"cvar_alpha": 0.10, "tail_factor": 3.0, "LAW1_MAX_RUIN": 0.05},
        "does_not": ["infinite scenario sets", "continuous state distributions", "endogenous probability reaction"],
    },
    "run_monte_carlo_simulation": {
        "computes": "Bankroll trajectory simulation with discrete left-tail shock modeling",
        "typed_inputs": ["capital", "trials", "steps", "win_rate", "payoff", "risk_fraction", "shock_prob", "shock_loss"],
        "defaults": {"trials": 10000, "steps": 100, "shock_prob": 0.01, "shock_loss": 0.10},
        "does_not": ["multi-asset portfolio covariance", "regime shifts", "continuous time dynamics"],
    },
    "run_decision_monte_carlo": {
        "computes": "Sensitivity analysis, growth-rate ranking, and outcome sampling of candidate decisions",
        "typed_inputs": ["candidates", "states", "is_ruin (boolean flag)", "n", "prob_jitter", "wealth", "materiality", "barrier", "sample_outcomes", "tail_uncertainty"],
        "defaults": {"n": 2000, "prob_jitter": 0.20, "LAW1_MAX_RUIN": 0.05, "materiality": 0.01, "barrier": 0.0, "sample_outcomes": False, "tail_uncertainty": 1.0},
        "does_not": [
            "sample outcomes by default (optional parameter sample_outcomes=False)",
            "fat tails",
            "jump-diffusion",
            "minimax regret",
            "Pareto frontier",
        ],
    },
    "compute_mcda": {
        "computes": "Multi-Criteria Decision Analysis with linear normalization and weighted summation",
        "typed_inputs": ["candidates", "criteria", "weights", "scores", "veto_floors"],
        "defaults": {"LAW1_MAX_RUIN": 0.05},
        "does_not": ["non-linear utility interactions", "probabilistic criteria", "adversarial counter-play"],
    },
    "derive_ruin_floors": {
        "computes": "Deterministic ruin floor calculation for MCDA constraint integration (deprecated)",
        "typed_inputs": ["candidates", "ruin_inputs", "target_criterion", "floor_value"],
        "defaults": {"floor_value": 5.0},
        "does_not": ["direct probability evaluation (use screen_ruin)"],
    },
    "screen_ruin": {
        "computes": "Hard Law #1 ruin filter checking whether declared ruin probability exceeds 5%",
        "typed_inputs": ["candidates", "ruin_estimates (p_ruin, horizon, basis)"],
        "defaults": {"LAW1_MAX_RUIN": 0.05},
        "does_not": [
            "infer unflagged catastrophic wealth loss (requires caller-provided estimate)",
            "guarantee 0.00% empirical ruin in finite samples",
        ],
    },
    "gto_screen": {
        "computes": "Integrated fail-closed screening combining Law #1 ruin veto and MCDA ranking",
        "typed_inputs": ["candidates", "criteria", "weights", "scores", "ruin_estimates", "veto_floors"],
        "defaults": {"LAW1_MAX_RUIN": 0.05},
        "does_not": ["causal DAG modeling", "open system equilibrium solving"],
    },
    "compute_dual_vault_barbell": {
        "computes": "Runway and allocation metrics for Fortress (DBU) vs Arena (ACU) vaults",
        "typed_inputs": ["fortress_capital", "arena_capital", "monthly_burn"],
        "defaults": {"FORTRESS_MIN_RUNWAY_MONTHS": 12.0, "ARENA_MAX_FRACTION": 0.10},
        "does_not": ["yield compounding", "dynamic asset correlation"],
    },
    "compute_internal_devaluation": {
        "computes": "Runway extension and burn reduction ratio from cost deflation",
        "typed_inputs": ["current_burn", "reduced_burn", "liquid_reserves", "post_shock_income"],
        "defaults": {"post_shock_income": 0.0},
        "does_not": ["inflation adjustment", "revenue price elasticity"],
    },
    "compute_borrow_vulnerability": {
        "computes": "Exposure and vulnerability score for third-party borrowed capital / platform custody",
        "typed_inputs": ["exposure_amount", "net_worth"],
        "defaults": {"BVI_RUIN_SCORE": 60.0, "BVI_FREEZE_EXPOSURE_PCT": 15.0},
        "does_not": ["liquidation cascade simulation", "broker margin call latency"],
    },
}



@dataclass
class RuinEstimate:
    p_ruin: float
    horizon: str
    basis: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.p_ruin <= 1.0):
            raise ValueError("p_ruin must be between 0.0 and 1.0")
        if not self.horizon or not self.horizon.strip():
            raise ValueError("horizon must be specified and non-empty")
        if self.basis not in {"computed", "base-rate", "agent-estimate"}:
            raise ValueError(
                f"basis must be one of {{'computed', 'base-rate', 'agent-estimate'}}, got '{self.basis}'"
            )


@dataclass
class EEVResult:
    mev: float
    eu: float
    eo: float
    skeptic_discount: float
    raw_ev: float
    net_eev: float
    roi_percent: float
    verdict: str
    utility: float = 0.0

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "           ECONOMIC EXPECTED VALUE (EEV) AUDIT              ",
            "============================================================",
            f"  Gross Monetary EV (MEV)       : S${self.mev:,.2f}",
            f"  Expected Utility Term E(U)    : S${self.utility:,.2f}",
            f"  Execution & Friction Drag (EU): S${self.eu:,.2f}",
            f"  Opportunity & Focus Cost (EO) : S${self.eo:,.2f}",
            f"  Skeptic / Bias Discount       : {self.skeptic_discount * 100:.1f}%",
            "------------------------------------------------------------",
            f"  Raw Net Expectancy            : S${self.raw_ev:,.2f}",
            f"  Final Payoff-Weighted EEV     : S${self.net_eev:,.2f}",
            f"  Net ROI on Committed Drag     : {self.roi_percent:+.1f}%",
            f"  Strategic Verdict             : {self.verdict}",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class KellyResult:
    win_rate: float
    payoff_ratio: float
    edge: float
    full_kelly: float
    half_kelly: float
    quarter_kelly: float
    recommended_fraction: float
    verdict: str
    ruin_capped_fraction: float = 0.0

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "             KELLY CRITERION SIZING REPORT                  ",
            "============================================================",
            f"  Win Rate (p)                  : {self.win_rate * 100:.1f}%",
            f"  Payoff Ratio (b = Win/Loss)   : {self.payoff_ratio:.2f}:1",
            f"  Net Mathematical Edge         : {self.edge * 100:+.2f}%",
            "------------------------------------------------------------",
            f"  Full Kelly Fraction (f*)      : {self.full_kelly * 100:.2f}%",
            f"  Half-Kelly (Standard GTO)     : {self.half_kelly * 100:.2f}%",
            f"  Quarter-Kelly (Conservative)  : {self.quarter_kelly * 100:.2f}%",
            f"  Ruin-Capped Limit (Law #1)    : {self.ruin_capped_fraction * 100:.2f}%",
            f"  Recommended Position Sizing   : {self.recommended_fraction * 100:.2f}%",
            f"  Execution Verdict             : {self.verdict}",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class RuinResult:
    win_rate: float
    payoff_ratio: float
    risk_per_trade_fraction: float
    ruin_drawdown_threshold: float
    analytical_ruin_prob: float
    simulated_ruin_prob: float
    verdict: str
    violates_law1: bool = False

    def __post_init__(self) -> None:
        self.violates_law1 = self.violates_law1 or (self.conservative_ruin_pct > (LAW1_MAX_RUIN * 100.0))

    @property
    def conservative_ruin_pct(self) -> float:
        return max(self.simulated_ruin_prob, self.analytical_ruin_prob) * 100.0

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "             LAW OF RUIN (LAW #1) RISK AUDIT                ",
            "============================================================",
            f"  Win Rate                      : {self.win_rate * 100:.1f}%",
            f"  Payoff Ratio                  : {self.payoff_ratio:.2f}:1",
            f"  Risk Per Trade (Fraction)     : {self.risk_per_trade_fraction * 100:.2f}%",
            f"  Ruin Threshold (Drawdown)     : -{self.ruin_drawdown_threshold * 100:.1f}%",
            "------------------------------------------------------------",
            f"  Analytical Ruin Probability   : {self.analytical_ruin_prob * 100:.4f}%",
            f"  Empirical Simulated Ruin Rate : {self.simulated_ruin_prob * 100:.4f}%",
            f"  Survival Gate Verdict         : {self.verdict}",
            f"  Law #1 Violation (>5% Ruin)  : {'YES (HARD VETO)' if self.violates_law1 else 'NO (Ergodic)'}",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class MonteCarloResult:
    n_trials: int
    n_steps: int
    initial_capital: float
    mean_final_capital: float
    median_final_capital: float
    ci_95_lower: float
    ci_95_upper: float
    ci_99_lower: float
    ci_99_upper: float
    mean_max_drawdown_pct: float
    worst_drawdown_pct: float
    ruin_probability_pct: float
    growth_rate_geometric_mean: float

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            f"       MONTE CARLO TRAJECTORY SIMULATION (N={self.n_trials:,})       ",
            "============================================================",
            f"  Simulation Steps per Trial    : {self.n_steps}",
            f"  Initial Bankroll              : S${self.initial_capital:,.2f}",
            "------------------------------------------------------------",
            f"  Mean Final Capital            : S${self.mean_final_capital:,.2f}",
            f"  Median Final Capital          : S${self.median_final_capital:,.2f}",
            f"  Geometric Mean Growth Rate    : {self.growth_rate_geometric_mean * 100:+.2f}% / step",
            f"  95% Prediction Interval       : [S${self.ci_95_lower:,.2f}, S${self.ci_95_upper:,.2f}]",
            f"  99% Prediction Interval       : [S${self.ci_99_lower:,.2f}, S${self.ci_99_upper:,.2f}]",
            "------------------------------------------------------------",
            f"  Mean Max Drawdown             : -{self.mean_max_drawdown_pct:.1f}%",
            f"  99th Pct Max Drawdown         : -{self.worst_drawdown_pct:.1f}%",
            f"  Ruin Probability (< -50% DD)  : {self.ruin_probability_pct:.2f}%",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class CandidateSimulationStats:
    candidate: str
    win_frequency_pct: float
    pct_eev_positive: float
    pct_ruin: float
    median_eev: float
    mean_eev: float
    p10_eev: float
    p90_eev: float
    ruin_gate_passed: bool
    verdict: str
    median_growth: float | None = None
    mean_growth: float | None = None
    ruin_source: dict[str, int] = field(default_factory=lambda: {"typed": 0, "computed": 0})
    outcome_p10: float | None = None
    outcome_p90: float | None = None
    realized_ruin_pct: float | None = None


@dataclass
class DecisionMonteCarloResult:
    n_trials: int
    candidates: list[str]
    winner_frequencies: dict[str, float]
    candidate_stats: dict[str, CandidateSimulationStats]
    top_candidate: str
    seed: int | None = None
    vetoed_candidates: list[str] = field(default_factory=list)
    ranking_metric: str = "EEV"

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            f"       DECISION MONTE CARLO SIMULATION (N={self.n_trials:,})       ",
            "============================================================",
            f"  Top Candidate                 : {self.top_candidate} ({self.winner_frequencies.get(self.top_candidate, 0.0):.1f}% win rate)",
            f"  Ranking Metric                : {self.ranking_metric}",
            "------------------------------------------------------------",
            f"  {'CANDIDATE':<20} | {'WIN %':<7} | {'% EEV>0':<8} | {'% RUIN':<7} | {'MEDIAN':<10} | {'P10':<10} | VERDICT",
            "------------------------------------------------------------",
        ]
        for cand, stats in self.candidate_stats.items():
            lines.append(
                f"  {cand:<20} | {stats.win_frequency_pct:>6.1f}% | {stats.pct_eev_positive:>7.1f}% | "
                f"{stats.pct_ruin:>6.2f}% | S${stats.median_eev:>8.2f} | S${stats.p10_eev:>8.2f} | {stats.verdict}"
            )
        if self.vetoed_candidates:
            lines.extend([
                "------------------------------------------------------------",
                f"  VETOED CANDIDATES (Law #1 Ruin > {LAW1_MAX_RUIN * 100:.1f}%):",
            ])
            for cand in self.vetoed_candidates:
                lines.append(f"    [VETO] {cand}")
        lines.append("============================================================")
        return "\n".join(lines)


@dataclass
class PolicyRobustnessStats:
    policy: str
    is_feasible: bool
    worst_outcome: float
    max_regret: float
    expected_payoff: float | None = None
    expected_regret: float | None = None
    cvar_alpha: float | None = None
    p_ruin_scaled: float = 0.0


@dataclass
class RobustnessResult:
    policies: list[str]
    scenarios: list[str]
    feasible_policies: list[str]
    infeasible_policies: list[str]
    benchmarks: dict[str, float]
    policy_stats: dict[str, PolicyRobustnessStats]
    minimax_regret_winner: str
    maximin_winner: str
    ev_winner: str | None
    verdict: str
    is_iia_sensitive: bool = False
    ruin_screened: bool = True

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "         SCENARIO-MATRIX ROBUSTNESS ANALYSIS (GTO)          ",
            "============================================================",
            f"  Minimax Regret Winner : {self.minimax_regret_winner}",
            f"  Maximin Winner (Floor): {self.maximin_winner}",
        ]
        if self.ev_winner is not None:
            lines.append(f"  EV Winner             : {self.ev_winner}")
        lines.extend([
            f"  Strategic Verdict     : {self.verdict}",
            "------------------------------------------------------------",
            f"  {'POLICY':<16} | {'STATUS':<10} | {'WORST':<8} | {'MAX REGRET':<10} | {'EV':<8} | {'CVaR':<8}",
            "------------------------------------------------------------",
        ])
        for pol, stats in self.policy_stats.items():
            status = "FEASIBLE" if stats.is_feasible else "INFEASIBLE"
            ev_str = f"{stats.expected_payoff:.2f}" if stats.expected_payoff is not None else "N/A"
            cvar_str = f"{stats.cvar_alpha:.2f}" if stats.cvar_alpha is not None else "N/A"
            lines.append(
                f"  {pol:<16} | {status:<10} | {stats.worst_outcome:>8.2f} | {stats.max_regret:>10.2f} | {ev_str:>8} | {cvar_str:>8}"
            )
        lines.append("============================================================")
        return "\n".join(lines)


@dataclass
class MCDAResult:
    candidates: list[str]
    criteria: list[str]
    normalized_weights: dict[str, float]
    composite_scores: dict[str, float]
    ranked_candidates: list[tuple[str, float]]
    winner: str
    runner_up: str
    margin_abs: float
    margin_pct: float
    is_stable: bool
    stability_verdict: str
    perturbation_flips: list[str]
    pairwise_dominance: list[str]
    verdict: str
    vetoed_candidates: dict[str, list[str]] = field(default_factory=dict)
    veto_screen_applied: bool = False
    ruin_exemptions: dict[str, str] = field(default_factory=dict)

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "       MULTIPLE-CRITERIA DECISION ANALYSIS (MCDA) BUNDLE   ",
            "============================================================",
            f"  Top Candidate             : {self.winner} (Score: {self.composite_scores.get(self.winner, 0.0):.3f})",
            f"  Runner-Up                 : {self.runner_up} (Score: {self.composite_scores.get(self.runner_up, 0.0):.3f})",
            f"  Winning Margin            : +{self.margin_abs:.3f} (+{self.margin_pct:.1f}%)",
            f"  Sensitivity (±10% Weights): {self.stability_verdict}",
            f"  Strategic Verdict         : {self.verdict}",
        ]
        if not self.veto_screen_applied:
            lines.append("  ⚠ WARNING                 : NO HARD-CONSTRAINT SCREEN APPLIED (DEC-500 §3A SKIPPED)")
        lines.extend([
            "------------------------------------------------------------",
            "  RANKED COMPOSITE SCORES:",
        ])
        for rank, (cand, score) in enumerate(self.ranked_candidates, 1):
            lines.append(f"    {rank}. {cand:<30} : {score:.3f}")

        if self.vetoed_candidates:
            lines.extend([
                "------------------------------------------------------------",
                "  VETOED CANDIDATES (DEC-500 §3A HARD-CONSTRAINT VETO):",
            ])
            for cand, breaches in self.vetoed_candidates.items():
                breaches_str = "; ".join(breaches)
                lines.append(f"    [VETO] {cand:<23} : {breaches_str}")

        if self.ruin_exemptions:
            lines.extend([
                "------------------------------------------------------------",
                "  RUIN EXEMPTIONS (NOT SCREENED):",
            ])
            for cand, reason in self.ruin_exemptions.items():
                lines.append(f"    [EXEMPT] {cand:<21} : {reason}")

        lines.extend([
            "------------------------------------------------------------",
            "  NORMALIZED CRITERIA WEIGHTS:",
        ])
        for crit, w in self.normalized_weights.items():
            lines.append(f"    {crit:<25} : {w * 100:.1f}%")

        if self.pairwise_dominance:
            lines.extend([
                "------------------------------------------------------------",
                "  PAIRWISE DOMINANCE OBSERVATIONS:",
            ])
            for obs in self.pairwise_dominance:
                lines.append(f"    - {obs}")

        if self.perturbation_flips:
            lines.extend([
                "------------------------------------------------------------",
                "  PERTURBATION FLIPS (±10% WEIGHT DRIFT):",
            ])
            for flip in self.perturbation_flips:
                lines.append(f"    ! {flip}")

        lines.append("============================================================")
        return "\n".join(lines)


@dataclass
class BarbellAuditResult:
    fortress_capital: float
    arena_capital: float
    total_capital: float
    arena_fraction: float
    monthly_burn: float
    fortress_runway_months: float
    expected_arena_return: float
    catastrophic_arena_loss_pct: float
    ruin_violation: bool
    verdict: str
    currency: str = "S$"

    def to_ascii_table(self) -> str:
        curr = f"{self.currency} " if not self.currency.endswith("$") else self.currency
        lines = [
            "============================================================",
            "         DUAL-VAULT BARBELL RISK AUDIT (DBU vs ACU)         ",
            "============================================================",
            f"  Fortress Capital (DBU)        : {curr}{self.fortress_capital:,.2f}",
            f"  Arena Capital (ACU)           : {curr}{self.arena_capital:,.2f}",
            f"  Total Liquid Capital          : {curr}{self.total_capital:,.2f}",
            f"  Arena Allocation Fraction     : {self.arena_fraction * 100:.2f}%",
            f"  Baseline Monthly Burn Rate    : {curr}{self.monthly_burn:,.2f}",
            f"  Fortress Survival Runway      : {self.fortress_runway_months:.1f} months",
            "------------------------------------------------------------",
            f"  Law #1 Ruin Violation (>10%)  : {'YES (HARD VETO)' if self.ruin_violation else 'NO (Ergodic)'}",
            f"  Strategic Verdict             : {self.verdict}",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class InternalDevaluationResult:
    current_burn: float
    reduced_burn: float
    burn_reduction_pct: float
    liquid_reserves: float
    post_shock_income: float
    boxer_runway_months: float
    sovereign_runway_months: float
    runway_expansion_factor: float
    is_infinite_runway: bool
    verdict: str
    currency: str = "S$"

    def to_ascii_table(self) -> str:
        curr = f"{self.currency} " if not self.currency.endswith("$") else self.currency
        lines = [
            "============================================================",
            "     INTERNAL DEVALUATION AUDIT (ANTI-BOXER HEURISTIC)      ",
            "============================================================",
            f"  Pre-Devaluation Monthly Burn  : {curr}{self.current_burn:,.2f}",
            f"  Post-Devaluation Monthly Burn : {curr}{self.reduced_burn:,.2f}",
            f"  Burn Compression Achieved     : {self.burn_reduction_pct:.1f}%",
            f"  Post-Shock Cash Income        : {curr}{self.post_shock_income:,.2f}",
            f"  Liquid Cash Reserves          : {curr}{self.liquid_reserves:,.2f}",
            "------------------------------------------------------------",
            f"  Boxer Runway ('Work Harder')  : {'INFINITE' if self.boxer_runway_months == float('inf') else f'{self.boxer_runway_months:.1f} months'}",
            f"  Sovereign Runway (Devalued)   : {'INFINITE' if self.is_infinite_runway else f'{self.sovereign_runway_months:.1f} months'}",
            f"  Runway Expansion Factor       : {'INFINITE' if self.is_infinite_runway else f'{self.runway_expansion_factor:.2f}x'}",
            f"  Strategic Verdict             : {self.verdict}",
            "============================================================",
        ]
        return "\n".join(lines)


@dataclass
class BorrowVulnerabilityResult:
    counterparty_exposure: float
    total_net_worth: float
    exposure_pct: float
    unilateral_freeze_power: bool
    unhedged_credit: bool
    upstream_spec_complete: bool
    bvi_score: float
    ruin_violation: bool
    verdict: str
    currency: str = "S$"

    def to_ascii_table(self) -> str:
        curr = f"{self.currency} " if not self.currency.endswith("$") else self.currency
        lines = [
            "============================================================",
            "   BORROW VULNERABILITY INDEX (BVI / KINGDOM LOGISTICS)     ",
            "============================================================",
            f"  Counterparty Exposure Capital : {curr}{self.counterparty_exposure:,.2f}",
            f"  Total Sovereign Net Worth     : {curr}{self.total_net_worth:,.2f}",
            f"  Exposure Fraction             : {self.exposure_pct:.2f}%",
            f"  Unilateral Freeze / Terms     : {'YES (Platform Risk)' if self.unilateral_freeze_power else 'NO (Symmetric)'}",
            f"  Unhedged Credit Conceded      : {'YES (Vulnerable)' if self.unhedged_credit else 'NO (Gated)'}",
            f"  Upstream Spec Bounded         : {'YES (Air-tight)' if self.upstream_spec_complete else 'NO (Heroism Trap)'}",
            "------------------------------------------------------------",
            f"  Borrow Vulnerability Score    : {self.bvi_score:.1f} / 100",
            f"  Law #1 Ruin Exposure          : {'CRITICAL HAZARD' if self.ruin_violation else 'CONTAINED'}",
            f"  Strategic Verdict             : {self.verdict}",
            "============================================================",
        ]
        return "\n".join(lines)


def compute_eev(
    mev: float = 0.0,
    eu: float | None = None,
    eo: float | None = None,
    skeptic_discount: float = 0.15,
    utility: float = 0.0,
    *,
    friction: float | None = None,
    opportunity_cost: float | None = None,
) -> EEVResult:
    """Computes Economic Expected Value (EEV).

    Canonical formula:
      EEV_raw = MEV + E(U) - Friction - E(O)          all terms in S$
      EEV_net = EEV_raw * (1 - skeptic_discount)      only if EEV_raw > 0; losses at face value
      E(U)    = S$-denominated willingness-to-pay for the non-monetary benefit (never raw "utils")

    Parameters:
        mev: Gross Monetary Expected Value (S$).
        eu: Execution & Friction Drag — direct costs (S$). Alias for friction.
        eo: Opportunity & Attention Cost (S$). Alias for opportunity_cost.
        skeptic_discount: Optimism haircut applied ONLY to positive raw EV [0.0, 1.0).
        utility: Expected Utility E(U) — S$-denominated willingness-to-pay.
        friction: Execution & Friction Drag (S$). Preferred alias for eu.
        opportunity_cost: Opportunity & Attention Cost (S$). Preferred alias for eo.
    """
    if skeptic_discount < 0.0 or skeptic_discount >= 1.0:
        raise ValueError("skeptic_discount must be in range [0.0, 1.0)")

    eff_friction = friction if friction is not None else (eu if eu is not None else 0.0)
    eff_opportunity = opportunity_cost if opportunity_cost is not None else (eo if eo is not None else 0.0)

    raw_ev = mev + utility - eff_friction - eff_opportunity
    # F-04 fix: discount is an optimism haircut — it ONLY applies to positive EV.
    # Applying it to negative EV would make losses look smaller (the opposite of skepticism).
    if raw_ev > 0:
        net_eev = raw_ev * (1.0 - skeptic_discount)
    else:
        net_eev = raw_ev  # Losses are reported at full face value

    total_drag = eff_friction + eff_opportunity
    roi_percent = (net_eev / total_drag * 100.0) if total_drag > 0 else (100.0 if net_eev > 0 else 0.0)

    if net_eev > 0 and roi_percent >= 50.0:
        verdict = "APPROVE (+EV Asymmetric Opportunity)"
    elif net_eev > 0:
        verdict = "MARGINAL (+EV but High Drag / Low Margin)"
    else:
        verdict = "REJECT (-EV Drain / Negative Asymmetry)"

    return EEVResult(
        mev=mev,
        eu=eff_friction,
        eo=eff_opportunity,
        skeptic_discount=skeptic_discount,
        raw_ev=raw_ev,
        net_eev=net_eev,
        roi_percent=roi_percent,
        verdict=verdict,
        utility=utility,
    )


def _ruin_root(p: float, b: float) -> float:
    """Solves characteristic equation for asymmetric random walk:
    p * x^(b + 1) - x + q = 0 for unique root x in (0, 1) via stdlib bisection.
    """
    q = 1.0 - p
    edge = (p * b) - q
    if edge <= 0.0:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(60):
        mid = (low + high) / 2.0
        val = p * math.pow(mid, b + 1.0) - mid + q
        if val > 0.0:
            low = mid
        else:
            high = mid
    root = (low + high) / 2.0
    return root


def compute_half_kelly(
    win_rate: float,
    payoff_ratio: float,
    variance_drag: float = 0.5,
) -> KellyResult:
    """Calculates Half-Kelly position sizing with variance dampening and Law #1 ruin capping.

    f* = (b*p - q) / b
    where p = win_rate, q = 1 - p, b = payoff_ratio (win/loss)
    """
    if not (0.0 <= win_rate <= 1.0):
        raise ValueError("win_rate must be between 0.0 and 1.0")
    if payoff_ratio <= 0.0:
        raise ValueError("payoff_ratio must be positive")

    p = win_rate
    q = 1.0 - p
    b = payoff_ratio

    edge = (p * b) - q
    f_star = edge / b if b > 0 else 0.0

    if f_star <= 0.0:
        full_k = 0.0
        half_k = 0.0
        quarter_k = 0.0
        rec_fraction = 0.0
        ruin_capped_fraction = 0.0
        verdict = "NO BET (-EV or Zero Edge)"
    else:
        full_k = f_star
        half_k = f_star * 0.5
        quarter_k = f_star * 0.25
        base_rec = half_k * (1.0 - max(0.0, min(0.9, variance_drag - 0.5)))

        root = _ruin_root(p, b)
        if root >= 1.0 or edge <= 0.0:
            ruin_capped_fraction = 0.0
        else:
            threshold = 0.5  # 50% drawdown ruin barrier
            f_cap = threshold * math.log(root) / math.log(LAW1_MAX_RUIN)
            f_cand = min(base_rec, f_cap)
            for _ in range(15):
                r_check = compute_ruin_probability(win_rate, payoff_ratio, f_cand, trials_for_sim=10000)
                if not r_check.violates_law1:
                    break
                f_cand *= 0.9
            ruin_capped_fraction = f_cand

        rec_fraction = min(base_rec, ruin_capped_fraction)
        if rec_fraction < base_rec:
            verdict = f"APPROVED (RUIN-BOUND: Alloc {rec_fraction * 100:.2f}% of Liquid Bankroll)"
        else:
            verdict = f"APPROVED (Alloc {rec_fraction * 100:.2f}% of Liquid Bankroll)"

    return KellyResult(
        win_rate=win_rate,
        payoff_ratio=payoff_ratio,
        edge=edge,
        full_kelly=full_k,
        half_kelly=half_k,
        quarter_kelly=quarter_k,
        recommended_fraction=rec_fraction,
        verdict=verdict,
        ruin_capped_fraction=ruin_capped_fraction,
    )


def compute_ruin_probability(
    win_rate: float,
    payoff_ratio: float,
    risk_per_trade_fraction: float,
    ruin_drawdown_threshold: float = 0.5,
    trials_for_sim: int = 10000,
    steps_for_sim: int = 200,
) -> RuinResult:
    """Calculates ruin probability via two DIFFERENT models.

    WARNING (F-02 Red-Team Finding, 2026-09-26):
    The analytical and simulated estimates model DIFFERENT stochastic processes:

    - ANALYTICAL: Classic Gambler's Ruin on an additive random walk with fixed
      bet sizes (additive P&L). Solves the exact characteristic equation
      p*x^(b+1) - x + q = 0 for the unique root x in (0, 1), then computes
      P(Ruin) = x^units where units = drawdown_threshold / risk_fraction.
      For b=1, this reduces to (q/p)^units.

    - SIMULATION: Geometric (multiplicative) compounding where each step
      changes capital by ±(risk_fraction * capital). Models real leveraged
      trading more accurately but is path-dependent and step-count-sensitive.

    These two estimates are NOT cross-validation pairs — they answer slightly
    different questions. The verdict uses the MORE CONSERVATIVE (higher) of
    the two to err on the side of safety per Law #1 (Never Risk Ruin).
    """
    if not (0.0 < win_rate < 1.0):
        raise ValueError("win_rate must be strictly between 0 and 1")
    if payoff_ratio <= 0.0 or risk_per_trade_fraction <= 0.0:
        raise ValueError("payoff_ratio and risk_per_trade_fraction must be positive")

    p = win_rate
    q = 1.0 - p
    b = payoff_ratio
    edge = (p * b) - q

    # Analytical ruin (additive random walk characteristic root model):
    # Units to ruin = ruin_drawdown_threshold / risk_per_trade_fraction
    units = ruin_drawdown_threshold / risk_per_trade_fraction
    if edge <= 0.0:
        analytical_ruin = 1.0
    else:
        root = _ruin_root(p, b)
        analytical_ruin = min(1.0, math.pow(root, units)) if root < 1.0 else 1.0

    # Empirical Monte Carlo simulation (GEOMETRIC/multiplicative model):
    ruin_count = 0
    rng = random.Random(42)
    for _ in range(trials_for_sim):
        cap = 1.0
        peak = 1.0
        for _ in range(steps_for_sim):
            is_win = rng.random() < win_rate
            if is_win:
                cap += cap * (risk_per_trade_fraction * b)
            else:
                cap -= cap * risk_per_trade_fraction

            if cap > peak:
                peak = cap

            dd = (peak - cap) / peak
            if dd >= ruin_drawdown_threshold or cap <= (1.0 - ruin_drawdown_threshold):
                ruin_count += 1
                break  # F-03: absorbing barrier — stop this trial on ruin

    simulated_ruin = ruin_count / trials_for_sim

    # F-02 fix: use the MORE CONSERVATIVE (higher) estimate for the verdict
    conservative_ruin = max(simulated_ruin, analytical_ruin)
    violates_law1 = conservative_ruin > LAW1_MAX_RUIN

    if violates_law1:
        verdict = f"VETO (Violates Law #1: Ruin Probability > {LAW1_MAX_RUIN * 100:.1f}%)"
    elif conservative_ruin > 0.01:
        verdict = f"CAUTION (Elevated Left-Tail Risk: 1.0% - {LAW1_MAX_RUIN * 100:.1f}%)"
    else:
        verdict = "PASS (Ergodic & Safe: Ruin Probability < 1.0%)"

    return RuinResult(
        win_rate=win_rate,
        payoff_ratio=payoff_ratio,
        risk_per_trade_fraction=risk_per_trade_fraction,
        ruin_drawdown_threshold=ruin_drawdown_threshold,
        analytical_ruin_prob=analytical_ruin,
        simulated_ruin_prob=simulated_ruin,
        verdict=verdict,
        violates_law1=violates_law1,
    )


def run_monte_carlo_simulation(
    initial_capital: float = 10000.0,
    win_rate: float = 0.55,
    payoff_ratio: float = 1.5,
    risk_fraction: float = 0.02,
    n_trials: int = 10000,
    n_steps: int = 100,
    left_tail_shock_prob: float = 0.01,
    left_tail_shock_loss: float = 0.10,
    ruin_threshold_pct: float = 50.0,
    seed: int | None = 42,
) -> MonteCarloResult:
    """Executes a geometric trajectory simulation with left-tail shocks.

    NOTE: Reported 'ci_95/99' values are 2.5th/97.5th percentile PREDICTION
    INTERVALS of simulated terminal capital, NOT confidence intervals for a
    population parameter. 'worst_drawdown_pct' is the 99th percentile of
    max drawdown (not the absolute worst case).
    """
    # F-03 fix: validate all inputs
    if n_trials <= 0:
        raise ValueError(f"n_trials must be positive, got {n_trials}")
    if n_steps <= 0:
        raise ValueError(f"n_steps must be positive, got {n_steps}")
    if initial_capital <= 0:
        raise ValueError(f"initial_capital must be positive, got {initial_capital}")
    if not (0.0 <= win_rate <= 1.0):
        raise ValueError(f"win_rate must be in [0.0, 1.0], got {win_rate}")
    if math.isnan(win_rate) or math.isnan(risk_fraction) or math.isnan(payoff_ratio):
        raise ValueError("win_rate, risk_fraction, and payoff_ratio must not be NaN")
    if math.isinf(risk_fraction) or math.isinf(payoff_ratio):
        raise ValueError("risk_fraction and payoff_ratio must be finite")
    if risk_fraction < 0:
        raise ValueError(f"risk_fraction must be non-negative, got {risk_fraction}")
    if payoff_ratio <= 0:
        raise ValueError(f"payoff_ratio must be positive, got {payoff_ratio}")

    rng = random.Random(seed)
    final_capitals: list[float] = []
    max_drawdowns: list[float] = []
    ruin_count = 0

    for _ in range(n_trials):
        cap = initial_capital
        peak = cap
        max_dd = 0.0

        for _ in range(n_steps):
            # Check for catastrophic shock
            if left_tail_shock_prob > 0.0 and rng.random() < left_tail_shock_prob:
                cap -= cap * left_tail_shock_loss
            else:
                is_win = rng.random() < win_rate
                if is_win:
                    cap += cap * (risk_fraction * payoff_ratio)
                else:
                    cap -= cap * risk_fraction

            if cap > peak:
                peak = cap

            dd = ((peak - cap) / peak) * 100.0 if peak > 0 else 100.0
            if dd > max_dd:
                max_dd = dd

            if cap <= initial_capital * (1.0 - ruin_threshold_pct / 100.0):
                # F-03 fix: Absorbing barrier — stop trading this trial on ruin
                ruin_count += 1
                break

        final_capitals.append(cap)
        max_drawdowns.append(max_dd)

    final_capitals.sort()
    max_drawdowns.sort()

    mean_final = sum(final_capitals) / n_trials
    median_final = final_capitals[int(n_trials * 0.50)]

    idx_2_5 = max(0, int(n_trials * 0.025))
    idx_97_5 = min(n_trials - 1, int(n_trials * 0.975))
    idx_0_5 = max(0, int(n_trials * 0.005))
    idx_99_5 = min(n_trials - 1, int(n_trials * 0.995))

    ci_95_lower = final_capitals[idx_2_5]
    ci_95_upper = final_capitals[idx_97_5]
    ci_99_lower = final_capitals[idx_0_5]
    ci_99_upper = final_capitals[idx_99_5]

    mean_max_dd = sum(max_drawdowns) / n_trials
    worst_dd_99 = max_drawdowns[int(n_trials * 0.99)]
    ruin_prob = (ruin_count / n_trials) * 100.0

    # Geometric mean growth rate per step
    if median_final > 0 and initial_capital > 0 and n_steps > 0:
        geom_growth = math.pow(median_final / initial_capital, 1.0 / n_steps) - 1.0
    else:
        geom_growth = -1.0

    return MonteCarloResult(
        n_trials=n_trials,
        n_steps=n_steps,
        initial_capital=initial_capital,
        mean_final_capital=mean_final,
        median_final_capital=median_final,
        ci_95_lower=ci_95_lower,
        ci_95_upper=ci_95_upper,
        ci_99_lower=ci_99_lower,
        ci_99_upper=ci_99_upper,
        mean_max_drawdown_pct=mean_max_dd,
        worst_drawdown_pct=worst_dd_99,
        ruin_probability_pct=ruin_prob,
        growth_rate_geometric_mean=geom_growth,
    )


def compute_growth_rate(
    wealth: float,
    states: list[tuple[Any, ...] | dict[str, Any]],
    *,
    barrier: float = 0.0,
) -> float:
    """Calculates expected log-wealth growth rate (time-average ergodicity).

    Formula:
        g = sum_i(p_i * ln(1 + payoff_i / wealth))
    Returns -inf if any state with p > 0 has is_ruin=True or wealth + payoff <= barrier * wealth.

    Parameters:
        wealth: Liquid capital available before the decision (> 0).
        states: List of state tuples (prob, payoff[, is_ruin]) or dicts with
                {"prob": p, "payoff": x, ["is_ruin": bool]}.
        barrier: Ruin boundary multiplier (default 0.0, meaning total wipeout: wealth + payoff <= 0).
                 Must be >= 0.0.
    """
    if not isinstance(wealth, (int, float)) or wealth <= 0.0 or math.isnan(wealth) or math.isinf(wealth):
        raise ValueError(f"wealth must be a positive finite number, got {wealth}")
    if barrier < 0.0 or math.isnan(barrier) or math.isinf(barrier):
        raise ValueError(f"barrier cannot be lowered below 0.0, got {barrier}")
    if not states:
        raise ValueError("states list must not be empty")

    parsed_states: list[tuple[float, float, bool]] = []
    for item in states:
        if isinstance(item, (tuple, list)):
            if len(item) == 2:
                p, payoff, is_r = float(item[0]), float(item[1]), False
            elif len(item) == 3:
                p, payoff, is_r = float(item[0]), float(item[1]), bool(item[2])
            else:
                raise ValueError(f"State tuple must have 2 or 3 elements, got {len(item)}")
        elif isinstance(item, dict):
            p = float(item["prob"])
            payoff = float(item["payoff"])
            is_r = bool(item.get("is_ruin", False))
        else:
            raise TypeError(f"State must be tuple, list, or dict, got {type(item)}")

        if math.isnan(p) or math.isnan(payoff) or math.isinf(p) or math.isinf(payoff):
            raise ValueError(f"State contains NaN or Inf: prob={p}, payoff={payoff}")
        if p < 0.0:
            raise ValueError(f"State probability must be non-negative, got {p}")
        parsed_states.append((p, payoff, is_r))

    prob_sum = sum(p for p, _, _ in parsed_states)
    if abs(prob_sum - 1.0) > 1e-5:
        raise ValueError(
            f"State probabilities must sum to 1.0, got {prob_sum:.6f}. "
            "Add an explicit complementary state so probabilities sum to 1.0."
        )

    growth = 0.0
    for p, payoff, is_r in parsed_states:
        if p > 0.0:
            if is_r or (wealth + payoff <= barrier * wealth):
                return -float("inf")
            ratio = 1.0 + (payoff / wealth)
            if ratio <= 0.0:
                return -float("inf")
            growth += p * math.log(ratio)

    return growth


def run_decision_monte_carlo(
    candidates: list[str],
    states: dict[str, list[tuple[Any, ...] | dict[str, Any]]],
    *,
    n: int = 2000,
    prob_jitter: float = 0.20,
    seed: int | None = 42,
    wealth: float | None = None,
    materiality: float = 0.01,
    barrier: float = 0.0,
    sample_outcomes: bool = False,
    tail_uncertainty: float = 1.0,
) -> DecisionMonteCarloResult:
    """Runs a general decision Monte Carlo simulation across candidate state spaces.

    Parameters:
        candidates: List of candidate strategies/paths.
        states: Dict mapping candidate to list of state tuples or dicts:
                (prob, payoff) or (prob, payoff, is_ruin).
        n: Number of simulation iterations (default 2000).
        prob_jitter: Symmetric range for state probability perturbation (default ±20%).
        seed: Random seed for reproducibility (default 42).
        wealth: Liquid capital to evaluate log-wealth growth and computed ruin (optional).
        materiality: Threshold fraction of wealth where payoff is considered material (default 0.01).
        barrier: Ruin boundary multiplier (default 0.0, wealth + payoff <= barrier * wealth).
        sample_outcomes: If True, draws one discrete outcome per trial and reports P10/P90.
        tail_uncertainty: Log-uniform perturbation factor for ruin states (>= 1.0, default 1.0).
    """
    if not candidates:
        raise ValueError("candidates list must not be empty")
    if n <= 0:
        raise ValueError("n (trial count) must be positive")
    if not (0.0 <= prob_jitter < 1.0):
        raise ValueError("prob_jitter must be in [0.0, 1.0)")
    if wealth is not None and (wealth <= 0.0 or math.isnan(wealth) or math.isinf(wealth)):
        raise ValueError(f"wealth must be a positive finite number, got {wealth}")
    if barrier < 0.0 or math.isnan(barrier) or math.isinf(barrier):
        raise ValueError("barrier cannot be lowered below 0.0")
    if tail_uncertainty < 1.0 or math.isnan(tail_uncertainty) or math.isinf(tail_uncertainty):
        raise ValueError("tail_uncertainty must be >= 1.0")
    if materiality <= 0.0 or math.isnan(materiality) or math.isinf(materiality):
        raise ValueError("materiality must be positive")

    for c in candidates:
        if c not in states:
            raise ValueError(f"Candidate '{c}' missing from states dictionary")
        if not states[c]:
            raise ValueError(f"Candidate '{c}' has empty states list")

    rng = random.Random(seed)

    # Pre-parse candidate states: list of (base_prob, payoff, is_ruin)
    parsed_states: dict[str, list[tuple[float, float, bool]]] = {}
    ruin_sources: dict[str, dict[str, int]] = {}

    has_material_payoff = False

    for c in candidates:
        cand_states: list[tuple[float, float, bool]] = []
        typed_ruin_count = 0
        computed_ruin_count = 0

        for item in states[c]:
            if isinstance(item, (tuple, list)):
                if len(item) == 2:
                    prob = float(item[0])
                    payoff = float(item[1])
                    typed_is_ruin = False
                elif len(item) == 3:
                    prob = float(item[0])
                    payoff = float(item[1])
                    typed_is_ruin = bool(item[2])
                else:
                    raise ValueError(f"State tuple must have 2 or 3 elements, got {len(item)}")
            elif isinstance(item, dict):
                prob = float(item["prob"])
                payoff = float(item["payoff"])
                typed_is_ruin = bool(item.get("is_ruin", False))
            else:
                raise TypeError(f"State must be tuple, list, or dict, got {type(item)}")

            if prob < 0.0 or math.isnan(prob) or math.isinf(prob):
                raise ValueError(f"State probability must be non-negative finite number, got {prob}")
            if math.isnan(payoff) or math.isinf(payoff):
                raise ValueError(f"Payoff must be finite number, got {payoff}")

            # Determine ruin and provenance
            if typed_is_ruin:
                typed_ruin_count += 1
                is_ruin = True
            elif wealth is not None and (wealth + payoff <= barrier * wealth):
                computed_ruin_count += 1
                is_ruin = True
            else:
                is_ruin = False

            if wealth is not None and abs(payoff) >= (materiality * wealth):
                has_material_payoff = True

            cand_states.append((prob, payoff, is_ruin))

        prob_sum = sum(p for p, _, _ in cand_states)
        if abs(prob_sum - 1.0) > 1e-6:
            raise ValueError(
                f"Candidate '{c}' state probabilities sum to {prob_sum:.6f} != 1.0. "
                f"Add an explicit 'other/unknown' state so probabilities sum to 1.0."
            )
        parsed_states[c] = cand_states
        ruin_sources[c] = {"typed": typed_ruin_count, "computed": computed_ruin_count}

    use_growth_ranking = (wealth is not None) and has_material_payoff
    ranking_metric = "growth" if use_growth_ranking else "EEV"

    # Tracking metrics per candidate
    eev_trajectories: dict[str, list[float]] = {c: [] for c in candidates}
    growth_trajectories: dict[str, list[float]] = {c: [] for c in candidates}
    ruin_pct_trajectories: dict[str, list[float]] = {c: [] for c in candidates}
    win_counts: dict[str, int] = dict.fromkeys(candidates, 0)

    # Outcome sampling tracking
    candidate_sampled_outcomes: dict[str, list[float]] = {c: [] for c in candidates}
    candidate_sampled_ruins: dict[str, int] = dict.fromkeys(candidates, 0)

    for _ in range(n):
        trial_eevs: dict[str, float] = {}
        trial_growths: dict[str, float] = {}
        trial_ruin_ps: dict[str, float] = {}

        for c in candidates:
            c_states = parsed_states[c]
            norm_probs: list[float] = []

            ruin_indices = [i for i, (_, _, is_r) in enumerate(c_states) if is_r]
            non_ruin_indices = [i for i, (_, _, is_r) in enumerate(c_states) if not is_r]

            if tail_uncertainty > 1.0 and ruin_indices and non_ruin_indices:
                jittered_ruin: dict[int, float] = {}
                for idx in ruin_indices:
                    base_p = c_states[idx][0]
                    if base_p > 0:
                        u = rng.uniform(-math.log(tail_uncertainty), math.log(tail_uncertainty))
                        jittered_ruin[idx] = base_p * math.exp(u)
                    else:
                        jittered_ruin[idx] = 0.0

                total_ruin_p = sum(jittered_ruin.values())
                if total_ruin_p >= 0.9999:
                    scale = 0.9999 / total_ruin_p
                    for idx in ruin_indices:
                        jittered_ruin[idx] *= scale
                    total_ruin_p = 0.9999

                remaining_p = max(0.0001, 1.0 - total_ruin_p)
                raw_non_ruin: dict[int, float] = {}
                for idx in non_ruin_indices:
                    base_p = c_states[idx][0]
                    if prob_jitter > 0:
                        j = rng.uniform(-prob_jitter, prob_jitter)
                        raw_non_ruin[idx] = max(0.00001, base_p * (1.0 + j))
                    else:
                        raw_non_ruin[idx] = max(0.00001, base_p)
                non_ruin_sum = sum(raw_non_ruin.values())

                norm_probs = [0.0] * len(c_states)
                for idx in ruin_indices:
                    norm_probs[idx] = jittered_ruin[idx]
                for idx in non_ruin_indices:
                    norm_probs[idx] = remaining_p * (raw_non_ruin[idx] / non_ruin_sum)
            else:
                raw_probs: list[float] = []
                for base_p, _, _ in c_states:
                    if prob_jitter > 0:
                        j = rng.uniform(-prob_jitter, prob_jitter)
                        raw_probs.append(max(0.0001, base_p * (1.0 + j)))
                    else:
                        raw_probs.append(base_p)
                total_p = sum(raw_probs)
                norm_probs = [p / total_p for p in raw_probs]

            # Calculate EEV, ruin probability, and growth rate in this trial
            trial_eev = 0.0
            trial_ruin_p = 0.0
            trial_growth = 0.0
            trial_has_ruin = False

            for i, (_, payoff, is_ruin) in enumerate(c_states):
                p_i = norm_probs[i]
                trial_eev += p_i * payoff
                if is_ruin:
                    trial_ruin_p += p_i

                if wealth is not None and not trial_has_ruin and p_i > 0:
                    if is_ruin or (wealth + payoff <= barrier * wealth):
                        trial_has_ruin = True
                    else:
                        ratio = 1.0 + (payoff / wealth)
                        if ratio <= 0.0:
                            trial_has_ruin = True
                        else:
                            trial_growth += p_i * math.log(ratio)

            if trial_has_ruin:
                trial_growth = -float("inf")

            eev_trajectories[c].append(trial_eev)
            ruin_pct_trajectories[c].append(trial_ruin_p * 100.0)
            if wealth is not None:
                growth_trajectories[c].append(trial_growth)

            trial_eevs[c] = trial_eev
            trial_ruin_ps[c] = trial_ruin_p
            if wealth is not None:
                trial_growths[c] = trial_growth

            # Outcome sampling if requested
            if sample_outcomes:
                r = rng.random()
                cum = 0.0
                sampled_idx = 0
                for idx, p in enumerate(norm_probs):
                    cum += p
                    if r <= cum or idx == len(norm_probs) - 1:
                        sampled_idx = idx
                        break
                sampled_payoff = c_states[sampled_idx][1]
                sampled_is_ruin = c_states[sampled_idx][2]
                candidate_sampled_outcomes[c].append(sampled_payoff)
                if sampled_is_ruin:
                    candidate_sampled_ruins[c] += 1

        # In each draw, candidates whose draw ruin probability exceeds LAW1_MAX_RUIN are ineligible.
        # Winner of draw is chosen among eligible candidates.
        eligible = [c for c in candidates if trial_ruin_ps[c] <= LAW1_MAX_RUIN]
        if eligible:
            if use_growth_ranking:
                best_cand = max(eligible, key=lambda c: trial_growths[c])
            else:
                best_cand = max(eligible, key=lambda c: trial_eevs[c])
            win_counts[best_cand] += 1

    # Aggregate candidate statistics
    winner_frequencies: dict[str, float] = {}
    candidate_stats: dict[str, CandidateSimulationStats] = {}

    for c in candidates:
        win_freq = (win_counts[c] / n) * 100.0
        winner_frequencies[c] = win_freq

        eevs = sorted(eev_trajectories[c])
        mean_eev = sum(eevs) / n
        median_eev = eevs[n // 2]
        p10_idx = int(n * 0.10)
        p90_idx = min(int(n * 0.90), n - 1)
        p10_eev = eevs[p10_idx]
        p90_eev = eevs[p90_idx]

        pos_eev_count = sum(1 for val in eevs if val > 0)
        pct_eev_pos = (pos_eev_count / n) * 100.0

        mean_ruin_pct = sum(ruin_pct_trajectories[c]) / n
        ruin_gate_passed = mean_ruin_pct <= (LAW1_MAX_RUIN * 100.0)

        # Growth statistics
        if wealth is not None:
            growths = sorted(growth_trajectories[c])
            median_growth = growths[n // 2]
            finite_growths = [g for g in growths if not math.isinf(g)]
            if len(finite_growths) == len(growths):
                mean_growth = sum(growths) / n
            else:
                mean_growth = -float("inf")
        else:
            median_growth = None
            mean_growth = None

        # Outcome sampling statistics
        if sample_outcomes:
            sorted_outcomes = sorted(candidate_sampled_outcomes[c])
            outcome_p10 = sorted_outcomes[p10_idx]
            outcome_p90 = sorted_outcomes[p90_idx]
            realized_ruin_pct = (candidate_sampled_ruins[c] / n) * 100.0
        else:
            outcome_p10 = None
            outcome_p90 = None
            realized_ruin_pct = None

        if not ruin_gate_passed:
            verdict = f"FAIL (Law #1 Ruin >= {LAW1_MAX_RUIN * 100.0:.0f}%)"
        elif p10_eev > 0:
            verdict = "PASS (Robust)"
        elif pct_eev_pos >= 70.0:
            verdict = "MARGINAL (EEV>0 >= 70%, but P10 <= 0)"
        else:
            verdict = "FAIL (EEV>0 < 70%)"

        candidate_stats[c] = CandidateSimulationStats(
            candidate=c,
            win_frequency_pct=win_freq,
            pct_eev_positive=pct_eev_pos,
            pct_ruin=mean_ruin_pct,
            median_eev=median_eev,
            mean_eev=mean_eev,
            p10_eev=p10_eev,
            p90_eev=p90_eev,
            ruin_gate_passed=ruin_gate_passed,
            verdict=verdict,
            median_growth=median_growth,
            mean_growth=mean_growth,
            ruin_source=ruin_sources[c],
            outcome_p10=outcome_p10,
            outcome_p90=outcome_p90,
            realized_ruin_pct=realized_ruin_pct,
        )

    vetoed_candidates = [c for c in candidates if not candidate_stats[c].ruin_gate_passed]
    eligible_cands = [c for c in candidates if candidate_stats[c].ruin_gate_passed]
    if eligible_cands:
        if use_growth_ranking:
            top_candidate = max(
                eligible_cands,
                key=lambda c: (
                    candidate_stats[c].median_growth if candidate_stats[c].median_growth is not None else -float("inf"),
                    winner_frequencies[c],
                ),
            )
        else:
            top_candidate = max(eligible_cands, key=lambda c: winner_frequencies[c])
    else:
        top_candidate = "NONE"

    return DecisionMonteCarloResult(
        n_trials=n,
        candidates=candidates,
        winner_frequencies=winner_frequencies,
        candidate_stats=candidate_stats,
        top_candidate=top_candidate,
        seed=seed,
        vetoed_candidates=vetoed_candidates,
        ranking_metric=ranking_metric,
    )


def compute_robustness(
    policies: list[str],
    scenarios: list[str],
    payoff: dict[str, dict[str, float]],
    *,
    ruin: dict[str, dict[str, bool]] | None = None,
    probs: dict[str, float] | None = None,
    wealth: float | None = None,
    barrier: float = 0.0,
    cvar_alpha: float = 0.10,
    tail_factor: float = 3.0,
) -> RobustnessResult:
    """Evaluates scenario-by-policy robustness using Minimax Regret, Maximin, and CVaR.

    Parameters:
        policies: Candidate strategic policies / choices.
        scenarios: Plausible world states / scenarios.
        payoff: Dict mapping policy -> scenario -> float payoff.
        ruin: Optional dict mapping policy -> scenario -> bool (is ruin state).
        probs: Optional dict mapping scenario -> float probability (must sum to 1.0).
        wealth: Optional pre-decision liquid capital (> 0). If provided, computes
                ruin states dynamically where wealth + payoff <= barrier * wealth.
        barrier: Ruin boundary multiplier (default 0.0, meaning total wipeout).
                 Must be >= 0.0.
        cvar_alpha: Lower tail probability mass fraction for CVaR (default 0.10).
        tail_factor: Multiplier for typed ruin tail probabilities (default 3.0).
    """
    if not policies:
        raise ValueError("policies list must not be empty")
    if not scenarios:
        raise ValueError("scenarios list must not be empty")
    if len(set(policies)) != len(policies):
        raise ValueError(f"duplicate policy names found in {policies}")
    if len(set(scenarios)) != len(scenarios):
        raise ValueError(f"duplicate scenario names found in {scenarios}")
    if not (0.0 < cvar_alpha <= 1.0) or math.isnan(cvar_alpha) or math.isinf(cvar_alpha):
        raise ValueError(f"cvar_alpha must be in (0.0, 1.0], got {cvar_alpha}")
    if tail_factor < 1.0 or math.isnan(tail_factor) or math.isinf(tail_factor):
        raise ValueError(f"tail_factor must be >= 1.0, got {tail_factor}")
    if wealth is not None and (
        not isinstance(wealth, (int, float))
        or wealth <= 0.0
        or math.isnan(wealth)
        or math.isinf(wealth)
    ):
        raise ValueError(f"wealth must be a positive finite number, got {wealth}")
    if barrier < 0.0 or math.isnan(barrier) or math.isinf(barrier):
        raise ValueError(f"barrier cannot be lowered below 0.0, got {barrier}")

    # Validate payoffs
    for p in policies:
        if p not in payoff:
            raise ValueError(f"policy '{p}' missing from payoff dictionary")
        for s in scenarios:
            if s not in payoff[p]:
                raise ValueError(f"missing cell: payoff['{p}']['{s}']")
            val = payoff[p][s]
            if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                raise ValueError(f"NaN or Inf payoff for policy '{p}', scenario '{s}': {val}")

    # Validate ruin dict & computed ruin
    ruin_screened = (ruin is not None) or (wealth is not None)
    clean_ruin: dict[str, dict[str, bool]] = {}
    for p in policies:
        clean_ruin[p] = {}
        for s in scenarios:
            is_r = False
            if ruin is not None and p in ruin and s in ruin[p]:
                is_r = bool(ruin[p][s])
            if wealth is not None and wealth + payoff[p][s] <= barrier * wealth:
                is_r = True
            clean_ruin[p][s] = is_r

    # Validate probs dict if provided
    clean_probs: dict[str, float] | None = None
    if probs is not None:
        clean_probs = {}
        for s in scenarios:
            if s not in probs:
                raise ValueError(f"scenario '{s}' missing from probs dictionary")
            pr = probs[s]
            if not isinstance(pr, (int, float)) or math.isnan(pr) or math.isinf(pr) or pr < 0.0:
                raise ValueError(f"NaN, Inf, or negative probability for scenario '{s}': {pr}")
            clean_probs[s] = float(pr)
        prob_sum = sum(clean_probs.values())
        if abs(prob_sum - 1.0) > 1e-5:
            raise ValueError(f"Scenario probabilities must sum to 1.0, got {prob_sum:.6f}")

    # 1. Feasibility screen
    is_feasible_map: dict[str, bool] = {}
    p_ruin_scaled_map: dict[str, float] = {}

    for p in policies:
        if clean_probs is None:
            has_ruin = any(clean_ruin[p][s] for s in scenarios)
            is_feasible_map[p] = not has_ruin
            p_ruin_scaled_map[p] = 1.0 if has_ruin else 0.0
        else:
            raw_ruin = sum(clean_probs[s] for s in scenarios if clean_ruin[p][s])
            scaled_ruin = min(1.0, tail_factor * raw_ruin)
            p_ruin_scaled_map[p] = scaled_ruin
            is_feasible_map[p] = scaled_ruin <= LAW1_MAX_RUIN

    feasible_policies = [p for p in policies if is_feasible_map[p]]
    infeasible_policies = [p for p in policies if not is_feasible_map[p]]

    # 2. Benchmarks across feasible policies
    benchmarks: dict[str, float] = {}
    for s in scenarios:
        if feasible_policies:
            benchmarks[s] = max(payoff[p][s] for p in feasible_policies)
        else:
            benchmarks[s] = 0.0

    # 3. Policy statistics
    policy_stats: dict[str, PolicyRobustnessStats] = {}
    for p in policies:
        worst_out = min(payoff[p][s] for s in scenarios)
        max_reg = max((benchmarks[s] - payoff[p][s]) for s in scenarios)

        if clean_probs is not None:
            exp_payoff = sum(clean_probs[s] * payoff[p][s] for s in scenarios)
            exp_regret = sum(clean_probs[s] * (benchmarks[s] - payoff[p][s]) for s in scenarios)

            # CVaR alpha: lower tail expectation
            sorted_outcomes = sorted([(payoff[p][s], clean_probs[s]) for s in scenarios], key=lambda x: x[0])
            accum_mass = 0.0
            weighted_sum = 0.0
            for out_val, pr_val in sorted_outcomes:
                needed = cvar_alpha - accum_mass
                if needed <= 1e-12:
                    break
                taken = min(pr_val, needed)
                weighted_sum += out_val * taken
                accum_mass += taken
            cvar_val = weighted_sum / cvar_alpha
        else:
            exp_payoff = None
            exp_regret = None
            cvar_val = None

        policy_stats[p] = PolicyRobustnessStats(
            policy=p,
            is_feasible=is_feasible_map[p],
            worst_outcome=worst_out,
            max_regret=max_reg,
            expected_payoff=exp_payoff,
            expected_regret=exp_regret,
            cvar_alpha=cvar_val,
            p_ruin_scaled=p_ruin_scaled_map[p],
        )

    # 4. Winners among feasible policies
    if not feasible_policies:
        return RobustnessResult(
            policies=policies,
            scenarios=scenarios,
            feasible_policies=feasible_policies,
            infeasible_policies=infeasible_policies,
            benchmarks=benchmarks,
            policy_stats=policy_stats,
            minimax_regret_winner="NONE",
            maximin_winner="NONE",
            ev_winner="NONE" if clean_probs is not None else None,
            verdict="FAIL (No feasible policies survive Law #1 ruin filter)",
            is_iia_sensitive=False,
            ruin_screened=ruin_screened,
        )

    # Minimax regret winner: min max_regret
    minimax_regret_winner = min(
        feasible_policies,
        key=lambda p: (policy_stats[p].max_regret, -policy_stats[p].worst_outcome, p),
    )

    # Maximin winner: max worst_outcome (floor)
    maximin_winner = max(
        feasible_policies,
        key=lambda p: (policy_stats[p].worst_outcome, -policy_stats[p].max_regret, p),
    )

    # EV winner if probabilities provided
    if clean_probs is not None:
        ev_winner: str | None = max(
            feasible_policies,
            key=lambda p: (
                policy_stats[p].expected_payoff if policy_stats[p].expected_payoff is not None else -float("inf"),
                -policy_stats[p].max_regret,
                p,
            ),
        )
    else:
        ev_winner = None

    # 5. Strategic Verdict
    if clean_probs is not None:
        if minimax_regret_winner == maximin_winner == ev_winner:
            verdict = f"ROBUST CONSENSUS: {minimax_regret_winner} dominates across all criteria"
        else:
            verdict = "CRITERIA DISAGREE: choice depends on trust in the probabilities"
    else:
        if minimax_regret_winner == maximin_winner:
            verdict = f"ROBUST CONSENSUS: {minimax_regret_winner} minimizes regret and maximizes floor"
        else:
            verdict = "CRITERIA DISAGREE: minimax regret and maximin select different policies"

    # 6. IIA Disclosure: recompute without dominated policies
    is_iia_sensitive = False
    dominated_policies: list[str] = []
    for p in feasible_policies:
        for other in feasible_policies:
            if other == p:
                continue
            if all(payoff[other][s] >= payoff[p][s] for s in scenarios) and any(payoff[other][s] > payoff[p][s] for s in scenarios):
                dominated_policies.append(p)
                break

    for dom_p in dominated_policies:
        rem_feasible = [p for p in feasible_policies if p != dom_p]
        if len(rem_feasible) >= 2:
            rem_benchmarks = {s: max(payoff[p][s] for p in rem_feasible) for s in scenarios}
            rem_winner = min(
                rem_feasible,
                key=lambda p: (
                    max(rem_benchmarks[s] - payoff[p][s] for s in scenarios),
                    -policy_stats[p].worst_outcome,
                    p,
                ),
            )
            if rem_winner != minimax_regret_winner:
                is_iia_sensitive = True
                break

    if is_iia_sensitive:
        verdict += " [IIA-SENSITIVE]"

    if not ruin_screened:
        verdict += " [UNSCREENED: no ruin labels; Law #1 not applied]"

    return RobustnessResult(
        policies=policies,
        scenarios=scenarios,
        feasible_policies=feasible_policies,
        infeasible_policies=infeasible_policies,
        benchmarks=benchmarks,
        policy_stats=policy_stats,
        minimax_regret_winner=minimax_regret_winner,
        maximin_winner=maximin_winner,
        ev_winner=ev_winner,
        verdict=verdict,
        is_iia_sensitive=is_iia_sensitive,
        ruin_screened=ruin_screened,
    )


def compute_mcda(
    candidates: list[str],
    criteria: list[str],
    weights: dict[str, float] | list[float],
    scores: dict[str, dict[str, float]] | dict[str, list[float]],
    sensitivity_pct: float = 0.10,
    margin_threshold_pct: float = 5.0,
    veto_floors: dict[str, float] | None = None,
    hard_vetoes: dict[str, list[str]] | None = None,
    ruin_exemptions: dict[str, str] | None = None,
) -> MCDAResult:
    """Computes Multiple-Criteria Decision Analysis (MCDA) with deterministic sensitivity and §3A veto screening.

    Uses weighted-sum scoring with user-specified weights (NOT AHP).

    Performs:
    1. Input validation (fail-closed on NaN, Inf, negative weights, duplicates).
    2. Hard-constraint feasibility screen (DEC-500 §3A VETO) — fail-closed on unknown keys.
    3. Base composite scoring using normalized weights (DEC-500 §3C-3D) on feasible candidates.
    4. Pairwise dominance inspection (§3F).
    5. ±10% weight perturbation sensitivity testing across each criterion (§3E).
    6. Deterministic stability verification and Path D / Path E routing.
    """
    if not candidates:
        raise ValueError("candidates list cannot be empty")
    if not criteria:
        raise ValueError("criteria list cannot be empty")

    # F-05 fix: reject duplicate candidates
    if len(candidates) != len(set(candidates)):
        seen_c = set()
        dupes_c = []
        for c in candidates:
            if c in seen_c:
                dupes_c.append(c)
            else:
                seen_c.add(c)
        raise ValueError(f"Duplicate candidate names detected: {dupes_c}")

    # F-05 fix: reject duplicate criteria
    if len(criteria) != len(set(criteria)):
        seen_cr = set()
        dupes_cr = []
        for c in criteria:
            if c in seen_cr:
                dupes_cr.append(c)
            else:
                seen_cr.add(c)
        raise ValueError(f"Duplicate criteria names detected: {dupes_cr}")

    # Format weights
    weight_dict: dict[str, float] = {}
    if isinstance(weights, list):
        if len(weights) != len(criteria):
            raise ValueError(f"weights list length ({len(weights)}) does not match criteria length ({len(criteria)})")
        weight_dict = {crit: float(w) for crit, w in zip(criteria, weights, strict=True)}
    elif isinstance(weights, dict):
        for crit in criteria:
            if crit not in weights:
                raise ValueError(f"Missing weight for criterion: {crit}")
            weight_dict[crit] = float(weights[crit])
    else:
        raise TypeError("weights must be a list or dict")

    # F-05 fix: reject NaN, Inf, and negative weights
    for crit, w in weight_dict.items():
        if math.isnan(w):
            raise ValueError(f"Weight for criterion '{crit}' is NaN — all weights must be finite non-negative numbers")
        if math.isinf(w):
            raise ValueError(f"Weight for criterion '{crit}' is infinite — all weights must be finite non-negative numbers")
        if w < 0:
            raise ValueError(f"Negative weight for criterion '{crit}' ({w}) — all weights must be non-negative")

    total_weight = sum(weight_dict.values())
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")
    normalized_weights = {crit: w / total_weight for crit, w in weight_dict.items()}

    # Format scores: map candidate -> dict[crit, score]
    score_matrix: dict[str, dict[str, float]] = {}
    for cand in candidates:
        if cand not in scores:
            raise ValueError(f"Missing scores for candidate: {cand}")
        cand_scores = scores[cand]
        if isinstance(cand_scores, list):
            if len(cand_scores) != len(criteria):
                raise ValueError(f"Score list length for {cand} ({len(cand_scores)}) does not match criteria ({len(criteria)})")
            score_matrix[cand] = {crit: float(s) for crit, s in zip(criteria, cand_scores, strict=True)}
        elif isinstance(cand_scores, dict):
            for crit in criteria:
                if crit not in cand_scores:
                    raise ValueError(f"Candidate {cand} missing score for criterion: {crit}")
            score_matrix[cand] = {crit: float(cand_scores[crit]) for crit in criteria}
        else:
            raise TypeError(f"Scores for {cand} must be list or dict")

    # F-05 fix: reject NaN and Inf scores
    for cand in candidates:
        for crit in criteria:
            val = score_matrix[cand][crit]
            if math.isnan(val):
                raise ValueError(f"Score for candidate '{cand}', criterion '{crit}' is NaN — all scores must be finite")
            if math.isinf(val):
                raise ValueError(f"Score for candidate '{cand}', criterion '{crit}' is infinite — all scores must be finite")

    # 1. DEC-500 §3A Hard-Constraint VETO Gate
    if hard_vetoes is not None:
        unknown_hard = set(hard_vetoes.keys()) - set(candidates)
        if unknown_hard:
            raise ValueError(
                f"Hard veto candidate(s) {unknown_hard} are not in candidates list {candidates}. "
                f"This signals a typo or mismatch in candidate naming. Fix the candidate names to match."
            )

    veto_screen_applied = (veto_floors is not None) or (hard_vetoes is not None)
    vetoed_candidates: dict[str, list[str]] = {}
    feasible_candidates: list[str] = []

    # Record any pre-screened hard vetoes
    if hard_vetoes:
        for cand, reasons in hard_vetoes.items():
            if reasons:
                vetoed_candidates[cand] = list(reasons)

    if veto_floors is not None:
        # F-01 fix: fail-closed on empty veto dict
        if not veto_floors:
            raise ValueError(
                "veto_floors is an empty dict — this signals intent to screen but screens nothing. "
                "Provide at least one hard-constraint floor, or pass veto_floors=None to skip screening."
            )
        # F-01 fix: fail-closed on unknown veto keys
        veto_keys = set(veto_floors.keys())
        criteria_keys = set(criteria)
        unknown_keys = veto_keys - criteria_keys
        if unknown_keys:
            raise ValueError(
                f"Veto floor key(s) {unknown_keys} are not scored criteria {criteria_keys}. "
                f"This would silently skip the constraint check (fail-open). "
                f"Fix the key names to match criteria exactly."
            )

        for cand in candidates:
            if cand in vetoed_candidates:
                continue
            breaches = []
            for crit, floor in veto_floors.items():
                actual_score = score_matrix[cand][crit]
                if actual_score < floor:
                    breaches.append(f"Breached {crit} floor ({actual_score:.2f} < {floor:.2f})")
            if breaches:
                vetoed_candidates[cand] = breaches
            else:
                feasible_candidates.append(cand)
    else:
        for cand in candidates:
            if cand not in vetoed_candidates:
                feasible_candidates.append(cand)

    # If all candidates are vetoed
    if not feasible_candidates:
        return MCDAResult(
            candidates=candidates,
            criteria=criteria,
            normalized_weights=normalized_weights,
            composite_scores={},
            ranked_candidates=[],
            winner="NONE",
            runner_up="NONE",
            margin_abs=0.0,
            margin_pct=0.0,
            is_stable=False,
            stability_verdict="INFEASIBLE (All candidates vetoed)",
            perturbation_flips=["ALL CANDIDATES BREACHED HARD CONSTRAINTS"],
            pairwise_dominance=[],
            verdict="NO FEASIBLE PATH — ALL CANDIDATES BREACHED HARD CONSTRAINTS (RETURN TO PHASE 2)",
            vetoed_candidates=vetoed_candidates,
            veto_screen_applied=True,
            ruin_exemptions=dict(ruin_exemptions) if ruin_exemptions else {},
        )

    def calc_scores(w_map: dict[str, float]) -> dict[str, float]:
        return {
            cand: sum(w_map[crit] * score_matrix[cand][crit] for crit in criteria)
            for cand in feasible_candidates
        }

    # Base composite scores on feasible candidates
    base_scores = calc_scores(normalized_weights)
    ranked = sorted(base_scores.items(), key=lambda x: x[1], reverse=True)

    winner, winner_score = ranked[0]
    if len(ranked) > 1:
        runner_up, runner_up_score = ranked[1][0], ranked[1][1]
        margin_abs = winner_score - runner_up_score
        margin_pct = (margin_abs / runner_up_score * 100.0) if runner_up_score > 0 else (100.0 if margin_abs > 0 else 0.0)
    else:
        runner_up = "NONE"
        runner_up_score = 0.0
        margin_abs = winner_score
        margin_pct = 100.0

    # Pairwise dominance checks on feasible candidates
    pairwise_dominance: list[str] = []
    for i, c1 in enumerate(feasible_candidates):
        for c2 in feasible_candidates[i + 1:]:
            c1_dom = all(score_matrix[c1][crit] >= score_matrix[c2][crit] for crit in criteria) and any(score_matrix[c1][crit] > score_matrix[c2][crit] for crit in criteria)
            c2_dom = all(score_matrix[c2][crit] >= score_matrix[c1][crit] for crit in criteria) and any(score_matrix[c2][crit] > score_matrix[c1][crit] for crit in criteria)
            if c1_dom:
                pairwise_dominance.append(f"'{c1}' strictly dominates '{c2}' across all criteria")
            elif c2_dom:
                pairwise_dominance.append(f"'{c2}' strictly dominates '{c1}' across all criteria")
            elif abs(base_scores[c1] - base_scores[c2]) < 1e-9:
                pairwise_dominance.append(f"'{c1}' and '{c2}' are in an exact composite tie ({base_scores[c1]:.3f})")

    # Check whether winner strictly dominates all other feasible alternatives
    is_strictly_dominant_winner = len(feasible_candidates) > 1 and all(
        (all(score_matrix[winner][crit] >= score_matrix[other][crit] for crit in criteria)
         and any(score_matrix[winner][crit] > score_matrix[other][crit] for crit in criteria))
        for other in feasible_candidates if other != winner
    )

    # Sensitivity testing: ±10% perturbation
    perturbation_flips: list[str] = []
    is_stable = True

    if len(feasible_candidates) == 1:
        # Sole surviving candidate after feasibility screen: cannot be flipped
        is_stable = True
    else:
        if margin_pct < margin_threshold_pct:
            if is_strictly_dominant_winner:
                perturbation_flips.append(
                    f"INFORMATIONAL: Winner margin (+{margin_pct:.2f}%) is below {margin_threshold_pct:.1f}% threshold, but '{winner}' strictly dominates all alternatives across all criteria."
                )
            else:
                is_stable = False
                perturbation_flips.append(
                    f"TIE / LOW MARGIN: Winner margin (+{margin_pct:.2f}%) is below {margin_threshold_pct:.1f}% threshold"
                )

        for crit in criteria:
            for delta in [-sensitivity_pct, sensitivity_pct]:
                pert_w = normalized_weights.copy()
                orig_w = pert_w[crit]
                new_w = orig_w * (1.0 + delta)
                diff = new_w - orig_w

                other_sum = sum(w for c, w in pert_w.items() if c != crit)
                if other_sum > 0:
                    for c in criteria:
                        if c == crit:
                            pert_w[c] = new_w
                        else:
                            pert_w[c] -= diff * (pert_w[c] / other_sum)
                else:
                    pert_w[crit] = 1.0

                p_total = sum(pert_w.values())
                pert_w = {c: w / p_total for c, w in pert_w.items()}

                p_scores = calc_scores(pert_w)
                p_ranked = sorted(p_scores.items(), key=lambda x: x[1], reverse=True)
                p_winner = p_ranked[0][0]

                if p_winner != winner:
                    is_stable = False
                    direction = f"+{sensitivity_pct*100:.0f}%" if delta > 0 else f"-{sensitivity_pct*100:.0f}%"
                    perturbation_flips.append(
                        f"Weight drift on {crit} ({direction}) flips winner from '{winner}' to '{p_winner}'"
                    )

    if is_stable:
        if len(feasible_candidates) == 1:
            stability_verdict = "ROBUST (Sole surviving feasible candidate after hard-constraint screen)"
            if veto_screen_applied:
                verdict = f"RECOMMENDED (SCORED) -> '{winner}' IS SOLE FEASIBLE PATH"
            else:
                verdict = f"ADVISORY ONLY (NO VETO SCREEN) -> PRIMARY PREFERENCE IS '{winner}'"
        else:
            stability_verdict = "ROBUST (Stable winner across all ±10% weight perturbations)"
            if veto_screen_applied:
                verdict = f"RECOMMENDED (SCORED) -> '{winner}' WITH CONTINGENCY '{runner_up}'"
            else:
                verdict = f"ADVISORY ONLY (NO VETO SCREEN) -> PRIMARY PREFERENCE IS '{winner}' WITH CONTINGENCY TO '{runner_up}'"
    else:
        stability_verdict = "UNSTABLE (Rank flips or margin < 5% under perturbation)"
        if veto_screen_applied:
            verdict = "UNSTABLE / TIE DETECTED -> DO NOT FORCE PICK; ROUTE TO PATH D (EXPERIMENT) OR PATH E (WAIT)"
        else:
            verdict = "ADVISORY ONLY (NO VETO SCREEN) -> UNSTABLE / TIE DETECTED; ROUTE TO PATH D OR PATH E"

    return MCDAResult(
        candidates=candidates,
        criteria=criteria,
        normalized_weights=normalized_weights,
        composite_scores=base_scores,
        ranked_candidates=ranked,
        winner=winner,
        runner_up=runner_up,
        margin_abs=margin_abs,
        margin_pct=margin_pct,
        is_stable=is_stable,
        stability_verdict=stability_verdict,
        perturbation_flips=perturbation_flips,
        pairwise_dominance=pairwise_dominance,
        verdict=verdict,
        vetoed_candidates=vetoed_candidates,
        veto_screen_applied=veto_screen_applied,
        ruin_exemptions=dict(ruin_exemptions) if ruin_exemptions else {},
    )


class VetoFloorRequired(ValueError):
    """Raised by gto_screen when veto screening is missing or empty.

    gto_screen is a fail-closed entry point enforcing Law #1.
    To run in advisory-only mode without screening, call compute_mcda() explicitly.
    """
    pass


def derive_ruin_floors(
    candidates: list[str],
    ruin_inputs: dict[str, dict[str, Any] | RuinResult],
    target_criterion: str = "Robustness",
    floor_value: float = 5.0,
) -> dict[str, float]:
    """Deprecated: derive hard-constraint veto floors from ruin parameters.

    Use screen_ruin() which directly evaluates computed ruin probabilities.
    """
    import warnings
    warnings.warn(
        "derive_ruin_floors is deprecated. Use screen_ruin() which directly evaluates computed ruin probabilities.",
        DeprecationWarning,
        stacklevel=2,
    )
    if not candidates:
        raise ValueError("candidates list cannot be empty")
    if not ruin_inputs:
        raise ValueError("ruin_inputs cannot be empty — provide ruin data for candidates")

    return {target_criterion: floor_value}


def screen_ruin(
    candidates: list[str],
    ruin_inputs: dict[str, dict[str, Any] | RuinResult | RuinEstimate],
    *,
    ruin_exempt: dict[str, str] | None = None,
) -> dict[str, list[str]]:
    """Evaluates Law #1 conservative ruin probability for candidates.

    Args:
        candidates: List of candidate names to screen.
        ruin_inputs: Dict mapping candidate names to RuinResult, RuinEstimate, or kwargs for compute_ruin_probability.
        ruin_exempt: Dict mapping candidate names to written exemption reasons.

    Returns:
        Dict mapping candidate names that violate Law #1 to list of veto reasons.
        e.g. {"CandA": ["Law #1: conservative ruin 100.0% > 5.0%"]}

    Raises:
        VetoFloorRequired: If any candidate is missing from both ruin_inputs and ruin_exempt.
        ValueError: If exemption reason is too short (< 10 non-space characters) or attempts to exempt a computed violation.
        TypeError: If ruin_inputs value is not a dict, RuinResult, or RuinEstimate.
    """
    if not candidates:
        raise ValueError("candidates list cannot be empty")
    if not ruin_inputs:
        raise ValueError("ruin_inputs cannot be empty — provide ruin data for candidates")

    exempt = ruin_exempt or {}
    for cand, reason in exempt.items():
        if not isinstance(reason, str) or len(reason.strip()) < 10:
            raise ValueError(
                f"Exemption reason for candidate '{cand}' must be at least 10 non-space characters"
            )
        if cand in ruin_inputs:
            c_data = ruin_inputs[cand]
            c_violates = False
            if isinstance(c_data, RuinEstimate):
                c_violates = c_data.p_ruin > LAW1_MAX_RUIN
            elif isinstance(c_data, dict) and "p_ruin" in c_data:
                c_violates = float(c_data["p_ruin"]) > LAW1_MAX_RUIN
            elif isinstance(c_data, RuinResult):
                c_violates = c_data.violates_law1 or (c_data.conservative_ruin_pct > (LAW1_MAX_RUIN * 100.0))
            elif isinstance(c_data, dict):
                c_res = compute_ruin_probability(**c_data)
                c_violates = c_res.violates_law1
            if c_violates:
                raise ValueError(
                    f"Cannot exempt candidate '{cand}' that has a computed Law #1 violation"
                )

    missing = [c for c in candidates if c not in ruin_inputs and c not in exempt]
    if missing:
        raise VetoFloorRequired(
            f"Candidate(s) {missing} missing from ruin_inputs and not in ruin_exempt. "
            f"Fail-closed Law #1 requires every candidate to have verified ruin data or an explicit exemption."
        )

    hard_vetoes: dict[str, list[str]] = {}
    for cand in candidates:
        if cand in exempt:
            continue
        data = ruin_inputs[cand]
        if isinstance(data, RuinEstimate):
            if data.p_ruin > LAW1_MAX_RUIN:
                hard_vetoes[cand] = [
                    f"Law #1: {data.basis} ruin {data.p_ruin * 100.0:.1f}% over {data.horizon} > {LAW1_MAX_RUIN * 100.0:.1f}%"
                ]
            continue
        elif isinstance(data, dict) and "p_ruin" in data:
            est = RuinEstimate(
                p_ruin=float(data["p_ruin"]),
                horizon=str(data.get("horizon", "unspecified")),
                basis=str(data.get("basis", "agent-estimate")),
            )
            if est.p_ruin > LAW1_MAX_RUIN:
                hard_vetoes[cand] = [
                    f"Law #1: {est.basis} ruin {est.p_ruin * 100.0:.1f}% over {est.horizon} > {LAW1_MAX_RUIN * 100.0:.1f}%"
                ]
            continue
        elif isinstance(data, RuinResult):
            res = data
        elif isinstance(data, dict):
            res = compute_ruin_probability(**data)  # type: ignore[arg-type]
        else:
            raise TypeError(f"ruin_inputs for '{cand}' must be dict, RuinResult, or RuinEstimate, got {type(data)}")

        if res.conservative_ruin_pct > (LAW1_MAX_RUIN * 100.0):
            res.violates_law1 = True
        if res.violates_law1:
            hard_vetoes[cand] = [f"Law #1: conservative ruin {res.conservative_ruin_pct:.1f}% > 5.0%"]

    return hard_vetoes


def gto_screen(
    candidates: list[str],
    criteria: list[str],
    weights: list[float] | dict[str, float],
    scores: dict[str, dict[str, float]] | dict[str, list[float]],
    *,
    veto_floors: dict[str, float] | None = None,
    ruin_inputs: dict[str, dict[str, Any] | RuinResult | RuinEstimate] | None = None,
    ruin_exempt: dict[str, str] | None = None,
    ruin_criterion: str = "Robustness",
    ruin_floor: float = 5.0,
    sensitivity_pct: float = 0.10,
    margin_threshold_pct: float = 5.0,
) -> MCDAResult:
    """Fail-closed GTO decision screening entry point.

    Enforces Law #1: raises VetoFloorRequired if veto_floors is None or empty
    and no ruin_inputs are provided.

    If ruin_inputs is supplied, screens candidates against Law #1 (<= 5.0% ruin)
    via screen_ruin and applies them as hard_vetoes.

    To deliberately evaluate options advisory-only without hard vetoes,
    call compute_mcda() directly.
    """
    import warnings

    if ruin_criterion != "Robustness" or ruin_floor != 5.0:
        warnings.warn(
            "ruin_criterion and ruin_floor parameters in gto_screen have no effect since T0.1 "
            "(screen_ruin evaluates computed ruin directly). Pass veto_floors or ruin_inputs instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    if ruin_inputs is None and (veto_floors is None or not veto_floors):
        raise VetoFloorRequired(
            "gto_screen is fail-closed and requires active veto_floors or ruin_inputs to enforce Law #1. "
            "Pass veto_floors={...}, pass ruin_inputs={...}, or use compute_mcda() for explicit advisory-only mode."
        )

    hard_vetoes: dict[str, list[str]] | None = None
    if ruin_inputs is not None:
        hard_vetoes = screen_ruin(candidates, ruin_inputs, ruin_exempt=ruin_exempt)

    return compute_mcda(
        candidates=candidates,
        criteria=criteria,
        weights=weights,
        scores=scores,
        veto_floors=veto_floors,
        hard_vetoes=hard_vetoes,
        ruin_exemptions=dict(ruin_exempt) if ruin_exempt else None,
        sensitivity_pct=sensitivity_pct,
        margin_threshold_pct=margin_threshold_pct,
    )


# Canonical alias
mcda_score = compute_mcda


def compute_dual_vault_barbell(
    fortress_capital: float,
    arena_capital: float,
    monthly_burn: float,
    expected_arena_return: float = 0.20,
    catastrophic_arena_loss_pct: float = 1.0,
    currency: str = "S$",
) -> BarbellAuditResult:
    """Audits capital allocation across DBU (Fortress Vault) and ACU (Convex Arena).

    Enforces the Dual-Vault Barbell Invariant (Protocol 577):
    - Arena allocation must be capped at <= 10.0% of total liquid capital (Law #1).
    - Fortress survival runway must provide at least 12 months of survival at baseline burn.
    """
    if expected_arena_return != 0.20:
        warnings.warn(
            "expected_arena_return is a decorative parameter and is deprecated.",
            DeprecationWarning,
            stacklevel=2,
        )
    if catastrophic_arena_loss_pct != 1.0:
        warnings.warn(
            "catastrophic_arena_loss_pct is a decorative parameter and is deprecated.",
            DeprecationWarning,
            stacklevel=2,
        )

    if fortress_capital < 0.0 or arena_capital < 0.0:
        raise ValueError("Fortress and arena capital must be non-negative.")
    if monthly_burn <= 0.0:
        raise ValueError("Monthly burn must be positive.")

    total_capital = fortress_capital + arena_capital
    arena_fraction = (arena_capital / total_capital) if total_capital > 0.0 else 0.0
    fortress_runway_months = fortress_capital / monthly_burn

    # Ruin condition: Arena fraction > ARENA_MAX_FRACTION breaches Law #1
    if arena_fraction > ARENA_MAX_FRACTION:
        ruin_violation = True
        verdict = f"VETO: Arena allocation ({arena_fraction * 100:.1f}%) exceeds {ARENA_MAX_FRACTION * 100:.1f}% ceiling. Violates Law #1."
    elif fortress_runway_months < FORTRESS_MIN_RUNWAY_MONTHS:
        ruin_violation = True
        verdict = f"VETO: Fortress runway ({fortress_runway_months:.1f} mo) under {FORTRESS_MIN_RUNWAY_MONTHS:.1f} mo buffer. Insufficient DBU protection."
    else:
        ruin_violation = False
        verdict = "PASS: Dual-Vault Barbell verified. DBU fortress insulated; ACU arena strictly bounded."

    return BarbellAuditResult(
        fortress_capital=fortress_capital,
        arena_capital=arena_capital,
        total_capital=total_capital,
        arena_fraction=arena_fraction,
        monthly_burn=monthly_burn,
        fortress_runway_months=fortress_runway_months,
        expected_arena_return=expected_arena_return,
        catastrophic_arena_loss_pct=catastrophic_arena_loss_pct,
        ruin_violation=ruin_violation,
        verdict=verdict,
        currency=currency,
    )


def compute_internal_devaluation(
    current_burn: float,
    reduced_burn: float,
    liquid_reserves: float,
    post_shock_income: float = 0.0,
    currency: str = "S$",
) -> InternalDevaluationResult:
    """Computes survival runway extension under Sovereign Internal Devaluation vs Boxer Fallacy.

    Compares:
    - Boxer strategy: maintaining pre-shock burn and attempting to 'work harder'
    - Sovereign strategy: immediately compressing burn rate to the floor
    """
    if current_burn <= 0.0 or reduced_burn <= 0.0:
        raise ValueError("Current burn and reduced burn must be positive.")
    if reduced_burn > current_burn:
        raise ValueError("Reduced burn must be less than or equal to current burn.")
    if liquid_reserves < 0.0 or post_shock_income < 0.0:
        raise ValueError("Reserves and income must be non-negative.")

    burn_reduction_pct = ((current_burn - reduced_burn) / current_burn) * 100.0

    net_deficit_boxer = max(0.0, current_burn - post_shock_income)
    boxer_runway_months = (liquid_reserves / net_deficit_boxer) if net_deficit_boxer > 0.0 else float("inf")

    net_deficit_sovereign = max(0.0, reduced_burn - post_shock_income)

    if net_deficit_sovereign == 0.0:
        is_infinite_runway = True
        sovereign_runway_months = float("inf")
        runway_expansion_factor = float("inf")
        verdict = "SOVEREIGN ESCAPE: Reduced burn fully covered by post-shock income. Runway is infinite."
    else:
        is_infinite_runway = False
        sovereign_runway_months = liquid_reserves / net_deficit_sovereign
        if boxer_runway_months > 0.0 and math.isfinite(boxer_runway_months):
            runway_expansion_factor = sovereign_runway_months / boxer_runway_months
        elif math.isinf(boxer_runway_months):
            # Boxer already infinite (income >= current_burn) but sovereign isn't
            # (income < reduced_burn somehow — unusual, but handle gracefully)
            runway_expansion_factor = 1.0
        else:
            runway_expansion_factor = 1.0
        verdict = (
            f"STABILIZED: Runway expanded by {runway_expansion_factor:.1f}x "
            f"({sovereign_runway_months:.1f} months vs {boxer_runway_months:.1f} months)."
        )

    return InternalDevaluationResult(
        current_burn=current_burn,
        reduced_burn=reduced_burn,
        burn_reduction_pct=burn_reduction_pct,
        liquid_reserves=liquid_reserves,
        post_shock_income=post_shock_income,
        boxer_runway_months=boxer_runway_months,
        sovereign_runway_months=sovereign_runway_months,
        runway_expansion_factor=runway_expansion_factor,
        is_infinite_runway=is_infinite_runway,
        verdict=verdict,
        currency=currency,
    )


def compute_borrow_vulnerability(
    counterparty_exposure: float,
    total_net_worth: float,
    unilateral_freeze_power: bool = False,
    unhedged_credit: bool = False,
    upstream_spec_complete: bool = True,
    currency: str = "S$",
) -> BorrowVulnerabilityResult:
    """Computes the Borrow Vulnerability Index (BVI) under Kingdom Logistics (Protocol 577).

    Evaluates whether an operator has conceded unhedged leverage to a counterparty:
    - Exposure fraction on counterparty rails
    - Unilateral terms alteration / asset freeze rights
    - Unhedged credit delivery (work delivered before payment clears)
    - Upstream specification completeness
    """
    if counterparty_exposure < 0.0 or total_net_worth < 0.0:
        raise ValueError("Exposure and net worth must be non-negative.")

    exposure_pct = (counterparty_exposure / total_net_worth * 100.0) if total_net_worth > 0.0 else 0.0

    score = 0.0
    # Exposure contribution (up to 40 pts)
    score += min(40.0, exposure_pct * 2.0)
    # Unilateral freeze or regulatory terms power (25 pts)
    if unilateral_freeze_power:
        score += 25.0
    # Unhedged credit (work delivered before payment) (25 pts)
    if unhedged_credit:
        score += 25.0
    # Incomplete upstream spec (10 pts)
    if not upstream_spec_complete:
        score += 10.0

    bvi_score = min(100.0, score)

    # Law #1 Ruin condition: BVI >= BVI_RUIN_SCORE or exposure > BVI_FREEZE_EXPOSURE_PCT with unilateral freeze power
    if bvi_score >= BVI_RUIN_SCORE or (exposure_pct > BVI_FREEZE_EXPOSURE_PCT and unilateral_freeze_power):
        ruin_violation = True
        verdict = "CRITICAL VULNERABILITY: Severe borrow exposure. Sever counterparty supply lines immediately."
    elif bvi_score >= 35.0:
        ruin_violation = False
        verdict = "ELEVATED FRICTION: Enforce milestone gating and reduce exposed capital to sacrificial tranche."
    else:
        ruin_violation = False
        verdict = "CONTAINED: Fortress intact; counterparty holds zero unhedged leverage."

    return BorrowVulnerabilityResult(
        counterparty_exposure=counterparty_exposure,
        total_net_worth=total_net_worth,
        exposure_pct=exposure_pct,
        unilateral_freeze_power=unilateral_freeze_power,
        unhedged_credit=unhedged_credit,
        upstream_spec_complete=upstream_spec_complete,
        bvi_score=bvi_score,
        ruin_violation=ruin_violation,
        verdict=verdict,
        currency=currency,
    )



def _safe_json_default(obj: Any) -> Any:
    """Handle non-JSON-serializable values (inf, -inf, NaN) for safe JSON output."""
    if isinstance(obj, float):
        if math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        if math.isnan(obj):
            return "NaN"
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _serialize_for_json(d: dict[str, Any]) -> dict[str, Any]:
    """Recursively replace inf/nan floats with string sentinels for JSON safety."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
            out[k] = "Infinity" if (math.isinf(v) and v > 0) else ("-Infinity" if math.isinf(v) else "NaN")
        elif isinstance(v, dict):
            out[k] = _serialize_for_json(v)
        else:
            out[k] = v
    return out


def get_receipts_path() -> Path:
    """Discover the decision receipts JSONL path with environment override."""
    env_path = os.environ.get("ATHENA_RECEIPTS_PATH")
    if env_path:
        return Path(env_path).resolve()
    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        return Path(env_root).resolve() / ".athena" / "decision_receipts.jsonl"
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".athena_root").exists() or (parent / ".context").exists():
            return parent / ".athena" / "decision_receipts.jsonl"
    return cwd / ".athena" / "decision_receipts.jsonl"


def _get_cal_ledger_path() -> Path:
    """Discover the calibration ledger path with environment override."""
    env_cal = os.environ.get("ATHENA_CAL_LEDGER_PATH")
    if env_cal:
        return Path(env_cal).resolve()
    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        return Path(env_root).resolve() / ".context" / "calibration" / "CALIBRATION_LEDGER.md"
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".context").exists():
            return parent / ".context" / "calibration" / "CALIBRATION_LEDGER.md"
    return cwd / ".context" / "calibration" / "CALIBRATION_LEDGER.md"


def extract_verdict(res: Any) -> str:
    """Extract strategic verdict string from result object."""
    if hasattr(res, "verdict") and res.verdict:
        return str(res.verdict)
    if hasattr(res, "candidate_stats") and hasattr(res, "top_candidate") and res.top_candidate:
        cand_stat = res.candidate_stats.get(res.top_candidate)
        if cand_stat and hasattr(cand_stat, "verdict"):
            return str(cand_stat.verdict)
    return "N/A"


def extract_top(res: Any) -> str:
    """Extract top candidate / winning policy from result object."""
    if hasattr(res, "top_candidate") and res.top_candidate:
        return str(res.top_candidate)
    if hasattr(res, "minimax_regret_winner") and res.minimax_regret_winner:
        return str(res.minimax_regret_winner)
    if hasattr(res, "winner") and res.winner:
        return str(res.winner)
    if hasattr(res, "preferred_strategy") and res.preferred_strategy:
        return str(res.preferred_strategy)
    return "N/A"


def log_decision_receipt(
    action: str,
    inputs: Any,
    result: Any,
    receipts_path: Path | None = None,
    real_decision: bool = False,
    review_date: str | None = None,
    prediction: str | None = None,
    cal_ledger_path: Path | None = None,
) -> dict[str, Any]:
    """Append a verified decision receipt to .athena/decision_receipts.jsonl.

    When real_decision is True, also appends a CALIBRATION_LEDGER entry (09-30 T4.1).
    """
    if isinstance(inputs, str):
        inputs_str = inputs
    elif isinstance(inputs, dict):
        inputs_str = json.dumps(_serialize_for_json(inputs), sort_keys=True)
    else:
        inputs_str = str(inputs)

    if hasattr(result, "__dataclass_fields__"):
        outputs_str = json.dumps(_serialize_for_json(asdict(result)), sort_keys=True)
    elif isinstance(result, dict):
        outputs_str = json.dumps(_serialize_for_json(result), sort_keys=True)
    else:
        outputs_str = str(result)

    combined = inputs_str + outputs_str
    receipt_id = f"GTO-{hashlib.sha256(combined.encode('utf-8')).hexdigest()[:8]}"
    input_sha256 = hashlib.sha256(inputs_str.encode("utf-8")).hexdigest()
    ts = datetime.now(timezone.utc).isoformat()
    verdict = extract_verdict(result)
    top = extract_top(result)

    entry = {
        "receipt_id": receipt_id,
        "ts": ts,
        "action": action,
        "verdict": verdict,
        "top": top,
        "input_sha256": input_sha256,
        "real_decision": bool(real_decision),
        "review_date": review_date if review_date else None,
        "prediction": prediction if prediction else None,
    }

    path = receipts_path or get_receipts_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        warnings.warn(f"Failed to write decision receipt to {path}: {exc}", RuntimeWarning, stacklevel=2)

    # T4.1: If real_decision, append an entry to CALIBRATION_LEDGER
    if real_decision:
        try:
            cal_file = cal_ledger_path or _get_cal_ledger_path()
            if cal_file.exists():
                cal_content = cal_file.read_text(encoding="utf-8")
                cal_nums = [int(m) for m in re.findall(r"###\s+CAL-(\d+)", cal_content)]
                next_cal = max(cal_nums) + 1 if cal_nums else 1
                new_cal_id = f"CAL-{next_cal:03d}"
                dl = review_date if review_date else (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
                claim = prediction if prediction else f"GTO decision '{action}' recommendation '{top}' achieves superior performance with verdict '{verdict}'."
                domain = "trading" if action in ("kelly", "ruin", "drawdown") else "technical"

                cal_entry = (
                    f"### {new_cal_id}\n"
                    f"- **Claim**: {claim}\n"
                    f"- **Probability**: 0.70\n"
                    f"- **Deadline**: {dl}\n"
                    f"- **Domain**: {domain}\n"
                    f"- **Rationale**: Real decision logged via GTO Engine receipt {receipt_id}. Action: {action}. Verdict: {verdict}. Top: {top}.\n"
                    f"- **Source**: {receipt_id}\n"
                    f"- **Outcome**: pending\n"
                    f"- **Resolved**: —\n\n"
                )

                template_marker = "-->\n"
                if "## Active Predictions" in cal_content:
                    active_idx = cal_content.find("## Active Predictions")
                    marker_idx = cal_content.find(template_marker, active_idx)
                    if marker_idx != -1:
                        insert_pos = marker_idx + len(template_marker)
                        cal_content = cal_content[:insert_pos] + "\n" + cal_entry + cal_content[insert_pos:].lstrip("\n")
                    else:
                        insert_pos = active_idx + len("## Active Predictions\n\n")
                        cal_content = cal_content[:insert_pos] + cal_entry + cal_content[insert_pos:]
                    cal_file.write_text(cal_content, encoding="utf-8")
        except Exception as exc:
            warnings.warn(f"Failed to append to CALIBRATION_LEDGER: {exc}", RuntimeWarning, stacklevel=2)

    return entry


def execute_decision_action(
    action: str,
    payload: dict[str, Any],
    real: bool = False,
    review_date: str | None = None,
    prediction: str | None = None,
    no_receipt: bool = False,
    receipts_path: Path | None = None,
    cal_ledger_path: Path | None = None,
) -> tuple[Any, dict[str, Any] | None]:
    """Execute a strategic decision action and optionally log a decision receipt."""
    res: Any
    if action == "robustness":
        res = compute_robustness(
            policies=payload["policies"],
            scenarios=payload["scenarios"],
            payoff=payload["payoff"],
            ruin=payload.get("ruin"),
            probs=payload.get("probs"),
            wealth=payload.get("wealth"),
            barrier=payload.get("barrier", 0.0),
            cvar_alpha=payload.get("cvar_alpha", 0.10),
            tail_factor=payload.get("tail_factor", 3.0),
        )
    elif action == "mcda":
        has_ruin = bool(payload.get("ruin_inputs")) or payload.get("require_veto", False)
        extra_kwargs: dict[str, Any] = {}
        if "ruin_criterion" in payload:
            extra_kwargs["ruin_criterion"] = payload["ruin_criterion"]
        if "ruin_floor" in payload:
            extra_kwargs["ruin_floor"] = payload["ruin_floor"]
        if has_ruin:
            res = gto_screen(
                candidates=payload["candidates"],
                criteria=payload["criteria"],
                weights=payload["weights"],
                scores=payload["scores"],
                sensitivity_pct=payload.get("sensitivity_pct", 0.10),
                margin_threshold_pct=payload.get("margin_threshold_pct", 5.0),
                veto_floors=payload.get("veto_floors"),
                ruin_inputs=payload.get("ruin_inputs"),
                ruin_exempt=payload.get("ruin_exempt"),
                **extra_kwargs,
            )
        else:
            res = compute_mcda(
                candidates=payload["candidates"],
                criteria=payload["criteria"],
                weights=payload["weights"],
                scores=payload["scores"],
                sensitivity_pct=payload.get("sensitivity_pct", 0.10),
                margin_threshold_pct=payload.get("margin_threshold_pct", 5.0),
                veto_floors=payload.get("veto_floors"),
            )
    elif action == "decision-mc":
        raw_states = payload["states"]
        mc_states: dict[str, list[tuple[Any, ...] | dict[str, Any]]] = {}
        for cand, st_list in raw_states.items():
            mc_states[cand] = [tuple(item) for item in st_list]
        res = run_decision_monte_carlo(
            candidates=payload["candidates"],
            states=mc_states,
            n=payload.get("n", 2000),
            prob_jitter=payload.get("prob_jitter", 0.20),
            seed=payload.get("seed", 42),
            wealth=payload.get("wealth"),
            materiality=payload.get("materiality", 0.01),
            barrier=payload.get("barrier", 0.0),
            sample_outcomes=payload.get("sample_outcomes", False),
            tail_uncertainty=payload.get("tail_uncertainty", 1.0),
        )
    elif action == "growth-rate":
        raw_states = payload["states"]
        states_list: list[tuple[Any, ...] | dict[str, Any]] = [tuple(item) for item in raw_states]
        res = compute_growth_rate(
            wealth=payload["wealth"],
            states=states_list,
            barrier=payload.get("barrier", 0.0),
        )
    elif action == "eev":
        res = compute_eev(
            mev=payload.get("mev", 1000.0),
            eu=payload.get("eu", payload.get("friction", 200.0)),
            eo=payload.get("eo", payload.get("opportunity_cost", 100.0)),
            skeptic_discount=payload.get("discount", payload.get("skeptic_discount", 0.15)),
            utility=payload.get("utility", 0.0),
            friction=payload.get("friction"),
            opportunity_cost=payload.get("opportunity_cost"),
        )
    elif action == "kelly":
        res = compute_half_kelly(
            win_rate=payload["win_rate"],
            payoff_ratio=payload["payoff"],
            variance_drag=payload.get("variance_drag", 0.5),
        )
    elif action == "ruin":
        res = compute_ruin_probability(
            win_rate=payload["win_rate"],
            payoff_ratio=payload["payoff"],
            risk_per_trade_fraction=payload.get("risk_fraction", 0.02),
            ruin_drawdown_threshold=payload.get("ruin_threshold", 0.5),
        )
    elif action == "monte-carlo":
        initial_cap = payload.get("capital", 10000.0)
        res = run_monte_carlo_simulation(
            initial_capital=initial_cap,
            win_rate=payload["win_rate"],
            payoff_ratio=payload["payoff"],
            risk_fraction=payload.get("risk_fraction", 0.02),
            n_trials=payload.get("trials", 10000),
            n_steps=payload.get("steps", 100),
            left_tail_shock_prob=payload.get("shock_prob", 0.01),
            left_tail_shock_loss=payload.get("shock_loss", 0.10),
        )
    elif action == "barbell":
        res = compute_dual_vault_barbell(
            fortress_capital=payload["fortress"],
            arena_capital=payload["arena"],
            monthly_burn=payload["burn"],
            currency=payload.get("currency", "S$"),
        )
    elif action == "devaluation":
        reserves_val = payload.get("liquid_reserves", payload.get("capital"))
        reserves = float(reserves_val) if reserves_val is not None else 0.0
        res = compute_internal_devaluation(
            current_burn=payload["current_burn"],
            reduced_burn=payload["reduced_burn"],
            liquid_reserves=reserves,
            post_shock_income=payload.get("post_shock_income", 0.0),
            currency=payload.get("currency", "S$"),
        )
    elif action == "borrow-audit":
        net_worth_val = payload.get("net_worth", payload.get("capital"))
        net_worth = float(net_worth_val) if net_worth_val is not None else 0.0
        res = compute_borrow_vulnerability(
            counterparty_exposure=payload["exposure"],
            total_net_worth=net_worth,
            unilateral_freeze_power=payload.get("freeze_power", False),
            unhedged_credit=payload.get("unhedged_credit", False),
            upstream_spec_complete=payload.get("upstream_spec_complete", not payload.get("upstream_spec_incomplete", False)),
            currency=payload.get("currency", "S$"),
        )
    else:
        raise ValueError(f"Unknown action: {action}")

    receipt: dict[str, Any] | None = None
    if not no_receipt:
        receipt = log_decision_receipt(
            action=action,
            inputs=payload,
            result=res,
            receipts_path=receipts_path,
            real_decision=real,
            review_date=review_date,
            prediction=prediction,
            cal_ledger_path=cal_ledger_path,
        )

    return res, receipt


UNRECEIPTED_CLAIM_PATTERNS: list[str] = [
    r"Law #1 (?:PASS|VETO)",
    r"RECOMMENDED \(SCORED\)",
    r"\bhard-vetoed\b",
    r"\b(?:ran|executed) (?:a |the )?(?:decision )?Monte Carlo\b",
    r"\bMonte Carlo (?:confirms|shows|verdict)\b",
    r"\bcode-enforced\b",
    r"\bGTO (?:confirmed|verified|verdict)\b",
    r"\bguarantee\w*\s+(?:\w+\s+)?survival\b",
    r"P\(ruin\)\s*(?:<=|<|≤)\s*\d+(?:\.\d+)?\s*%",
]


def find_unreceipted_engine_claims(
    text: str,
    receipts_path: Path | None = None,
) -> list[str]:
    """Scan text for GTO engine assertions that lack a valid receipt or [agent-estimate] tag.

    Vocabulary heuristic; catches recurrences of known phrasings, not paraphrases.
    Returns a list of unreceipted claim phrases found in the text.
    Allowed if a valid GTO-xxxxxxxx receipt ID cited in the text exists in the
    last 500 lines of .athena/decision_receipts.jsonl, or if the individual
    sentence containing the claim carries '[agent-estimate]'.
    """
    if not text:
        return []

    path = receipts_path or get_receipts_path()
    valid_receipt_ids: set[str] = set()

    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()[-500:]
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if "receipt_id" in entry:
                            valid_receipt_ids.add(entry["receipt_id"])
                    except json.JSONDecodeError:
                        m = re.search(r'"receipt_id":\s*"(GTO-[0-9a-fA-F]{8})"', line)
                        if m:
                            valid_receipt_ids.add(m.group(1))
        except Exception:
            pass

    # If any valid receipt ID from receipts file is cited in the text, all claims are receipted
    cited_ids = re.findall(r"\b(GTO-[0-9a-fA-F]{8})\b", text)
    if any(rid in valid_receipt_ids for rid in cited_ids):
        return []

    # Check sentence-by-sentence
    sentences = re.split(r"(?<=[.!?\n])\s+", text)
    violations: list[str] = []

    for sentence in sentences:
        s_clean = sentence.strip()
        if not s_clean:
            continue
        if "[agent-estimate]" in s_clean.lower():
            continue
        for pat in UNRECEIPTED_CLAIM_PATTERNS:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                violations.append(m.group(0))

    return list(dict.fromkeys(violations))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Athena GTO Numerical Computation Engine (ASCII Math Only)"
    )
    parser.add_argument(
        "--action",
        choices=[
            "eev",
            "kelly",
            "ruin",
            "monte-carlo",
            "mcda",
            "decision-mc",
            "robustness",
            "barbell",
            "devaluation",
            "borrow-audit",
        ],
        required=False,
        help="Calculation action to execute",
    )
    parser.add_argument("--capabilities", action="store_true", help="Print capability manifest JSON")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Calibration & Decision Receipt parameters (T3.1, T4.1)
    parser.add_argument("--real", action="store_true", default=False, help="Flag this run as a consequential real decision")
    parser.add_argument("--review-date", type=str, default=None, help="Calibration review date (YYYY-MM-DD)")
    parser.add_argument("--prediction", type=str, default=None, help="Anticipated hypothesis / prediction for calibration tracking")
    parser.add_argument("--no-receipt", action="store_true", default=False, help="Skip appending to decision receipts")
    parser.add_argument("--cal-ledger", type=str, default=None, help="Path to CALIBRATION_LEDGER.md (for --real logging)")

    # MCDA, Decision MC & Robustness parameters
    parser.add_argument("--input", type=str, help="JSON string or file path containing input data for action (e.g. robustness matrix)")
    parser.add_argument("--mcda-json", type=str, help="JSON string or file path containing MCDA inputs")
    parser.add_argument("--mc-json", type=str, help="JSON string or file path containing decision Monte Carlo inputs")
    parser.add_argument(
        "--require-veto",
        action="store_true",
        help="Enforce fail-closed Law #1 veto screening via gto_screen (raises if veto_floors is missing)",
    )

    # EEV parameters
    parser.add_argument("--mev", type=float, default=1000.0, help="Monetary Expected Value")
    parser.add_argument("--eu", type=float, default=200.0, help="Execution & Friction Drag")
    parser.add_argument("--eo", type=float, default=100.0, help="Opportunity & Attention Cost")
    parser.add_argument("--discount", type=float, default=0.15, help="Skeptic Discount (0.0-1.0)")
    parser.add_argument("--utility", type=float, default=0.0, help="Expected Utility E(U) in S$")
    parser.add_argument("--friction", type=float, default=None, help="Execution & Friction Drag (alias for --eu)")
    parser.add_argument("--opportunity-cost", type=float, default=None, help="Opportunity & Attention Cost (alias for --eo)")

    # Kelly & Ruin parameters
    parser.add_argument("--win-rate", type=float, default=0.55, help="Win rate fraction (0.0-1.0)")
    parser.add_argument("--payoff", type=float, default=1.5, help="Payoff ratio (Win/Loss)")
    parser.add_argument("--variance-drag", type=float, default=0.5, help="Variance Drag factor")
    parser.add_argument("--risk-fraction", type=float, default=0.02, help="Risk fraction per trade")
    parser.add_argument("--ruin-threshold", type=float, default=0.5, help="Ruin drawdown threshold")

    # Monte Carlo parameters
    parser.add_argument("--capital", type=float, default=None, help="Capital (deprecated for devaluation/borrow-audit; use --liquid-reserves or --net-worth)")
    parser.add_argument("--trials", type=int, default=10000, help="Monte Carlo trial count")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps per trial")
    parser.add_argument("--shock-prob", type=float, default=0.01, help="Left-tail shock probability")
    parser.add_argument("--shock-loss", type=float, default=0.10, help="Left-tail shock loss fraction")

    # Dual-Vault Barbell parameters (Protocol 577)
    parser.add_argument("--fortress", type=float, default=None, help="Fortress Vault (DBU) capital")
    parser.add_argument("--arena", type=float, default=None, help="Speculative Arena (ACU) capital")
    parser.add_argument("--burn", type=float, default=None, help="Baseline monthly burn rate")

    # Internal Devaluation parameters
    parser.add_argument("--current-burn", type=float, default=None, help="Pre-devaluation monthly burn rate")
    parser.add_argument("--reduced-burn", type=float, default=None, help="Post-devaluation monthly burn rate")
    parser.add_argument("--liquid-reserves", type=float, default=None, help="Liquid cash reserves for devaluation")
    parser.add_argument("--post-shock-income", type=float, default=0.0, help="Post-shock ongoing monthly cash income")

    # Borrow Vulnerability parameters (Kingdom Logistics)
    parser.add_argument("--exposure", type=float, default=None, help="Counterparty exposure capital")
    parser.add_argument("--net-worth", type=float, default=None, help="Total sovereign net worth for borrow audit")
    parser.add_argument("--freeze-power", action="store_true", help="Counterparty holds unilateral terms/freeze rights")
    parser.add_argument("--unhedged-credit", action="store_true", help="Work or capital delivered prior to payment clearance")
    parser.add_argument("--upstream-spec-incomplete", action="store_true", help="Upstream specification or invariants are incomplete")

    # Currency parameter
    parser.add_argument("--currency", type=str, default="S$", help="Currency denomination symbol (e.g. S$, USD, US$)")

    args = parser.parse_args(argv)
    if args.capabilities:
        print(json.dumps(CAPABILITY_MANIFEST, indent=2))
        return 0
    if not args.action:
        parser.error("--action is required when not querying --capabilities")

    try:
        payload: dict[str, Any]
        if args.action == "mcda":
            input_val = args.mcda_json or args.input
            if not input_val:
                raise ValueError("--mcda-json is required when --action is mcda")
            if os.path.exists(input_val):
                with open(input_val, encoding="utf-8") as f:
                    payload = json.load(f)
            else:
                payload = json.loads(input_val)
            if args.require_veto:
                payload["require_veto"] = True
        elif args.action == "decision-mc":
            input_val = args.mc_json or args.input
            if not input_val:
                raise ValueError("--mc-json is required when --action is decision-mc")
            if os.path.exists(input_val):
                with open(input_val, encoding="utf-8") as f:
                    payload = json.load(f)
            else:
                payload = json.loads(input_val)
        elif args.action == "robustness":
            input_val = args.input or args.mcda_json or args.mc_json
            if not input_val:
                print("Error: --action robustness requires --input <matrix.json>", file=sys.stderr)
                return 2
            if os.path.exists(input_val):
                with open(input_val, encoding="utf-8") as f:
                    payload = json.load(f)
            else:
                payload = json.loads(input_val)
        elif args.action == "eev":
            payload = {
                "mev": args.mev,
                "eu": args.eu if args.friction is None else args.friction,
                "eo": args.eo if args.opportunity_cost is None else args.opportunity_cost,
                "discount": args.discount,
                "utility": args.utility,
            }
        elif args.action == "kelly":
            payload = {
                "win_rate": args.win_rate,
                "payoff": args.payoff,
                "variance_drag": args.variance_drag,
            }
        elif args.action == "ruin":
            payload = {
                "win_rate": args.win_rate,
                "payoff": args.payoff,
                "risk_fraction": args.risk_fraction,
                "ruin_threshold": args.ruin_threshold,
            }
        elif args.action == "monte-carlo":
            payload = {
                "capital": args.capital if args.capital is not None else 10000.0,
                "win_rate": args.win_rate,
                "payoff": args.payoff,
                "risk_fraction": args.risk_fraction,
                "trials": args.trials,
                "steps": args.steps,
                "shock_prob": args.shock_prob,
                "shock_loss": args.shock_loss,
            }
        elif args.action == "barbell":
            missing = [f for f, v in [("--fortress", args.fortress), ("--arena", args.arena), ("--burn", args.burn)] if v is None]
            if missing:
                print(f"Error: --action barbell requires flags: {', '.join(missing)}", file=sys.stderr)
                return 2
            payload = {
                "fortress": args.fortress,
                "arena": args.arena,
                "burn": args.burn,
                "currency": args.currency,
            }
        elif args.action == "devaluation":
            reserves = args.liquid_reserves
            if reserves is None and args.capital is not None:
                warnings.warn("--capital is deprecated for devaluation; use --liquid-reserves", DeprecationWarning, stacklevel=2)
                reserves = args.capital
            missing = []
            if args.current_burn is None:
                missing.append("--current-burn")
            if args.reduced_burn is None:
                missing.append("--reduced-burn")
            if reserves is None:
                missing.append("--liquid-reserves")
            if missing:
                print(f"Error: --action devaluation requires flags: {', '.join(missing)}", file=sys.stderr)
                return 2
            payload = {
                "current_burn": args.current_burn,
                "reduced_burn": args.reduced_burn,
                "liquid_reserves": reserves,
                "post_shock_income": args.post_shock_income,
                "currency": args.currency,
            }
        elif args.action == "borrow-audit":
            net_worth = args.net_worth
            if net_worth is None and args.capital is not None:
                warnings.warn("--capital is deprecated for borrow-audit; use --net-worth", DeprecationWarning, stacklevel=2)
                net_worth = args.capital
            missing = []
            if args.exposure is None:
                missing.append("--exposure")
            if net_worth is None:
                missing.append("--net-worth")
            if missing:
                print(f"Error: --action borrow-audit requires flags: {', '.join(missing)}", file=sys.stderr)
                return 2
            payload = {
                "exposure": args.exposure,
                "net_worth": net_worth,
                "freeze_power": args.freeze_power,
                "unhedged_credit": args.unhedged_credit,
                "upstream_spec_incomplete": args.upstream_spec_incomplete,
                "currency": args.currency,
            }
        else:
            raise ValueError(f"Unknown action: {args.action}")

        res, receipt = execute_decision_action(
            action=args.action,
            payload=payload,
            real=args.real,
            review_date=args.review_date,
            prediction=args.prediction,
            no_receipt=args.no_receipt,
            cal_ledger_path=Path(args.cal_ledger) if args.cal_ledger else None,
        )

        if args.json:
            out = _serialize_for_json(asdict(res)) if hasattr(res, "__dataclass_fields__") else {"result": res}
            if receipt:
                out["receipt_id"] = receipt["receipt_id"]
            print(json.dumps(out, indent=2))
        else:
            print(res.to_ascii_table() if hasattr(res, "to_ascii_table") else str(res))
            if receipt:
                print(f"receipt: {receipt['receipt_id']}")

        return 0
    except Exception as exc:
        print(f"Error executing GTO engine: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

