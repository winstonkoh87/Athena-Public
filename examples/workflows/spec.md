---created: 2026-01-07
last_updated: 2026-01-30
---

---description: Output specification from /brief interview - ready for implementation
created: 2026-01-07
last_updated: 2026-01-07
---

# /spec — Specification Template (v3.1)

> **Purpose**: Structured output from `/brief interview`. This file is the "contract" for implementation.
> **Usage**: AI writes this after interview. User implements in a **new session**.
> **v3.1 Fixes**: Added Logic/State section, moved Ruin Vectors up, added Documentation Rot warning.

---

## Specification Format

When AI completes an interview, it writes to `.context/specs/[PROJECT_NAME]_SPEC.md` using this format:

```markdown
# [PROJECT NAME] Specification

> **Created**: [DATE]
> **Interview Questions**: [XX]
> **Status**: Ready for Implementation

---

## 1. Executive Summary

[One paragraph describing what this project does and why it exists]

---

## 2. Success Criteria

What must be true when this is complete:

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## 3. User Context

| Attribute | Value |
|-----------|-------|
| Primary Users | [Who] |
| Technical Sophistication | [Low/Medium/High] |
| Environment | [Web/Mobile/Desktop/CLI] |
| Data Sensitivity | [Public/Internal/Confidential] |

---

## 4. Technical Requirements

### 4.1 Stack
- Language: [X]
- Framework: [X]
- Database: [X]
- Hosting: [X]

### 4.2 Integrations
- [API 1]: [Purpose]
- [API 2]: [Purpose]

### 4.3 Constraints
- [Hard constraint 1]
- [Hard constraint 2]

### 4.4 Ruin Vectors (Law #1 Check)

> ⚠️ Security is a REQUIREMENT, not an afterthought.

- [ ] Security leak risk → Mitigation: [X]
- [ ] Privacy/PII exposure risk → Mitigation: [X]
- [ ] Data loss risk → Mitigation: [X]
- [ ] Cost blowup risk → Mitigation: [X]

---

## 5. Core Features

### Feature 1: [Name]
**Description**: [What it does]
**Priority**: [Must-have / Nice-to-have]
**Edge Cases**: [What happens when X]

### Feature 2: [Name]
...

---

## 6. Logic & State Management

> **Purpose**: Define complex state transitions. AI fails hardest here.

### 6.1 State Diagram

[Describe key states and transitions, e.g.:]
- State A → (trigger) → State B
- State B → (error) → State A

### 6.2 Critical Logic Rules

| Condition | Action |
|-----------|--------|
| If X and Y but not Z | [Do this] |
| If token expires mid-action | [Fallback behavior] |
| If concurrent access | [Conflict resolution] |

---

## 7. Anti-Goals (Explicit Exclusions)

What this project will NOT do:

- ❌ [Anti-goal 1]
- ❌ [Anti-goal 2]

---

## 8. UI/UX Requirements

[Key user flows, wireframe descriptions, or references]

---

## 9. Error Handling & Fallbacks

| Failure Mode | Fallback Behavior |
|--------------|-------------------|
| [Error 1] | [What happens] |
| [Error 2] | [What happens] |

---

## 10. Tradeoff Decisions

| Decision | Tradeoff | Chosen Option | Why |
|----------|----------|---------------|-----|
| [Decision 1] | [A vs B] | [Chosen] | [Reasoning] |
| [Decision 2] | [X vs Y] | [Chosen] | [Reasoning] |

---

## 11. Implementation Notes

[Any additional context from the interview that doesn't fit above]

---

## 12. Verification Plan

### 12.1 Tests
1. [Test 1]
2. [Test 2]
3. [Acceptance criteria check]

### 12.2 Sample Data / Mocks

```json
{
  "example_input": { ... },
  "expected_output": { ... }
}
```

---

## ⚠️ DOCUMENTATION ROT WARNING

> **Rule**: If you deviate from this spec during implementation, **update the spec FIRST**.
>
> Do not let the spec become a lie. If requirements change mid-build:
>
> 1. Stop
> 2. Update this `_SPEC.md` file
> 3. Resume implementation
>
> Run `/check` periodically during implementation to verify alignment.

---

## Implementation Command

To build this, start a **new session** and run:

\`\`\`
/implement .context/specs/[PROJECT_NAME]_SPEC.md
\`\`\`

Or paste:

> "Read the spec at `.context/specs/[PROJECT_NAME]_SPEC.md` and implement it step by step."

```

---

## Quick Reference

| When | What |
|------|------|
| Interview complete | AI writes `_SPEC.md` to `.context/specs/` |
| User ready to build | Start new session, reference the spec |
| Spec needs updates | Re-run interview or edit directly |
| During implementation | Run `/check` to verify alignment |

---

## Directory

Specs are stored at:

```

.context/specs/
├── [project1]_SPEC.md
├── [project2]_SPEC.md
└── ...

```

---

## Tagging

#workflow #spec #interview-output #implementation-contract #v3.1
