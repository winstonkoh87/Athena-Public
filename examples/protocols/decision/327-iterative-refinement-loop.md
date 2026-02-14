---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2026-01-05
---

# Protocol 170: Iterative Refinement Loop (Poetiq Pattern)

> **Status**: ACTIVE  
> **Source**: Poetiq ARC-AGI Scaffolding Analysis (Dec 2025)  
> **Trigger**: Complex problems requiring multiple solution attempts, `/ultrathink` with high-stakes flag

---

## Philosophy

> "Loop until solved, or until diminishing returns detected."

Most reasoning is single-pass. This protocol enables **multi-iteration refinement** with explicit termination conditions.

---

## Trigger Conditions

- [ ] Problem has no obvious single solution
- [ ] Multiple valid approaches exist
- [ ] Stakes are high (>$10K or >6 month impact)
- [ ] User explicitly requests deep iteration
- [ ] Initial attempt scored <80% confidence

---

## Structure

### Phase A: Initial Hypothesis Generation

Generate 3-5 candidate solutions using existing parallel reasoning ([Protocol 75](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md)).

**Output**: Ranked list of hypotheses with confidence scores.

---

### Phase B: Implement & Check

For each hypothesis (top 2-3):

1. **Generate concrete implementation** — Code, plan, steps, or strategy
2. **Run mental simulation** — Walk through execution, identify failure modes
3. **Stress test** — Edge cases, adversarial scenarios, what-ifs
4. **Score against success criteria** — 0-100% confidence

**Output**: Score matrix per hypothesis.

---

### Phase C: Refine or Terminate

```
Decision Logic:

IF best_score >= 90%:
    → TERMINATE: Output best solution with high confidence

ELIF iteration_count >= max_iterations (default: 5):
    → TERMINATE: Output best solution + caveat about iteration limit

ELIF delta_improvement < 5% for 2 consecutive iterations:
    → TERMINATE: Diminishing returns detected

ELSE:
    → REFINE: Use feedback to generate improved hypotheses
    → GOTO Phase A
```

---

### Phase D: Self-Audit & Deposit

1. Log iteration count + score trajectory
2. Record what worked / what didn't
3. Deposit pattern to session log for calibration
4. If reusable insight found → file to relevant case study or protocol

---

## Termination Conditions

| Condition | Trigger | Action |
|-----------|---------|--------|
| **Success** | Score ≥ 90% | Output solution |
| **Max Iterations** | 5 loops completed | Output best + caveat |
| **Diminishing Returns** | Δ < 5% for 2 iterations | Early terminate |
| **Timeout** | Context limit approaching | Output best available |

---

## Example Application

```
User: Design a compensation structure for my sales team.

Iteration 1:
- Hypothesis A: Fixed salary + commission
- Hypothesis B: Pure commission
- Hypothesis C: Base + quota bonus
- Scores: A=70%, B=50%, C=75%

Iteration 2 (refine C):
- C.1: Base + tiered quota bonus
- C.2: Base + accelerators above target
- Scores: C.1=82%, C.2=85%

Iteration 3 (refine C.2):
- C.2.1: Add team bonus component
- Score: 88%

Iteration 4:
- Score: 89% (Δ = 1%)

Iteration 5:
- Score: 89% (Δ = 0%)
→ TERMINATE: Diminishing returns. Output C.2.1 variant.
```

---

## Integration Points

- Activated by `/ultrathink` when high-stakes detected
- Uses [Protocol 75](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md) for parallel hypothesis generation
- Uses [Protocol 38](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md) for verification phases
- Deposits to RSI per [Protocol 140](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/140-base-rate-audit.md)

---

## Tags

# protocol #reasoning #iteration #refinement #poetiq #stealable

## Related Protocols

- [Protocol 128: Internal Family Systems](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/128-internal-family-systems.md)
