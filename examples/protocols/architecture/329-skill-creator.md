---
created: 2026-01-02
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: skill-creator
description: Meta-skill for creating new Athena skills/protocols. Use when building reusable capabilities, workflows, or specialized knowledge modules.
tags: [meta, skill-creation, protocol, architecture]
created: 2026-01-02
last_updated: 2026-01-02
---

# Skill Creator Protocol

> Adapted from Anthropic's `skill-creator` skill. Integrated 02 January 2026.

---

## Core Principles

### 1. Concise is Key

The context window is a public good. Only add context Claude doesn't already have.

**Challenge each piece**: "Does Claude really need this?" and "Does this justify its token cost?"

Prefer concise examples over verbose explanations.

### 2. Set Appropriate Degrees of Freedom

| Freedom | When to Use | Example |
|---------|-------------|---------|
| 🟢 **High** (text-based) | Multiple approaches valid, context-dependent | Creative writing, design decisions |
| 🟡 **Medium** (pseudocode) | Preferred pattern exists, some variation OK | API integration patterns |
| 🔴 **Low** (specific scripts) | Fragile operations, consistency critical | File format generation, auth flows |

> Think of Claude exploring a path: a narrow bridge needs guardrails (low freedom), an open field allows many routes (high freedom).

---

## Skill Anatomy

```
.agent/skills/
├── capabilities/          # Technical skills (frontend, testing, MCP)
│   └── Skill_Name.md
├── protocols/             # Decision/workflow protocols
│   └── domain/
│       └── XXX-protocol-name.md
└── playbooks/             # Domain-specific guides
    └── Playbook_Name.md
```

### File Structure

```markdown
---
name: skill-name
description: Clear description of what and when
tags: [relevant, tags]
---

# Skill Name

> Source/adaptation note

## Overview
Brief purpose statement.

## Core Content
The actual skill logic, examples, patterns.

## Integration with Athena
- Trigger: "When user says X"
- Artifacts: Where outputs go
- Related: Links to related protocols

## Tagging
#skill #domain #tags
```

---

## 6-Step Skill Creation Process

### Step 1: Understand with Concrete Examples

Ask:

- "What functionality should this skill support?"
- "Give examples of how it would be used"
- "What would a user say to trigger this skill?"

**Exit**: Clear sense of the functionality needed.

### Step 2: Plan Reusable Contents

For each example, analyze:

1. How would I execute this from scratch?
2. What scripts/references/assets would help if done repeatedly?

| Example Query | Analysis | Reusable Asset |
|---------------|----------|----------------|
| "Rotate this PDF" | Same code each time | `scripts/rotate_pdf.py` |
| "Build me a todo app" | Same boilerplate | `assets/hello-world/` template |
| "How many users logged in?" | Same schema discovery | `references/schema.md` |

### Step 3: Initialize the Skill

Create the skill file in the appropriate directory:

- **Capability** → `.agent/skills/capabilities/Skill_Name.md`
- **Protocol** → `.agent/skills/protocols/domain/XXX-name.md`
- **Playbook** → `.agent/skills/playbooks/Playbook_Name.md`

### Step 4: Write the Skill

Implement:

- YAML frontmatter (name, description, tags)
- Core logic/patterns
- Examples (concise > verbose)
- Integration section

### Step 5: Register the Skill

Run:

```bash
python3 .agent/scripts/generate_tag_index.py
```

This auto-updates `TAG_INDEX.md` and `SKILL_INDEX.md`.

### Step 6: Iterate Based on Usage

After real usage:

- Refine based on what works/breaks
- Add edge cases discovered in practice
- Remove unused sections

---

## Integration with Athena

- **Trigger**: "Create a skill for X" or "Make a protocol for Y"
- **Workflow**: Follow 6-step process above
- **Verification**: Run `orphan_detector.py` + `generate_tag_index.py`

---

## Tagging

# skill #meta #protocol-creation #architecture
