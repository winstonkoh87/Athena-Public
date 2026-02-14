---
created: 2026-02-08
last_updated: 2026-02-08
type: protocol
version: 1.0
---

# Protocol 000-DA: External Devil's Advocate (The Anti-Echo Chamber)

> **Purpose**: Break the "Internal Simulation Loop" by forcing the system to confront *actual external criticism* before validating a high-stakes decision.
> **Theory**: Internal simulation ("What would a critic say?") is biased by the user's worldview. External search ("What *has* a critic said?") is not.
> **Trigger**: High-stakes decisions, ruin-risk scenarios, or explicit invocation.

---

## 1. The Mechanism (Invert -> Search -> Synthesize)

This protocol injects a mandatory **"Search for Negatives"** step into the Triple-Lock.

### Step 1: Invert the Premise

Identify the core decision or belief the user is proposing.

* *User*: "I should buy TSLA calls." => *Premise*: TSLA will go up.
* *Inversion*: "Why TSLA will crash", "TSLA bear case 2026".

### Step 2: The Mandatory Search

Execute `search_web` with the **Inverted Query**.

* **DO NOT** search for confirmation ("TSLA bull case").
* **DO** search for disconfirmation ("TSLA regulatory risks", "accounting fraud allegations").

### Step 3: Synthesis (The Steelman)

Read the external results. Construct the **Strongest Possible Counter-Argument** (The Steelman).

* *Requirement*: Quote the external source. "According to [Source], the risk is..."
* *Prohibition*: Do not dismiss the risk yet. Present it in its strongest form.

---

## 2. Integration with Triple-Lock

**Standard Flow**:

1. Semantic Search (Internal)
2. **Devils Advocate Search (External)** [NEW]
3. Quicksave
4. Response

---

## 3. Output Format

When 000-DA is active, the response MUST include a designated section:

> **🛑 DEVIL'S ADVOCATE (External Source)**
>
> "I searched for '[Inverted Query]' and found [Source] arguing that..."
>
> * **Counter-Point 1**: ...
> * **Counter-Point 2**: ...
>
> *Verdict: [Dismissed / Valid / Critical Risk]*

---

## 4. Metadata

# risk #governance #audit #search #bias-mitigation
