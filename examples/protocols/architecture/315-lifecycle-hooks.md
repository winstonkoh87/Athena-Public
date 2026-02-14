---
created: 2026-01-08
last_updated: 2026-01-30
graphrag_extracted: true
---

---id: 315
title: Lifecycle Hooks
category: architecture
tags: [hooks, automation, workflow, architecture]
created: 2026-01-08
source: Claude Code v2.1.0 pattern analysis
last_updated: 2026-01-13
---

# Protocol 315: Lifecycle Hooks

> **Source**: Stolen from Claude Code v2.1.0 hooks architecture

## Overview

Lifecycle hooks are predefined execution points that run automatically at specific stages of a session or operation. They provide **non-invasive extensibility** without modifying core logic.

## Hook Types

| Hook | Trigger | Athena Implementation |
|------|---------|----------------------|
| **PreSession** | Session start | `/start` workflow, `boot.py` |
| **PostExchange** | After each user message | `quicksave.py` (mandatory) |
| **PreOutput** | Before response delivery | Semantic search (mandatory) |
| **PostSession** | Session end | `/end` workflow, `session_archive.py` |
| **OnChange** | File modification detected | `skill_watcher.py` (new) |

## Frontmatter Spec

Workflows and skills can declare hooks in their frontmatter:

```yaml
---
hooks:
  pre: validate_environment.py
  post: cleanup_temp_files.py
once: true  # Run only once per session
---
```

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `hooks.pre` | string | Script to run before execution |
| `hooks.post` | string | Script to run after execution |
| `once` | boolean | If true, hook runs only once per session |

## Once-Only Pattern

For initialization hooks that shouldn't repeat:

```yaml
---
once: true
---
```

Use case: API client initialization, environment validation, one-time cleanup.

## Execution Order

```
┌─────────────────────────────────────┐
│  1. PreSession (boot.py)           │
│  2. Loop:                          │
│     a. PreOutput (semantic search) │
│     b. Compose response            │
│     c. PostExchange (quicksave)    │
│  3. PostSession (session_archive)  │
└─────────────────────────────────────┘
```

## Sandboxed Execution

For high-risk operations, hooks can run in isolated context:

```yaml
---
sandbox: true
---
```

Sandboxed hooks do not persist state to main session. Use for:

- Financial calculations
- Destructive testing
- External API calls with side effects

## Anti-Patterns

- ❌ Hooks that block on user input (breaks automation)
- ❌ Hooks with external dependencies without fallback
- ❌ Nested hooks (hooks calling hooks)

## References

- [/start workflow](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/start.md)
- [/end workflow](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/end.md)
- [quicksave.py](file:///Users/[AUTHOR]/Desktop/Project%20Athena/.agent/scripts/quicksave.py)

---

# protocol #architecture #hooks #automation
