---
type: protocol
id: 900
title: Project Scaffolding Standards (Claude Code V4)
created: 2026-01-30
tags: [coding, standards, setup]
last_updated: 2026-01-30
graphrag_extracted: true
---

# Protocol 900: Project Scaffolding Standards

> **Source**: The Complete Guide to Claude Code V4 (Part 2)
> **Purpose**: Prevent scope creep and maintain architectural intent by enforcing a standardized project structure.

## 1. Required Files (The Core 4)

Every new project MUST contain:

1. `.env` (Managed by `.gitignore`, NEVER committed)
2. `.env.example` (Template with placeholders)
3. `.gitignore` (Must exclude `.env`, `node_modules/`, `dist/`, `__pycache__/`)
4. `CLAUDE.md` (Project overview and architectural rules)

## 2. Directory Structure

Standard layout for modular codebases:

```text
project/
├── src/            # Source code
├── tests/          # Unit and integration tests
├── docs/           # Documentation
├── .agent/         # Agent configuration (local overrides)
│   ├── skills/
│   ├── agents/
│   └── scripts/
└── scripts/        # Human-runnable scripts
```

## 3. Node.js Specifics

If the project is Node.js, the entry point MUST handle unhandled rejections:

```javascript
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  process.exit(1);
});
```

## 4. Initialization Checklist

- [ ] Create `.gitignore` first.
- [ ] Initialize git repo.
- [ ] Create `README.md` with "Goal" and "Stack".
- [ ] Create `CLAUDE.md` with project context.
