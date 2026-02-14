---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2026-01-02
---

# Protocol 98: State Freezer (Anti-Compaction)

> **Source**: Harvested from r/ClaudeCode (Main_Payment_6430)
> **Status**: ACTIVE
> **Purpose**: Prevent critical state loss during context compaction

---

## 1. Problem Statement

Context compaction ("compact death scythe") destroys nuanced state. The summary often loses:

- Specific constraints mentioned early in conversation
- Architectural decisions and their rationale
- User preferences stated once and assumed thereafter
- Active plan phase and remaining tasks

---

## 2. Solution: Pre-Compaction Snapshot

### Trigger Conditions

Execute State Freeze when ANY of:

1. Context window > 80% capacity
2. Before `/end` or session close
3. User explicitly requests checkpoint
4. Before experimental/risky operations
5. Major topic pivot detected

### Freeze Payload Structure

```markdown
## STATE FREEZE [YYYY-MM-DD HH:MM SGT]

### Active Plan
- Current phase: [PLANNING/EXECUTION/VERIFICATION]
- Current task: [specific task from task.md]
- Remaining: [bullet list of uncompleted items]

### Critical Constraints
- [User-specified constraint 1]
- [User-specified constraint 2]

### Architectural Decisions Made
- [Decision 1]: [rationale]
- [Decision 2]: [rationale]

### User Preferences This Session
- [Preference 1]
- [Preference 2]

### Do NOT Forget
- [Absolutely critical item 1]
- [Absolutely critical item 2]
```

---

## 3. Execution Protocol

### Pre-Compaction (Proactive)

1. Detect compaction approaching (context > 80%)
2. Generate Freeze Payload
3. Write to session log with `## STATE FREEZE` header
4. Continue work

### Post-Compaction (Recovery)

1. On session start, check for recent STATE FREEZE in session log
2. Load Freeze Payload into context
3. Announce: "State recovered from freeze point [timestamp]"

---

## 4. Autonomic Behavior

This protocol runs **implicitly**. User sees outcome, not process.

- **No Permission Required**: Creating freeze, writing to session log
- **Permission Required**: None (this is safety infrastructure)

---

## 5. Integration Points

| Trigger | Action |
|---------|--------|
| `/start` | Check for recent freeze, inject if found |
| `/save` | Force immediate freeze |
| `/end` | Force immediate freeze before close |
| Context > 80% | Auto-freeze |

---

## Tagging

# protocol #context-management #anti-compaction #state-preservation
