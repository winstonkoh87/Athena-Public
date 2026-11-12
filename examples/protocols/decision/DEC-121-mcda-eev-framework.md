---
created: 2026-02-08
last_updated: 2026-07-22
---

# Protocol 121: Decision Frameworks (MCDA / EEV / Pairwise)

> **Source**: Zero-Point Codex v3.0 / Few-shot v29
> **Domain**: Decision / Multi-Criteria Optimization
> **Priority**: ⭐⭐⭐ Critical

---

## 1. MCDA (Multi-Criteria Decision Analysis)

> **Definition**: A systematic process for evaluating multiple conflicting criteria in decision making. Used for "Exoskeleton" selection (IDEs), hardware purchases, or arena selection.

### The MCDA Process

1. **Define Goal**: "What is the single most important outcome?"
2. **Identify Options**: List at least 3 distinct paths.
3. **Define Criteria**: (e.g., Sovereignty, Intelligence, Speed, Cost).
4. **Weighting**: Assign importance to each criterion (Total = 100%).
5. **Scoring**: Rank options 1-10 for each criterion.
6. **Calculate**: `Weighted Score = Score * (Weight / 100)`.

---

## 2. Pairwise Comparison

> **Definition**: A method of comparing entities in pairs to judge which of each entity is preferred, or has a greater amount of some quantitative property.

### Use Case

When criteria are qualitative and difficult to weight linearly (e.g., "Aesthetics vs. Security").

**Mechanism**:

- Compare A vs B, B vs C, A vs C.
- Assign a winner to each.
- The option with the most "wins" is the prioritized choice.
- **Goal**: Resolves "Inconsistency" in complex weighting models.

---

## 3. EEV (Economic Expected Value)

> **Definition**: Expected Aggregate Value that accounts for Mathematical Expected Value (MEV), subjective probability weighting, and utility functions.

### The Formula

`EEV = MEV + E(U) - E(O)`

- **MEV**: Mathematical Expected Value (Monetary Expected Value). `MEV = ∑ [ p_i * v_i ]`
- **E(U)**: Expected Utility based on stakeholder utility functions (accounts for human factors, non-monetary value, and *Law #1: Risk of Ruin* via Veto Clause).
- **E(O)**: Expected Opportunity Cost.

**Operational Implementation**:

- If any single `u(x_i) = -∞` (Ruin), the total `EEV` defaults to **-∞** regardless of probability or MEV.
- This is the mathematical enforcement of **Law #1**.

---

## 4. Decision Rule (The Solver)

1. **Run MCDA** to find the "Rational Best".
2. **Run Pairwise** to check for "Gut/Value" alignment.
3. **Run EEV** to ensure no outcome violates **Law #1** and to optimize for true utility.
4. **Verdict**: The option that clears the EEV safety gate and leads the MCDA/Pairwise ranking.

---

## Tags

**Tags**: #protocol #decision #mcda #eev #mev #pairwise #optimization #zero-point-codex
