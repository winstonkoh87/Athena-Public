---
protocol_id: 410
title: "Agent Status Broadcasting"
version: "1.0"
status: ACTIVE
created: 2026-02-02
source: "Maestro (its-maestro-baby/maestro)"
category: observability
---

# Protocol 410: Agent Status Broadcasting

> **Origin**: Stolen from Maestro's MCP status polling pattern
> **Purpose**: Real-time visibility into agent state for orchestration and UI

---

## Context

When running multiple agents, the orchestrator needs to know each agent's state:

- Are they working or idle?
- Do they need user input?
- Have they encountered an error?

## Status States

| State | Description | Example |
|-------|-------------|---------|
| `idle` | Agent waiting for next task | Between tasks |
| `working` | Actively processing | Editing files, running commands |
| `needs_input` | Blocked on user | Needs clarification, approval |
| `finished` | Task complete | Ready for review |
| `error` | Unrecoverable failure | Crash, API error |

## Implementation

### 1. Status File

Each agent writes to `.athena/agent_status.json`:

```json
{
  "session_id": "2026-02-02-session-10",
  "agent_id": "antigravity-001",
  "status": "working",
  "current_task": "Implementing Protocol 409",
  "updated_at": "2026-02-02T23:08:45+08:00",
  "progress": {
    "completed": 3,
    "total": 10
  }
}
```

### 2. Broadcast Script

```python
# .agent/scripts/athena_status.py
import json
from pathlib import Path
from datetime import datetime

STATUS_FILE = Path.home() / ".athena" / "agent_status.json"

def broadcast_status(status: str, task: str = None, progress: dict = None):
    """Update agent status for orchestration visibility."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "session_id": os.environ.get("ATHENA_SESSION_ID", "unknown"),
        "agent_id": os.environ.get("ATHENA_AGENT_ID", "unknown"),
        "status": status,
        "current_task": task,
        "updated_at": datetime.now().isoformat(),
        "progress": progress
    }
    
    STATUS_FILE.write_text(json.dumps(data, indent=2))
    print(f"📡 Status: {status} — {task}")
```

### 3. Status Polling

```bash
# Check all agent statuses
cat ~/.athena/agent_status.json

# Watch for changes
watch -n 1 cat ~/.athena/agent_status.json
```

## Integration Points

- **Boot Script**: Set status to `working` on session start
- **Quicksave Script**: Set current task from message
- **Error Handler**: Set status to `error` on exception
- **Task Completion**: Set status to `finished`

## UI Integration (Future)

```
┌────────────────────────────────────────────┐
│ Athena Orchestrator                        │
├────────────────────────────────────────────┤
│ Agent 1: ●working  [Protocol 409] ████░░ 40%│
│ Agent 2: ●idle                              │
│ Agent 3: ●needs_input  [Awaiting approval] │
└────────────────────────────────────────────┘
```

## Related Protocols

- Protocol 409 (Parallel Worktree Orchestration)
- Protocol 413 (Multi-Agent Coordination)

---

# protocol #observability #status #broadcasting #stolen/maestro
