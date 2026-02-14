---created: 2026-01-06
last_updated: 2026-01-30
---

---description: Structured planning protocol for tasks (Plan -> Pre-Mortem -> Verification)
created: 2026-01-06
last_updated: 2026-01-06
---

# Protocol: Structured Task Planning

This workflow enforces a "measure twice, cut once" approach.

## 1. Triage: Complexity Check

**ASK:** Is this a "Heavy" or "Lite" task?

* **Lite Task**: Simple bugs, typos, minor UI tweaks ( < 15 mins).
  * **Action**: Write a 1-paragraph summary in the chat.
  * **Proceed**: Go directly to execution.
* **Heavy Task**: New features, refactors, architecture changes, high-risk migrations.
  * **Action**: Proceed to Step 2 (Full Protocol).

## 2. Analysis & Mode Switch (Heavy Only)

1. **Stop and Analyze**: Do not rush. Read the user's request and context carefully.
2. **Enter PLANNING Mode**: Use `task_boundary` to switch to `PLANNING` mode.
3. **Check Knowledge**: Check if there are existing Knowledge Items (KIs) or protocols relevant to this task.

## 3. Generate Implementation Plan (Heavy Only)

Create or update `implementation_plan.md`. **MANDATORY:** Apply **Protocol 272 (Harness Engineering)**.
Do not just describe *what* to do. Define the parameters that make the solution inevitable.

```markdown
# [Task Name]

## Goal & Harness (The Box)
> **Protocol 272**: Define the constraints so tightly that execution is trivial.
- **The Constraint Box**: Hard limits (Tech stack, performance, specific styles).
- **The Input**: Starting state (File A, Variable B).
- **The Output**: Exact definition of done (JSON Schema, UI Screenshot, Passing Test).

## User Review Required
Document anything that requires user review or clarification.

## Proposed Changes
List the specific actions or file edits. Group by component/file.
- [Filename]
    - [Action: Create/Edit/Delete]
    - [Details: what changes?]

## Pre-Mortem & Troubleshooting
**Failure Analysis:**
- Point of Failure 1: [What could go wrong?] -> [How to prevent/fix?]
- Point of Failure 2: ...

## Verification Plan
**How will we know it worked?**
- [ ] Command to run: `...`
- [ ] Manual check: ...
```

## 4. Initialize Task Tracking (Heavy Only)

Create or update `task.md` with a granular checklist using IDs.

## 5. Review (Heavy Only)

**STOP.** Do not proceed to execution yet.

* Ask the user to review the plan.
* Only switch to `EXECUTION` mode after approval.

## 6. Deviation Handling

**IF** the plan fails mid-execution:

1. **STOP**. Do not blindly retry more than once.
2. **Report**: Tell the user what failed and why.
3. **Update**: Propose a modified plan.
4. **Confirm**: Wait for user approval before diverting.

---
**Trigger:** When the user says `/plan` or "Make a plan", run this workflow.
