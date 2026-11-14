# Skills Directory

This directory contains reusable AI skills that extend agent capabilities. Each skill is a self-contained instruction set that teaches your AI agent a specialized workflow.

## Available Skills

```
skills/
├── coding/
│   ├── diagnostic-refactor/   # Diagnose code issues before editing
│   └── spec-driven-dev/       # Build a design spec before writing code
├── decision/
│   └── mcda-solver/           # Multi-criteria decision matrix calculator
├── quality/
│   └── red-team-review/       # Adversarial QA review for any artifact
├── research/
│   └── deep-research-loop/    # Structured multi-source research workflow
└── workflow/
    └── context-compactor/     # Compress context to stay within token limits
```

## What is a Skill?

A **skill** is a specialized prompt pattern + workflow that teaches an AI agent how to perform a specific task well. Each skill contains:

- `SKILL.md` — Main instruction file with the prompt and execution workflow
- Optional: scripts, examples, templates

## Quick Start

### For Antigravity Users

Skills in `.agent/skills/` are auto-detected. To use these templates:

```bash
# Copy a skill template into your workspace
cp -r examples/skills/coding/spec-driven-dev .agent/skills/

# The skill is now available to your agent automatically
```

### For Other IDEs

1. Read the `SKILL.md` file for the skill you want to use
2. Follow the execution workflow described
3. The AI will produce output in the specified format

## Creating Your Own Skills

Every skill follows this structure:

```yaml
---
name: my-custom-skill
description: One-line description of what this skill does
argument-hint: "trigger phrase | alternative trigger"
auto-invoke: false          # true = auto-load on context match, false = user-invoked only
model: default              # model override when skill is active
user-invocable: true        # false = background knowledge only, hidden from slash menu
allowed-tools:              # tools allowed without permission prompts
  - Read
  - Bash
---

# Skill Title

## Triggers
[Keywords and phrases that activate this skill]

## Execution Workflow
[Step-by-step instructions]

## Output Format
[Expected output structure]
```

### Frontmatter Reference

| Field | Required | Description |
|:------|:---------|:------------|
| `name` | Yes | Skill identifier and `/slash-command` |
| `description` | Yes | When to invoke (used for auto-discovery) |
| `argument-hint` | No | Autocomplete hint (e.g., `[issue-number]`) |
| `auto-invoke` | No | `true` to auto-load on context match (default: `false`) |
| `model` | No | Model override when skill is active (default: `default`) |
| `user-invocable` | No | Set `false` to hide from slash menu (default: `true`) |
| `allowed-tools` | No | Tools allowed without permission prompts |

### Auto-Invoke Guidelines

Set `auto-invoke: true` for skills that should activate automatically when the conversation matches their domain:

- **Safety gates** (circuit-breaker, law-of-ruin) — must auto-invoke to enforce constraints
- **Analysis tools** (kelly-mandate, base-rate-audit) — auto-invoke enriches responses transparently
- **User-invoked only** (marketing-swarm, git-worktree-swarm) — heavyweight workflows that should only run on explicit command

> [!IMPORTANT]
> **`auto-invoke: true` is a request, not a mechanism.** Frontmatter is prose — the model *chooses* whether to honor it, and in practice it fails most often on exactly the prompts that matter (emotionally-loaded or high-stakes contexts). If a skill genuinely must fire deterministically, wire a **hook**: see [`examples/hooks/meta_awareness_gate.py`](../hooks/meta_awareness_gate.py) for a code-enforced `UserPromptSubmit` trigger that injects the skill's gate into context regardless of model discretion. Epistemic statuses: `code-enforced` (a hook/script runs it) vs `agent-discretion` (the model must remember). Label your skills honestly — a safety gate that is only `agent-discretion` is not a gate.

See [CONTRIBUTING.md](../../.github/CONTRIBUTING.md) for guidelines on adding new skills.
