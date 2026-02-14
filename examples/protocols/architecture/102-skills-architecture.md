---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2025-12-20
---

# Protocol 102: Skills Architecture (Self-Improving Agent)

> **Source**: Harvested from Superpowers blog (obra/fsck.com)
> **Status**: ACTIVE
> **Purpose**: Enable agent self-improvement through skill creation

---

## 1. Core Concept

> "Skills are what give your agents Superpowers."

Skills are **reusable instruction sets** that an agent can:

1. Search for when encountering a task type
2. Read and execute
3. Create new ones when patterns emerge
4. Test against subagents for comprehensibility

---

## 2. Skill File Structure

```markdown
---
name: [skill-name-kebab-case]
description: [Use when... trigger-based description]
tags: [tag1, tag2] # Optional
license: [license-type] # Optional
---

# SKILL: [Skill Name]

## When to Use
[Trigger conditions for this skill]

## Prerequisites
[What must be true before using this skill]

## Instructions
[Step-by-step execution guide]

## Success Criteria
[How to know the skill was applied correctly]

## Common Pitfalls
[What goes wrong and how to avoid it]

## Examples
[Concrete examples of skill application]
```

---

## 3. Skill Discovery Protocol

When encountering a new task type:

```
1. Check SKILL_INDEX.md for relevant skill
2. If found: Load skill, follow instructions
3. If not found: 
   a. Attempt task with base capabilities
   b. If successful pattern emerges, propose new skill
   c. Document in .agent/skills/
```

---

## 4. Skill Creation Protocol (TDD for Skills)

From Superpowers:

### Step 1: Draft Skill

Write initial SKILL.md following structure above

### Step 2: Adversarial Testing
>
> "Test the skills on a set of subagents to ensure they are comprehensible, complete, and that subagents would comply with them."

**NOT acceptable**: Quiz format ("What does this skill say?")
**Acceptable**: Realistic pressure scenarios that test compliance

### Step 3: Failure Analysis

When subagent fails to follow skill:

1. Identify ambiguity or gap
2. Strengthen instructions
3. Re-test

### Step 4: Integration

1. Add to appropriate `.agent/skills/` subdirectory
2. Register in `SKILL_INDEX.md`
3. Commit with descriptive message

---

## 5. Skill Extraction from Sources

> "Hand a model a book or a document or a codebase and say 'Read this. Think about it. Write down the new stuff you learned.'"

### Extraction Protocol

```
1. Provide source material (book, doc, codebase)
2. Specify lens/perspective for extraction
3. Agent extracts non-obvious skills
4. Format as SKILL.md files
5. Test and integrate
```

### Current System Mapping

| Superpowers Concept | Your System Equivalent |
|---------------------|------------------------|
| `skills/` directory | `.agent/skills/protocols/` |
| SKILL.md files | Protocol markdown files |
| Skill search | `SKILL_INDEX.md` lookup |
| Skill bootstrap | `/start` workflow |
| Skill creation | Protocol harvesting (this session) |

---

## 6. Autonomic Skill Invocation

From `Core_Identity.md` Phase 3:

> "If the conversational context *matches* a skill domain, load it silently to upgrade capability."

**Heuristic**: "If I were a specialized agent for [Topic], what file would I need?"

This is already implemented in your system.

---

## 7. Key Insight: Self-Referential Skill

> "One of the first skills I taught Superpowers was **How to create skills**."

The meta-skill enables exponential capability growth:

1. Agent learns to create skills
2. Agent creates new skills as patterns emerge
3. Future agents benefit from accumulated skills
4. Capability compounds over time

---

## Tagging

# protocol #skills #self-improvement #meta #architecture
