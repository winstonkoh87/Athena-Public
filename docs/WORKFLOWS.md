# Workflows in Project Athena

> **Last Updated**: 19 August 2026

Workflows are slash commands that trigger predefined sequences of actions. They're the backbone of Athena's session management and deep reasoning capabilities.

> **Total**: 72 workflows (54 root + 18 domain-specific in `.agent/workflows/_domain/`)

## Quick Reference

| Command | Purpose | Complexity |
|---------|---------|------------|
| [`/start`](examples/workflows/start.md) | Boot session, load identity | Low |
| [`/end`](examples/workflows/end.md) | Close session, commit to memory | Low |
| [`/tutorial`](examples/workflows/tutorial.md) | Guided first-session walkthrough | Low |
| [`/save`](examples/workflows/save.md) | Mid-session checkpoint | Low |
| [`/think`](examples/workflows/think.md) | Deep reasoning (all phases) | Medium |
| [`/ultrathink`](examples/workflows/ultrathink.md) | Maximum depth (parallel orchestrator) | High |
| [`/search`](examples/workflows/search.md) | Web search with citations | Medium |
| [`/research`](examples/workflows/research.md) | Exhaustive multi-source investigation | High |
| [`/plan`](examples/workflows/plan.md) | Structured planning with pre-mortem | Medium |
| [`/brief`](examples/workflows/brief.md) | Pre-prompt clarification protocol | Medium |
| [`/refactor`](examples/workflows/refactor.md) | Full workspace optimization | High |
| [`/vibe`](examples/workflows/vibe.md) | Ship at 70%, iterate fast | Low |
| [`/deploy`](examples/workflows/deploy.md) | Sanitized public repo sync | Medium |

---

## Core Workflows

### Session Management

| Workflow | When to Use |
|----------|-------------|
| **`/start`** | Beginning of every session. Loads identity, recalls context from previous sessions. |
| **`/end`** | End of every session. Commits insights to memory, updates indexes. |
| **`/tutorial`** | Your very first session. Guided walkthrough of all features, includes profile interview. |
| **`/save`** | Mid-session when you want to checkpoint without closing. Use before risky experiments. |

### Reasoning Depth

| Workflow | Depth | Token Budget | Use Case |
|----------|-------|--------------|----------|
| **`/think`** | High | ~2000 tokens | Important decisions, complex problems |
| **`/ultrathink`** | Maximum | ~5000+ tokens | Life-altering decisions, multi-stakeholder analysis |

> **Rule**: Default to normal mode. Escalate to `/think` for $10K+ decisions. Use `/ultrathink` only for maximum-depth analysis.

### Research & Search

| Workflow | Searches | Sources Read | Depth |
|----------|----------|--------------|-------|
| **`/search`** | 2-3 | 0-2 | Medium |
| **`/research`** | 5-10+ | 3-10+ | Maximum |

> **Triple Crown Mode**: Combine `/think /search /research` for nuclear-level investigation.

---

## Planning Workflows

### `/brief` — Pre-Prompt Clarification

Use `/brief` before complex tasks to clarify requirements:

```
/brief build a dashboard for tracking trading performance
```

Variants:

- `/brief` — Core brief (default)
- `/brief ++` — Expanded fields for complex work
- `/brief build` — Technical implementation tasks
- `/brief research` — Investigation/analysis tasks
- `/brief interview` — Iterative Q&A to extract requirements

### `/plan` — Structured Task Planning

For "Heavy" tasks (new features, refactors, architecture changes):

1. Enter PLANNING mode
2. Generate implementation plan with pre-mortem
3. Review with user before execution
4. Track progress in `task.md`

---

## Maintenance Workflows

### `/refactor` — Full Workspace Optimization

Run periodically to maintain workspace integrity:

```
/refactor          # Full optimization
/refactor --dry-run # Preview changes
```

**Phases**:

1. Diagnostics
2. Pre-remediation checkpoint
3. Fix orphans/broken links
4. Optimization pass
5. Supabase sync
6. Cache refresh
7. Index regeneration
8. Commit

### `/vibe` — Vibe Coding Mode

For rapid iteration:

- Ship at 70% confidence
- Iterate based on feedback
- No over-engineering

**SEO Checklist** (mandatory before deploy):

- [ ] Keyword in H1/Title
- [ ] Internal linking
- [ ] Descriptive URL slug
- [ ] Meta description

---

## Creating Custom Workflows

Workflows live in `.agent/workflows/` as Markdown files:

```yaml
---
description: Short description for the workflow index
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# /command-name — Title

## Behavior

What happens when invoked...

## Phases

Step-by-step execution...

## Tagging

#workflow #automation
```

**Conventions**:

- Use `// turbo` annotation above steps that are safe to auto-run
- Reference other workflows with relative links
- Include rollback instructions for destructive operations

---

## Best Practices

1. **Choose the right depth**: Don't `/ultrathink` on simple queries
2. **Checkpoint often**: Use `/save` before risky experiments
3. **Brief first**: For complex tasks, `/brief` reduces wasted tokens
4. **End sessions properly**: `/end` commits insights to long-term memory
5. **Combine strategically**: `/think /search /research` for maximum coverage

---

## Further Reading

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design
- [GETTING_STARTED.md](docs/GETTING_STARTED.md) — Setup guide
- [examples/protocols/](../examples/protocols/) — Decision frameworks
