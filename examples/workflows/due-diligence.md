---created: 2025-12-24
last_updated: 2026-01-30
---

---description: Real-world due diligence workflow — structured analysis for investment decisions
created: 2025-12-24
last_updated: 2025-12-24
---

# /due-diligence — Execution Script

> **Alias for**: Investment/Business evaluation mode  
> **When to use**: Friend asks for money, startup pitch, "silent partner" offer, franchise opportunity

---

## Behavior

When `/due-diligence` or `/dd` is invoked, activate structured analysis mode:

> [!IMPORTANT]
> **KILL SWITCH FIRST**: Before financials, check for regulatory/structural deal-breakers that make the investment impossible regardless of returns.

> [!IMPORTANT]  
> **CROSS-MODEL VALIDATION**: For any deal >$10K, submit draft analysis to 3+ SOTA models for blind review before finalizing.

---

## Phase 0: Kill Switch Check (5 min)

// turbo

Before ANY financial modeling:

- [ ] What regulatory constraints apply? (Licenses, permits, subletting rules)
- [ ] Can this be legally structured as proposed?
- [ ] What happens if the operator walks away? (Collateral check)
- [ ] Is the exit mechanism defined?

**If Kill Switch Found**: Stop. Report the structural deal-breaker. Financials are irrelevant.

---

## Phase 1: Framework Cascade (15 min)

// turbo

Apply all relevant frameworks:

- [ ] **PESTLE**: Macro environment scan (Political, Economic, Social, Tech, Legal, Environmental)
- [ ] **Five Forces**: Industry attractiveness (Rivalry, Buyers, Suppliers, Entrants, Substitutes)
- [ ] **SWOT**: Internal strengths/weaknesses, external opportunities/threats
- [ ] **Funding Source Ladder**: Why is THEIR capital source significant?

---

## Phase 2: Financial Model (15 min)

// turbo

Build 3-scenario model:

- [ ] **Worst Case**: Conservative assumptions, high cost, low revenue
- [ ] **Realistic Case**: Industry benchmarks, median outcomes
- [ ] **Best Case**: Optimistic but plausible assumptions

For each scenario:

- Monthly P&L (Revenue, COGS, OpEx, Net Profit)
- 3-Year Return on Investment
- Probability-Weighted Expected Value (EV)

**EV Formula**:

```
EV = Σ (Probability × 3-Year Return) - Initial Investment
```

---

## Phase 3: Human-AI Discussion (10 min)

Prompt the user for:

- [ ] What data am I missing?
- [ ] Are my assumptions realistic based on YOUR knowledge?
- [ ] What's the operator's experience level?
- [ ] What's your risk tolerance?

Recalibrate model based on feedback.

---

## Phase 4: Cross-Model Peer Review (15 min)

// turbo

Submit draft analysis to LMArena or direct API calls:

- [ ] Gemini-3-Pro: Check numerical consistency
- [ ] Claude-3.5-Sonnet: Check for actionability gaps
- [ ] Perplexity-Sonar: Check for regulatory nuances
- [ ] GPT-4o: Check for framing/bias issues

Integrate non-redundant feedback.

---

## Phase 5: Final Synthesis (10 min)

Produce final report with:

1. **Executive Summary** (1 page max)
2. **Recommendation** (Clear: INVEST / DO NOT INVEST / CONDITIONAL)
3. **Term Sheet** (If proceeding, structure the deal properly)
4. **DD Checklist** (What to verify before signing)

---

## Output Structure

```markdown
# Investment Due Diligence Report

## Executive Summary
- Deal Terms
- Key Findings (Traffic Light: 🔴🟡🟢)
- Recommendation

## Regulatory Feasibility (Kill Switch Check)
## PESTLE Analysis
## Five Forces
## SWOT
## Financial Projections (3 Scenarios + EV)
## Risk Assessment
## Recommendation
## Term Sheet (If Proceeding)
## DD Checklist

## Appendix: References
## Appendix: Methodology
```

---

## Quick Reference: Red Flags

| Signal | Implication |
|--------|-------------|
| Approaching friends, not banks | Institutional rejection likely |
| No personal capital at risk | Zero skin in game |
| Undefined exit mechanism | No liquidity |
| "Trust me" instead of POS data | Governance risk |
| Operator has no industry experience | Expensive learning curve on YOUR money |

---

## Example

```text
User: /due-diligence My friend wants me to invest $30K in his bubble tea franchise.

AI:
[Phase 0: Kill Switch Check]
→ Is this a legitimate franchise or rebranded self-start?
→ What are the franchise fee terms?
→ Who holds the lease?

[Phase 1: Framework Cascade]
→ PESTLE: Bubble tea market saturation, GST impact, labor costs
→ Five Forces: High rivalry, low switching cost, high substitutes

[Phase 2: Financial Model]
→ 3 scenarios, EV calculation

[Phase 3: Human-AI Discussion]
→ "What's the franchise royalty rate?"

[Phase 4: Cross-Model Review]
→ Submit to peers, integrate feedback

[Phase 5: Final Report]
→ Structured output with recommendation
```

---

## Tagging

# workflow #automation #due-diligence #investment #dd
