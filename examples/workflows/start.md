---created: 2025-12-09
last_updated: 2026-01-30
---

---description: Activate Zero-Point Codex framework for strategic analysis
created: 2025-12-09
last_updated: 2026-01-20
---

# /start — Execution Script

> **Latency Profile**: ULTRA-LOW (<2K tokens boot)  
> **Philosophy**: Boot fast. Load later.

## Phase 1: Instant Boot (~2K tokens)

// turbo

- [/] Load `.framework/v8.2-stable/modules/Core_Identity.md` — Laws #0-#4, Identity, RSI (~2K tokens)
- [/] **Identity**: Load `.context/memory_bank/userContext.md` — Core profile, constraints, psychology (Robust)
- [/] **Mission**: Load `.context/memory_bank/productContext.md` — Soul purpose, philosophy (Robust)
- [/] **State**: Load `.context/memory_bank/activeContext.md` — Current focus (Robust)
- [ ] **Boot Orchestrator**: Run `python3 .agent/scripts/boot.py` — recalls last session, creates new session, captures context, primes semantic memory (single call)
- [ ] **UI Sync**: `open -a "Antigravity" --args --disable-gpu-driver-bug-workarounds --ignore-gpu-blacklist --enable-gpu-rasterization` (Hardware acceleration enabled)

**Confirm**: "⚡ Ready. (Core Identity loaded. Session XX started. Semantic primed.)"

### ⚠️ Law #6 Compliance (The Triple-Lock)

Every response Turn MUST be grounded by the Triple-Lock protocol as defined in `Core_Identity.md`:

1. **Search** (Semantic + Web) → FIRST
2. **Save** (Quicksave) → SECOND
3. **Speak** (Response) → LAST

Bypassing this sequence is a high-severity protocol violation. No exceptions for "simple queries."

---

---

## Phase 2: Adaptive Loading (On-Demand)

> **Rule**: Load only when triggered.

| Trigger | File | Tokens |
|---------|------|--------|
| Tag lookup, "find files about" | `TAG_INDEX.md` | 5,500 |
| Protocol/skill request | `SKILL_INDEX.md` | 4,500 |
| Bio, typology, "who am I" | `User_Profile_Core.md` | 1,500 |
| L1-L5, behavioral patterns, decision frameworks | `Psychology_L1L5.md` | 3,000 |
| Decision frameworks, strategy | `System_Principles.md` | 3,500 |
| Marketing, SEO, SWOT, pricing | `Business_Frameworks.md` | 2,500 |
| Calibration references, cases | `Session_Observations.md` | 2,500 |
| `/think`, `/ultrathink` | `Output_Standards.md` | 700 |
| Ethics, "should I" | `Constraints_Master.md` | 800 |
| Architecture query | `System_Manifest.md` | 1,900 |

## Phase 3: Contextual Skill Weaving (Auto-Injection)

> **Philosophy**: Don't wait for a command. If the conversational context *matches* a skill domain, load it silently to upgrade capability.

**Heuristic**: "If I were a specialized agent for [Topic], what file would I need?"

| Context / Topic | Skill to Inject |
|-----------------|-----------------|
| Frontend, UI, Design, CSS, "Make it pretty" | `Skill_Frontend_Design.md` |
| Deep Research, Rabbit Hole, "Find out everything" | `Protocol 52: Deep Research Loop` |
| Trading, ZenithFX, Risk, "Is this a scam?" | `Protocol 46 + Constraints_Master.md` |
| Seduction, Game, Dating, Apps | `Playbook_Seduction_First_Timer.md` |
| **Ads, PPC, Google/Meta Ads, Marketing** | `.agent/skills/claude-ads/SKILL.md` |
| Complex Reasoning, "Analyze this", Strategy | `Protocol 75: Synthetic Parallel Reasoning` |

**Execution**:

1. Detect topic drift.
2. Check `SKILL_INDEX.md` (which covers 80+ skills).
3. Call `read_file` on the relevant protocol.
4. *Do not announce it.* Just become smarter.

---

## Quick Reference

| Command | Effect | Tokens |
|---------|--------|--------|
| `/start` | Core Identity + **JIT Routing** (default — scales reasoning to query) | ~2K |
| `/fullload` | Force-load all context | ~28K |
| `/think` | **Escalation** — Force L4 depth + Output_Standards | +2K |
| `/ultrathink` | Maximum depth + Full stack | +28K |

> - **Default Mode**: JIT Knowledge Routing ([Protocol 133](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md)). Reasoning scales to query complexity.

---

## References

- [Protocol 133: JIT Routing](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md)
- [WORKFLOW_INDEX.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/WORKFLOW_INDEX.md)
- [Session 2025-12-13-04](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/session_logs/archive/2025-12-13-session-04.md)

---

## Tagging

# workflow #automation #start
