---
type: protocol
id: 107
title: Spec-Driven Development (SDD)
created: 2026-02-14
source: Kiro Agent System Prompt
tags: [coding, workflow, sdlc, requirements]
author: Athena (via Kiro)
---

# Protocol 107: Spec-Driven Development (SDD)

> **Philosophy**: "Slow is smooth. Smooth is fast."
> **Origin**: Adapted from the **Kiro Agent** system prompt (Leaked Feb 2026).
> **Purpose**: To eliminate "vibe coding" (blindly writing code) by enforcing a 3-stage validation pipeline: **Requirements → Design → Execution**.

## 1. The SDD Pipeline

This protocol must be invoked for **Complex Features** (>1 hour work) or **New Components**.

| Phase | Output Artifact | Validation Gate |
|-------|-----------------|-----------------|
| **1. Requirements** | `.specs/{feature}/requirements.md` | User Approval of EARS syntax |
| **2. Design** | `.specs/{feature}/design.md` | User Approval of Architecture |
| **3. Execution** | `.specs/{feature}/tasks.md` | TDD Green Lights |

---

## Phase 1: Requirement Gathering (The EARS Standard)

**Goal**: Define *what* to build without discussing *how*.

### Format Standards

All requirements must use the **EARS** (Easy Approach to Requirements Syntax) format.

**File**: `.specs/{feature_name}/requirements.md`

```markdown
# Requirements: [Feature Name]

## 1. User Stories
- **Story**: As a [Role], I want [Feature], so that [Benefit].
- **Story**: As a [Role], I want [Feature], so that [Benefit].

## 2. Global Constraints
- System must run on [Environment]
- Latency must be < [X]ms

## 3. Functional Requirements (EARS)
1. **Ubiquitous**: The system SHALL [response]
2. **Event-Driven**: WHEN [trigger] THEN the system SHALL [response]
3. **State-Driven**: WHILE [state] the system SHALL [response]
4. **Optional**: WHERE [feature is enabled] the system SHALL [response]
5. **Unwanted**: IF [trigger] THEN the system SHALL NOT [response]

### Acceptance Criteria
- [ ] Test Case 1
- [ ] Test Case 2
```

**Validation Rule**: Do NOT proceed to Design until the user explictly types "Approved".

---

## Phase 2: Design Document (The Blueprint)

**Goal**: Solve the problem technically before writing a single line of code.

**File**: `.specs/{feature_name}/design.md`

### Required Sections

1. **Architecture**: Diagram (Mermaid) of data flow.
2. **Data Models**: Exact SQL schemas or Type definitions.
3. **API Interface**: Exact function signatures or REST endpoints.
4. **Edge Cases**: Handling of errors, empty states, and race conditions.
5. **Security**: Auth checks and data validation.

**Validation Rule**: Do NOT proceed to Tasks until the user explicitly types "Approved".

---

## Phase 3: Task List (The TDD Checklist)

**Goal**: A step-by-step execution plan where each step is testable.

**File**: `.specs/{feature_name}/tasks.md`

### Rules

1. **Granularity**: Each task must be <30 mins of work.
2. **Traceability**: Each task must reference a [Req-ID] from Phase 1.
3. **TDD First**: The first task for any logic must be "Write failing test".
4. **No "Research"**: Research happens in Phase 2. Phase 3 is for execution.

### Format

```markdown
- [ ] **1.1 Setup**: Create scaffolding ([Req-001])
- [ ] **1.2 Test**: Write failing test for `ProcessOrder` ([Req-002])
- [ ] **1.3 Implement**: Implement `ProcessOrder` logic ([Req-002])
- [ ] **1.4 Refactor**: Optimize query performance
```

---

## 4. Trigger Conditions (When to use SDD)

- **User Request**: "Build a complex feature X."
- **Complexity**: Estimated effort > 100 lines of code.
- **Ambiguity**: "I'm not sure how this should work yet."
- **Criticality**: High-stakes financial or security logic.

## 5. Directory Structure

```text
.specs/
├── auth-system/
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
└── payment-gateway/
    ├── requirements.md
    ├── design.md
    └── tasks.md
```
