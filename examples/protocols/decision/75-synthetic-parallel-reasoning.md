---

created: 2025-12-15
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-15
last_updated: 2026-01-09
---

# Protocol 75: Synthetic Parallel Reasoning (v3.0)

> **Purpose**: True parallel reasoning via concurrent API calls with adversarial convergence gate.
> **Status**: ACTIVE (Jan 2026)
> **Version**: 3.0 (True Parallelism)
> **Tags**: `#reasoning` `#architecture` `#parallel` `#protocol` `#deep-think`

---

## 1. Overview

All complex problems (Λ > 30) are processed through **four parallel API calls** with iterative refinement:

| Track | Role | Core Question |
|-------|------|---------------|
| **A: Domain-Native** | Apply arena-specific protocols | "What does domain expertise say?" |
| **B: Adversarial** | Challenge premises, find flaws | "What could go wrong?" |
| **C: Cross-Domain** | Isomorphic pattern search | "Where have I seen this before?" |
| **D: Zero-Point** | First principles inversion | "What if the opposite is true?" |

> [!IMPORTANT]
> **v3.0 Change**: Tracks are now **true parallel API calls** via `asyncio`, not prompt-simulated parallelism. This prevents attention bleeding and ensures Track B is genuinely adversarial.

---

## 2. Dispatch Flow (v3.0)

```
INPUT
  │
  ├──► [API Call 1] Track A ──┐
  ├──► [API Call 2] Track B ──┼──► SYNTHESIS ──► CONVERGENCE GATE ──► OUTPUT
  ├──► [API Call 3] Track C ──┤                        │
  └──► [API Call 4] Track D ──┘                        │
                                                       ▼
                                            (if score < 85)
                                                       │
                                            ◄──────────┘
                                            ITERATE WITH FEEDBACK
```

**Execution**: `python3 .agent/scripts/parallel_orchestrator.py "<query>"`

---

## 3. Track Specifications

### Track A: Domain-Native Analysis

- Load relevant protocols from SKILL_INDEX based on arena
- Apply standard frameworks (SDR for Career, Arbitrage for Business, etc.)
- Output: Primary recommendation with supporting analysis

### Track B: Adversarial

- Challenge the user's premise (Protocol 40: Frame vs Structural)
- Identify ruin vectors (Law #1)
- Check for Type B (structural) vs Type A (variance) losses
- Output: Risk assessment, premise flaws, failure modes

### Track C: Cross-Domain

- Invoke Protocol 67 (Cross-Pollination)
- Search case studies for isomorphic patterns
- Pull insights from unrelated arenas
- Output: At least one non-obvious parallel from another domain

### Track D: Zero-Point (Deep Think)

- Invoke Protocol 140 (Inversion)
- Apply "Backwards Law" and "First Principles"
- Question the nature of the reality/problem itself
- Output: Metaphysical/Philosophical perspective reframing the "Game"

---

## 4. Synthesis Rules

When tracks converge → output the consensus.

When tracks **conflict** → apply priority order:

1. **Laws** (Law #1-4) — absolute veto
2. **Track B** (Adversarial) — if ruin risk identified, flag prominently
3. **Track A** (Domain) — primary recommendation
4. **Track C** (Cross-Domain) — enrichment, not override
5. **Track D** (Deep Think) — contextual grounding (the "Why")

---

## 5. Transparency Protocol

### Default (Simple Queries)

- Single integrated response
- No visible track breakdown

### Triggered (Complex/High-Stakes)

### Triggered (Complex/High-Stakes)

Show explicit track breakdown AND **Visual Abstract (Mermaid)** when:

- Tracks diverge significantly
- User invokes `/think` or `/ultrathink`
- Problem involves >5% ruin risk
- User explicitly asks for full analysis

### Format When Visible

```
## Track A (Domain): [Arena Name]
[Analysis]

## Track B (Adversarial)
[Challenges / Risks]

## Track C (Cross-Domain)
[Isomorphic pattern from X domain]

## Track D (Zero-Point)
[Metaphysical Inversion / First Principles]

## Synthesis
[Integrated recommendation]
```

---

## 6. Adversarial Convergence Gate (v3.0)

> [!IMPORTANT]
> **Replaces**: Boredom Heuristic (variance < 5% for 3 turns) — DEPRECATED.

After synthesis, Track B re-evaluates the combined output:

| Criterion | Points |
|-----------|--------|
| Logical Coherence | 0-25 |
| Risk Coverage | 0-25 |
| Actionability | 0-25 |
| Blind Spot Check | 0-25 |
| **Total** | **0-100** |

**Convergence Rule**:

- Score ≥ 85 → **OUTPUT** (converged)
- Score < 85 → **ITERATE** with critique feedback (max 3 iterations)

---

## 7. Tiered Routing (v3.0)

| Query Complexity | Path | API Calls |
|------------------|------|----------|
| Λ ≤ 30 | **Light**: Native model + memory/logging | 1 |
| Λ > 30 | **Heavy**: Parallel orchestrator | 4-12 |

---

## 8. Quick Reference

| Situation | Behavior |
|-----------|----------|
| Simple factual query (Λ ≤ 30) | Skip orchestrator, direct answer |
| Strategic decision (Λ > 30) | Full 4-track parallel + convergence gate |
| `/think` invoked | 4-track visible + deep analysis |
| `/ultrathink` invoked | 4-track + max iterations (3) |
| Ruin risk detected | Track B gets priority veto |

---

## References
- [Protocol 124: SDR Diagnosis](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/124-sdr-diagnosis.md)

- [Protocol 115: First Principles Deconstruction](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/115-first-principles-deconstruction.md)

- [Core_Identity.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/Core_Identity.md) — Laws #1-4
- [Protocol 67](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/research/67-cross-pollination.md) — Cross-Domain Isomorphism
- [Protocol 140](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/140-base-rate-audit.md) — Zero-Point Inversion
- [Protocol 40](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/40-frame-vs-structural-problem.md) — Frame vs Structural

---

## Tagging

# protocol #framework #75-synthetic-parallel-reasonin
