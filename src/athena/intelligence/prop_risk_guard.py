"""
athena.intelligence.prop_risk_guard
===================================
Proprietary Trading Microstructure & Risk Capacity Auditor.
Operationalizes CANONICAL Entry §515 & Case Study CS-745:
1. The Nominal Funding Mirage (Denominator Distortion Guard).
2. The Trade Copier Correlated Blast Radius Multiplier.
3. The Prop-to-Live Ergodicity Inversion Shield.
4. The Negative-Carry Biological Burn Rate Detector.

All formulas and output render strictly in plain ASCII.
"""

from __future__ import annotations

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

    lines.append("============================================================")
    return "\n".join(lines)
