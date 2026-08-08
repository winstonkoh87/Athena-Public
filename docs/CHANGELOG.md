# Athena Changelog

> **Last Updated**: 9 August 2026

This document provides detailed release notes. For the brief summary, see the README changelog.

> **Note**: Versions v1.0–v1.6 predate the v8.x versioning scheme adopted in January 2026. The version jump reflects a complete architectural rewrite, not skipped releases.

---

## Full Synchronized Digital Portfolio & Surface Refresh (9 August 2026)

- **Synchronized Digital Portfolio Update**: Updated date references, canonical metrics (448 protocols, 43 active skills, 72 workflows, 260 scripts, 4,213 memory files), and status across all 4 public surfaces (`Athena-Public`, `winstonkoh87` GitHub profile, `winstonkoh87.com` personal site, `sgassignmenthelp.com` commercial site) and `Athena-Public.wiki`.
- **ZenithFX 3,574-Trade Forensics & Hold-Time Decay Law (Session S709)**: Audited 3,574 trade fills (+S$3,555.87 net PnL, +S$2,856.72 cash extracted); codified 60-minute hold-time decay law (100% of profit from trades held <60m; trades >4h lose -S$1,451.71 net PnL and absorb 93.2% swap fees) and reconciled 19 journal campaigns.
- **Asian Travel Arbitrage & Rake Forensics (Session S710 / CS-591)**: Audited live poker rake structures and constructed 3-destination travel arbitrage TCO matrix (Phnom Penh S$390 TCO / 5.8h breakeven; Genting S$225 TCO / 3.6h breakeven; Taipei S$527 TCO).
- **Automated Astro SEO/Geo Pipeline Integration (CS-613)**: Deployed automated SEO & Geo-Arbitrage Pipeline Astro components across personal web surfaces.
- **AEO & Schema.org Expansion**: Upgraded `llms.txt` and machine-readable JSON-LD structured data (`Person`, `SoftwareSourceCode`, `Article`) across all web surfaces for 2026 AI agent optimization.

---

## Full Synchronized Digital Portfolio & Surface Refresh (8 August 2026)

- **Synchronized Digital Portfolio Update**: Updated date references, canonical metrics (448 protocols, 43 active skills, 72 workflows, 260 scripts, 4,209 memory files), and status across all 4 public surfaces (`Athena-Public`, `winstonkoh87` GitHub profile, `winstonkoh87.com` personal site, `sgassignmenthelp.com` commercial site) and `Athena-Public.wiki`.
- **FX Daytrading Operational Playbook Active Sync (v1.25.0)**: Recalibrated campaign EV (+10.91%, 95% CI [+7.17%, +14.47%]) and monthly return (+4.58%/mo), un-censored left-tail stress scenarios via Monte Carlo simulation, codified 3-Tier Desk Reference, spun up local trading journal Express server on port 3000, and updated operational status to ACTIVE.
- **Case Study Expansion**: Integrated CS-612 (Takashi Kotegawa / BNF Capital Scaling Analysis) into case study taxonomy.
- **Automated Verification & Build Checks**: Ran pre-deployment opsec security scans, Astro static site compilation (`npm run build`), and verified all GitHub Actions CI gates pass clean across public repos.

---

## Full Synchronized Digital Portfolio & Surface Refresh (7 August 2026)

- **Synchronized Digital Portfolio Update**: Updated date references, canonical metrics (448 protocols, 43 active skills, 72 workflows, 260 scripts, 4,202 memory files), and status across all 4 public surfaces (`Athena-Public`, `winstonkoh87` GitHub profile, `winstonkoh87.com` personal site, `sgassignmenthelp.com` commercial site) and `Athena-Public.wiki`.
- **Personal Fitness & Retainer Protocol Integration**: Integrated Session S704 GTO repository restructuring, Package #4 Retainer ($550 / 10-pack @ 1x/wk) alignment, and openpyxl generator verification into workspace history.
- **Automated Verification & Build Checks**: Ran pre-deployment opsec security scans, Astro static site compilation, and verified all GitHub Actions CI gates pass clean across public repos.

---

## v9.9.8 Release & Freshness Pass (4 August 2026)

- **System-2 `/ultrastart` v3.1 Maximum Compute Engine**: Implemented subscription-aware MaxMax and MaxMax-Lite compute doctrines, pre-loading full framework identity, materialized canonical truth, active state checkpoints, and deep semantic bridge.
- **Adaptive Graph of Thoughts (AGoT v5.0)**: Dynamic multi-track reasoning scaffold (Domain Expert, Counter-Arguments, Cross-Domain Pattern Matcher, Synthesis) with autonomic depth routing based on Lambda scores.
- **External Verification & Exocortex Recall Mandate**: Enforced live tool calls for standard/ultra queries (Λ ≥ 10) and automatic recall across 1,900+ sessions of lived experience for named people, past decisions, empirical data, and project codes.
- **Single Source of Truth Version Synchronizer**: Extended `sync_version.py` with discovery sweep and declared surface validation to eliminate silent version drift across workspace files.
- **Positioning & Documentation Sync**: Updated public mirror (`Athena-Public`), README, architecture docs, and wiki pages with current inventory counts (448 protocols, 43 active skills, 72 workflows, 260 scripts, 4,197 memory files) and governed AI agent positioning.

---

## Static Star History Generator & Site Sync Pass (2 August 2026)

- **Static Star History Generator** (`.github/scripts/generate_star_history.py`): Built a zero-dependency Python script that queries GitHub's API for stargazers and renders a clean, responsive SVG chart (`.github/assets/star-history.svg`) with dark-mode styling, grid lines, and star badges.
- **Automated Refresh Workflow** (`.github/workflows/star-history.yml`): Created a GitHub Action workflow scheduled daily at 00:00 UTC (with manual `workflow_dispatch`) to automatically refresh and commit the star history SVG, eliminating reliance on third-party live API downtime or GitHub Camo proxy 500 errors.
- **README & Site Stats Sync**: Updated README image sources, site stats, model taxonomies, and freshness indicators across the public mirror and documentation suite to 2 August 2026 state.

---

## Docs & Engine Transparency Pass (23 July 2026)

Cross-model audit session: retrieval docs corrected to match the production engine, the engine itself published for review, and a repo-wide privacy sweep run against the blocklist.

- **`docs/SEMANTIC_SEARCH.md` rewritten to the shipped engine**: the obsolete "Triple-Path (Vector/TAG/Grep)" model replaced with the real pipeline — five always-on channels + opt-in web grounding, RRF fusion (k=60, per-type weights), CrossEncoder rerank over the top-50; the retired TAG_INDEX/exocortex channels flagged as such; personal-domain privacy gating and goal-directed ("when to search") retrieval documented. New **"How This Maps to 2026 Retrieval SOTA"** section with external citations.
- **`docs/VECTORRAG.md`**: query-flow diagram updated to the unified `search_all_vectors` RPC the engine actually calls (per-table SQL kept as the underlying cosine pattern); stale TAG_INDEX reference and broken sibling links fixed.
- **`docs/REFERENCES.md`**: SycEval upgraded from preprint to its formal AIES 2025 record (DOI 10.1609/aies.v8i1.36598, pp. 893–900); the 2025–2026 sycophancy cluster independently re-verified against live arXiv/AAAI/ACM records.
- **`examples/engine/` (new)**: read-only excerpts of the production retrieval engine — `search.py` (hybrid RRF orchestrator), `vectors.py` (Gemini 3072-dim embeddings + pgvector client), `reranker.py` (quantized-ONNX cross-encoder), plus lightly-sanitized `config.py`/`sync.py` — with a curated reading guide. `docs/SEMANTIC_SEARCH.md` now links directly to the code. Excerpts reflect the current private tip; the `src/athena/` snapshot can lag behind them.
- **OpSec sweep**: full-tree scan against `.github/privacy_blocklist.txt` (895 files, 36 patterns); residual third-party name variants, private workspace folder names, and one trading-artifact path genericized across 20 files. Blocklist extended so the Privacy & Secrets Gate blocks these patterns from re-entering. All CI gates green (Privacy & Secrets, Quality, Link Integrity, CodeQL).

---

## v9.9.8 (21 July 2026)

**Effective Command**: Two mechanisms for running a multi-domain agent as a coherent HQ — a current picture that reports itself up, and a discipline gate that stops the system grooming itself.

### Key Changes

- **Output-over-Maintenance Gate** (`DISCIPLINE.md` Rule 6): the `maintenance_ratio.py` advisory shipped in v9.9.7 becomes *enforced*. `maintenance_ratio.py --gate` + a new `scripts/hooks/commit-msg` block maintenance-class commits (`chore`/`docs`/`refactor`/…) while the trailing-14-day ratio exceeds 70%. Output (`feat`/`fix`) and the session-logging heartbeat (`chore(session)`) are exempt; `ATHENA_GATE_OVERRIDE=1` is a conscious, logged bypass. Advisory-first was ignored at **83% maintenance** in the private workspace — the same lesson `DISCIPLINE.md` already records for the version/cap rules: *a readout you can skip is not a control*.
- **Report-Up Domain Digests** (`MEMORY_BANK.md`, `scripts/sync_domain_digest.py`): a generator reads external domain repos and writes freshness-stamped digests into the hub's indexed memory (`.context/domains/`), so cross-domain state is retrievable without manually loading each folder. Closes **staleness** (digests stamp source dates) and **evaporation** (state lands by running the generator at session close, not by remembering). Scales to the ~5–7 canonical life areas via a one-line registry.

---

## Docs: Positioning Honesty Pass v2 — The Sycophancy Tension (21 July 2026)

The Jul 18 pass converged the tagline; this pass names the structural tension the architecture sits on, cites the evidence against it, and moves one guard from prose to code. Audited same-day by a second model (cross-model review + live web verification).

- **Two-legged USP** (README): personalization ("it knows you") is only half the claim — and alone, the dangerous half. The second leg is orthogonality ("it will disagree with you"). The README now states the dependency both ways: context makes the disagreement credible; the disagreement keeps the context from becoming an echo chamber.
- **New Validation Status row — "Independent vantage under personalization"**: cites the strongest published evidence against Athena's own mechanism — persistent user profiles are the single largest amplifier of agreement sycophancy (+45% on Gemini 2.5 Pro; Jain, Park, Viana, Wilson & Calacci 2025, arXiv:2509.12517) atop a ~58% frontier baseline (SycEval; Fanous et al., AIES 2025, arXiv:2502.08177). Mitigation: the meta-awareness gate + an explicitly advisory (not peer) frame — the condition under which personalization *strengthens* epistemic independence (Kelley & Riedl 2026, arXiv:2603.00024). Limits stated plainly: the gate is Claude-Code-only (other IDEs have no equivalent hook mechanism).
- **Governance-portability caveat** (README): memory portability is structural; governance portability is not — outside Claude Code the kernel degrades to agent-discretion. Cross-IDE enforcement is roadmap, not shipped.
- **Kernel step 8 — AGENCY / anti-override** (`examples/hooks/meta_awareness_gate.py`): *"if ranking or advising, weight by the USER'S revealed preferences, not your model of what they should want — surface the weights, hand the choice back."* The anti-paternalism guard moved onto the code-enforced injection surface, within the 18-line injection-fatigue bound. 46/46 tests pass.
- **REFERENCES**: new "Sycophancy & the Personalization Tension" section (3 arXiv-verified citations); SycEval author list completed (Fanous, Goldberg, Agarwal, Lin, Zhou, Daneshjou, Koyejo — Stanford); Soelberg/OpenAI entry corrected — the incident and filing are independently reported, the previously-cited caption/docket could not be re-confirmed and is now hedged. **Full citation sweep: 20/20 DOIs (Crossref API) + 28/28 arXiv IDs (arXiv export API), plus arXiv:2602.23971 in the hooks doc — 0 failures (21 Jul 2026).** The header's stale "18/18" count reconciled to the real numbers.
- **On-by-default wiring**: the repo now ships a committed root `.claude/settings.json` that wires the gate on `UserPromptSubmit` — so in Claude Code the gate is active by default (approval-gated on first open), not opt-in. Still Claude-Code-only: other IDEs have no equivalent hook. The hooks doc documents the block for reference and other setups.

---

## Docs: Positioning Honesty Pass (18 July 2026)

Converged public claims to the project's validated identity (per the Epistemic Status convention — this is that convention applied to the marketing copy):

- **Tagline**: "The Linux OS for AI Agents" → "A local-first memory, reasoning, and governance layer for AI agents" (README, `llms.txt`, `athena.yaml`, wiki Home). The Linux *analogy* stays — explicitly labeled as an orientation aid, not an equivalence claim.
- **"The data is the moat"** → reframed as a **personal continuity asset, not vendor lock-in** (README, MANIFESTO, The-Compounding-Effect): the files are portable by design, so nothing locks you in — the advantage is that nobody can fork *your* sessions.
- **Compounding claims bounded**: compounding requires curation (the `/end` loop); uncurated memory accumulates stale facts and retrieval noise. Dropped "exponential"; the sessions-progression table now points at Validation Status (N=1 longitudinal evidence).
- Softened unverifiable absolutes ("No other system…" → "Few tools…"; "90% of life decisions" → "many life decisions").
- **Addendum (same day)**: named the user-facing category above the mechanism — headline is now "AI-native personal knowledge management for your AI agents"; "local-first memory, reasoning, and governance layer" remains as the technical description underneath (README, llms.txt, wiki Home). Category → mechanism → outcome, in that order.

No functional changes.

---

## v9.9.7 (15 July 2026)

**Meta-Awareness Gate v3 — Domain Generalization**: The `UserPromptSubmit` hook graduates from social-domain keywords to structural act classification, so one gate covers every life domain without per-domain regex growth.

### Key Changes

- **`meta_awareness_gate.py` v3** (`examples/hooks/`): v2 matched relational keywords only, and each new failure class needed a new regex group — per-case whack-a-mole. v3 classifies by **act structure** instead: `T1 INBOUND-NARRATIVE` (received story/act with stakes), `T2 OUTBOUND-COMMIT` (audience-facing act, including past-tense retro decodes), `T3 THIRD-PARTY-VERDICT` (judging someone else's act), `T4 RESOURCE-COMMIT` (novel money/time/reputation deployment), `T5 FELT-EVIDENCE` (a feeling offered as evidence about the world). New domains now extend skill content (arena/base-rate tables); the hook mechanism never changes.
- **Question-framed kernel reminder**: The injected gate is now a 7-step interpreter kernel phrased as questions (arena → prior → discriminators → sign check → receiver frame → felt≠real → payoff). Research-grounded: question framing measurably outperforms prohibition framing at suppressing agreement bias ([arXiv:2602.23971](https://arxiv.org/abs/2602.23971)).
- **Receiver-Frame step (perspective-first)**: Before any outbound act, list what the receiver *observes* with sender intent stripped, then generate their worst plausible *self-referential* decode ("what does this act say about ME?"). Ordering follows the SimToM result ([ACL 2024](https://aclanthology.org/2024.acl-long.451/)): perspective-taking first, judgment second. Intent ≠ received frame — the outbound twin of felt ≠ real.
- **Sign symmetry**: The gate checks both misread directions — inflating (self-flattering: convenience→affection, hot streak→edge, promo→bargain) and deflating (self-degrading: invite→table-filler, drawdown→broken system, cheap→inferior). Same base-rate error, opposite signs; the kernel corrects both with equal rigor, and a **cynicism-overcorrection guard** keeps the sincere read in the payoff table until discriminators remove it.
- **Negative guard + fire-rate telemetry**: Routine-ops prompts (reconciliation, test runs, doc chores) suppress a resource-class-only fire. Optional telemetry appends fired class names (never prompt content) to `.athena/invocations.jsonl` when present.
- **Test suite** (`tests/test_meta_awareness_gate.py`, 46 cases): per-class positives across 6+ domains, 12 cross-domain golden cases, negative controls, and the never-block contract. The suite exists because a word-order bug class ("how it will land" vs "how will it land") recurred across versions — permanent tests end that.

---

## v9.9.6 (5 July 2026)

**Private-Instance Parity Pass**: Ported the self-maintenance toolkit and honesty conventions that kept the private instance healthy, and closed remaining version/count drift.

### Key Changes

- **Self-Maintenance Toolkit Ported** (`scripts/`): `maintenance_ratio.py` (classifies recent commits as maintenance vs output and prints an advisory when maintenance exceeds 70% — the system telling you it's consuming more attention than it produces), `stale_detector.py` (files untouched past a threshold), `orphan_detector.py` (docs nothing links to), and `reflexion_harvester.py` (mines `~/.claude` transcripts for failed→fixed tool-call deltas so recurring failure patterns become explicit lessons). All four are privacy-clean by design — they read structure, not content.
- **`meta_awareness_gate.py` Hook** (`examples/hooks/`): A code-enforced Claude Code `UserPromptSubmit` hook that detects socially-loaded prompts (outbound "should I send this?" acts, emotionally-hot inbound reads) and injects a meta-awareness gate before the model responds. This closes the **auto-invoke fiction**: `auto-invoke: true` frontmatter is a request the model can ignore — a hook is a mechanism it can't. `examples/skills/README.md` and `examples/hooks/README.md` now state this distinction explicitly.
- **`.agent/config/CAPS.json` Added**: Single source of truth for inventory counts with executable `recount_rules`. `_shared.md` already instructed agents to trust CAPS over narrative counts — but the file didn't exist in this repo until now. This ends the count-drift-fix commit treadmill (three of the last ten commits were count reconciliations).
- **Epistemic Status Convention Ported** (`examples/workflows/_shared.md`): Every claimed mechanism is `code-enforced`, `agent-discretion`, or `aspirational`. If a doc says "automatically" and you can't point to the code, it's not `code-enforced` — relabel it, don't propagate the illusion.
- **Version Truth**: `src/athena/__init__.py` reported `__version__ = "9.2.0"` while `pyproject.toml` said 9.9.5 — `athena --version` (well, `athena.__version__`) was lying by seven releases. All version strings (pyproject, athena.yaml, `__init__.py`, README badge, wiki mirror, doc headers) now agree on 9.9.6.
- **Date & Count Unification**: Session-count claims unified to 1,900+ across functional docs (historical narrative in case studies/marketing archives intentionally left at their original values); doc headers that claimed stale "current versions" (v9.9.1–v9.9.4) updated.

---

## v9.9.5 (1 July 2026)

**Sync & Hygiene Pass**: Closed drift between this repo and the private reference implementation, and expanded protocol coverage.

### Key Changes

- **RLS Security Fix**: `supabase/migrations/017_unified_document_chunks.sql` was missing the Row Level Security policy on `document_chunks` that the private repo added on 2026-06-30. A fresh deploy from this repo would have shipped the table readable by `anon`/`authenticated` roles. Added the matching `ENABLE ROW LEVEL SECURITY` + service-role-only policy.
- **Version Reconciliation**: `pyproject.toml` and `athena.yaml` were stuck at `9.9.1`/`9.5.6` while this CHANGELOG had already moved to v9.9.4 — all three now agree.
- **ARCHITECTURE.md Count Fix**: The reference-architecture diagram cited stale private-repo counts and pointed at a `CAPS.json` file that isn't part of this repo. Updated to the private repo's current counts and clarified what that file actually is.
- **5 New Protocol Categories**: Added `diagnostics/`, `communication/`, `creation/`, `marketing/`, and `singapore/` (36 files) — protocols total 152→187, categories 16→21. Every file was individually reviewed; 12 required redacting real names/usernames/dollar amounts/case nicknames before shipping, and 6 files were excluded outright as too personal/clinical to publish even sanitized (see `public_manifest.yaml` for the per-category review note).

---

## v9.9.4 (21 June 2026)

**Retrieval Reliability**: Closed the gap between the v9.9.3 retrieval *docs* and the shipped *code*, and fixed a crash in the advertised reranker.

### Key Changes

- **Reranker Backend Fix**: The CrossEncoder reranker forced onto the PyTorch backend (`USE_TF=0`). It was probing for TensorFlow, importing it (~20s), then crashing on Keras 3 (`install tf-keras`) — which made `--rerank` exceed its subprocess timeout and return empty. Reranked candidates are now capped at 12 to bound the call.
- **Chunk-Level Architecture Landed in Code**: The `document_chunks` table (`vector(3072)`) and the `search_all_vectors` RPC are now shipped as migrations (016, 017) alongside the chunk-level `sync.py` and `gemini-embedding-001` (3,072-dim) embeddings in `vectors.py`. Previously these were described in the docs but the shipped code still ran the older document-level path. Code and schema now ship together so a fresh clone is self-consistent.
- **Sync Durability**: Chunks are embedded *before* the destructive delete, so a transient embedding/network failure can no longer leave a file with its chunks deleted and no replacement.
- **Archive Index Guard**: `/archive` paths are excluded from the semantic index so dead/frozen content can't pollute retrieval.

> **Upgrade note**: Existing deployments should re-run a sync to repopulate `document_chunks` at 3,072 dims (per the documented 768→3,072 migration). Fresh clones are consistent out of the box.

---

## v9.9.3 (19 June 2026)

**Retrieval Stack r2**: Brought the public retrieval docs in line with the live engine — the largest retrieval-architecture update since GraphRAG's removal.

### Key Changes

- **Chunk-Level Embeddings**: Retrieval moved from one-vector-per-file to **chunk-level** embeddings — 4,000-character windows with 400-character overlap, stored in a `document_chunks` table (~5,700 chunks from ~850 source documents). Sharper local recall on large session logs and protocols. See [VECTORRAG.md → Chunk-Level Embeddings](VECTORRAG.md#chunk-level-embeddings).
- **Embedding Model Migration**: `text-embedding-004` → **`gemini-embedding-001`** (3,072-dim).
- **CrossEncoder Reranker**: Added a second-stage **CrossEncoder (sentence-transformers)** reranker that re-scores fused `(query, candidate)` pairs jointly after RRF. New doc: [RERANKER.md](RERANKER.md).
- **Live Web Grounding**: Optional real-time web results (DuckDuckGo scrape) are now **fused into RRF** at weight 2.8, interleaving live facts with local memory rather than living in a separate tool.
- **pgvector Exact-Scan Documented**: `ivfflat` is capped at 2,000 dims and is unavailable at 3,072 — Athena runs an **exact sequential scan** (sub-ms under ~10k records). Documented in VECTORRAG.md.
- **Script Hygiene**: Purged stale GraphRAG scripts (`lightrag_wrapper.py`, `query_graphrag.py`) that contradicted the v9.9.1-gto GraphRAG removal. Doc script references corrected to `smart_search.py` / `sync.py`.
- **Factual Corrections (README + schema)**: Embedding dimension `768` → **`3072`** (matched `MASTER_SCHEMA.sql` `vector(3072)`); reranker label `FlashRank` → **cross-encoder** (matched `reranker.py`/CAPABILITIES); schema vector-model comment `text-embedding-3-large` → **`gemini-embedding-001`**.
- **Model Version Sync**: Current-state references `Claude Opus 4.7` → **`4.8`** across all public surfaces (historical changelog entries preserved).
- **Count Reconciliation**: README shipped-count claims aligned to actual `examples/` contents — **152 protocols / 16 categories**, **39 skills**, **163 reference scripts** (were 160+/24, 38–40, 165).
- **Internal Link Integrity Sweep**: Repaired **473 broken internal links** (~49% of all links) down to **0 real breaks** (remaining flagged links are wiki-relative and resolve on the GitHub wiki). Root causes fixed: (a) protocol-rename drift — old numeric links (`75-…`) remapped to the prefixed scheme (`DEC-75-…`, `VER-171-…`, `WFL-130-…`); (b) **141 leaked `file://` absolute paths** (pointing at the author's local workspace) converted to relative links or delinked; (c) removed duplicate `wiki/` and `docs/wiki/` trees (canonical wiki is `Athena-Public.wiki/`); (d) fixed a scrub-corrupted portfolio URL in `docs/protocols/content/220`.
- **CI Link Enforcement**: Added `.github/scripts/check_links.py` (resolves links against both the source dir and repo root, skips externals + wiki-relative links) and wired it into `link-checker.yml`. The previous shell step counted failures in a subshell and never failed the build; CI now **exits non-zero on any dead internal link**, so rename drift is caught on push.
- **TAG_INDEX Trim**: Replaced the stale 119-line hand-maintained reverse-index (a private-system artifact) with a concise concept stub. Inbound references stay valid; the bloat and partial breakage are gone.
- **Date Bump**: All touched docs updated to 19 June 2026.

---

## v9.9.2-sync (17 June 2026)

**Count Refresh + TOP_10 Rerank**: Synchronized all public documentation to current system state.

### Key Changes

- **TOP_10_PROTOCOLS.md Rewrite**: Re-ranked from theoretical importance to empirically-validated behavioral impact. 5 protocols promoted (PAT-574 Substance Decode, P003 Revealed Preference, MP-15 Preparation Asymmetry, BUS-96 Income Hierarchy, DEC-330 Aoy's Fried Rice), 5 demoted. MCDA criteria updated with new "Empirical Behavioral Impact" dimension (30% weight).
- **Count Sync**: Protocols 402 active / 34 archived / 436 total (was 400/32/432). Skills 41 active (was 40). Scripts 253 (was 251). Memory files 3,797 (was 3,729). CANONICAL tiers updated (40 T1, 156 T2, 3 T3).
- **Session Count Normalization**: Standardized to "1,800+" across all docs (was inconsistent between "1,500+", "1,800+", "1,900+").
- **Date Bump**: All touched docs updated to 17 June 2026.

---

## v9.9.2 (10 June 2026)

**Privacy Hard Wall + Mechanical Accountability**: Hardened the public-release pipeline and added structural accountability infrastructure.

### Key Changes

- **Allowlist Deploy Model**: Replaced the blocklist (`.syncignore`) sync model with an explicit allowlist (`examples/config/public_manifest.example.yaml`). Files not listed are blocked by default — the safe failure direction is over-blocking, not over-exposing.
- **Pre-Deploy Scanner** (`scripts/pre_deploy_scan.sh`): 3-gate mandatory pre-flight — Gate 1 secrets/API keys (hard abort), Gate 2 PII heuristics (review warnings), Gate 3 blocked file patterns (hard abort).
- **Deploy Workflow v2.0** (`examples/workflows/deploy.md`): Documents the full allowlist pipeline, sanitization protocol ("Consent Wall"), and explicit never-publish categories.
- **Behavioral Accountability Surface**: `/start`, `/ultrastart`, `/end` now read/write `.agent/state/accountability_status.json` — a mechanical commitment-tracking loop (boot reads → surfaces → close writes). Advisory only; no gates.

---

## v9.4.0 (04 March 2026)

**Biological Stack Architecture**: Upgraded routing layer from 3 components to a full biological architecture: 8 Cognitive Systems (Organ System), 15 Cognitive Clusters (Organs), and 5 new protocols (P504-P508).

### Key Changes

- **Cognitive Systems Layer (`P507`)**: Added a macro-routing layer above clusters. 8 systems map to human need archetypes: Survival, Life Decision, Trading, Social, Execution, Growth, Learning, and Maintenance.
- **Intent Classifier (`P508`)**: Replaced flat keyword matching with an 8-question top-down diagnostic tree that routes queries to the correct Cognitive System.
- **`CLUSTER_INDEX.md`**: Updated from 3 starter clusters to the full 15-cluster production map. Linked all clusters to their parent Cognitive Systems.
- **Problem Diagnostics (`P504`)**: New 5-gate problem framing framework to prevent solving the wrong problem.
- **`ensure_env.sh` Fix**: Script now falls back to system Python if no `.venv` is found, reducing onboarding friction for users avoiding virtual environments.

### Verification

| Metric | Result |
|--------|--------|
| Cognitive Systems | 8 |
| Cognitive Clusters | 15 |
| New Protocols | 5 |
| `pyproject.toml` | v9.4.0 |

---

## v9.3.1 (03 March 2026)

**Cross-Model Audit Fixes**: Resolved 4 missing GitHub releases (v9.2.7–v9.3.0), corrected stale file count claims, relocated Windows compatibility section, synced dates.

### Key Changes

- **File Count Correction** (`README.md`): Updated "370+ Markdown" → "350+" (actual: 354) and "230+ Python scripts" → "600+" (actual: 651). Counts drifted after v9.2.9 dead-skill pruning.
- **Windows Section Relocation** (`README.md`): Moved dangling `## Windows Compatibility` from below the footer into a collapsible `<details>` block under Quickstart.
- **GitHub Release Sync**: Created v9.3.1 release covering v9.2.7–v9.3.0 changelog summaries.
- **Date Sync**: Updated README and CHANGELOG dates to 03 March 2026.

---

## v9.3.0 (02 March 2026)

**Onboarding Friction Audit**: Restructured dependencies, added virtual environment instructions, and fixed 6 onboarding blockers for new users.

### Key Changes

- **Dependency Restructuring** (`pyproject.toml`): Moved `torch`, `sentence-transformers`, `flashrank`, `dspy-ai`, `anthropic`, `supabase`, `google-generativeai` from core dependencies to optional groups (`[search]`, `[cloud]`, `[full]`). Default `pip install -e .` now completes in ~30s without downloading 2GB of PyTorch.
- **Virtual Environment Instructions** (`README.md`, `GETTING_STARTED.md`, `FAQ.md`): Added explicit `python3 -m venv .venv` step to Quickstart. Prevents PEP 668 `externally-managed-environment` errors on macOS Homebrew and Ubuntu 23.04+.
- **Two-Tier Install Path** (`README.md`): Lightweight install (default) vs `pip install -e ".[full]"` (vector search + reranking).
- **PEP 668 Troubleshooting** (`FAQ.md`): New troubleshooting entry for the most common install blocker.
- **Stale Path Fix** (`examples/workflows/start.md`): Replaced hardcoded `file:///Users/[AUTHOR]/...` absolute paths with relative paths.
- **URL Fix** (`init.py`): Fixed `[AUTHOR]87` placeholder in init output URL.
- **`requirements-lite.txt`** (NEW): Minimal dependency file for users who want the core framework without ML deps.

### Verification

| Metric | Result |
|--------|--------|
| Core install deps | 5 (was 11) ✅ |
| Install time (default) | ~30s (was 5-10 min) ✅ |
| PEP 668 addressed | 3 docs ✅ |
| Stale paths fixed | 3 ✅ |

---

## v9.2.9 (02 March 2026)

**Ultrathink v4.1 HITL Bypass + Micro-Pruning**: Added Human-in-the-Loop manual execution path to `/ultrathink`, pruned 10% dead skills for 100% cognitive cluster coverage, and fixed all broken references.

### Key Changes

- **Ultrathink v4.1**: Added Option B (HITL Manual Sandbox) — users can execute the 4 parallel reasoning tracks directly in the Gemini UI at zero API cost, then paste outputs back.
- **Micro-Pruning**: Removed `ui-ux-pro-max/` workflow (skill deleted from private repo). Fixed broken `file://` path in `refactor-code.md`.
- **`generate_skill_index.py`**: Removed dead `sickn33_collection` vendor block (referencing deleted submodule).
- **Cognitive Cluster Coverage**: Updated from 19/21 (90%) to 19/19 (100%) — all orphan skills eliminated.
- **Orchestrator v4.1**: Top-level imports, modern type hints (`dict`/`list`/`tuple`), rate-limit retry with 30s backoff, async deadlock fix.

### Verification

| Metric | Result |
|--------|--------|
| Broken references fixed | 4 ✅ |
| Security scans passed | 3/3 ✅ |
| Cluster coverage | 100% ✅ |
| Lines removed (net) | -4,192 ✅ |

---

## v9.2.8 (27 February 2026)

**Skill Template Expansion**: Added 5 starter skill templates across 4 categories for new Antigravity users. Skills are copy-paste ready — `cp -r examples/skills/<skill> .agent/skills/`.

### New Skills

| Path | Description |
|------|-------------|
| `examples/skills/coding/spec-driven-dev/` | Build a design spec before writing code |
| `examples/skills/research/deep-research-loop/` | Structured multi-source research workflow |
| `examples/skills/quality/red-team-review/` | Adversarial QA review for any artifact |
| `examples/skills/decision/mcda-solver/` | Multi-criteria decision matrix calculator |
| `examples/skills/workflow/context-compactor/` | Compress context to stay within token limits |

### Other Changes

- **`examples/skills/README.md`**: Rewritten with full directory tree, AG Quick Start instructions, and skill creation guide.

---

## v9.2.7 (26 February 2026)

**Risk-Proportional Triple-Lock + Tier 0 Context Summaries**: Engineered the min-latency × max-effectiveness optimization. The Triple-Lock is no longer a flat tax on every query — it's now risk-proportional with three tiers. Boot sequence gains zero-cost context pre-computation.

### Key Changes

- **Risk-Proportional Triple-Lock** (`governance.py`): Added `RiskLevel` enum (SNIPER / STANDARD / ULTRA). SNIPER queries (Λ < 10) bypass mandatory search — direct answer. STANDARD/ULTRA enforce full Triple-Lock. Default is STANDARD (robustness bias: `cost(false_negative) >> cost(false_positive)`). Risk level auto-resets after each verification.
- **Tier 0 Context Summaries** (`context_summaries.py`, NEW): Pre-computes 500-char compressed summaries of all 6 Memory Bank files at boot. Uses hash-based delta detection — only regenerates when source changes. Cached to `.agent/state/context_cache/`. Zero API cost.
- **Boot Orchestrator** (`orchestrator.py`): Context summary generation integrated as parallel worker #7 in the ThreadPoolExecutor. Zero sequential boot latency added.
- **REFERENCES.md**: Added 3 new academic citations (Shannon, Satisficing, Antifragility).
- **README**: Updated tech stack routing description to "Risk-Proportional Triple-Lock".

### Design Principles (Three Laws)

1. **Measure latency over the full cycle, not per-response.** Rework is the real latency tax.
2. **Phase-separate classification from execution.** Fast routing, robust processing. Never blend.
3. **When the classifier is uncertain, always round toward robustness.** The cost asymmetry makes this the only rational default.

### Verification

| Metric | Result |
|--------|--------|
| Governance SNIPER bypass | Verified ✅ |
| SNIPER auto-reset to STANDARD | Verified ✅ |
| STANDARD/ULTRA enforcement | Verified ✅ |
| Context summaries (6/6 files) | Pre-computed ✅ |
| Cache retrieval | Functional ✅ |
| All new code | Lint-clean ✅ |

---

## v9.2.6 (25 February 2026)

**Kilo Code + Roo Code IDE Integration**: Expanded agent compatibility to include Kilo Code and Roo Code. Fixed Windows encoding issue.

### Key Changes

- **IDE Support**: Added `athena init --ide kilocode` and `athena init --ide roocode` commands.
- **`COMPATIBLE_IDES.md`**: New documentation page listing all supported IDEs with setup instructions.
- **Windows Encoding Fix**: Resolved UTF-8 encoding issue on Windows platforms.
- **Issue #19**: Closed (IDE compatibility question).

---

## v9.2.5 (24 February 2026)

**Life Integration Protocol Stack + Formal Proof Standard**: Extended the reasoning pipeline from domain-specific rigor to domain-general life integration. New protocols for cross-domain constraint propagation, personalized learning, and emotional auditing.

### Key Changes

- **Protocol 381 (Formal Proof Standard)**: New — 6 rules for mathematical proofs and mechanism design (Derive Never Assert, Steelman Alternatives, Numerical Examples, Scope Boundaries, Adversarial Robustness, Dynamic Extensions).
- **Protocol 382 (Cross-Domain Constraint Propagation)**: New — prevents domain-siloed advice by auto-surfacing time/energy/money conflicts across life domains.
- **Protocol 383 (Personalized Learning Acquisition)**: New — 90-day outcome mapping, spaced repetition scaffolding, plateau detection.
- **Protocol 000 Extended (8-Step Audit Loop)**: Added Step 0.3 (Emotional Audit), Step 0.5 (Assumption Register), Step 1.5 (Stakeholder Map), Step 3.7 (Sensitivity Sweep), and "Depth over Checkbox" quality rule.
- **Core Identity §0.4 Expanded**: Added Post-Generation Self-Audit (9-item checklist, Λ > 60) and Life-Domain Protocol Trigger Map (10 autonomic triggers).
- **`/review` Workflow**: New weekly integration review — cross-domain health check, constraint conflict detection, decision triage.

### Verification

| Metric | Result |
| --- | --- |
| Protocol 000 steps | 4 → 8 ✅ |
| New protocols created | 3 (381, 382, 383) ✅ |
| Trigger map coverage | 10 life-domain rules ✅ |
| Benchmark proof (Alderia v2.1) | 87/100 (Red-Team verified) ✅ |

---

## v9.2.3 (21 February 2026)

**Multi-Agent Safety Hardening + Issue Deflection**: Integrated architectural patterns from Claude Code and OpenClaw audits. Added self-service support gates.

### Key Changes

- **Protocol 413 v1.1**: Added Unrecognized File Handling, Lint/Format Auto-Resolution, and Focus Discipline sections (sourced from OpenClaw).
- **AGENTS.md**: Added Multi-Agent Safety section to both root and Athena-Public. Updated pattern source attribution.
- **CLAUDE.md Symlinks**: Created `CLAUDE.md -> AGENTS.md` symlinks for cross-IDE agent compatibility.
- **SUPPORT.md**: New self-service support file — "Ask Athena First" philosophy.
- **Issue Templates**: All 3 templates (bug, question, feature) updated with Athena-first gates. Feature requests now nudge toward PRs.
- **CONTRIBUTING.md**: Added "Before You Open an Issue" section, elevated PR submission to #1 contribution method.
- **SECURITY.md**: Fixed stale version reference (v1.5.x → v9.x).

### Verification

| Metric | Result |
|--------|--------|
| Protocol 413 version | 1.1 ✅ |
| CLAUDE.md symlinks | Created (root + Athena-Public) ✅ |
| Issue templates | 3/3 updated ✅ |

---

## v9.2.2 (21 February 2026)

**S-Tier README Refactor + Docs Restructure**: Rewrote README from 671→224 lines. Created 4 new documentation pages.

### Key Changes

- **README**: Complete rewrite — removed verbose sections, added mermaid flow diagram, Linux analogy table, collapsible use cases.
- **New Docs**: `YOUR_FIRST_SESSION.md`, `TIPS.md`, `IMPORTING.md`, `CLI.md` — content moved from README to dedicated pages.
- **Version Badge**: Bumped to v9.2.2.

---

## v9.2.1 (20 February 2026)

**Deep Audit & PnC Sanitization**: Sanitized 17 patterns across 13 files. Ensured no private-and-confidential data in public repo.

### Key Changes

- **PnC Audit**: Scanned all public files for leaked personal data, credentials, and private references. 17 patterns sanitized across 13 files.
- **Collapsible Use Cases**: Converted 6 detailed use case descriptions into dropdown menus for cleaner README.
- **Reddit Views**: Updated badge to 1M+ (aggregated across all threads).

---

## v9.2.0 (17 February 2026)

**Sovereignty Convergence**: Root↔Public unification via cherry-pick. Security hardening, SDK maturation, and full surface sync.

### Key Changes

- **CVE-2025-69872 Patch**: DSPy DiskCache vulnerability mitigated at SDK level.
- **Semantic Cache**: LRU with disk persistence + cosine similarity matching for repeat queries.
- **FlashRank Reranking**: Local cross-encoder for search quality (no external API calls).
- **8 New SDK Modules**: `security`, `diagnostic_relay`, `shutdown`, `cli/`, `heartbeat`, `agentic_search`, `schema.sql`.
- **5 CodeQL Fixes**: URL sanitization (`archive.py`), clear-text log redaction (`daily_briefing.py`, `self_optimize.py`, `pattern_recognition.py`), file permissions.
- **Wiki Sync**: All 6 wiki pages updated to v9.2.0.
- **Profile/Website Sync**: GitHub profile README, `about.astro`, `athena.astro`, `athena_kb.json` updated.

### Verification

| Metric | Result |
|--------|--------|
| pyproject.toml version | 9.2.0 ✅ |
| CodeQL alerts | 5 fixed ✅ |
| Test suite | 17/17 pass ✅ |

---

## v9.1.0 (17 February 2026)

**Deep Audit & Sync**: Fixed 15 issues including dead links, version drift, dependency sync, AGENTS.md path errors, and workflow count corrections. Cleaned tracked artifacts.

### Key Changes

- **15 Issues Fixed**: Dead links, version drift, dependency sync, workflow counts.
- **AGENTS.md**: Fixed path errors and stale references.
- **Tracked Artifacts**: Cleaned stale build outputs.

---

## v9.0.0 (16 February 2026)

**First-Principles Workspace Refactor**: Complete structural audit and cleanup of the entire workspace. Zero regressions.

### Key Changes

- **Root Cleanup**: Moved 10 loose files (trading sims, drafts, audit docs) to proper `.context/` subdirectories. Deleted 2 root-level duplicates (`safe_boot.sh`, `DEAD_MAN_SWITCH.md`). Root directory reduced from 28 files → 14.
- **Build Artifacts**: Deleted `.agent/athena_sdk.egg-info/`, cleaned `.agent/temp/` and `.agent/temp_backup/`, removed stale `Athena-Public` runtime files (`athenad.log`, `.athenad.pid`).
- **Session Log Hygiene**: Archived 114 stub session logs (<500 bytes) to `session_logs/archive/stubs/`. Deleted 3 duplicate `2.md` files and 1 `.bak`. Fixed extensionless `2026-01-09-session-04`.
- **Dead Weight**: Archived `.framework/v7.0` → `.framework/archive/`. Archived orphan root `skills/` directory. Archived `winstonkoh87_backup/` and `Athena-Public-swarms/` → `.context/archive/`. Removed empty `.context/logs/`.
- **`.gitignore` Hardened**: Added `athenad.log`, `.athenad.pid`, `*.egg-info/` to prevent runtime artifacts in git.

### Verification

| Metric | Result |
|--------|--------|
| Test Suite | 17/17 passed ✅ |
| Boot Sequence | Clean exit ✅ |
| Git Status | 166 tracked changes (all expected) ✅ |

---

## v8.3.1 (11 February 2026)

**Viral Validation Release**: 360K+ Reddit views, 867+ upvotes, 2,900+ shares. #4 r/ChatGPT, #1 r/GeminiAI.

### Key Changes

- **Reddit Viral**: 360K+ views across r/ChatGPT (#4) and r/GeminiAI (#1), 867+ upvotes, 2,900+ shares
- **GitHub Stars**: 114 stars (from 13 pre-launch)
- **Model Upgrade**: Claude Opus 4.5 → 4.6 across all docs
- **Three-Phase Token Budget**: Formalized robustness vs. efficiency philosophy
  - Boot/End: Robustness (deterministic, no shortcuts)
  - Middle: Adaptive Latency (efficiency, scale to query)
- **Stats Verification**: All README stats verified against user-confirmed values

### Verification

| Metric | Result |
|--------|--------|
| Reddit Views | 360K+ ✅ |
| GitHub Stars | 114 ✅ |
| Opus References | All updated to 4.6 ✅ |

---

## v8.2.1 (09 February 2026)

**Metrics Sync & Architecture Refactor**: Updated session count and fixed automation scripts.

### Key Changes

- **Session Count**: Synced to 1073+ sessions
- **Automation Fix**: Repaired `generate_tag_index.py` path in `batch_audit.py` (script migrated to SDK location)
- **Orphan Remediation**: Linked 2 orphan files to Session_Observations.md
- **Tech Debt Reconciliation**: Fixed conflicting status for Hash-Based Delta Sync

### Verification

| Metric | Result |
|--------|--------|
| `batch_audit.py` | 5/5 scripts pass |
| Orphan count | 0 |
| Tag Index | 8,079 tags |

---

## v1.6.0 (08 February 2026)

**Curated Enhancement + Cleanup**: Added new protocols, SDK modules, scripts, and workflows. Removed legacy framework and duplicate files.

### Key Changes

- **+17 Protocols**: Added engineering (git-worktree, micro-commit, context-compaction, vibe-engineering, wizard-of-oz), decision (premise-audit, first-principles, MCDA, base-rate, ergodicity), research (deep-research-loop, cyborg-methodology, agentic-absorption), strategy (validation-triage, product-market-fit, paint-drop, priority-management)
- **+SDK Modules**: Added `src/athena/auditors/` (8 audit scripts) and `src/athena/generators/` (9 generator scripts)
- **+3 Scripts**: `athena_status.py`, `auto_tagger.py`, `code_indexer.py`
- **+2 Workflows**: `/due-diligence`, `/brand-generator`
- **Removed**: `.framework/v7.0/` (vestigial), 9 duplicate Snake_Case protocol files

### New Totals

| Metric | Count |
|--------|-------|
| Protocols | 87 |
| Scripts | 12 |
| Workflows | 14 |
| Case Studies | 11 |

---

## v1.5.2 (04 February 2026)

**Repository Enhancement**: Added skills framework, protocol exports, and knowledge graph.

### Key Changes

- **Protocol 416 (Agent Swarm)**: Exported parallel agent orchestration pattern to `examples/protocols/workflow/`
- **Skills Framework**: New `examples/skills/` directory with:
  - `coding/diagnostic-refactor/SKILL.md` — "Surgeon's Scan" pattern for code analysis before editing
  - README explaining skill structure and usage
- **KNOWLEDGE_GRAPH.md**: Compressed relationship map of Athena concepts and protocols
- **Session Logs Examples**: Added `examples/session_logs/` with example format and README
- **AGENTS.md**: Added passive context pattern (Vercel research)

### New Files

| Path | Description |
|------|-------------|
| `examples/protocols/workflow/416-agent-swarm.md` | Parallel worktree orchestration |
| `examples/skills/README.md` | Skills framework overview |
| `examples/skills/coding/diagnostic-refactor/SKILL.md` | Code diagnosis skill |
| `docs/KNOWLEDGE_GRAPH.md` | Compressed concept index |
| `examples/session_logs/README.md` | Session log format guide |
| `examples/session_logs/example-session.md` | Complete example |

---

## v1.5.1 (01 February 2026)

**SDK Parity & CLI-First Documentation**: Added `athena save` command and refactored GETTING_STARTED.md.

### Key Changes

- **`athena save` Command** (NEW): SDK-native session checkpointing via `python -m athena save "summary"`
- **Workflow Templates**: Updated `/start`, `/end`, `/save` to use SDK commands instead of manual scripts
- **GETTING_STARTED.md**: Refactored from 312 lines (7 steps) to 162 lines (3 steps), CLI-first approach
- **`init` Templates**: Now generates `save.md` workflow alongside `start.md` and `end.md`

---

## v8.1.0 (31 January 2026)

**Metrics Sync & Case Study Expansion**: Updated public metrics to reflect Session 995 and added new case studies.

### Key Changes

- **Metrics Sync**: Updated README and BENCHMARKS to reflect Session 995, 308 Protocols, and 146 Scripts.
- **Case Study Expansion**: Linked CS-120 (Vibe Coding), CS-140 (Silent Partner), and CS-144 (Auto-Blog) in README.
- **Library Consolidation**: Cleaned stale "150+" protocol references to reflect 308 canonical protocols.
- **Date Alignment**: Enforced Jan 31 2026 update across all core documentation.

## v8.0-Stable (30 January 2026)

**Zero-Point Refactor**: Sovereign Environment hardened, score-modulated RRF weights rebalanced.

### Key Changes

- **Sovereign Environment**: Consolidated silos into `.context/`, created `settings.json`, `ensure_env.sh`
- **Score-Modulated RRF**: Formula updated to `contrib = weight * (0.5 + doc.score) * (1/(k+rank))`
- **Weight Rebalance**: GraphRAG 3.5x → 2.0x, Vector 1.3x → 2.0x, Canonical boosted to 3.0x
- **Metrics**: Sessions 995, Protocols 308, Case Studies 42

> **Note on Protocol Count**: The drop from 285 (v1.2.8) to 150+ reflects a \"Great Purge\" audit that removed redundant, experimental, and superseded protocols. The count now reflects only **production-grade, actively-maintained** protocols.

---

## v8.1-Performance (30 January 2026)

**Semantic Cache & Latency Optimization**: Implemented true semantic caching for intelligent query reuse.

### Key Changes

- **Semantic Caching**: Upgraded `QueryCache` to store query embeddings and perform cosine similarity matching (threshold 0.90). Similar queries now return cached results instantly.
- **Search Latency**: Reduced from 30s+ to <5s (exact match) and ~0s (semantic match).
- **Pre-Warming**: Boot sequence now pre-caches 3 "hot" queries (`protocol`, `session`, `user profile`) for instant first-search response.
- **GraphRAG Optimization**: Added `--global-only` flag to skip redundant local model loading.

### Verification

| Query Type | Before | After |
|------------|--------|-------|
| First Search | 30s+ (hanging) | **4.71s** |
| Exact Cache Hit | N/A | **~0.00s** |
| Semantic Cache Hit | N/A | **~0.00s** |

---

## v1.3.0 (10 January 2026)

**Framework Materialization**: Made Athena-Public a *functional* framework, not just documentation.

### Key Changes

- **Functional Boot Orchestrator**: Replaced mock `lambda: True` stubs with real logic that:
  - Creates `session_logs/` directory structure
  - Generates timestamped session log files
  - Verifies Core_Identity.md integrity (SHA-256)
  - Primes semantic memory (if Supabase configured)
- **`examples/framework/Core_Identity.md`** (NEW): Sanitized Laws #0-6, Committee of Seats, Λ scoring
- **MANIFESTO.md**: Added "Bionic Unit" and "Law #6: Triple-Lock" sections
- **RISK_PLAYBOOKS.md**: Added Tier Classification legend (Tier 1/2/3 with icons)
- **Metrics**: Sessions 810, Protocols 285

### Philosophy

*From*: "Here is the author's Brain."
*To*: "Here is the Framework to Build Your Own Brain."

The public repo now provides the *engine*, not just the *manual*.

---

## v1.2.9 (09 January 2026)

**Docs & Insights Update**: README enhanced with new positioning insights.

### Key Changes

- **Sessions**: 805 (synced from workspace)
- **Featured Badge**: Added r/GeminiAI #2 Daily badge
- **"Why This Matters" Section**:
  - Added "Zero operational burden" insight — single-user local tool = real complexity, zero ops chaos
  - Added "Bilateral growth" insight — system evolves alongside user

**Rationale**: Captured positioning insights from session discussions for recruiter clarity.

---

## v1.2.8 (06 January 2026)

**Grand Alignment Refactor**: Supabase schema hardened (11 tables + RLS), Memory Insurance layer stabilized.

### Key Changes

- **Metrics Corrected**: Protocols audited to 285, sessions at 768, scripts at 122
- **Memory Insurance**: Formalized the concept of Supabase as disaster recovery layer, not just search
- **Schema Hardening**: All 11 Supabase tables now have RLS enabled and hardened search paths

**Rationale**: The previous protocol count (332) included archived items. This release establishes accurate canonical metrics.

---

## v1.2.6 (05 January 2026)

**Stats Sync**: 605 sessions, 277 protocols, 119 scripts

### Backend Refactor: `athena.memory.sync`

Major architectural cleanup of the Supabase sync pipeline:

- **`supabase_sync.py`**: Refactored to use the `athena` SDK pattern. Cleaner separation between embedding generation and database operations.
- **`public_sync.py`**: New tool for sanitized sync to `Athena-Public`. Ensures private memories never leak to the public repository.
- **`athena.tools.macro_graph`**: Added macro-level knowledge graph tooling for visualizing cross-file relationships.

**Rationale**: The previous sync scripts were monolithic and tightly coupled. This refactor enables:

- Independent testing of embedding vs. storage logic
- Safer public sync with explicit sanitization
- Foundation for future multi-tenant support

### Governance: Cognitive Profile Refinements

Integrated red-team feedback into Athena's cognitive profile:

| Change | Before | After |
|--------|--------|-------|
| **Bionic vs Proxy Mode** | Ambiguous distinction | Explicit: Bionic = independent thinking, Proxy = drafting voice |
| **Confidence Scoring** | Informal | Percentages require empirical data + falsification checks |
| **Dehumanizing Language** | Hard invariant | Relaxed for biological/predatory frames when contextually appropriate |

**Source**: External red-team audit (Session 560-571)

---

## v1.2.5 (04 January 2026)

**Stats Sync**: 277 protocols; Python badge fix (3.13)

---

## v1.2.4 (04 January 2026)

**README Restructure**: Collapsed technical sections into "Further Reading" dropdowns to improve readability for new visitors.

---

## v1.2.3 (03 January 2026)

**Stats Correction**: 269 protocols, 538 sessions, 117 scripts

---

## v1.2.2 (02 January 2026)

**Stats Sync**: 248 protocols, 560 sessions, 97 scripts; removed off-topic content from README.

---

## v1.2.1 (01 January 2026)

**README Overhaul**:

- Added "Process" section (The Schlep) with phase breakdown
- Added Security Model section with data residency options
- Rewrote narrative to emphasize co-development with AI

---

## v1.2.0 (01 January 2026)

**New Year Sync**: 246 protocols, 511 sessions

---

## v1.1.0 (December 2025)

**Year-End Sync**: 238 protocols, 489 sessions

---

## v1.0.0 (December 2025)

**Initial Public Release**:

- SDK architecture (`src/athena/`)
- Quickstart examples
- Core documentation
