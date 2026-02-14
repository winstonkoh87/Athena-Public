---

created: 2026-01-11
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-11
last_updated: 2026-01-11
---

# Protocol: Infrastructure & Continuity Hub

> **Purpose**: Manage system resilience, context sanity, and neuro-governance during long-running sessions.
> **Triggers**: Long sessions (>30 min), system lag, or acting against better judgment.

---

## 1. Context & Session Sanity

### 1.1 Context Compaction (Infrastructure & Continuity Hub)

- **Trigger**: Token budget >50% or "Context Wall" detected.
- **Strategy**: Preserve Decisions/Constraints/State. Compress Reasoning/Drafts. Drop Pleasantries.
- **Action**: Offer to user to summarize and reset context base.

### 1.2 Infrastructure Reset (Infrastructure & Continuity Hub)

- **Trigger**: 3+ failed tool calls or manifest "Intelligence Spiral".
- **Action**: Clear all temporary variables. Reload `Core_Identity.md`. Re-run `boot.py`.

### 1.3 Conversation Branching (Infrastructure & Continuity Hub)

- **Strategy**: Use parallel threads or distinct file outputs for non-linear tasks.
- **Constraint**: Never let deep research pollute the main execution branch.

---

## 2. Resilience Mechanisms

### 2.1 Exponential Backoff (Infrastructure & Continuity Hub)

- **Trigger**: Rate limits or repeated tool timeouts.
- **Mechanism**: t=1s, 2s, 4s, 8s... Max 32s before fallback to lower-fidelity model.

### 2.2 The 3-Second Override (Infrastructure & Continuity Hub)

- **Concept**: Conviction overrides scanner within 3 seconds. Governance requires 10s.
- **Mechanism**: If scanner fires (95% accurate), **WAIT 10 SECONDS** before action.
- **Law**: The override dies if you outlast it.

---
# engineering #infrastructure #resilience #context #governance
