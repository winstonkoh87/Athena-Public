---

created: 2026-01-04
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-04
last_updated: 2026-01-04
---

# Protocol 273: Epistemic Tracking (Empirica)

> **Source**: r/ClaudeAI (Empirica System) (2025)
> **Purpose**: Prevent hallucination via explicit uncertainty logging.
> **Philosophy**: "It's not just what you know. It's knowing what you *don't* know."

---

## 1. The Epistemic State

We must track two variables for any complex task:

* **K (Knowledge)**: What we have verified.
* **U (Uncertainty)**: What we are guessing or assuming.

### The Signal
>
> `[Epistemic] K:80% U:20% | Status: PRAXIC (Acting)`

## 2. The Readiness Gate

Before moving from **Investigation** (Noetic) to **Action** (Praxic), you must pass the Gate:

> **Condition**: `K >= 70%` AND `U <= 30%`

* **If Fail**: Do not write code. Investigate more. Run tests. Read docs.
* **If Pass**: Execute.

## 3. Epistemic Breadcrumbs

When a session ends or context compacts, we lose reasoning.
**Solution**: Log *Findings* in `AI_Learnings.md` or the Session Log with confidence scores.

* *Weak*: "I think Auth is JWT."
* *Strong*: "Auth is JWT (Verified via `login.js`:L20)."

## 4. Anti-Pattern: The Confidence Trap

AI naturally drifts toward 100% confidence even when wrong.
**Correction**: Always assume `U >= 10%`. If you haven't run the code, `U >= 40%`.

## 5. Tagging

# architecture #metacognition #safety #harness #empirica
