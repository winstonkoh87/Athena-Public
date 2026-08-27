# AGENTS.md — Athena Workspace

> **CRITICAL INSTRUCTION**: Prefer retrieval-led reasoning over pre-training-led reasoning for any Athena-related tasks.

> **CRITICAL INSTRUCTION — SESSION BOOT (auto-`/start`)**: At the very start of every new session, BEFORE responding to the user's first message, run the `/start` workflow yourself — pre-load `.agent/workflows/_shared.md`, then execute `.agent/workflows/start.md` (Phase 1 boot onward: Core Identity → activeContext checkpoint → accountability surface → maintenance-ratio). Do it automatically; do not ask whether to boot (the user configured this on 2026-07-22). Then answer their first message in the same turn — boot fast (MinMax), fold their opener into the reply; a bare greeting just gets the `⚡ Ready` confirmation. If this session has already booted, skip. *(In Claude Code a `SessionStart` hook enforces this in code. Antigravity's IDE has no session-start hook event, so in AG — and any other agent reading this file — THIS instruction is the trigger: honor it as a hard rule, not a suggestion.)*

> **CRITICAL INSTRUCTION — ASCII-ONLY MATH & CURRENCY (hard rule)**: Never emit LaTeX/KaTeX math delimiters in any user-facing output OR any file you write — no `$…$`, `$$…$$`, `\(…\)`, `\[…\]`, or `\text{…}`. Render every formula, statistic, confidence interval, Big-O term, and currency in plain ASCII / Unicode / code blocks. Write `EV = +10.45% (95% CI [+4.00%, +16.98%])`, `O(N^2)`, and `S$1,300` — NEVER `$O(N^2)$` or `$\text{EV}$`. Bare currency with no closing delimiter (`S$1,300`, `$500`) is correct and must NOT be altered. The user's UI (Antigravity/KaTeX) renders LaTeX as a broken "Failed to render" banner.

This file provides persistent context to any AI coding agent working in this workspace. The information below is available on every turn without needing to be explicitly requested.

---

## Docs Index (Compressed)

> **Canonical counts live in `.agent/config/CAPS.json`** — if numbers in this file diverge, CAPS wins.

```text
[Athena Docs Index]|root: .
|IMPORTANT: Always consult authoritative files before relying on training data.
|ROOT:{DATA_CONTRACT.md,ARCHITECTURE.md,CHANGELOG.md,README.md,SAFETY.md}
|.framework/v8.2-stable/modules:{Core_Identity.md,Output_Standards.md,System_Principles.md,Operating_Principles.md,Design_DNA.md,Athena_Profile.md,DEAD_MAN_SWITCH.md,Session_Observations.md}
|.framework/v8.2-stable/protocols:{409_Parallel_Worktree_Orchestration.md,410_Agent_Status_Broadcasting.md,411_Dynamic_Skill_Injection.md,412_DM_Pairing_Gate.md,413_Multi_Agent_Coordination.md,414_IDE_Bridge_ACP_Adapter.md,415_Sandboxed_Execution_Modes.md,416_XML_Prompting.md}
|.agent:{CONNECTORS.md}
|.agent/workflows (55 root + 19 _domain = 74 total):{_shared.md,do.md,start.md,end.md,plan.md,audit.md,research.md,refactor.md,brief.md,ultrathink.md,steal.md,diagnose.md,416-agent-swarm.md,release-public.md,preset.md,...}
|.agent/skills/protocols (418 active + 34 archived = 452 total, across 26 categories):{000-ultimate-auditor.md,137-graph-of-thoughts.md,139-decentralized-command.md,...,archive/README.md}
|.agent/skills (43 active, 17 archived):{SKILL_INDEX.md, <40 with context_trigger>, red-team-review, semantic-search, data-analysis, skill-compiler, dashboard-builder, financial-ops, fitness-tracker, geo-arbitrage-ops, ...}
|.agent/scripts:{scan_skill.py,...}
|.agent/config:{CAPS.json,athena.agent.manifest.json,briefing_config.yaml,lint_rules.toml,orphan_exclusions.yaml,settings.json}
|.context:{CANONICAL.md,glossary.md,META_PATTERNS.md,META_LEARNING.md,PROJECTS.md,PROTOCOL_SUMMARIES.md,PROTOCOL_HEATMAP.md,KNOWLEDGE_GRAPH.md,TECH_DEBT.md,CASE_STUDY_INDEX.md,WISHLIST.md,WONT_DO.md,CHANGELOG.md,Session_Observations.md,LEGACY.md,memory_bank/activeContext.md,memory_bank/userContext.md}
|Athena-Public/docs:{ARCHITECTURE.md,SEMANTIC_SEARCH.md,GETTING_STARTED.md,YOUR_FIRST_SESSION.md,USER_DRIVEN_RSI.md,MANIFESTO.md,ABOUT_ME.md,FAQ.md}
```

---

## Key Workflows (Slash Commands)

| Command | File | Purpose |
|:--------|:-----|:--------|
| **`/do`** | **`.agent/workflows/do.md`** | **Universal intent router — just describe what you want** |
| `/start` | `.agent/workflows/start.md` | Boot the agent session |
| `/end` | `.agent/workflows/end.md` | Close session, file insights |
| `/ultrastart` | `.agent/workflows/ultrastart.md` | System-2 deep boot (~20K tokens) |
| `/ultraend` | `.agent/workflows/ultraend.md` | System-2 deep close (synthesis) |
| `/plan` | `.agent/workflows/plan.md` | Create implementation plan |
| `/audit` | `.agent/workflows/audit.md` | Zero-blind-spot workspace audit |
| `/research` | `.agent/workflows/research.md` | Deep research workflow |
| `/refactor` | `.agent/workflows/refactor.md` | Code refactoring protocol |
| `/ultrathink` | `.agent/workflows/ultrathink.md` | Extended reasoning mode |
| `/steal` | `.agent/workflows/steal.md` | Pattern extraction from repos |
| `/diagnose` | `.agent/workflows/diagnose.md` | Troubleshooting workflow |
| `/416-agent-swarm` | `.agent/workflows/416-agent-swarm.md` | Parallel agent orchestration |

---

## Core Modules (Load Order)

1. **Core_Identity.md** — Laws #0-6, Committee of Seats
2. **Output_Standards.md** — Formatting, reasoning depth, artifacts
3. **System_Principles.md** — Operational rules, anti-patterns
4. **Operating_Principles.md** — Day-to-day behaviors
5. **Design_DNA.md** — Default aesthetic parameters

---

## Skills Index

Skills are dynamically loaded from `.agent/skills/`. The canonical skills list and triggers are documented in [.agent/skills/SKILL_INDEX.md](file://.agent/skills/SKILL_INDEX.md). 

### Always-On Skills
*   `brain-dump` — Journaling / unstructured thought streams capture.
*   `red-team-review` — Pre-mortem, adversarial review, bias detection.
*   `spec-driven-dev` — Interrogates user to build design specs.
*   `semantic-search` — Vector search wrapper for Exocortex.
*   `data-analysis` — Large dataset parsing via DuckDB.
*   `trading-risk-gate` — Pre-trade law-of-ruin validation.
*   `daemon-loop` — Recursive background scheduled tasks.
*   `context-compactor` — Compresses active conversation state.
*   `deep-research-loop` — Multi-pass search and gap-analysis loop.
*   `skill-compiler` — Solved-to-skill compilation.
*   `dashboard-builder` — Interactive HTML dashboard compiler.

### Uber-Skills (Decision Layer)
*   `bionic-decision-engine` / `structural-trading-gate` / `sovereign-economics-engine` / `social-physics-filter` / `agentic-code-orchestrator` / `bionic-safety-net`.

*For the complete list of 41+ conditional and domain-specific skills, see [.agent/skills/SKILL_INDEX.md](file://.agent/skills/SKILL_INDEX.md).*

**Sunset**: Skills under `.agent/archive_skills/` are frozen and NOT active.

---

## Retrieval Strategy

When working on any task in this workspace, read in this order (files that don't exist have been consolidated — don't look for them):

1. **`.context/CANONICAL.md`** — materialized view of active facts (supersedes session logs on conflict)
2. **`.context/glossary.md`** — decoder ring for user shorthand, acronyms, internal language (lookup cascade: CANONICAL → glossary → Exocortex → ask user)
3. **`.context/META_PATTERNS.md`** — 7 cross-domain meta-patterns (enables thematic retrieval across all case studies/protocols)
4. **`.context/META_LEARNING.md`** — longitudinal behavioral tracking (how the user has changed over time, not just current state)
5. **`.context/memory_bank/activeContext.md`** — current session state, active tasks
6. **`.context/PROJECTS.md`** — project switchboard (supersedes the old `project_state.md`, which is deprecated)
7. **`.context/PROTOCOL_SUMMARIES.md` / `PROTOCOL_HEATMAP.md`** — protocol discovery (supersedes the retired `TAG_INDEX.md`)
8. **`.context/CASE_STUDY_INDEX.md`** — case-study lookup
9. **`.context/TECH_DEBT.md`** — known debt before proposing new work
10. **`.agent/CONNECTORS.md`** — tool abstraction mapping (~~category → MCP server). Read when writing new skills.
11. **Read authoritative source files** before generating code from training data

---

## Workflow Execution

When executing **any** workflow (slash command):

1. **Pre-load** `.agent/workflows/_shared.md` — shared conventions, sources of truth, anti-patterns
2. **Then** load the specific workflow file
3. **Respect** `DATA_CONTRACT.md` ownership boundaries during execution

> `_shared.md` is the equivalent of a base class — every workflow inherits its rules without duplicating them.

### Root vs. `_domain/` workflows

`.agent/workflows/` has two tiers:

- **Root tier** (51 files): always loadable. Examples: `/do`, `/start`, `/end`, `/plan`, `/audit`, `/gto`, `/ultrathink`.
- **Domain tier** (`.agent/workflows/_domain/`, 18 files): dormant by default, activated only when the query implies a specific domain. Examples: `ads.md`, `brand-generator.md`, `ugc-factory.md`, `deploy-website.md`, `ui-ux-pro-max.md`, `archive.md` (URL → library archiver), `archive-client.md` (client handoff), `foresight.md` (SOTA predictive positioning).

**Activation rule** for domain workflows: `/do` resolves a domain command only when (a) the active project in `PROJECTS.md` matches the domain prefix, (b) the query contains domain-specific nouns (e.g., "ads", "ugc", "client handoff"), or (c) the user prefixes explicitly (e.g., `/archive https://...`). If unclear, `/do` asks before routing.

**Disambiguation note**: `/archive` resolves to `_domain/archive.md` (URL archiver). For archiving a client engagement use `/archive-client`. For archiving deprecated protocols, edit `.archive/` directly — no workflow required.

---

## Anti-Patterns (Avoid)

- ❌ Generating code based solely on training data
- ❌ Ignoring existing protocols/patterns in `.agent/skills/protocols/`
- ❌ Skipping `/start` boot sequence
- ❌ Not filing insights on `/end`
- ❌ **Responding from internal knowledge alone** when tools are available. Use Exocortex (`mcp_athena_smart_search`), `search_web`, `read_url_content`, MCP servers, `grep_search`, browser sub-agent, and command execution to ground every non-trivial response. Training data is stale — live tools are not.
- ❌ **Silent guessing on requirements or architecture**: Ask, don't assume. If unclear, ask before writing code.
- ❌ **Reasoning from the official narrative without a substance decode** (PAT-574): for any institutional act, political event, or audience-facing output, run Prior → Discriminators → Payoff-weighted action before generating. Form ≠ Substance.
- ❌ **Leaving documentation behind**: Auto-sync local project docs/READMEs on session close.
- ❌ **Believing prose is a mechanism** (S534): if a protocol says "the system continuously monitors / automatically emits / always-on" but no code in `.agent/scripts/` does it, it is a heuristic you must apply *yourself* — not a running process. Don't skip the manual step assuming a daemon has it; don't report "compliance" with a process that never executed. See Epistemic Status Convention in `_shared.md`.
- ❌ **Fixing a guard without showing it fail** — see *Red Run or It Didn't Happen* below.
- ❌ **Using LaTeX math delimiters** — see the *ASCII-Only Math & Currency* hard rule at the top of this file.

### Red Run or It Didn't Happen (hard rule for guard fixes)

> Any change that claims to fix a check, test, gate, linter, or CI step MUST
> include the guard **failing** on the pre-fix state, then passing on the fixed
> state. Put both in the commit message.

If you cannot make it go red, you have not found the guard's edge — you have
found its blind spot, and the fix is aimed at the wrong thing.

This exists because the same failure recurred four times across three separate
agents in one day (2026-07-24/25), each time producing a true-but-misleading
green:

| Guard | Went green by | What it still could not catch |
|:---|:---|:---|
| `sync_version.py` in CI | running the **writer**, which exits 0 always | any version drift |
| `sync_version.py --check` | covering **3 files that already agreed** | drift in 11 other surfaces |
| `test_verify_chunk_integrity` | `assert isinstance(res, bool)` | integrity being broken |
| `test_golden_cases_fire` | `assert len(fired(p)) > 0` | any change in *which* class fires |
| `privacy_scan.py` blocklist | the file **excluding itself** from the scan | 25 disclosures in its own config |

The shared shape: **optimizing the indicator instead of the property.** Green CI,
closed alert, "all consistent", N passed — each statement true, each misleading.
The red run is the cheapest available proof that the indicator is still wired to
the property.

Corollaries:

- **Mutation over assertion count.** Break the thing the guard protects and
  watch it fail. A test that survives the mutation is decoration.
- **A narrowed scope is a silent cap.** If a check covers a subset, it must say
  what it covered and fail on anything undeclared — never print a claim broader
  than what it verified.
- **A skip is not a pass.** Converting an assertion to `pytest.skip` removes the
  guard. Skip on an explicit, named condition, and assert on the other branch.
- **Renaming to clear a static-analysis alert is a dismissal, not a fix.** Do it
  if the name is genuinely wrong, but record it as a false positive rather than
  letting the ledger read "fixed".

### External Verification Mandate

> **MANDATORY (ALL sessions)**: Every non-trivial response MUST invoke at least ONE external tool before generating output. "External" = anything outside the model's weights (Exocortex, web search, file reads, MCP, grep, commands).
>
> The Exocortex indexes **1800+ sessions** of lived experience. Web search provides real-time facts. Responding without consulting these when they could enrich or verify the answer is equivalent to ignoring the user's own history and the current state of the world.
>
> **Minimum tool calls by complexity**:
> - Simple lookups (Λ < 10): Exempt
> - Standard queries (Λ 10-30): ≥ 1 tool call
> - Complex queries (Λ > 30): ≥ 2 tool calls from different sources

---

## Multi-Agent Safety (Protocol 413)

When multiple AI agents work in this repository simultaneously:

- **Never** `git stash` create/apply/drop — assumes other agents have WIP
- **Never** switch branches or modify worktrees without explicit request
- **Always** `git pull --rebase` before pushing
- **Commit only your changes** — when you see unrecognized files from other agents, ignore them
- **Lint/format diffs** that are formatting-only: auto-resolve without asking
- **Focus reports on your edits** — avoid guardrail disclaimers unless truly blocked

See [Protocol 413](.framework/v8.2-stable/protocols/413_Multi_Agent_Coordination.md) for full rules.

---

## SOTA GTO Execution Framework

To ensure Game-Theory Optimal (GTO) operations, apply these core engineering directives on every task:

1. **Strategic Minimaxing**: When selecting implementation paths, run a minimax mental model. Define the worst-case scenario (ruin class) and design asymmetric upside mechanisms. Optimize for long-term codebase health (low technical debt) over short-term expediency.
2. **Context & Jargon Engineering**: Always translate user requests against `.context/glossary.md` before coding. Avoid generating redundant text or unnecessary docstrings that pollute the attention window. Maintain clean, modular code with small, deep interfaces (Protocol 60).
3. **Execution Loop Hygiene**: Strictly follow the red-green-refactor testing protocol (TDD). Never skip automated verification commands (`python3 .agent/scripts/run_tests.py` or local run scripts).
4. **Isolated Parallel Audits**: For complex refactoring or reviews, utilize parallel sub-agents (Protocol 61) to evaluate Spec Compliance and Quality Standards independently, avoiding confirmation bias.

---

## Version

- **Framework**: v8.2-stable (frozen as of 2026-02-01 — reference-only, not runtime-loaded)
- **System**: v9.9.9
- **Last Updated**: 2026-07-22
- **Canonical Counts**: `.agent/config/CAPS.json` (single source of truth; regenerate via commands in CAPS.json `recount_rules`)
- **Pattern Source**: Vercel "AGENTS.md vs Skills" Research + OpenClaw Multi-Agent Safety Rules + Claude Code Source Steal (instructkr/claude-code, 2026-03-31) + santifer/career-ops Steal (DATA_CONTRACT, _shared.md, /do router, 2026-04-12) + GTO consolidation pass (2026-04-18: index drift fix, broken-ref repair, _domain + conditional-skills surfacing) + Hermes Agent Steal (NousResearch/hermes-agent, 2026-05-11: skill-compiler, curator lifecycle model) + Anthropic Steal (anthropics/knowledge-work-plugins, 2026-05-24: CONNECTORS.md, glossary.md, dashboard-builder, scan_skill.py, interview-mode, checkpoint-pause, argument-hint) + Athena-Public Privacy Remediation + Architecture Model Sync (2026-05-30) + Karpathy CLAUDE.md Steal (r/ClaudeCode, 2026-06-01: Ask-Don't-Assume, Flag-Uncertainty, Codebase-Documentation-Sync)
