---

created: 2025-12-20
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-20
last_updated: 2025-12-24
---

# Protocol 130: The Vibe Coding System (System-Assisted Building)

> **Source**: r/vibecoding (User: Tonjiez)
> **Purpose**: High-velocity product building by treating AI as a system component, not just a generator.
> **Philosophy**: "High-level thinking first. Context is King. Docs are for Agents."

---

## Phase 1: High-Level Thinking (The Brief)

**Tool**: Chat Interface (High Reasoning Model)
**Output**: Locked Context

Start every project by defining the "Soul" of the build. Do not write code until this is clear.

1. **What the product is**: One sentence pitch.
2. **What it is not**: Anti-goals (e.g., "Not mobile first," "Not real-time").
3. **Core Flows**: Step-by-step user journey.
4. **Constraints**: Tech stack, budget, time.
5. **Tradeoffs**: Speed vs. Quality, Scale vs. Simplicity.

*Context Lock*: Keep this in the chat history. This prevents "drift" later.

---

## Phase 2: The Workplan (The Architect)

**Tool**: Editor + Reasoning Model
**Action**: Create a blank project. Build a `WORKPLAN.md`.

**Critical Step**: Do not write feature code. Write the *Plan*.
The Workplan must define:

1. **Tech Stack**: Explicit versions.
2. **Data Modeling**: Schemas, entity relationships.
3. **Architecture**: Design patterns, folder structure.
4. **Design System**: Strategy (Tailwind, CSS variables), component hierarchy.
5. **Security**: Auth, RLS, validation rules.
6. **Tests**: Testing strategy.
7. **Docs & Rules**: **CRITICAL**. These are not just for humans; they are "Agent Context."

**Rule**: "Lock the methodology early." (e.g., FSD - Feature Sliced Design, Atomic Design). No mixing.

---

## Phase 3: Foundation (The Big Context Shot)

**Tool**: High Context Model (Opus 4.5/Gemini 3 Pro)
**Action**: Initial Scaffold

1. Feed the *entire* Workplan to the model.
2. Generate the full skeleton/foundation in one shot.
3. **Why**: Reduces rewrites. Ensures consistent patterns across files.
4. **Outcome**: Git commit `feat: initial scaffold`.

---

## Phase 4: The Loop (Layered Execution)

**Tool**: Editor (Cursor) + MCPs

1. **Task Tracking**: Use a task file or Notion MCP to track progress.
2. **Database**: Push migrations directly via tools/MCPs.
3. **Design Loop**:
    * Figma -> Editor.
    * Ensure Figma structure mirrors Code structure (Components).
4. **Iteration**:
    * *Small fixes*: Fast Model (Opus 4.5/Gemini 3 Flash).
    * *Architectural changes*: Reasoning Model (Opus/Gemini Pro/o1).

---

## Phase 4.5: The Anti-Gravity Safety Protocol (Law #1)

**Trigger**: Before any destructive action (DB migration, bulk delete, API write).

**Rule**: AI has **Proposal Rights**, not **Execution Rights** on destructive ops.

1. **The Undo Button**: `git commit` BEFORE allowing AI to touch code.
2. **The Data Lifeboat**: Automated daily backups for Production DB.
3. **The Sandbox**: Never run experimental agent loops on Production data.

> "If you don't commit, you don't have the right to complain when the AI drops your tables."

---

## Phase 5: Deployment

**Tool**: Vercel/Deploy MCP

* Deploy early.
* Automate the pipeline.

---

## Key Principles

1. **Docs = Agent Constraints**. Writing good documentation is prompt engineering for your future agent interactions.
2. **One Context Container**. Keep the vision in one high-context thread/file.
3. **Plan Mode > Edit Mode**. Spending 20 mins planning saves 2 hours of "nannying" the AI.

## Tagging

# coding #workflow #architecture #vibecoding #productivity
