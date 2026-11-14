# Athena — Architecture Reference

> **Last Updated**: 14 November 2026
> **Version**: v10.0.6
> **Canonical Counts**: See `.agent/config/CAPS.json` — if numbers in this file diverge, CAPS wins.
> **Bionic Unit Spec**: `BIONIC_UNIT_SPEC.md` (private workspace) — the definitive human-AI augmentation mapping

---

## Workspace Structure

```
Athena-Public/                       # Clean-lobby repository (32 tracked root entries)
├── .agent/                          # Core runtime configuration
│   ├── config/                      #   CAPS.json, ag_middleware.json, gate_config.json, harness_scorecard.yaml
│   └── scripts/lib/                 #   Compatibility shims (jsonl_tail.py -> athena.core)
├── .context/                        # Reference context & architecture templates
├── .framework/                      # v8.2-stable core reference modules (frozen)
├── .github/                         # CI workflows, templates, CODEOWNERS & governance docs
├── data/                            # Static reference datasets
├── docker/                          # Containerized deployment & sandbox configs
├── docs/                            # 50 top-level guides (89 files)
├── examples/                        # Reference workflows, protocols, skills, case studies & scripts
│   ├── workflows/                   #   78 slash-command workflow templates (minmax, ultrastart, ultraend, ...)
│   ├── scripts/                     #   Reference automation & audit scripts (ucds_audit.py, wargame_runner.py, ...)
│   ├── skills/ & protocols/         #   44 skills & 410 active protocols (26 categories)
│   └── case_studies/, demos/, templates/
├── scripts/                         # 50 curated public runtime scripts (boot_status.py, hook_stop_verify.py, harness_score.py, ...)
├── src/                             # Athena SDK source (113 Python files across 11 subpackages)
│   └── athena/                      #   auditors, boot, cli, core, eval, generators, intelligence, lifecycle, memory, templates, tools
├── supabase/                        # Cloud vector store schema & RPC migrations
├── tests/                           # Public test suite (59 Python files)
├── AGENTS.md                        # System boot & governance entrypoint
├── CLAUDE.md                        # Symlink -> AGENTS.md
├── ARCHITECTURE.md                  # This file
├── CHANGELOG.md                     # Release history
├── DATA_CONTRACT.md                 # Data governance & schema contract
├── SAFETY.md                        # Life-safety, ruin prevention & crisis guardrails
├── README.md                        # Public repository overview
├── athena.yaml / pyproject.toml     # SDK & runtime manifests
└── Makefile / LICENSE / llms.txt    # Build targets, MIT license & LLM index
```

> **Canonical Counts (`CAPS.json`)**: `410 active + 51 archived = 461 protocols (26 categories)`, `44 active skills (17 archived)`, `78 workflows (57 root + 21 _domain/)`, `629 case studies`, `177 CANONICAL Section 4 entries`. See [`.agent/config/CAPS.json`](.agent/config/CAPS.json).
> **Decoupled Workspaces (External)**:
> - **FX Trading Desk**: Isolated external workspace. Athena supplies cognitive governance, risk gates (`trading-risk-gate`, `structural-trading-gate`, `trade_guardian.py`), and variance shields (Law #1), while execution scripts and tick logs stay separate.
> - **Media Production**: Centralized external pipelines (`imagen-studio`, `veo-choreographer`, Remotion). Binary renders and audio assets are excluded from the core repository.

---

### Cognitive Stack — Perception Model (v10.0.6)

> Modeled after human sensory processing: **Parallel Activation → Attention Gate → Executive Function → Response**.
> The brain doesn't classify-then-route; it activates-then-filters. Athena's runtime works the same way.
> *(Epistemic status tags: `[code-enforced]` = deterministic script/gate; `[agent-discretion]` = heuristic applied by the LLM; `[aspirational]` = planned mechanism).*

```
                    ┌─────────────────────────────────────────┐
  Prompt ──────────▶│  ① TRANSDUCTION [code-enforced]         │
  (Stimulus)        │  ├── Semantic Memory    (Vectors)       │
                    │  ├── Lexical / FTS      (BM25)          │
                    │  ├── Structured Memory  (CANONICAL, KB) │
                    │  ├── Entity / Tags      (Index files)   │
                    │  └── Filesystem         (Filenames)     │
                    │  5 channels (+ opt web) fire via RRF    │
                    └──────────────┬──────────────────────────┘
                                   │ raw activations
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │  ② ATTENTION GATE [code-enforced]       │
                    │  ├── Top-down: Prior context narrows    │
                    │  ├── Bottom-up: Novel/high-signal wins  │
                    │  ├── Weighted RRF Fusion (k=60)         │
                    │  └── Cross-Encoder Reranker (Top-K)     │
                    └──────────────┬──────────────────────────┘
                                   │↑ bidirectional feedback
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │  ③ EXECUTIVE FUNCTION (Decision Layer)  │
                    │  ├── Ruin Gate [code-enforced] (Law #1) │
                    │  ├── Crisis Gate [code-enforced] (P509) │
                    │  ├── Circuit Breaker [agent-discretion] │
                    │  └── Calibration [aspirational/agent]   │
                    │      (Λ suppresses SNIPER web in code;  │
                    │       depth scaling is agent discretion)│
                    └──────────────┬──────────────────────────┘
                                   │
                                   ▼
                               Response (Action)
```

### How Each Stage Maps to Athena

| Stage | Human Analog | Athena Implementation | Epistemic Status |
|:------|:-------------|:----------------------|:-----------------|
| **① Transduction** | Sensory receptors fire simultaneously | Agent-pull via `context_gate` / `search.py` across 5 local channels (Canonical, Vectors, FTS BM25, Tags, Filenames) + conditional Web Search, verified at turn end by `stop_governance_gate.py` | `code-enforced` |
| **② Attention Gate** | Thalamus filters — only relevant signals pass | Weighted RRF fusion (k=60) + FlashRank cross-encoder reranker | `code-enforced` |
| **③ Executive Function** | Prefrontal cortex — plan, inhibit, decide | Law #1 gates ruin (`block_ruin.py`); P509 crisis referral (`hook_crisis_gate.py`, `hook_stop_verify.py`); Circuit breaker (`circuit-breaker`); Λ scores risk (suppresses SNIPER web in code; depth is agent discretion) | Mixed (`code-enforced` gates + `agent-discretion`) |
| **Response** | Motor cortex — act | Agent generates output, Stop verification gate checks formatting/hotlines/secrets | `code-enforced` Stop gate |

### What's NOT Linear

The old model (`Intent → System → Cluster → Skill → Protocol`) assumed a waterfall: classify first, then route. This fails because:

1. **Classification errors cascade** — misclassify intent and the entire chain fires wrong
2. **No feedback** — once classified, there's no mechanism to re-evaluate
3. **Memory is gated by labels** — trading knowledge is invisible during a "psychology" query, even when it's relevant (e.g., Sizing Ghost = emotional variance = psychology AND trading)

The perception model fixes all three: everything activates in parallel, relevance emerges from the data, and feedback loops allow course-correction mid-processing.

### Cognitive Domains (Memory Activation Targets)

These are **not routing stages** — they're the memory domains that activate during transduction. The prompt doesn't get classified into one; relevant memories from ALL domains surface simultaneously.

| Priority | Domain | Archetype | Key Skills |
|:---------|:-------|:----------|:-----------|
| 1 | 🛡️ Survival | Crisis / ruin prevention | `circuit-breaker`, `trading-risk-gate` |
| 2 | 🫀 Life Decision | Irreversible personal choice | `therapeutic-ifs`, `decision-journal`, `red-team-review` |
| 3 | 📈 Trading | Capital deployment | `trading-risk-gate`, `zenith-execution`, `trade-journal-analyzer` |
| 4 | 🤝 Social | Interpersonal dynamics | `power-inversion`, `consiglieri-protocol` |
| 5 | ⚙️ Execution | Build / ship / create | `spec-driven-dev`, `micro-commit`, `visual-verify-ui` |
| 6 | 📣 Growth | Distribution / audience | `distribution-physics`, `brand-foundations`, `seo-auditor` |
| 7 | 📖 Learning | Understanding / knowledge | `deep-research-loop`, `semantic-search` |
| 8 | 🔄 Maintenance | System homeostasis | `context-compactor`, `daemon-loop` |

**Priority does NOT mean "route here first"** — it means "if multiple domains activate with equal signal strength, the higher-priority domain's memories take precedence in the attention gate." Survival always wins ties. This is the amygdala hijack analog.

### Cluster Map (Procedural Memory Index)

Clusters represent bundles of procedural knowledge that co-activate. When the attention gate passes a trading-related signal, clusters #3-5 activate as a unit, not sequentially.

| # | Cluster | Capstone Skill | Domain |
|:--|:--------|:---------------|:-------|
| 1 | Diagnostic Engine | P501 | Decision |
| 2 | Context Lifecycle | P502 | Architecture |
| 3 | Trading Risk Gate | `trading-risk-gate` | Trading |
| 4 | Trading Execution | `zenith-execution` | Trading |
| 5 | Trade Analytics | `trade-journal-analyzer` | Trading |
| 6 | Social Contract | `power-inversion` + `consiglieri-protocol` | Business/Social |
| 7 | Inner Work | `therapeutic-ifs` | Psychology |
| 8 | Adversarial QA | `red-team-review` | Quality |
| 9 | Strategic Reasoning | `decision-journal` + `synthetic-parallel-reasoning` | Decision |
| 10 | Distribution Engine | `distribution-physics` + `brand-foundations` + `seo-auditor` | Marketing |
| 11 | Swarm Orchestrator | `marketing-swarm` + `git-worktree-swarm` | Architecture |
| 12 | Research Pipeline | `deep-research-loop` + `semantic-search` | Research |
| 13 | Build Lifecycle | `spec-driven-dev` + `micro-commit` + `visual-verify-ui` | Engineering |
| 14 | Sovereign Safety | `circuit-breaker` + `context-compactor` | Safety |
| 15 | Problem-Solving Engine | P504 + P115 + P505 + P506 + `red-team-review` | Reasoning |

Full cluster details: `CLUSTER_INDEX.md` (private workspace — see table above for summary)

### Inventory

| Layer | Count |
|:------|------:|
| Cognitive Domains | 8 |
| Cognitive Clusters | 15 |
| Skills | 44 active (17 archived) |
| Protocols | 410 active (51 archived; 461 total) |
| Workflows | 78 (57 root + 21 _domain/) |

---

## Proactive Cognition Layer (Grace Harper Model)

> The Perception Model is **reactive** — it requires a stimulus. But the bionic unit also needs a **proactive** layer that fires without a prompt. This is the conscience: it reminds, enforces, and blocks based on time, behavioral patterns, and the absence of action.

```
                              ┌──────────────────────────────┐
                              │  ④ PROACTIVE LAYER (Daemon)  │
                              │  ├── Temporal triggers       │
  Time / Behavior ──────────▶ │  ├── Behavioral pattern scan │
  (No user prompt)            │  ├── Absence detection       │
                              │  └── Accountability nudge    │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │  Enforcement Actions         │
                              │  ├── Remind  (BEH-601 sat)   │
                              │  ├── Nudge   (BEH-603 rev)   │
                              │  └── Block   (Circuit Break) │
                              └──────────────────────────────┘
```

### Trigger Types

| Trigger | Example | Fires When |
|:--------|:--------|:-----------|
| **Temporal** | BEH-601 Saturday gym | `/start` detects Saturday AM |
| **Behavioral pattern** | BEH-602 schema trigger log | `/end` detects 3+ schema-driven decisions in session |
| **Absence of action** | Solo gym streak = 0 | Weekly accountability audit finds no logged execution |
| **Ruin proximity** | Circuit breaker | Cumulative red flags exceed threshold |

### Relationship to Perception Model

The two layers are **complementary, not nested**:

- **Reactive** (Perception Model): User asks → parallel activation → attention gate → executive function → response
- **Proactive** (Grace Harper): Time/behavior fires → BEH protocol activation → nudge/enforce/block

The proactive layer can **inject context** into the reactive layer — e.g., when `/start` surfaces an active BEH accountability trigger, that context enters the Attention Gate's top-down priming for the rest of the session.

### Implementation (Hybrid: Hook-Enforced Boot + Operational Workflows)

| Touchpoint | How It Works |
|:-----------|:-------------|
| `SessionStart` hook (`.agents/hooks.json` + `.agent/scripts/hook_auto_start.py`) | Code-enforced boot injection (`/start` directive on Antigravity `injectSteps` & Claude Code `hookSpecificOutput`) |
| `scripts/boot_status.py` | Runtime boot telemetry — session sync, BEH-601 hiatus alerts, and Maintenance vs Output split |
| `/start` | Behavioral Accountability Surface — surfaces active BEH protocols, day-aware prompts |
| `/end` | Behavioral Accountability Close — BEH-602 trigger log gate, weekly execution audit |
| `/ultrastart` | Deep BEH context load, schema trigger pre-load |
| `daemon-loop` skill | Autonomous recurring background checks (`/schedule` & `launchd` plists) |
| `circuit-breaker` skill | Ruin-proximity inhibition |

---

## Boot Sequence

```text
/start (MinMax v2.0 default)     → ~8–12K tokens, <2s (batched boot_status.py <1.0s)
/ultrastart (MaxMax v4.0 curated) → <=40K tokens (<20% of 200K ECL ceiling)
```

1. **Identity & Context Priming**: Core Identity (Laws #0–#4) + surgical `activeContext.md` checkpoint **prime top-down attention**. Under `/ultrastart`, curated slices (`CANONICAL.md` L1-185, `PROJECTS.md` switchboard) + Frame/Decision gates pre-load within a strict `<=40K` token ceiling, paired with explicit `/ultraend` session close.
2. **Parallel Status Aggregation**: Single-shot `scripts/boot_status.py` (or `.agent/scripts/athena-py scripts/boot_status.py`) replaces sequential subprocesses with concurrent status, frame, due-decision, and index-health collection (`<1.0s`).
3. **JIT Procedural Activation**: Protocol 530 (conditional skill loading) injects matching skills/protocols only on demand rather than loading the entire registry at boot.

### Loading Strategy (Progressive Disclosure)

| Layer | Trigger | Tokens / Size |
|:------|:--------|--------------:|
| Core Identity | `/start` | ~2K |
| Memory Bank (surgical slices) | `/start` | ~3.5K |
| `boot_status.py` + Sentinel | `/start` | ~2K |
| CANONICAL Tier 1 (always boot) | `/start` | ~13K (66 entries, ~50KB) |
| CANONICAL Tier 2 (domain-triggered) | Query match | ~13K (110 entries, ~50KB on demand) |
| CANONICAL Tier 3 (on-demand) | Explicit search hit | ~0.2K (1 entry, <1KB) |
| Protocol / Skill cluster (on-demand) | `context_trigger` / Attention gate | ~3–15K per bundle |
| MaxMax v4.0 curated boot | `/ultrastart` | <=40K (`<20%` of 200K ECL) |

---

## Retrieval Stack

```text
src/athena/tools/search.py (vector_mode: "local" | "auto" | "always" + grep fallback)
├── Tiered Vector Escalation (MinMax v2.0)
│   ├── "local"  — SNIPER (<10) / explicit local lookup: FTS5 + canonical + filenames (<1s, zero remote embedding block)
│   ├── "auto"   — STANDARD (10-30): speculative local + ONNX cross-encoder overlap with quality-floor vector escalation (<=5s wall cap)
│   └── "always" — ULTRA (>30) / deep queries: full Supabase pgvector RPC fan-out + parallel reranking
├── Hybrid Activation Channels
│   ├── Canonical search (CANONICAL.md keyword matching, min 2-hit)
│   ├── Vector search (Supabase pgvector, parallel RPCs, threshold >=0.3)
│   ├── Filename search (workspace path matching, keyword OR logic)
│   ├── Framework docs search (keyword matching in .framework/ + memory_bank/)
│   ├── SQLite FTS5 / DB search (local .athena/athena.db or .agent/inputs/athena.db via athena.core.db.connect_sqlite)
│   └── Web search [opt-in, auto via needs_web()] (provider layer: Serper/Brave/DDG)
├── Caching & Unified SQLite (athena.core.db.connect_sqlite: WAL + busy_timeout)
│   ├── QueryCache (src/athena/core/cache.py) — zero-write on cache hit, decoupled search_cache_vecs.db SQLite sidecar
│   └── PersistentEmbeddingCache (src/athena/memory/vectors.py) — serialized thread-safe embedding SQLite cache
├── Fusion & Attention Gate
│   ├── Weighted RRF (k=60, weights in search.py::WEIGHTS) + ONNX Cross-Encoder reranker (top-50 -> limit)
│   └── mcp_server.py::context_gate — parallel Meta-Pattern fan-out + deduplicated personalisation context
├── Telemetry: retrieval_log.jsonl (quality: hit/partial/miss, source distribution)
└── Grep fallback (runs automatically on timeout or degraded network)
    ├── CANONICAL.md & PROTOCOL_SUMMARIES.md
    ├── Session log filenames & content (bounded tail by mtime)
    └── Memory bank files
```

---

## Risk-Proportional Response (Law #6)

| Level | Lambda Score | Protocol | Latency |
|:------|-------------:|:---------|--------:|
| SNIPER | < 10 | Direct answer. Search exempt (`vector_mode="local"` when used). | ~1s |
| STANDARD | 10-30 | Triple-Lock (`context_gate` / `vector_mode="auto"` -> Speak, `stop_governance_gate.py` verified; `quicksave` at milestones / `/end`) | ~2-5s |
| ULTRA | > 30 | Triple-Lock + MaxMax v4.0 (`vector_mode="always"`, `<=40K` curated boot, Frame/Decision gates) | Deep / Curated |

---

## Active Indexes (5 generated files)

| Index | Path | Purpose |
|:------|:-----|:--------|
| `CLUSTER_INDEX.md` | `.agent/CLUSTER_INDEX.md` | Routing map (15 clusters + 8 systems) |
| `WORKFLOW_INDEX.md` | `.agent/WORKFLOW_INDEX.md` | Workflow registry (root + `_domain/`) |
| `SKILL_INDEX.md` | `.agent/skills/SKILL_INDEX.md` | Active skills + protocol tree registry |
| `PROTOCOL_SUMMARIES.md` | `.context/PROTOCOL_SUMMARIES.md` | All-protocol quick-lookup |
| `KNOWLEDGE_GRAPH.md` | `.context/KNOWLEDGE_GRAPH.md` | Concept relationships |

> **Archived** (`TAG_INDEX_legacy`, `CODE_INDEX.json`, `protocols.json`): Moved to `.context/archive/` and `.agent/archive_skills/`. (`SKILL_INDEX.md` remains active at `.agent/skills/SKILL_INDEX.md`.)

---

## Protocol Taxonomy (26 active categories — see `CAPS.json`)

| Category | Count | Category | Count |
|:---------|------:|:---------|------:|
| architecture | 65 | decision | 51 |
| psychology | 42 | business | 31 |
| engineering | 25 | strategy | 25 |
| workflow | 23 | pattern-detection | 20 |
| communication | 19 | safety | 15 |
| content | 14 | meta | 11 |
| reasoning | 9 | marketing | 8 |
| research | 8 | singapore | 7 |
| trading | 7 | coding | 6 |
| case-studies | 4 | creation | 4 |
| diagnostics | 4 | verification | 4 |
| memory | 3 | behavioral | 2 |
| qa | 2 | design | 1 |
| *archive* | *51* | — | — |

---

## Intelligence & Memory Subsystems (v10.0.6)

### 1. Intelligence Engine (`src/athena/intelligence/`)
- **`gto_engine.py`**: Deterministic Multiple-Criteria Decision Analysis (MCDA) engine with automated ±10% weight perturbation, pairwise dominance auditing, and winner stability gates. Automatically detects unstable ties and routes to Path D (Reversible Experiment) or Path E (Wait/Status Quo). Computes Empirically-discounted Expected Value (EEV), Half-Kelly sizing, Law-of-Ruin probabilities, dual-vault barbell screens, and Monte Carlo decision/trade simulations (`log_decision_receipt`, `find_unreceipted_engine_claims`).
- **`wargame.py`** *(paired with `examples/scripts/wargame_runner.py` and `/wargame`)*: Two-turn sequential adversarial wargaming and Red Cell adjudication engine (`adjudicate_wargame`, `resolve_two_turn_cell`). Enforces Turn-1 absorbing barrier truncation (`t1_worst`), fail-closed Law #1 survival vetting (`UnscreenedWargame`), Game-Mode maximin and minimax-regret ranking, counterparty best-response (`red_best_responses`, `blue_at_red_br`, `red_br_winner`), sovereign rule-change shock columns (`counterparty_writes_rules=True`), deciding-margin fragility detection (`FRAGILITY_THRESHOLD = 0.10`), field provenance verification (`VALID_PROVENANCE_BASES`), and context-isolated Red Cell independence verification (`ObservableActionPacket`, `.athena/wargame_runs.jsonl`, `[THEATER]` stamping).
- **`ucds_validator.py`** *(paired with `examples/scripts/ucds_audit.py`, `/osint`, and Protocol 580)*: Deterministic validator for the Universal Counterparty Dossier Standard (`UCDSDossierValidator`, `audit_ucds_dossier`). Enforces Track A/B bifurcation (`Track A-R`, `Track A-P`, `Track A-N`, `Track B`), non-compensatory binary knockout gates (`PASS | FAIL | HARD VETO`), 6-section completeness, directional cashflow inversion guards (front-loaded cash for client receivables vs. back-loaded milestones for vendor payables), the 5-state provenance ladder (`VERIFIED`, `ATTESTED`, `ABSENT:LAWFUL`, `ABSENT:SUSPICIOUS`, `CONTRADICTED`), the Singapore Exempt Private Company (`ABSENT:LAWFUL`) rule, functional archetype quarantine on Track B, and plain-ASCII math validation.
- **`frame_ledger.py`**: Pre-registered problem framing, hypothesis tracking (`Hypothesis`, `FrameRecord`), Value of Information (VOI / `compute_evi`) stopping gates, tier complexity caps (`TIER_CAPS`), and Brier calibration scoring (`FrameLedger`, `validate_frame`, `score_frames`).
- **`evidence_contract.py`**: Structured frontmatter claim extraction (`EvidenceClaim`, `ClaimKind`, `ClaimStatus`) and interpersonal calibration guardrails (`filter_claims_for_profiling`, `validate_interpersonal_calibration`).
- **`spec_gate.py`**: Upstream four-pillar specification verifier (`UpstreamSpecGate`: Physical Envelope, Disciplinary Lexicon & Scope Boundaries, Frozen Empirical Telemetry, Submission Binary Contract).
- **`prop_risk_guard.py`**: Proprietary trading drawdown capacity and ergodicity/carry auditing (`audit_prop_risk_capacity`, `audit_ergodicity_and_carry`, `PropCapacityAudit`, `ErgodicityCarryAudit`).
- **`gate_telemetry.py`**: Governance gate telemetry aggregation and outbound substance-decode contract auditing (`GateTelemetryAnalyzer`, `evaluate_substance_decode_adherence`).
- **`sentinel.py`**: Boot/shutdown sentinel verification and active-context session checkpointing (`check_boot_sentinel`, `check_shutdown_sentinel`, `update_active_context`).

### 2. Contextual ATX Heading Breadcrumb Chunker (`src/athena/memory/`)
- **`contextual_chunker.py`**: Pure standard-library hierarchical parser that extracts Markdown ATX heading hierarchy (`# Title > ## Section > ### Subheading`) and prepends structured breadcrumbs to every text chunk prior to vector embedding. Eliminates orphan context loss across RAG queries (shipped S1053).

### 3. Runtime Infrastructure, Verification & Guard Tooling (`src/athena/`, `scripts/` & `examples/scripts/`)
- **`src/athena/core/db.py`**: Unified SQLite connection factory (`connect_sqlite` with `WAL` journal mode, `busy_timeout`, and validated `synchronous` PRAGMA) and database path resolver (`resolve_athena_db_path`), backing `QueryCache` (`cache.py`) and `PersistentEmbeddingCache` (`vectors.py`).
- **`src/athena/core/jsonl_tail.py`**: Shared O(1) bounded EOF-seek JSONL tail reader and gzip log rotator (`read_jsonl_tail_lines`, `read_tail_jsonl_records`, `read_latest_jsonl_record`, `rotate_jsonl_if_oversized`), re-exported via `.agent/scripts/lib/jsonl_tail.py` and `examples/scripts/lib/jsonl_tail.py`.
- **`scripts/boot_status.py`**: Single-pass parallel boot status aggregator replacing legacy sequential shell calls (`<1.0s` target wall time).
- **`src/athena/tools/trade_guardian.py`**: Deterministic FX trade holding-duration guardrail (`TradeGuardian` with sweet-spot, optimal, and danger holding thresholds).
- **Governance & Stop Audit Gates**: `scripts/hook_stop_verify.py` & `examples/scripts/stop_governance_gate.py` (O(1) tail-scan Stop hooks) paired with non-blocking `audit_warnings` in `src/athena/mcp_server.py::quicksave` (`_has_raw_latex_delimiters` + bounded-tail `read_tail_jsonl_records` + `find_unreceipted_engine_claims`).
- **`src/athena/tools/citation_verifier.py`**: Automated Crossref API client with title similarity scoring and DOI metadata verification (shipped S1032).
- **`scripts/contrast_check.py`**: Deterministic W3C WCAG 2.1 relative luminance checker with built-in reference self-tests (shipped S1055).

---

## CANONICAL Progressive Disclosure (v10.0.6)

Section 4 (Strategic Frameworks) contains 177 entries, ~101KB (full `CANONICAL.md`: ~409KB). Progressive disclosure tiers:

| Tier | Count | Size | Loading Strategy |
|:-----|------:|-----:|:-----------------|
| Tier 1 (Always Boot) | 66 | ~50KB | Loaded on every `/start` — universal laws, identity truths |
| Tier 2 (Domain-Triggered) | 110 | ~50KB | Loaded when query matches domain keywords (trading, pricing, etc.) |
| Tier 3 (On-Demand) | 1 | <1KB | Loaded only via explicit search hit |

**Boot savings**: 51% of CANONICAL Section 4 deferred (~51KB saved per session).

Tier map: `.agent/telemetry/tier_map.json` (generated by `canonical_tier_analysis.py`).

---

## MCP Servers (FastMCP v3.x, stdio transport — 19 Athena + 5 DuckDB Tools)

```
src/athena/mcp_server.py (19 tools)
├── smart_search               — Hybrid RAG search (read, memory)
├── agentic_search             — Multi-step query decomposition (read, admin)
├── quicksave                  — Session checkpoint with Triple-Lock governance
├── health_check               — System health check (read)
├── recall_session             — Session log retrieval (read, memory)
├── governance_status          — Triple-Lock compliance state
├── list_memory_paths          — Active memory directory inventory
├── set_secret_mode            — Toggle demo/external redaction mode
├── meta_awareness_check       — Run meta-awareness diagnostic
├── permission_status          — Current permission + tool manifest
├── report_external_web_search — Audit external web search invocation
├── search_web                 — Live web search provider relay
├── classify_turn              — Classify turn complexity (SNIPER/STANDARD/ULTRA)
├── frame_open                 — Open pre-registered problem frame & hypothesis
├── frame_validate             — Validate VOI, ruin floor, and R1-R13 gates
├── frame_resolve              — Record frame outcome & Brier score
├── frame_status               — Inspect open/closed frames
├── decision_screen            — Deterministic EEV / 1/3 Kelly / Ruin / MCDA screen
├── context_gate               — Context gating and missing retrieval resolution
└── Resources:
    ├── athena://session/current  — Full current session log
    └── athena://memory/canonical — CANONICAL.md content

src/athena/duckdb_mcp_server.py (5 tools)
├── query                      — Read-only analytical SQL over local files/tables
├── profile                    — Column summary & cardinality profiling
├── create_table_from_file     — Load CSV/JSON/Parquet into session DuckDB table
├── list_tables                — Inspect registered DuckDB tables
└── export_result              — Export query output to disk
```

**Config**: `~/.gemini/antigravity/mcp_config.json` (registered as stdio server).

---

## Telemetry & Instrumentation (v10.0.6)

| Component | Path | Purpose |
|:----------|:-----|:--------|
| Retrieval Log | `.agent/telemetry/retrieval_log.jsonl` | Every search: query, quality (hit/partial/miss), source contribution |
| Retrieval Audit | `.agent/scripts/retrieval_audit.py` | 4-section report: quality distribution, source contribution, consistent misses, daily trend |
| CANONICAL Tier Map | `.agent/telemetry/tier_map.json` | Machine-readable tier classification for progressive disclosure |
| CANONICAL Analyzer | `.agent/scripts/canonical_tier_analysis.py` | Non-destructive Section 4 tiering classifier |

**Key Metric**: Effective Recall Ratio = (hits + partials × 0.5) / total queries.

---

## Metrics

Live inventory counts are **not duplicated here** — a hand-maintained table only drifts. The single source of truth is **[`.agent/config/CAPS.json`](.agent/config/CAPS.json)**, kept current by the Gate-4 pre-commit hook (`core.hooksPath=.agent/hooks`), which also auto-syncs the Workspace Structure tree at the top of this file. Read counts from there.