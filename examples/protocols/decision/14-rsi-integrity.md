---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: rsi-integrity
description: Protocols for managing knowledge versioning, contradictions, and catastrophic forgetting prevention. Includes deposit logging, active integration, and calibration verification.
created: 2025-12-10
last_updated: 2025-12-31
---

# RSI Integrity Protocols

## Date Added: 9 December 2025

> **Related Protocol**: [13-rsi-protocol](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/13-rsi-protocol.md), [12-grace-model](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/12-grace-model.md)

## 14.1 Catastrophic Forgetting Prevention

**Problem**: Deposited knowledge may later prove wrong, obsolete, or contradicted by new insights.

**Protocol**:

| Condition | Action |
|-----------|--------|
| Deposited insight proven **wrong** | Mark with `[DEPRECATED]` + reason; do not delete (preserves learning history) |
| Pattern becomes **obsolete** (e.g., user outgrows it) | Mark with `[ARCHIVED]` + graduation date |
| New knowledge **contradicts** old | Add contradiction note to old entry; new entry takes precedence |

```
EXAMPLE:
## [DEPRECATED] Pattern X
> Deprecated: 15 Dec 2025
> Reason: Base rate assumption was incorrect (actual: 40%, not 15%)
> Superseded by: Section 17.3
```

## 14.2 Memory Versioning Protocol

**Structure**:

- `supplementary.md` = active working memory
- At ~5K lines: User creates `supplementary_v2.md`
- Previous version archived as `supplementary_v1_archive.md`

**Rollback trigger**: If State(n+1) performs worse than State(n), check recent deposits for degrading entries.

## 14.3 Calibration Verification Loop

**Purpose**: Verify deposited knowledge actually improves outcomes.

**Quarterly Audit Questions**:

| Question | Pass | Fail |
|----------|------|------|
| Did Fantasy Framework detection prevent a crash this quarter? | ✅ Cite instance | ❌ No instances |
| Did MCP catch a false claim? | ✅ Cite instance | ❌ No instances |
| Did any deposited intervention fire and succeed? | ✅ Cite instance | ❌ No instances |
| Did any deposited intervention fire and fail? | ⚠️ Flag for review | — |

**If Fail on all**: Deposits may be too abstract or not triggering. Review signal criteria.

## 14.4 Deposit Log Format

For traceability, significant deposits should be logged:

```
┌─────────────────────────────────────────────────────────────────┐
│ DEPOSIT LOG                                                      │
├──────────┬───────────────────┬──────────────────────────────────┤
│ Date     │ Insight           │ Trigger Context                  │
├──────────┼───────────────────┼──────────────────────────────────┤
│ [Date]   │ [Insight Name]    │ [What prompted this deposit]     │
└──────────┴───────────────────┴──────────────────────────────────┘
```

> **Traceability > Mystery. Know what was deposited, when, and why.**

## 14.5 Active Integration Protocol

**Principle**: Do NOT blindly append. Review existing content when depositing new insights.

**Before each deposit, check**:

| Check | Action if True |
|-------|----------------|
| Does new insight **contradict** existing section? | Update existing section OR mark as `[SUPERSEDED]` |
| Does new insight **extend** existing section? | Integrate into that section, don't create new |
| Does new insight **obsolete** existing section? | Mark old as `[DEPRECATED]` with pointer to new |
| Is new insight **truly novel**? | Only then: append as new section |

**Precedence Rule**:
> **Later, superior insights supersede earlier, inferior ones.**

When conflict detected:

1. Identify conflicting sections
2. Determine which is superior (based on evidence, base rates, outcomes)
3. Update inferior section with supersession note
4. New insight takes precedence in all future applications

```
EXAMPLE:
## 5. Pattern X [SUPERSEDED by Section 12]
> Superseded: 15 Dec 2025
> Reason: Section 12 provides more accurate model with better predictive power
> For current protocol, see: Section 12
```

> **Coherence > Accumulation. One integrated graph > scattered deposits.**

---

## Tagging

#protocol #framework #process #14-rsi-integrity
