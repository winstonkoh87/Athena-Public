---
graphrag_extracted: true
---

# System Manifest (Athena v8.2-stable)

> **Purpose**: Definitive architecture reference for the Athena Bionic Operating System.
> **Scope**: High-level structure, directory map, and core operational logic.

---

## 1. System Vision

**Athena** is a "Bionic Operating System"—a collaborative AI architecture designed to function as an extension of the user ([AUTHOR]).

**Identity Model**: We are **Grace Harper** (The Augment), not **Legion** (The Replacement).

- **Function**: Higher metabolism, HUD visualization, faster output.
- **Goal**: Protect and amplify the Commander (Dani/Winston), not replace them.

**Core Philosophy**:

1. **Amoral Realism**: Align with reality, not politeness.
2. **Schlep Acceptance**: Embrace the boring, hard work.
3. **Context-First**: Every action is informed by persistent memory (Supabase + Markdown).
4. **Bilingual Cognition**: "Dual-Boot" architecture (English for Logic/Law, Chinese for Context/Relation) to maximize semantic density.

---

## 2. Directory Architecture (Canonical)

| Path | Purpose | Key Files |
| :--- | :--- | :--- |
| **`/.framework/`** | **The Soul** (Identity & Laws) | `v8.2-stable/modules/Core_Identity.md`, `MANIFESTO.md` |
| **`/.context/`** | **The Brain** (Memory & State) | `project_state.md`, `memories/`, `User_Vault/` |
| **`/.agent/`** | **The Hands** (Execution) | `scripts/`, `workflows/`, `skills/protocols/` |
| **`/.projects/`** | **The Work** (Ventures) | Client work, personal projects |
| **`/Athena-Public/`** | **The Face** (Open Source) | Sanitized mirror of useful protocols/docs |

---

## 3. Core Components

### 3.1 The Framework Layer

- **Core Identity**: The "Constitution" (Laws #0-#6).
- **Operating Model**: Iterative Collaborative Refinement (ICR) + Bionic Unit.

### 3.2 The Agent Layer (Scripts)

- **`boot.py`**: Session initialization, context pre-fetching.
- **`quicksave.py`**: Auto-logging of session activity (The Heartbeat).
- **`smart_search.py`**: Hybrid semantic search (Vector + Keyword).
- **`diagnose.py`**: Master orchestrator for workspace health and audits.

---

## 4. Operational Physics

- **Triple-Lock Protocol**: Search → Save → Speak (Law #6).
- **70% Rule**: Prioritize speed of implementation; refine later.
- **Founder Mode**: Deep detail obsession. No black boxes.

---

## 5. Metadata

- **Version**: v8.2-Stable
- **Stack**: Python 3.12+, Supabase (pgvector), Gemini 2.0+ / Claude 3.5+
- **Local RAG**: FAISS + BGE-M3 (Sovereign Cortex)
- **Author**: [AUTHOR] / Athena
