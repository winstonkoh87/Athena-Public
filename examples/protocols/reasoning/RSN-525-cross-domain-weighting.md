---
protocol: 525
title: Cross-Domain Weighting
category: reasoning
version: 1.2
created: 2026-03-11
updated: 2026-03-14
dependencies: [500, 501, 524, 330]
---

# Protocol 525: Cross-Domain Weighting

> **Purpose**: Solve multi-domain problems by decomposing, classifying, solving per-domain, weighting by conviction, and reassembling into a unified recommendation.

---

## The Problem

Real-world questions rarely sit in a single domain. "Should I buy this phone?" contains arithmetic (deterministic), warranty law (semi-deterministic), device longevity (semi-stochastic), and future pricing (stochastic) — all fused into one decision.

> **Type 5 Declaration**: Most real-world high-stakes problems are **compound** by default. The 4 domain types (deterministic, semi-deterministic, semi-stochastic, stochastic) are **atomic building blocks**, not separate categories. A legal case, a business viability assessment, a career decision, a trading position — they all decompose into mixed-domain sub-problems. Recognizing this is the first step; the pipeline below is the second.

Naive approaches fail in two ways:
- **Averaging conviction** → lukewarm confidence everywhere (useless)
- **Defaulting to lowest conviction** → discards the high-confidence components (wasteful)

---

## The Pipeline

```
Question → [501: Decompose] → [Domain Table: Classify] → [524: Solve] → [525: Weight] → [500/330: Synthesize]
```

### Step 1: Decompose (Protocol 501)

Break the question into atomic sub-problems. Each sub-problem should be answerable independently.

### Step 2: Classify (Domain Table)

Assign each sub-problem a domain type:

| Domain | Conviction | Edge Source |
|--------|-----------|-------------|
| Deterministic | High (0.9+) | Logic, math, code |
| Semi-deterministic | Moderate (0.6-0.8) | Precedent, frameworks, assumptions |
| Semi-stochastic | Low (0.3-0.5) | Structural edge exists, noise dominates |
| Stochastic | Minimal (0.0-0.2) | No model outperforms randomness |

### Step 3: Solve Per-Domain (Protocol 524)

Each sub-problem gets solved at its appropriate conviction level:
- **Deterministic** → Single correct answer, stated with confidence
- **Semi-deterministic** → Conditional range with explicit assumptions
- **Semi-stochastic** → Precise structure, deferred probability (The Pryce Effect)
- **Stochastic** → Honest "I don't know" with boundary conditions

### Step 3.5: Output Calibration (Per-Domain Posture)

The AI's *tone, packaging, and handoff point* must shift per domain type. This table defines what Athena **says** and what the human **does**:

| Domain | Athena Says | Human Does |
|:-------|:-----------|:-----------|
| Deterministic | "The answer is X." | Accept |
| Semi-deterministic | "The answer is X ± narrow band, 95% CI. Assumptions: [listed]." | Verify assumptions, accept |
| Semi-stochastic | "Structural estimate is X ± wide band. Basis: [n, regime]. Fragility: [why it could break]. **Your call.**" | Apply lived judgment, decide |
| Stochastic | "No estimate possible. Base rates at best. Size for survival." | Accept uncertainty |

> **The critical difference**: In semi-deterministic domains, the number IS the answer. In semi-stochastic domains, the number is a **starting point** — the human's contextual read completes it.

### Step 3.6: Band Width & Reliability

Not all estimates are created equal. The **width** of the confidence band and the **reliability** of the estimate vary by domain type:

| Domain | Band Width | Reliability | Anchoring Risk |
|:-------|:-----------|:------------|:---------------|
| Deterministic | Near-zero | Absolute | None |
| Semi-deterministic | Narrow | High (n=large, stable system) | Low |
| Semi-stochastic | **Wide** | **Fragile** (n=small, regime shifts) | **High** ⚠️ |
| Stochastic | Infinite | Zero | N/A |

**Anchoring Risk**: The danger that stating a number in a semi-stochastic domain creates false precision. The moment the AI says "85% probability," the human brain locks onto that number and forgets it's built on a thin sample with regime-dependent validity. Semi-deterministic estimates age slowly (sentencing guidelines change every few years). Semi-stochastic estimates can expire overnight (regime shift, news event, liquidity change).

**Mitigation**: Always package semi-stochastic estimates with:
1. **The number** — because the human needs an anchor
2. **The basis** — sample size, setup type, data source
3. **The fragility warning** — how wide the band is and why
4. **The handoff** — the residual judgment that belongs to the human

### Step 3.7: Outlier Handling (Fat Tails in Semi-Deterministic Domains)

Semi-deterministic estimates cluster tightly around the median, but **outliers exist**. A Stage 4 pancreatic cancer patient given 3-6 months may live a decade. A defendant facing 5-10 years may walk on a technicality.

**The Rule**: Plan for the median, hedge for the tail. The outlier does not change the recommendation — it changes the hedge.

| Approach | Posture | Example |
|:---------|:--------|:--------|
| ❌ Ignore outliers | False precision — presents median as ceiling | "You have 3-6 months." |
| ❌ Overweight outliers | False hope — presents tail as actionable | "But some people live decades, so who knows!" |
| ✅ Acknowledge distribution shape | Plan for median, keep optionality for tail | "Median: 3-6 months. 5-year survival: ~3%. Build strategy around median; don't close every door." |

> **Anti-pattern**: Outlier anecdotes corrupting structural decisions. A patient who rejects palliative care to chase $50K/month experimental treatments because "my cousin's friend beat Stage 4" is treating a semi-deterministic problem as if it were stochastic.

### Step 3.8: Domain Reclassification Over Time

Domains can **shift along the spectrum**. The same activity may have been semi-deterministic a decade ago and stochastic today.

**Example**: Job search.
- **~2000-2015** (Semi-deterministic): Smaller applicant pools, human reviewers, clear signal path. Right qualifications → hired. N=1 was predictable.
- **~2020-2026** (Approaching stochastic): 500+ applicants per listing, ATS keyword filters, AI-generated applications flooding the pipeline, ghost jobs. Signal-to-noise ratio collapsed.

**The Failure Mode**: When a domain reclassifies and the operator still uses the old domain's solving strategy.

Grinding 200 job applications (Sense→Analyze→Respond) in a game that now requires Probe→Sense→Respond — or exiting the game entirely — is the most efficient path to exhaustion. The problem is not effort; the problem is the arena.

> **Diagnostic**: If your hit rate has collapsed despite maintaining or improving your inputs, check whether the domain itself has reclassified. The GTO response may be to change the game (P500 Phase 2, Path C: Lateral/Asymmetric), not to try harder at the old game.

### Step 4: Weight and Reassemble

#### Rule 1: Conviction Weights the Recommendation

Higher-conviction components get more influence on **what to do**. Lower-conviction components get more influence on **how much to risk**.

```
Recommendation = Σ (Sub-answer × Conviction Weight)
```

High-conviction components → decide the ACTION.
Low-conviction components → decide the POSITION SIZE (exposure, hedge, risk budget).

#### Rule 2: Reversibility Override (Law #1)

Any sub-problem flagging irreversible downside gets veto power regardless of conviction:

```
IF any sub-problem has:
  P(ruin) > 5%        → HARD VETO
  Irreversible harm   → HARD VETO
  Reversible downside  → Factor into risk budget, continue
```

### Step 5: Synthesize (Protocol 500 + 330)

Output the unified recommendation using EEV (Protocol 330), not MEV:

> **Action**: [What to do — driven by high-conviction components]
> **Risk Gate**: [Key risk factor — driven by low-conviction components]
> **Veto Check**: [Law #1 status — pass/fail]

---

## Worked Examples

### Example 1: Legal — "Should my client take the plea bargain?"

Defence counsel in a corporate fraud case. Prosecution offers 3 years (with rehab and early release, effectively ~1 year). Going to trial risks up to 10 years if convicted.

| Sub-Problem | Domain | Conviction | Answer |
|:------------|:-------|:-----------|:-------|
| What does the statute say? (max sentence, elements) | Deterministic | 0.95 | Max 10 years. Elements of offense clearly defined. |
| How strong is the prosecution's evidence? | Semi-deterministic | 0.75 | Chain of custody gap in Exhibit D. Exploitable but not dispositive. |
| What do sentencing precedents show? | Semi-deterministic | 0.70 | 68% conviction rate in comparable cases (n=47, SG courts 2020-2025). |
| How will this specific judge interpret the evidence? | Semi-stochastic | 0.35 | Unknown — personality, political climate, judicial temperament. |
| How will this specific jury react to testimony? | Semi-stochastic | 0.30 | 12 humans with unknown biases and emotional responses. |
| Will surprise evidence or witnesses emerge? | Stochastic | 0.10 | Unknowable unknowns. |

**EV Calculation** (deterministic): Plea = 1 year certain. Trial = P(acquittal) × 0 + P(conviction) × E[sentence]. At 68% base rate, E[trial] ≈ 4.2 years.

**Output Calibration**: "Structural analysis favors the plea bargain (1yr vs expected 4.2yr at trial). Evidence gaps in Exhibits D and F are exploitable but insufficient alone for acquittal. **Your courtroom read: does your assessment of this judge/jury shift P(acquittal) above 35%? If yes, trial. If no, plea.**"

**Veto check**: Neither option triggers Law #1 (no irreversible ruin — prison is severe but not permanent). Decision deferred to human with structural framing. ✅

---

### Example 2: Trading — "Should I long EURUSD at 100 pips SL, 5% risk?"

Trader with $5K bankroll. Considering a long EURUSD position with 100-pip stop loss, risking $250 (5%).

| Sub-Problem | Domain | Conviction | Answer |
|:------------|:-------|:-----------|:-------|
| Is 100-pip SL structurally sound? | Semi-deterministic | 0.85 | ATR is 73 pips. 100/73 = 137% coverage. Survives noise. ✅ |
| Is 5% ($250) appropriate risk? | Deterministic | 0.90 | Within One-Third Kelly / campaign risk bounds, within pain threshold. ✅ |
| Should I long EURUSD right now? (direction) | Stochastic | 0.10 | No model reliably predicts direction. |
| Will this specific trade win? | Stochastic | 0.05 | Identical to TOTO at the individual trade level. |

**Output Calibration**: "SL: 100 pips is within the structurally valid band [73-130]. Sizing: $250 at 5% passes Kelly and pain threshold checks. Direction and timing: **zero edge — your call.** Based on your system's 65% WR over 120 trades, ensemble EV is +5.5% — but this is an ensemble property (n=120, regime-dependent, ±3-4% CI). It tells you what to expect over 50+ trades, not this one. **Your read: does the chart confirm your thesis? Y/N.**"

**Veto check**: $250 on a $5K bankroll = 5% risk. Survivable. Law #1 passes. ✅

---

### Example 3: Consumer — "Should I buy this used S24 Ultra at $650?"

| Sub-Problem | Domain | Conviction | Answer |
|------------|--------|-----------|--------|
| Is 66% off retail correct? | Deterministic | 0.95 | Yes — arithmetic verified |
| Will warranty cover dead pixel? | Semi-deterministic | 0.70 | Likely — manufacturing defect precedent favors it |
| Will phone last 3+ years? | Semi-stochastic | 0.50 | Probable — flagship SoC, but battery is wildcard |
| Will a better deal appear? | Stochastic | 0.10 | Unknown — no predictive model |

**Weighted synthesis**: Strong buy. Warranty inspection is the key risk gate. Future pricing is unknowable and therefore not actionable — excluded from decision.

**Veto check**: Max downside = $650 for a phone with a dead pixel. Reversible (resell). Law #1 passes. ✅

---

## Anti-Patterns

- ❌ Treating multi-domain questions as single-domain
- ❌ Averaging conviction across sub-problems
- ❌ Giving stochastic components equal vote to deterministic ones
- ❌ Ignoring the reversibility gate because the weighted sum looks good
- ❌ Stating semi-stochastic estimates without the fragility warning (anchoring risk)
- ❌ Blending sub-problems — letting stochastic uncertainty contaminate deterministic answers

---

## Prior Art

This protocol draws on and extends the **Cynefin framework** (Snowden, 1999), which classifies decision contexts into five domains: clear, complicated, complex, chaotic, and confusion. Cynefin's recognition that domains are not static — and that knowledge-driven "clockwise drift" reclassifies problems from chaotic → complex → complicated → clear — anticipates the "progressive reclassification" concept in §6 by over two decades.

**What P525 adds beyond Cynefin**:

| | Cynefin | Protocol 525 |
|:--|:--------|:-------------|
| **Classifies** | The decision domain | The domain + the **AI output posture** per domain |
| **Specifies** | How humans should sense-make in each domain | How the AI should **talk, package, and defer** per sub-problem |
| **Addresses** | Human decision-making in organisations | Human-AI **division of labour** per sub-problem |
| **Conviction-decisiveness split** | Not addressed | Core contribution (Protocol 524) — independent axes |
| **Compound decomposition** | Implicit | Explicit pipeline: decompose → classify per sub-problem → solve → weight → synthesize |
| **Band width / anchoring risk** | Not addressed | Formal mapping per domain type (§3.6) |

Cynefin tells you *what domain you're in*. Protocol 525 tells the AI *how to behave in that domain*.

---

## Related Protocols

- [Protocol 500: GTO Problem Solver](../decision/DEC-500-gto-problem-solver.md) — Final synthesis engine
- [Protocol 501: Diagnostic Engine](../decision/DEC-501-diagnostic-engine.md) — Decomposition step
- [Protocol 524: Conviction-Decisiveness Split](RSN-524-conviction-decisiveness-split.md) — Per-domain solving
- [Protocol 330: Economic Expected Value](../decision/DEC-330-economic-expected-value.md) — EEV weighting
- Core Identity: Law #1 (Ruin Veto) — Override gate

## References

- Snowden, D.J. & Boone, M.E. (2007). "A Leader's Framework for Decision Making." *Harvard Business Review*, 85(11), 68–76.
- Snowden, D.J. (1999). "Liberating Knowledge." *Caspian Publishing*, London.

