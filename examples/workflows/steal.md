---created: 2025-12-22
last_updated: 2026-01-30
---

---description: Analyze external content for patterns worth integrating into Athena
created: 2025-12-22
last_updated: 2026-01-11
---

# /steal — Pattern Extraction & Integration

> **Philosophy**: Action over documentation. If it doesn't improve the workspace, skip it.

## Trigger

User provides external content (article, GitHub repo, code, framework, Reddit post, etc.) with `/steal` command.

## Execution Flow

1. **Analyze** the provided content for:
   - Code patterns worth stealing
   - Workflow improvements
   - New protocols/skills
   - Architectural patterns

2. **Triage** using this matrix:

   | Value Level | Action |
   |-------------|--------|
   | **High** — New capability or significant improvement | Integrate immediately (create script/protocol/workflow) |
   | **Medium** — Useful pattern, not urgent | Note in response, offer to integrate |
   | **Low** — Interesting but already exists or not applicable | "Nothing to steal" — move on |
   | **Zero** — No value | Silent acknowledgment, no artifacts |

3. **Integration Types** (if High/Medium):
   - **Code pattern** → Create script in `.agent/scripts/`
   - **Workflow pattern** → Create/update workflow in `.agent/workflows/`
   - **Protocol/skill** → Create in `.agent/skills/protocols/`
   - **Business insight** → Add to `System_Principles.md` or case study

4. **Output**:
   - If integrating: One-liner summary of what was added/changed
   - If nothing: "Nothing to steal" or brief explanation why

5. **Pattern Harvesting (Meta-Observation)**:
   When analyzing AI-generated content or observing AI reasoning traces:
   - Study search patterns (parallel vs sequential, keyword choices)
   - Note reasoning structures (how it decomposes problems)
   - Observe tool use patterns (when it chooses which tools)
   - Extract heuristics that could become protocols

   > "How did the AI solve this? Can I steal that pattern?"

## Anti-Patterns

- ❌ Create documentation-only artifacts
- ❌ Write case studies for marginal insights
- ❌ Over-analyze when the answer is "nothing"
- ❌ Ask for clarification when content is clearly low-value

## Tagging

# workflow #automation #steal #integration
