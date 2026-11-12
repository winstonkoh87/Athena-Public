---
name: zenith-execution
description: "Unified trade execution suite: One-Third Kelly sizing, stop-loss calculation, Monte Carlo simulation, and portfolio rebalancing. Absorbs: kelly-mandate, stop-loss-calc, monte-carlo-sim, portfolio-rebalancer."
argument-hint: "setup | sizing | simulate | rebalance | optimize <ticker>"
allowed-tools:
  - Read
  - Bash
  - WebFetch
auto-invoke: true
model: default
context_trigger: "position sizing, Kelly, stop loss, Monte Carlo, simulate, rebalance, trade execution, portfolio optimization"
---

# ZenithFX Execution Suite (Expanded)

> **Absorbs**: `kelly-mandate`, `stop-loss-calc`, `monte-carlo-sim`, `portfolio-rebalancer`

Unified quantitative execution skill for High Win-Rate trading systems (Protocol 367).

## Triggers

"zenith", "trade setup", "position size", "stop loss", "kelly criterion", "how much to risk", "invalidation point", "simulate", "monte carlo", "rebalance", "portfolio allocation"

## Sub-Commands

### 1. Position Sizing: One-Third Kelly (0.33x) GTO Anchor

#### Mathematical Foundation: MacLean, Thorp & Ziemba (2011) Continuous Drawdown Theorem

```text
P(Drawdown >= D) = (1 - D)^(2/c - 1)
Growth Rate Kept: g(c) = c * (2 - c)
```

For 50% drawdown (`D = 0.50`):
- **Full Kelly (1.00x)**: 100.0% growth, 50.0% P(down 50%) — Suicidal
- **Half-Kelly (0.50x)**: 75.0% growth, 12.5% P(down 50%) — Violates Law #1 (`> 5%`)
- **One-Third Kelly (0.33x)**: 55.6% growth, 3.1% P(down 50%) — **GTO Sweet Spot (Passes Law #1)**
- **Quarter-Kelly (0.25x)**: 43.8% growth, 0.8% P(down 50%) — Defensive mode

1. Demands Win Rate, Reward:Risk, and Total Capital.
2. Computes Full Kelly (theoretical optimum): `f* = (bp - q) / b`.
3. Scales by One-Third (`f = f* / 3`) per campaign (aggregate risk across all orders/layers) to satisfy Law #1 (`<= 5%` halving risk).
4. Hard caps at 10% regardless of edge (and 1-2% operational floor per setup).

### 2. Stop-Loss (Structural Invalidation)

1. Identifies the price where the trade premise is demonstrably false.
2. Calculates distance between Entry and Invalidation.
3. Fits pre-determined Capital Risk % into that distance → Position Size.

**Rule**: A Stop Loss is a *structural invalidation point*, not an arbitrary budget allowance.

### 3. Monte Carlo Simulation

Simulates N independent trades through a given structure.

**Inputs**: Win Rate (%), Risk:Reward, Risk per trade (%), Number of trades (N), Starting capital.

```python
import random

def monte_carlo(wr, rr, risk_pct, n_trades, starting_capital, n_paths=1000):
    results = []
    ruin_count = 0
    max_drawdowns = []
    for _ in range(n_paths):
        equity = starting_capital
        peak = equity
        max_dd = 0
        for _ in range(n_trades):
            if random.random() < wr:
                equity += equity * risk_pct * rr
            else:
                equity -= equity * risk_pct
            peak = max(peak, equity)
            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)
            if equity <= starting_capital * 0.2:
                ruin_count += 1
                break
        results.append(equity)
        max_drawdowns.append(max_dd)
    results.sort()
    return {
        "median": results[len(results)//2],
        "p5": results[int(len(results)*0.05)],
        "p95": results[int(len(results)*0.95)],
        "max_dd_median": sorted(max_drawdowns)[len(max_drawdowns)//2],
        "ruin_probability": ruin_count / n_paths,
        "double_probability": sum(1 for r in results if r >= starting_capital * 2) / n_paths,
    }
```

**Output**:

```
Monte Carlo Simulation (1,000 paths × N trades)
─────────────────────────────────────────────
Structure: WR=60%, RR=1.0, Risk=1.1%/trade
Starting Capital: $10,000

Median Terminal Equity:  $XX,XXX
5th Percentile:          $X,XXX
95th Percentile:         $XX,XXX
Max Drawdown (median):   XX.X%
P(Ruin):                 X.X%
P(Double):               XX.X%
─────────────────────────────────────────────
Verdict: [PASS/FAIL] — structure is [robust/fragile]
```

### 4. Portfolio Rebalance

1. Evaluates current allocation weights vs initial target weights.
2. Identifies momentum drift.
3. Outputs specific buy/sell orders to restore Kelly/Structural parity.

## Reference Protocols

- Protocol 367: High Win-Rate Supremacy
- Protocol 368: Five Levers
- Protocol 46: Trading Methodology
