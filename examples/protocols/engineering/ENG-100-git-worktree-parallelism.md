---
created: 2025-12-18
last_updated: 2026-07-22
---

# Protocol 100: Git Worktree Parallelism

> **Source**: Harvested from r/ClaudeCode (ice9killz, Cal-Culator) + Superpowers blog
> **Status**: REFERENCE (Requires multi-agent tooling)
> **Purpose**: Enable parallel agent execution without branch conflicts

---

## 1. Concept

Git worktrees allow multiple working directories from a single repository, each on a different branch. This enables:

- **Parallel Development**: Multiple agents work simultaneously on different features
- **No Clobbering**: Changes don't interfere with each other
- **Clean Merges**: Each worktree produces isolated commits

---

## 2. Workflow Pattern

### Setup Phase

```bash
# From main repo
git worktree add ../project-feature-auth feature/auth
git worktree add ../project-feature-api feature/api
git worktree add ../project-feature-ui feature/ui
```

### Parallel Execution

```
Agent 1 → ../project-feature-auth/ → works on auth
Agent 2 → ../project-feature-api/ → works on API
Agent 3 → ../project-feature-ui/ → works on UI
```

### Merge Phase

```bash
# Smart merge (sequential, with conflict resolution)
git checkout main
git merge feature/auth
git merge feature/api
git merge feature/ui

# Or create PRs for review
```

---

## 3. Superpowers Implementation

From the Superpowers blog:

1. **Auto-Worktree Creation**: After brainstorm → plan phase, automatically create worktree for task
2. **Subagent Dispatch**: Main agent dispatches tasks to subagents in worktrees
3. **Code Review**: Main agent reviews each subagent's work before accepting
4. **Merge Options**: PR, local merge, or stop

---

## 4. Conflict Resolution Strategies

| Strategy | When to Use |
|----------|-------------|
| **Sequential Merge** | Low-conflict features (different files) |
| **Rebase Before Merge** | High-conflict, need clean history |
| **Smart Merge Agent** | Let an agent resolve conflicts with context |
| **Human Review** | Critical conflicts, architectural decisions |

---

## 5. Current System Limitations

This protocol is **REFERENCE ONLY** because:

1. Current tooling doesn't support spawning parallel Claude instances
2. No built-in subagent orchestration
3. Merge conflict resolution requires human judgment

### Future Integration Points

- When multi-agent support arrives, implement auto-worktree
- Use for long-running background tasks
- Enable for CI/CD pipeline parallelization

---

## 6. Manual Application

Even without automation, the pattern is useful:

1. User manually opens multiple terminals
2. Each terminal runs Claude Code in different worktree
3. User coordinates via CLAUDE.md or shared documentation
4. Manual merge at end

---

## Tagging

# protocol #git #parallelism #multi-agent #reference
