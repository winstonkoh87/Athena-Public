---
created: 2026-01-02
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: methodology-alignment
description: Maps BMAD's 4-Phase methodology (Analysis, Planning, Solutioning, Implementation) to Athena's 3-Phase task modes (PLANNING, EXECUTION, VERIFICATION).
tags: [methodology, process, bmad, workflow]
created: 2026-01-02
last_updated: 2026-01-02
---

# Protocol 332: Methodology Alignment

> **Source**: BMAD-METHOD v6 Integration. Integrated 02 January 2026.  
> **Purpose**: Bridge external 4-phase methodologies with Athena's native 3-phase operating modes.

---

## Phase Mapping Matrix

Athena uses 3 atomic modes (`task_boundary`), while BMAD uses 4 lifecycle phases.

| Athena Mode | BMAD Phase | Focus |
|-------------|------------|-------|
| **PLANNING** | **1. Analysis** | Problem definition, research, requirements. |
| **PLANNING** | **2. Planning** | PRD, specs, creating tickets/tasks. |
| **PLANNING** | **3. Solutioning** | Architecture design, component breakdown. |
| **EXECUTION** | **4. Implementation** | Coding, testing, "story-driven development". |
| **VERIFICATION** | **(Validation)** | Explicit QA, walkthrough creation, audit. |

---

## Detailed Definitions

### 1. Analysis (Athena: PLANNING)

- **Goal**: Understand the *What* and *Why*.
- **Tools**: `/search`, `/research`, `read_url_content`.
- **Output**: Problem Statement, User Stories.

### 2. Planning (Athena: PLANNING)

- **Goal**: Define the *How* (Process).
- **Artifacts**: `task.md`, `implementation_plan.md`.
- **Activities**: Breaking down work, sequencing.

### 3. Solutioning (Athena: PLANNING/EXECUTION Transition)

- **Goal**: Design the *Structure*.
- **Activities**: Schema design, API contracts, system diagrams.
- **Output**: Protocol selection, architecture diagrams.

### 4. Implementation (Athena: EXECUTION)

- **Goal**: Build the *Thing*.
- **Activities**: Coding, debugging, unit testing.
- **Artifacts**: Code files, tests.

### 5. Verification (Athena: VERIFICATION)

- **Goal**: Prove it *Works*.
- **Activities**: `orphan_detector.py`, `pytest`, Browser testing.
- **Artifacts**: `walkthrough.md`, `audit_log`.

---

## Integration with Task Boundary

When using `task_boundary`, map BMAD phases as follows:

- **Start of Task** → **PLANNING** (Covers Analysis, Planning, Solutioning).
- **Coding** → **EXECUTION** (Implementation).
- **Testing/Review** → **VERIFICATION**.

> "Solutioning" is the bridge. If solutioning is purely design (writing docs), it's PLANNING. If it involves prototyping code, it's EXECUTION.

---

## Tagging

# protocol #process #methodology #bmad #alignment
