---
created: 2025-12-27
last_updated: 2026-01-30
graphrag_extracted: true
---

---id: 200
title: Feature Context Persistence
category: architecture
created: 2025-12-27
last_updated: 2025-12-27
---

# Protocol 200: Feature Context Persistence

> **Purpose**: Maintain context across multiple sessions for features that span days/weeks.

## Problem

Session logs (`quicksave.py`) capture conversation flow but are **session-scoped**. Multi-day features lose context when sessions end.

## Solution

For any feature expected to span multiple sessions, create a **Feature Context File**.

## Template

Location: `.context/features/FEATURE-NAME.md`

```markdown
# Feature: [Name]

**Goal**: [One-line objective]

## Current Phase
- Phase: [N of M]
- Status: [In Progress / Blocked / Done]
- Acceptance Criteria: [What signals completion?]

## Progress Log
| Date | Phase | Accomplishment | Decision |
|------|-------|----------------|----------|
| YYYY-MM-DD | N | Did X | Chose Y because Z |

## Deviations
- [Date]: Changed X to Y because Z

## Relevant Files
- `path/to/file.py` — [Role]
- `path/to/doc.md` — [Role]

## Next Session Primer
> What the AI needs to know to resume immediately:
> - [Context point 1]
> - [Context point 2]
```

## Trigger

Create a Feature Context File when:

- Estimated work > 2 sessions
- Multiple components involved
- Complex decision history worth preserving

## Execution

1. On first session: Create feature file with Goal + Phase 1
2. End of each session: Update Progress Log + Next Session Primer
3. On `/start`: AI scans `.context/features/` for active features
4. On completion: Move to `.context/features/archive/`

---

## Tags

# protocol #architecture #context #persistence
