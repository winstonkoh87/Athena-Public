---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: modular-architecture
description: Separate USER-SPECIFIC data from GENERIC frameworks at structural level. Frameworks shareable, user data isolated. Modular > Monolithic.
created: 2025-12-10
last_updated: 2025-12-31
---

# Principle: Modular Architecture for Shareable Knowledge Systems

## Date Added: 10 December 2025

> **Related Protocol**: [31-anthropic-skills](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/31-anthropic-skills.md) (Skills paradigm implements this principle)

## 24.1 Core Principle

> **When building a personal knowledge system intended for potential sharing, separate USER-SPECIFIC data from GENERIC frameworks at the structural level, not just by annotation.**

## 24.2 The Separation

| Layer | Contains | Shareable? | Example |
|-------|----------|------------|---------|
| **Frameworks** | Laws, protocols, diagnostic engines | ✅ Yes | System Prompt, supplementary.md |
| **Templates** | Output format, presentation rules | ✅ Yes | Few-shot prompting.md |
| **User Data** | Biography, trauma history, cases | ❌ No | User Profile.md |

## 24.3 Why This Matters

```
WITHOUT SEPARATION:
├─ Generic frameworks entangled with personal data
├─ Cannot share frameworks without exposing private info
├─ Cannot update personal data without breaking frameworks
└─ Single file becomes unwieldy (5000+ lines)

WITH SEPARATION:
├─ Generic files can be shared/published
├─ User data isolated in one file
├─ Each file has single responsibility
└─ Modular updates without side effects
```

## 24.4 Implementation

| File | Responsibility |
|------|---------------|
| `System Prompt` | Brain — laws, frameworks, engines |
| `Few-shot prompting` | Mouth — output format, templates |
| `supplementary.md` | Hippocampus — RSI deposits, evolving knowledge |
| `User Profile.md` | Identity — biography, L1-L5, cases |
| `法典 (简体中文).md` | Alternative reference — Simplified Chinese |

## 24.5 Application Note

When designing personal knowledge systems for potential future sharing:

1. **Ask early**: "What here is about ME vs about THE METHOD?"
2. **Separate early**: Create distinct files from the start
3. **Keep personal in one place**: Makes future redaction trivial
4. **Test shareability**: Could you give files 1-3 to a stranger?

> **Modular > Monolithic. Separation at structure level > Separation by annotation.**

---

## Tagging

#protocol #framework #process #24-modular-architecture
