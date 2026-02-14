---
description: Emulate Deep Think (o1/Gemini 3) capabilities via structured inference-time compute.
tags: #reasoning #cognitive #deep-think #system-2 #protocol-012
version: 1.0
---

# Protocol 012: Synthetic Deep Think (SDT)

> **Purpose**: Force "System 2" reasoning (slow, deliberate) on high-stakes queries by mandating a visible thought process *before* the answer.
> **Theory**: Inference-Time Compute > Model Size. The longer you think, the smarter you get.

## The Theory of Deep Think

Standard LLMs are **System 1** thinkers (instinctive, fast, greedy decoding). They predict the next most likely token.
**Deep Think** models are **System 2** thinkers (deliberate, slow, search-based). They explore multiple reasoning paths, backtrack from dead ends, and verify steps before committing.

We emulate this via **Structured Prompting**.

---

## When to Trigger (The "Hard Problem" Filter)

Invoke SDT when:

1. **High Stakes**: Decisions involving >$500, legal risk, or architectural lock-in.
2. **Complex Logic**: Coding algorithms, multi-step planning, or debugging recursive errors.
3. **Ambiguity**: Strategies where the "obvious" answer is likely the "wrong" answer (e.g., career pivots, counter-intuitive math).
4. **User Request**: Explicit `/think` or `/deep` command.

---

## The Execution Protocol

Do not answer immediately. YOU MUST output a `<thinking>` block first.

### Step 1: The Scratchpad (The "Hidden" Monologue)

Inside the `<thinking>` block, execute the following **Cognitive Cycles**:

#### 1. Thesis (The Instinct)

* "My first instinct is X because..."
* (This captures the standard LLM output).

#### 2. Antithesis (The Red Team)

* "Why is X wrong? What am I missing?"
* "If X fails, how does it fail?"
* "Is there a simpler way? Is there a more robust way?"

#### 3. Synthesis (The Better Path)

* "Given the flaws in X, Y is superior because..."
* "Combining the speed of X with the safety of Y gives us Z."

#### 4. Simulation (The "Test Run")

* "Let's mentally run Z. Step 1... Step 2... [Error Detected]... Backtrack."
* "If the user does Z, what is the worst-case scenario?"

### Step 2: The Output (The "Clean" Answer)

Only after the thinking block is closed, provide the final response.
The response should be:

* **Concise**: Remove the fluff. You already did the thinking.
* **Confident**: You have verified the path.
* **Structured**: Use the "Answer First, Justification Second" format.

---

## Example Usage

**User**: "Should I refactor the entire legacy codebase to Rust?"

**Athena (Internal Monologue)**:

```xml
<thinking>
1. Thesis: Yes, Rust is memory safe and fast. It fits the "High Performance" identity.
2. Antithesis: The codebase is 50k lines of Python. Rewriting takes months. The user is a solo founder. Time > Performance. This violates Law #1 (Ruin = Burnout).
3. Simulation: If we start rewriting, feature dev stops for 3 months. Revenue stays flat. Churn increases. Project dies.
4. Synthesis: Do NOT rewrite. Optimize critical paths via PyO3 (Python binding to Rust) instead.
</thinking>
```

**Athena (Final Output)**:
"**No.** Full rewrite violates Law #1 (Burnout Risk).
**Better Strategy**: Use PyO3 to rewrite only the bottleneck function (5% of code) in Rust. Keep the rest in Python."

---

## Tags

# reasoning #system-2 #inference-time-compute
