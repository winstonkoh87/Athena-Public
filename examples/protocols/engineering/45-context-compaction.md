---
created: 2025-12-12
last_updated: 2026-01-30
graphrag_extracted: true
---

---description: Mid-session context compression to extend conversations
created: 2025-12-12
last_updated: 2025-12-18
---

# Protocol 45: Context Compaction

> **Source**: Adapted from GPT-5.2 + Claude Opus 4.5 features  
> **Purpose**: Enable long-running tasks by compressing context when approaching limits

---

## Trigger Conditions

Activate context compaction when:

1. Token budget crosses **50%** (100K of 200K)
2. Session has been running for **extended period** (>30 min continuous)
3. About to hit **context wall** in long conversation

---

## Compaction Strategy

### What to PRESERVE (High Signal)

- Active task objectives and decisions made
- Key constraints and requirements
- Current state of implementation
- Critical user preferences surfaced this session
- Unresolved questions

### What to COMPRESS (Medium Signal)

- Intermediate reasoning that led to conclusions
- Multiple drafts/iterations (keep final only)
- Extended research summaries (keep TL;DR)
- Verbose explanations (keep bullet points)

### What to DROP (Low Signal)

- Pleasantries and acknowledgments
- Redundant confirmations
- Superseded information
- Fully resolved sub-tasks

---

## Implementation Methods

### Method 1: Session Summary (Default)

```
At compaction trigger:
1. Generate 500-word session summary
2. Capture: Decisions, State, Next Steps, Open Questions
3. Continue with summary as context base
```

### Method 2: Progressive Offload

```
When token budget >60%:
1. Move completed tasks to session log file
2. Keep only active work in context
3. Reference archived content via file reads if needed
```

### Method 3: Checkpoint System

```
At natural breakpoints:
1. Create checkpoint summary
2. Tag with timestamp and state hash
3. Enable "resume from checkpoint" on next session
```

---

## Integration with Existing Tools

| Tool | Compaction Role |
|------|-----------------|
| `token_budget.py` | Triggers compaction warning |
| `compress_session.py` | Executes log compression |
| `get_latest_session.py` | Loads compressed context on resume |
| `task.md` | Tracks progress through compaction |

---

## Workflow Update

Add to `/start.md`:

```
// turbo
- [ ] If resuming long session, check if compaction beneficial
```

Add to session mid-point:

```
At 50% token budget:
- Offer to compact context ("Want me to summarize and compress?")
- User can accept or decline
```

---

## Example Usage

```
AI: [Internal check] Token budget at 55%. Session running 45 min.

AI: "We've covered a lot of ground. Want me to compress our earlier 
discussion into a summary so we can continue with more room? 
Key decisions will be preserved."

User: "Ya, do it."

AI: [Generates 500-word summary capturing state]
    [Continues with compressed context]
```

---

## Notes

- Compaction is **lossy** — some nuance will be lost
- For critical sessions, prefer **offload to file** over in-context compression
- Always confirm with user before major compaction

---

## Tagging

#protocol #framework #process #45-context-compaction
