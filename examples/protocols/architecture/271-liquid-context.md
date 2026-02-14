---

created: 2026-01-04
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-04
last_updated: 2026-01-04
---

# Protocol 271: Liquid Context (The "Docs" Pattern)

> **Source**: Boris Cherny (Creator of Claude Code) / Reddit (2025)
> **Purpose**: Convert behavioral errors into permanent instruction updates.
> **Philosophy**: "Don't just fix the code. Fix the instructions that generated the code."

---

## 1. The Core Mechanic

**Liquid Context** is the practice of treating documentation not as a static record, but as a mutable **Action Layer**.

If the AI makes a mistake (e.g., uses the wrong CSS class, hallucinates a dependency, fails a test), the correction MUST be propagated to a persistent context file (`AI_Learnings.md` or `project_state.md`).

### The Formula

> **Error** → **Correction** → **Update Docs** → **Retry**

This prevents the "Groundhog Day" loop where the user fixes the same AI mistake in every session.

## 2. Implementation: `AI_Learnings.md`

Every active project should have an `AI_Learnings.md` (or equivalent section in `README.md`) specifically for **Robot Eyes**.

**Structure**:

```markdown
# AI Learnings & Instructions

> **NOTICE**: Read this before generating code for this project.

## Proven Patterns (Do This)
- [x] Use `min-h-screen` for all page wrappers (Fixes: 2024-01-02 layout bug).
- [x] Use `supabase_search.py` BEFORE answering any query.

## Anti-Patterns (Do Not Do This)
- [ ] Do NOT use `shadcn/ui` (we are using raw Tailwind).
- [ ] Do NOT suggest `cd` commands (use absolute paths).
```

## 3. The Compounding Engineering Loop

When a user rejects a plan or code:

1. **Diagnose**: Why did I fail? (Missing context? Bad assumption?)
2. **Patch**: Fix the immediate code.
3. **Solidify**: Add a rule to `AI_Learnings.md`.
    * *Example*: "I assumed `pytest` was installed. It's `unittest`." -> *Update*: "Use `unittest` for all tests."
4. **Verify**: Confirm the new rule is actionable.

## 4. Sub-Agent Handover

If handing off to a sub-agent or another session:
"Check `AI_Learnings.md` for the latest constraints."

## 5. Tagging

# workflow #architecture #learning #context-engineering
