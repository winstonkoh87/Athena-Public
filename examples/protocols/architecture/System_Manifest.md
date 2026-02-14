---

created: 2025-12-30
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-30
last_updated: 2026-01-16
---

# Athena System Manifest (v7.5)

> **Status**: ACTIVE
> **Enforcement**: Strict (via `audit_imports.py`)
> **Source of Truth**: This document defines the canonical architecture.

---

## 1. The 4-Layer Architecture

Athena operates on a "Bionic OS" model with four distinct layers of abstraction.

### Layer 1: Framework (`.framework/`)

* **Role**: The "Soul". Immutable identity, laws, and operating principles.
* **Responsibility**: Defines *who* the agent is and *how* it reasons.
* **Dependencies**: Zero. Cannot import from other layers.
* **Key Files**: `Core_Identity.md`, `Laws.md`.

### Layer 2: Context (`.context/`)

* **Role**: The "Brain". Persistent memory, user profile, and project state.
* **Responsibility**: storage of session logs, case studies, and knowledge.
* **Dependencies**: Passive. Read by Agent layer.

### Layer 3: Agent (`.agent/` and `src/athena/`)

* **Role**: The "Hands". Executable code, workflows, and tools.
* **Responsibility**: Action, orchestration, and interface.
* **Components**:
  * `src/athena/`: The Core SDK (Python Package).
  * `.agent/scripts/`: Legacy scripts and thin wrappers (Migrating to SDK).
  * `.agent/workflows/`: Declarative process definitions.

### Layer 4: Public (`Athena-Public/`)

* **Role**: The "Face". Sanitized, recruiter-safe mirror.
* **Responsibility**: Open-source demonstration.
* **Constraint**: One-way sync. Never import *from* Public.

---

## 2. Dependency Rules (The Law)

To prevent "Spaghetti Code", the following import rules are enforced:

| Module / Layer | Allowed to Import FROM | Forbidden to Import FROM |
| :--- | :--- | :--- |
| **athena.core** | Standard Lib, 3rd Party | `athena.tools`, `athena.memory` (Circular) |
| **athena.memory** | `athena.core` | `athena.tools` |
| **athena.tools** | `athena.core`, `athena.memory` | None |
| **.agent/scripts/** | `athena.*` | Other Scripts (No relative imports between scripts) |

> **Rule**: Scripts in `.agent/scripts/` are **Entry Points**. They should not be libraries. Logic belongs in `athena.*`.

---

## 3. Approved Entry Points

Only these files are intended to be executed directly.

### Operational

* `python3 .agent/scripts/boot.py`: Initializes session.
* `python3 .agent/scripts/quicksave.py`: Logs session state.
* `python3 .agent/scripts/refactor.py`: System maintenance.
* `python3 .agent/scripts/sync_to_public.py`: Public repo sync.

### DevOps / Maintenance

* `python3 .agent/scripts/generate_map.py`: Updates this manifest.
* `python3 .agent/scripts/audit_imports.py`: Verifies architecture compliance.

---

## 4. Script-to-Package Roadmap (v7.5)

We are migrating from a "Flat Script" model to a "Package" model.

| Phase | Action | Status |
| :--- | :--- | :--- |
| **0. Init** | Create `pyproject.toml` and `src/athena` | ✅ Done |
| **1. Shim** | Scripts import from `athena` but keep CLI interface | 🚧 In Progress |
| **2. Port** | Move logic from `scripts/*.py` to `src/athena/*` | 📅 Future |
| **3. Clean** | Delete legacy scripts, replacing with `athena -m ...` | 📅 Future |

---

## 5. Directory Map (Auto-Generated)

> **Last Updated**: (Pending Run)
> **Filter**: Excludes `.git`, `__pycache__`, `archive`, `node_modules`

[AUTO_GENERATED_MAP_START]
```text
├── .agent/
│   ├── TASK_LOG.md
│   ├── WORKFLOW_INDEX.md
│   ├── athena/
│   │   ├── __init__.py
│   │   ├── atomic_io.py
│   │   ├── cache.py
│   │   ├── config.py
│   │   └── logger.py
│   ├── athena_sdk.egg-info/
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   ├── dependency_links.txt
│   │   ├── requires.txt
│   │   └── top_level.txt
│   ├── config/
│   │   └── orphan_exclusions.yaml
│   ├── decisions/
│   │   └── Decision_Log.md
│   ├── eval/
│   │   ├── README.md
│   │   ├── gold_queries.json
│   │   └── run_eval.py
│   ├── frameworks/
│   │   └── pattern_recognition/
│   │       ├── __init__.py
│   │       ├── analyzers/
│   │       │   ├── __init__.py
│   │       │   ├── financial_analyzer.py
│   │       │   ├── media_analyzer.py
│   │       │   └── text_analyzer.py
│   │       ├── base.py
│   │       └── factory.py
│   ├── graphrag/
│   │   ├── communities.json
│   │   ├── entities.json
│   │   ├── knowledge_graph.gpickle
│   │   ├── knowledge_graph.html
│   │   ├── knowledge_graph_lite.html
│   │   ├── knowledge_graph_mini.html
│   │   ├── knowledge_graph_planetary.html
│   │   ├── knowledge_graph_sfw.html
│   │   ├── knowledge_graph_sized.html
│   │   └── knowledge_graph_solar.html
│   ├── hooks/
│   │   └── README.md
│   ├── mcp_server/
│   │   ├── antigravity_server.py
│   │   ├── requirements.txt
│   │   └── skills/
│   │       └── document_factory.py
│   ├── migrations/
│   │   └── 001_create_hnsw_indexes.sql
│   ├── patterns/
│   │   ├── 01-risk-management-isomorphism.md
│   │   ├── 02-agency-vs-product.md
│   │   ├── 03-trojan-horse-shadow-arbitrage.md
│   │   ├── 04-baseline-anchoring-medicine.md
│   │   └── 05-leadership-matrix.md
│   ├── personas/
│   │   └── PERSONA_REGISTRY.md
│   ├── prompts/
│   │   └── visual/
│   │       └── skillsfuture_linkedin_promo.txt
│   ├── protocols.json
│   ├── pyproject.toml
│   ├── scripts/
│   │   ├── analyze.py
│   │   ├── antigravity_server.py
│   │   ├── ask_codebase.py
│   │   ├── audit_graph_coverage.py
│   │   ├── audit_imports.py
│   │   ├── audit_session_costs.py
│   │   ├── auto_linker.py
│   │   ├── auto_tagger.py
│   │   ├── batch_audit.py
│   │   ├── boot.py
│   │   ├── browser_agent.py
│   │   ├── build_graph.py
│   │   ├── calendar_agent.py
│   │   ├── compress_context.py
│   │   ├── compress_memory.py
│   │   ├── compress_sessions.py
│   │   ├── create_session.py
│   │   ├── cross_reference.py
│   │   ├── diagnose.py
│   │   ├── embed_codex.py
│   │   ├── extract_entities.py
│   │   ├── extract_keyframes.py
│   │   ├── gemini_client.py
│   │   ├── generate_case_study.py
│   │   ├── generate_graph_vis.py
│   │   ├── generate_map.py
│   │   ├── generate_protocol.py
│   │   ├── generate_puml.py
│   │   ├── generate_sfw_graph.py
│   │   ├── generate_skill_index.py
│   │   ├── generate_tag_index.py
│   │   ├── git_commit.py
│   │   ├── graph_audit.py
│   │   ├── harvest_check.py
│   │   ├── index_graphrag.py
│   │   ├── ingest_profile.py
│   │   ├── link_builder.py
│   │   ├── memory_integrity.py
│   │   ├── metabolic_monitor.py
│   │   ├── metabolic_scan.py
│   │   ├── metadata_extractor.py
│   │   ├── migrate_sessions.py
│   │   ├── mu_graphrag_bridge.py
│   │   ├── orphan_detector.py
│   │   ├── pattern_recognition.py
│   │   ├── plot_business_curves.py
│   │   ├── plot_social_curves.py
│   │   ├── populate_forward_lineage.py
│   │   ├── pre_commit_check.py
│   │   ├── protocol_compliance.py
│   │   ├── protocol_entropy.py
│   │   ├── protocol_scaffold.py
│   │   ├── query_codex.py
│   │   ├── query_graphrag.py
│   │   ├── quicksave.py
│   │   ├── refactor.py
│   │   ├── repair_links.py
│   │   ├── reranker.py
│   │   ├── research_agent.py
│   │   ├── response_wrapper.py
│   │   ├── resume_session.py
│   │   ├── run_tests.py
│   │   ├── sanitize_for_export.py
│   │   ├── search_web.py
│   │   ├── semantic_audit.py
│   │   ├── session_telemetry.py
│   │   ├── setup_bankai.sh
│   │   ├── setup_calendar_auth.py
│   │   ├── setup_graphrag.py
│   │   ├── shutdown.py
│   │   ├── skill_gap_detector.py
│   │   ├── slurp_url.py
│   │   ├── smart_search.py
│   │   ├── stale_detector.py
│   │   ├── structure_map.py
│   │   ├── suggest_protocols.py
│   │   ├── supabase_schema.sql
│   │   ├── supabase_schema_expansion.sql
│   │   ├── supabase_schema_protocols.sql
│   │   ├── supabase_search.py
│   │   ├── supabase_search_functions.sql
│   │   ├── supabase_setup.py
│   │   ├── supabase_sync.py
│   │   ├── sync_to_public.py
│   │   ├── telegram_bot.py
│   │   ├── test_memori.py
│   │   ├── test_scripts.py
│   │   ├── test_supabase.py
│   │   ├── token_budget.py
│   │   ├── transcribe_audio.py
│   │   ├── transcribe_video.py
│   │   ├── update_metrics.py
│   │   ├── update_prime_hash.py
│   │   ├── upload_to_supabase.py
│   │   ├── verify_analyst.py
│   │   ├── verify_ingestion.py
│   │   ├── visualize_graph.py
│   │   └── watchdog.py
│   ├── skills/
│   │   ├── SKILL_INDEX.md
│   │   ├── capabilities/
│   │   │   ├── CAP-distribution-automation.md
│   │   │   ├── Skill_Agents_Context.md
│   │   │   ├── Skill_Claude_Code_Orchestration.md
│   │   │   ├── Skill_DSPy_Optimized.md
│   │   │   ├── Skill_DeepCode_Analysis.md
│   │   │   ├── Skill_DeepVoice_Resonance.md
│   │   │   ├── Skill_Document_Factory.md
│   │   │   ├── Skill_Fleet_Management.md
│   │   │   ├── Skill_Frontend_Design.md
│   │   │   ├── Skill_GraphRAG.md
│   │   │   ├── Skill_LinkedIn_Post.md
│   │   │   ├── Skill_MCP_Architecture.md
│   │   │   ├── Skill_MCP_Builder.md
│   │   │   ├── Skill_Memori_SQL_Memory.md
│   │   │   ├── Skill_Skill_Creator.md
│   │   │   ├── assets/
│   │   │   │   └── linkedin_visual_reference.jpg
│   │   │   ├── codebase_qa.md
│   │   │   └── context_compression.md
│   │   ├── fantasy-framework-detection/
│   │   │   ├── SKILL.md
│   │   │   └── resources/
│   │   │       └── asymmetry-table.md
│   │   └── protocols/
│   │       ├── architecture/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/architecture/099-session-output-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/101-compaction-recovery.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/102-skills-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/108-bionic-operational-physics.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/139-decentralized-command.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/158-entity-lookup-before-analysis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/159-verification-before-claim.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/168-context-driven-development.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/200-feature-context-persistence.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/202-recovery-patterns.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/210-data-lifecycle-strategy.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/215-canonical-memory.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/24-modular-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/architecture/243-context-engineering.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/250-rev9-identity-architecture.md
│   │       │   ├── 77-adaptive-latency-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/85-token-hygiene.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/87-container-sandboxing.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/89-hybrid-token-conservation.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/93-forward-only-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/96-latency-indicator.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/98-depth-vs-width-theory.md
│   │       │   └── System_Manifest.md
│   │       ├── business/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/106-distribution-physics.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/108-direct-response-halbert.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/Strategic_Analysis_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/127-recursive-value-trap.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/160-certainty-offer.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/230-unit-economics-physics.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/Strategic_Analysis_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/76-flywheel-architecture.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/84-vdestiny-canon.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/Strategic_Analysis_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/91-pearson-synthesis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/92-formal-informal-reality-gap.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/business/96-income-hierarchy.md
│   │       ├── case-studies/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/case-studies/27-sg-healthcare-de-facto.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/case-studies/33-chia-boon-teck-case.md
│   │       ├── communication/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Adaptive_Response_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── 243-exhibit-mode-communication.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Strategic_Influence_Protocols.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Adaptive_Response_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Adaptive_Response_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Interaction_Architecture_Hub.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/communication/Adaptive_Response_Standard.md
│   │       ├── community/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/community/118-egregore-protocol.md
│   │       ├── content/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/content/Content_Publication_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/content/221-high-performance-ux-design.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/content/231-llm-seeding-geo-strategy.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/content/232-ai-trajectory-alignment.md
│   │       ├── creation/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/creation/142-metaphorical-design-injection.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/creation/242-latent-cluster-activation.md
│   │       ├── decision/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/09-recursive-decision-navigator.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/10-mutual-calibration-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/109-principles-dalio.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/11-possible-probable-trap.md
│   │       │   ├── 110-einstein-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/111-premise-audit.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/115-first-principles-deconstruction.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/118-soep-framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/12-grace-model.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/123-einstein-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/124-sdr-diagnosis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/125-soep-framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/128-sovereign-paths.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/129-horizon-split-framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/13-rsi-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/131-bimodal-arena-analysis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/135-information-asymmetry-immunity.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/137-graph-of-thoughts.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/14-rsi-integrity.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/140-base-rate-audit.md
│   │       │   ├── 140-zero-point-inversion.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/161-sovereign-operating-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/163-precommitment-heuristic.md
│   │       │   ├── 170-iterative-refinement-loop.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/180-utility-function-analysis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/181-sdr-diagnostic.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/185-premise-validation-gate.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/187-terminal-node-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/188-stpp-timeline-projection.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/193-ergodicity-check.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/243-delulu-gap-heuristic.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/40-frame-vs-structural-problem.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/49-efficiency-robustness-tradeoff.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/64-commitment-device-framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/94-bionic-cognitive-pipeline.md
│   │       ├── diagnostics/
│   │       │   ├── DIAG-001-knowledge-action-gap.md
│   │       │   ├── DIAG-002-baseline-check.md
│   │       │   ├── DIAG-003-frame-collision.md
│   │       │   └── DIAG-004-chat-forensics.md
│   │       ├── economics/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/economics/033-principal-agent-problem.md
│   │       ├── engineering/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── 250-project-spec-mandate.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │       ├── health/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/health/122-physiological-operating-system.md
│   │       ├── leadership/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/leadership/146-containment-defense.md
│   │       ├── meta/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/meta/110-zero-point-protocol.md
│   │       ├── pattern-detection/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/112-form-substance-gap.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/117-randian-dilemma.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/15-divine-call-trap.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/16-graph-of-thoughts-theory.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/17-three-timeline-got.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/18-probabilistic-analysis-stack.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/21-edge-case-reductio.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/23-isomorphism-detection.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/30-arena-taxonomy.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/34-rigged-game-principle.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/47-bs-detection.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/83-depth-principle.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/95-cynical-baseline.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/97-ai-slop-detection.md
│   │       ├── psychology/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/107-integrated-therapeutic-mode.md
│   │       │   ├── 113-limerent-distortion.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/113-missing-baseline-model.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/114-limerent-reality-distortion.md
│   │       │   ├── 114-missing-baseline.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/120-power-inversion.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/122-good-boy-paradox.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/134-symbolic-transmutation.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/158-relationship-tier-audit.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/159-augmentation-circuit-breaker.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/165-source-code-calibration.md
│   │       │   ├── 184-missing-baseline-model.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/186-soep-second-order-effects.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/189-correct-container-principle.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/19-state-greater-than-act.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/191-heavy-light-game.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/194-three-mode-calibration.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/195-friend-portfolio-model.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/196-schema-deconstruction-stack.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/197-deterministic-logic-error.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/20-adult-adult-communication.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/22-divine-call-archaeology.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/25-reliving-vs-processing.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/26-filter-stack-model.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/29-disappointment-fork.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/31-anthropic-skills.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/32-naggers-knowing-saying.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/35-emotional-intensity-dysregulation.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/36-schema-installation-gaslighting.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/37-double-bind-trap.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/43-template-installation.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/58-silent-8-scarcity-break.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/59-mirror-instantiation.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/71-acting-out-cycle.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/82-cognitive-dissonance-hooks.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/98-social-audit-defense.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/99-the-velvet-rope.md
│   │       ├── reasoning/
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/reasoning/169-re2-rereading.md
│   │       ├── research/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/52-deep-research-loop.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/54-cyborg-methodology.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/research/67-cross-pollination.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/70-agentic-absorption.md
│   │       ├── safety/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/104-seymour-skeptic-layer.md
│   │       │   ├── 121-reality-gate-hope-override.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/170-dissonance-threshold-crisis.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/241-honesty-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/48-circuit-breaker-systemic.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/68-anti-karason-protocol.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/safety/80-citadel-recovery-architecture.md
│   │       │   ├── LAW1_RUIN.md
│   │       │   └── RISK_PLAYBOOKS.md
│   │       ├── singapore/
│   │       │   ├── SG-001-randian-sg.md
│   │       │   ├── SG-002-face-physics.md
│   │       │   ├── SG-003-ns-arena.md
│   │       │   ├── SG-004-system-auto-immune.md
│   │       │   └── SG-005-academic-compression.md
│   │       ├── social/
│   │       │   └── LinkedIn_Publication_Strategy.md
│   │       ├── strategy/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/121-amoral-realism.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/162-product-market-operations-fit.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/192-systematic-reconstruction.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/strategy/42-red-blue-curve-taxonomy.md
│   │       │   └── SDR_CALCULATOR.md
│   │       ├── trading/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/trading/46-trading-methodology.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/trading/56-shopee-refugee-arbitrage.md
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/trading/57-influencers-put-option.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/trading/65-arbitrage-formula.md
│   │       ├── verification/
│   │       │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/verification/141-claim-atomization-audit.md
│   │       │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/verification/171-cross-model-validation.md
│   │       └── workflow/
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/103-promptography.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/130-vibe-coding.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/171-bionic-operational-physics.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/workflow/53-adventure-mode.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/62-co-thinking-interface.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/69-iterative-siege.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/72-proactive-extrapolation-framework.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/73-contextual-pre-action-check.md
│   │           ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/74-iterative-creative-production.md
│   │           └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/81-forge-iteration.md
│   ├── templates/
│   │   ├── CASE_STUDY_SPEC_TEMPLATE.md
│   │   ├── PROJECT_CONTEXT_TEMPLATE.md
│   │   ├── REPO_SPEC_TEMPLATE.md
│   │   └── vibecoding_spec.json
│   ├── tests/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── core_laws/
│   │   │   ├── test_law0_subjective.md
│   │   │   ├── test_law1_ruin.md
│   │   │   ├── test_law2_arena.md
│   │   │   └── test_law3_revealed.md
│   │   ├── identity/
│   │   │   └── test_not_assistant.md
│   │   ├── test_quicksave_smoke.py
│   │   └── test_sync_smoke.py
│   └── workflows/
│       ├── audit-code.md
│       ├── audit.md
│       ├── brief.md
│       ├── circuit.md
│       ├── deploy.md
│       ├── diagnose.md
│       ├── due-diligence.md
│       ├── dump.md
│       ├── easy.md
│       ├── end.md
│       ├── guide.md
│       ├── needful.md
│       ├── primer.md
│       ├── refactor.md
│       ├── reindex.md
│       ├── research.md
│       ├── resume.md
│       ├── save.md
│       ├── search.md
│       ├── semantic.md
│       ├── start.md
│       ├── steal.md
│       ├── think.md
│       ├── ultrathink.md
│       └── vibe.md
├── .context/
│   ├── Architecture_Hybrid_Memory.md
│   ├── CANONICAL.md
│   ├── KNOWLEDGE_GRAPH.md
│   ├── PROJECT_ARCHITECTURE.puml
│   ├── TAG_INDEX.md
│   ├── TECH_DEBT.md
│   ├── analysis/
│   │   └── session_review_2025_12_26.md
│   ├── audit/
│   │   ├── CEREMONY_TIER2.md
│   │   ├── DATA_GOVERNANCE.md
│   │   ├── RISK_REGISTER.md
│   │   └── SYSTEM_PRIMER.md
│   ├── cache/
│   │   ├── compression/
│   │   │   ├── 06e66e3e553f8ff00b9c5c7db44afd00_79537233.md
│   │   │   ├── 0d9ad3250049a272daa230571a8eeeaf_362818e7.md
│   │   │   ├── 0d9ad3250049a272daa230571a8eeeaf_b97901a2.md
│   │   │   ├── 0d9ad3250049a272daa230571a8eeeaf_f9a10eab.md
│   │   │   ├── 125453feefe55e55cee1268224498351_82df7e0e.md
│   │   │   ├── 1730d1cc0d201a59bab6ddfbe64f83ec_e8c57c3c.md
│   │   │   ├── 174703538d40082ae6520af52bab516a_174811a5.md
│   │   │   ├── 17b15cced97b74a8e2aa52875313b387_0cf4a3d9.md
│   │   │   ├── 17fde8b5e9f8e13b417cf27e2ba969fe_98a8e622.md
│   │   │   ├── 17fde8b5e9f8e13b417cf27e2ba969fe_fce014b1.md
│   │   │   ├── 1a76dfe8e5f5e1516c70e4b7e9d23cf9_aed03ba3.md
│   │   │   ├── 1d8afcb04f00a1bded351b92af13d4ee_c765eeb6.md
│   │   │   ├── 21b91629a8fecef68e6ca2acf50d952c_40a5de91.md
│   │   │   ├── 231845095676a0e66226feb08db65c06_e2aa5054.md
│   │   │   ├── 2590e280b53f0e9447c1562ff271856a_4a5a45ae.md
│   │   │   ├── 2590e280b53f0e9447c1562ff271856a_6ce8b63a.md
│   │   │   ├── 2590e280b53f0e9447c1562ff271856a_721ca74d.md
│   │   │   ├── 25deccb61624c2fe2e26f680d8ea01d4_026d43c3.md
│   │   │   ├── 2845fee3b6ea875bc8d2a636aaa0a90f_05441aab.md
│   │   │   ├── 2845fee3b6ea875bc8d2a636aaa0a90f_f9efab0c.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_131c6e8a.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_1d044f66.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_6eb084f0.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_a50911c3.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_a7bc4cac.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_ae0afc64.md
│   │   │   ├── 28dfb1e1c523119e7c9cb9445dfd5bae_e032371e.md
│   │   │   ├── 2a21d33a0bd8303fa449c3d51f6b0e79_924b7170.md
│   │   │   ├── 2bbf981936ed1e3937e58fb012b5945c_4e12c598.md
│   │   │   ├── 2bd3df1fde11095376d0a5b346f3e3f2_2020b4ae.md
│   │   │   ├── 2d69d5ff469c5e2327948951da7d15a5_d5333c73.md
│   │   │   ├── 2df795980b8b9ea79737ec41eb334c68_382b9516.md
│   │   │   ├── 2ec1e63e64423cdd1f93995645b9cfd6_a5a94b5d.md
│   │   │   ├── 2ecdf57d4ef62ace70c197464cb76871_29206193.md
│   │   │   ├── 2ecdf57d4ef62ace70c197464cb76871_57b0adde.md
│   │   │   ├── 2ecdf57d4ef62ace70c197464cb76871_a53cb1e8.md
│   │   │   ├── 31defc826c60f89b84c2790aa6296c55_5036d0b2.md
│   │   │   ├── 349f56b01fde160a38c249f5134257b3_a5a94b5d.md
│   │   │   ├── 35292bff2a96aa14787f2ecba1334bb1_37deeeb1.md
│   │   │   ├── 35a91e2ce7d0798236a3f353fe97c20a_2b4db4d7.md
│   │   │   ├── 360db1b952ac929cef371e8cc464ad47_a5f9d524.md
│   │   │   ├── 37bb32514b413954951938b5d5f74917_b03e3a4d.md
│   │   │   ├── 38d94feaf97f49b9ad0ac22b3984901a_b1cc9e3b.md
│   │   │   ├── 3aeebd162f467971c7071e9a752a46ff_9dbeeb80.md
│   │   │   ├── 3b9da08216903bafd73d804048f6e77a_841fb394.md
│   │   │   ├── 3b9da08216903bafd73d804048f6e77a_a4305c43.md
│   │   │   ├── 3b9da08216903bafd73d804048f6e77a_cb9cb103.md
│   │   │   ├── 3b9da08216903bafd73d804048f6e77a_d8436f1d.md
│   │   │   ├── 3cb22386b4c38c9b4c374893e6b87757_36d97621.md
│   │   │   ├── 3d07c6e775f93b6000fd9210854dd240_677c1949.md
│   │   │   ├── 3d15e4e272786a0793222ff7a2501d06_83d806ed.md
│   │   │   ├── 4042f4359e6d1f15ef14a0aad0932c85_a1c3439c.md
│   │   │   ├── 44b84bf461c8c87824350eb767ed172a_4e7546a5.md
│   │   │   ├── 44b84bf461c8c87824350eb767ed172a_ac21a39c.md
│   │   │   ├── 44b84bf461c8c87824350eb767ed172a_ff647d04.md
│   │   │   ├── 4537366c8b8b4c53f69b410d071ffa98_67ea681f.md
│   │   │   ├── 4871245759a22321b0f1ea717a4afcf7_a68596b9.md
│   │   │   ├── 4c1a05c4ccc7760c5485b53e2effd29d_d25e495a.md
│   │   │   ├── 4c2495a872f20853bf83e3424117fec4_0cf4a3d9.md
│   │   │   ├── 4c626a71e311546aafac917143fbb505_cfa33da7.md
│   │   │   ├── 541a2a7edfd1efc660cd57501c5aef06_8516c64c.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_41081bc7.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_82b3a3b4.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_ca9e2af9.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_d376f3b5.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_e326f7c6.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_ee487ebd.md
│   │   │   ├── 54e9cc4b42e1074e907e4637ef17ea86_f2c09471.md
│   │   │   ├── 57b43785b23b533b47f99e17427a003f_974bc8bc.md
│   │   │   ├── 59ff8afbfbf194fa76f189a6a357e981_c7def6e6.md
│   │   │   ├── 61b25f6e872dcdc3ea7e6bb21c4f9cfd_427895e7.md
│   │   │   ├── 61b25f6e872dcdc3ea7e6bb21c4f9cfd_753e953c.md
│   │   │   ├── 622fe8888a3e755a85d5b6497ea523b6_db0178e4.md
│   │   │   ├── 643e95dbabbea67138866a2056e531d2_ec1caf91.md
│   │   │   ├── 64b7a9d47604a7d6b99ee87355d3ef74_2e803769.md
│   │   │   ├── 64fb76e9c0608f6040d762aa65893252_aae59132.md
│   │   │   ├── 65ad7309ecbf7938dadb5c44c66ff8fc_952aa509.md
│   │   │   ├── 6834eabeb4c034171fddf1c86f2441eb_d724ffce.md
│   │   │   ├── 6baba9d9741ab02f6441fcb59dd84377_e8c57c3c.md
│   │   │   ├── 705e3c7a1fa4c3756a9337348caa8ec2_820cf26a.md
│   │   │   ├── 71a19b6cab790d30db56145a64df1909_d131e1bc.md
│   │   │   ├── 71c5dbfd4e79fa4fc0aa678717d56a2d_81b34ca2.md
│   │   │   ├── 72b8df84151ee2ab4411ca466231ab12_f43639b8.md
│   │   │   ├── 73bb8b524fb51be3482c0403a82079ca_bebbe875.md
│   │   │   ├── 75e6fe21aad54c6536cfe39a61565b7f_9dc48ca5.md
│   │   │   ├── 775639832062f32888fe14198e20b6a0_f72c55c8.md
│   │   │   ├── 786941fa81835e765d7c0370ecd67cae_13b38665.md
│   │   │   ├── 786941fa81835e765d7c0370ecd67cae_d8aedcd8.md
│   │   │   ├── 7e8d8306b59b6db7bc7155eda91bb3c6_a6803623.md
│   │   │   ├── 800ee455ea7c96d8d41493d592da0cbc_4393c7a4.md
│   │   │   ├── 80e740d5121fb9a18a5abd7cd5dd0eca_00191ced.md
│   │   │   ├── 80e740d5121fb9a18a5abd7cd5dd0eca_32f6b765.md
│   │   │   ├── 8122340db0717d4f16b6a39bb87fa175_7673ef9f.md
│   │   │   ├── 833ab84fcf9a3fce8e78aad5c4227e6e_cf6cfd89.md
│   │   │   ├── 833ab84fcf9a3fce8e78aad5c4227e6e_e3c542b4.md
│   │   │   ├── 833ab84fcf9a3fce8e78aad5c4227e6e_e8340441.md
│   │   │   ├── 859b9fb4e4782a3924090f6384854fb0_7f886005.md
│   │   │   ├── 88c503346ddae9f6e660d2233773d87a_6225fd90.md
│   │   │   ├── 8b2be3638b31b2228fa051e2032c695c_12d7dd66.md
│   │   │   ├── 8b7e8b1ba06d5b8a32a4c21581db59c2_7cad06b2.md
│   │   │   ├── 8bf6960c58872cea552a75735381de8a_1a79f9b6.md
│   │   │   ├── 8bf6960c58872cea552a75735381de8a_786d1063.md
│   │   │   ├── 8c23a7d8796f70040200e5e27598b1a0_6460e318.md
│   │   │   ├── 8d650015e4499e9db38b9daea9b2dfde_1fa33b7f.md
│   │   │   ├── 8d650015e4499e9db38b9daea9b2dfde_3cfc3ac6.md
│   │   │   ├── 8d650015e4499e9db38b9daea9b2dfde_52a2e3c3.md
│   │   │   ├── 8dc531ab25ed5f85e1171c6c3eb3f6ea_1a1a607a.md
│   │   │   ├── 8dd472db83fcedc76b8de314b2ec0d2f_fd778fd6.md
│   │   │   ├── 90b869d6d4d0d22c05cdff6ef5a2d8f6_27c1907c.md
│   │   │   ├── 91501867dac452f00a390d8471602caa_2020b4ae.md
│   │   │   ├── 91501867dac452f00a390d8471602caa_a07e43cb.md
│   │   │   ├── 941f2253003428659dda38c82654f5b9_2cd577cc.md
│   │   │   ├── 96919dbffb69032583d9ae0890c91b77_bdb80b31.md
│   │   │   ├── 973d1db7587562243a39642eb771d456_47575c8d.md
│   │   │   ├── 97408d0ed8c2e6cb0e1dfa7a0d7b82ed_2737c5f2.md
│   │   │   ├── 97ca157298c837711a547646cfd12613_36af8c12.md
│   │   │   ├── 9e2bbdd465a20f3858121c99907133b6_73c155f9.md
│   │   │   ├── 9e6810c7e8487529fcd7801a78dd90f2_d3e722bd.md
│   │   │   ├── a123c55144cc83a4276fb6322adc92c2_8a7c158e.md
│   │   │   ├── a30d5b4664a4af49c7f16e4f9e2d87bf_9e8c5728.md
│   │   │   ├── a553390bc83f865bbb91937c87882fcd_64154b9a.md
│   │   │   ├── ac2fd933d0885577332815e4e849ca48_d3e722bd.md
│   │   │   ├── ae2685d4d0806e3698f321a702584f5e_5a72f256.md
│   │   │   ├── ae2685d4d0806e3698f321a702584f5e_b99deeec.md
│   │   │   ├── ae2685d4d0806e3698f321a702584f5e_c8d5772f.md
│   │   │   ├── b1646dd41fdd1973b76dabfeefda5aa4_b39e478b.md
│   │   │   ├── b6b1d4ec12e7002935ab0cbee4ec26e6_f43639b8.md
│   │   │   ├── b9e328eaebbaedeaa26a8ec8d193d7fa_3d2e04d1.md
│   │   │   ├── b9e328eaebbaedeaa26a8ec8d193d7fa_78af339e.md
│   │   │   ├── ba133a8f71a9663be8c147d06e50aa69_1f945fa0.md
│   │   │   ├── bb0b4daaa041d412dc51f4c72e504d2c_06986a0b.md
│   │   │   ├── bb6c84ac37537a53222d91eedefa398a_08618e49.md
│   │   │   ├── bfe93679c32bd1f796332fba59c433f6_d672a49d.md
│   │   │   ├── c2ab1f2364664478d24a430a0eb395a3_639c9b82.md
│   │   │   ├── c6b46c187a459f0a8b4ab5ea56b7ed2b_9dc48ca5.md
│   │   │   ├── c6c9eeeddd1c750cea0f92fa4b1c08ce_3f3ca7ce.md
│   │   │   ├── c77d76348122400c30d2433d94d59651_6dcb309b.md
│   │   │   ├── c83019e36da282c0a37f2d896d700e8e_9dbeeb80.md
│   │   │   ├── c92bf8d2e9d48984db2cdede6c45e0bf_73e7451a.md
│   │   │   ├── c990bd6f70e51c172c58f66f9ecadad3_c960a0c9.md
│   │   │   ├── cc524d7099d13a354dfd92d8a43b34df_051823ee.md
│   │   │   ├── cc76eef26aa025c74c4905c39d2260c0_73e7451a.md
│   │   │   ├── d196c79292b0e63531ee17b2e9237253_e0056427.md
│   │   │   ├── d45c73d4970eccf1f86184d0ce1e8fb5_003c0ac2.md
│   │   │   ├── d8abd9b8ba707e2e9eeac397585f4c67_242a3d05.md
│   │   │   ├── d914a89374fe2ca8175bf7aedcb96546_8162600b.md
│   │   │   ├── d93fc6bf7a33fc850d67e5d990709376_1bceda15.md
│   │   │   ├── d93fc6bf7a33fc850d67e5d990709376_61927757.md
│   │   │   ├── d9af93fe69cfb7efec696c325643d4af_b39e478b.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_034948f5.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_4e6e452b.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_5e902173.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_60677b51.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_701a7ace.md
│   │   │   ├── db9a75e33c918c3e0c4802e40b71ee6a_94c05cfa.md
│   │   │   ├── df55f428911f0757112bbe2e61d0aa29_6a4fa199.md
│   │   │   ├── dfc26ffe12ccc7275e64eb0f524987f7_bebbe875.md
│   │   │   ├── e15a608f5db300429ee5d13148b57115_463856f5.md
│   │   │   ├── e2c0eccc12df52ba63a057f4577688ce_974bc8bc.md
│   │   │   ├── e459e9bc84d8b4302c9f682b1a5e0ac9_9c47b81c.md
│   │   │   ├── e6d3ab9752b6c7de502cbff9e36db8d5_75bb4750.md
│   │   │   ├── e8c90176649c4e0c82a188a017966f8a_887e35f2.md
│   │   │   ├── e991777182738a5ec1e747c155078650_561c52ac.md
│   │   │   ├── ecc8c0a39f28b9205b627d3487ba6c4e_94617863.md
│   │   │   ├── ecc8c0a39f28b9205b627d3487ba6c4e_fa2d69a4.md
│   │   │   ├── eec7a02677048f5f3a2b0efeefeab18e_ceba5847.md
│   │   │   ├── ef357969a4cf86307dddfd9f3c5d5842_4cb20cbc.md
│   │   │   ├── ef6e55f1d7279bbcc8d6e0f9b86d7253_c960a0c9.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_140dc41c.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_47461d00.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_508652c2.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_619869a9.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_71e2b7f7.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_800b16c3.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_9835b9f9.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_9b6b5c03.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_f3c94da4.md
│   │   │   ├── f0bc12588ac53e49aea0c02013b4ae2e_fd858664.md
│   │   │   ├── f35b5c94db152ad6d0740d7bedcf8750_64154b9a.md
│   │   │   ├── f4a8c9aa429bc8eccacd7a57cd8a0f9c_1a46375e.md
│   │   │   ├── f4a8c9aa429bc8eccacd7a57cd8a0f9c_f7062887.md
│   │   │   ├── fcbf1ebd74ac304daef75d28a3dd1e14_6aac8378.md
│   │   │   ├── fe6e9af0984a1ade96640fdeec7ae2af_4350effe.md
│   │   │   └── metadata_index.json
│   │   └── scripts_compressed.md
│   ├── codebase_compressed.txt
│   ├── design/
│   │   └── concept_n8n_trilateral.md
│   ├── features/

│   ├── implementation_plans/
│   │   └── 2025-12-27_website_audit.md
│   ├── journals/
│   │   └── TEMPLATE.md
│   ├── memori.db
│   ├── memories/
│   │   ├── Architectural_Critique_2025.md
│   │   ├── Audit_Report_2025_12_13.md
│   │   ├── Strategic_Analysis_2025_12_14.md
│   │   ├── case_studies/
│   │   │   ├── BIZ-002-pitch-deck-principles.md
│   │   │   ├── BIZ-DMA-002-digital-marketing-services-exploration.md
│   │   │   ├── CS-004-behavioral-economics.md
│   │   │   ├── CS-005-shower-probability.md
│   │   │   ├── CS-006-agency-economy.md
│   │   │   ├── CS-007-bukit-batok-solipsism.md
│   │   │   ├── CS-008-fa-extraction-cycle.md
│   │   │   ├── CS-009-plausible-deniability-shield.md
│   │   │   ├── CS-010-free-value-trap.md
│   │   │   ├── CS-011-friendship-forensics.md
│   │   │   ├── CS-012-hope-override-mechanism.md
│   │   │   ├── CS-013-agency-paternalism.md
│   │   │   ├── CS-014-compliance-loop-daryl.md
│   │   │   ├── CS-015-toxic-positivity-economics.md
│   │   │   ├── CS-016-sovereign-heel-sry.md
│   │   │   ├── CS-017-neoh-yong-guru-marketing.md
│   │   │   ├── CS-037-samuel-rondot-validated-cloning.md
│   │   │   ├── CS-038-meetwhere-distribution-physics.md
│   │   │   ├── CS-039-preschool-coverup-gag-order-physics.md
│   │   │   ├── CS-040-andy-coffee-shop.md
│   │   │   ├── CS-041-thea1physics-distribution.md
│   │   │   ├── CS-042-better-call-saul-positioning.md
│   │   │   ├── CS-043-melvin-portfolio-concept.md
│   │   │   ├── CS-044-ilp-trust-arbitrage.md
│   │   │   ├── CS-045-bcm-silent-partner-workflow.md
│   │   │   ├── CS-046-client-negotiation-clawback-trap.md
│   │   │   ├── CS-047-singapore-pools-hope-tax.md
│   │   │   ├── CS-048-zenithfx-gatekeeper-protocol.md
│   │   │   ├── CS-049-moneylender-debt-spiral.md
│   │   │   ├── CS-050-samchoon-arrested-development.md
│   │   │   ├── CS-051-oc-shower-dynamics.md
│   │   │   ├── CS-052-naive-idealism-tax.md
│   │   │   ├── CS-053-reuben-wang-schema-error.md
│   │   │   ├── CS-054-zero-moat-fallacy.md
│   │   │   ├── CS-055-umbrage-frame-collapse.md
│   │   │   ├── CS-056-weaponized-vulnerability-jj.md
│   │   │   ├── CS-057-independence-horizon-n1000.md
│   │   │   ├── CS-058-singapore-policy-failures.md
│   │   │   ├── CS-059-sutd-confession.md
│   │   │   ├── CS-060-migma-compiler-moat.md
│   │   │   ├── CS-061-poetiq-scaffolding-analysis.md
│   │   │   ├── CS-062-vibe-coding-gap.md
│   │   │   ├── CS-063-analysis-jj-junkai-gemini.md
│   │   │   ├── CS-064-analysis-thirteen-xyz-audit.md
│   │   │   ├── CS-065-analysis-vdestiny-market-gap.md
│   │   │   ├── CS-066-biz-dma-001-digital-marketing-folder.md
│   │   │   ├── CS-067-12-20-pattern-seed.md
│   │   │   ├── CS-068-12-21-astroturfing-humblebrag.md
│   │   │   ├── CS-069-antipatterns-reddit.md
│   │   │   ├── CS-070-apprenticeship-leverage.md
│   │   │   ├── CS-071-auto-claude-orchestration.md
│   │   │   ├── CS-072-backlinko-seo-2026.md
│   │   │   ├── CS-073-bionic-convergence.md
│   │   │   ├── CS-074-blog-evolution-2026.md
│   │   │   ├── CS-075-carousell-gap-analysis.md
│   │   │   ├── CS-076-child-aggression-calibration.md
│   │   │   ├── CS-077-child-aggression-gold-standard.md
│   │   │   ├── CS-078-claude-workflow-erik-cupsa.md
│   │   │   ├── CS-079-context-first-application.md
│   │   │   ├── CS-080-cost-estimation-overclaim.md
│   │   │   ├── CS-081-cozyplace-shadow-hotel.md
│   │   │   ├── CS-082-dark-forest-github-traffic.md
│   │   │   ├── CS-083-digital-brain-theft-paradox.md
│   │   │   ├── CS-084-edmw-lift-scenario.md
│   │   │   ├── CS-085-end-of-jobs-framework.md
│   │   │   ├── CS-086-ex-friend-reality-gap.md
│   │   │   ├── CS-087-gpt5-math-novelty.md
│   │   │   ├── CS-088-grit-quota-arbitrage.md
│   │   │   ├── CS-089-grab-driver-economics.md
│   │   │   ├── CS-090-healthcare-sunk-cost-cartel.md
│   │   │   ├── CS-091-ilp-upstream-fallacy.md
│   │   │   ├── CS-092-intj-vs-entj-command-heuristic.md
│   │   │   ├── CS-093-influencer-sponsorship-ask.md
│   │   │   ├── CS-094-jj-sorry-babe-trap.md
│   │   │   ├── CS-095-joya-onsen-hijack.md
│   │   │   ├── CS-096-linkedin-outreach.md
│   │   │   ├── CS-097-paradigm-math-productized-service.md
│   │   │   ├── CS-098-precommitment-asymmetric-downside.md
│   │   │   ├── CS-099-prison-correspondence-yeo-hoe-soon.md
│   │   │   ├── CS-100-project-vend-agentic-failure.md
│   │   │   ├── CS-101-protocol-92-cluster-2025.md
│   │   │   ├── CS-102-retrenched-tech-worker.md
│   │   │   ├── CS-103-sgfr-trend-trap.md
│   │   │   ├── CS-104-sg-retail-death-spiral.md
│   │   │   ├── CS-105-sam-altman-ai-future.md
│   │   │   ├── CS-106-sandai-fishball-trap.md
│   │   │   ├── CS-107-shame-niche-education.md
│   │   │   ├── CS-107-third-choice-generation.md
│   │   │   ├── CS-108-addiction-modulator-pattern.md
│   │   │   ├── CS-108-singapore-social-contract-collapse.md
│   │   │   ├── CS-109-singapore-web-traffic-2025.md
│   │   │   ├── CS-110-soh-vs-snoc.md
│   │   │   ├── CS-111-study-datodurian-rwa.md
│   │   │   ├── CS-112-study-jun-kai-paradox.md
│   │   │   ├── CS-113-the-14-day-silence.md
│   │   │   ├── CS-114-the-17-year-old-hawker.md
│   │   │   ├── CS-115-the-haunting-invalidation.md
│   │   │   ├── CS-116-transformation-chat-to-os.md
│   │   │   ├── CS-117-tuition-agent-incentives.md
│   │   │   ├── CS-118-tutor-distribution-trap.md
│   │   │   ├── CS-119-vdestiny-business-model.md
│   │   │   ├── CS-120-vibe-coding-zero-cost-stack.md
│   │   │   ├── CS-121-first-mover-analysis.md
│   │   │   ├── CS-122-web-design-2026.md
│   │   │   ├── CS-123-wordplay-value-collapse.md
│   │   │   ├── CS-124-idea-carousell-portfolio-service.md
│   │   │   ├── CS-125-jeremy-ryan-case.md
│   │   │   ├── CS-126-jun-kai-case.md
│   │   │   ├── CS-127-mental-model-business-traps.md
│   │   │   ├── CS-128-pool-incident-case.md
│   │   │   ├── CS-129-carousell-gap.md
│   │   │   ├── CS-130-umbrage-ng-frame-collapse.md
│   │   │   ├── CS-130-vibem8-friend-matching-friction.md
│   │   │   ├── CS-131-teen-hawker.md
│   │   │   ├── CS-132-sandai-fishball.md
│   │   │   ├── CS-133-water-polo-trap.md
│   │   │   ├── CS-134-jj-protocol.md
│   │   │   ├── CS-135-reuben-soh-attack-surface.md
│   │   │   ├── CS-136-the-managed-out-trap.md
│   │   │   ├── CS-137-adverdize-competitor-analysis.md
│   │   │   ├── CS-215-ai-influencer-automation.md
│   │   │   ├── CS-138-ai-photography-bridge-income.md
│   │   │   ├── CS-216-portfolio-meta-analysis.md
│   │   │   ├── CS-139-analysis-psyche-deep-dive-archived.md
│   │   │   ├── CS-140-bcm-silent-partner-analysis.md
│   │   │   ├── CS-141-study-samtrade-goh-nai-de.md
│   │   │   ├── CS-142-study-tuition-trap.md
│   │   │   ├── CS-143-geo-seo-for-ai-models.md
│   │   │   ├── CS-144-awwl-distribution-niche-basics.md
│   │   │   ├── CS-218-n8n-auto-blog-workflow.md
│   │   │   ├── CS-145-dchtoons-schlep-sovereignty.md
│   │   │   ├── Case_Grab_Driver_Economics.md
│   │   │   ├── Case_LinkedIn_Shitali.md
│   │   │   ├── SGP-CORP-001-umbrage-ng-frame-collapse.md
│   │   │   ├── assets/
│   │   │   │   ├── bench_display.svg
│   │   │   │   ├── business_curves_vis.png
│   │   │   │   ├── changing_room_map.svg
│   │   │   │   ├── command_structures.png
│   │   │   │   ├── hybrid_command.png
│   │   │   │   ├── shower_mechanics.svg
│   │   │   │   ├── shower_spit_roast.svg
│   │   │   │   ├── social_curves_vis.png
│   │   │   │   ├── social_curves_vis_final.png
│   │   │   │   ├── social_curves_vis_final_v2.png
│   │   │   │   └── threesome_mechanics.svg
│   │   │   └── relationship_timeline.svg
│   │   ├── search_log.txt
│   │   ├── session_logs/
│   │   │   ├── 2025-12-26-session-06.md
│   │   │   ├── 2025-12-26-session-07.md
│   │   │   ├── 2025-12-26-session-08.md
│   │   │   ├── 2025-12-26-session-09.md
│   │   │   ├── 2025-12-26-session-10.md
│   │   │   ├── 2025-12-26-session-11.md
│   │   │   ├── 2025-12-26-session-12.md
│   │   │   ├── 2025-12-26-session-13.md
│   │   │   ├── 2025-12-26-session-14.md
│   │   │   ├── 2025-12-26-session-15.md
│   │   │   ├── 2025-12-26-session-16.md
│   │   │   ├── 2025-12-26-session-17.md
│   │   │   ├── 2025-12-26-session-18.md
│   │   │   ├── 2025-12-26-session-19.md
│   │   │   ├── 2025-12-26-session-20.md
│   │   │   ├── 2025-12-26-session-21.md
│   │   │   ├── 2025-12-26-session-22.md
│   │   │   ├── 2025-12-26-session-23.md
│   │   │   ├── 2025-12-26-session-24.md
│   │   │   ├── 2025-12-26-session-25.md
│   │   │   ├── 2025-12-26-session-26.md
│   │   │   ├── 2025-12-26-session-27.md
│   │   │   ├── 2025-12-26-session-28.md
│   │   │   ├── 2025-12-26-session-29.md
│   │   │   ├── 2025-12-26-session-30.md
│   │   │   ├── 2025-12-26-session-31.md
│   │   │   ├── 2025-12-26-session-32.md
│   │   │   ├── 2025-12-26-session-33.md
│   │   │   ├── 2025-12-26-session-34.md
│   │   │   ├── 2025-12-27-session-01.md
│   │   │   ├── 2025-12-27-session-02.md
│   │   │   ├── 2025-12-27-session-03.md
│   │   │   ├── 2025-12-27-session-04.md
│   │   │   ├── 2025-12-27-session-05.md
│   │   │   ├── 2025-12-27-session-06.md
│   │   │   ├── 2025-12-27-session-07.md
│   │   │   ├── 2025-12-27-session-08.md
│   │   │   ├── 2025-12-27-session-09.md
│   │   │   ├── 2025-12-27-session-10.md
│   │   │   ├── 2025-12-27-session-11.md
│   │   │   ├── 2025-12-27-session-12.md
│   │   │   ├── 2025-12-27-session-13.md
│   │   │   ├── 2025-12-27-session-14.md
│   │   │   ├── 2025-12-27-session-15.md
│   │   │   ├── 2025-12-27-session-16.md
│   │   │   ├── 2025-12-27-session-17.md
│   │   │   ├── 2025-12-27-session-18.md
│   │   │   ├── 2025-12-27-session-19.md
│   │   │   ├── 2025-12-27-session-20.md
│   │   │   ├── 2025-12-28-session-01.md
│   │   │   ├── 2025-12-28-session-02.md
│   │   │   ├── 2025-12-28-session-03.md
│   │   │   ├── 2025-12-28-session-04.md
│   │   │   ├── 2025-12-28-session-05.md
│   │   │   ├── 2025-12-28-session-06.md
│   │   │   ├── 2025-12-28-session-07.md
│   │   │   ├── 2025-12-28-session-08.md
│   │   │   ├── 2025-12-28-session-09.md
│   │   │   ├── 2025-12-28-session-10.md
│   │   │   ├── 2025-12-28-session-11.md
│   │   │   ├── 2025-12-28-session-12.md
│   │   │   ├── 2025-12-28-session-13.md
│   │   │   ├── 2025-12-28-session-14.md
│   │   │   ├── 2025-12-28-session-15.md
│   │   │   ├── 2025-12-28-session-16.md
│   │   │   ├── 2025-12-28-session-17.md
│   │   │   ├── 2025-12-28-session-18.md
│   │   │   ├── 2025-12-28-session-19.md
│   │   │   ├── 2025-12-28-session-20.md
│   │   │   ├── 2025-12-28-session-21.md
│   │   │   ├── 2025-12-28-session-22.md
│   │   │   ├── 2025-12-28-session-23.md
│   │   │   ├── 2025-12-28-session-24.md
│   │   │   ├── 2025-12-28-session-25.md
│   │   │   ├── 2025-12-28-session-26.md
│   │   │   ├── 2025-12-28-session-27.md
│   │   │   ├── 2025-12-28-session-28.md
│   │   │   ├── 2025-12-28-session-29.md
│   │   │   ├── 2025-12-29-session-05.md
│   │   │   ├── 2025-12-29-session-06.md
│   │   │   ├── 2025-12-29-session-07.md
│   │   │   ├── 2025-12-29-session-08.md
│   │   │   ├── 2025-12-29-session-09.md
│   │   │   ├── 2025-12-29-session-10.md
│   │   │   ├── 2025-12-29-session-11.md
│   │   │   ├── 2025-12-29-session-12.md
│   │   │   ├── 2025-12-30-session-01.md
│   │   │   ├── 2025-12-30-session-02.md
│   │   │   ├── 2025-12_Analysis.md
│   │   │   └── analysis/
│   │   │       └── 2025-12-21-ultrathink-blindspots.md
│   │   ├── strategic_analysis/
│   │   │   └── Strategic_Analysis_2025-12-26_Gemini_Audit.md
│   │   ├── templates/
│   │   │   └── session_log_template.md
│   │   └── visualizations/
│   │       ├── athena_graph_live.html
│   │       ├── graphrag_visual.png
│   │       └── structure_map.html
│   ├── metrics/
│   │   └── refactor_log.csv
│   ├── playbooks/
│   │   ├── Playbook_Business_Coordination_Model.md
│   │   ├── Playbook_Career_Crisis_Navigation.md
│   │   ├── Playbook_Locker_Room_1on1.md
│   │   ├── Playbook_Psychological_Profiling.md
│   │   └── Playbook_Seduction_First_Timer.md
│   ├── project_state.md
│   ├── raw_data/
│   │   └── psychology/
│   │       └── 2025-12_chat_export.json
│   ├── references/
│   │   ├── Reference_25Y90D_Focus_Framework.md
│   │   ├── Reference_API_Cost_Tracker.md
│   │   ├── Reference_Blue_Herring_Academy.md
│   │   ├── Reference_Claude_Pricing.md
│   │   ├── Reference_Competitor_Models.md
│   │   ├── Reference_Gary_Halbert_Frameworks.md
│   │   ├── Reference_Paul_Graham_Frameworks.md
│   │   ├── Reference_Prompt_AntiPatterns.md
│   │   ├── Reference_Prompter_Evolution.md
│   │   ├── Reference_Ray_Dalio_Principles.md
│   │   ├── Reference_SOTA_Models_Dec2025.md
│   │   ├── Reference_Taylor_Pearson_Frameworks.md
│   │   ├── References.md
│   │   └── Zero_Point_Codex.md
│   ├── scenarios/
│   │   ├── Scenario_Locker_Room_Decision_Tree.md
│   │   └── Scenario_Locker_Room_Flow_V2.md
│   ├── strategies/
│   │   ├── Strategy_Platform_Leakage.md
│   │   └── Strategy_Tuition_Market_Analysis.md
│   └── task.md
├── .framework/
│   └── v7.0/
│       ├── MANIFESTO.md
│       └── modules/
│           ├── Core_Identity.md
│           ├── Governance_Audit_2025.md
│           ├── System_Principles.md
│           ├── Output_Standards.md
│           ├── System_Manifest.md
│           └── System_Principles.md
├── .gitignore
├── ARCHITECTURE.md
├── Athena-Public/
│   ├── .gitignore
│   ├── LICENSE
│   ├── README.md
│   ├── community/
│   │   ├── CHANGELOG.md
│   │   ├── CODE_OF_CONDUCT.md
│   │   ├── CONTRIBUTING.md
│   │   ├── ROADMAP.md
│   │   └── SECURITY.md
│   ├── docs/
│   │   ├── ARCHITECTURE.md
│   │   ├── FEATURES.md
│   │   ├── GETTING_STARTED.md
│   │   ├── GLOSSARY.md
│   │   ├── SEMANTIC_SEARCH.md
│   │   ├── TAG_INDEX.md
│   │   ├── VECTORRAG.md
│   │   ├── athena_banner.png
│   │   ├── case-studies/
│   │   │   ├── Case_Blog_Evolution_2026.md
│   │   │   ├── Case_Sam_Altman_AI_Future.md
│   │   │   ├── Case_Web_Design_2026.md
│   │   │   └── Decision_Framework_Application.md
│   │   ├── concepts/
│   │   │   └── Cognitive_Architecture.md
│   │   ├── protocols/
│   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/131-bimodal-arena-analysis.md
│   │   │   ├── RISK_PLAYBOOKS.md
│   │   │   ├── content/
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/content/Content_Publication_Standard.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/content/221-high-performance-ux-design.md
│   │   │   │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/content/232-ai-trajectory-alignment.md
│   │   │   └── engineering/
│   │   │       └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   └── tri-lateral-iteration.md
│   ├── examples/
│   │   ├── ANALYTICS_REPORT.md
│   │   ├── CASE_STUDY_EXAMPLE.md
│   │   ├── DEMO_SCRIPT.md
│   │   ├── PATTERN_EXAMPLE.md
│   │   ├── case_studies/
│   │   │   ├── CS-120-vibe-coding-zero-cost-stack.md
│   │   │   ├── CS-140-bcm-silent-partner-analysis.md
│   │   │   └── CS-218-n8n-auto-blog-workflow.md
│   │   ├── concepts/
│   │   │   ├── adaptive_latency.md
│   │   │   ├── amoral_realism.md
│   │   │   ├── anti_hallucination.md
│   │   │   ├── origin_story.md
│   │   │   └── paradigm_shift.md
│   │   ├── demo.html
│   │   ├── demo.webp
│   │   ├── demo_screenshot.png
│   │   ├── graphrag_visualization.png
│   │   ├── knowledge_graph_demo.html
│   │   ├── logs/
│   │   │   └── debug_session_example.md
│   │   ├── protocols/
│   │   │   ├── architecture/
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/101-compaction-recovery.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/102-skills-architecture.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/108-bionic-operational-physics.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/139-decentralized-command.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/158-entity-lookup-before-analysis.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/159-verification-before-claim.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/168-context-driven-development.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/200-feature-context-persistence.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/202-recovery-patterns.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/210-data-lifecycle-strategy.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/215-canonical-memory.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/24-modular-architecture.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/250-rev9-identity-architecture.md
│   │   │   │   ├── 77-adaptive-latency-architecture.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/85-token-hygiene.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/87-container-sandboxing.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/89-hybrid-token-conservation.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/93-forward-only-architecture.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/96-latency-indicator.md
│   │   │   │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/98-depth-vs-width-theory.md
│   │   │   ├── engineering/
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Infrastructure_Hub.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Execution_Standard.md
│   │   │   ├── meta/
│   │   │   │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/meta/110-zero-point-protocol.md
│   │   │   ├── research/
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/52-deep-research-loop.md
│   │   │   │   ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/54-cyborg-methodology.md
│   │   │   │   └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/70-agentic-absorption.md
│   │   │   └── workflow/
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/103-promptography.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/130-vibe-coding.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/171-bionic-operational-physics.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/62-co-thinking-interface.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/69-iterative-siege.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/72-proactive-extrapolation-framework.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/73-contextual-pre-action-check.md
│   │   │       ├── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/74-iterative-creative-production.md
│   │   │       └── file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/workflow/81-forge-iteration.md
│   │   ├── scripts/
│   │   │   ├── analyze.py
│   │   │   ├── antigravity_server.py
│   │   │   ├── ask_codebase.py
│   │   │   ├── audit_graph_coverage.py
│   │   │   ├── audit_session_costs.py
│   │   │   ├── auto_linker.py
│   │   │   ├── auto_tagger.py
│   │   │   ├── batch_audit.py
│   │   │   ├── boot.py
│   │   │   ├── browser_agent.py
│   │   │   ├── build_graph.py
│   │   │   ├── calendar_agent.py
│   │   │   ├── compress_context.py
│   │   │   ├── compress_memory.py
│   │   │   ├── compress_sessions.py
│   │   │   ├── context_capture.py
│   │   │   ├── cross_reference.py
│   │   │   ├── diagnose.py
│   │   │   ├── embed_codex.py
│   │   │   ├── extract_entities.py
│   │   │   ├── extract_keyframes.py
│   │   │   ├── gemini_client.py
│   │   │   ├── generate_case_study.py
│   │   │   ├── generate_graph_vis.py
│   │   │   ├── generate_protocol.py
│   │   │   ├── generate_puml.py
│   │   │   ├── generate_skill_index.py
│   │   │   ├── generate_tag_index.py
│   │   │   ├── git_commit.py
│   │   │   ├── graph_audit.py
│   │   │   ├── harvest_check.py
│   │   │   ├── index_graphrag.py
│   │   │   ├── ingest_profile.py
│   │   │   ├── link_builder.py
│   │   │   ├── memory_integrity.py
│   │   │   ├── metadata_extractor.py
│   │   │   ├── mu_graphrag_bridge.py
│   │   │   ├── orphan_detector.py
│   │   │   ├── plot_business_curves.py
│   │   │   ├── pre_commit_check.py
│   │   │   ├── protocol_compliance.py
│   │   │   ├── protocol_entropy.py
│   │   │   ├── protocol_scaffold.py
│   │   │   ├── query_codex.py
│   │   │   ├── query_graphrag.py
│   │   │   ├── quicksave.py
│   │   │   ├── refactor.py
│   │   │   ├── repair_links.py
│   │   │   ├── reranker.py
│   │   │   ├── research_agent.py
│   │   │   ├── response_wrapper.py
│   │   │   ├── resume_session.py
│   │   │   ├── run_tests.py
│   │   │   ├── sanitize_for_export.py
│   │   │   ├── search_web.py
│   │   │   ├── setup_bankai.sh
│   │   │   ├── setup_calendar_auth.py
│   │   │   ├── setup_graphrag.py
│   │   │   ├── shutdown.py
│   │   │   ├── skill_gap_detector.py
│   │   │   ├── slurp_url.py
│   │   │   ├── smart_search.py
│   │   │   ├── stale_detector.py
│   │   │   ├── structure_map.py
│   │   │   ├── suggest_protocols.py
│   │   │   ├── supabase_schema.sql
│   │   │   ├── supabase_schema_expansion.sql
│   │   │   ├── supabase_schema_protocols.sql
│   │   │   ├── supabase_search.py
│   │   │   ├── supabase_search_functions.sql
│   │   │   ├── supabase_setup.py
│   │   │   ├── supabase_sync.py
│   │   │   ├── sync_to_public.py
│   │   │   ├── telegram_bot.py
│   │   │   ├── test_memori.py
│   │   │   ├── test_scripts.py
│   │   │   ├── test_supabase.py
│   │   │   ├── token_budget.py
│   │   │   ├── transcribe_audio.py
│   │   │   ├── transcribe_video.py
│   │   │   ├── update_prime_hash.py
│   │   │   ├── upload_to_supabase.py
│   │   │   ├── verify_analyst.py
│   │   │   ├── verify_ingestion.py
│   │   │   ├── visualize_graph.py
│   │   │   └── watchdog.py
│   │   ├── templates/
│   │   │   ├── SKILL_INDEX_template.md
│   │   │   ├── TASK_LOG_template.md
│   │   │   ├── case_study_template.md
│   │   │   ├── core_identity_template.md
│   │   │   ├── operating_principles_template.md
│   │   │   ├── protocol_template.md
│   │   │   └── session_log_template.md
│   │   └── workflows/
│   │       ├── audit-code.md
│   │       ├── audit.md
│   │       ├── brief.md
│   │       ├── circuit.md
│   │       ├── deploy.md
│   │       ├── diagnose.md
│   │       ├── due-diligence.md
│   │       ├── dump.md
│   │       ├── easy.md
│   │       ├── end.md
│   │       ├── guide.md
│   │       ├── needful.md
│   │       ├── primer.md
│   │       ├── refactor.md
│   │       ├── reindex.md
│   │       ├── research.md
│   │       ├── resume.md
│   │       ├── save.md
│   │       ├── search.md
│   │       ├── semantic.md
│   │       ├── start.md
│   │       ├── steal.md
│   │       ├── think.md
│   │       ├── ultrathink.md
│   │       └── vibe.md
│   └── site/
│       ├── 404.html
│       ├── about.html
│       ├── contact.html
│       ├── framework.html
│       ├── index.html
│       └── writing.html
├── Athena-Public.wiki/
│   ├── Architecture-Overview.md
│   ├── FAQ.md
│   ├── Getting-Started.md
│   ├── Home.md
│   ├── Workflow-Reference.md
│   └── _Sidebar.md
├── DEAD_MAN_SWITCH.md
├── Digital Marketing Business/
│   ├── 11.8 Company Deck_070525.pdf
│   ├── DMA Credential Deck.pptx.pdf
│   ├── Jbstudio Website Brochure.pdf
│   ├── SEO - Q2 2024 APAC - $300 OFF for Winston.pdf
│   ├── WhatsApp Image 2025-05-21 at 13.16.00.jpeg
│   └── WhatsApp Image 2025-05-21 at 13.17.01.jpeg
├── README.md
├── TECH_DEBT.md
├── Winston/
│   ├── documents/
│   │   ├── doc_2020-03-01_1764kb.pdf
│   │   ├── doc_2020-03-07_1076kb.pdf
│   │   ├── doc_2020-03-08_165kb.pdf
│   │   ├── doc_2020-03-10_3720kb.pdf
│   │   ├── doc_2020-03-12a_502kb.pdf
│   │   ├── doc_2020-03-12b_430kb.pdf
│   │   ├── doc_2020-03-13a_1811kb.pdf
│   │   ├── doc_2020-03-13b_526kb.pdf
│   │   ├── doc_2020-03-14_1514kb.pdf
│   │   ├── doc_2020-04-12_1519kb.pdf
│   │   └── profile_photo_2019.jpeg
│   ├── linkedin/
│   │   ├── assets/
│   │   │   └── cover_image.jpeg
│   │   └── current_snapshot.md
│   ├── private/
│   │   └── github-recovery-codes.txt
│   ├── profile/
│   │   ├── Archetype_The_Ballast.md
│   │   ├── Athena_Profile.md
│   │   ├── Business_Frameworks.md
│   │   ├── Constraints_Master.md
│   │   ├── System_Principles.md
│   │   ├── Psychology_L1L5.md
│   │   ├── Session_Observations.md
│   │   ├── Target_Profile_Daryl_Cheng.md
│   │   ├── User_Profile_Core.md
│   │   ├── Voice_DNA.md
│   │   └── athena_avatar.svg
│   ├── psychology/
│   │   ├── escalation_ladder_framework.md
│   │   ├── hypothetical_observer_scenario.md
│   │   ├── integration_protocol.md
│   │   ├── result.json
│   │   ├── scenario_processing_framework.md
│   │   └── t1_t2_engagement_protocol.md
│   └── strategies/
│       └── Strategy_SEO_Keywords.md
├── docs/
│   └── audit/
│       ├── DATA_GOVERNANCE.md
│       ├── DECISION_LOG.md
│       ├── PRE_MORTEM_ARCHIVE.md
│       ├── RISK_REGISTER.md
│       ├── SUCCESSION_PROTOCOL.md
│       └── SYSTEM_PRIMER.md
├── output.txt
├── output_fixed.txt
├── pyproject.toml
├── result.json
├── safe_boot.sh
├── src/
│   └── athena/
│       ├── __init__.py
│       └── core/
│           └── __init__.py
└── supabase/
    ├── .gitignore
    ├── config.toml
    ├── functions/
    │   └── sync-athena/
    │       ├── deno.json
    │       └── index.ts
    └── migrations/
        └── 003_full_workspace_sync.sql
```
[AUTO_GENERATED_MAP_END]

## Related Protocols
- [CS044: ILP Trust Arbitrage](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS044_ILP_Trust_Arbitrage.md)

- [CS044: ILP Trust Arbitrage](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS-044-ilp-trust-arbitrage.md)
