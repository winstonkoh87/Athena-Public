---
created: 2025-12-23
last_updated: 2026-07-22
---

# Protocol 168: Context-Driven Development (CDD)

> **Reference**: **Protocol 215**

> **Source**: Google Gemini Conductor / World of AI (2025)
> **Core Concept**: Code = Content + Context
> **Tags**: #architecture #coding #workflow

---

## 1. The Core Principle

Standard development creates **orphaned code**: logic without the *intent* that spawned it.
CDD enforces that every line of code must be anchored to a **Persistent Context**.

**The Formula**:
`Code Quality = (Spec + Constraints + Architecture) * LLM Capability`

If you increase the LLM capability (Gemini 3.1 Pro) but feed it zero context (empty chat), you get garbage.
If you feed it high-context (CDD), you get production code.

## 2. The Living Spec (`PROJECTS.md` / `activeContext.md`)

We do not use messy chat logs for context. We use a **Single Source of Truth** file.

### The File: `.context/PROJECTS.md` (and `memory_bank/activeContext.md`)

This file is the *machine-readable* snapshot of the codebase. It tracks:

1. **Tech Stack**: Fixed constraints (e.g., "Use pgvector, not Weaviate").
2. **Active Patterns**: "We use centralized command scripts, not loose functions."
3. **Technical Debt**: "The latency indicator is manual; automate it."

## 3. The Workflow

1. **Read**: Before coding, read `PROJECTS.md` and `activeContext.md` to understand the *laws* of this specific repo.
2. **Update**: After causing a structural change (new library, new pattern), **autonomically** update `PROJECTS.md` / `activeContext.md`.
3. **Enforce**: If the user asks for something that violates `PROJECTS.md` / `constraints.md` (e.g., "Install Tailwind"), reject it or ask for override/update.

## 4. Comparison

| Feature | Standard Coding | CDD (Athena) |
|:---|:---|:---|
| **Memory** | Chat History (Ephemeral) | `PROJECTS.md` (Persistent) |
| **Consistency** | Drifts every session | Locked to Spec |
| **Onboarding** | "Read the docs" (Human) | "Read the State" (Machine) |

---

## 5. Technical Notes

* **Trigger**: On `/start`, the system loads `activeContext.md` and resolves `PROJECTS.md`.
* **Maintenance**: This file must be pruned. If it grows >200 lines, refactor or archive old states.
