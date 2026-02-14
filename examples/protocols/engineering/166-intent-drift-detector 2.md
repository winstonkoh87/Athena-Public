---

created: 2025-12-23
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-23
last_updated: 2026-01-13
---

# Protocol 166: Intent Drift Detector

> **Purpose**: Prevent silent logic corruption from cumulative AI prompts.
> **Trigger**: When code "works" but feels wrong, or when explaining logic is harder than it should be.

---

## The Problem

AI preserves **output**, not **intent**.

```
Prompt 1: "Build feature X"     → Code A (works, intent captured)
Prompt 2: "Optimize X"          → Code B (output matches, intent drifts)
Prompt 5: "Fix edge case"       → Code E (works, but WHY is unclear)
Prompt N: "Add one more thing"  → Code N (works, original intent lost)
```

Each prompt is **lossy compression**. The LLM matches *current output*, not *original reasoning*.

---

## Diagnostic Questions

Before touching "working" code, ask:

1. **Can I explain WHY this works?** (not just THAT it works)
2. **Does current logic match ORIGINAL intent** or just current output?
3. **How many prompts have touched this file since freeze?**
4. **Would I be confident handing this to another developer?**

---

## Red Flags

| Signal | Interpretation |
|--------|----------------|
| "It works but I don't know why" | Intent already drifted |
| Prompt count > 5 on same file | High mutation risk |
| Nested conditionals added "to fix edge case" | Bandaid on bandaid |
| "AI added this, not sure what it does" | Lost authorship |

---

## The Rule

> **If prompts > 5 AND you can't explain the logic → STOP. Audit before continuing.**

### Mandatory Infrastructure (The "Steal" from r/vibecoding)

1. **Explicit Intent Logging**: Every significant logical change MUST be documented in `.agent/TASK_LOG.md`. Explain *what* was changed and *why* (the intent), not just the output.
2. **Visual Verification**: Use `python3 .agent/scripts/generate_puml.py` to refresh the visual architecture. Ensure current logic hasn't created unintended structural complexity.

---

## Integration

- Links to: [Protocol 130: Vibe Coding](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/130-vibe-coding.md) — when speed matters
- Links to: [Protocol 93: Forward-Only Architecture](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/93-forward-only-architecture.md) — freeze after validation
- Links to: [TASK_LOG.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/TASK_LOG.md) — intent persistence
- Source: Reddit r/vibecoding (Dec 2025)

---

## Tagging

`#protocol` `#engineering` `#vibe-coding` `#intent-preservation`
