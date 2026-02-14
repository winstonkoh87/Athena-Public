---
created: 2026-02-02
last_updated: 2026-02-02
version: 1.0
origin: Session 05 (Blackjack Probability Analysis)
dependencies: [Law #1, Protocol 193 (Ergodicity Check)]
tags: [decision, utility, risk, gambling, speculation, rationality]
---

# Protocol 330: Expected Aggregate Value (EAV) Framework

> **Purpose**: Integrate quantitative (financial) and qualitative (experiential) returns into a single decision metric.
> **Prime Directive**: Law #1 (No Ruin) — Veto any action with >5% Risk of Ruin, regardless of E(AV).

---

## 1. The Formula

$$E(AV) = E(V) + E(U) - E(O)$$

| Symbol | Name | Definition |
|:---|:---|:---|
| **E(V)** | Expected Financial Value | Net monetary return per time unit ($/hr) |
| **E(U)** | Expected Utility Value | Hedonic/experiential value converted to $/hr |
| **E(O)** | Expected Opportunity Cost | Value of the next-best alternative use of time ($/hr) |

---

## 2. Step-by-Step Calculation

### Step 1: Calculate E(V) — Financial Value

$$E(V) = (\text{Win Rate} \times \text{Avg Win}) - (\text{Loss Rate} \times \text{Avg Loss})$$

**Example (Blackjack $0.01 units, 300 hands/hr):**

- House Edge: -0.5%
- E(V) = -0.005 × $0.01 × 300 = **-$0.015/hr**

---

### Step 2: Calculate E(U) — Utility Value

> **Method**: Comparable Anchor + Skeptic's Discount

1. List 3 **paid** entertainment activities you **actually** buy.
2. Assign their $/hr cost.
3. Rank the target activity relative to them.
4. **Apply Skeptic's Discount**: Multiply by **0.8** (humans overestimate future enjoyment).

| Activity | Cost/hr |
|:---|:---|
| Movie | $7.50 |
| Video Game | $0.60 |
| Bar/Club | $12.50 |

**Example**: "Blackjack is slightly more fun than a video game, less fun than a movie."

- Raw Estimate: $3.00/hr
- **Skeptic's Discount**: $3.00 × 0.8 = **E(U) = $2.40/hr**

> ⚠️ **Anti-Rationalization Rule**: E(U) anchors MUST be activities you have paid for in the last 90 days. No hypotheticals.

---

### Step 3: Calculate E(O) — Opportunity Cost

> **Method**: Marginal Wage Rate + Energy Modifier

**The Energy Constraint**:
Opportunity Cost can only be claimed IF you have the **energy** to execute the alternative work RIGHT NOW.

| Energy State | E(O) Calculation |
|:---|:---|
| **High Energy** (Could work productively) | E(O) = Your hourly rate |
| **Low Energy** (Tired, need rest) | **E(O) = $0** |
| **Dead Time** (Commuting, waiting) | **E(O) = $0** |

**Example (Playing on the bus while tired):**

- E(O) = **$0/hr** (No real alternative available)

> ⚠️ **Anti-Inflation Rule**: E(O) cannot exceed your **average** hourly rate over the last 30 days, not your theoretical peak rate.

---

### Step 4: Calculate E(AV)

$$E(AV) = E(V) + E(U) - E(O)$$

**Example:**

- E(V) = -$0.02/hr
- E(U) = +$2.40/hr (after Skeptic's Discount)
- E(O) = $0.00/hr
- **E(AV) = +$2.38/hr** → ✅ Proceed

---

## 3. Decision Matrix

| Step | Check | Action |
|:---|:---|:---|
| **1. Law #1 Veto** | RoR > 5%? | ❌ **REJECT** (No exceptions) |
| **2. Variance Tax** | High variance activity? | Add **10% stress tax** to E(V) |
| **3. E(AV) Calculation** | E(AV) < 0? | ❌ **REJECT** |
| **4. E(AV) Calculation** | E(AV) = 0? | ⚖️ **NEUTRAL** (Indifferent) |
| **5. E(AV) Calculation** | E(AV) > 0 AND RoR ≤ 5%? | ✅ **ACCEPT** |

---

## 4. Required Safety Patches

### A. The Skeptic's Discount (E(U))
>
> "Multiply your initial gut feeling by **0.8**. We historically overestimate how much fun a paid activity will be."

### B. The Energy Modifier (E(O))
>
> "Opportunity Cost can only be non-zero if you have the **specific energy level** required to perform the alternative work *right now*. If you are too tired to work, E(O) = $0."

### C. The Variance Tax
>
> "If the activity has high variance (gambling, crypto, speculation), increase the cost basis in E(V) by **10%** to account for the 'Stress Tax' and emotional volatility."

### D. The Anchor Constraint (E(U))
>
> "E(U) anchors must be activities you have **actually paid for** in the last 90 days. No hypothetical comparisons."

---

## 5. Kill Switch Conditions

**ABANDON this framework immediately if:**

1. **Actual Liquid Net Worth drops by >10%** in a single month while following this protocol.
   - *Indicates*: RoR calculation was flawed or variance is unmanageable.

2. **Post-activity regret consistently exceeds pre-activity anticipation.**
   - *Indicates*: E(U) is chronically mis-estimated.

3. **E(U) becomes the dominant swing variable in >80% of decisions.**
   - *Indicates*: Framework is being gamed to rationalize bad decisions.

---

## 6. Worked Example (Entertainment Blackjack)

| Variable | Value | Notes |
|:---|:---|:---|
| **Context** | $0.01 Martingale on Natural8 | Playing for entertainment |
| **Bankroll** | $20 | Disposable "fun money" |
| **RoR** | <2% | 2,000 units = durable |
| **E(V)** | -$0.02/hr | House edge on micro-stakes |
| **E(U) Raw** | $3.00/hr | "More fun than video games" |
| **E(U) Adjusted** | $2.40/hr | Apply 0.8 Skeptic's Discount |
| **E(O)** | $0/hr | Playing during "dead time" |
| **E(AV)** | **+$2.38/hr** | ✅ Proceed |

**Verdict**: Positive E(AV). RoR is low. Law #1 satisfied. **Play for fun.**

---

## 7. Key Insights (Origin: Session 05)

1. **Humans maximize Utility, not Dollars.** The math of E(V) ignores the joy of playing.
2. **Subjective Utility must be constrained** to prevent rationalization (Skeptic's Discount).
3. **Opportunity Cost is often zero** during rest blocks, commuting, or low-energy states.
4. **Law #1 is non-negotiable.** Even a massively positive E(AV) is rejected if RoR > 5%.
5. **Sample Size matters.** In +EV systems, P(Profit) increases with $N$. In -EV systems, P(Ruin) increases with $N$.

---

## 8. The Barbell Maximizer (Optimization Strategy)

To maximize the **E(AV) Curve** over a lifetime, you must solve for **Geometric Growth** (Compound Interest) minus **Volatility Drag**.

**The Mathematical Solution**: The 90/10 Barbell.

| Component | Allocation | Role | Effect on E(AV) |
|:---|:---|:---|:---|
| **The Anchor** | 90% | Low Variance, Low Yield (Cash/Bonds) | **Survival**. Prevents Ruin (Law #1). |
| **The Convexity** | 10% | High Variance, Infinite Upside (Speculation) | **Growth**. Captures outliers. |

**Why this Maximizes E(AV):**

1. **Safety**: The Anchor ensures you never hit an absorbing barrier (Ruin).
2. **Upside**: The Convexity ensures you participate in "Black Swan" positive events.
3. **Efficiency**: It avoids the "Mediocre Middle" (Medium Risk, Capped Reward) where Volatility Drag kills compounding.

> **Directive**: Bet 10-20% on +EV/High Variance. Keep 80-90% in Safe Harbor. This is the optimal frontier.

---

## References

- [Protocol 193: Ergodicity Check](file:///Users/[AUTHOR]/Desktop/Project%20Athena/.agent/skills/protocols/decision/193-ergodicity-check.md)
- [Core Identity: Law #1](file:///Users/[AUTHOR]/Desktop/Project%20Athena/Athena-Public/examples/framework/Core_Identity.md)
- [Blackjack Apprenticeship: Bankroll Management](https://www.blackjackapprenticeship.com/blackjack-bankroll-management/)

---

# decision #utility #risk #gambling #speculation #rationality
