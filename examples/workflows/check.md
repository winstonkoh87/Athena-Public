---created: 2026-01-04
last_updated: 2026-01-30
---

---description: Run verification loop on current work (Protocol 270)
created: 2026-01-04
last_updated: 2026-01-04
---

# /check — Verification Loop

> **Purpose**: Enforce Protocol 270. Verify the last action taken.
> **Trigger**: User types `/check` or you finished a major task.

## Phase 1: Context Analysis

1. **Read** `task.md` or `AI_Learnings.md` to identify the active context.
2. **Identify** the Verification Plan stated in the last `task_boundary` or `implementation_plan.md`.
    - *If no plan exists*: **HALT**. You violated Protocol 270. Propose a plan immediately.

## Phase 2: Route & Verify

### Branch A: Code / Script Verification
>
> *Use when:* Modifying logic, backend scripts, algorithms.

1. **Construct Command**: Create a one-liner test.
    - Python: `python3 -c "from file import func; assert func() == expected"`
    - Script: `python3 .agent/scripts/test_script.py`
2. **Execute**: Use `run_command`.
3. **Analyze**: Did it exit code 0?

### Branch B: Browser / UI Verification
>
> *Use when:* Modifying HTML, CSS, JS, or visible content.

1. **Start Server**: Ensure distinct local server is running (e.g., `python3 -m http.server 8080`).
2. **Launch Agent**: Use `browser_subagent`.
    - **Task**: "Navigate to <http://localhost:8080>. [Perform Action]. Verify [Result]."
    - **Capture**: Take a screenshot of the result.

### Branch C: Documentation / Config Verification
>
> *Use when:* Modifying markdown, configs, or non-executable files.

1. **Validation**: Run specific linters or validators if available.
2. **Visual Check**: Use `cat` or `grep` to confirm key strings are present.

## Phase 3: Reporting

1. **Pass**: "✅ Verification Passed. [Evidence]."
2. **Fail**: "❌ Verification Failed. [Error Log]. Initiating Fix Loop..." -> **Protocol 271 (Update Docs)**.

---

## Auto-Run (Turbo)

// turbo

1. Check for `verify_deployment.py` availability.
2. If available, run: `python3 .agent/scripts/verify_deployment.py --mode=check`
