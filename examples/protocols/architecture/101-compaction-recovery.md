---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2026-01-11
---

# Protocol 101: Compaction Recovery (Transcript Archaeology)

> **Source**: Harvested from r/ClaudeCode (AVanWithAPlan)
> **Status**: REFERENCE (Requires transcript access)
> **Purpose**: Detect and recover information lost during context compaction

---

## 1. Problem Statement

Context compaction creates **discontinuities**:

- Pre-compaction: Rich, nuanced understanding
- Compaction summary: Lossy compression
- Post-compaction: Missing critical details

The user often doesn't notice what was lost until much later.

---

## 2. Ideal System (AVanWithAPlan's Vision)

### Transcript Analysis

```
1. Parse full transcript (can be 10s-100s of millions of tokens)
2. Detect all compaction events
3. Compare pre/post compaction state
4. Rate information loss for each compaction
5. Generate bespoke summary of lost information
```

### Compaction Recovery

```
1. Before compaction: Snapshot critical state
2. After compaction: Analyze what summary missed
3. Inject recovered information into context
4. User/agent sees no discontinuity
```

### Cross-Session Search

```
1. Index all transcripts (including subagent transcripts)
2. Query: "Where did we discuss X?"
3. Return: Location + surrounding context summary
4. Use subagent to search (avoid polluting main context)
```

---

## 3. Current System Approximation

Without transcript access, we approximate with:

| Ideal Feature | Current Approximation |
|---------------|----------------------|
| Transcript analysis | Session logs with checkpoints |
| Compaction detection | STATE FREEZE protocol (Development Execution Standard) |
| Cross-session search | `get_latest_session.py` + manual review |
| Recovery injection | Load session log on `/start` |

---

## 4. Superpowers "Memories" System

From the blog:

1. **Transcript Duplication**: Copy transcripts outside `.claude` (prevents auto-deletion)
2. **Vector Indexing**: SQLite + vector embeddings for semantic search
3. **Summary Generation**: Claude Haiku summarizes each conversation
4. **Search Tool**: CLI tool for agents to search past memories
5. **Subagent Search**: Main agent delegates search to subagent (avoids context pollution)

### Key Insight
>
> "To ensure that fruitless searches don't pollute the context window, the skill explains that Claude needs to use a subagent to do the searching."

---

## 5. Implementation Roadmap

### Phase 1 (Current): Manual Checkpoints

- [x] Session logs with checkpoints
- [x] STATE FREEZE protocol
- [x] `get_latest_session.py`

### Phase 2 (Near-term): Enhanced Logging

- [ ] Auto-checkpoint on volume/depth triggers
- [ ] Structured state snapshots
- [ ] Pre-compaction freeze automation

### Phase 3 (Future): Full Recovery

- [ ] Transcript parser
- [ ] Compaction event detector
- [ ] Vector indexing for past sessions
- [ ] Subagent search delegation

---

## 6. Discontinuity Detection Heuristics

Signs that compaction lost critical information:

| Signal | Implication |
|--------|-------------|
| Agent asks question already answered | Memory loss |
| Agent contradicts earlier decision | Decision lost |
| Agent repeats completed work | Progress lost |
| Agent forgets constraint | Constraint lost |
| User says "I already told you" | General memory loss |

### Recovery Action

When discontinuity detected:

1. Check session log for relevant STATE FREEZE
2. Check previous session logs
3. Ask user to re-state if not found
4. Document gap for post-session review

---

## Tagging

# protocol #context-management #compaction #recovery #reference
