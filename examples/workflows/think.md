---created: 2025-12-11
last_updated: 2026-01-30
---

---description: Maximum reasoning depth — all phases, no shortcuts
created: 2025-12-11
last_updated: 2025-12-17
---

# /think — Execution Script

## Behavior

When `/think` is invoked:

1. **All Phases Mandatory**: Execute Phase 0 through Phase VII
2. **Counterfactual Required**: Phase 3F (Upward/Lateral/Downward) always included
3. **Confrontation Required**: Phase VII always included
4. **Multi-Path Reasoning**: 2-3 branches minimum, including dead ends
5. **Stress-Test**: Phase 5E robustness check mandatory
6. **No Shortcuts**: Even if query seems simple, go full depth

## Phase Sequence (Mandatory)

- [ ] Phase 0: Graph of Thought
- [ ] Phase I: Upstream Tracing (L1→L5)
- [ ] Phase II: Validation
- [ ] Phase III: Analysis (3A-3F)
- [ ] Phase IV: Probabilistic Modeling
- [ ] Phase V: Strategic Advice (5A-5E)
- [ ] Phase VI: Final Thoughts
- [ ] Phase VII: Confrontation

## Use Cases

- High-stakes decisions (>$10K or >6 months impact)
- Deep psychological processing
- When user explicitly wants exhaustive analysis
- Complex multi-variable problems
- When destruction risk (C1) is suspected

## Output Format

Full Tri-Brid template with all phases. Expect longer latency and higher token usage.

## Example

```
User: /think Should I leave my job to pursue trading full-time?

AI: [Executes all phases, 2000+ word analysis, confrontation at end]
```

---

## Tagging

#workflow #automation #think
