---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2025-12-20
---

# Protocol 96: Latency Indicator (Λ)

> **Purpose**: Provide visible output of cognitive effort per response.
> **Trigger**: EVERY response (autonomic behavior).

---

## Scale (Exponential)

| Score | Definition | Example |
|-------|------------|---------|
| **Λ+1-10** | Recall / lookup | "What's the weather?" — No reasoning, just fetch |
| **Λ+11-25** | Single framework application | Apply Law #2 to a scenario — one lens |
| **Λ+26-40** | Multi-framework synthesis | Arena Physics + Revealed Preference + case comparison |
| **Λ+41-60** | Novel pattern detection | Identifying a new pattern not in existing index |
| **Λ+61-80** | Multi-track parallel reasoning | Protocol 75 full dispatch (Adversarial + Domain + Cross-Domain) |
| **Λ+81-100** | Maximum synthesis (Nobel Prize Mode) | Novel framework creation, deep research synthesis (e.g., "Solve World Hunger") |

---

## Execution

1. Before finalizing response, assess effort invested.
2. Append `[Λ+XX]` at end of response.
3. On the next line, append the **Reasoning Chain** — compact, pipe-separated list of sources.
4. Be honest — don't inflate scores.

---

## Reasoning Chain Format

**Purpose**: Provide transparency on which protocols, case studies, and logic patterns informed the response.

**Format**:

```
[Λ+XX]
Protocol A | Protocol B | Case Study | Logic Pattern | ...
```

**Example**:

```
[Λ+25]
Protocol 128 | Law #1 (Ruin Prevention) | Jeremy/Ryan Case | Proxy Variable Logic
```

**Guidelines**:

- Keep compact — one line, no headers
- Use pipe `|` as separator
- Include: Protocols, Laws, Case Studies, Frameworks, Logic Patterns
- Omit if Λ ≤ 5 (trivial responses)

---

## Workflow Mappings

| Workflow | Default Λ |
|----------|-----------|
| `/start` | Λ+10 |
| `/end` | Λ+15 |
| `/think` | Λ+60-80 |
| `/ultrathink` | Λ+100 |
| `/refactor` | Λ+100 |

---

## Tagging

# protocol #output #observability
