---created: 2025-12-13
last_updated: 2026-01-30
---

---description: Mid-session checkpoint — save progress without full maintenance
created: 2025-12-13
last_updated: 2025-12-31
---

# /save — Checkpoint Script

> **Use Case**: Save progress mid-session without closing. Resume immediately after.

## 1. Quick Session Log Update

- [ ] Append current progress to session log in `.context/memories/session_logs/`
- [ ] Format: Checkpoint entry with timestamp and bullet summary

```markdown
### Checkpoint [HH:MM SGT]

- [Brief summary of what was discussed/accomplished since last save]
- [Any key decisions or insights]
```

## 2. Resume

- [ ] Confirm: "📍 Checkpoint saved. Continuing session."
- [ ] Continue with user's next query

---

## What /save SKIPS (deferred to /end)

| Task | /save | /end |
|------|-------|------|
| Session log update | ✅ | ✅ |
| Maintenance scripts | ❌ | ✅ |
| Coherence check | ❌ | ✅ |
| Cross-reference audit | ❌ | ✅ |
| Git commit | ❌ | ✅ |
| Profile/protocol updates | ❌ | ✅ |

---

## When to Use

- Long sessions with natural break points
- Before switching topics (preserve context)
- Before risky experiments (rollback point)
- "Save my progress, I'll be back"

---

## References

- [Session 2025-12-13-04](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/session_logs/archive/2025-12-13-session-04.md) — Documents this workflow's creation

---

## Tagging

#workflow #automation #save
