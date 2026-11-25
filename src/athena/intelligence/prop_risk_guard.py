"""
athena.intelligence.prop_risk_guard
===================================
Proprietary Trading Microstructure & Risk Capacity Auditor.
Operationalizes CANONICAL Entry §515 & Case Study CS-745:
1. The Nominal Funding Mirage (Denominator Distortion Guard).
2. The Trade Copier Correlated Blast Radius Multiplier.
3. The Prop-to-Live Ergodicity Inversion Shield.
4. The Negative-Carry Biological Burn Rate Detector.
5. Two-Barrier Brigade Sizing, Two-Bucket 1/3 Kelly & Wilson Shrinkage Gate.

All formulas and output render strictly in plain ASCII.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PropAuditVerdict(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    REJECT = "REJECT"


class AccountType(str, Enum):
    PROP_EVALUATION = "prop_evaluation"
    LIVE_PERSONAL = "live_personal"
    SACRIFICIAL_FUSE = "sacrificial_fuse"


class BrigadeBucket(str, Enum):
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"


@dataclass
class PropCapacityAudit:
    nominal_balance: float = 0.0
    effective_loss_limit: float = 0.0
    denominator_distortion_factor: float = 0.0
    dollar_risk_per_trade: float = 0.0
    num_synced_accounts: int = 1
    aggregate_dollar_risk: float = 0.0
    nominal_risk_pct: float = 0.0
    true_effective_risk_pct: float = 0.0
    trades_to_ruin: float = 0.0
    violates_denominator_mirage: bool = False
    violates_copier_blast_radius: bool = False
    verdict: PropAuditVerdict = PropAuditVerdict.REJECT
    reasons: list[str] = field(default_factory=list)
    recommended_dollar_risk_per_account: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "nominal_balance": self.nominal_balance,
            "effective_loss_limit": self.effective_loss_limit,
            "denominator_distortion_factor": round(self.denominator_distortion_factor, 2),
            "dollar_risk_per_trade": self.dollar_risk_per_trade,
            "num_synced_accounts": self.num_synced_accounts,
            "aggregate_dollar_risk": round(self.aggregate_dollar_risk, 2),
            "nominal_risk_pct": round(self.nominal_risk_pct, 4),
            "true_effective_risk_pct": round(self.true_effective_risk_pct, 4),
            "trades_to_ruin": round(self.trades_to_ruin, 2),
            "violates_denominator_mirage": self.violates_denominator_mirage,
            "violates_copier_blast_radius": self.violates_copier_blast_radius,
            "verdict": self.verdict.value,
            "reasons": self.reasons,
            "recommended_dollar_risk_per_account": round(self.recommended_dollar_risk_per_account, 2),
        }


@dataclass
class ErgodicityCarryAudit:
    account_type: AccountType = AccountType.LIVE_PERSONAL
    cash_at_risk: float = 0.0
    total_liquid_net_worth: float = 0.0
    monthly_living_burn: float = 0.0
    independent_monthly_cashflow: float = 0.0
    net_monthly_carry: float = 0.0
    violates_ergodicity_inversion: bool = False
    violates_negative_carry_drag: bool = False
    verdict: PropAuditVerdict = PropAuditVerdict.REJECT
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_type": self.account_type.value,
            "cash_at_risk": self.cash_at_risk,
            "total_liquid_net_worth": self.total_liquid_net_worth,
            "monthly_living_burn": self.monthly_living_burn,
            "independent_monthly_cashflow": self.independent_monthly_cashflow,
            "net_monthly_carry": round(self.net_monthly_carry, 2),
            "violates_ergodicity_inversion": self.violates_ergodicity_inversion,
            "violates_negative_carry_drag": self.violates_negative_carry_drag,
            "verdict": self.verdict.value,
            "reasons": self.reasons,
        }


def audit_prop_risk_capacity(
    nominal_balance: float,
    max_drawdown_limit: float,
    dollar_risk_per_trade: float,
    daily_loss_limit: float | None = None,
    num_synced_accounts: int = 1,
) -> PropCapacityAudit:
    """
    Audits risk capacity against the true liquidation buffer rather than nominal marketing balances.
    Mechanic 1 (CS-745 / §515): Stated nominal balances create 10x-20x denominator over-leverage.
    Mechanic 2 (CS-745 / §515): Cloud trade copiers multiply risk vectors across all accounts.
    """
    # 1. Calculate effective liquidation buffer (strictest limit binds)
    if daily_loss_limit is not None and 0.0 < daily_loss_limit < max_drawdown_limit:
        effective_loss_limit = float(daily_loss_limit)
    else:
        effective_loss_limit = float(max_drawdown_limit)

    effective_loss_limit = max(effective_loss_limit, 1.0)
    denominator_distortion_factor = (
        nominal_balance / effective_loss_limit if effective_loss_limit > 0 else 1.0
    )

    num_synced = max(int(num_synced_accounts), 1)
    aggregate_dollar_risk = float(dollar_risk_per_trade) * num_synced

    nominal_risk_pct = (
        (float(dollar_risk_per_trade) / nominal_balance) * 100.0
        if nominal_balance > 0
        else 0.0
    )
    true_effective_risk_pct = (
        (aggregate_dollar_risk / effective_loss_limit) * 100.0
        if effective_loss_limit > 0
        else 0.0
    )

    trades_to_ruin = (
        effective_loss_limit / aggregate_dollar_risk
        if aggregate_dollar_risk > 0
        else 999.0
    )

    # Invariants
    # Invariant 1: True risk should not exceed 5.0% of true liquidation buffer (Law #1: P(ruin) <= 5%)
    violates_denominator_mirage = (true_effective_risk_pct > 5.0) or (trades_to_ruin < 20.0)

    # Invariant 2: Trade Copier blast radius: if syncing multiple accounts, aggregate risk must stay within buffer
    violates_copier_blast_radius = (
        num_synced > 1 and aggregate_dollar_risk > (effective_loss_limit * 0.05)
    )

    reasons: list[str] = []
    if violates_denominator_mirage:
        reasons.append(
            f"Nominal Denominator Distortion: Proposed risk (${aggregate_dollar_risk:.2f}) "
            f"consumes {true_effective_risk_pct:.1f}% of true liquidation buffer (${effective_loss_limit:.2f}) "
            f"[only {trades_to_ruin:.1f} trades to ruin]. Nominal {nominal_risk_pct:.2f}% is an optical illusion."
        )

    if violates_copier_blast_radius:
        reasons.append(
            f"Trade Copier Correlated Blast Radius: Syncing {num_synced} accounts with "
            f"aggregate risk ${aggregate_dollar_risk:.2f} ({true_effective_risk_pct:.1f}% of buffer) "
            "without 1/N scaling converts normal drawdowns into simultaneous terminal liquidation."
        )

    if violates_denominator_mirage or violates_copier_blast_radius:
        verdict = PropAuditVerdict.REJECT
    elif true_effective_risk_pct > 3.0:
        verdict = PropAuditVerdict.WARNING
    else:
        verdict = PropAuditVerdict.PASS

    # Recommended risk: 1% of true liquidation buffer divided by number of synced accounts
    recommended_dollar_risk_per_account = (effective_loss_limit * 0.01) / num_synced

    return PropCapacityAudit(
        nominal_balance=nominal_balance,
        effective_loss_limit=effective_loss_limit,
        denominator_distortion_factor=denominator_distortion_factor,
        dollar_risk_per_trade=dollar_risk_per_trade,
        num_synced_accounts=num_synced,
        aggregate_dollar_risk=aggregate_dollar_risk,
        nominal_risk_pct=nominal_risk_pct,
        true_effective_risk_pct=true_effective_risk_pct,
        trades_to_ruin=trades_to_ruin,
        violates_denominator_mirage=violates_denominator_mirage,
        violates_copier_blast_radius=violates_copier_blast_radius,
        verdict=verdict,
        reasons=reasons,
        recommended_dollar_risk_per_account=recommended_dollar_risk_per_account,
    )


def audit_ergodicity_and_carry(
    account_type: str | AccountType,
    cash_at_risk: float,
    total_liquid_net_worth: float,
    monthly_living_burn: float,
    independent_monthly_cashflow: float,
) -> ErgodicityCarryAudit:
    """
    Audits ergodicity topology and biological carry drag.
    Mechanic 3 (CS-745 / §515): Prop-to-Live Ergodicity Inversion (symmetrical 100% loss of savings).
    Mechanic 4 (CS-745 / §515): Negative-Carry Full-Time Trading Drag (deterministic living burn vs stochastic P&L).
    """
    if isinstance(account_type, str):
        try:
            acc_type = AccountType(account_type.lower())
        except ValueError:
            acc_type = AccountType.LIVE_PERSONAL
    else:
        acc_type = account_type

    net_monthly_carry = float(independent_monthly_cashflow) - float(monthly_living_burn)
    total_liquid = max(float(total_liquid_net_worth), 1.0)
    risk_fraction = float(cash_at_risk) / total_liquid

    # Invariant 3: Live Personal accounts must not risk more than 10% of total liquid net worth
    violates_ergodicity_inversion = False
    if acc_type == AccountType.LIVE_PERSONAL and risk_fraction > 0.10:
        violates_ergodicity_inversion = True
    elif acc_type == AccountType.SACRIFICIAL_FUSE and (cash_at_risk > 1500.0 or risk_fraction > 0.15):
        # Air-gapped fuse must stay bounded (<= S$1,500 / $1,000 USD, or <= 15% float)
        violates_ergodicity_inversion = True

    # Invariant 4: Independent cashflow must cover deterministic monthly living burn
    violates_negative_carry_drag = independent_monthly_cashflow < monthly_living_burn

    reasons: list[str] = []
    if violates_ergodicity_inversion:
        reasons.append(
            f"Ergodicity Inversion: Live brokerage exposure (${cash_at_risk:.2f}) represents "
            f"{risk_fraction * 100.0:.1f}% of total liquid net worth (${total_liquid:.2f}). "
            "Prop-sized risk on unhedged personal cash guarantees absorbing barrier collapse."
        )

    if violates_negative_carry_drag:
        reasons.append(
            f"Negative-Carry Biological Burn Drag: Independent cashflow (${independent_monthly_cashflow:.2f}) "
            f"does not cover living burn (${monthly_living_burn:.2f}), creating a monthly deficit of "
            f"${abs(net_monthly_carry):.2f}. Forcing deterministic living expenses onto stochastic "
            "market variance triggers panic-induced over-leveraging and strategy drift."
        )

    if violates_ergodicity_inversion or violates_negative_carry_drag:
        verdict = PropAuditVerdict.REJECT
    elif net_monthly_carry < 300.0:
        verdict = PropAuditVerdict.WARNING
    else:
        verdict = PropAuditVerdict.PASS

    return ErgodicityCarryAudit(
        account_type=acc_type,
        cash_at_risk=cash_at_risk,
        total_liquid_net_worth=total_liquid_net_worth,
        monthly_living_burn=monthly_living_burn,
        independent_monthly_cashflow=independent_monthly_cashflow,
        net_monthly_carry=net_monthly_carry,
        violates_ergodicity_inversion=violates_ergodicity_inversion,
        violates_negative_carry_drag=violates_negative_carry_drag,
        verdict=verdict,
        reasons=reasons,
    )


def format_prop_risk_report(
    capacity_audit: PropCapacityAudit,
    carry_audit: ErgodicityCarryAudit | None = None,
    brigade_audit: BrigadeSizingAudit | None = None,
) -> str:
    """Renders plain ASCII report for CLI and audit outputs."""
    lines: list[str] = [
        "============================================================",
        "=== Prop Risk Microstructure & Capacity Audit (CANONICAL §515) ===",
        "============================================================",
        f"Nominal Balance:           ${capacity_audit.nominal_balance:,.2f}",
        f"Effective Loss Limit:      ${capacity_audit.effective_loss_limit:,.2f}",
        f"Denominator Distortion:    {capacity_audit.denominator_distortion_factor:.1f}x nominal inflation",
        f"Dollar Risk Per Trade:     ${capacity_audit.dollar_risk_per_trade:,.2f}",
        f"Synced Accounts (Copier):  {capacity_audit.num_synced_accounts}",
        f"Aggregate Dollar Risk:     ${capacity_audit.aggregate_dollar_risk:,.2f}",
        f"Nominal Risk Percentage:   {capacity_audit.nominal_risk_pct:.2f}%",
        f"True Effective Risk:       {capacity_audit.true_effective_risk_pct:.2f}% of true buffer",
        f"Trades to Liquidation:     {capacity_audit.trades_to_ruin:.1f} trades",
        f"Capacity Verdict:          {capacity_audit.verdict.value}",
    ]
    if capacity_audit.reasons:
        lines.append("Violations / Findings:")
        for r in capacity_audit.reasons:
            lines.append(f"  - {r}")
    lines.append(
        f"Recommended Risk/Account:  ${capacity_audit.recommended_dollar_risk_per_account:,.2f} (1/N scaled)"
    )

    if carry_audit:
        lines.extend([
            "------------------------------------------------------------",
            "=== Ergodicity Topology & Biological Carry Audit ===",
            "------------------------------------------------------------",
            f"Account Type:              {carry_audit.account_type.value}",
            f"Cash at Risk:              ${carry_audit.cash_at_risk:,.2f} ({ (carry_audit.cash_at_risk / max(carry_audit.total_liquid_net_worth, 1.0)) * 100.0:.1f}% of net worth)",
            f"Monthly Living Burn:       ${carry_audit.monthly_living_burn:,.2f}",
            f"Independent Cashflow:      ${carry_audit.independent_monthly_cashflow:,.2f}",
            f"Net Monthly Carry:         ${carry_audit.net_monthly_carry:,.2f}",
            f"Carry Verdict:             {carry_audit.verdict.value}",
        ])
        if carry_audit.reasons:
            lines.append("Carry Violations:")
            for r in carry_audit.reasons:
                lines.append(f"  - {r}")

    if brigade_audit:
        lines.extend([
            "------------------------------------------------------------",
            "=== Brigade Two-Barrier Sizing & Kelly Audit ===",
            "------------------------------------------------------------",
            f"Bucket Regime:             {brigade_audit.bucket.value}",
            f"Division Capital:          ${brigade_audit.division_capital:,.2f} ({brigade_audit.division_risk_pct:.2f}%/setup)",
            f"Remaining Q-HWM Buffer:    ${brigade_audit.remaining_hwm_buffer:,.2f} ({brigade_audit.hwm_risk_pct:.2f}%/setup)",
            f"Fuse Ceiling:              ${brigade_audit.fuse_limit:,.2f} ({brigade_audit.fuse_utilization_pct:.1f}% used)",
            f"Losses to Q-HWM Lockout:   {brigade_audit.losses_to_hwm_lockout:.2f} losses",
            f"Effective WR / BE WR:      {brigade_audit.effective_win_rate * 100.0:.2f}% / {brigade_audit.breakeven_win_rate * 100.0:.2f}%",
            f"1/3 Kelly Frontier:        {brigade_audit.one_third_kelly_pct:.2f}% of Division",
            f"Brigade Verdict:           {brigade_audit.verdict.value}",
            f"Recommended Max Risk:      ${brigade_audit.recommended_max_risk_dollars:,.2f}",
        ])
        if brigade_audit.reasons:
            lines.append("Brigade Findings:")
            for r in brigade_audit.reasons:
                lines.append(f"  - {r}")

    lines.append("============================================================")
    return "\n".join(lines)


@dataclass
class BrigadeSizingAudit:
    division_capital: float = 0.0
    quarterly_hwm_limit: float = 0.0
    remaining_hwm_buffer: float = 0.0
    fuse_limit: float = 0.0
    setup_risk_dollars: float = 0.0
    reward_to_risk: float = 0.0
    win_rate: float = 0.0
    effective_win_rate: float = 0.0
    sample_size: int | None = None
    bucket: BrigadeBucket = BrigadeBucket.CONSERVATIVE
    barrier_distortion_factor: float = 0.0
    division_risk_pct: float = 0.0
    hwm_risk_pct: float = 0.0
    fuse_utilization_pct: float = 0.0
    losses_to_hwm_lockout: float = 0.0
    breakeven_win_rate: float = 0.0
    raw_ev_per_dollar: float = 0.0
    effective_ev_per_dollar: float = 0.0
    one_third_kelly_pct: float = 0.0
    violates_hwm_barrier: bool = False
    violates_fuse_ceiling: bool = False
    violates_bucket_ceiling: bool = False
    violates_negative_ev: bool = False
    violates_tp_floor: bool = False
    verdict: PropAuditVerdict = PropAuditVerdict.PASS
    reasons: list[str] = field(default_factory=list)
    recommended_max_risk_dollars: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "division_capital": self.division_capital,
            "quarterly_hwm_limit": self.quarterly_hwm_limit,
            "remaining_hwm_buffer": round(self.remaining_hwm_buffer, 2),
            "fuse_limit": self.fuse_limit,
            "setup_risk_dollars": self.setup_risk_dollars,
            "reward_to_risk": round(self.reward_to_risk, 4),
            "win_rate": round(self.win_rate, 4),
            "effective_win_rate": round(self.effective_win_rate, 4),
            "sample_size": self.sample_size,
            "bucket": self.bucket.value,
            "barrier_distortion_factor": round(self.barrier_distortion_factor, 2),
            "division_risk_pct": round(self.division_risk_pct, 4),
            "hwm_risk_pct": round(self.hwm_risk_pct, 4),
            "fuse_utilization_pct": round(self.fuse_utilization_pct, 2),
            "losses_to_hwm_lockout": round(self.losses_to_hwm_lockout, 2),
            "breakeven_win_rate": round(self.breakeven_win_rate, 4),
            "raw_ev_per_dollar": round(self.raw_ev_per_dollar, 4),
            "effective_ev_per_dollar": round(self.effective_ev_per_dollar, 4),
            "one_third_kelly_pct": round(self.one_third_kelly_pct, 4),
            "violates_hwm_barrier": self.violates_hwm_barrier,
            "violates_fuse_ceiling": self.violates_fuse_ceiling,
            "violates_bucket_ceiling": self.violates_bucket_ceiling,
            "violates_negative_ev": self.violates_negative_ev,
            "violates_tp_floor": self.violates_tp_floor,
            "verdict": self.verdict.value,
            "reasons": self.reasons,
            "recommended_max_risk_dollars": round(self.recommended_max_risk_dollars, 2),
        }


def wilson_lower_bound(win_rate: float, sample_size: int, z: float = 1.96) -> float:
    """Compute the Wilson score lower confidence bound for binomial win rate p."""
    if not (0.0 <= win_rate <= 1.0) or not math.isfinite(win_rate):
        raise ValueError("win_rate must be finite and within [0.0, 1.0]")
    if sample_size <= 0:
        raise ValueError("sample_size must be a positive integer")
    if z < 0.0 or not math.isfinite(z):
        raise ValueError("z must be non-negative and finite")

    z2 = z * z
    denom = 1.0 + z2 / sample_size
    center = win_rate + z2 / (2.0 * sample_size)
    margin = z * math.sqrt((win_rate * (1.0 - win_rate) + z2 / (4.0 * sample_size)) / sample_size)
    return max(0.0, (center - margin) / denom)


def _validate_brigade_inputs(
    division_capital: float,
    quarterly_hwm_limit: float,
    fuse_limit: float,
    setup_risk_dollars: float,
    reward_to_risk: float,
    win_rate: float,
    current_drawdown_from_hwm: float,
    sample_size: int | None,
) -> None:
    """Fail fast on invalid or non-finite Brigade sizing inputs."""
    positive_fields = (
        ("division_capital", division_capital),
        ("quarterly_hwm_limit", quarterly_hwm_limit),
        ("fuse_limit", fuse_limit),
        ("setup_risk_dollars", setup_risk_dollars),
        ("reward_to_risk", reward_to_risk),
    )
    for name, val in positive_fields:
        if not math.isfinite(val) or val <= 0.0:
            raise ValueError(f"{name} must be finite and > 0")
    if not math.isfinite(win_rate) or not (0.0 <= win_rate <= 1.0):
        raise ValueError("win_rate must be finite and within [0.0, 1.0]")
    if not math.isfinite(current_drawdown_from_hwm) or current_drawdown_from_hwm < 0.0:
        raise ValueError("current_drawdown_from_hwm must be finite and >= 0")
    if sample_size is not None and sample_size <= 0:
        raise ValueError("sample_size must be > 0 when provided")


def audit_brigade_sizing(
    division_capital: float,
    quarterly_hwm_limit: float,
    fuse_limit: float,
    setup_risk_dollars: float,
    reward_to_risk: float,
    win_rate: float,
    sample_size: int | None = None,
    current_drawdown_from_hwm: float = 0.0,
    tp_discipline_verified: bool = True,
    allow_max_stack: bool = False,
) -> BrigadeSizingAudit:
    """
    Audits setup sizing against coupled Two-Barrier constraints:
    1. Nearest absorbing barrier: Quarterly Trailing HWM vs Division capital.
    2. Live Sacrificial Fuse ceiling (e.g., USD 1,000).
    3. Two-Bucket 1/3 Kelly regime: <= 5.0% Conservative (R:R < 1.0), <= 2.0% Aggressive (R:R >= 1.0).
    4. Wilson 95% lower-bound uncertainty shrinkage when sample_size is given.
    5. +20% deep-grid TP floor (b >= 0.20) to block relief-exit payoff truncation.
    """
    _validate_brigade_inputs(
        division_capital=division_capital,
        quarterly_hwm_limit=quarterly_hwm_limit,
        fuse_limit=fuse_limit,
        setup_risk_dollars=setup_risk_dollars,
        reward_to_risk=reward_to_risk,
        win_rate=win_rate,
        current_drawdown_from_hwm=current_drawdown_from_hwm,
        sample_size=sample_size,
    )

    remaining_hwm_buffer = max(float(quarterly_hwm_limit) - float(current_drawdown_from_hwm), 0.0)
    barrier_distortion_factor = (
        float(division_capital) / remaining_hwm_buffer if remaining_hwm_buffer > 0.0 else float("inf")
    )
    division_risk_pct = (float(setup_risk_dollars) / float(division_capital)) * 100.0
    hwm_risk_pct = (
        (float(setup_risk_dollars) / remaining_hwm_buffer) * 100.0 if remaining_hwm_buffer > 0.0 else 100.0
    )
    fuse_utilization_pct = (float(setup_risk_dollars) / float(fuse_limit)) * 100.0
    losses_to_hwm_lockout = remaining_hwm_buffer / float(setup_risk_dollars) if remaining_hwm_buffer > 0.0 else 0.0

    breakeven_win_rate = 1.0 / (1.0 + float(reward_to_risk))
    effective_win_rate = wilson_lower_bound(win_rate, sample_size) if sample_size is not None else float(win_rate)
    raw_ev_per_dollar = float(win_rate) * float(reward_to_risk) - (1.0 - float(win_rate))
    effective_ev_per_dollar = effective_win_rate * float(reward_to_risk) - (1.0 - effective_win_rate)
    full_kelly_pct = max(0.0, (effective_ev_per_dollar / float(reward_to_risk)) * 100.0)
    one_third_kelly_pct = full_kelly_pct / 3.0

    bucket = BrigadeBucket.CONSERVATIVE if reward_to_risk < 1.0 else BrigadeBucket.AGGRESSIVE
    routine_div_cap_pct = 5.0 if bucket == BrigadeBucket.CONSERVATIVE else 2.0
    routine_hwm_cap_pct = 15.0

    max_stack_eligible = (
        bucket == BrigadeBucket.CONSERVATIVE
        and allow_max_stack
        and tp_discipline_verified
        and reward_to_risk >= 0.20
    )
    hard_div_cap_pct = 7.5 if max_stack_eligible else routine_div_cap_pct
    hard_hwm_cap_pct = 22.5 if max_stack_eligible else routine_hwm_cap_pct

    violates_fuse_ceiling = float(setup_risk_dollars) > float(fuse_limit)
    violates_hwm_barrier = (remaining_hwm_buffer <= 0.0) or (hwm_risk_pct > hard_hwm_cap_pct)
    violates_bucket_ceiling = division_risk_pct > hard_div_cap_pct
    violates_negative_ev = (raw_ev_per_dollar <= 0.0) or (effective_ev_per_dollar <= 0.0)
    violates_tp_floor = (reward_to_risk < 0.20) or (not tp_discipline_verified and division_risk_pct > 5.0)

    reasons: list[str] = []
    if violates_fuse_ceiling:
        reasons.append(
            f"Fuse Ceiling Breach: Setup risk (${setup_risk_dollars:,.2f}) exceeds active fuse (${fuse_limit:,.2f})."
        )
    if violates_hwm_barrier:
        reasons.append(
            f"Quarterly HWM Barrier Breach: Setup consumes {hwm_risk_pct:.2f}% of remaining Q-HWM buffer "
            f"(${remaining_hwm_buffer:,.2f}; {losses_to_hwm_lockout:.2f} losses to lockout, cap {hard_hwm_cap_pct:.1f}%)."
        )
    if violates_bucket_ceiling:
        reasons.append(
            f"Two-Bucket Ceiling Breach: {division_risk_pct:.2f}% of Division exceeds {bucket.value} "
            f"1/3 Kelly cap ({hard_div_cap_pct:.1f}%)."
        )
    if violates_negative_ev:
        reasons.append(
            f"Negative Effective EV: Effective WR ({effective_win_rate * 100.0:.2f}%) fails breakeven "
            f"({breakeven_win_rate * 100.0:.2f}%) after uncertainty adjustment (EV={effective_ev_per_dollar:+.4f})."
        )
    if violates_tp_floor:
        reasons.append(
            f"Payoff Truncation / TP Floor Breach: R:R b={reward_to_risk:.2f} or unverified TP discipline "
            "violates minimum b >= 0.20 (+20% setup capital) requirement."
        )

    is_outer_stack_warning = (
        max_stack_eligible
        and (division_risk_pct > routine_div_cap_pct or hwm_risk_pct > routine_hwm_cap_pct)
    )
    if any((violates_fuse_ceiling, violates_hwm_barrier, violates_bucket_ceiling, violates_negative_ev, violates_tp_floor)):
        verdict = PropAuditVerdict.REJECT
    elif is_outer_stack_warning:
        reasons.append(
            f"Outer Max-Stack Band: {division_risk_pct:.2f}% Div / {hwm_risk_pct:.2f}% Q-HWM requires strict b >= 0.20 TP."
        )
        verdict = PropAuditVerdict.WARNING
    else:
        verdict = PropAuditVerdict.PASS

    if violates_negative_ev or remaining_hwm_buffer <= 0.0 or reward_to_risk < 0.20:
        recommended_max_risk_dollars = 0.0
    else:
        cap_by_hwm = remaining_hwm_buffer * (routine_hwm_cap_pct / 100.0)
        cap_by_bucket = float(division_capital) * (routine_div_cap_pct / 100.0)
        cap_by_kelly = float(division_capital) * (one_third_kelly_pct / 100.0)
        recommended_max_risk_dollars = min(cap_by_hwm, cap_by_bucket, float(fuse_limit), cap_by_kelly)

    return BrigadeSizingAudit(
        division_capital=float(division_capital),
        quarterly_hwm_limit=float(quarterly_hwm_limit),
        remaining_hwm_buffer=remaining_hwm_buffer,
        fuse_limit=float(fuse_limit),
        setup_risk_dollars=float(setup_risk_dollars),
        reward_to_risk=float(reward_to_risk),
        win_rate=float(win_rate),
        effective_win_rate=effective_win_rate,
        sample_size=sample_size,
        bucket=bucket,
        barrier_distortion_factor=barrier_distortion_factor,
        division_risk_pct=division_risk_pct,
        hwm_risk_pct=hwm_risk_pct,
        fuse_utilization_pct=fuse_utilization_pct,
        losses_to_hwm_lockout=losses_to_hwm_lockout,
        breakeven_win_rate=breakeven_win_rate,
        raw_ev_per_dollar=raw_ev_per_dollar,
        effective_ev_per_dollar=effective_ev_per_dollar,
        one_third_kelly_pct=one_third_kelly_pct,
        violates_hwm_barrier=violates_hwm_barrier,
        violates_fuse_ceiling=violates_fuse_ceiling,
        violates_bucket_ceiling=violates_bucket_ceiling,
        violates_negative_ev=violates_negative_ev,
        violates_tp_floor=violates_tp_floor,
        verdict=verdict,
        reasons=reasons,
        recommended_max_risk_dollars=recommended_max_risk_dollars,
    )
