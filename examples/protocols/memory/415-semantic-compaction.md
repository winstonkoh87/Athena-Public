---
description: "Compress completed tasks into semantic summaries to preserve context window."
created: 2026-02-11
source: "Steal from Beads (Steve Yegge)"
---

# Protocol 415: Semantic Compaction (The O(1) Context Law)

> **Philosophy**: Completed tasks are "Dead Context." They should not occupy "Live RAM" (Active Context). They should be compressed into "ROM" (Semantic Summary) or archived to "Disk" (Session Logs).

## 1. The Physics of Decay

- **Linear Growth**: Without compaction, `activeContext.md` grows O(N) with every task completed.
- **Context Pollution**: Old tasks (`[x] Setup Env`) distract the LLM from current tasks.
- **The Ideal State**: The Context Window should only contain **Active Constraints** and **Current Objectives**.

## 2. The Compaction Logic

| State | Definition | Action |
| :--- | :--- | :--- |
| **Active** | `[ ] Task A` | Keep in `activeContext.md`. |
| **Freshly Done** | `[x] Task A` (Last 3) | Keep in `activeContext.md` as "Recent Momentum". |
| **Stale Done** | `[x] Task A` (>3 items ago) | **COMPACT** -> Semantic Summary / Archive. |

## 3. Execution (The Script)

Run `.agent/scripts/compact_context.py` to:

1. **Scan** `activeContext.md` for the `## Active Tasks` section.
2. **Count** `[x]` items.
3. **If > 3**:
    - Move the oldest `[x]` items to a `## Session Compaction` or `## Recent History` section, purely as a summarized line (e.g., "Phase 1 Complete").
    - OR, better yet, **Archive** them to the daily session log and delete them from `activeContext.md`, replacing with a high-level summary bullet.

## 4. The Rules

1. **Never Delete Without Trace**: Always ensure the item exists in `session_logs` before removing from `activeContext`.
2. **Summarize, Don't Just Delete**: Replace 10 micro-tasks with 1 macro-accomplishment.
    - *Before*: `[x] Install updates`, `[x] Fix typos`, `[x] Git push`...
    - *After*: `[x] Maintenance Sweep (Updates + Fixes)`
3. **Preserve Momentum**: Keep the last 3 checks visible so the user feels progress.

---
**Tags**: #protocol #ai #productivity #context-management #semantic-compaction #llm-optimization #automation
