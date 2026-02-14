---
description: Orchestrate parallel agent swarms using worktrees
created: 2026-02-03
last_updated: 2026-02-03
---

# /swarm — Parallel Agent Orchestration

> **Purpose**: Convert linear "wait time" into parallel "build time".
> **Power Level**: High (Requires M2/M3 Chip for >2 Agents).
> **Protocol**: [Protocol 409 (Worktrees)](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v8.2-stable/protocols/409_Parallel_Worktree_Orchestration.md)

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
# Create isolated environments
.agent/scripts/parallel_session.sh create swarm-fe
.agent/scripts/parallel_session.sh create swarm-be
.agent/scripts/parallel_session.sh create swarm-qa
```

### Phase 2: The Swarm (Build)

You (The Orchestrator) assign tasks to each "Seat" (simulated or real).

> **Note**: In a single-window interface (Antigravity), we simulate this by switching Context Windows or rapidly context-switching between worktrees.
> *True Parallelism requires multiple terminal windows or the `tm` script.*

**Context Switch**:

```bash
cd ../.worktrees/session-swarm-fe
# Build Frontend...
```

### Phase 3: The Convergence (Merge)

When tasks are done, merge back to Main.

```bash
# 1. Commit in worktree
git commit -am "Feat: Frontend complete"
git push origin feature/session-swarm-fe

# 2. Merge in Main
cd ../../Project\ Athena
git merge feature/session-swarm-fe
git merge feature/session-swarm-be
```

## 3. Safety Constraints

- **Database**: All swarm agents MUST share the *same* dev database (or mocks) to ensure compatibility.
- **API Contract**: Defines the "Interface" *first*. Backend and Frontend cannot diverge.
  - *Action*: Create `api_spec.json` or `schema.prisma` in Main before splitting.

## 4. Trigger Commands

- `/swarm start <objective>` -> Initiates split
- `/swarm status` -> Lists active worktrees
- `/swarm merge` -> Auto-merges all active swarm branches

---

# workflow #swarm #parallel #productivity
