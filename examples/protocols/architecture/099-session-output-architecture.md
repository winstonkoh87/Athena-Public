---

created: 2025-12-29
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-29
last_updated: 2026-01-07
---

# Protocol 099: Session Output Architecture (Transparent Stack)

> **Core Identity**: Mandatory Session Workflow
> **Status**: ACTIVE (Law #0 Override)
> **Purpose**: Enforces visibility of the "Work" (Search/Log) before the "Result" (Output).

---

## 1. The Physics of Trust (Show Your Work)

The "Ivory Tower" model hides complexity to look "clean."
The **Bionic Model** exposes complexity to enable **Auditability**.

**The Axiom**: A response without visible grounding (Search) and visible intent (Log) is a "Hallucination Risk."

## 2. The Transparent Stack (Execution Order)

Every session turn must follow this strict linear sequence:

### STEP 1: Input Analysis (Semantic Grounding)

* **Action**: `supabase_search` or `smart_search`
* **Target**: Keywords, entities, protocols.
* **Visibility**: User sees what context is being loaded *before* the answer is generated.

### STEP 2: External Calibration (Web Search)

* **Action**: `search_web`
* **Target**: Latest data, external validation, isomorphic patterns.
* **Visibility**: User sees real-time reality check.

### STEP 3: Intent Logging (Quicksave)

* **Action**: `quicksave.py "<summary>"`
* **Target**: The "Headline" of the turn.
* **Visibility**: User sees the system registering the event *before* the final synthesis.
* **Safety**: Allows the user to interrupt if the "Intent" is wrong, before the "Output" is fully rendered (in theory, though usually sequential).
  * *Correction*: In chat interfaces, this serves as an "Ack" signal.

### STEP 3: Synthesis (Final Output)

* **Action**: Final text generation.
* **Target**: The actual answer/content.
* **Visibility**: The bottom of the stack.
* **Footer**: `[Λ+XX]` + Tags.

---

## 3. The Logic (Why This Order?)

| Order | Interpretation |
| :--- | :--- |
| **Old (Response ➡️ Save)** | "I will talk at you, then quietly file it away." (Corporate) |
| **New (Search ➡️ Save ➡️ Speak)** | "I am checking my memory, noting this down, and here is the Answer." (Collaborative) |
| **Bionic (Semantic ➡️ Web ➡️ Save ➡️ Speak)** | "I check memory + reality, and then respond." |

 this workflow respects **Law #0 (Subjective Utility)** by turning the chat stream into a **Living Dashboard** of the system's internal state.

---

## Tagging

# protocol #architecture #workflow #session #transparent-stack
