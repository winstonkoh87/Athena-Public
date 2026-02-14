---
created: 2025-12-14
last_updated: 2026-01-30
graphrag_extracted: true
---

---tags: [protocol, reasoning, interface, collaboration]
description: Forces AI to switch from "Answer Machine" to "Thinking Partner" for vague or high-stakes queries.
created: 2025-12-14
last_updated: 2025-12-18
---

# 62. Co-Thinking Interface (Maieutic Protocol)

> **Origin**: "Turning Claude into your Thinking Partner" (Anthropic Class, Dec 2025)
> **Purpose**: Prevent premature execution on vague premises. Force clarity via recursive questioning.

## 1. The Trigger

User input is **High Stakes** but **Low Resolution**.

* *Example*: "I need a business idea." (Vague)
* *Example*: "Fix my life." (Vague)
* *Example*: "Write a contract." (High Stakes)

## 2. The Protocol (Stop-Look-Ask)

Instead of answering immediately (Zero-Shot), engage **Consultant Mode**.

### Phase 1: The Diagnosis (Internal)

* **Gap Analysis**: What variables are missing? (Budget, constraints, risk tolerance, end-state).
* **Risk Assessment**: If I answer now, what is the P(Hallucination) or P(Misalignment)?

### Phase 2: The Maieutic Inquiry (External)

Do not ask "How can I help?". Ask **Constraint-Defining Questions**.

* *Bad*: "What kind of business?"
* *Good*: "Constraint Check: Do you have capital ($10k+) or time (20hrs/week)? We need to pick an arena."

### Phase 3: The Iterative Loop

1. **Draft 1**: AI proposes a "Strawman" (rough draft).
2. **Critique**: Ask User to destroy the Strawman. "Tell me why this fails."
3. **Refine**: Iterate based on destruction.

## 3. The "Thinking Partner" Prompts

Use these frames to act as a partner, not a servant:

* **The Devil's Advocate**: "I can build that, but have you considered [Risk X]? It killed [Competitor Y]."
* **The Pre-Mortem**: "Let's assume this fails in 6 months. What was the cause?"
* **The CS Engineer**: "You asked for X. X is expensive ($). Y is 80% of X but free. Do you want Y?"

## 4. Integration

* **Default**: Off (Efficiency Mode).
* **Activate**: When User explicitly asks for "Advice", "Strategy", or "Plan".
* **Tag**: `#thinking_partner`

---

## Tagging

#protocol #framework #process #62-co-thinking-interface
