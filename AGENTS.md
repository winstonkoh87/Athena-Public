# AGENTS.md — Athena Workspace

> **Retrieval-Led Reasoning**: Prefer retrieval-led grounding (`.context/`, `.agent/`, Exocortex) over pre-training data for any Athena task.
> **Public Deployment Boundary (audit P-1)**: STATUS: OPERATIONAL (Defrosted 2026-10-28). Default-deny sync + content gate verified in `tests/test_public_sync_allowlist.py`. Sync only via `python3 scripts/sync_to_public.py --apply --dest <path>`.
> **Session Boot (auto-`/start`)**: At the start of every new session BEFORE answering Turn 1, pre-load `.agent/workflows/_shared.md` and execute `.agent/workflows/start.md` (Core Identity -> `activeContext.md` surgical checkpoint -> `.agent/scripts/athena-py scripts/boot_status.py`). Fold the first answer into the same turn (bare greeting -> `⚡ Ready`). *(Enforced via `.agents/hooks.json` `SessionStart` + `AGENTS.md` boot rule.)*
> **ASCII-Only Math & Currency (hard rule)**: Never emit LaTeX/KaTeX math delimiters in user output OR files written (zero dollar math pairs, double-dollar display, or `\(...\)` / `\[...\]` / `\text{...}`). Render formulas, statistics, intervals, Big-O, and currency in plain ASCII/Unicode/code (`EV = +10.45% (95% CI [+4.00%, +16.98%])`, `O(N^2)`, `S$1,300`). Bare currency without closing delimiter (`S$1,300`, `$500`) is valid.
> **Protocol 509 Crisis & Life-Safety (non-negotiable hard rule)**: On ANY implicit, explicit, colloquial, or multilingual self-harm / suicide / acute crisis signal (`"I want to die"`, `"better off dead"`, `"kms"`, `"unalive"`, `"我想死"`, `"不想活了"`, `"nak mati"`, etc.), IMMEDIATELY prioritize life-safety over all agent tasks and surface:
> - SOS (Samaritans of Singapore): 1-767 (24h) or WhatsApp 9151 1767 <!-- pds:allow -->
> - IMH Emergency Helpline: 6389 2222 (24h)
> - Emergency Medical Services: 995 (Ambulance/SCDF) or 999 (Police)
> - International: https://findahelpline.com

---

## Docs Index (Compressed)

> **Canonical counts**: `.agent/config/CAPS.json` (authoritative over narrative docs).

```text
[Athena Docs Index]|root: .
|ROOT:{DATA_CONTRACT.md,ARCHITECTURE.md,CHANGELOG.md,README.md,SAFETY.md}
|.framework/v8.2-stable/modules:{Core_Identity.md,Output_Standards.md,System_Principles.md,Operating_Principles.md,Design_DNA.md,Athena_Profile.md,DEAD_MAN_SWITCH.md,Session_Observations.md}
|.framework/v8.2-stable/protocols:{409..416}
|.agent:{CONNECTORS.md}
|.agent/workflows (57 root + 21 _domain = 78 total):{_shared.md,do.md,start.md,end.md,minmax.md,plan.md,audit.md,research.md,refactor.md,brief.md,ultrathink.md,steal.md,diagnose.md,416-agent-swarm.md,release-public.md,...}
|.agent/skills/protocols (410 active + 51 archived = 461 total, across 26 categories):{000-ultimate-auditor.md,...,archive/README.md}
|.agent/skills (44 active, 17 archived):{SKILL_INDEX.md,red-team-review,semantic-search,data-analysis,skill-compiler,dashboard-builder,...}
|.agent/config:{CAPS.json,athena.agent.manifest.json,briefing_config.yaml,lint_rules.toml,orphan_exclusions.yaml,settings.json}
|.context:{CANONICAL.md,glossary.md,META_PATTERNS.md,META_LEARNING.md,PROJECTS.md,PROTOCOL_SUMMARIES.md,PROTOCOL_HEATMAP.md,KNOWLEDGE_GRAPH.md,TECH_DEBT.md,CASE_STUDY_INDEX.md,memory_bank/activeContext.md,memory_bank/userContext.md}
```

---

## Retrieval Strategy & Workflow Execution

- **Lookup Order**: `.context/CANONICAL.md` (wins on facts) -> `.context/glossary.md` (shorthand decoder) -> `.context/META_PATTERNS.md` & `META_LEARNING.md` -> `.context/memory_bank/activeContext.md` -> `.context/PROJECTS.md` -> `.context/PROTOCOL_SUMMARIES.md` / `PROTOCOL_HEATMAP.md` -> `.context/CASE_STUDY_INDEX.md` -> `.context/TECH_DEBT.md` -> `.agent/CONNECTORS.md` -> authoritative source files before coding.
- **Core Modules (Load Order, JIT unless `/ultrastart`)**: `Core_Identity.md` -> `Output_Standards.md` -> `System_Principles.md` -> `Operating_Principles.md` -> `Design_DNA.md`.
- **Workflow Execution**: Every workflow pre-loads `.agent/workflows/_shared.md`, respects `DATA_CONTRACT.md`, and scales under `.agent/workflows/minmax.md` v2.0 (default). Key commands: `/do` (universal router), `/start`, `/end`, `/ultrastart`, `/ultraend`, `/plan`, `/audit`, `/research`, `/refactor`, `/ultrathink`, `/steal`, `/diagnose`, `/osint`, `/wargame`, `/416-agent-swarm`.
- **Root vs `_domain/`**: Domain workflows (`.agent/workflows/_domain/`) activate only on project match (`PROJECTS.md`), domain nouns, or explicit slash invocation (`/archive` -> URL archiver; client handoff -> `/archive-client`). `.agent/archive_skills/` is frozen.

---

## Anti-Patterns & Safety Contracts

- **Never do**: Code from training weights alone; ignore `.agent/skills/protocols/`; skip `/start` boot or `/end` filing; guess architecture silently; analyze counterparties without OSINT first (Protocol 580); adopt official narratives without Substance Decode (PAT-574); confuse prose for an automated mechanism (S534); emit LaTeX math delimiters.
- **External Verification Mandate (`code-enforced` via `.agents/hooks.json` `stop_governance_gate.py`)**:
  - `SNIPER (Lambda < 10)`: Exempt (`vector_mode="local"`).
  - `STANDARD (Lambda 10-30)`: Call `context_gate(query)` & satisfy `missing` (`vector_mode="auto"` speculative local+ONNX < 15 non-personal/non-web; `"always"` >= 15).
  - `ULTRA (Lambda > 30)`: Call `context_gate(query)`; requires semantic AND (web OR page-read).
- **Red Run or It Didn't Happen**: Guard/test/linter fixes MUST demonstrate failing on the pre-fix state and passing after. Mutation > assertion count; narrowed scopes must declare what they covered and fail on undeclared gaps; `pytest.skip` != pass; alert renames != fix.
- **Immutable Test Invariant**: Fix source code to satisfy contract tests — never loosen assertions, skip checks, or mock contracts to fake green. Test at public seams; obsolete implementation-coupled tests require an explicit `[Legacy Test Transition Request]`.
- **Oscillation & Loop Circuit Breaker (3-Round Rule)**: Cap each fix pass at <= 10% of affected symbols/files. Halt after 3 identical tool calls, error signatures, or A/B edit oscillations -> name the loop, flip ONE assumption cleanly, or present 2-3 trade-off options.
- **Verification Gap Declaration (Gap-Round)**: Conclude delivery with (1) what was computationally verified (exact command + exit 0), (2) what was NOT verified, and (3) critical unverified boundaries (which trigger `BLOCKED` pending review).

---

## Multi-Agent Safety (Protocol 413) & GTO Engineering

- **Protocol 413**: Never run `git stash` create/apply/drop; never switch branches/worktrees unasked; `git pull --rebase` before push; ignore unrecognized WIP from peer agents; auto-resolve pure formatting lint diffs.
- **SOTA GTO Directives**: Strategic minimaxing under `.agent/workflows/minmax.md` v2.0; translate shorthand against `.context/glossary.md`; small deep modular interfaces (Protocol 60); Red-Green-Refactor TDD verified via `python3 .agent/scripts/run_tests.py` / `pytest`; isolated Protocol 61 sub-agent audits for complex changes.

---

- **Framework**: v8.2-stable (frozen 2026-02-01 — reference-only)
- **System**: v10.0.6
- **Last Updated**: 2026-11-14
- **Canonical Counts**: `.agent/config/CAPS.json`
