---
name: trading-risk-gate
description: "Unified pre-trade safety gate: Ruin check (Law #1), ergodicity audit, and win-rate dominance validation. Absorbs: ergodicity-check, law-of-ruin, win-rate-dominance."
argument-hint: "ruin check | should I take this trade | is this safe | compare WR vs RR"
auto-invoke: true
model: default
context_trigger: "ruin, is this safe, should I risk, veto, ergodic, sequence risk, WR vs RR, position size, Law #1, bankruptcy"
---

# Trading Risk Gate (Pre-Trade Safety)

> **Absorbs**: `ergodicity-check`, `law-of-ruin`, `win-rate-dominance`

Unified pre-trade gate. Answers: "Should I take this trade?" by running three checks in sequence.

## Triggers

"is this safe", "should I risk", "ruin", "Law #1", "veto", "ergodic", "sequence risk", "wr vs rr", "win rate stability", "why am I losing with 1:3", "absorbing state", "all-in", "bankruptcy"

## The Three-Gate Pipeline

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

### Gate 1: Ruin Class Check (Law #1)

| Layer | Domain | Event Horizon |
|-------|--------|---------------|
| 1 | Biological | Death, permanent disability |
| 2 | Legal | Incarceration, criminal record |
| 3 | Financial | Bankruptcy, margin call |
| 4 | Social | De-platforming, exile |
| 5 | Psychological | Burnout Stage 4, loss of agency |

**VETO** if P(Ruin) > 5%. No exceptions.

### Gate 2: Ergodicity Audit

- Ensemble average ≠ Time average for non-ergodic processes (Taleb / Ole Peters). Never accept ensemble odds for a time decision — you only get one trajectory.
- Do NOT apply `(1 - r)^n` with `r = fraction risked per trade`; that formula applies only when `r` is the per-trial probability of a total wipeout event.
- For stopped trading strategies, compute gambler's ruin (`RoR`) via `scripts/gto_exec.sh ruin ...`, `decision_screen(action='ruin', ...)`, or `zenith-execution` Monte Carlo (absorbing barrier at 0.2× capital).
- **VETO** if P(ruin) > 5% (P(survival) < 95%) over the planned trial sequence.

### Gate 3: Win Rate Dominance

- High WR / Low RR systems structurally dominate High RR / Low WR systems
- Variance Drag (`sigma^2 / 2 = Variance / 2`) geometrically destroys low-WR portfolios
- Validates that the system's WR sustains the chosen RR structure

## Output

```
RISK GATE REPORT
────────────────
Gate 1 (Ruin):      [✅ PASS / ❌ VETO — domain: ...]
Gate 2 (Ergodicity): [✅ PASS / ❌ VETO — P(survival): X%]
Gate 3 (WR/RR):     [✅ PASS / ⚠️ WARN — variance drag exceeds ...]

VERDICT: [CLEARED / VETOED]
```

## Reference Protocols

- Protocol 193: Ergodicity Check
- Protocol 367: High Win-Rate Supremacy
- Law #1: No Irreversible Ruin
