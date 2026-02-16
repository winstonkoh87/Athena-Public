---
protocol_id: 409
title: "Parallel Worktree Orchestration"
version: "1.0"
status: ACTIVE
created: 2026-02-02
source: "Maestro (its-maestro-baby/maestro)"
category: orchestration
---

# Protocol 409: Parallel Worktree Orchestration

> **Origin**: Stolen from Maestro's git worktree isolation pattern
> **Purpose**: Run multiple AI sessions on the same codebase without merge conflicts

---

## Context

When running multiple AI coding sessions in parallel (e.g., 2-4 Antigravity instances), they may conflict if editing the same files or branch. Git worktrees provide **complete isolation** — each session gets its own working directory.

## Implementation

### 1. Worktree Creation

```bash
# Create a worktree for session N
.agent/scripts/parallel_session.sh create $SESSION_ID

# Under the hood:
git worktree add ../.worktrees/session-$SESSION_ID -b feature/session-$SESSION_ID
```

### 2. Directory Structure

```
project-root/
├── .git/                          # Main git directory
├── .worktrees/                    # Worktree base (gitignored)
│   ├── session-1/                 # Agent 1's isolated copy
│   │   └── (full repo clone)
│   ├── session-2/                 # Agent 2's isolated copy
│   └── session-3/                 # Agent 3's isolated copy
└── (main working directory)       # Your primary checkout
```

### 3. Merge Workflow

```bash
# When session completes:
cd ../.worktrees/session-$SESSION_ID
git add -A
git commit -m "Session $SESSION_ID complete"
git push origin feature/session-$SESSION_ID

# Open PR or rebase onto main
git checkout main
git merge feature/session-$SESSION_ID
```

### 4. Cleanup

```bash
# Remove worktree when done
git worktree remove ../.worktrees/session-$SESSION_ID
git branch -d feature/session-$SESSION_ID
```

## Activation Trigger

- User runs multiple AI sessions (`maestro` mode)
- High-complexity parallel decomposition detected
- User explicitly requests worktree isolation

## Anti-Patterns

- ❌ Do NOT use worktrees for sequential work
- ❌ Do NOT create worktrees without explicit user request
- ❌ Do NOT auto-merge worktrees (user must approve)

## Related Protocols

- Protocol 413 (Multi-Agent Coordination)
- Protocol 410 (Agent Status Broadcasting)

---

## Script: `parallel_session.sh`

```bash
#!/bin/bash
# .agent/scripts/parallel_session.sh

set -e

ACTION=$1
SESSION_ID=${2:-$(date +%s)}
WORKTREE_BASE="../.worktrees"

case $ACTION in
  create)
    mkdir -p "$WORKTREE_BASE"
    git worktree add "$WORKTREE_BASE/session-$SESSION_ID" -b "feature/session-$SESSION_ID"
    echo "✅ Created worktree: $WORKTREE_BASE/session-$SESSION_ID"
    echo "📍 Branch: feature/session-$SESSION_ID"
    ;;
  
  list)
    git worktree list
    ;;
  
  remove)
    git worktree remove "$WORKTREE_BASE/session-$SESSION_ID" --force
    git branch -D "feature/session-$SESSION_ID" 2>/dev/null || true
    echo "🗑️  Removed worktree and branch for session-$SESSION_ID"
    ;;
  
  *)
    echo "Usage: parallel_session.sh {create|list|remove} [session_id]"
    exit 1
    ;;
esac
```

---

# protocol #orchestration #parallel #worktree #stolen/maestro
