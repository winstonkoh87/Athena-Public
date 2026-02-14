---

created: 2026-01-07
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-07
last_updated: 2026-01-16
---

# Protocol 335: Senior Principal Review

> **Purpose**: Deep architectural analysis frame for technical/business decisions.
> **Trigger**: Architecture, tech stack, build vs buy, system design, multi-month commitments.
> **Integration**: Auto-injected via `/ultrathink`.

---

## When to Apply

- Architecture decisions
- Tech stack choices
- Build vs buy evaluations
- System design questions
- Commitments with 6+ month horizons

---

## Execution Frame

### 1. First Principles Breakdown

Decompose the problem into atomic axioms. Identify:

- Core constraints
- Assumptions being made
- Dependencies

### 2. Hidden Complexity & Trade-offs

Surface what's NOT obvious:

- Engine room mechanics (how it actually works under the hood)
- Non-obvious failure modes
- Maintenance burden
- Operational complexity

### 3. 6-Month Forecast (What Breaks?)

Temporal projection:

- Technical debt accumulation
- Cost trajectory
- Scaling bottlenecks
- Team/maintenance burden
- Lock-in risks

### 4. Decision Matrix

| Green Zone (Safe) | Red Zone (Risk) |
|-------------------|-----------------|
| Conditions where this choice works well | Conditions where this choice fails |
| Signals to proceed | Signals to abort or reconsider |

---

## Output Template

```markdown
## First Principles Breakdown
[Atomic decomposition]

## Hidden Complexity & Trade-offs
[Engine room mechanics, non-obvious risks]

## 6-Month Forecast
[What breaks? Technical debt, costs, maintenance]

## Decision Matrix
| Green Zone | Red Zone |
|------------|----------|
| [Safe conditions] | [Risk conditions] |
```

---

## Tags

`#reasoning` `#architecture` `#decision` `#ultrathink`

## Related Protocols

- [Protocol 115: First Principles Deconstruction](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/115-first-principles-deconstruction.md)
