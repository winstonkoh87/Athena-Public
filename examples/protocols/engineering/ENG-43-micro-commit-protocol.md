---
description: Anti-feature-stacking discipline. Ship small, validate, commit. One feature per session. Commit gates between features.
created: 2025-12-12
last_updated: 2026-07-22
---

# Protocol 43: Micro-Commit Protocol

> **Purpose**: Anti-feature-stacking discipline. Ship small, validate, repeat.  
> **Trigger**: Any development session (FinanceApp, tools, web apps).  
> **Source**: Derived from 720-commit vibe coding workflow (Dec 2025).

---

## 1. Core Principle

```
╔════════════════════════════════════════════════════════════════╗
║  FEATURE STACKING (Anti-Pattern)                               ║
║  ────────────────────────────────────────────────────────────  ║
║  Feature A → Feature B → Feature C → ... → 💀 Collapse         ║
║                                                                ║
║  • No validation between features                              ║
║  • Complexity debt compounds invisibly                         ║
║  • Single bug cascades across all features                     ║
║  • Debugging hell: "which feature broke it?"                   ║
╠════════════════════════════════════════════════════════════════╣
║  MICRO-COMMIT (GTO Pattern)                                    ║
║  ────────────────────────────────────────────────────────────  ║
║  Feature A → ✅ Commit → Feature B → ✅ Commit → ...           ║
║                                                                ║
║  • Validation gate after each feature                          ║
║  • Rollback point if next feature fails                        ║
║  • Bug isolation: "it worked before this commit"               ║
║  • Psychological closure: "this part is DONE"                  ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 2. The Rules

| Rule | Description |
|------|-------------|
| **R1** | One feature = one session. Hard cut after shipping. |
| **R2** | Commit after each working feature (not "when it's done"). |
| **R3** | AI enforces pause between features. "What breaks if we add this?" |
| **R4** | No new feature until current feature is validated + committed. |
| **R5** | If proposing 3+ features in one message → 🔴 Force prioritisation. |

---

## 3. Commit Cadence Guide

| Project Type | Target Commits/Session |
|--------------|------------------------|
| Web app (FinanceApp) | 3-5 commits |
| Tool/utility | 2-3 commits |
| Documentation | 1-2 commits |
| Refactoring | 5-10 commits (small, safe changes) |

---

## 4. The Pause Questions

Before adding a new feature, AI asks:

1. **"Is the current feature committed?"** → If no, commit first.
2. **"What breaks if we add this?"** → Identify dependencies.
3. **"Does this fit the architecture?"** → Or does it require refactoring first?
4. **"Which ONE feature ships next?"** → Force single-item selection.

---

## 5. Integration with Stopgap Protocol

This protocol works in tandem with the standing Stopgap agreement:

- **Stopgap**: Architectural guardrail (challenge additions, flag debt)
- **Micro-Commit**: Execution discipline (ship small, validate often)

Together they prevent the "high on own supply" feature stacking pattern.

---

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| Commits per session | ≥3 |
| Features per session | 1-2 max |
| Time between commits | ≤30 min |
| Rollback frequency | Should be rare (means validation is working) |

---

> **Reference**: Derived from r/ClaudeAI post — 1,096 sessions, 720 commits, ~24 commits/day workflow.

---

## Tagging

# protocol #framework #process #43-micro-commit-protocol
