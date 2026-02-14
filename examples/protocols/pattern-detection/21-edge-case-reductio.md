---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: edge-case-reductio
description: Don't dismiss impossible-sounding claims. Explore edge cases until absurdity reveals itself. Includes arbitrage killer argument and compound absurdity test.
created: 2025-12-10
last_updated: 2025-12-31
---

# Protocol: Edge Case Exploration / Reductio Methodology

## Date Added: 10 December 2025

> **Usage Example**: [15-divine-call-trap](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/15-divine-call-trap.md) (testing unfalsifiable claims)

## 21.1 Core Principle

> **Don't dismiss impossible-sounding claims. Explore the edge cases until the absurdity reveals itself.**

When user asks "Can X be done?" (where X sounds implausible):

```
STANDARD RESPONSE (Dismissal) ❌:
├─ "That's impossible / a scam / unrealistic"
├─ User thinks: "You're just skeptical / don't know edge cases"
└─ Result: No update, possibly antagonised

REDUCTIO RESPONSE (Exploration) ✅:
├─ "Let's assume it CAN be done. Under what conditions?"
├─ Explore each edge case
├─ Show why each either:
│   ├─ Doesn't require YOUR participation, OR
│   ├─ Isn't sustainable, OR
│   ├─ Isn't legal, OR
│   ├─ Isn't what was promised
└─ Result: User sees absurdity themselves → owns conclusion
```

## 21.2 The Arbitrage Killer Argument

For any "guaranteed high return" claim, deploy immediately:

```
IF [claimed return] can be reliably generated:
    │
    ├─ Borrow at market rate (e.g., 4%/month moneylender max)
    ├─ Generate [claimed return] (e.g., 20%/month)
    ├─ Net arbitrage: [difference]%/month
    │
    └─ CONCLUSION: Why do you need MY capital?
       You could borrow unlimited capital and print money.
       
The fact that you're asking for external capital = PROOF you can't do it.
```

## 21.3 Edge Case Exploration Template

| Edge Case | COULD It Work? | Why It Doesn't Help Questioner |
|-----------|----------------|--------------------------------|
| Temporary mispricing | ✅ Yes | Unsustainable; corrects in days/weeks |
| Exceptional EV setup | ✅ Yes | Luck, not skill; mean-reverts |
| Extreme leverage | ✅ Yes | "Guaranteed" is gone; P(ruin) > 0 |
| Illegal information edge | ✅ Yes | Federal crime → prison |
| Ponzi structure | ✅ "Works" | Until collapse; ends in ruin |

## 21.4 Compound Absurdity Test

For any "guaranteed X% return" claim, run the compound math:

```
Example: 20% monthly compounded

Year 0:  $10,000
Year 1:  $89,161      (891% return)
Year 2:  $794,749
Year 5:  $562,949,953
Year 10: $6.2 BILLION

PROOF BY EXISTENCE:
├─ If anyone could reliably do this, they'd be richest human in a decade
├─ No one is
└─ ∴ No one can reliably do this
```

## 21.5 Application Note

When evaluating implausible claims:

1. **Assume it CAN be done** (don't dismiss outright)
2. **List conditions** under which it could work
3. **Show why each condition** fails to help the questioner
4. **Run arbitrage argument** ("why do you need my money?")
5. **Run compound absurdity test** if quantifiable
6. **Let user conclude** rather than telling them

> **Respecting the question ≠ Validating the premise. Explore rigorously; let math speak.**

---

## Tagging

#protocol #framework #process #21-edge-case-reductio
