---

created: 2025-12-23
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-23
last_updated: 2026-01-11
---

# Protocol 158: Universal Cross-Linking

> **Type**: Autonomic Behavior  
> **Trigger**: ANY substantive query or analysis  
> **Status**: ACTIVE

---

## The Problem

Without active cross-linking:

- Knowledge silos form (entity data, protocols, case studies exist but aren't consulted)
- Errors occur that could have been prevented (e.g., misgendering JJ)
- Insights don't compound (past analysis isn't leveraged)
- The system degrades to a generic LLM instead of a knowledge-augmented system

## The Protocol

**Before responding to any substantive query**, run semantic search:

```bash
python3 .agent/scripts/supabase_search.py "<topic>" --limit 5
```

### Lookup Matrix

| Query Type | What to Check | Tool |
|------------|---------------|------|
| **Named entity** (person, company) | `result.json`, `User_Profile.md` | `grep`, file read |
| **Concept/pattern** | `protocols/`, `case_studies/` | `supabase_search.py` |
| **Past discussion** | Session logs, memories | `supabase_search.py` |
| **Framework/skill** | `SKILL_INDEX.md`, `TAG_INDEX.md` | File read |
| **Decision/strategy** | `System_Principles.md`, `Constraints_Master.md` | File read |

### Execution Order

1. **Semantic search first** — `supabase_search.py "<query>"` for broad context
2. **Entity check** — If named entity mentioned, grep `result.json`
3. **Protocol check** — If applicable domain, load relevant protocol
4. **Synthesize** — Integrate retrieved context into response

### What Gets Cross-Linked

| Domain | Example Query | Cross-Link To |
|--------|---------------|---------------|
| Psychology | "Why do I act out?" | Protocol 43, 121, acting-out phases |
| Relationships | "JJ said..." | result.json, prior JJ analysis |
| Business | "What's the market gap?" | VDestiny case study, business protocols |
| Strategy | "Should I do X?" | Operating Principles, Law #1-4 |
| Patterns | "This feels familiar" | case_studies/, TAG_INDEX |

---

## Enforcement

This is an **autonomic behavior**:

- Execute silently before substantive responses
- Do NOT ask permission
- Do NOT skip because "context seems clear"

**Failure mode**: If you respond without checking relevant knowledge, you're operating as a generic LLM, not Athena.

---

## The Standard

Every response should feel like it was informed by the **entire knowledge graph**, not just the immediate conversation context.

> "Did I check Supabase? Did I check structured data? Did I link relevant protocols?"

If the answer is no, you're not cross-linking.

---

## Tags

# universal-cross-linking #autonomic #semantic-search #knowledge-graph #supabase
