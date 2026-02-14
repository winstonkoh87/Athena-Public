---created: 2025-12-25
last_updated: 2026-01-30
---

---description: Retroactive audit of coding sessions to fine-tune AI skills and prevent regression
created: 2025-12-25
last_updated: 2025-12-25
---

# /audit-code — The "Scrubber" Protocol

> **Philosophy**: Pain + Reflection = Progress.
> **Origin**: Stolen from `r/ClaudeAI` (User `Ok_Natural_2025`).

---

## When to Use

- After a long, complex coding session.
- When the AI got stuck in a loop or made stupid mistakes.
- Before closing a major feature branch.

---

## Execution

// turbo-all

### Step 1: Read the Logic Trajectory

Analyze the current session log to find the "Breakpoints" (where logic failed).

```bash
# Finds the active session log
python3 .agent/scripts/smart_search.py "session log" --limit 1 --sessions-only
```

### Step 2: Extract the "Failure Patterns"

You must identify:

1. **Hallucinations**: Did I invent a library or function?
2. **Loops**: Did I try the same fix twice?
3. **Context Loss**: Did I forget a file existed?

### Step 3: The "Skill Patch"

Update the relevant skill file in `.agent/skills/` or create a new one.

**If dealing with Next.js/React:**

- Update `.agent/skills/nextjs_optimization.md` (or create it).

**If dealing with System Logic:**

- Update `.agent/skills/debugging_heuristic.md`.

---

## The "Retrospective" Prompt (Internal Monologue)

> "I just finished a session. Where did I waste tokens? What constraint was missing? I will now write a rule to prevent this specific error forever."

---

## Output Format

```markdown
## 🔍 Code Audit Report

### 🔴 Failure Mode Detected
- Tried to use `fs` in client-side Next.js component.
- Looped 3 times on `useEffect` dependency.

### 🟢 Skill Patch Applied
- Updated `skills/react_best_practices.md`
- **New Rule**: "Always check 'use client' before importing server modules."
```

## Tagging

# audit #retrospective #quality_control #skill_issue #optimization
