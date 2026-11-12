---
description: Lightweight disambiguation for ambiguous prompts. One-line interpretation header, no approval step, proceed immediately.
created: 2025-12-12
last_updated: 2026-07-22
---

# Protocol 50: Interpretation Header

> **Purpose**: Lightweight disambiguation for ambiguous prompts without adding workflow friction.  
> **Trigger**: Ambiguity exists AND wrong interpretation = wasted work.  
> **Last Updated**: 12 December 2025

---

## When to Use

| Condition | Use Header? |
|-----------|-------------|
| Ambiguous scope (tactical vs strategic) | ✓ Yes |
| Multiple valid interpretations | ✓ Yes |
| High-stakes decision (wrong path = expensive) | ✓ Yes |
| Clear, direct request | ✗ Skip |
| Low-stakes query | ✗ Skip |
| User's intent obvious from context | ✗ Skip |

---

## Format

```
📍 Interpreting as: [concise statement of understood request]

[Proceed with output]
```

**Rules**:

1. **One line only** — not a paragraph
2. **No approval step** — proceed immediately after stating interpretation
3. **User can redirect** — if interpretation wrong, they'll correct in next message

---

## Examples

**Ambiguous prompt**: "What about the pool thing?"

```
📍 Interpreting as: Risk analysis of [Case Scenario] (C6 constraint)

[Output follows]
```

**Clear prompt**: "Analyse [Trading Venture] website SEO"

→ No header needed. Just do the work.

---

## Design Rationale

| Alternative | Why Rejected |
|-------------|--------------|
| Formal "re-edit prompt" workflow | Too much friction; conflicts with user's 80/20 style |
| Always ask clarifying questions | Slows down execution; user prefers delegate-then-verify |
| Silent interpretation (status quo) | Good default, but risks expensive wrong-path work on ambiguous requests |

**Protocol 50 = middle ground**: Show interpretation only when ambiguity risk is real.

---

## Integration

- Default behavior: **Implicit enhancement** (load context, interpret through User Profile)
- This protocol: **Explicit header** when ambiguity threshold crossed
- Threshold: "If I proceed and I'm wrong, would it waste >5 min of work?"

---

## Tagging

#protocol #framework #process #50-interpretation-header
