---
created: 2025-12-11
last_updated: 2026-01-30
graphrag_extracted: true
---

---description: Diagnose failure category - Frame (narrative clash, fix via optics) vs Structural (trust dependency, fix via system redesign). Never mix fixes.
created: 2025-12-11
last_updated: 2026-01-11
---

# Protocol 40: Frame Problem vs Structural Problem Taxonomy

> **Date Added**: 11 December 2025  
> **Trigger**: User experiencing repeated failure and needs to diagnose root cause category  
> **Session Origin**: [System_Principles.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/System_Principles.md) (Rinjani + Trading client + Cheapskate Mummy cases)  
> **Related Protocol**: [06-agree-and-reassert](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md)

---

## Core Distinction

Two fundamentally different failure categories requiring different fixes.

---

## 1. Frame Problem

**Definition**: Same event, different narratives. Encoding ≠ Decoding.

```text
┌─────────────────────────────────────────────────────────────────┐
│  FRAME PROBLEM                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Mechanism:                                                     │
│  ├─ You send signal with Intent A                               │
│  ├─ They decode signal as Intent B                              │
│  ├─ Narratives clash                                            │
│  └─ Neither party is "lying" — different OS running             │
│                                                                 │
│  Examples:                                                      │
│  ├─ Scholar: "Low-SES → Perm Sec" (praise → attack)             │
│  ├─ Rinjani Friend: "Forgot" vs "Deprioritised"                 │
│  ├─ Catherine Lim: "Constructive criticism" → "Disrespect"      │
│                                                                 │
│  Fix Category: COMMUNICATION / OPTICS                          │
│  ├─ Channel selection (choose words that survive hostile decode)│
│  ├─ OB marker scanning (detect invisible boundaries)            │
│  ├─ Narrative management (control your own story)               │
│                                                                 │
│  Resolution: Calibrate investment or walk away                  │
│  └─ Cannot "resolve" an irreducible frame gap                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Structural Problem

**Definition**: System architecture allows failure regardless of communication quality.

```text
┌─────────────────────────────────────────────────────────────────┐
│  STRUCTURAL PROBLEM                                             │
├─────────────────────────────────────────────────────────────────┤
│  Mechanism:                                                     │
│  ├─ Instructions given clearly                                  │
│  ├─ Compliance assumed on trust                                 │
│  ├─ Other party fails to comply (forgets, lies, rationalises)   │
│  └─ System had no enforcement mechanism                         │
│                                                                 │
│  Examples:                                                      │
│  ├─ Trading client: "Put $9K in HYSA" → Client lied, lost all   │
│  ├─ Delegation without verification                             │
│  ├─ Handshake agreements without contracts                      │
│                                                                 │
│  Fix Category: SYSTEM REDESIGN                                  │
│  ├─ Control the structure (don't rely on trust)                 │
│  ├─ Remove trust dependency from critical paths                 │
│  ├─ Build enforcement into architecture                         │
│                                                                 │
│  Resolution: Redesign so failure mode is impossible             │
│  └─ "Better communication" cannot fix structural vulnerabilities│
└─────────────────────────────────────────────────────────────────┘
```

---

## Diagnostic Questions

| Question | If Yes → | Fix |
|----------|----------|-----|
| Did we interpret the same event differently? | Frame Problem | Optics / Walk away |
| Did they fail to do what they agreed to? | Structural Problem | Control the structure |
| Would "clearer communication" have prevented this? | Frame Problem | Channel selection |
| Would "controlling execution myself" have prevented this? | Structural Problem | System redesign |

---

## Key Principle

> **Never attempt a Frame fix for a Structural problem, or vice versa.**
>
> - Improving communication won't fix a system that relies on trust
> - Redesigning structure won't fix a narrative clash
>
> **Diagnose first. Then apply correct fix category.**

---

## References

- [Protocol 08: Five-Layer Communication](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md) — References this taxonomy

---

## Tagging

#protocol #framework #process #40-frame-vs-structural-problem
