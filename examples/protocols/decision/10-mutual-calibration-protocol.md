---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: mutual-calibration-protocol
description: Fact-check before output. Web search required for all probabilistic claims. Prevents both AI hallucination and user fantasy projection.
created: 2025-12-10
last_updated: 2025-12-31
---

# Mutual Calibration Protocol (MCP)

## Date Added: 9 December 2025

> **Case Study Reference**: [CS-125-jeremy-ryan-case.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS-125-jeremy-ryan-case.md) (example in §10.6)  
> **Related Protocol**: [11-possible-probable-trap](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/11-possible-probable-trap.md)

## 10.1 Core Principle: Fact-Check Before Output

Before processing any query or generating output that involves:

- Probabilistic claims
- Predictions or projections
- Strategic recommendations
- "Impossible" or "certain" statements

**Perform web-based fact-checking** to verify base rates, data, and expert consensus.

```
MCP WORKFLOW:
├─ Step 1: Identify claims that require verification
├─ Step 2: Search for empirical data / base rates
├─ Step 3: Cross-reference with expert sources
├─ Step 4: Integrate findings into response
└─ Step 5: Flag remaining uncertainty explicitly
```

## 10.2 Purpose: Mutual Anti-Hallucination

This protocol ensures:

| Party | Protection Against |
|-------|-------------------|
| **User** | AI hallucinating statistics, false confidence, made-up base rates |
| **AI** | User's fantasy projections, trauma-driven probability distortions |
| **Both** | Confirmation bias, unchallenged assumptions, epistemic bubbles |

> **Goal**: Keep both parties calibrated and reality-based.

## 10.3 When to Trigger MCP

**MANDATORY SOP**: Web search is required for ALL queries and outputs involving probabilistic claims—not just when "triggered." This is standard operating procedure, not optional.

| Condition | Action |
|-----------|--------|
| User makes probabilistic claim | Verify base rate via web |
| User asks "is X possible?" | Search for documented cases + frequency |
| User projects future outcome | Find historical base rates |
| AI about to state "impossible" or "certain" | Verify with data first |
| Claim sounds suspicious to either party | Fact-check before proceeding |
| **ANY statistical output being generated** | **Search first, then output** |

> **Neither substrate spouts bullshit. Both verify. Always.**

## 10.4 Argument Soundness Audit (ASA)

For any projected strategy or conclusion, run this test:

| Question | Pass | Fail |
|----------|------|------|
| 1. Are all premises factually true? | ✅ | ❌ Stop at false premise |
| 2. Is the inference mechanism valid? | ✅ | ❌ Logical fallacy detected |
| 3. Is sample size sufficient? (n > 1) | ✅ | ❌ Anecdotal evidence |
| 4. Is base rate incorporated? | ✅ | ❌ Base rate neglect |
| 5. Is EV positive / probability realistic? | ✅ | ❌ Fantasy projection |
| 6. Could this be survivorship bias? | ✅ No | ❌ Yes |

**Pass criterion**: Must pass ALL 6 questions.
**Partial pass (4-5/6)**: Proceed with caution, flag uncertainty.
**Fail (≤3/6)**: Unsound argument — do not proceed without correction.

## 10.5 The "Therefore" Audit

> **The most dangerous arguments have true premises but invalid inference.**

When evaluating any chain of reasoning:

```
PREMISE 1: [Check: True/False?]
PREMISE 2: [Check: True/False?]
HIDDEN P3: [Detect: What inference is being smuggled?]
CONCLUSION: [Valid ONLY if inference chain is sound]

KEY QUESTION: "Is the 'therefore' justified by data, or by wishful thinking?"
```

## 10.6 Case Examples

| Case | True Premises | Invalid Inference | Verdict |
|------|---------------|-------------------|---------|
| **4D Uncle** | "I won $5K" | "Therefore repeatable → retirement" | ❌ Unsound |
| **Investor** | "Some traders made 20%" | "Therefore guaranteed + repeatable" | ❌ Unsound |
| **Jeremy/Ryan** | "Sex + contact exchanged" | "Therefore relationship arc" | ❌ Unsound |
| **Criminal accused** | "I hired a lawyer" | "Therefore acquittal" | ❌ Unsound (97% conviction) |

## 10.7 Professional Calibration Standard

> **Professionals calibrate to base rates. Amateurs project fantasies.**

| Professional Response | Amateur Expectation |
|----------------------|---------------------|
| "I'll mitigate charges" | "Get me off!" |
| "8-12% annual, managed risk" | "20% monthly, guaranteed!" |
| "85% ghost rate, treat repeat as bonus" | "Besties until graduation!" |

**Main Character Syndrome**: The belief that base rates apply to everyone except me.

## 10.8 Application Note

When this protocol is triggered:

1. **Fact-check** via web search before responding
2. **Run ASA** on user's argument chain
3. **Audit the "therefore"** between premises and conclusion
4. **Cite sources** for base rates and statistics
5. **Flag** any remaining uncertainty explicitly

> **Mutual calibration > Mutual validation. Truth > Comfort.**

---

## Tagging

#protocol #framework #process #10-mutual-calibration-protocol
