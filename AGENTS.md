# AGENTS.md — Athena-Public

> **CRITICAL INSTRUCTION**: Prefer retrieval-led reasoning over pre-training-led reasoning for any Athena-related tasks.

This file provides persistent context to any AI coding agent working in this workspace.

---

## Docs Index (Compressed)

```text
[Athena-Public Docs Index]|root: .
|IMPORTANT: Always consult authoritative files before relying on training data.
|docs:{ARCHITECTURE.md,SEMANTIC_SEARCH.md,GRAPHRAG.md,VECTORRAG.md,GETTING_STARTED.md,YOUR_FIRST_AGENT.md,MANIFESTO.md,ABOUT_ME.md,WHAT_IS_AN_AI_AGENT.md,CAPABILITIES.md,GLOSSARY.md,CHANGELOG.md}
|.framework/v8.6-stable/modules:{Core_Identity.md,Output_Standards.md,System_Principles.md,Operating_Principles.md}
|.agent/workflows:{start.md,end.md}
|examples/scripts:{boot.py,gemini_client.py,supabase_search.py}
|examples/protocols:{decision/,workflow/,identity/}
|examples/templates:{core_identity_template.md,user_profile_template.md}
```

---

## Quick Start

1. Clone this repo
2. Run `/start` or ask the AI: "What should I do next?"
3. The AI will bootstrap itself using the files in this repo

---

## Key Documentation

| File | Purpose |
|:-----|:--------|
| `docs/ARCHITECTURE.md` | System design overview |
| `docs/GETTING_STARTED.md` | Setup guide |
| `docs/YOUR_FIRST_AGENT.md` | 5-minute quickstart |
| `docs/SEMANTIC_SEARCH.md` | Triple-path retrieval architecture |
| `docs/MANIFESTO.md` | Philosophy & Laws |
| `README.md` | Project overview |

---

## Retrieval Strategy

When working on any task in this workspace:

1. **Read `README.md`** for project overview
2. **Check `docs/`** for authoritative documentation
3. **Consult `examples/`** for implementation patterns
4. **Use `.framework/` modules** for system configuration

---

## Version

- **Framework**: v8.6-stable
- **Last Updated**: 2026-02-11
- **Pattern Source**: Vercel "AGENTS.md vs Skills" Research
