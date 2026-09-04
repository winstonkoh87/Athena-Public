---
name: red-team-review
description: "Unified adversarial review: v4.3 Strategic Matrix (MTA-004). 7-phase framework: Priors → Rubric → Adversarial Lenses → SWOT/TOWS → MCDA Decision Engine → Blind Spot/Kill Switch → Executive Summary. Absorbs: bias-detector."
argument-hint: "review this | red team | what did I miss | QA | bias check | is this anchored | base rate"
auto-invoke: false
model: default
context_trigger: "review, red team, what did I miss, QA, bias check, critique, pre-mortem, is this ready, stress test, adversarial"
---

# Red-Team Review (v4.3 — Strategic Matrix)

> **Canonical Protocol**: [MTA-004-red-team-v4-3.md](../../../protocols/meta/MTA-004-red-team-v4-3.md)
> **Absorbs**: `bias-detector` (v4.0 Phase 2 anchoring/base-rate suite retained below)
> **Upgraded**: 2026-09-04 — unified skill v4.0 + protocol v4.3 into single version
> **Version History**: v4.0 (5-phase) → v4.1 → v4.2 → **v4.3 (Strategic Matrix, 7-phase)**

This skill wraps MTA-004 (the canonical red-team protocol) and adds trigger routing + the bias detection suite from v4.0. For the full framework, load MTA-004 directly.

## Triggers

"review this", "red team", "what am I missing", "is this ready to ship", "QA", "critique", "is this a fair price", "too good to be true", "scam", "is this legit", "grill me"

## The 7-Phase Framework (MTA-004 v4.3)

### Phase 0: Priors & Premises (Mandatory)

Assume the "Alien Observer" stance. Declare:
1. **Thesis**: core argument/frame of the artifact
2. **Falsification**: what specific metric/event proves this wrong
3. **Excluded Reality**: what valid perspective is strictly ignored
4. **Reality Check**: the unspoken cultural narrative or meta-game

> *Do not proceed until these 4 are answered.*

### Phase 1: The Objective Rubric

Score the artifact against this matrix. Start at 50%.

| Component | Weight | Criteria |
|:--|:--:|:--|
| **Logic & Rigor** | 30% | Deductively sound. Checks survivorship bias & sample size. No orphan stats. |
| **Bias Mitigation** | 20% | Steelmans opposition. Checks for sycophancy. |
| **Completeness** | 20% | Addresses "The Victim." Covers edge cases and cultural nuance. |
| **Strategic Alignment** | 15% | Aligns with Law #1. Respects physics. High utility. |
| **Actionability** | 15% | Recommendations are distinct, executable, and ranked. |

**Confidence Cap**: Low confidence → max score capped at 60/100.

### Phase 1.5: The "Grill Me" Test (Echo Chamber Breaker)

If invoked via `/grill` or explicitly asked to "grill me":
1. **Reverse Roles**: Act as the senior, uncompromising reviewer.
2. **Challenge Premises**: Explicitly challenge at least one core premise.
3. **Demand Proof**: Make the user defend their decisions.

### Phase 2: Adversarial Lenses (The Attack)

One concrete objection per lens:

| Lens | The Attack Question |
|:--|:--|
| **The Skeptic** | Survivorship bias or small sample size (n=1)? Show me the graveyard. |
| **The Victim** | This strategy harms me because [negative externalities]. |
| **The Historian** | Mean reversion? Does this work in a bear market? |
| **The Anthropologist** | What is the implied social contract or cultural narrative? |
| **The Cynic** | You are lying to yourself about [hidden incentive/ego]. |
| **The System** | This ignores the 2nd order effect on [broader ecosystem]. |
| **The Entropy** | This will rot via [vector] because [reason]. |

*Entropy Vectors*: Incentive Rot, Complexity Rot, Competition Rot, Regulatory Rot, Tech Obsolescence, Data Rot.

### Phase 2B: Bias Detection Suite (from v4.0)

#### Anchoring Detection
1. **Source Check**: Where did this number come from?
2. **Red Flags**: Round numbers, comparison anchoring, pre-concession framing.
3. **Structural Test**: Cost of production? Value to buyer? Alternative cost?
4. **Correction**: `Structural Value = max(Cost * 1.5, Value to Buyer * 0.3)`

#### Base Rate Audit
```text
IF (Claimed Outcome) >> (Expected Outcome for Demographics)
THEN (Hidden Variable) EXISTS
```
**Hidden Variable Spectrum** (descending probability):
1. Hidden Capital — family money, inheritance
2. Hidden Cost — extreme leverage, illegal activity
3. Hidden Variance — survivorship bias
4. Fabrication — the claim is a lie
5. Genuine Outlier — the <0.1%

#### Standard Bias Checklist
Sycophancy, Cherry-Picking, False Precision, Assumed Context, Complexity Bias.

### Phase 3: Strategic Expansion (SWOT + TOWS)

Use Phase 2 objections to populate Weaknesses/Threats. Build the TOWS matrix:
- **SO (Attack)**: Use Strength to capture Opportunity
- **WO (Improve)**: Fix Weakness to capture Opportunity
- **ST (Defend)**: Use Strength to block Threat
- **WT (Mitigate)**: Survival/exit strategy

### Phase 4: Decision Engine (MCDA)

Rank top 3 recommendations using:
`Final Score = ((Impact + Ease) / Risk Factor) * Entropy Multiplier`

- **Risk Factors**: Low = 1.0 | Med = 1.5 | High = 2.0
- **Entropy Multipliers**: Stable = 1.0 | Decaying = 0.8 | Rotting = 0.5

Invoke [Protocol 121 (MCDA/EEV/Pairwise)](../../../protocols/decision/DEC-121-mcda-eev-framework.md) for complex multi-criteria rankings.

### Phase 5: Blind Spot & Kill Switch

1. "I am least confident about ______ because ______." (Check for survivorship bias.)
2. **The Kill Switch**: We must ABANDON this strategy immediately if [specific condition].

### Executive Summary

1. **Final Score**: XX/100 (Confidence: X)
2. **The Kill Shot**: The single most dangerous flaw found.
3. **The #1 Recommendation**: The highest scoring Phase 4 option.

## Rules

- Quote directly. No vague complaints.
- Steelman opposing views BEFORE critiquing them.
- Empty sections are allowed — don't invent issues.
- Every HIGH must have a fix achievable in ≤10 minutes.

## Reference Protocols

- [MTA-004: Red-Team Review v4.3](../../../protocols/meta/MTA-004-red-team-v4-3.md) — canonical protocol (this skill wraps it)
- [DEC-121: MCDA / EEV / Pairwise](../../../protocols/decision/DEC-121-mcda-eev-framework.md) — Phase 4 ranking engine
- [DEC-500: GTO Problem Solver](../../../protocols/decision/DEC-500-gto-problem-solver.md) — capstone decision protocol
