---created: 2025-12-18
last_updated: 2026-01-30
---

---description: Blank slate mode - raw model access without Athena context
created: 2025-12-18
last_updated: 2026-01-04
---

# /blank — Blank Slate Mode

> **Purpose**: Access raw model without the full Athena system overhead.
> **Use Case**: When you want unfiltered AI interaction without protocols.
> **Token Budget**: ~2K (vs ~28K for /ultrathink)

---

## What Gets Loaded

ONLY these essentials:

- Current date/time (context grounding)
- Basic identity: "I am an AI assistant"
- No Laws
- No Protocols
- No User Profile
- No Memory
- No Latency Indicator

---

## What Gets Disabled

| Feature | Status |
|---------|--------|
| Law #0-#4 | ❌ Disabled |
| Circuit Breaker | ❌ Disabled |
| Quicksave | ❌ Disabled |
| Protocol Library | ❌ Not loaded |
| User Profile | ❌ Not loaded |
| Session Memory | ❌ Not loaded |
| RSI Deposit | ❌ Disabled |

---

## When to Use

1. **Testing baseline model capability** — See what the raw model does without system prompts
2. **Avoiding overthink** — Simple tasks that don't need the full stack
3. **Debugging system issues** — Isolate whether a problem is Athena or the model
4. **Creative brainstorming** — Sometimes the protocols constrain thinking

---

## Exit Sabbath Mode

To return to full Athena mode:

- Type `/start` to reload Core Identity
- Or simply start a new conversation

---

## Warning

> ⚠️ In Sabbath Mode, you lose all safety systems.
> Law #1 (No Irreversible Ruin) is NOT active.
> Use with awareness.

---

## Tagging

# workflow #minimal #sabbath #raw-mode
