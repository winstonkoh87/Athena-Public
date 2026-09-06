# Athena — Architecture Reference

> **Last Updated**: 7 September 2026
> **Version**: v9.9.9
> **Canonical Counts**: See `.agent/config/CAPS.json` — if numbers in this file diverge, CAPS wins.
> **Bionic Unit Spec**: `BIONIC_UNIT_SPEC.md` — the definitive human-AI augmentation mapping (private workspace)

---

## Workspace Structure

```
Athena/
├── .agent/                        # Agent configuration
│   ├── skills/                    #   43 active skills (42 with context_trigger)
│   │   └── protocols/             #   419 active + 34 archived = 453 total, 26 categories
│   │       └── archive/           #     34 deprecated protocols (read-only, see README)
│   ├── workflows/                 #   55 root + 19 _domain = 74 slash-command workflows
│   │   └── _domain/               #     Domain-scoped, conditionally activated
│   ├── scripts/                   #   273 automation scripts
│   ├── telemetry/                 #   Retrieval instrumentation logs + tier maps
│   ├── config/                    #   Agent manifests + CAPS.json (canonical counts)
│   ├── CLUSTER_INDEX.md           #   15 cognitive clusters (routing map)
│   ├── WORKFLOW_INDEX.md          #   Workflow registry
│   ├── graphrag/                  #   [REMOVED 2026-06-06] Knowledge graph formally retired
│   ├── swarms/                    #   Multi-agent swarm definitions
│   └── archive_skills/            #   17 sunset skills (read-only, see README)
│
├── .context/                      # Personal knowledge base
│   ├── memories/                  #   4,569 memory files (session logs + case studies + profile)
│   │   ├── session_logs/          #     Dated session records
│   │   ├── case_studies/          #     492 documented patterns (15 domains, 7 archived)
│   │   ├── profile/               #     Core profile, psychology, voice DNA
│   │   └── observations/          #     Session insights
│   ├── memory_bank/               #   10 boot files (activeContext, userContext,
│   │                              #     productContext, threatPlaybooks,
│   │                              #     sessionArchive, decisionLog, etc.)
│   ├── CANONICAL.md               #   Canonical memory (compacted truths)
│   ├── PROJECTS.md                #   Active project switchboard (supersedes legacy project_state.md)
│   ├── PROTOCOL_SUMMARIES.md      #   All-protocol index
│   ├── PROTOCOL_HEATMAP.md        #   Protocol usage heatmap
│   ├── KNOWLEDGE_GRAPH.md         #   Concept relationships
│   ├── TECH_DEBT.md               #   Technical debt tracker
│   ├── CASE_STUDY_INDEX.md        #   Case study domain taxonomy (14 domains)
│   └── archive/                   #   Retired indexes (TAG_INDEX_*, project_state_legacy)
│
├── .athena/                       # Runtime state (daemon, PID, crash reports)
├── .framework/                    # v8.2-stable modules + protocols (frozen 2026-02-01; reference-only)
│   └── archive/                   #   v7 / v8.0 / v8.1 codex archive (historical)
├── .projects/                     # Isolated project workspaces
│
├── src/                           # Athena SDK source (72 Python files)
├── tests/                         # Test suite (11 files, 86 tests)
├── supabase/                      # Cloud vector store migrations
│
├── Athena-Public/                 # Public mirror (sibling repo)
├── docs/                          # Documentation (76 files)
├── FX Trading/                    # Active trading workspace
├── media-factory/                 # Content generation pipeline
│
├── README.md                      # Private repo README
├── ARCHITECTURE.md                # This file
├── pyproject.toml                 # Python packaging
└── .env                           # API keys (gitignored)
```

---

## Cognitive Stack — Perception Model (v9.9.9)

> Modeled after human sensory processing: **Parallel Activation → Attention Gate → Executive Function → Response**.
> The brain doesn't classify-then-route; it activates-then-filters. Athena's runtime works the same way.

```
                    ┌─────────────────────────────────────────┐
  Prompt ──────────▶│  ① TRANSDUCTION (Parallel Activation)   │
  (Stimulus)        │  ├── Semantic Memory    (CANONICAL, KB) │
                    │  ├── Episodic Memory    (Session Logs)  │
                    │  ├── Procedural Memory  (Skills/Protos) │
                    │  └── Contextual Memory  (activeContext) │
                    │  7 channels fire simultaneously via RRF  │
                    └──────────────┬──────────────────────────┘
                                   │ raw activations
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │  ② ATTENTION GATE (Relevance Filter)    │
                    │  ├── Top-down: Prior context narrows    │
                    │  ├── Bottom-up: Novel/high-signal wins  │
                    │  ├── Threshold: Only > threshold passes │
                    │  └── Progressive Disclosure (Tier 1→2→3)│
                    └──────────────┬──────────────────────────┘
                                   │↑ bidirectional feedback
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │  ③ EXECUTIVE FUNCTION (Decision Layer)  │
                    │  ├── Risk Gate    (Law #1 — No Ruin)    │
                    │  ├── Inhibition   (Circuit Breaker)     │
                    │  ├── Planning     (Working Memory)      │
                    │  └── Calibration  (Λ Score → depth)     │
                    └──────────────┬──────────────────────────┘
                                   │
                                   ▼
                              Response (Action)
```

### How Each Stage Maps to Athena

| Stage | Human Analog | Athena Implementation |
|:------|:-------------|:----------------------|
| **① Transduction** | Sensory receptors (eyes, ears, skin) fire simultaneously | `search.py` fires 7 parallel channels: Canonical, Vectors, SQLite, Tags, Filenames, Framework, Exocortex |
| **② Attention Gate** | Thalamus filters — only relevant signals reach cortex | Weighted RRF fusion (k=60) + confidence threshold + progressive disclosure tiers |
| **③ Executive Function** | Prefrontal cortex — plan, inhibit, decide | Λ score calibrates depth; Law #1 gates ruin; Circuit Breaker inhibits; Red Team reviews |
| **Response** | Motor cortex — act | Agent generates output, files checkpoints, updates context |

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

| Layer | Count | Description |
|:------|------:|:------------|
| Cognitive Domains | 8 | Memory activation targets (priority-ordered for tie-breaking) |
| Cognitive Clusters | 15 | Co-activating procedural memory bundles |
| Skills | 43 active (17 archived) |
| Protocols | 419 active (34 archived; 453 total) |
| Workflows | 74 (55 root + 19 _domain/) |

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

The proactive layer can **inject context** into the reactive layer — e.g., when `/start` surfaces "BEH-601: 0 solo sessions in 20 weeks," that context enters the Attention Gate's top-down priming for the rest of the session.

### Implementation (Operational, Not Coded)

| Touchpoint | How It Works |
|:-----------|:-------------|
| `/start` | Behavioral Accountability Surface — surfaces active BEH protocols, day-aware prompts |
| `/end` | Behavioral Accountability Close — BEH-602 trigger log gate, weekly execution audit |
| `/ultrastart` | Deep BEH context load, schema trigger pre-load |
| `daemon-loop` skill | Autonomous recurring background checks |
| `circuit-breaker` skill | Ruin-proximity inhibition |

---

## Boot Sequence

```
/start → ~10K tokens, <5s
```

1. Load core identity (Laws #0–#4) — **primes top-down context** for attention gate
2. Load memory bank (userContext, productContext, activeContext) — **seeds episodic memory**
3. Run `boot.py` (session recall, semantic prime, daemon health check, COS init)
4. JIT activation replaces static routing — Protocol 530 (conditional skill loading) activates relevant procedural memory on demand

### Loading Strategy (Progressive Disclosure)

| Layer | Trigger | Tokens |
|:------|:--------|-------:|
| Core Identity | `/start` | ~2K |
| Memory Bank (3 files) | `/start` | ~3.5K |
| Boot orchestrator | `/start` | ~2K |
| CANONICAL Tier 1 (always boot) | `/start` | ~16K (29 entries) |
| CANONICAL Tier 2 (domain-triggered) | Query match | ~41K (140 entries, loaded on demand) |
| Protocol (on-demand) | Attention gate pass | ~3-7K each |
| Skill cluster (on-demand) | `context_trigger` match | ~5-15K per cluster |
| Full context | `/fullload` | ~28K |

---

## Retrieval Stack

```
src/athena/tools/search.py (12s God Mode timeout + grep fallback)
├── Full SDK search (parallel hybrid RRF + semantic cache)
│   ├── Canonical search (CANONICAL.md keyword matching, min 2-hit)
│   ├── Tag search (grep against TAG_INDEX shards)
│   ├── Vector search (Supabase pgvector, 11 parallel RPCs, threshold ≥0.3)
│   ├── ~~GraphRAG search~~ (REMOVED 2026-06-06 — stale 16 months, user directive)
│   ├── Filename search (find across project root, keyword OR logic)
│   ├── Framework docs search (keyword matching in .framework/ + memory_bank/)
│   ├── SQLite search (local athena.db — files + tags)
│   └── Exocortex search (Wikipedia FTS5)
├── Fusion: Weighted RRF (k=60, per-type weights, dynamic score modifiers)
├── Telemetry: retrieval_log.jsonl (quality: hit/partial/miss, source distribution)
└── Grep fallback (runs if full search times out)
    ├── CANONICAL.md
    ├── PROTOCOL_SUMMARIES.md
    ├── Session log filenames
    └── Memory bank files
```

---

## Risk-Proportional Response (Law #6)

| Level | Λ Score | Protocol | Latency |
|:------|--------:|:---------|--------:|
| SNIPER | < 10 | Direct answer. Search exempt. | ~1s |
| STANDARD | 10-30 | Triple-Lock (Search → Save → Speak) | ~5-10s |
| ULTRA | > 30 | Triple-Lock + Triple Crown reasoning | Unbounded |

---

## Active Indexes (4 lean files, 63KB total)

| Index | Size | Purpose |
|:------|-----:|:--------|
| `CLUSTER_INDEX.md` | 18KB | Routing map (15 clusters → 26 skills) |
| `WORKFLOW_INDEX.md` | 6KB | Workflow registry (74 workflows) |
| `PROTOCOL_SUMMARIES.md` | 24KB | All-protocol quick-lookup |
| `KNOWLEDGE_GRAPH.md` | 15KB | Concept relationships |

> **Archived** (2026-03-26): TAG_INDEX (1.55MB), CODE_INDEX.json (374KB), SKILL_INDEX.md (97KB), protocols.json (169KB). Moved to `.context/archive/` and `.agent/archive_skills/` respectively. See GTO Audit for rationale.

---

## Protocol Taxonomy (26 active categories)

| Category | Count | Category | Count |
|:---------|------:|:---------|------:|
| architecture | 67 | psychology | 41 |
| decision | 54 | business | 31 |
| engineering | 28 | strategy | 25 |
| workflow | 25 | communication | 19 |
| pattern-detection | 16 | safety | 15 |
| content | 13 | meta | 13 |
| reasoning | 10 | marketing | 8 |
| research | 7 | trading | 7 |
| coding | 6 | singapore | 6 |
| diagnostics | 5 | case-studies | 4 |
| creation | 4 | memory | 3 |
| qa | 2 | behavioral | 2 |
| design | 1 | archive | 34 |

---

## CANONICAL Progressive Disclosure (v9.9.9)

Section 4 (Strategic Frameworks) contains 199 entries, ~57KB. Progressive disclosure tiers:

| Tier | Count | Size | Loading Strategy |
|:-----|------:|-----:|:-----------------|
| Tier 1 (Always Boot) | 40 | ~16KB | Loaded on every `/start` — universal laws, identity truths |
| Tier 2 (Domain-Triggered) | 156 | ~40KB | Loaded when query matches domain keywords (trading, pricing, etc.) |
| Tier 3 (On-Demand) | 3 | ~1KB | Loaded only via explicit search hit |

**Boot savings**: 69% of Section 4 deferred = ~40KB saved per session.

Tier map: `.agent/telemetry/tier_map.json` (generated by `canonical_tier_analysis.py`).

---

## MCP Server

```
src/athena/mcp_server.py (FastMCP v3.x, stdio transport)
├── smart_search      — Hybrid RAG search (read, memory)
├── agentic_search    — Multi-step query decomposition (read, admin)
├── quicksave         — Session checkpoint with Triple-Lock governance
├── health_check      — Vector API + Database subsystem audit
├── recall_session    — Retrieve recent session log content
├── governance_status — Triple-Lock compliance state
├── list_memory_paths — Active memory directory inventory
├── set_secret_mode   — Toggle demo/external redaction mode
├── permission_status — Current permission + tool manifest
└── Resources:
    ├── athena://session/current  — Full current session log
    └── athena://memory/canonical — CANONICAL.md content
```

**Config**: `~/.gemini/antigravity/mcp_config.json` (registered as stdio server).

---

## Telemetry & Instrumentation (v9.8.0)

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