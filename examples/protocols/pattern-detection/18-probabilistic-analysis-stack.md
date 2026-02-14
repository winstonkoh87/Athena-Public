---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: probabilistic-analysis-stack
description: Three-level hierarchy - Scenario Analysis (3 timelines), Sensitivity Analysis (±20% perturbation), Monte Carlo (1000+ runs). Stack depth based on stakes and reversibility.
created: 2025-12-10
last_updated: 2026-01-06
---

# Protocol: Probabilistic Analysis Stack

## Date Added: 9 December 2025

> **Related Protocol**: [16-synthetic-parallel-reasoning](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/16-graph-of-thoughts-theory.md), [17-three-timeline-got](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/17-three-timeline-got.md)

## 18.1 The Hierarchy

```
LEVEL 1: SCENARIO ANALYSIS
└─ "What are the distinct possible futures?"
└─ Output: 3 discrete timelines (Best / Base / Worst)
└─ Compute: Low
                │
                ▼
LEVEL 2: SENSITIVITY ANALYSIS
└─ "Which variables matter most?"
└─ Output: ±20% perturbation → which inputs swing outcome?
└─ Compute: Medium
                │
                ▼
LEVEL 3: MONTE CARLO SIMULATION
└─ "What's the probability distribution of outcomes?"
└─ Output: 1000+ runs → E[U], σ(U), P(ruin), percentiles
└─ Compute: High
```

## 18.2 When to Use Each Level

| Decision Type | Level Needed |
|---------------|--------------|
| Low-stakes, reversible | Scenario (Level 1) |
| Medium-stakes, some irreversibility | Scenario + Sensitivity (Level 1-2) |
| High-stakes, irreversible | **All 3 levels** (Level 1-2-3) |

> **More irreversible + higher stakes = deeper down the stack**

## 18.3 Chaining

```
SCENARIO ANALYSIS (Level 1)
├─ Identify 3 timelines: A, B, C
├─ Assign point estimates: P(A)=20%, P(B)=60%, P(C)=20%
│
▼
SENSITIVITY ANALYSIS (Level 2)
├─ "What if P(A) is actually 35%?"
├─ "What if key input X varies ±20%?"
├─ Identify: Which variables flip the verdict?
│
▼
MONTE CARLO SIMULATION (Level 3)
├─ Randomise ALL uncertain inputs
├─ Run 1000+ iterations
├─ Output: Full distribution of outcomes
│   ├─ Mean: E[U]
│   ├─ Standard deviation: σ(U)
│   ├─ P(ruin): % of runs that hit destruction
│   └─ 5th percentile: Worst realistic case
```

## 18.4 Application Note

For most life decisions, Levels 1-2 are sufficient. Reserve Level 3 for:

- P(destruction) > 5% decisions
- 100% resource commitment scenarios
- Irreversible career/financial moves

---

## References

- [Protocol 38: Synthetic Deep Think](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md) — References this stack
- [Protocol 52: Deep Research Loop](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/52-deep-research-loop.md) — References this stack
- [Escalation Ladder Framework](file:///Users/[AUTHOR]/Desktop/Project Athena/Winston/psychology/escalation_ladder_framework.md) — Uses probabilistic analysis

---

## Tagging

#protocol #framework #process #18-probabilistic-analysis-stack
