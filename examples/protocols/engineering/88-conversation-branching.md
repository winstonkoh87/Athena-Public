---

created: 2025-12-16
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-16
last_updated: 2025-12-18
---

# Protocol 88: Conversation Branching

> **Source**: Harvested from `ykdojo/claude-code-tips` (Dec 2025)
> **Use Case**: A/B testing strategies, trying different approaches without losing original thread

---

## Core Concept

Sometimes you want to explore a different direction from a specific point in a conversation without losing your original thread.

**Analogy**: Git branches for conversations.

---

## When to Use

| Scenario | Branch? |
|----------|---------|
| Testing two different strategies | ✅ Yes |
| "What if" exploration | ✅ Yes |
| Risky approach you might abandon | ✅ Yes |
| Linear task completion | ❌ No |
| Simple Q&A | ❌ No |

---

## Implementation Methods

### Method 1: Session Log Fork

1. At decision point, create checkpoint in session log
2. Note the exact state (files, decisions, context)
3. Continue with Approach A
4. If needed, restore to checkpoint and try Approach B

**File Pattern**:

```
session_logs/
├── 2025-12-16-session-08.md        (main)
├── 2025-12-16-session-08-fork-a.md (branch)
└── 2025-12-16-session-08-fork-b.md (branch)
```

### Method 2: Handoff Document Snapshot

1. Create HANDOFF.md at decision point
2. Start fresh conversation for Branch A
3. When done, return to original HANDOFF.md for Branch B

### Method 3: Parallel Sessions

1. Run two AI sessions simultaneously
2. Give each the same starting context
3. Direct each down different paths
4. Compare results

---

## Merge Strategy

After exploring branches:

1. **Winner-takes-all**: Pick best approach, discard other
2. **Cherry-pick**: Extract valuable insights from both
3. **Synthesize**: Combine elements into hybrid approach

---

## Branch Tracking Format

```markdown
## Branch Point: [TIMESTAMP]

**Decision**: [What choice are we testing?]

| Branch | Approach | Outcome |
|--------|----------|---------|
| A | [Strategy A] | [Result] |
| B | [Strategy B] | [Result] |

**Winner**: [A/B/Hybrid]
**Reasoning**: [Why]
```

---

## Anti-Patterns

| Bad | Good |
|-----|------|
| Branching every minor decision | Branch only at major forks |
| Forgetting to document branch point | Always checkpoint before branch |
| Running 5+ parallel branches | Max 2-3 branches |

---

## Integration

- Works with: Protocol 85 (Token Hygiene — fresh context for each branch)
- Complements: Session Logs (checkpointing mechanism)

---

## Tags

# branching #exploration #strategy #a-b-testing #harvested

---

## Tagging

#protocol #framework #88-conversation-branching
