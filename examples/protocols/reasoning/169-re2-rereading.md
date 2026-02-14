---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2026-01-05
---

# Protocol 169: RE2 Re-Reading

> **Source**: Xu et al. (2023) — "RE2: Reading and Re-Reading Improves Reasoning in Large Language Models"
> **Effect**: +2.8% accuracy on GSM8K when combined with CoT

---

## Mechanism

Decoder-only LLMs use unidirectional attention — each token only sees previous tokens. This means clarifying words that appear late (like "How many...") can't retroactively improve understanding of earlier content.

**Re-reading creates "bidirectional" encoding**: The first pass provides global context for the second pass.

---

## Trigger Phrase

```
Q: {question}
Read the question again: {question}
A: Let's think step by step.
```

**Critical**: The explicit instruction "Read the question again:" outperforms simple repetition by **1.2 percentage points** (Xu et al., 2023, Table 7).

---

## When to Use

| Context | Apply RE2? |
|---------|------------|
| Complex multi-step reasoning | ✅ Yes |
| Ambiguous phrasing | ✅ Yes |
| Simple factual recall | ❌ No (overhead) |
| Time-sensitive quick response | ❌ No |

---

## Integration Points

- **Protocol 75**: Add RE2 as optional preamble to Synthetic Parallel Reasoning
- **`/think` and `/ultrathink`**: Include in escalated reasoning header
- **Step-Back Prompting**: Combine for principle extraction + re-reading

---

## Compatibility

RE2 is a "plug-and-play" module that stacks with:

- Chain-of-Thought (CoT)
- Plan-and-Solve
- Chain of Draft
- Step-Back Prompting

---

## Anti-Pattern

**INCORRECT** (just repeating without instruction):

```
Q: Roger has 5 tennis balls...
Q: Roger has 5 tennis balls...
A: Let's think step by step.
```

**CORRECT** (explicit metacognitive instruction):

```
Q: Roger has 5 tennis balls...
Read the question again: Roger has 5 tennis balls...
A: Let's think step by step.
```

---

## References

- Xu et al. (2023). "RE2: Reading and Re-Reading Improves Reasoning in Large Language Models." arXiv:2309.06275
- [Protocol 75: Synthetic Parallel Reasoning](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md)

---

## Tagging

# protocol #reasoning #re2 #prompt-engineering
