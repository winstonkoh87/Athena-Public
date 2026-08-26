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
import json
import math
import random
import sys
from dataclasses import asdict, dataclass
from typing import Any


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

    def to_ascii_table(self) -> str:
        lines = [
            "============================================================",
            "           ECONOMIC EXPECTED VALUE (EEV) AUDIT              ",
            "============================================================",
            f"  Gross Monetary EV (MEV)       : S${self.mev:,.2f}",
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
            f"  95% Confidence Interval       : [S${self.ci_95_lower:,.2f}, S${self.ci_95_upper:,.2f}]",
            f"  99% Confidence Interval       : [S${self.ci_99_lower:,.2f}, S${self.ci_99_upper:,.2f}]",
            "------------------------------------------------------------",
            f"  Mean Max Drawdown             : -{self.mean_max_drawdown_pct:.1f}%",
            f"  Worst-Case Max Drawdown (99th): -{self.worst_drawdown_pct:.1f}%",
            f"  Ruin Probability (< -50% DD)  : {self.ruin_probability_pct:.2f}%",
            "============================================================",
        ]
        return "\n".join(lines)


def compute_eev(
    mev: float,
    eu: float,
    eo: float,
    skeptic_discount: float = 0.15,
) -> EEVResult:
    """Computes Economic Expected Value (EEV).

    EEV = (MEV - EU - EO) * (1.0 - skeptic_discount)
    """
    if skeptic_discount < 0.0 or skeptic_discount >= 1.0:
        raise ValueError("skeptic_discount must be in range [0.0, 1.0)")

    raw_ev = mev - eu - eo
    net_eev = raw_ev * (1.0 - skeptic_discount)
    total_drag = eu + eo
    roi_percent = (net_eev / total_drag * 100.0) if total_drag > 0 else (100.0 if net_eev > 0 else 0.0)

    if net_eev > 0 and roi_percent >= 50.0:
        verdict = "APPROVE (+EV Asymmetric Opportunity)"
    elif net_eev > 0:
        verdict = "MARGINAL (+EV but High Drag / Low Margin)"
    else:
        verdict = "REJECT (-EV Drain / Negative Asymmetry)"

    return EEVResult(
        mev=mev,
        eu=eu,
        eo=eo,
        skeptic_discount=skeptic_discount,
        raw_ev=raw_ev,
        net_eev=net_eev,
        roi_percent=roi_percent,
        verdict=verdict,
    )


def compute_half_kelly(
    win_rate: float,
    payoff_ratio: float,
    variance_drag: float = 0.5,
) -> KellyResult:
    """Calculates Half-Kelly position sizing with variance dampening.

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
        verdict = "NO BET (-EV or Zero Edge)"
    else:
        full_k = f_star
        half_k = f_star * 0.5
        quarter_k = f_star * 0.25
        rec_fraction = half_k * (1.0 - max(0.0, min(0.9, variance_drag - 0.5)))
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
    )


def compute_ruin_probability(
    win_rate: float,
    payoff_ratio: float,
    risk_per_trade_fraction: float,
    ruin_drawdown_threshold: float = 0.5,
    trials_for_sim: int = 10000,
    steps_for_sim: int = 200,
) -> RuinResult:
    """Calculates both analytical and empirical Gambler's Ruin probability."""
    if not (0.0 < win_rate < 1.0):
        raise ValueError("win_rate must be strictly between 0 and 1")
    if payoff_ratio <= 0.0 or risk_per_trade_fraction <= 0.0:
        raise ValueError("payoff_ratio and risk_per_trade_fraction must be positive")

    p = win_rate
    q = 1.0 - p
    b = payoff_ratio
    edge = (p * b) - q

    # Analytical approximation of ruin:
    # Units to ruin = ruin_drawdown_threshold / risk_per_trade_fraction
    units = ruin_drawdown_threshold / risk_per_trade_fraction
    if edge <= 0.0:
        analytical_ruin = 1.0
    else:
        # Standard random walk ruin equation approximation:
        # P(Ruin) = (q / (p * b)) ^ units
        ratio = q / (p * b) if (p * b) > 0 else 1.0
        analytical_ruin = min(1.0, math.pow(ratio, units)) if ratio < 1.0 else 1.0

    # Empirical Monte Carlo simulation for verification
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
                break

    simulated_ruin = ruin_count / trials_for_sim

    if simulated_ruin > 0.05 or analytical_ruin > 0.05:
        verdict = "VETO (Violates Law #1: Ruin Probability > 5.0%)"
    elif simulated_ruin > 0.01:
        verdict = "CAUTION (Elevated Left-Tail Risk: 1.0% - 5.0%)"
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
    """Executes a 10,000-trial geometric trajectory simulation with left-tail shocks."""
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
                # Absorbing barrier for ruin
                cap = max(0.0, cap)

        final_capitals.append(cap)
        max_drawdowns.append(max_dd)
        if max_dd >= ruin_threshold_pct or cap <= initial_capital * 0.5:
            ruin_count += 1

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Athena GTO Numerical Computation Engine (ASCII Math Only)"
    )
    parser.add_argument(
        "--action",
        choices=["eev", "kelly", "ruin", "monte-carlo"],
        required=True,
        help="Calculation action to execute",
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # EEV parameters
    parser.add_argument("--mev", type=float, default=1000.0, help="Monetary Expected Value")
    parser.add_argument("--eu", type=float, default=200.0, help="Execution & Friction Drag")
    parser.add_argument("--eo", type=float, default=100.0, help="Opportunity & Attention Cost")
    parser.add_argument("--discount", type=float, default=0.15, help="Skeptic Discount (0.0-1.0)")

    # Kelly & Ruin parameters
    parser.add_argument("--win-rate", type=float, default=0.55, help="Win rate fraction (0.0-1.0)")
    parser.add_argument("--payoff", type=float, default=1.5, help="Payoff ratio (Win/Loss)")
    parser.add_argument("--variance-drag", type=float, default=0.5, help="Variance Drag factor")
    parser.add_argument("--risk-fraction", type=float, default=0.02, help="Risk fraction per trade")
    parser.add_argument("--ruin-threshold", type=float, default=0.5, help="Ruin drawdown threshold")

    # Monte Carlo parameters
    parser.add_argument("--capital", type=float, default=10000.0, help="Initial capital")
    parser.add_argument("--trials", type=int, default=10000, help="Monte Carlo trial count")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps per trial")
    parser.add_argument("--shock-prob", type=float, default=0.01, help="Left-tail shock probability")
    parser.add_argument("--shock-loss", type=float, default=0.10, help="Left-tail shock loss fraction")

    args = parser.parse_args(argv)

    try:
        res: Any
        if args.action == "eev":
            res = compute_eev(args.mev, args.eu, args.eo, args.discount)
        elif args.action == "kelly":
            res = compute_half_kelly(args.win_rate, args.payoff, args.variance_drag)
        elif args.action == "ruin":
            res = compute_ruin_probability(
                args.win_rate,
                args.payoff,
                args.risk_fraction,
                args.ruin_threshold,
            )
        elif args.action == "monte-carlo":
            res = run_monte_carlo_simulation(
                initial_capital=args.capital,
                win_rate=args.win_rate,
                payoff_ratio=args.payoff,
                risk_fraction=args.risk_fraction,
                n_trials=args.trials,
                n_steps=args.steps,
                left_tail_shock_prob=args.shock_prob,
                left_tail_shock_loss=args.shock_loss,
            )
        else:
            raise ValueError(f"Unknown action: {args.action}")

        if args.json:
            print(json.dumps(asdict(res), indent=2))
        else:
            print(res.to_ascii_table())

        return 0
    except Exception as exc:
        print(f"Error executing GTO engine: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
