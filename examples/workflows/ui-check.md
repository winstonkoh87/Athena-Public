---
description: Visual QA using Browser Sub-Agent. Captures screenshots/recordings of critical UI paths.
created: 2026-02-13
tags: [workflow, qa, visual, browser]
---

# /ui-check — Visual Quality Assurance

> **Latency Profile**: HIGH (Browser interaction)
> **Purpose**: "Don't just look at code. Look at the product."
> **Mechanism**: Dispatches a `browser_subagent` to verify UI integrity.

## Phase 1: Environment Check

// turbo

```bash
# Check if local server is running (assuming port 3000 or 8080)
lsof -i :3000 >/dev/null && echo "✅ Server running on :3000" || echo "⚠️ Server not found on :3000 (Start it manually if needed)"
lsof -i :8080 >/dev/null && echo "✅ Server running on :8080" || echo "⚠️ Server not found on :8080"
```

## Phase 2: Browser Verification (The "Eyeball" Test)

> **Agent Instruction**:
>
> 1. Launch `browser_subagent`.
> 2. Visit the local project URL (e.g., <http://localhost:3000>).
> 3. Click through critical paths (Nav, Auth, Dashboard).
> 4. **Capture Screenshot** of the final state.
> 5. Report any layout breaks or console errors.

## Phase 3: Reporting

// turbo

```bash
echo "✅ Visual check completed at $(date)" >> .context/session_logs/qa_log.md
```
