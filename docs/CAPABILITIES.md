# Athena Capabilities Catalog

> **Purpose**: Comprehensive inventory of Athena's automation layer  
> **Note**: This catalog describes capabilities. Implementation code is private.

---

## System Metrics

| Metric | Count |
|--------|-------|
| **Automation Scripts** | 290 |
| **Decision Protocols** | 461 (410 active + 51 archived, 26 categories) |
| **Orchestration Workflows** | 78 (57 root + 21 domain) |
| **Skills** | 44 active (43 with context_trigger), 17 archived |
| **Case Studies** | 629 |
| **Total Sessions** | 2,100+ |
| **Memory Files** | 5,991 |

---

## 🔧 Automation Scripts (290)

### Session Management

| Script | Description |
|--------|-------------|
| `boot.py` | Session orchestrator — integrity checks, context loading, protocol injection |
| `shutdown.py` | Session close — harvest check, git commit, compliance report |
| `quicksave.py` | Automatic session logging with hot-sync to vector DB |
| `resume_session.py` | Context recovery for interrupted sessions |

### Semantic Memory

| Script | Description |
|--------|-------------|
| `supabase_sync.py` | Full memory sync to pgvector with chunking and deduplication |
| `supabase_search.py` | Hybrid RAG search (semantic + keyword + reranking) |
| `smart_search.py` | Weighted RRF orchestration with cross-encoder rerank |
| `upload_to_supabase.py` | Supabase **Storage** bucket CLI — upload/download/list files, create buckets (not embeddings; those go through `supabase_sync.py`) |

### Knowledge Graph (DEPRECATED — Removed S435, 6 June 2026)

> GraphRAG was removed due to cost/complexity exceeding retrieval quality gains. Scripts retained in archive for reference.

| Script | Description | Status |
|--------|-------------|--------|
| `build_graph.py` | Entity-relationship extraction and graph construction | Archived |
| `query_graphrag.py` | Community-aware graph search (Microsoft GraphRAG pattern) | Archived |
| `index_graphrag.py` | Graph indexing for retrieval | Archived |
| `generate_graph_vis.py` | Interactive HTML graph visualization | Archived |

### Code Quality & Audit

| Script | Description |
|--------|-------------|
| `batch_audit.py` | Multi-file validation and consistency checks |
| `orphan_detector.py` | Find unlinked protocols and dead references |
| `protocol_compliance.py` | Track protocol violations per session |
| `harvest_check.py` | Ensure insights are captured before session close |
| `pre_commit_check.py` | Pre-commit gate for quality enforcement |

### Context Engineering

| Script | Description |
|--------|-------------|
| `compress_context.py` | Token optimization for long contexts |
| `compress_memory.py` | Archive old sessions with semantic summaries |
| `compress_sessions.py` | Batch session archival with 80/20 retention |
| `token_budget.py` | Token allocation optimization |

### Content Generation

| Script | Description |
|--------|-------------|
| `generate_case_study.py` | Template-based case study scaffolding |
| `generate_protocol.py` | Protocol creation with ID assignment |
| `generate_skill_index.py` | Protocol & skill registry generation (`SKILL_INDEX.md`) |

### Integration & Agents

| Script | Description |
|--------|-------------|
| `telegram_bot.py` | Telegram interface for Athena queries |
| `browser_agent.py` | Headless browser automation |
| `calendar_agent.py` | Google Calendar integration |
| `gemini_client.py` | Gemini API client with retry logic |
| `research_agent.py` | Multi-source research orchestration |

### Utilities

| Script | Description |
|--------|-------------|
| `diagnose.py` | System health diagnostics |
| `refactor.py` | Master orchestrator for deep maintenance |
| `sync_to_public.py` | Sanitized export to public repo |
| `git_commit.py` | Automated commit with semantic messages |

---

## 📜 Decision Protocols (461 total: 410 active + 51 archived, 26 categories)

### Architecture (65)

- **Protocol 133**: Query Archetype Routing — JIT knowledge loading based on query type
- **Protocol 168**: Context-Driven Development — Living spec pattern
- **Protocol 200**: Feature Context Persistence — Multi-session tracking
- **Protocol 215**: Canonical Memory — Materialized view for truth lookup
- **Protocol 242**: Latent Cluster Activation — Compressed context injection
- **Protocol 330**: Scale-Adaptive Intelligence — 5-level project scaling

### Decision Frameworks (51)

- **Protocol 38**: Synthetic Deep Think — Pseudo-depth via structured prompting
- **Protocol 49**: Efficiency-Robustness Tradeoff — When to optimize vs. fortify
- **Protocol 75**: Synthetic Parallel Reasoning — 3-track analysis (Domain/Adversarial/Cross-Domain)
- **Protocol 135**: Information Asymmetry Immunity — Meta-knowledge exploitation
- **Protocol 144**: Trilateral Validation — User + AI + Red Team feedback loop
- **Protocol 261**: Skeptic Gate — Antecedents-first reasoning

### Psychology (42)

- **Protocol 107**: Integrated Therapeutic Mode — Safe processing vs. analysis
- **Protocol 158**: Relationship Tier Audit — Investment vs. return calibration
- **Protocol 159**: Augmentation Circuit Breaker — Schema interception
- **Protocol 262**: Mismatch Radar — Reciprocity gap detection

### Business (31)

- **Strategic Analysis Framework**: Four Fits Diagnostic — Market/Product/Channel/Model fit
- **Protocol 160**: Certainty Offer — Risk reversal for high-ticket sales
- **Protocol 230**: Unit Economics Physics — Breakeven-first pricing
- **Protocol 306**: Outcome Economy — Value-based AI pricing
- **Strategic Analysis Framework**: Income Hierarchy — Labour → Freelance → Agency → Product ladder

### Engineering (25)

- **Agentic Engineering Strategy**: Wizard of Oz Architecture — Manual backend, automated frontend
- **Agentic Engineering Strategy**: Vibe Engineering — Ship at 70%, iterate fast
- **Agentic Engineering Strategy**: Intent Drift Detector — Scope creep prevention
- **Development Execution Standard**: TDD Workflow — Test-driven development gates

### Communication (19)

- **Protocol 50**: Interpretation Header — Explicit assumption declaration
- **Protocol 116**: Multi-Layer Communication — Public/private channel optimization
- **Protocol 252**: Constructive Feedback Stack — Criticism without damage

### Safety (15)

- **Protocol 48**: Circuit Breaker (Systemic) — Automatic ruin prevention
- **Protocol 68**: Anti-Karason Protocol — Identity drift detection
- **Protocol 104**: Seymour Skeptic Layer — Adversarial self-audit
- **LAW1_RUIN.md**: Irreversible ruin calculator

### Content (14)

- **Content Publication Standard**: Blog Post Gold Standard — 3-sentence rule, hidden gems
- **Protocol 221**: High-Performance UX Design — Breathability physics
- **Protocol 260**: Content Resonance Spec — "That's Me" reaction targeting

### Strategy (25)

- **Protocol 121**: Amoral Realism — IS vs SHOULD analysis
- **Protocol 162**: PMOD Framework — Problem > Market > Operations > Distribution
- **Protocol 172**: Barnacle SEO — Attach to high-authority domains

---

## ⚙️ Orchestration Workflows (78: 57 root + 21 domain)

| Workflow | Description |
|----------|-------------|
| `/start` | Boot sequence — load identity, create session, prime memory |
| `/end` | Session close — finalize log, commit, compliance check |
| `/refactor` | Deep maintenance — audit, sync, compress, rebuild indexes |
| `/think` | Elevated reasoning — force L4 depth + structured output |
| `/ultrathink` | Maximum depth — full stack load + extended reasoning |
| `/vibe` | Fast shipping mode — 70% rule, iterate quickly |
| `/research` | Deep rabbit hole — multi-source exhaustive search |
| `/osint` | Counterparty due diligence, binary knockouts, and 6-section UCDS dossier |
| `/wargame` | Two-turn adversarial wargaming with context-isolated Red Cell generation |
| `/brief` | Pre-prompt clarification — scope before execution |
| `/audit` | Cross-model validation — Claude vs Gemini comparison |
| `/deploy` | Public repo sync — sanitize and push |
| `/semantic` | Semantic search — query vector DB before answering |
| `/brand-generator` | Agency Killer — $10K branding package in 20 mins |
| `/333-diagnostic` | Lead generation diagnostic — structured problem discovery |
| `/ugc-factory` | AI UGC volume strategy — batch content generation |
| `/voice-agent-deploy` | ElevenLabs + Twilio voice agent setup |

---

## 📚 SDK Structure

```
athena/
├── core/
│   ├── config.py          # Centralized paths, marker-based root discovery
│   ├── governance.py      # Triple-Lock and doom-loop circuit breaker
│   ├── permissions.py     # Capability RBAC and secret-mode gating
│   └── models.py          # Data models for sessions, protocols, entities
├── intelligence/
│   ├── evidence_contract.py # Structured claim extraction & interpersonal calibration
│   ├── frame_ledger.py      # Frame validation, VOI gate, Brier calibration ledger
│   ├── gate_telemetry.py    # Governance gate telemetry & substance-decode audit
│   ├── gto_engine.py        # EEV dominance, ruin ceiling, Paths A-E screen
│   ├── prop_risk_guard.py   # Prop drawdown capacity & ergodicity/carry audit
│   ├── sentinel.py          # Boot/shutdown sentinel & active-context checkpointing
│   ├── spec_gate.py         # Upstream 4-pillar specification verification gate
│   ├── ucds_validator.py    # Universal Counterparty Dossier Standard (UCDS) gate
│   └── wargame.py           # 2-turn sequential game trees & trough ruin check
├── memory/
│   ├── cache.py           # TTL-based LRU cache for search
│   └── vectors.py         # Embedding generation and retrieval
├── tools/
│   ├── latency.py         # Λ complexity indicator
│   ├── search.py          # Hybrid RAG orchestrator (RRF + FTS5 + pgvector)
│   ├── fts_search.py      # Local SQLite FTS5 BM25 lexical search
│   └── reranker.py        # Cross-encoder reranking
└── mcp_server.py          # 19-tool FastMCP server (+ duckdb_mcp_server.py: 5 tools)
```

---

## 📖 Case Study Categories (629 total)

| Category | Examples |
|----------|----------|
| **Business Models** | Content Agency Arbitrage, Four Fits Diagnostics, Productized Services |
| **Psychology** | Attachment Patterns, Schema Installation, Relationship Dynamics |
| **Singapore Context** | Healthcare Cartel, Education Arbitrage, Social Contract |
| **AI/Automation** | Agentic Coding, Claude Workflows, Retrieval Optimization |
| **Marketing** | SEO Distribution, Content Resonance, Influencer Economics |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.x |
| **Vector DB** | Supabase (pgvector) |
| **Embeddings** | Google gemini-embedding-001 |
| **LLM** | Gemini 3.1 Pro / Claude Opus 4.6 |
| **Hosting** | GitHub Pages / Cloudflare |

---

> **Note**: This catalog demonstrates the scope and sophistication of Athena's capabilities. Implementation details are proprietary.

# capabilities #automation #protocols
