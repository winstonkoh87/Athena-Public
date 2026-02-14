---
description: Apply the Diagnostic-First Refactoring protocol to a specific file or module.
---

# /refactor-code — Code Hygiene & Optimization

> **Trigger**: `/refactor-code <filename>`
> **Skill**: [Diagnostic-First Refactoring](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/coding/diagnostic-refactor/SKILL.md)
> **Source**: r/vibecoding pattern.

## Philosophy
>
> **"Measure twice, cut once."**
> We do not blindly refactor. We generate a "Bill of Materials" (Diagnostic Report) first, review the ROI (LOC reduction), and then execute.

## Execution Steps

### Phase 1: The Surgeon's Scan (Diagnosis)

1. **Read Target**: Load the content of the target file.
2. **Invoke Skill**: Use the prompt from `Diagnostic-First Refactoring`.
3. **Generate Report**: Write to `.context/audits/refactor_report_[filename].md`.
    * *Must include*: Dead Code, Complexity, Redundancy, Performance, Modernization.
    * *Must include*: Estimated LOC reduction table.

### Phase 2: The Authorization Gate

1. **Present Summary**: Output the high-level stats (e.g., "Potential to save 150 lines. Complexity reduction: High.").
2. **Ask**: "Review the report at `.context/audits/refactor_report_[filename].md`. Proceed with execution?"

### Phase 3: The Surgical Strike (Execution)

> **Condition**: Only if user replies "Yes" or "Proceed".

1. **Apply Changes**: Edit the file to implement the approved recommendations.
2. **Verify**: Run basic linting/testing if available.
3. **Quicksave**: Log the refactor.

## Tagging

# refactor #code_quality #optimization #vibecoding
