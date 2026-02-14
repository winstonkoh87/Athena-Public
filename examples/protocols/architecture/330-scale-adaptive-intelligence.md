---
created: 2026-01-02
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: scale-adaptive-intelligence
description: Automatically adjusts planning depth based on project complexity. Use when determining appropriate effort level for any task.
tags: [architecture, planning, complexity, bmad]
created: 2026-01-02
last_updated: 2026-01-06
---

# Protocol 330: Scale-Adaptive Intelligence

> **Source**: BMAD-METHOD v6. Integrated 02 January 2026.  
> **Purpose**: Match planning depth to project complexity automatically.

---

## The Problem

One-size-fits-all planning wastes resources:

- **Over-planning** bug fixes → Slow delivery
- **Under-planning** enterprise systems → Technical debt, rework

## The Solution: 5-Level Scaling

| Level | Project Type | Planning Depth | Athena Mode |
|-------|-------------|----------------|-------------|
| **L1** | Bug Fix / Typo | Minimal | Quick response |
| **L2** | Small Feature | Light spec | Single session |
| **L3** | Medium Project | PRD + Tech Spec | `/brief` + `/think` |
| **L4** | Large System | Full architecture | `/research` + multi-session |
| **L5** | Enterprise | Complete lifecycle | `/ultrathink` + formal review |

---

## Detection Heuristics

### Automatic Classification

| Signal | L1-L2 | L3 | L4-L5 |
|--------|-------|-------|-------|
| Files affected | 1-3 | 4-10 | >10 |
| New dependencies | 0 | 1-2 | >2 |
| API changes | None | Minor | Breaking |
| Time horizon | Hours | Days | Weeks+ |
| Stakeholders | 1 | 2-3 | >3 |
| Risk of rework | Low | Medium | High |

### Manual Override

User can force level: "This is L4 complexity" or `/ultrathink` (forces L5).

---

## Planning Depth by Level

### L1: Bug Fix (Minimal)

- [ ] Identify root cause
- [ ] Fix and verify
- [ ] Done

### L2: Small Feature (Light)

- [ ] Clarify requirements (1-2 questions)
- [ ] Implement
- [ ] Test affected paths
- [ ] Done

### L3: Medium Project (Standard)

- [ ] Requirements gathering (`/brief`)
- [ ] Technical approach
- [ ] Implementation plan
- [ ] Code + test
- [ ] Review + ship

### L4: Large System (Full)

- [ ] Stakeholder alignment
- [ ] PRD / Requirements doc
- [ ] Architecture design
- [ ] Component breakdown
- [ ] Implementation phases
- [ ] Testing strategy
- [ ] Documentation
- [ ] Deployment plan

### L5: Enterprise (Complete)

- [ ] All L4 items
- [ ] Security review
- [ ] Scalability analysis
- [ ] Rollback strategy
- [ ] Monitoring/observability
- [ ] Runbooks
- [ ] Post-mortem template

---

## Integration with Athena

- **Detection**: Auto-classify at session start based on user request
- **Routing**: Map to appropriate workflow (`/brief`, `/think`, `/ultrathink`)
- **Transparency**: State detected level in response

**Example**:
> "This looks like an L3 (medium) project. I'll use the standard planning approach. Override with `/ultrathink` if you want full depth."

---

## Related Protocols

- [Protocol 133](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md): Query Archetype Routing
- [Protocol 77](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/77-adaptive-latency-architecture.md): Adaptive Latency

---

## Tagging

# protocol #architecture #complexity #bmad #scale-adaptive
