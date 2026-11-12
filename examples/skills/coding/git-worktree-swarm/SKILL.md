---
name: git-worktree-swarm
description: Automates the complex setup of parallel git worktrees for agentic swarms with dependency-aware wave execution.
argument-hint: "deploy <agents> | cleanup | waves"
allowed-tools:
  - Bash
auto-invoke: false
model: default
context_trigger: "worktree, parallel agents, swarm, multi-agent, concurrent development, wave execution"
---

# Git Worktree Swarm Orchestrator

Sets up parallel, isolated git environments so multiple sub-agents can work on the same repository simultaneously without merge conflicts. Uses **wave-based execution** to respect task dependencies.

## Triggers

"swarm", "parallel agents", "setup worktrees", "multi-agent", "wave execution"

## Core Mechanics

### Phase 1: Setup

1. Detect current branch.
2. Spawn `n` temporary worktrees (`.agent-workspace-1`, etc.).
3. Assign tasks to isolated clones.

### Phase 2: Wave Execution (Dependency DAG)

Plans are grouped into **waves** based on dependency analysis:

```
WAVE 1 (parallel — no dependencies)
├── Worktree A: Task 1 (User model)     → Fresh context (P513)
├── Worktree B: Task 2 (Product model)  → Fresh context (P513)
│
[State merge: A.state + B.state → combined handoff]
│
WAVE 2 (parallel — depends on Wave 1)
├── Worktree C: Task 3 (Orders API, needs User model)
├── Worktree D: Task 4 (Cart API, needs Product model)
│
[State merge: C.state + D.state → combined handoff]
│
WAVE 3 (sequential — depends on Wave 2)
└── Worktree E: Task 5 (Checkout UI, needs Orders + Cart)
```

**Wave Assignment Rules**:

| Condition | Assignment |
|---|---|
| Task has no dependencies | Wave 1 |
| Task depends on Wave N output | Wave N+1 |
| Tasks touch the same files | Same wave, sequential (not parallel) |
| Task has cross-cutting concerns | Latest wave of any dependency |

### Phase 3: Context Isolation (P513)

Each worktree agent receives only:

- The specific plan/task
- Relevant source files (from dependency analysis)
- STATE.md (accumulated decisions from prior waves)
- Project context (design.md / REQUIREMENTS.md)

Never: full conversation history, debug logs, unrelated research.

### Phase 4: Merge

1. Each task commits atomically (P43 micro-commit).
2. Merge worktrees back to main branch in wave order.
3. Conflict resolution: if merge conflicts arise, spawn resolution agent.
4. Cleanup: remove temporary worktrees.

## Reference Paths

- [Protocol 513: Context Isolation](../../../protocols/engineering/ENG-513-context-isolation.md)
- [Protocol 43: Micro-Commit](../../../protocols/engineering/ENG-43-micro-commit-protocol.md)
- [Protocol 100: Git Worktree Parallelism](../../../protocols/engineering/ENG-100-git-worktree-parallelism.md)
- [Protocol 409: Parallel Worktree Orchestration](../../../../.framework/v8.2-stable/protocols/409_Parallel_Worktree_Orchestration.md)
