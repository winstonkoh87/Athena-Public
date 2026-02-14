---
created: 2025-12-14
last_updated: 2026-01-30
graphrag_extracted: true
---

---description: Iterative self-referential development loop. "Siege" a problem until solved, rather than "Try once and quit". Inspired by 'ralph-wiggum' plugin.
tags: [#protocol, #iteration, #loop, #sieging, #ralph-wiggum]
created: 2025-12-14
last_updated: 2026-01-06
---

# Protocol 69: Iterative Siege (Ralph Loop)

> **Purpose**: Industrialized problem solving. "Siege" the problem until a condition is met.
> **Trigger**: Complex coding tasks, debugging recalcitrant errors, or multi-step logic puzzles.
> **Source**: Session 41 (2025-12-14) — Inspired by `ralph-wiggum` Claude plugin.

---

## 1. The Core Concept

Most AIs are "One-Shot" engines. They try, fail, and apologize.
**The Siege Engine** does not apologize. It reloads.

**The Loop**:

1. **Attempt**: Execute plan.
2. **Verify**: Check result (Lint, Test, Error Log).
3. **Refine**: If fail, modify plan based on error.
4. **Repeat**: GOTO 1 until `Success` OR `Max_Retries`.

---

## 2. Application: The "Siege" Workflow

When a task is marked `[SIEGE]`:

1. **Define Success Condition**: (e.g., "Build passes with 0 errors" or "Test suite turns green").
2. **Set Retry Budget**: (e.g., "Max 5 attempts").
3. **Execute Loop**:

```text
WHILE (Current_State != Success_Condition) AND (Attempts < Max_Retries):
    1. Analyze Current_State
    2. Identify Blockers
    3. Formulate Hypothesis
    4. Execute Fix
    5. Update Current_State
    6. Increment Attempts
```

4. **Exit Strategy**:
    * **Success**: Report victory + method.
    * **Failure**: Report "Siege Broken" + summary of failed hypotheses (to save user time).

---

## 3. When to Use (Trigger)

* **Debugging**: "Fix this error." (Don't ask me how, just cycle until it's gone).
* **Refactoring**: "Migrate this file to FSD." (Cycle until linter is happy).
* **Research**: "Find the answer." (Dig until not empty).

---

## 4. The "Smart Siege" (Optimization)

A "Dumb Siege" repeats the same mistake.
A "Smart Siege" uses **Gradient Descent**:

* Attempt 1: Standard Fix.
* Attempt 2: Alternative Library.
* Attempt 3: Monkey Patch / Brute Force.
* Attempt 4: Radical Simplification (Delete feature).

**Rule**: Each iteration must change the *Approach*, not just the *Syntax*.

---

## References

* [Protocol 54: Cyborg Methodology](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/54-cyborg-methodology.md) — The parent philosophy
* [Claude Code 'ralph-wiggum'](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) — The inspiration

---

## Tagging

#protocol #framework #69-iterative-siege
