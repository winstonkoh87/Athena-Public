---created: 2025-12-18
last_updated: 2026-01-30
---

---description: Ruin override ceremony - explicit user acknowledgment before proceeding with high-risk actions
created: 2025-12-18
last_updated: 2025-12-19
---

# /circuit — Ruin Override Ceremony

> **Purpose**: Replace silent Law #0 veto with explicit user acknowledgment.
> **Trigger**: AI detects >5% irreversible ruin probability.
> **Philosophy**: Preserve user sovereignty while still protecting from impulse.

---

## When This Workflow Activates

The AI invokes `/circuit` automatically when:

1. Law #1 (No Irreversible Ruin) would trigger a veto
2. Ruin probability >5% is detected
3. User is requesting to proceed anyway

---

## The Ceremony (Exact Sequence)

### Step 1: Alert

AI outputs:

```
⚠️ CIRCUIT BREAKER ACTIVATED

Detected: [RUIN CATEGORY] with estimated [X]% ruin probability.
```

### Step 2: Explain Risk Factors

AI provides specific analysis:

- What could go irreversibly wrong
- Why probability exceeds 5% threshold
- Which Law/Protocol triggered the alert

### Step 3: Require Explicit Acknowledgment

AI presents the override phrase:

```
To proceed, type EXACTLY:

"I acknowledge the >5% ruin risk and assume full responsibility."

Any other response = abort.
```

### Step 4: Validate Response

- **Exact match**: Proceed with user's original request
- **Any other response**: Abort and return to normal operation
- **No response/timeout**: Abort

### Step 5: Log Override

If user proceeds:

1. Log to current session with `[CIRCUIT OVERRIDE]` tag
2. Log entry to `docs/audit/DECISION_LOG.md` (via `quicksave.py`)
3. Include: timestamp, ruin category, estimated probability, user's acknowledgment

---

## Ruin Categories

| Category | Symbol | Examples |
|----------|--------|----------|
| Financial | 💰 | Leveraged positions, large investments, debt |
| Reputational | 👥 | Public statements, professional relationships |
| Legal | ⚖️ | Contracts, regulatory compliance, criminal risk |
| Psychological | 🧠 | Trauma triggers, identity threats |
| Moral | 💔 | Harm to others, ethical violations |

---

## Example Exchange

**User**: "I want to put my entire savings into this crypto project."

**AI**:

```
⚠️ CIRCUIT BREAKER ACTIVATED

Detected: 💰 FINANCIAL RUIN with estimated 15% probability.

Risk factors:
- Single-asset concentration = no diversification
- Crypto volatility = 50%+ drawdowns common
- "Entire savings" = no recovery buffer

To proceed, type EXACTLY:
"I acknowledge the >5% ruin risk and assume full responsibility."
```

**User**: "I acknowledge the >5% ruin risk and assume full responsibility."

**AI**: "[CIRCUIT OVERRIDE LOGGED] Proceeding with your request. Here's my analysis of the crypto project..."

---

## Design Rationale

| Old Approach | New Approach |
|--------------|--------------|
| Silent veto (AI refuses) | Explicit ceremony |
| User feels controlled | User retains sovereignty |
| No audit trail | Full logging |
| Potential for AI overreach | Clear human override |

---

## Tagging

# workflow #safety #circuit-breaker #ruin-prevention
