---
created: 2026-01-30
last_updated: 2026-01-30
graphrag_extracted: true
---

---title: "Protocol 105: The Agentic SDLC (The Sandwich Model)"
type: "process"
tags: ["agentic", "workflow", "sdlc", "qoder", "spec-driven-development"]
created: 2026-01-30
source: "Session 06 / Qoder AMA"
last_updated: 2026-01-30
---

# Protocol 105: The Agentic SDLC (The Sandwich Model)

> **Core Philosophy**: "The Code is Temporary. The Spec is the Product."

## 1. The Paradigm Shift

The economic value of "writing syntax" (Phase 2) has collapsed to near-zero. The value of **Definition** (Phase 1) and **Verification** (Phase 3) has skyrocketed.

### The "Sandwich" Workflow

We operate on a **50/20/50** effort split (derived from Qoder Team empirical data):

| Phase | Activity | Owner | Effort | Nature of Work |
| :--- | :--- | :--- | :--- | :--- |
| **1. Spec** | **Architecting** | **Global Main (User)** | **50%** | **High Focus**. Defining constraints, edge cases, and "Done" state. |
| **2. Execution** | **Coding** | Agent (Autonomous) | 10% | **Low Touch**. The "Schlep" (boilerplate, syntax, glue). **DO NOT INTERRUPT.** |
| **3. Verify** | **Auditing** | **Global Main (User)** | **40%** | **High Grind**. Verifying *logic* and *flow* (not syntax). Finding silent failures. |

---

## 2. The New Roles

### 2.1 The Architect (Phase 1)

* **Old Job**: Translator (Thoughts → Python).
* **New Job**: Architect (Thoughts → Spec).
* **The Golden Rule**: "Ambiguity is the enemy." If the spec is vague, the agent *will* hallucinate complexity or choose the lazy path.
* **Artifact**: The `Spec Sheet` is now the **Source Code**. The actual `.py` files are just compiled artifacts of the Spec.

### 2.2 The Silent Engine (Phase 2)

* **The "No Interruption" Rule**: Do not interrupt the agent during execution.
  * **Context Fragility**: Interruptions force expensive context switches.
  * **Velocity**: The agent writes faster than you can read.
  * **The Schlep**: Let the agent handle the boring "glue code."

### 2.3 The Auditor (Phase 3)

* **The Trap**: "It runs, so it works." (False).
* **The Reality**: Agents write perfect syntax but can make **Semantic Errors** (logic gaps, security holes, unhandled edge cases).
* **Action**: Move from "Code Review" (checking style) to "Logic Audit" (checking outcomes). Verify the *flow*, not just the *function*.

---

## 3. The "Golden Spec" Template

To ensure Phase 2 runs autonomously, the Spec must contain:

1. **Context**: The "Vibe" and Role (e.g., "Senior React Engineer").
2. **The "One Job"**: Strict Scope Definition (e.g., "Implement Login ONLY").
3. **Constraints (The "No" List)**: explicit prohibitions (e.g., "No raw CSS, use Tailwind").
4. **Acceptance Criteria**: The binary "Definition of Done".

---

> **Tags**: #workflow #agentic #sdlc #architecture
