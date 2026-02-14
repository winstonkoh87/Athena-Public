---created: 2026-01-02
last_updated: 2026-01-30
---

---description: High-Stakes Documentation Workflow (The Anthropic Method)
created: 2026-01-02
last_updated: 2026-01-02
---

# Document Co-Authoring Workflow

> **Purpose**: Create high-stakes documentation (PRD, RFC, Strategy) using the "Editor vs. Writer" separation of concerns.
> **Source**: Protocol CS-198 (Anthropic Skills)

## Phase 1: Context Gathering (The Dump)

**Step 1: The Brief**
Use `/brief` to trigger the initial interview.

- **Audience**: Who is reading this?
- **Goal**: What is the single outcome?
- **Constraints**: Format, length, tone?

**Step 2: The Context Dump**
> "Dump everything you know about this topic. Paste emails, slack messages, notes. Don't worry about structure."

**Step 3: The Gap Analysis**
Agent asks 5-10 clarifying questions to fill holes in the context.

---

## Phase 2: Structure & Drafting (The Build)

**Step 4: Structure Agreement**
Agent proposes the Table of Contents (ToC).
User approves or modifies.

**Step 5: Sectional Drafting Loop**
For each section:

1. **Agent**: "Brainstorming 5 key points for [Section Name]..."
2. **User**: Selects points to keep/kill.
3. **Agent**: Writes the draft for that section.
4. **User**: Surgical edits (or "LGTM").

---

## Phase 3: The Simulation (Reader Test)

**Step 6: Fresh Eyes Audit**
Agent wipes context (simulated) and reads the fresh draft.

- "Roleplay as [Target Audience]. What is confusing?"
- "Roleplay as [The Skeptic]. What is the weak point?"

**Step 7: Final Polish**
Fix issues found in simulation.
Export to final artifact.
