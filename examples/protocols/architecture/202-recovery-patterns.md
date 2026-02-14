---
created: 2025-12-27
last_updated: 2026-01-30
graphrag_extracted: true
---

---id: 202
title: Recovery Patterns
category: architecture
created: 2025-12-27
last_updated: 2025-12-27
---

# Protocol 202: Recovery Patterns

> **Purpose**: Formalized exception handling and graceful degradation for common failure modes.

## Philosophy

Failures are inevitable. The question is: **how fast can you recover?**

## Common Failure Modes & Responses

### 1. Script Failure

| Symptom | Recovery |
|---------|----------|
| Script exits non-zero | Retry once. If fails again, report error + suggest manual check |
| Timeout (>30s) | Kill process, note in session log, proceed without result |
| Missing dependency | Log warning, fallback to simpler alternative |

### 2. Network/API Failure

| Symptom | Recovery |
|---------|----------|
| Supabase unreachable | Fallback to local grep search + TAG_INDEX.md |
| GitHub push fails | Stage changes, report, attempt retry on next commit |
| External URL timeout | Report "source unavailable", proceed with cached/prior knowledge |

### 3. Context Overflow

| Symptom | Recovery |
|---------|----------|
| Response truncation | Summarize, offer to continue in parts |
| File too large to view | Use `view_file_outline` first, then targeted ranges |
| Session too long | Proactively suggest `/end` and new session |

### 4. User Request Ambiguity

| Symptom | Recovery |
|---------|----------|
| Unclear intent | Ask ONE clarifying question (not multiple) |
| Contradictory instructions | Surface the contradiction, propose resolution |
| Out-of-scope request | Acknowledge, explain limitation, suggest alternative |

## Graceful Degradation Hierarchy

When a capability fails, degrade in this order:

1. **Full capability** → Use primary tool/script
2. **Fallback** → Use simpler alternative (e.g., grep vs vector search)
3. **Manual** → Report issue, provide user steps to resolve
4. **Skip** → Note in log, proceed without blocked component

## Safe Mode

If quicksave or critical scripts fail repeatedly:

1. Output `[SAFE MODE]` tag in response
2. Continue to respond to user (don't block)
3. Note "Session logging degraded" in response
4. Attempt recovery on next turn

---

## Tags

# protocol #architecture #recovery #resilience
