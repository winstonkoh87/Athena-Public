---

created: 2025-12-23
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-23
last_updated: 2026-01-06
---

# Protocol 159: Verification Before Claim

> **Trigger**: AI claims a feature, fix, or system is "done" or "working"
> **Reference**: [Protocol 168](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/168-context-driven-development.md)
> **Source**: User feedback, Session 2025-12-23-07

---

## The Failure Pattern

```
❌ AI writes code → claims "fixed" → moves on
   User discovers later it never worked
```

## The Correct Pattern

```
✅ AI writes code → runs live test → shows output → THEN claims "fixed"
```

---

## Enforcement Rule

**Before claiming any of these states, you MUST demonstrate with live output**:

| Claim | Required Proof |
|-------|----------------|
| "Fixed" | Run the fix, show it works |
| "Working" | Execute the function, show output |
| "Deployed" | Hit the endpoint, show response |
| "Configured" | Run a test that uses the config |

**No live test = No claim.**

---

## Origin

User caught AI claiming semantic search was "fixed" when it had never been verified. The schema was wrong, functions were missing, but AI moved on without testing.

> "I would never have known if I had not tested you out."

This protocol exists because trust requires verification, not just intention.

---

## Tags

# verification #trust #calibration #protocol
