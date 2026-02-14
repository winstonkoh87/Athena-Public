---
description: Orchestrate parallel agent swarms using worktrees
created: 2026-02-03
last_updated: 2026-02-03
---

# /swarm — Parallel Agent Orchestration (Protocol 416)

> **Purpose**: Convert linear "wait time" into parallel "build time".
> **Power Level**: High (Requires M2/M3 Chip for >2 Agents).

---

## 1. The Swarm Architecture

Instead of 1 Agent doing A -> B -> C, we spawn 3 Agents:

- **Agent Alpha**: Frontend (React/Tailwind)
- **Agent Beta**: Backend (Python/FastAPI)
- **Agent Gamma**: QA/Tests (Pytest/Cypress)

## 2. Execution Flow

### Phase 1: The Split (Commander)

User defines the objective.
**Command**:

```bash
### Phase 1: The Split (Commander)

User defines the objective.
**Command**:

```bash
# Create isolated environments (via worktrunk)
python3 examples/scripts/worktrunk.py add frontend
python3 examples/scripts/worktrunk.py add backend
python3 examples/scripts/worktrunk.py add qa
```

### Phase 2: The Swarm (Build)

You (The Orchestrator) assign tasks to each "Seat".

**Context Switch**:

```bash
# List active swarms
python3 examples/scripts/worktrunk.py list

# Switch to swarm (manual cd)
cd ../Athena-Public-swarms/frontend
# Build Frontend...
```

### Phase 3: The Convergence (Merge)

When tasks are done, merge back to Main.

```bash
# 1. Commit in worktree
git commit -am "Feat: Frontend complete"
git push origin swarm/frontend

# 2. Merge via Worktrunk
python3 examples/scripts/worktrunk.py merge frontend
python3 examples/scripts/worktrunk.py merge backend
```

## 3. Safety Constraints

- **Database**: All swarm agents MUST share the *same* dev database (or mocks) to ensure compatibility.
- **API Contract**: Define the "Interface" *first*. Backend and Frontend cannot diverge.
  - *Action*: Create `api_spec.json` or `schema.prisma` in Main before splitting.

## 4. Trigger Commands

- `/swarm start <objective>` -> Initiates split
- `/swarm status` -> Lists active worktrees
- `/swarm merge` -> Auto-merges all active swarm branches

---

## Why This Works

| Traditional | Swarm |
|------------|-------|
| Agent A does Frontend (2h) | Agent A: Frontend (2h) |
| Agent A does Backend (2h) | Agent B: Backend (2h) |
| Agent A does Tests (1h) | Agent C: Tests (1h) |
| **Total: 5 hours** | **Total: 2 hours** (parallel) |

---

# workflow #swarm #parallel #productivity
