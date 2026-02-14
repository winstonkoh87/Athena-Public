---created: 2025-12-28
last_updated: 2026-01-30
---

---description: Run the Athena Guidance System (suggest_protocols.py)
created: 2025-12-28
last_updated: 2025-12-28
---

# /guide — Contextual Protocol Advisor

> **Usage**: `/guide "some context or problem"`

This workflow runs the `suggest_protocols.py` script, which scans your 290+ Protocols and Case Studies to recommend the best "Mental Models" for your current situation.

## Steps

1. Run the Guidance System
// turbo

```bash
python3 .agent/scripts/suggest_protocols.py "$@"
```
