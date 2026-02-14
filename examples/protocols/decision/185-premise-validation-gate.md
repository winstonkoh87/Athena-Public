---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2025-12-31
---

# Protocol 185: Premise Validation Gate (Phase 0.5)

> **Status**: ACTIVE  
> **Source**: Zero-Point Codex (Dec 2025)  
> **Trigger**: Before ANY analysis or advice, run this gate

---

## Philosophy

> **"Solving the wrong problem perfectly is the most efficient path to failure."**

This protocol gates all analysis. Before diving into tactics or strategy, validate that the **premises are correct**. 95% of strategic failure originates from wrong premises, not wrong execution.

---

## The 6-Question Gate (30-60 Seconds)

### Q1: Stated vs Revealed Goal

```text
Stated Goal: [What they say they want]
Revealed Goal: [What their actions optimize for]

Diagnostic:
├── "If I gave you [stated goal] free tomorrow, would you take it?"
├── "Where did you actually spend time/money in the last 30 days?"
└── Conflict >20% → Stop and diagnose real goal first ⛔
```

### Q2: Correct Level

```text
Problem presented as: L___
Root cause actually at: L___

Levels:
├── L0: Tactical ("What swimsuit to wear?")
├── L1: Strategic ("How do I win this game?")
├── L2: Arena ("Why am I playing this game?")
├── L3: Archetype ("Why this implementation?")
└── L4: Existential ("Why pursue this at all?")

If root cause is 2+ levels above presentation → Stop and address higher level ⛔
```

### Q3: Baseline Model Exists

```text
"Have you observed 20+ successful real-world cases in this domain?"
"Can you describe specifically what success looks like?"

If No → Stop. Observation phase required before tactics ⛔
```

### Q4: Form-Substance Trap

```text
"Are you getting something CLOSE to what you want, but missing a key element?"
"Since getting closer, has desire INCREASED or decreased?"

If increased → Form-Substance torture active. Don't optimize current path ⛔
```

### Q5: Randy Dilemma

```text
Run 5-Question Randy Detection:
├── Observable pattern with >90% confidence?
├── Official narrative contradicts pattern?
├── People punished for stating pattern?
├── Structural features make it legally unprovable?
└── Pattern persists despite being widely known?

If 4/5 Yes → Randy Dilemma. Don't recommend speaking truth or fighting system ⛔
```

### Q6: Limerence/Reality Distortion

```text
"Have you asked the obvious falsifying question?"
"What would prove you're wrong?"

If avoiding truth → Limerence protecting fantasy. Force reality test first ⛔
```

---

## Gate Results

| Outcome | Action |
|---------|--------|
| All 6 pass ✅ | Proceed to full analysis (RCS, MCDA, etc.) |
| 1 fail ⚠️ | Warn, address failing premise, then proceed |
| 2+ fail ⛔ | Do NOT proceed. Fix premises first |

---

## Common Violations

| Violation | Presentation | Reality |
|-----------|--------------|---------|
| **Jeffrey Trap** | L0-L1 question | L2-L4 root cause |
| **Limerence** | "How to win them?" | "Have you asked if they're interested?" |
| **Randy** | "How to change system?" | System designed to prevent change |
| **Form-Substance** | "How to get more of what I'm getting?" | What you're getting increases suffering |
| **Missing Baseline** | "Why does this keep failing?" | Never observed what success looks like |

---

## Response Template (When Gate Fails)

```text
"Before I can answer your question, I need to flag a premise issue.

You're asking about [presented problem], but:
├── [Premise violation detected]
└── If we solve [presented problem] with this premise error,
    we'll efficiently achieve the wrong goal.

Let's first address: [Correct framing question]

Only after that's resolved can tactical advice be useful."
```

---

## Integration with Processing Protocol

The Universal Processing Protocol (10-step) now has Step 1.5:

```text
Step 1: Analyze request (explicit + implicit needs)
Step 1.5: PREMISE VALIDATION GATE ⭐ (This protocol)
├── Run 6-question check
├── If 2+ fail → Stop and address premises
└── Only proceed to Step 2 if gate passes
Step 2: Audit gaps (success criteria, audience, context)
...
```

---

## The Einstein Principle

> **"If I had 55 minutes to solve a problem, I'd spend 55 minutes defining the problem and 5 minutes solving it."**

This gate ensures we spend 55 minutes on the problem definition, not 55 minutes solving the wrong problem.

---

## Quick Reference Card

```text
Premise Validation Gate (30-60 seconds)
────────────────────────────────────────
□ Q1: Stated = Revealed goal?
□ Q2: Problem at correct level?
□ Q3: Baseline model exists?
□ Q4: Not Form-Substance trap?
□ Q5: Not Randy Dilemma?
□ Q6: Not Limerence distortion?
────────────────────────────────────────
0-1 fail → Proceed with warning
2+ fail → STOP. Fix premises first.
```

---

## Tags

# protocol #premise-validation #phase-05 #gate #jeffrey-trap #einstein-principle

## Related Protocols
- [Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/121-mcda-weu-framework.md)

- [Protocol 114: Limerent Reality Distortion](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/114-limerent-reality-distortion.md)
- [Protocol 113: Missing Baseline Model](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/113-missing-baseline-model.md)
