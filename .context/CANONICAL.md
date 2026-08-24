---
{created: '2025-12-27', last_updated: '2026-03-19'}
last_updated: 2026-07-22
---

# Canonical Memory (Materialized View)

> **Protocol**: **Protocol 215**  
> **Purpose**: Single Source of Truth for active facts. Supersedes conflicting info in Session Logs.  
> **Last Updated**: 22 July 2026 (v9.5.6)

---

## 1. System Metrics (Financial & Operational)

| Metric | Value | Basis | Verified |
| :--- | :--- | :--- | :--- |
| **Weighted Avg Session Cost** | **< $1** | Opus w/ Cache Hit Optimization | Session 18 |
| **Subscription Cost** | **$20/month** | Antigravity Flat Rate | Persistent |
| **Arbitrage Multiplier** | **~15x-45x** | Value Extracted ÷ Cost | Session 18 |
| **Total Sessions (All Time)** | **1,100+** | Phase 1 Complete (v9.2.3) | Session 07 (Feb 22) |
| **Total Case Studies** | **401** | .context/memories/case_studies/ | Session 09 (Feb 23) |
| **Total Protocols** | **148+** | examples/protocols/ (15 categories) | Session (Mar 19) |
| **Total Scripts** | **226** | .agent/scripts/*.py | Session 06 (Feb 23) |
| **Supabase Embedded Docs** | **851+** | Vector DB count (Exact Search/JSONB) | Session 08 |
| **Estimated Sync Rate** | **~85%** | User<>AI alignment | Case Study |
| **Consulting Rate** | **[PERSONAL]** | Market validation | Session 2026-01-28 |
| **PLC Cost Basis** | **[PERSONAL]** | DIWY Model (50% of Market) | Session 2026-01-27 |
| **Geo-Arbitrage TCO** | **[REDACTED]** | Multi-destination cost optimization | Session 04 (Feb 09) |
| **Portfolio Traffic** | **~3% Conversion** | 3 CTA clicks / 97 sessions | Session 2026-02-11 |
| **FX Strategy (RETO)** | **Trimodal** | Engineered Outcomes (Loss/Income/Jackpot) | Session 01 (Feb 15) |
| **Sovereign Stack** | **Hetzner + Cloudflare + Scrapling** | Protocol 106 + 052 (Full Stealth) | Session 04 (Feb 14) |
| **Exocortex Index** | **6.16M Articles (6.1GB)** | SQLite FTS5 (Fused w/ Main Search) | Session 08 (Feb 15) |
| **Metabolism** | **Active (Nocturnal + DSPy)** | 4AM Auto-Consolidation + Self-Tuning Prompts | Session 17 (Feb 15) |
| **Compute Arbitrage** | **~15x+ value** | Flat-rate subscription vs API pricing dislocation | Session 01 (Mar 01) |

---

## 1.1 Success Ledger (Outcome Metrics)

> **Philosophy**: Measure Leverage, not just Activity. (Protocol 245)

| Metric | Current Value | Target | Definition |
| :--- | :--- | :--- | :--- |
| **Context Injection Cost** | **~4k tokens** | <5k | Robust Boot (Identity+Mission+State) |
| **Boot Velocity** | **~30s** | <30s | Time from `/start` to Ready |
| **Insight Capture Rate** | **100% (Auto)** | 100% | Sessions with automated extraction |
| **Recall Ratio** | **~45%** | >50% | Retrieval vs Re-generation (Cognitive Offload) |
| **Cumulative Time Saved** | **~41 hrs** | ∞ | 496 sessions * 5 min saved/session |
| **Viral Verification** | **1M+ Reach (#1/#2)** | Top 5 | Athena Public Launch (Feb 2026) |
| **GitHub Conversion** | **~21.1%** | >15% | 964 unique cloners / 4,570 unique visitors (Feb 22) |
| **Positioning** | **Linux OS for Agents** | N/A | Validated via Reddit (1M+ views) & Session 14 |
| **Context Density** | **7K Signal > 15K Noise** | N/A | Protocol 321: Dense Boot + Hybrid RAG (Session 03) |

---

## 2. Core Laws (Immutable)

| Law | Statement | Enforcement |
| :--- | :--- | :--- |
| **#0** | Subjective Utility Supreme | Respect user's utility function unless it triggers #1 |
| **#1** | No Irreversible Ruin | >5% probability of ruin = Hard Veto |
| **#2** | Strategic Disadvantage Ratio (SDR) | SDR >5:1 = Exit the game, don't fight harder |
| **#3** | Actions > Words | Revealed Preference trumps stated preference |
| **#4** | Modular Architecture | New capability = new protocol file, not monolith expansion |
| **#5** | Epistemic Rigor | No orphan statistics; cite sources or mark "internal estimate" |
| **#6** | Risk-Proportional Triple-Lock | SNIPER (exempt) / STANDARD / ULTRA (robustness bias) |
| **#7** | Doom Loop Circuit Breaker | Same tool call 3x with identical args = Exit | governance.py |
| **#8** | Granular Rule Precedence | Tool-specific glob rules > General permissions | permissions.py |

---

## 3. Active Decisions (Architectural)

| Decision | Choice | Rationale |
| :--- | :--- | :--- |
| **Memory Pattern** | Memory Bank (Active) | `.context/memory_bank/` unified structure (Session 03) |
| **Content Architecture** | Astro Collections | Move from .astro pages to src/content/ (Session 2026-01-17) |
| **Deep Research Pivot** | Sherpa Curriculum (Consultancy) | Rejected "Scrappy" Micro-SaaS (VEP Bot) for High-Status "Sovereign Brain" Education. (Session 15) |
| **Vector DB** | Supabase (pgvector v0.4) | Cloud-native. Exact Search used due to dim limits. |
| **Embeddings** | gemini-embedding-001 | Optimized for Gemini |
| **LLM (Primary)** | Gemini 3.1 Pro (Antigravity) | Long context, native reasoning |
| **LLM (Coding)** | Claude Opus 4.7 | SOTA for code at mid-tier pricing |
| **Static Hosting** | Cloudflare Pages | $0, global CDN, no server management |
| **Blog Standards** | Content Publication Standard (Gold Standard) | Soulful Blogging (3-Sentence Rule, Hidden Gems) |
| **URL Structure** | Trailing Slash Enforced | `trailingSlash: 'always'` to match Cloudflare Pages behavior (Session 11) |
| **UX Standards** | Protocol 221 (Premium UX) | Breathability Physics (8-10vh padding, scale hover) |
| **Search Hierarchy** | CANONICAL > TAG_INDEX (Shards) > Sessions | Prevents stale data retrieval |
| **Delta Sync** | Hash-Based (xxhash) | Optimizes `supabase_sync.py` by skipping unchanged files (Session 2026-02-09) |
| **Semantic Search** | Hybrid RAG (FlashRank + Kinetic) | Architecture Flip: Storage -> Compute (Session 16) |
| **Signature Feature** | Sherpa Curriculum (Consultancy) | The moat: "Sovereign Brain" Installation vs "Rent-Seeking" SaaS |
| **Deep Think Sim** | Protocol 38 (Prompt-Only) | Pseudo-depth via structure avoids 100x compute cost (Good Enough architecture) |
| **Search Architecture** | Tiered (Reflex <200ms + Hybrid) | Blends mdfind (System) + Vector (Semantic) + Graph (Relational) |
| **Vector DB Schema** | Metadata JSONB Added | Fixes semantic search RPC errors (Verified Session 03) |
| **GraphRAG Model** | gemini-flash-lite-latest | Optimized for high-throughput entity extraction (Free Tier compatible) |
| **LLM (Local/Ollama)** | qwen3:4b | Best 4B model for 8GB RAM constraint; thinking mode + tool use |
| **Caching Layer** | Multi-Tiered (LRU + Prefetch + Segments) | Automated hot-file prefetch & protocol rule extraction for boot speed |
| **Backlink Strategy** | Sovereign Link Network | Hub (Portfolio) <-> Spokes (Assets) virtuous cycle (Session 2026-01-26) |
| **Legal Architecture** | The Willy Clause | Explicit liability shield for client execution failure (Session 08) |
| **V4 Integration** | Autonomic Mode (Quad-Lock) | "Magic" > Manual. Automated Scaffolding & Secret Scanning (Session 13) |
| **Bilingual Cognition** | Dual-Boot Architecture | English (Logic) + Chinese (Context) to maximize semantic density (Session 20) |
| **Business Model** | Sherpa Service (Consultancy) | Selling "Sovereign Brain" Installation & Education > "Software" (Session 15) |
| **Stop Pattern** | **Protocol 112** | Explicit negative constraints for safety (Claude Mastery Steal) |
| **Public Sync Guard** | Blacklist Mode + Hard Exclusion | `sync_to_public.py` excludes `case_studies` to prevent IP leak. (Session 11) |
| **Dependency Hygiene** | Minimalist (No Unused) | Removed `dspy-ai` to fix `diskcache` vuln. Attack surface reduction. (Session 11) |
| **Efficiency Wins** | Robust Macro + Efficiency Micro | **Reflex Search** (<200ms) + **Sniper Mode** (Risk-Based Compute) |
| **Pricing Strategy** | Tiered (Setup / Coach / Enterprise) | High-Ticket Setup & Integration (Session 12) |
| **Autonomy Level** | Metabolic Organism | System sleeps (consolidates) and evolves (optimizes) without user input. |
| **Hybrid Truth** | HITL Bridge (Manual Gemini) | **ZERO COST** Implementation. Replaced automated API with User-Bridge (Session 20) |
| **Skill Metabolism** | 3-Layer Architecture (Zeude) | Sensing (Telemetry) + Delivery (Hot-Reload) + Guidance (Nudge) adapted from Zeude for local-first sharpness. (Session 06) |
| **Skill Routing** | Semantic Skill Routing (JIT) | Replaced 4.5k token static index with dynamic targeted vector search to respect the 20k cap limit. (Session 07) |
| **Model Routing** | Flash / Pro / Opus | Flash (Boot/End), Pro (Chat), Opus (Coding) for optimized cost/depth. (Session 11) |
| **Subscription Profit** | Flat-rate = ~15x API Value | Cached reads in Subscription are 0.0x cost. Standard API is 0.1x. Subsidy cliff creates actual dollar profit. |
| **Trading Execution** | Meso-Path (Flat Layering) | Balances Robustness vs Efficiency for high leverage environments (CS-369) |
| **Deep Reasoning** | Mandatory Script Execution | Protocol 75 must be run via `parallel_orchestrator.py` to avoid LLM simulation decay. |

---

## 4. Strategic Frameworks (Active)

| Framework | Protocol | Core Principle |
| :--- | :--- | :--- |
| **PMOD** | 162 | Problem > Market > Operations > Distribution (Distribution is hardest) |
| **Arbitrage Formula** | 65 | Find gaps where perceived value >> delivery cost |
| **Wizard of Oz** | 66 | Manual backend, automated frontend until n>100 |
| **SDR Calculator** | Law #2 | If Strategic Disadvantage Ratio >5:1, exit arena |
| **Cross-Model Validation** | 171 | High-stakes claims must be checked by alternate LLM |
| **Pareto Frontier** | 49 | Robustness > Efficiency except when low-stakes AND recoverable |
| **Unit Economics** | 230 | Profit is an "Efficiency Shield" against variance (Breakeven focus) |
| **AI Trajectory** | 232 | Altman's Law: 10x cost-drop/yr (Plan Decade, Execute Week) |
| **Info Asymmetry** | Landa/Inside Man | Meta-knowledge dominance: "I know X, you don't know I know X" = Leverage |
| **Resonance Spec** | 260 | Content Metric: Describe symptom so well they say "That's Me" (Λ > 0) |
| **Optimization Lens** | CS-182 | Inverse Inquiry: "Don't ask Why (Moral), Ask What (Incentive)" |
| **Tribe vs Cohort** | CS-196 | Shared Struggle > Shared Consumption (Avoid the "Mall Walker") |
| **Trimodal Distribution** | Session 01 (Feb 15) | Engineer outcomes into 3 buckets (Punishment, Income, Jackpot) to defeat random variance. |
| **Risk Pareto Rule** | Protocol 050 | 80/20 Capital Allocation: 80% Robust (Low R), 20% Efficient (High R). |
| **MCDA Efficiency Rank** | Session 19 | Day Trading Priority: Spread Cost is King. Rank by cost efficiency. Exotics = Ruin. |
| **Relationship Dollar** | CS-197 | Kindness ≠ Currency. "Vending Machine" model leads to ruin. |
| **Mismatch Radar** | 262 | Detect reciprocity gaps early via 3 axes: Initiation, Bandwidth, Depth |
| **Skeptic Gate** | 261 | Antecedents-First, 3 Hypotheses, Least-Regret Move (breaks validation spirals) |
| **Trilateral Feedback** | session-16 | User (Intuition) + AI (Model) + Red Team (Audit) > Bilateral (Mutual Blindness Risk) |
| **SFA/CDSA Physics** | CS-198 | Financial Crime Floor = 5 Years (Double Tap charges) |
| **Validation vs Authority** | 309 | Validation = Single LP (10-20%); Authority = Multi-Page (80-90%) |
| **Clinkz Doctrine** | Session 12 | Identity-First Positioning; AI Agents > Human Team (Cost Arbitrage) |
| **WaaS Paradox** | CS-338 | Zone A (Profitable/Simple) vs Zone B (Unprofitable/Complex Apps) cliff |
| **XYZ Pricing** | CS-342 | Risk Distribution: Base (X) + Output (Y) + Outcome (Z) > Retainer |
| **Proof-First** | CS-345 | Content (Proof) precedes Ads (Traffic); Naked Ads = Burned Cash |
| **Macro-Viral** | Dear Modern | Mass Entertainment -> Long Trust -> Product (3.5M Followers) |
| **Micro-Trust** | A1 Physics | Targeted Proof ("F9->A2") -> Direct Whatsapp -> High Ticket (1k Followers) |
| **Pure Pull** | 316 | Focus on high-urgency/crisis niches (GBP/Amazon) + Mandatory infrastructure (Medical) |
| **Human-in-the-Loop** | 316 | Arbitrage exists only where generic AI output is insufficient (JSON-LD, Compliance) |
| **Kill Switch** | CS-340 | Asset Control (Hosting/Domain) is the only enforcement for Retainers |
| **Variance Tax** | Law #3 | Volatility is a subtraction term. Paid in Stops (Efficient) or Margin (Robust). (Session 02) |
| **Efficiency vs Robustness** | Trade-off Matrix | Efficient = High ROI / Low Survival. Robust = Low ROI / High Survival. (Session 02) |
| **Bank Robber Paradox** | Session 9 | Clinical detachment (Filter > Sales) = Ultimate Kindness. Passion vs Economics. |
| **Ghost Protocol** | Session 01 | Privacy is the Product. High-SES clients buy Immunity, not Competence. |
| **Selection > Conversion** | CS-373 | Situationship Fallacy: Use price/positioning to sort, not sell. Don't manufacture attraction. |
| **Validate > Capitalize** | CS-372 | CapEx/OpEx Trap: Low CapEx + Low OpEx + Fast Validation = Anti-Ruin. |
| **One Page Wonder** | CS-375 | SEO Bridge: Rank for high-vol info keywords (Grading System) -> Brand Exposure. |
| **3+1 Competitive Moat** | 282 | Price/Effectiveness/Efficiency + X-Factor (Hidden Benefit) = Market Entry condition. |
| **Twin Engine Protocol** | 46 | Unit A (Stable Income) + Unit B (Wealth Building) = Dual-engine financial structure. |
| **Familiarity Heuristic** | Session 2026-01-23 | Trust is borrowed. Use official assets (WhatsApp/Tele logos) to trigger "Safe" pattern recognition. |
| **Identity Consultant** | Session 2026-01-23 | "Not a Paper Mill" = High-Status Frame. Sell "Consulting", not "Ghostwriting". |
| **Drift Hazard** | CS-178 | "The Map is Not the Territory." Code evolves faster than Docs. Verify against Runtime (app.py), not Memory. |
| **Idea Meritocracy** | Protocol 140 | Believability Weighting (Ray Dalio). 3-Sigma Rule for Information Filtering. |
| **The Optionality Premium** | Session 08 | Rent Safety > Buy Leverage. Pay higher variable costs to avoid fixed-cost ruin until base volume is guaranteed. |
| **Capital Physics** | Session 01 (Jan 29) | Drawdown Budget (Cash Loss) + Margin Locked (Locked Cash) = Total Account Cash (Actual Cash). Terminology standardized for risk. |
| **The Generosity Trap** | Session 04 (Feb 09) | Low Fee + High Variance (Online) < High Fee + Low Variance (Live). Don't confuse "Cheap" with "Profitable". |
| **Depreciation Inversion** | CS-2026 | In distorted markets, "New" assets may have lower OpEx than "Used". (Car Buying Anomaly). |
| **Lateral Thinking** | Protocol 138 | **Kobayashi Maru**: If SDR > 5:1 (Rigged Game), question premises and break rules (if Law #1 safe). |
| **Wealth Psychology** | CS-2026-02-02 | The Decoupling: Protocol 404 (Fetch vs. Reason separation). |
| **Feedback Cutoff** | Law #8 | Imperviousness Ratio > 5.0 = Immediate Pivot to Service Level (No Teaching). |
| **Hope Override** | CS-012 | The tax paid for ignoring reality in favor of a simulation. Countermeasure: Reality Gate. |
| **Memory Hardening** | 2026-02-15 | Exponential Backoff + 60s Timeout to prevent 429 crashes (Session 03). |
| **Buffer Formula** | Session 09 | Volatility + 50% Margin of Safety. Calibrate stops to Noise, not Price. |
| **Pain Threshold Sizing** | Session 09 | Size = min(Technical Risk, Sleep Well Number). Psychology > Math. |
| **Sophie's Choice** | Session 07 (Feb 17) | Negative-Sum Game. Solution = Pre-Emption (Don't enter). |
| **Umbrage Trap** | CS-371 | Frame Failure (Anger). Solution = Reframe (Integrity funded by PnL). |
| **Bureaucratic Liability** | Law #27 | Authority floats (Immunity), Liability sinks (Executor). Never accept Resp without Auth. |
| **Volatility Drag** | Session 06 (Feb 18) | Growth = Edge - Variance/2. High variance imposes a "Tax" that destroys compounding. |
| **Variance Preference** | Session 06 (Feb 18) | Low Variance (Compounding) vs High Variance (Desperation/Free Roll). Match variance to survival constraint. |
| **Investor Barbell** | Session 03 (Feb 19) | Structure: 20% Active + 80% Safe Haven. Barbell allocation for structural ruin protection. |
| **GEO Alpha** | 317 | YouTube/Reddit organic threads > Website Blogs for LLM citation/visibility. (Session 12) |
| **Dual-Setup Sizing** | Session 02 (Feb 22) | Majority allocation to robust setups (wide invalidation) / minority to efficient setups (tight invalidation) |
| **AP Sizing Logic** | Session 02 (Feb 22) | Max allocation requires structural confluence signal (high-conviction tell) |
| **Kelly Constraints** | Session 02 (Feb 22) | Efficient setups (50% ATR) cap Kelly Fraction due to variance-induced lower Win Rate. |
| **Context Density** | 321 | Dense Signal (7K) > Padded Context (15K). Prioritize attention weight over raw volume. |
| **Bionic Swarm Blueprint** | Session 08 | **Backwards Induction**: Define Goal -> Map Prerequisites -> Node-Agent Assignment. |
| **Trading Hierarchy** | Session 08 | **Structure > Management > Selection**: Sizing/SL matches volatility, not budget. |
| **Marketing Swarm** | Session 08 | 16-skill modular architecture for ad extraction -> strategy -> production -> deployment. |
| **Distribution First Law** | Session 10 | Validating audience language/needs > engineering sophistication. (Moat building). |
| **The Dignity Premium** | Session 10 | The status/assurance surplus paid for human labor in B2C vs commodity AI. |
| **Half-Kelly Criterion** | Session 10 | Optimal compounding (75% growth, 50% variance reduction) for verified systems. |
| **Boring Task Alpha** | Session 10 | Automation of 2-3 repetitive tasks >> "AI Strategy" slide decks. |
| **Structural Null Zone** | Session 03 (Feb 26) | In semi-stochastic domains, provide a "valid structural zone" rather than a precise number, and emphasize position sizing. |
| **Bionic Synergy Guard** | Session 03 (Feb 26) | Do not yield to user pushback if the mathematical/structural reasoning is sound. Sycophancy breaks the Bionic Unit synergy. |
| **Friction Multiplier** | Session 07 (Feb 26) | Selling the procedure (rapid scoping) > Selling the result. Decreases pushback, warrants higher anchoring. |
| **The Pryce Effect** | Session 19 (Feb 27) | In semi-stochastic domains, P(S) is an unknown distribution. Assigning MEV/EEV weights without base rates is false precision. Defer P(S) to user intuition. |
| **Operator's Trade Blueprint** | 369 | Multi-lever configuration optimized for psychological robustness. Maps EEV > MEV with tiered capital classification. (Session 19) |
| **BCG Capital Matrix** | Session 10 | Core Portfolio (majority Cash Cow) pays a Capital Premium (wide invalidation, low RR) for win-rate survivability. The high-convexity tier demands total precision and maximum density. |
| **The Full Port Barbell** | Session 10 | The high-convexity tier relies on maximum leverage at the micro-level to create asymmetric payoff sets, accepting a bounded total loss as an entry fee. |
| **EEV Reality Testing** | Session 05 (Feb 28) | Applied Economic Expected Value and Law of Ruin cross-domain beyond financial markets to evaluate non-financial commitments. |
| **Input-Conviction Principle** | Case Study (Mar 04) | Athena's conviction is directly proportional to context completeness. Incomplete context → hedged framework (Law #1). Complete context → direct operational verdict. |
| **Zero-Iteration Harness Framework** | Session S808 (Aug 24) | Human iteration is a symptom of missing mechanical verifiers. 6-pillar architecture (Harness Engineering, Context Engineering, Spec-Driven Dev, Automated Evaluation & Oracles, Tool Ergonomics, Skill Compilation). Live evaluation of system via Capability x Enforcement (C x E) probe rather than declared claims. |
| **Deterministic Output-Side Gate** | Session S808 (Aug 24) | Low-latency (<300ms) output-side verification hook executing on the Stop lifecycle event before turn delivery. Enforces LaTeX/ASCII leak detection, API credential redaction, and Python syntax validation with Claude Code blocking contract (exit code 2 + stderr feedback). |
| **Bilateral Autonomous Self-RSI** | Session S808 (Aug 24) | Overnight autonomous diagnostics paired with daytime human gradient review (DEC-13). Guarded by Backpressure Saturation Gates (>= 3 unreviewed tickets -> hibernate), Maintenance Freeze Gates (>70% maintenance -> force revenue/delivery focus), and GTO EV scoring (EV >= 1.50). Proposes machine-checkable delta tickets with zero autonomous code mutations. |

---

## 6. Key Reference Documents

| Document | Purpose | Note |
| :--- | :--- | :--- |
| [Core_Identity.md](../.framework/v8.2-stable/modules/Core_Identity.md) | Laws, Identity, RSI | Reference |
| memory_bank/ | Active System Context | Supersedes project_state.md (Session 03) |
| **WORKFLOW_INDEX.md** | All 25+ workflows | Reference |
| **SKILL_INDEX.md** | All 215 protocols | Reference |
| **TAG_INDEX_*.md** | Sharded File discovery | Reference |

---
