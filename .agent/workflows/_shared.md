---
description: Shared workflow conventions and base context inherited by all workflows
created: 2026-04-12
last_updated: 2026-11-14
---

# Workflow Shared Context

> Implicit pre-load for every workflow (`_domain/` activates only on domain match or explicit `/command`). Framework modules override defaults here. Full UI, Anti-Abstraction, Swarm, and Routing specs: [`.agent/workflows/references/_shared_extended.md`](references/_shared_extended.md).

## Sources of Truth & Precedence

| Priority | File | Scope & Progressive Disclosure |
|:---|:---|:---|
| 1 | `.context/memory_bank/activeContext.md` | Current session thread (Header + latest `[[ S__` checkpoint) |
| 2 | `.context/CANONICAL.md` | Materialized truth & Tier 1 laws. JIT-load `CANONICAL_TIER2.md` (~64KB) on domain match; `CANONICAL_TIER3.md` (~1KB) on request. |
| 3 | `.context/memory_bank/userContext.md` | Identity, constraints, psychology |
| 4 | `.context/PROJECTS.md` | Active projects & pipeline |
| 5 | `.context/PROTOCOL_SUMMARIES.md` / `PROTOCOL_HEATMAP.md` | Protocol discovery |
| 6 | `.context/CASE_STUDY_INDEX.md` | Case-study precedents |
| 7 | `.context/TECH_DEBT.md` | Open tech debt before new proposals |

- **Conflicts**: `CANONICAL.md` > session logs/memories; `activeContext.md` > `CANONICAL.md` only for transient in-flight state; `userContext.md` > `CANONICAL.md` for user identity/psychology; `DATA_CONTRACT.md` wins all write-boundary questions. Same-tier ties -> ask user.
- **Counts & Retired Indexes**: Canonical counts live in `.agent/config/CAPS.json`. Never rely on retired `project_state.md` or `TAG_INDEX.md`.

## Risk Tiers, Grounding & Substance Decode

- **SNIPER (Λ < 10)**: Direct answer; search exempt (`vector_mode="local"`).
- **STANDARD (Λ 10-30)**: Call `context_gate(query)` or `smart_search` first; satisfy `missing`. Speculative fast-path runs for Λ 10-14 non-personalised/non-web queries; Λ >= 15 escalates to parallel vector + local. Default = STANDARD unless certain low-risk.
- **ULTRA (Λ > 30)**: Call `context_gate(query)`; requires semantic AND (web OR page-read).
- **Enforced by**: `.agents/hooks.json` (`stop_governance_gate.py`).

- **Substance Decode Lens (PAT-574, Λ >= 10)**: For T1 inbound narratives, T2 outbound commits (run Receiver-Frame Simulation), T3 third-party verdicts, T4 stakes (~S$100+; capital -> `trading-risk-gate`), or T5 felt-evidence: Prior -> Discriminators -> Sign check (MP-16) -> Payoff-weighted action (`substance-decode` / `hook_meta_awareness_gate.py`).
- **Mandatory Search & OSINT Triggers**: Always search Exocortex first on **Names/People**, **Past Decisions**, **Empirical Data**, **Project Codes**, or **Protocols/CS**; run **Protocol 580 (`/osint`)** before advising/pricing any external entity; use `search_web` / `read_url_content` for volatile facts.

## Core Shared Invariants

- **ASCII-only math & currency**: Zero LaTeX/KaTeX delimiters (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `\text{...}`) in chat or files.
- **Safety & Governance**: Pre-edit importer check (ENG-542 GateGuard); Red Run before guard fixes; never use `git stash`, switch branches, or alter other agents' files (Protocol 413); check Epistemic Status (`code-enforced` vs `agent-discretion`, S534); slice logs (`grep`/`head`/`tail`) rather than dumping whole files; pause with `[CHECKPOINT]` when `requires_approval: true`.
- **Autonomous Compute Tier**: Follow `context_gate` `compute_tier` without asking dispatch permission (see [`_shared_extended.md`](references/_shared_extended.md)).
