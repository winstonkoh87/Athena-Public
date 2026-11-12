---
name: structural-trading-gate
description: "Unified zero-emotion variance shield for capital markets (FX, crypto, CFDs) and poker. Absorbs trading-risk-gate + zenith-execution + trade-journal-analyzer into one engine."
vibe: "The math trades. You just execute."
context_trigger: "trade, poker, sizing, bankroll, drawdown, kelly, stop loss, position size, variance, risk reward, lot size, pips, ruin, MTT, buy-in, commission drag, layering, grid, oil, XBRUSD, EURUSD"
auto-invoke: true
model: default
source: "Retroactively compiled from 1,900+ sessions (2025-2026) via skill-compiler"
compiled_from: "protocols/trading/TRD-*, skills/trading-risk-gate, skills/zenith-execution, skills/trade-journal-analyzer"
absorbs: "trading-risk-gate, zenith-execution, trade-journal-analyzer"
meta_patterns: [MP-2, MP-4, MP-7, MP-11]
pinned: true
---

# Structural Trading Gate — The Zero-Emotion Variance Shield

> **Compiled**: 2026-05-11 (retroactive synthesis of all trading sessions)
> **Problem Class**: Any capital allocation question — FX, crypto, CFDs, poker, casino. Pre-trade safety, position sizing, post-trade analytics.
> **Axiom**: *"In non-ergodic systems, the strategy that maximizes EV is the one most likely to kill you. Survival > Optimization."*

## When to Use

Invoke whenever the user mentions:
- Any trade setup, entry, or sizing question
- Bankroll management (poker or trading)
- Drawdown analysis or recovery
- Commission/friction cost optimization
- Post-trade review or journal analysis
- "Should I hold over the weekend?"

## Solution Architecture

### Pre-Trade: The Three-Gate Pipeline

```
GATE 1: Law of Ruin          GATE 2: Ergodicity           GATE 3: WR Dominance
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ P(Ruin) > 5%?       │ ──▶ │ Non-ergodic?         │ ──▶ │ WR < Breakeven?     │
│ 5 Domains:          │     │ Absorbing barrier?   │     │ Variance Drag > EV? │
│ Bio/Legal/Fin/      │     │ P(survive N) < 80%?  │     │ RR structure viable? │
│ Social/Psych        │     │                      │     │                      │
│ VETO if YES ❌      │     │ VETO if YES ❌       │     │ WARN if YES ⚠️      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Position Sizing: One-Third Kelly GTO Anchor (DEC-046)

```text
Full Kelly:       f* = (bp - q) / b
One-Third Kelly:  f  = f* / 3
Quarter-Kelly:    f  = f* / 4

Where:
  b = net odds (reward / risk)
  p = probability of winning
  q = 1 - p

MacLean, Thorp & Ziemba (2011) Continuous Drawdown Theorem:
  P(Drawdown >= D) = (1 - D)^(2/c - 1)
  For D = 0.50 (50% drawdown / account halving):
    Full Kelly (c = 1.00) : P(down 50%) = 50.0%  (Suicidal)
    Half-Kelly (c = 0.50) : P(down 50%) = 12.5%  (Violates Law #1: 12.5% > 5%)
    Law #1 Cap (c = 0.38) : P(down 50%) = 5.0%   (Permissible leverage ceiling)
    One-Third  (c = 0.33) : P(down 50%) = 3.1%   (GTO Sweet Spot: keeps 55.6% compounding)
    Quarter    (c = 0.25) : P(down 50%) = 0.8%   (Defensive mode)

Example (10% EV, 1:3 R:R):
  b = 3, p = 0.55, q = 0.45
  f* = (3 * 0.55 - 0.45) / 3 = 0.40 (40% — suicidal)
  f  = 0.40 / 3 = 0.133 (13.3% — One-Third Kelly campaign cap)
  Practical: Cap at 1-2% risk per trade for operational safety.
```

**Rule**: Half-Kelly violates Law #1 (12.5% P(halving) > 5%). One-Third Kelly (0.33x) is the GTO ceiling per CAMPAIGN (aggregate exposure across layers). Industry standard 1-2% risk per trade is the operational floor.

### The Variance Shields

| Arena | Variance Shield | Rationale |
|-------|----------------|-----------|
| FX / CFD Trading | 2% max risk per trade | Ensures >95% survival over 100-trade sequences |
| Poker (Spins) | 300 buy-ins minimum | Neutralizes high-variance format |
| Poker (Cash) | 40 buy-ins minimum | Lower variance, faster recovery |
| Casino (Arbitrage) | 309-unit bankroll | Points farming protocol |

### The Iron Laws

| Law | Rule | Source |
|-----|------|--------|
| **No Weekend Holding** | Close ALL positions before market close Friday | CS-d11d5a7c: Weekend gaps = unhedgeable ruin |
| **No Martingale** | Never double down after a loss | CS-459: Martingale = guaranteed ruin at N→∞ |
| **Commission Awareness** | Calculate REAL EV after all friction | CS-9a7c4607: 46% commission drag on FX → pivot to 0-commission oil |
| **Drop-Down Trigger** | If bankroll hits X% drawdown, mechanically drop stakes | CS-76208648: Eliminate psychological tilt |
| **No FOMO Re-entry** | If stopped out, wait for fresh setup | TRD-369: "Fuck-Unfuck" principle |

### Layering Strategy (Advanced)

For mean-reversion and grid-based entries:

```
Layer 1: 30% of intended position at first signal
Layer 2: 30% at confirmation (e.g., structure break)
Layer 3: 40% at optimal entry (e.g., liquidity sweep)

Total risk across all layers: Still ≤ 2% of capital
```

### The Efficiency-Survival Inversion (MP-2)

| "Efficient" (Looks Smart, Kills You) | "Robust" (Looks Dumb, Survives) |
|:-------------------------------------|:-------------------------------|
| Full Kelly sizing | One-Third Kelly (0.33x GTO) |
| 58% allocation, max profit | 6% allocation, survives tail |
| Narrow SL + High R:R | Wide SL + High WR |
| Hold for "the big move" | Partial profit + re-entry |

**Rule**: Growth ≈ Edge − (sigma^2 / 2) = Edge − (Variance / 2). Variance drag is a SUBTRACTION term. High WR structurally dominates High RR (TRD-367).

### Post-Trade: Journal Analysis

After every trade or session:

1. **Classify the outcome**: Win/Loss/Breakeven
2. **Classify the process**: Good Process / Bad Process
3. **Map to drawdown type**:
   - Type A: Bad luck (good process, bad outcome) → Continue
   - Type B: Bad execution (bad process) → Fix the leak
   - Type C: System drift (rules changed) → Recalibrate
4. **Log friction costs**: Spread + commission + swap = REAL cost per trade

## Output Template

```
TRADE GATE REPORT
─────────────────
Setup:          [Description]
Gate 1 (Ruin):  [✅ PASS / ❌ VETO — domain: ...]
Gate 2 (Ergo):  [✅ PASS / ❌ VETO — P(survival): X%]
Gate 3 (WR/RR): [✅ PASS / ⚠️ WARN — variance drag: ...]
Position Size:  [X% of capital = $Y / Z lots]
Stop Loss:      [$X / Y pips]
Risk:Reward:    [1:X]
Weekend Check:  [CLEAR / CLOSE BEFORE FRIDAY]
Commission:     [$X per round-trip / Y% of expected profit]

VERDICT: [CLEARED / VETOED / CONDITIONAL]
```

## Absorbed Protocols & Skills

### Trading Protocols (7)
TRD-367 (High WR Supremacy), TRD-368 (Trade Structure Levers), TRD-369 (Fuck-Unfuck Principle), TRD-46 (Trading Methodology), TRD-56 (Shopee Refugee Arbitrage), TRD-57 (Influencer Put Option), TRD-65 (Arbitrage Formula)

### Decision Protocols (Trading-Related)
DEC-046 (Kelly Mandate), DEC-050 (Risk Pareto), DEC-101 (Inverse Sizing Matrix)

### Absorbed Skills
- `trading-risk-gate` → Pre-trade 3-gate pipeline
- `zenith-execution` → One-Third Kelly, stop-loss calc, Monte Carlo, portfolio rebalance
- `trade-journal-analyzer` → Post-trade drawdown classification

### Key Case Studies
CS-367 (High WR Supremacy), CS-461 (Multi-Timeframe Cascade), CS-462 (Mean Reversion), CS-463 (Fog of War), CS-465 (EURUSD Structure), CS-466 (BCG Trade Classification), CS-487 (Layering Strategy BTC), CS-493 (Toto EEV), CS-495 (Macro-Meso-Micro Barbell), CS-500 (Trading System Map), CS-502 (MTT Variance), CS-509 (FX Sim Stats Audit), CS-525 (FX Data Refined), CS-534 (Stop-Out Opportunity Cost), CS-560 (Stochastic-Deterministic Engine Map)

## Failure Modes & Mitigations

| Failure | Mitigation |
|---------|------------|
| **FOMO Override** | Gate 1 is NON-NEGOTIABLE. No "just this once." |
| **Revenge Trading** | Drop-Down Trigger is MECHANICAL, not discretionary |
| **Weekend Gap Risk** | Hard rule: Close ALL by Friday COB. No exceptions. |
| **Commission Blindness** | Calculate friction FIRST, then decide if edge survives |
| **Hindsight Bias** | Carnot Engine Fallacy (§325): The "perfect trade" only exists in hindsight |

## Validated Patterns (Empirical)

- [V] **High WR > High RR**: Variance Drag (sigma^2/2 = Variance/2) geometrically destroys low-WR portfolios. A 70% WR / 1:1 RR system dominates a 30% WR / 1:3 RR system over N>100 trades. | Reapply: Every system design.
- [V] **Commission Drag Kills Edge**: High round-trip FX commissions vs 0-commission instruments erode EV. Switching arenas can be a higher-EV move than optimizing entries. | Reapply: Every new instrument evaluation.
- [V] **One-Third Kelly is Maximum**: Full Kelly = theoretical ceiling (50% P(halving)). Half-Kelly still carries 12.5% P(halving). One-Third Kelly (0.33x) = Law #1 compliant GTO ceiling (3.1% P(halving), 55.6% compounding). | Reapply: Every position sizing calculation.
- [V] **Weekend Gaps are Non-Ergodic**: A single weekend gap can wipe weeks of gains. The expected cost of holding > expected gain. | Reapply: Every Friday.

## References

- META_PATTERNS.md — MP-2 (Efficiency-Survival Inversion)
- CS-560 — The Engine Map
- [bionic-decision-engine](../decision/bionic-decision-engine/SKILL.md) — Parent engine for non-capital decisions
