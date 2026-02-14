---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2026-01-05
---

# Protocol 180: Utility Function Analysis Framework

> **Status**: ACTIVE  
> **Source**: Deep analysis template extraction (Dec 2025)  
> **Trigger**: Complex decision with multiple stakeholders, high-stakes scenarios, relationship/business/life decisions

---

## Philosophy

> **"Never ask WHY. Ask WHAT FOR."**

Behavior that seems irrational is just optimizing for a utility you haven't identified yet. This protocol provides the complete framework for decoding utility functions and making GTO decisions.

---

## Trigger Conditions

- [ ] Decision involves multiple stakeholders with different incentives
- [ ] High stakes (>$10K, >6 month impact, or ruin-class risk)
- [ ] Behavior seems "irrational" or "confusing"
- [ ] Need to choose between multiple strategic paths
- [ ] Relationship/social dynamics require analysis

---

## Phase I: Upstream Diagnosis

Before solving the presented problem, identify the **actual** problem.

| Question | Purpose |
|----------|---------|
| What problem is the user presenting? | Surface-level request |
| What problem are they actually facing? | Root cause |
| Is this tactical (L0-L1) or existential (L4-L5)? | Determine depth |

**Template**:

```
Presented Problem: [What they asked]
Actual Problem: [What's really happening]
Root Cause: [Why this keeps happening]
```

---

## Phase II: Validation

Acknowledge reality before prescribing solutions:

- [ ] Acknowledge what happened factually
- [ ] Validate emotional experience
- [ ] Confirm legitimate aspects of their position
- [ ] Establish trust before delivering hard truths

---

## Phase III: Utility Function Extraction

### 3A: Deep Utility Function Notation

For each stakeholder, enumerate their optimization targets:

```
U(Stakeholder) = W₁×Factor₁ + W₂×Factor₂ + W₃×Factor₃ + W₄×Factor₄

Where:
- W = Weight (must sum to 1.0)
- Factor = What they're optimizing for
```

**Example**:

```
U(JJ) = 0.40×Validation + 0.30×LowEffort + 0.20×Optionality + 0.10×Entertainment

U(TuitionAgent) = 0.50×CommissionVelocity + 0.30×LowFriction + 0.20×TutorCompliance
```

### 3B: Stakeholder GTO Table

| Stakeholder | Primary Utility Function | GTO Move |
|-------------|--------------------------|----------|
| You | [What you optimize for] | [Best strategy given incentives] |
| Party B | [What they optimize for] | [Their likely move] |
| Institution | [What they optimize for] | [Their enforcement pattern] |

### 3C: De Facto vs De Jure Matrix

| Dimension | De Jure (Rules/Law) | De Facto (Reality) |
|-----------|---------------------|-------------------|
| Power | Formal equality | Real asymmetry |
| Enforcement | What rules say | What actually happens |
| Consequences | Official penalties | Actual outcomes |
| Protection | Theoretical rights | Practical defense |

**Key Insight**: Most people operate on De Jure. Winners operate on De Facto.

### 3D: Counterfactual Thinking

| Direction | Question | Utility Impact |
|-----------|----------|----------------|
| **Upward** | If you'd done better... | +X utility |
| **Downward** | If it had gone worse... | -Y utility |

**Asymmetry Check**: If downward >> upward, the risk is non-ergodic.

---

## Phase IV: Probabilistic Modeling

### 4A: Decision Tree

```
Current Position
    ├── Path A: [Action 1]
    │   ├── Node A1: [Outcome 1] (P=X%)
    │   │   └── Utility: [+/-]
    │   └── Node A2: [Outcome 2] (P=Y%)
    │       └── Utility: [+/-]
    │
    └── Path B: [Action 2]
        └── Outcome: [Result]
           └── Utility: [+/-]
```

### 4B: Expected Value Calculation

```
EV(Path A) = P₁×U₁ + P₂×U₂

Where:
- P = Probability of outcome
- U = Utility of outcome
```

**Example**:

```
EV(Continue) = 0.40×(+150) + 0.60×(-850) = -450 utility
EV(Exit) = 1.00×(+20) = +20 utility
Δ = +470 utility in favor of Exit
```

### 4C: Scenario Modeling

| Scenario | Probability | Outcome | Utility |
|----------|-------------|---------|---------|
| Best Case | X% | [Description] | +N |
| Modal Case | Y% | [Description] | +/-M |
| Worst Case | Z% | [Description] | -K |

### 4D: Non-Ergodic Risk Check

| Question | Answer |
|----------|--------|
| Is this a repeatable game? | Yes/No |
| Can losses be averaged out? | Yes/No |
| Does one bad outcome = permanent consequences? | Yes/No |

**If any answer is "permanent consequences"**: This is **non-ergodic**. Standard risk tolerance does not apply.

---

## Phase V: Strategic Recommendations

### 5A: Cognitive Correction

| Current Schema (Distorted) | Corrected Reality Map |
|----------------------------|----------------------|
| [What they believe] | [What's actually true] |

### 5B: Option Generation

**Option 1: [Name]** ⭐ (Rating)

- Actions: [Steps]
- Rationale: [Why]
- EV: [Expected value]

**Option 2: [Name]**

- Actions: [Steps]
- Rationale: [Why]
- EV: [Expected value]

### 5C: Multi-Criteria Decision Analysis (MCDA)

| Criteria | Weight | Option 1 | Option 2 | Option 3 |
|----------|--------|----------|----------|----------|
| Safety | X% | N/10 | N/10 | N/10 |
| Upside | Y% | N/10 | N/10 | N/10 |
| Long-term | Z% | N/10 | N/10 | N/10 |
| **Weighted Score** | 100% | **X.XX** | **X.XX** | **X.XX** |

### 5D: GTO Recommendation

**THE ANSWER**: [Clear, actionable recommendation]

**Why This Dominates**:

1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

**Implementation Timeline**:

- Today: [Action]
- This week: [Action]
- This month: [Action]

---

## Quick Reference: The Universal Decoder

```
INPUT: Observed Behavior
    ↓
PROCESS: "What utility function explains this?"
    ↓
OUTPUT: Predict next move → Choose response
```

| Moralizing Frame | Reality-Based Frame |
|------------------|---------------------|
| "Why is she so rude?" | "What is she optimizing for?" |
| "That's unfair!" | "What are the incentive structures?" |
| "He should treat me better" | "What utility am I providing?" |
| "This is wrong" | "This is predictable" |

---

## Integration Points

- Use with [Protocol 38: SDTP](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md) for deep analysis
- Use with [Protocol 121: Amoral Realism](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/121-amoral-realism.md) for frame
- Feeds into [Protocol 170: Iterative Refinement](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/170-dissonance-threshold-crisis.md) for complex decisions

---

## Tags

# protocol #utility-function #decision-analysis #stakeholder-mapping #gto #amoral-realism #mcda

## Related Protocols

- [Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/121-mcda-weu-framework.md)
