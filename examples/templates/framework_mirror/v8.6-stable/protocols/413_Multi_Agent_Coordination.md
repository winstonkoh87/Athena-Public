---
protocol_id: 413
title: "Multi-Agent Coordination"
version: "1.0"
status: ACTIVE
created: 2026-02-02
source: "OpenClaw (openclaw/openclaw)"
category: orchestration
---

# Protocol 413: Multi-Agent Coordination

> **Origin**: Stolen from OpenClaw's multi-agent safety guards
> **Purpose**: Prevent conflicts when multiple AI agents work on the same repository

---

## Context

When running multiple Antigravity/Claude/Cursor sessions on the same codebase:

- Git state can conflict (stash, branches, worktrees)
- Files may be edited simultaneously
- Commits may overlap

**This protocol defines safety guards.**

## Multi-Agent Safety Rules

### ❌ NEVER Do Without Explicit Request

| Action | Risk | Mitigation |
|--------|------|------------|
| `git stash` create/apply/drop | Other agent's WIP lost | Use worktrees instead (Protocol 409) |
| `git checkout <branch>` | Breaks other agent's file state | Stay on assigned branch |
| `git worktree add/remove` | May remove other agent's workspace | Coordinate via status file |
| `git pull --rebase --autostash` | Silent stash = data loss | Use explicit `git pull --rebase` only |
| Modify `.git/` internals | Corrupts shared state | Never touch |

### ✅ Safe Operations

| Action | Notes |
|--------|-------|
| `git status` | Always safe |
| `git diff` | Always safe |
| `git log` | Always safe |
| `git add <specific files>` | Scope to YOUR changes |
| `git commit` on designated branch | Only YOUR files |
| `git push` | Always `pull --rebase` first |

## Commit Semantics

| User Says | Agent Behavior |
|-----------|----------------|
| "commit" | Commit only YOUR changed files (use `git add -p` if needed) |
| "commit all" | Commit everything, but in grouped logical chunks |
| "push" | `git pull --rebase` first, then push |
| "push all" | Same, but force push iff explicitly confirmed |

## Parallel Detection

Before any destructive git operation, check:

```bash
# Check for active agents
if [ -f ~/.athena/agent_status.json ]; then
  ACTIVE=$(jq -r 'select(.status == "working")' ~/.athena/agent_status.json)
  if [ -n "$ACTIVE" ]; then
    echo "⚠️  Other agents are active. Coordination required."
  fi
fi
```

## Agent Lock File

For critical operations, use a lock:

```python
# .athena/agent_lock.json
{
  "holder": "antigravity-001",
  "operation": "git rebase",
  "acquired_at": "2026-02-02T23:15:00+08:00",
  "expires_at": "2026-02-02T23:20:00+08:00"
}
```

## Integration with Core_Identity.md

Add to Section 4.1 (Bionic Operational Physics):

```markdown
7. **Multi-Agent Safety (Protocol 413)**: When parallel agents detected:
   - NEVER create/apply/drop git stash
   - NEVER switch branches without explicit request
   - NEVER touch other agents' worktrees
   - "commit" = YOUR changes only
   - "push" = always `git pull --rebase` first
```

## Conflict Resolution

If conflict detected:

1. Stop immediately
2. Report conflict to user via status
3. Wait for explicit resolution instruction
4. Never auto-resolve merges

## Related Protocols

- Protocol 409 (Parallel Worktree Orchestration)
- Protocol 410 (Agent Status Broadcasting)

---

# protocol #orchestration #multi-agent #coordination #stolen/openclaw
