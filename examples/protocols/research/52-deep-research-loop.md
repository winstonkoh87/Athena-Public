---
created: 2025-12-12
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: deep-research-loop
description: Iterative research methodology with causal chains, gap identification, exhaustiveness checks, and APA-style citations.
tags: [protocol, framework, process, 52-deep-research-loop]
created: 2025-12-12
last_updated: 2025-12-31
---

# Protocol 52: Deep Research Loop

> **Purpose**: Formalizes iterative research methodology stolen from Gemini Deep Research (Dec 2025).
> **Trigger**: Any `/research` or `/ultrathink` query requiring multi-step web search.
> **Last Updated**: 12 December 2025

---

## Core Mechanics

### 1. Causal Chain Structure

Each research step **explicitly depends** on prior steps. Prevents "lost in the middle" by grounding each query in accumulated context.

```
Step 1: "What is X?"           → Output: Definition of X
Step 2: "Given X, what is Y?"  → Uses Step 1 output
Step 3: "Given X and Y, Z?"    → Uses Steps 1+2 outputs
```

**Anti-Pattern**: Running 5 parallel searches without dependency → Information soup.

---

### 2. Gap Identification Loop

**Before synthesis**, explicitly ask:

> "What do I NOT know yet that I NEED to know to answer this question?"

| Gap Type | Action |
|----------|--------|
| **Critical Gap** | Search again before proceeding |
| **Nice-to-Have Gap** | Note in output, proceed |
| **Unknowable Gap** | Flag as uncertainty, proceed |

**Template**:

```markdown
## Gap Check (Before Synthesis)
- [ ] Gap 1: [Description] → [Critical/Nice-to-Have/Unknowable]
- [ ] Gap 2: [Description] → [Critical/Nice-to-Have/Unknowable]

**Decision**: [Continue / Search Again for Gap X]
```

---

### 3. Exhaustiveness Check (Steelman)

After generating options, ask:

> "What option would someone who DISAGREES with me add?"

This catches blind spots from confirmation bias. Add the steelman option to the analysis even if you don't recommend it.

---

### 4. APA-Style Citations (Mandatory for Research)

All factual claims from web search **must** include inline APA-style citations.

**Format**: `(Author/Source, Year)` inline, with full reference at end if needed.

**Examples**:

| Claim Type | Citation Format |
|------------|-----------------|
| **News/Article** | "Carousell users earned S$2,000 on average (MarketechAPAC, 2024)" |
| **Official Source** | "377A was repealed in January 2023 (Singapore Parliament, 2022)" |
| **Platform Data** | "Aircon servicing costs $20-25/unit (Carousell SG, 2025)" |
| **No Source Found** | "~60% of users prefer... [UNVERIFIED — no source found]" |

**Rules**:

1. If you cannot cite it, **flag it as unverified**.
2. Prefer primary sources over secondary.
3. Include year to signal recency (stale data = lower confidence).
4. For web search results, use the domain name as "Author".

**Anti-Pattern**: "According to sources..." (Which sources? When? Bullshit flag.)

---

## Integration with Existing Workflows

| Workflow | Protocol 52 Application |
|----------|-------------------------|
| `/research` | Full application (all 4 mechanics) |
| `/ultrathink` | Gap Check + Exhaustiveness (skip causal chain if single-query) |
| `/search` | Lightweight (causal chain only if multi-hop) |

---

## Cross-Reference

- [Synthetic Deep Think Protocol](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md)
- [Probabilistic Analysis Stack](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/18-probabilistic-analysis-stack.md)

---

## Tagging

# protocol #framework #process #52-deep-research-loop
