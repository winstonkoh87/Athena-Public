---created: 2026-01-03
last_updated: 2026-01-30
---

---description: Soft Reset — Close current session and start a fresh one immediately.
created: 2026-01-03
last_updated: 2026-01-03
---

# /fresh — Session Hot Swap

> **Purpose**: Rotates the session log to a new file, effectively starting a "fresh slate" for the agent's long-term memory tracking.
> **Note**: This does NOT clear the LLM context window (scrollback), but it logically separates the work.

// turbo

1. **Close Current Session**:
   - Save final checkpoints.
   - Update metrics.
   - Write closing timestamp.

   ```bash
   python3 .agent/scripts/shutdown.py
   ```

// turbo
2. **Start New Session**:

- Create new session log (Session N+1).
- Re-prime context.

   ```bash
   python3 .agent/scripts/boot.py
   ```

1. **Reset Task State**:
   - The agent should manually call `task_boundary` with empty args to clear the UI.
