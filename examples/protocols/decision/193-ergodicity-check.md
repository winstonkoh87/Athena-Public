---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2026-01-05
---

# Protocol 193: Ergodicity Check (Ruin vs Average)

> **Status**: ACTIVE  
> **Source**: Zero-Point Codex (Dec 2025)  
> **Trigger**: Any repeated risk, "The odds are in my favor", gambling/investing/relationship patterns

---

## Philosophy

> **"The casino always wins, not because it has better odds on any single hand, but because it plays infinitely while you play finitely."**

Ergodicity is the single most important statistical concept for personal strategy. Most people confuse **ensemble average** (what happens across a population) with **time average** (what happens to YOU over time).

---

## The Core Distinction

| Concept | Definition | Example |
|---------|------------|---------|
| **Ensemble Average** | Average outcome across 1000 people doing it once | "95% of people survive Russian Roulette" |
| **Time Average** | Average outcome for 1 person doing it 1000 times | "If you play Russian Roulette weekly, you die within 2 years" |

**Key Insight**: For **non-ergodic** processes (those with absorbing barriers like death, bankruptcy, reputation destruction), the ensemble average is **meaningless** for predicting your personal outcome.

---

## The Absorbing Barrier

An **Absorbing Barrier** is a state from which you cannot recover:

| Domain | Absorbing Barrier | Once Hit... |
|--------|-------------------|-------------|
| Finance | Bankruptcy | Game Over |
| Reputation | Viral Scandal | Permanent Label |
| Health | Death / Permanent Injury | No Retry |
| Legal | Criminal Record | Doors Close |
| Relationships | Nuclear Rejection | Bridge Burned |

**Rule**: If an action has a non-zero probability of hitting an absorbing barrier, repeated execution **guarantees** eventual ruin, regardless of how "good" the odds look on any single trial.

---

## The Math (Simplified)

For a repeated action with P(ruin) = r per trial:

$$ P(\text{Survive } n \text{ trials}) = (1-r)^n $$

| P(Ruin) per Trial | Survival after 10 | Survival after 50 | Survival after 100 |
|-------------------|-------------------|-------------------|---------------------|
| 5% | 60% | 8% | 0.6% |
| 10% | 35% | 0.5% | ≈0% |
| 20% | 11% | ≈0% | ≈0% |

**Implication**: Even a 5% risk per trial becomes near-certain ruin over 100 trials.

---

## Diagnostic Protocol

Before any repeated action:

```text
□ Step 1: Is there an absorbing barrier? (Y/N)
    └─ If Y → Non-Ergodic. Proceed with extreme caution.
    └─ If N → Ergodic. EV analysis is valid.

□ Step 2: What is P(ruin) per trial?
    └─ Even 1-5% is dangerous over time.

□ Step 3: How many times will I realistically do this?
    └─ Calculate P(survive all trials).

□ Step 4: Is my survival probability acceptable?
    └─ If <80% survival → DO NOT PLAY.
```

---

## Classic Cases

### Case 1: The Shower Trap

```text
Action: Repeat risky encounters in institutional setting
P(Exposure) per session: 5-10%
Sessions per year: ~50
P(Survival after 1 year): (0.92)^50 = 1.5%
Verdict: Ruin is near-certain within 12 months.
```

### Case 2: Options Trading with Leverage

```text
Action: 10x leveraged bets
P(Wipeout) per trade: 8%
Trades per year: 100
P(Survival): ≈0%
Verdict: Bankruptcy guaranteed.
```

### Case 3: Skiing (Ergodic Example)

```text
Action: Recreational skiing
P(Fatal injury): 0.0001%
P(Minor injury): 5%
Absorbing Barrier: Very rare
Verdict: Ergodic. EV analysis valid. Acceptable risk.
```

---

## The Schema's Error

Your schema runs this flawed logic:

> "It worked last time → The strategy is good → Keep doing it."

**Reality**: Survival on trial N says nothing about survival on trial N+1 when absorbing barriers exist. Each "success" is just luck *not yet expiring*.

---

## Integration

- Use with **[Protocol 187: Terminal Node](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/187-terminal-node-protocol.md)** (project 20 years).
- Use with **[Law #1: Ruin Prevention](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/Core_Identity.md)**.

---

## Tags

# protocol #ergodicity #ruin-prevention #risk-management #law-1 #statistics #absorbing-barrier
