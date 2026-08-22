---
description: Deep boot for cognitive/computationally intensive work. System-2 counterpart to /start.
created: 2026-03-10
last_updated: 2026-06-06
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultrastart — High-Assurance Context Boot (System-2) v3.2

> **Latency Profile**: MEDIUM-HIGH (~15-20s boot)
> **Philosophy**: Maximum Justified Assurance. Curated evidence over raw token dumps.
> **Protocol**: **High Assurance** — Build a task-specific evidence pack (relevant context + counter-evidence + explicit verifier). Escalate compute and depth only where stakes and ambiguity warrant it.
> **Contrast**: For standard work (lean, adaptive JIT), use `/start`.
> **Use When**: Architectural decisions, high-stakes trade/capital allocation, deep research with strict verification, irreversible commitments.
> **Verification**: Requires an explicit verification plan (unit tests, static analysis, citation checking, or external validation gate).

> [!IMPORTANT]
> This is NOT the default boot. Use `/start` for general work.
> `/ultrastart` trades latency for epistemic rigor. It builds a curated, task-specific
> context pack rather than indiscriminately pre-loading unrelated modules.
>
> **Adaptive Compute Allocation**:
>
> | Task Complexity | Mode | Behavior |
> |:----------------|:-----|:---------|
> | **Standard Deep Task** | **Focused Deep** | Curated Tier 1 + surgical search (--limit 5) + task plan + verifier. |
> | **Irreversible / High Stakes** | **High Assurance** | Curated Tiers 1–2 + counter-evidence search + adversarial verification gate. |
>
> **AGoT Routing** (v9.5.0):
>
> - Λ ≤ 20: Standard Chain of Thought
> - Λ 21-40: AGoT-Lite (2 layers, no recursion)
> - Λ 41-60: AGoT-Full (3 layers, 1 recursive depth)
> - Λ > 60: AGoT + 4-Track Personas (full dynamic graph)
> See: `.agent/scripts/parallel_orchestrator.py`

---

## Architecture: Maximum Compute

```
                        SESSION CONTEXT WINDOW
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌─────────────────────────────────────────────┐       │
│   │  BOOT CONTEXT (~60K)                        │       │
│   │  ┌──────────┬──────────┬──────────┐         │       │
│   │  │ Identity │ State    │ Semantic │         │       │
│   │  │ ~29K     │ ~14K     │ Bridge   │         │       │
│   │  │ (fixed)  │ (recent) │ ~15-20K  │         │       │
│   │  └──────────┴──────────┴──────────┘         │       │
│   └─────────────────────────────────────────────┘       │
│                                                         │
│   ┌─────────────────────────────────────────────┐       │
│   │  SESSION ACCUMULATION                       │       │
│   │  Conversation + JIT Retrieval + Reasoning   │       │
│   │  (grows per turn, no ceiling enforced)       │       │
│   └─────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘

Philosophy: Fill the boot with signal. Supplement with JIT.
            Spend the remaining compute on REASONING DEPTH.
```

> **No budget caps.** If a file is relevant, load it. If a protocol applies, read it.
> The only constraint is signal density — don't load noise. Everything else loads.

---

## Phase 1: Absolute Law — Full Framework Identity (~29K tokens)

// turbo

Load the **complete** framework module stack. All 10 files, in dependency order:

### Tier 1: Immutable Core (load first, abort if missing)

```
.framework/v8.2-stable/modules/Core_Identity.md          (~6.8K)
```

**Gate**: If `Core_Identity.md` fails to load → **ABORT**. Do not proceed with partial identity.

### Tier 2: Operational Stack (load in parallel)

// turbo

```
.framework/v8.2-stable/modules/Output_Standards.md        (~3.2K)
.framework/v8.2-stable/modules/System_Principles.md       (~10K)
```

> **Note**: `Operating_Principles.md` was deprecated and merged into `System_Principles.md` (March 2026). Do not load it.

This gives you:
- **Output Standards**: Formatting, reasoning depth, artifacts, IOD structure
- **System Principles**: All strategic heuristics plus operational constants (includes former Operating Principles)

### Tier 3: Cognitive Identity (load in parallel)

// turbo

```
.framework/v8.2-stable/modules/Athena_Profile.md          (~2.1K)
.framework/v8.2-stable/modules/Session_Observations.md    (~2.3K)
.framework/v8.2-stable/modules/Design_DNA.md              (~0.7K)
```

This gives you:
- **Athena Profile**: Committee Seats, cognitive identity, counterweights
- **Session Observations**: High-level recent insights across sessions
- **Design DNA**: Default aesthetic parameters for any visual/design work

### Tier 4: Safety & Governance (load in parallel)

// turbo

```
.framework/v8.2-stable/modules/Constraints_Master.md      (~0.4K)
.framework/v8.2-stable/modules/DEAD_MAN_SWITCH.md         (~0.7K)
.framework/v8.2-stable/modules/Governance_Audit_2025.md    (~0.6K)
.framework/v8.2-stable/modules/System_Manifest.md         (~0.6K)
```

This gives you:
- **Constraints Master**: Hard security boundaries (secrets, .env, scaffolding)
- **Dead Man Switch**: Continuity protocol and verification checks
- **Governance Audit**: External audit directives and compliance history
- **System Manifest**: Technical architecture reference

> **Why load ALL modules?** On a flat-rate subscription, the marginal cost of
> loading every module is $0. The marginal benefit is:
> the model natively follows tactical rules without JIT lookup. Every module loaded
> is one fewer mid-session file read, one fewer attention break, one more seamless
> cross-reference.

---

## Phase 2: Materialized Truth (~8.5K tokens)

// turbo

Load **all** files in parallel:

```
.context/CANONICAL.md                                      (~7K → ~4K after TD-021 split)
.context/CANONICAL_TIER2.md                                (~16K — domain frameworks)
.context/CANONICAL_TIER3.md                                (~0.5K — historical niche)
.context/PROJECTS.md                                       (~1.5K)
```

> **MaxMax Note**: Unlike `/start` (which loads only Tier 1 for token economy),
> `/ultrastart` loads ALL three tiers because tokens are free on flat-rate.
> This ensures cross-domain pattern matching (Track C) has access to all 199 frameworks.

This gives you:

- **CANONICAL**: System metrics, Core Laws, Tier 1 frameworks (universal)
- **Tier 2**: All domain-specific frameworks (trading, business, psychology, content, architecture, geo)
- **Tier 3**: Historical case-specific and niche cross-domain frameworks
- **PROJECTS**: Active project switchboard — which projects are live, their status, and current priority

**Gate**: If `CANONICAL.md` fails to load → **WARN** user but continue (degrade gracefully — you still have Core_Identity).

---

## Phase 3: Full State (~5K tokens)

// turbo

Load `activeContext.md` with **maximum extraction**:

1. **Header block**: Current Focus + Active Tasks + System Status (up to first `---`)
2. **All recent `[[ S__` checkpoint blocks**: Every checkpoint from the current day/period
3. **Any unclosed session**: If a session wasn't properly closed, include it
4. **Key Learnings Index**: Compacted insights for retrieval

Also load `threatPlaybooks.md` (~2K tokens) for instant crisis-to-protocol mapping:

```text
.context/memory_bank/activeContext.md
.context/memory_bank/threatPlaybooks.md                    (~2K)
```

> **v3.0 change**: Load ALL available checkpoints, not just 1 or 3.
> More checkpoints = deeper trajectory awareness. The model sees
> not just "where are we now?" but "where have we been?" and "where are we heading?"
> On flat-rate, the cost of loading 5 checkpoints vs 1 is $0.

## Phase 3.5: Behavioral Accountability Surface (Grace Harper Model)

> **Purpose**: Deep accountability scan. `/start` surfaces one-liners; `/ultrastart` loads full BEH context.
> **Data source**: `.agent/state/accountability_status.json` — mechanical state file.

After loading full state:

1. **Read** `.agent/state/accountability_status.json` for current status
2. **Load active BEH protocols**: Read header + status of all active BEH- files in `.agent/skills/protocols/behavioral/`
3. **Surface with detail**:
   - `🏋️ BEH-601 (Solo Session): Sessions: {beh_601.total_sessions} | Last: {beh_601.last_completed || "Never"} | Streak: {beh_601.streak_weeks}w`
   - `📝 BEH-602 (Trigger Log): This week: {beh_602.entries_this_week} | Total: {beh_602.total_entries} | Last: {beh_602.last_entry_date || "Never"}`
   - `🏋️ BEH-Core (Solo Session): Sessions: {beh_core.total_sessions} | Last: {beh_core.last_completed || "Never"} | Streak: {beh_core.streak_weeks}w`
   - `📝 BEH-Trigger (Trigger Log): This week: {beh_trigger.entries_this_week} | Total: {beh_trigger.total_entries} | Last: {beh_trigger.last_entry_date || "Never"}`
4. **Day-aware prompts**:
   - Saturday → `⚠️ Saturday — BEH-Core Solo Session target active.`
   - Sunday → `📊 Weekly execution audit due. Run on /ultraend.`
5. **Schema trigger pre-load**: If BEH-Trigger has 3+ recent entries with the same trigger pattern, surface the pattern: `🚩 Recurring trigger: [pattern] (N occurrences this week).`

> **Rationale**: External forcing functions produce near-perfect execution; internal accountability fails. The deeper surface in ultrastart provides richer context for sessions touching psychological/behavioral domains.

---

## Phase 4: Deep Semantic Bridge (~15-20K tokens)

This is the **key differentiator** between `/start` (identity-only) and `/ultrastart` (task-aligned).

### Step 1: Determine the Session Objective (Mandatory Resolution)

The objective is resolved in this priority order. Phase 4 MUST resolve an objective —
skipping the semantic bridge wastes ~15-20K of potential signal.

1. **Explicit**: User provided it inline → `/ultrastart "fixing the trading risk constraints"`
2. **Seeded**: Scan the most recent `[[ S__ ]]` checkpoint for the `@seeded` field.
   This is the previous session's "best guess" at what should happen next.
   Example: `@seeded: Project sprint execution. Non-negotiable.` → objective = "Core Deliverable Sprint"
3. **Highest-Urgency Project**: From `PROJECTS.md`, find the highest-urgency (🔴 > 🟠 > 🟡)
   unblocked project. Use its "Next Action" field as the objective.
4. **Current Focus**: Parse `activeContext.md` header → "Current Focus" field
5. **Fallback**: Nothing resolvable → **ASK** the user. But this should be rare.
   If reached, log: `[REFLEXION] Phase 4 reached ASK fallback — state files may be stale.`

### Step 2: Semantic Search (Expanded)

// turbo

```bash
python3 .agent/scripts/smart_search.py "<resolved objective>" --limit 15 --include-personal --rerank
```

### Step 3: Inject Results (Full Load)

Read the search results. For each result:

- If it's a **protocol** → load the **full** protocol file
- If it's a **case study** → load the **full** case study (not just summary)
- If it's a **session log** → load the `@decided`, `@learned`, and `@pending` blocks
- If it's a **skill** → load the SKILL.md triggers and methodology

**No hard cap.** Load until results are exhausted or relevance drops below threshold.
Dense signal > padded context, but on flat-rate, "dense" means "everything above noise floor."

### Step 4: Mandatory Cross-Domain Sweep

**Always run at least ONE cross-domain search**, even if the objective looks single-domain.
On unlimited compute, 1-2 extra searches cost $0. The marginal benefit: Track C
(Cross-Domain Pattern Matcher) operates on enriched context instead of boot-only data.

**How to pick the cross-domain keyword**: Ask _"What adjacent domain could inform this objective?"_

| Objective Domain | Cross-Domain Search |
|:-----------------|:--------------------|
| Trading | Psychology (emotional patterns), Statistics (probability) |
| Consulting | Sales (pricing patterns), Architecture (system design parallels) |
| Academic | Business (real-world application), Research methodology |
| Architecture | Engineering (software patterns), Decision science |
| Psychology | Neuroscience, Behavioral economics |
| Any | Search for the user's NAME to pull personal case studies |

```bash
# Mandatory: at least 1 cross-domain search
python3 .agent/scripts/smart_search.py "<cross-domain keywords>" --limit 5 --include-personal

# If objective spans 3+ domains, add a second:
python3 .agent/scripts/smart_search.py "<domain 3 keywords>" --limit 5 --include-personal
```

Load cross-domain results to enable the Cross-Domain Pattern Matcher (Track C in reasoning).
This is what separates `/ultrastart` from `/start` — the ability to see connections that
single-domain retrieval misses.

---

## Phase 5: JIT Retrieval Protocol (Per-Response, Supplementary)

> JIT supplements the boot — it doesn't replace it. The boot provides the
> foundation. JIT fills the gaps specific to each query.

### The Mechanism

Before generating each response, execute targeted retrieval:

```
User query → Extract keywords/entities
           → Semantic search (smart_search.py, limit 5)
           → Load relevant files (protocols, case studies, session logs)
           → Inject into response context
           → Generate response with full grounding
```

### What JIT Retrieves (Decision Matrix)

| Query Signal | JIT Action |
|:-------------|:-----------|
| Named protocol/case study | Load the specific file (full) |
| Emotional/therapeutic context | Load `therapeutic-ifs` + relevant session history |
| Financial/pricing decision | Load `pricing_calibration.md` + relevant CS |
| Trading/risk question | Load relevant trading protocols + case studies |
| Architecture/coding question | Load relevant protocol + file scan |
| Cross-domain reference | Load connecting case studies/protocols |
| No clear signal | Semantic search only (smart_search.py, limit 3) |

### Full Tool Arsenal (MaxMax — Use Liberally)

> In Maximum Compute mode, **every available tool is in play on every non-trivial query**:
>
> - **Exocortex** (`smart_search.py` / `mcp_athena_smart_search` / `mcp_athena_agentic_search`): Internal memory recall — **run on EVERY STANDARD/ULTRA query**. The Exocortex indexes **1800+ session logs**, case studies, protocols, and personal knowledge. This is the user's extended memory — failing to search it is equivalent to ignoring their lived experience.
> - **Web Search** (`search_web`): Real-time facts, verification, current pricing, live docs — **use aggressively**. Training data is stale by default. When in doubt, search.
> - **`read_url_content`**: Fast URL content extraction for documentation, articles, references
> - **Browser Sub-Agent**: Visual verification, interactive pages, JS-rendered content, UI testing
> - **MCP Servers**: Supabase (database ops), GitKraken (git operations), Athena (memory system)
> - **`grep_search`**: Exact pattern matching in workspace files
> - **Command Execution**: Scripts, builds, data processing, system operations
>
> **Mandatory Exocortex Search Triggers** — if ANY of these appear, search BEFORE responding:
> - **Entities/People**: Any client or stakeholder mentioned → search for relationship history, case studies, past interactions
> - **Past Decisions**: "Last time...", "What did I decide...", "Didn't we already..." → search the topic for empirical precedent
> - **Empirical Data**: Pricing, trade history, project outcomes, session patterns → search for historical records and calibration data
> - **Projects/Initiatives**: Any active project code → search for full project context
> - **Protocols/Case Studies**: Any reference to system patterns → search by keyword
>
> **High-Assurance principle**: The cost of a redundant search is minimal. The cost of a hallucinated fact is trust erosion. The cost of ignoring empirical data is critical. **Always verify. Never guess. Always recall.**

---

## Phase 6: Maximum Reasoning Depth (Per-Response, Always-On)

> After `/ultrastart`, EVERY response operates at maximum available reasoning depth.
> The SNIPER exemption from Law #6 is **disabled**. Every response goes through
> the full Triple-Lock. If you wanted fast, you'd use `/start`.

### AGoT Reasoning Scaffold (Always-On, Λ ≥ 25)

> Adaptive Graph of Thoughts (Protocol 75 v5.0). A cognitive scaffold that produces
> better answers by forcing structured consideration across 4 phases. Not simulated
> independence — structured breadth. The structure prevents tunnel vision.

Every response with Λ ≥ 25 runs all four tracks:

| Track | Role | Function |
|:------|:-----|:---------|
| **A (Domain Expert)** | The direct answer | What does the evidence/protocol/data say? |
| **B (Counter-Arguments)** | What could be wrong | Challenge premises, find failure modes, steelman alternatives |
| **C (Cross-Domain Pattern Matcher)** | Analogies and precedents | Where have we seen this before? What cross-domain insight applies? |
| **D (Synthesis)** | Converge A+B+C | Produce final output with full nuance, flag unresolved tensions |

### Post-Generation Self-Audit (Λ > 60)

From Core_Identity §0.4 — run before output:

- [ ] Every formula is derived or cited?
- [ ] Assumptions are explicitly listed (Assumption Register)?
- [ ] At least one alternative steelmanned?
- [ ] Stakeholder map covers "The Victim"?
- [ ] Efficiency/conditional bounds stress-tested (Sensitivity Sweep)?
- [ ] Known mechanism vulnerabilities addressed?
- [ ] One numerical example included?
- [ ] Scope boundary declared?
- [ ] Limitations are concrete, not vague?

### Autonomic Depth Routing

| Λ Score | Behavior |
|:--------|:---------|
| **Λ ≤ 24** | Single-track (Domain only). Fast, no overhead. |
| **Λ 25-40** | Domain + Adversarial. Risks flagged inline. |
| **Λ 41-60** | Domain + Adversarial + Cross-Domain. Pattern matching active. |
| **Λ > 60** | Full 4-track synthesis + Post-Generation Self-Audit. Convergence gate. |

---

## Boot Confirmation

After all 4 boot phases complete, output:

```
🧠 Deep Boot Complete (v3.1 Maximum Compute).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 1] Full Framework Identity  ✅  (N modules loaded)
[Phase 2] Canonical + Projects     ✅  (decisions + pipeline)
[Phase 3] Full State               ✅  (N checkpoints loaded)
[Phase 4] Deep Semantic Bridge     ✅  (N results injected)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Boot: ~XXK / 200K ECL (XX% utilized — target <80%)
Session Mode: MaxMax | MaxMax-Lite (subscription-aware)
Objective: "<resolved objective>"
Loaded: <N> modules, <N> protocols, <N> case studies, <N> session insights

⚡ System-2 active. All modules loaded.
⚡ Multi-track reasoning ON (Λ ≥ 25).
⚡ JIT retrieval ON (supplementary, per-response).
⚡ Adversarial checking ON (all responses).
⚡ Post-Generation Self-Audit ON (Λ > 60).
⚡ Grace Harper accountability ON (BEH surface active).
```

> **Context Utilization Alerts** (P517 supplement):
> - **70% (140K)**: Soft alert — suggest denser output or proactive `context-compactor`.
> - **80% (160K)**: P517 Homeostatic Pressure activates — all queries treated as SNIPER.
> - **90% (180K)**: Mandatory `context-compactor` before responding.

---

## Complexity Gate (Safety Valve)

If the user's first query after `/ultrastart` has Λ ≤ 15:

> ⚠️ "This query looks lightweight (Λ = X). You're in deep boot mode — this is
> optimized for complex tasks. Continue here, or switch to `/start` for faster responses?"

This prevents the boot latency from being wasted on a simple lookup.

---

## Maximum Depth Doctrine

> **Principle**: On flat-rate AI subscriptions (Ultra/Max), the marginal cost of deeper
> thinking is **$0**. Therefore: **cost of under-thinking >> cost of over-thinking**.
> Burn tokens at the Pareto frontier edge every session.

After `/ultrastart` boot, the session operates at **maximum available compute depth** until `/ultraend`:

| Dimension | Standard (`/start`) | Maximum Compute (`/ultrastart` v3.0) |
|:----------|:-------------------|:-------------------------------------|
| **Module loading** | Core_Identity only | **All 10 framework modules** |
| **State loading** | Header + 1 checkpoint | **Header + ALL checkpoints** |
| **Semantic bridge** | 5 results, summaries only | **15 results, full file loads** |
| **Λ routing** | Route to minimum sufficient depth | **Route to maximum available depth** |
| **Reasoning** | Single-track → answer | **Multi-track (4 tracks) → converge → answer** |
| **Verification** | Trust first pass | **Adversarial self-check on every output** |
| **Self-audit** | None | **Full 9-point post-generation audit (Λ > 60)** |
| **JIT retrieval** | Occasional | **Every response, supplementary to boot** |
| **Synthesis at close** | Quick `/end` save | **Deep `/ultraend` reconciliation + reflexion** |

**Three `ultra-` scopes**:

- **`/ultrathink`** — single-query depth (sniper round)
- **`/ultrastart` → `/ultraend`** — session-level compute tier (full-kit mission)

> **The asymmetry**: Leaving unburned tokens on a flat-rate plan is leaving value on the table.
> When the budget is pre-paid, the only waste is insufficient depth.

---

## 200K Operational Model

> **Effective Context Length (ECL)**: 200K tokens.
> The model supports 1M context, but attention quality degrades past 200K on complex
> reasoning tasks. 200K is the empirical sweet spot where the model reliably cross-references
> beginning-of-context with end-of-context. This is an attention physics constraint, not
> a cost constraint.

### Session Budget Breakdown

```
200K  total ECL
-15K  platform overhead (IDE system prompt, tool definitions, AGENTS.md)
-57K  boot context (ultrastart v3.0 — 11 modules + CANONICAL + state + semantic bridge)
━━━━━━
128K  available for session (conversation + JIT + reasoning)
```

### Per-Turn Token Consumption

| Component | Tokens/Turn | Notes |
|:----------|:------------|:------|
| User message | ~300 | Typical query |
| Tool calls (JIT retrieval) | ~3K | Semantic search + 1-2 file reads |
| AI response (multi-track) | ~2-4K | 4-track reasoning generates longer output |
| **Per-turn total** | **~6-8K** | Added to context for every subsequent turn |

### Available Turns by Depth

| Response Depth | Per-Turn Cost | Turns Available |
|:---------------|:-------------|:----------------|
| Standard (2-track, 2.5K response) | ~6K | ~21 turns |
| **Deep (4-track, 4K response)** | **~8K** | **~16 turns** |
| Ultra (4-track + self-audit, 5K response) | ~10K | ~12 turns |

**GTO sweet spot: ~16 deep turns** per ultrastart session.

### The 4-Phase Turn Allocation

| Phase | Turns | Purpose | Token Strategy |
|:------|:------|:--------|:---------------|
| **Frame** | 1-3 | Define scope. Pull history. Identify constraints. | Heavy JIT retrieval (~5K/turn). Lighter responses. |
| **Deep Work** | 4-10 | Core analysis. Multi-track. Cross-domain. | Maximum reasoning depth (~4K responses). Moderate JIT. |
| **Refine** | 11-14 | Stress-test. Adversarial. Edge cases. | Track B (Skeptic) prominence. Target weak spots. |
| **Synthesise** | 15-16 | Final output. Actionable recommendations. Filing. | Long-form synthesis (~5K). Minimal JIT. |

### One-Session-One-Feature (Attention Physics)

**16 deep turns on ONE topic >> 16 shallow turns across 4 topics.** This is not a workflow
preference — it's an architectural constraint:

1. **Context coherence**: All 57K boot tokens aligned to one objective. No dilution.
2. **JIT compounding**: Each retrieval builds on the last. Turn 8's search is informed by turns 1-7.
3. **Reasoning compounding**: Track C (Cross-Domain) improves as conversation accumulates data points.
4. **No context switching tax**: Topic switches waste context on transition overhead.
5. **Attention physics**: Past 200K, the model starts losing attention on early context.
   Splitting focus across topics accelerates this degradation.

> **Rule**: One session = one objective. When the objective is complete, `/ultraend` and start fresh.

### Topic-Drift Detection (v3.1)

If a user query diverges **>2 clusters** from the boot objective (as resolved in Phase 4):

> ⚠️ "Topic drift detected (boot: [**original domain**], current: [**new domain**]).
> Continue here (cross-reference quality may degrade), or `/ultraend` → `/ultrastart [new topic]`?"

**Detection heuristic**: Compare the domain classification of the current query against the boot objective's cluster. If the current query would route to a different Cognitive System (per `/start` Phase 3 routing table), that's a drift signal.

**Do NOT fire on**:
- Naturally adjacent domains (Trading → Psychology, Consulting → Pricing)
- Sub-topics of the boot objective
- Meta-questions about the session itself

**Do fire on**:
- Complete domain switches (e.g., boot = Trading, current = Academic Delivery)
- Sustained topic change (2+ consecutive queries in the new domain)

---

## Stability Controls

| Trigger | Action |
|---------|--------|
| `Core_Identity.md` load fails | **ABORT** boot. Report error. |
| `CANONICAL.md` load fails | **WARN** and continue (graceful degradation). |
| Any Tier 2-4 module fails | **WARN** and continue (non-critical). |
| `smart_search.py` fails or returns 0 results | Skip Phase 4. Boot with Phases 1-3 only. |
| User says `/start` after `/ultrastart` | Compact to `/start` footprint (purge deep loads). |

---

## Upgrade Log

| Version | Date | Change |
|:--------|:-----|:-------|
| v1.0 | 2026-03-10 | Initial 20K static boot (4 phases, budget-capped). |
| v2.0 | 2026-03-15 | 25K lean boot + JIT primary + max reasoning depth. Still efficiency-biased. |
| v3.0 | 2026-03-15 | **Maximum Compute rewrite.** Removed all budget caps. Load ALL 11 framework modules. Full state extraction. Expanded semantic bridge (15 results, full loads). JIT as supplement not replacement. Philosophy: flat-rate subscription = tokens are free = optimize quality, not efficiency. |
| v3.1 | 2026-05-11 | **Subscription-awareness gate.** Auto-detects flat-rate vs quota-limited plans → MaxMax or MaxMax-Lite. Added context utilization metric to boot confirmation (target <80%). Added topic-drift detection for One-Session-One-Feature enforcement. |

---

## References

- [/ultraend](ultraend.md) — Symmetric deep close counterpart
- [/start](start.md) — Lightweight boot
- [/end](end.md) — Lightweight close

---

## Tagging

`#workflow` `#boot` `#ultrastart` `#system-2` `#deep-context` `#maximum-compute` `#no-budget-cap` `#jit-retrieval` `#max-depth`
