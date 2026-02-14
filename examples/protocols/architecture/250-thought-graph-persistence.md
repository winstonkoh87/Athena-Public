---

created: 2026-01-03
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-03
last_updated: 2026-01-03
---

# Protocol 250: Thought Graph Persistence (v2.1)
>
> **Version**: 2.1 (Stability Patch)
> **Created**: 2026-01-03
> **Tags**: #architecture #persistence #state-management #ultrathink

---

## 1. Philosophy

> "Thinking is a process. State is a snapshot. To pause the process, you must serialize the state."

In "Layer 5" recursive reasoning (`/ultrathink`), the AI operates beyond the stateless request/response cycle. To enable **Long-Horizon Thinking** and **Convergence Detection**, we must persist the "Thought Graph" to the filesystem, keyed by the unique session.

---

## 2. Schema Definition (`thought_graph_{session_id}.json`)

The state is stored in `.context/state/thought_graph_{session_id}.json`.

```json
{
  "session_id": "2026-01-03-session-03",
  "root_problem": "Should I emigrate to Portugal?",
  "status": "RUNNING", 
  "depth_current": 45,
  "depth_max": 999,
  "budget_used_tokens": 154200,
  "nodes": [
    {
      "id": "node_45",
      "type": "SYNTHESIS",
      "content": "Portugal D7 requires €9,840 passive income.",
      "entropy_score": 0.04, // Used for Boredom Heuristic
      "meta": {
        "variance_delta": -0.01 // Change from previous node
      }
    }
  ],
  "checkpoints": [
    { 
      "step": 10, 
      "summary": "Confirmed visa requirements. Moved to tax analysis." 
    }
  ]
}
```

---

## 3. The Boredom Heuristic (Convergence Logic)

> **Purpose**: Prevent infinite loops without imposing arbitrary "depth limits."

**Formula**:
If `Variance(last_3_nodes) < 0.05` (5% change), trigger **CONVERGENCE**.

**Pseudocode**:

```python
def check_boredom(graph):
    last_3 = graph.nodes[-3:]
    # If the AI is repeating itself or making negligible progress
    if similarity(last_3[0], last_3[1]) > 0.95 AND similarity(last_3[1], last_3[2]) > 0.95:
        return True # Stop, we are bored.
    return False
```

---

## 4. Rolling Summaries (Compression)

> **Purpose**: Prevent context window overflow during deep recursion.

**Rule**: Every 10 steps, compress the last 10 nodes into a single `CHECKPOINT` entry.

- **Action**: Summarize nodes [N-10] to [N].
- **Store**: Add to `checkpoints` array.
- **Prune**: Remove raw nodes [N-10] to [N] from active memory (keep on disk).

---

## 5. Implementation Steps

1. **Initialize**: Create `thought_graph_{session_id}.json`.
2. **Update**: Append nodes after every Phase.
3. **Check**: Run `check_boredom()`.
    - If `True` -> Trigger Phase 4 (Synthesis).
    - If `False` -> Continue Phase 3 (Loop).

---

## Tagging

# protocol #persistence #json #state-machine
