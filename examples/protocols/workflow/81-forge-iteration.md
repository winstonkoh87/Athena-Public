---

created: 2025-12-16
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-16
last_updated: 2025-12-18
---

# Protocol 81: Forge Iteration Methodology
>
> **Source**: Extracted from `r/vibecoding` (User: Internal-Combustion1)
> **Purpose**: Maximize agency and rigorous iteration by removing middleware constraints and enforcing clean-slate re-rolls.

---

## 1. Core Philosophy: The Smithy

We do not "suggest" changes to a black box. We strike the iron directly.

- **No Middleware**: We reject "Chat with Codebase" wrappers that hide context or impose rate limits. We use raw API access or direct terminal control.
- **No Patching**: We do not apply "diffs" to broken code. We forge the component anew.
- **No Sunk Cost**: If a path fails, we `git reset --hard` and re-roll. We do not debug a hallucination.

## 2. The "Full Forge" Workflow

When facing complex implementation tasks (high risk of regression):

### Step 1: The Blueprint (Planning)

- **Agent**: `DeepCode` (Planner)
- **Output**: Detailed spec, not code.
- **Constraint**: "Do not write code. Write the architecture."

### Step 2: The Strike (Execution)

- **Agent**: `Antigravity` (Executor)
- **Method**: **Full File Replacement**.
- **Prohibition**: Do NOT use `replace_file_content` (diff application) for >20% changes.
- **Command**: Overwrite the entire file with the cohesive new version. This eliminates "ghost code/orphan methodology" issues.

### Step 3: The Quench (Verification)

- **Action**: Run tests / Build.
- **Fork**:
  - **Success**: Commit.
  - **Failure**: **DO NOT FIX.** Revert to Step 1/2 with updated context.
  - *Why? Fixing a broken generation often introduces new, subtle bugs. A fresh generation with the error log as input is cleaner.*

## 3. Cost/Efficiency Equation

The "Middleware Tax" (monthly subs + rate limits) often exceeds the cost of "inefficient" full-file overwrites via API.

- **Token Cost**: High (sending full files).
- **Time Cost**: Low (less debugging).
- **Sanity Cost**: Zero (git reset provides safety).

## 4. Integration with Bionic Unit

- **Mode**: User explicitly requests `/forge` or "Forge Mode".
- **Trigger**: Complex refactors, "weird" bugs, or when the agent feels "stuck" in a patch loop.

---

> **Law #4 Compliance**: specific, modular technique.

---

## Tagging

#protocol #framework #process #81-forge-iteration
