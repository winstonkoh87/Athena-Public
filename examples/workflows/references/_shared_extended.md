---
description: Extended JIT workflow references split from _shared.md and start.md under MinMax v2.0
created: 2026-11-14
last_updated: 2026-11-14
---

# Extended Workflow Reference (JIT-Loaded)

> Loaded on demand — not part of the Turn-1 boot payload. Referenced from [`_shared.md`](../_shared.md) and [`start.md`](../start.md).

---

## 1. Epistemic Status Convention (S534 — Anti-Self-Mythologizing)

Every protocol or system that claims a mechanism declares its enforcement status:

| Status | Meaning | How to treat it |
|:---|:---|:---|
| `code-enforced` | Script, hook, or CI gate runs automatically (verifiable in `.agent/scripts/` or `.agents/hooks.json`) | Trust as an active guard. |
| `code-available` | Deterministic script exists (`src/athena/` or `.agent/scripts/`), invocation is manual/agent-triggered | Invoke explicitly when triggered — does not run on its own. |
| `agent-discretion` | Heuristic the agent must choose to apply | Apply deliberately — nothing enforces it automatically. |
| `aspirational` | Documented target not yet implemented in code | Treat as a note, not a capability. |

**Rule**: If documentation claims "the system automatically monitors / emits" without hook or CI execution, relabel it on touch rather than propagating false assurance.

---

## 2. Artifact-Anchored Retrieval & Server-Side Constraints

1. **Constraints server-side; routing client-side**: Survival rules (Law #1 Ruin, credential protection, grounding) live in `mcp_server.py` instructions and `stop_governance_gate.py`.
2. **Artifact-anchored over intention-anchored**: All `plan.md` / `spec-driven-dev` artifacts MUST contain a `Grounding & Prior Precedents` block (missing block = malformed plan).
3. **Write-time memory scoping**: When filing via MCP or `quicksave.py`, declare `scope: project | platform | general`. Claims marked `verified` require terminal execution proof; claims marked `general` require an explicit domain-independence rationale.

---

## 3. UI & Deliverable Quality Standards

### Probabilistic Drift Cascade Invariant (`agent-discretion`)
Never ask an LLM to simultaneously invent layout hierarchy and apply styling tokens:
1. **Phase 1 — Structural Markdown Wireframe**: Lock container structure, milestones/sections, column responsiveness (desktop vs mobile), and explicit asset/copy/CTA slots before styling.
2. **Phase 2 — Design Token Injection**: Apply immutable CSS design tokens ([`Design_DNA.md`](../../../.framework/v8.2-stable/modules/Design_DNA.md), `/web-build` in `_domain/web-build.md`).

### UI Craftsmanship Standard & 5 Mandatory Component States (`agent-discretion`)
1. **Single-Sentence Purpose Test**: Every shadow, border, icon, or color accent needs a single-sentence functional justification.
2. **5 Component States**: Account for **Default**, **Loading** (skeleton loader), **Empty** (actionable next step), **Error** (clear cause + "Retry"), and **Success** (transient confirmation).
3. **Tabular Figures**: Numeric metrics, timers, timestamps, and data tables MUST use `font-variant-numeric: tabular-nums` (`tabular-nums`).
4. **Contrast**: Meet WCAG AA (4.5:1 text, 3.0:1 UI/large text) via `.agent/scripts/athena-py .agent/scripts/contrast_check.py <fg> <bg>`.
5. **Ergonomics**: Minimum 44x44px mobile touch targets; zero horizontal overflow (`overflow-x`).

---

## 4. Engineering Execution Rubrics

### Fast-Model Execution Rubric ("Scalpel vs. Surgeon", `agent-discretion`)
1. **Per-Item Inline Sticky Notes**: Annotate risky plan items with parenthetical warnings (`(Tricky: check X before modifying Y)`).
2. **Explicit Uncertainty Permission**: When links are unverified, state *"It is unknown whether X links to Y — verify via tool before modifying."*
3. **Graduated Complexity Staging**: Order steps from deterministic/low-entropy (schemas, scaffolding) to high-entropy (business logic, UI).
4. **Concrete Identifiers**: Name exact file paths, symbols, and functions.
5. **Known-Good Precedent Anchoring**: Point to an existing file exemplar to collapse formatting/schema variance.

### Anti-Abstraction Ladder ("Laziest Senior Dev", `agent-discretion`)
Before writing a new helper/class/component (and **after** reading target code), descend and stop at the first rung that holds:
1. `YAGNI` -> Skip if unnecessary now.
2. `Already here` -> Reuse existing repo utility.
3. `Stdlib` -> Use Python/JS stdlib (`pathlib`, `itertools`, `collections`, `json`, `urllib`).
4. `Platform` -> Use native platform primitives (`<dialog>`, `<details>`, `:has()`, `Intl.*`, container queries).
5. `Dependency` -> Use an already-installed package API.
6. `One-liner` -> Clean 1-2 line inline expression.
7. `Minimum` -> Write the smallest clean abstraction that works.
*(Safety carve-out: validation, data-loss prevention, security, accessibility, and error handling are never skipped.)*

---

## 5. Autonomous Multi-Agent Dispatch (3-Tier Compute Ladder)

`code-enforced` via `context_gate` (`compute_tier` + `SWARM DIRECTIVE` / `SUBAGENT DIRECTIVE` in `src/athena/mcp_server.py`). Never ask the user for dispatch permission or internal cutoff thresholds.

| Tier | Mechanism | Topology & State | Activation Triggers |
|:---|:---|:---|:---|
| **Tier 0: Inline** | Monolithic single agent | Shared context, zero startup tax | SNIPER (`Lambda < 10`), 1-2 file edits, sequential dependent steps, fast local scripts via `run_command`. |
| **Tier 1: Subagent Fan-Out** | `invoke_subagent` (`research`, `browser`, `self`) | Star topology (1-way return). Supports `Model: 'flash_lite'` (recon) and `Workspace: 'branch'`. | Multi-module recon (3+ dirs), detached browser/OSINT task, or 1-shot fresh verification without peer iteration. |
| **Tier 2: Native Swarm** | `swarm` (`native_swarm` + `swarm_monitor`) | Shared board, `@mention` doorbells, `workspace: 'share'`, `fork: 'coordinator'`. Leave `model` unset unless switching on quota exhaustion or user request. | Clears Swarm Gate (`>= 3` independent streams OR `Lambda >= 25` Author+Verifier loop, context `< 80%`). |

**5 Hidden Auto-Swarm Use Cases**:
1. Client & academic deliverables (`author` + fresh `spec-auditor`/`data-auditor` iterating until zero blockers).
2. Multi-module feature builds/refactors (partition file ownership, `workspace: 'share'` authors + `verifier` per 2-4 authors).
3. Multi-vector OSINT & research (2-3 domain scouts + `skeptic` enforcing `substance-decode`).
4. Dashboards & data reconciliation (`data-reconciler` + `ui-builder` + `qa-verifier`).
5. High-stakes strategic red-teaming (`Lambda > 30`: parallel `skeptic`, `base-rate-auditor`, `blast-radius` lenses).

**Negative Space (Stay Tier 0)**: `Lambda < 10`, deterministic 50ms Python scripts, strict sequential pipelines, context saturation `> 80%` or quota pressure (P517).
**UI Transparency**: Emit `🚀 Autonomously dispatching [N] subagents: ...` (Tier 1) or `🐝 Autonomously activating Native Swarm ([Title]): ...` + board link at turn end (Tier 2).

---

## 6. Adaptive Loading Matrix & Cluster Routing (Phase 2 & 3 of `/start`)

### Adaptive Loading Table (Load Only When Triggered)
| Trigger | File | Est. Tokens |
|:---|:---|:---|
| Trading, Risk, Pricing, Business, Psychology, Content | `CANONICAL_TIER2.md` | ~16K |
| Historical niche precedent | `CANONICAL_TIER3.md` | ~500 |
| Tag / file lookup | `PROTOCOL_SUMMARIES.md` | ~3,500 |
| Protocol / skill search | `smart_search.py --skills-only` | ~1,000 |
| Bio / typology | `User_Profile_Core.md` | 1,500 |
| [PRIVATE_MODULE], therapy, inner work | `[PRIVATE_MODULE].md` | 3,000 |
| Decision & strategy frameworks | `System_Principles.md` | 3,500 |
| Marketing, SEO, SWOT, pricing | `Business_Frameworks.md` | 2,500 |
| Calibration cases | `Session_Observations.md` | 2,500 |
| `/think`, `/ultrathink` | `Output_Standards.md` | 700 |
| Ethics / constraints | `Constraints_Master.md` | 800 |
| System architecture | `System_Manifest.md` | 1,900 |
| Active projects / context switch | `PROJECTS.md` | ~500 |

### Intent Archetypes & Cluster Co-Activation Chains (`CLUSTER_INDEX.md`)
- **Archetypes (`Lambda >= 10`)**: Survival -> `#14 -> P509 -> #15 -> #8 -> P506`; Life Decision -> `P509 -> P519 -> #15 -> #7 -> #9 -> #6 -> #8 -> P506`; Trading -> `#3 -> #4 -> #5 -> #9`; Social -> `P519 -> #15 -> #7 -> #6 -> #8 -> P506`; Execution -> `#15 -> #13 -> #11 -> #8`; Growth -> `#12 -> #10 -> #11 -> #8`; Learning -> `#12 -> #9 -> #15 -> #8`; Maintenance -> `#1 -> #2 -> #14`.
- **Cluster Fallback**: `#3/#4` Trading (`trading-risk-gate -> zenith-execution`), `#10` Distribution (`distribution-physics + brand-foundations + seo-auditor + claude-ads`), `#12` Research (`deep-research-loop + semantic-search`), `#13` Build (`P512 + spec-driven-dev + atomic-execution + micro-commit + visual-verify-ui`), `#6` Social Contract (`power-inversion + consiglieri-protocol`), `#9` Strategic Reasoning (`decision-journal + synthetic-parallel-reasoning`), `#7` Inner Work (`therapeutic-ifs`), `#11` Swarm (`marketing-swarm + git-worktree-swarm + P513`), `#15` Problem-Solving (`P504 + P115 + P505 + red-team-review + P506`).
- **Auto-Cascades**: Trading `#3 -> #4`; Marketing `#10 -> #11`; Deep Think (`Lambda > 30`) `#9 -> #8`; Problem -> `#15 -> GoT Phase 5 -> #8`; Crisis -> `P509 -> P519 -> #15 -> P521 -> P505/P520 -> #8`.

---

## 7. Formatting, Telemetry & Conventions

- **Artifact Naming**: Protocols `NNN-kebab-case.md`, Workflows `kebab-case.md`, Skills `kebab-case/SKILL.md`, Sessions `YYYY-MM-DD-description.md`, Case Studies `CS-NNN-kebab-case.md`.
- **Output Style**: Zero corporate filler ("leverage", "synergy", "robust", "seamless"), cite sources or tag `"internal estimate"` (Law #5), one-session-one-feature (`234`), separate De-Sloppify cleanup pass over negative prompt constraints (QUA-541).
- **Checkpoint Pause (`requires_approval: true`)**: Propose clearly, await explicit approval, never batch approvals, tag `[CHECKPOINT]` (applies to irreversible actions/deletions/deployments/spend; not read-only analysis).
- **`argument_hint` & Connectors**: Skills may declare `argument_hint: "<desc>"` and use `~~category` placeholders mapped in `.agent/CONNECTORS.md`.
- **Telemetry**: Claude Code auto-logs via `hook_log_invocation.py` (do not double-log). In hookless hosts (Antigravity), log manual workflow/skill invocations to `.athena/invocations.jsonl`:
  ```bash
  .agent/scripts/athena-py .agent/scripts/log_invocation.py --type workflow --name "<name>" --trigger "user command"
  ```
- **Reflexion Journaling (Protocol 515)**: On errors costing backtracking or >2 turns, append to `quicksave`:
  `[REFLEXION] What failed: <failure>. Why: <root cause>. Lesson: <preventive action>.`
