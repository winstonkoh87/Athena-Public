"""
Contract Specifications & Pip-to-Dollar Mapping Engine (IC Markets Raw Spread).
================================================================================
Resolves TD-053: Asset Contract Specifications Mapping in Sizing Scripts.
Provides canonical contract sizing, pip values, lot size calculations, and
pre-trade dollar-to-pip stop loss validation across Forex, Metals, Crypto, and Indices.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContractSpec:
    symbol: str
    category: str
    contract_size: float
    quote_currency: str
    pip_size: float
    pip_value_std_lot: float
    min_lot: float = 0.01
    lot_step: float = 0.01


# Canonical IC Markets Raw Spread Specifications Table
_SPECS: dict[str, ContractSpec] = {}


def _register(
    symbols: list[str],
    category: str,
    contract_size: float,
    quote_currency: str,
    pip_size: float,
    pip_value_std_lot: float,
    min_lot: float = 0.01,
    lot_step: float = 0.01,
) -> None:
    for sym in symbols:
        _SPECS[sym.upper()] = ContractSpec(
            symbol=sym.upper(),
            category=category,
            contract_size=contract_size,
            quote_currency=quote_currency,
            pip_size=pip_size,
            pip_value_std_lot=pip_value_std_lot,
            min_lot=min_lot,
            lot_step=lot_step,
        )


# 1. Standard Forex (100,000 units base, pip = 0.0001, pip value = 10 units quote)
_register(
    ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"],
    category="forex",
    contract_size=100000.0,
    quote_currency="USD",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["USDCAD", "EURCAD", "GBPCAD", "AUDCAD", "NZDCAD"],
    category="forex",
    contract_size=100000.0,
    quote_currency="CAD",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["USDCHF", "EURCHF", "GBPCHF", "AUDCHF", "NZDCHF", "CADCHF"],
    category="forex",
    contract_size=100000.0,
    quote_currency="CHF",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["EURGBP"],
    category="forex",
    contract_size=100000.0,
    quote_currency="GBP",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["EURAUD", "GBPAUD"],
    category="forex",
    contract_size=100000.0,
    quote_currency="AUD",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["EURNZD", "GBPNZD", "AUDNZD"],
    category="forex",
    contract_size=100000.0,
    quote_currency="NZD",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)
_register(
    ["USDSGD", "EURSGD", "GBPSGD"],
    category="forex",
    contract_size=100000.0,
    quote_currency="SGD",
    pip_size=0.0001,
    pip_value_std_lot=10.0,
)

# 2. JPY Pairs (100,000 units base, pip = 0.01, pip value = 1,000 JPY)
_register(
    ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY", "SGDJPY"],
    category="forex_jpy",
    contract_size=100000.0,
    quote_currency="JPY",
    pip_size=0.01,
    pip_value_std_lot=1000.0,
)

# 3. Precious Metals
# Gold: 100 oz contract, 1 standard pip = $0.10 price move ($10/lot = $0.10/0.01 lot)
_register(
    ["XAUUSD", "GOLD"],
    category="metal",
    contract_size=100.0,
    quote_currency="USD",
    pip_size=0.10,
    pip_value_std_lot=10.0,
)
# Silver: 5,000 oz contract, 1 pip = 0.01 price move ($50/lot = $0.50/0.01 lot)
_register(
    ["XAGUSD", "SILVER"],
    category="metal",
    contract_size=5000.0,
    quote_currency="USD",
    pip_size=0.01,
    pip_value_std_lot=50.0,
)

# 4. Cryptocurrencies (IC Markets CFD Specifications)
# BTCUSD: 1 BTC contract. Standard point/pip move of $1.00 = $1.00 per lot ($0.01 per 0.01 micro lot)
_register(
    ["BTCUSD", "BITCOIN"],
    category="crypto",
    contract_size=1.0,
    quote_currency="USD",
    pip_size=1.0,
    pip_value_std_lot=1.0,
)
_register(
    ["ETHUSD", "ETHEREUM"],
    category="crypto",
    contract_size=1.0,
    quote_currency="USD",
    pip_size=1.0,
    pip_value_std_lot=1.0,
)

# 5. Major Equity Indices
_register(
    ["US30", "DJ30", "WS30"],
    category="index",
    contract_size=1.0,
    quote_currency="USD",
    pip_size=1.0,
    pip_value_std_lot=1.0,
)
_register(
    ["NAS100", "USTEC", "NDX200"],
    category="index",
    contract_size=1.0,
    quote_currency="USD",
    pip_size=1.0,
    pip_value_std_lot=1.0,
)
_register(
    ["SPX500", "US500"],
    category="index",
    contract_size=1.0,
    quote_currency="USD",
    pip_size=1.0,
    pip_value_std_lot=1.0,
)


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol string by stripping slashes, spaces, and punctuation."""
    return symbol.upper().replace("/", "").replace(" ", "").replace("_", "").replace("-", "")


def get_contract_spec(symbol: str) -> ContractSpec:
    """
    Retrieve ContractSpec for a given instrument symbol.
    Raises ValueError on unknown instrument (fails-closed).
    """
    clean_sym = normalize_symbol(symbol)
    if clean_sym in _SPECS:
        return _SPECS[clean_sym]

    raise ValueError(
        f"Unsupported instrument '{symbol}' (normalized: '{clean_sym}'). "
        f"Known symbols: {sorted(_SPECS.keys())}"
    )


def get_pip_value(symbol: str, lot_size: float = 1.0) -> float:
    """Return pip value in quote currency for the specified lot size."""
    spec = get_contract_spec(symbol)
    return round(spec.pip_value_std_lot * lot_size, 4)


def calculate_lot_size(
    symbol: str,
    stop_loss_pips: float,
    risk_amount_quote: float,
    min_lot: Optional[float] = None,
    lot_step: Optional[float] = None,
    round_down: bool = True,
) -> float:
    """
    Solve for lot size given a stop loss distance (in pips) and dollar risk.
    Formula: lot_size = risk_amount / (stop_loss_pips * pip_value_per_std_lot)
    """
    spec = get_contract_spec(symbol)
    min_l = min_lot if min_lot is not None else spec.min_lot
    step = lot_step if lot_step is not None else spec.lot_step

    if stop_loss_pips <= 0 or risk_amount_quote <= 0:
        return 0.0

    raw_lot = risk_amount_quote / (stop_loss_pips * spec.pip_value_std_lot)

    if round_down:
        # Quantize down to step to prevent over-risking
        steps = math.floor(raw_lot / step)
    else:
        steps = round(raw_lot / step)

    lot = steps * step
    if lot < min_l:
        return 0.0

    return round(lot, 2)


def validate_pip_dollar_stop(
    symbol: str,
    lot_size: float,
    stop_loss_pips: float,
    expected_dollar_risk: float,
    tolerance_pct: float = 0.05,
) -> tuple[bool, float, float]:
    """
    Validates that the solved pip distance matches the intended dollar stop (TD-053).
    Returns (is_valid, calculated_dollar_risk, delta_dollar).
    """
    spec = get_contract_spec(symbol)
    calculated_risk = round(lot_size * stop_loss_pips * spec.pip_value_std_lot, 2)
    delta = round(calculated_risk - expected_dollar_risk, 2)

    allowed_tolerance = abs(expected_dollar_risk * tolerance_pct)
    # Also allow at least 1 pip of tolerance for rounding steps
    min_step_tolerance = round(spec.pip_value_std_lot * spec.min_lot, 2)
    max_tolerance = max(allowed_tolerance, min_step_tolerance)

    is_valid = abs(delta) <= max_tolerance
    return is_valid, calculated_risk, delta
