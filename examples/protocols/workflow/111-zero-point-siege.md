---
type: protocol
id: 111
title: Zero-Point Siege
created: 2026-02-14
source: Manus Agent Loop Discipline
tags: [workflow, safety, robustness, siege]
author: Athena (via Manus)
---

## Protocol 111: Zero-Point Siege

> **Philosophy**: "Under high uncertainty, speed is a liability. Precision is the only exit."
> **Origin**: Adapted from **Manus** (The Agentic Loop Discipline).
> **Purpose**: To enforce maximum robustness for critical or multi-stage tasks where errors are costly.

## 1. Trigger Conditions

Switch to **Siege Mode** when:

- **Low Confidence**: `confidence < 0.4`.
- **High Risk**: Task involves data deletion, production deployment, or financial transactions.
- **Complex Environment**: Task involves unfamiliar tools or codebases.
- **Recovery Mode**: Task is initiated to fix a previous agent failure.

## 2. The Siege Rule: One-Tool-Constraint

During a Siege, the Agent MUST NOT call more than **ONE** tool per iteration.

- **Reasoning**: To prevent "Action Chains" from drifting away from the objective without validation.
- **Action**: Call tool -> Stop -> Inspect Output -> Re-evaluate State.

## 3. The Siege Workflow

1. **State Inspection**: Mandatory `ls` or `view_file` after any edit.
2. **Explicit Reasoning**: Before the next tool call, the agent must write a 1-sentence "Diagnostic" of the previous tool's outcome.
3. **Circuit Breaker**: If two consecutive tools fail, the agent MUST call `/think` or ask the user for clarification before the 3rd attempt.

## 4. Siege vs. Flow

| Feature | **Flow Mode** (Default) | **Siege Mode** (Protocol 111) |
| :--- | :--- | :--- |
| **Tool Parallelism** | Enabled (Multi-call) | **Disabled** (Single-call) |
| **Validation** | Post-task | **Post-step** |
| **Identity** | High-Agency Operator | **Defensive Auditor** |
| **Best For** | Routine coding, research | **Fixing bugs, migrations, deployments** |

## 5. Enforcement

When in Siege Mode, the agent should prepend its responses with `[SIEGE]` to signal a shift in operating physics.
