# Athena Changelog

> **Last Updated**: 16 February 2026

This document provides detailed release notes. For the brief summary, see the README changelog.

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
