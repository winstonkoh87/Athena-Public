---
description: High-Assurance Curated Compute boot (System-2) v4.0 — counterpart to /start
created: 2026-03-10
last_updated: 2026-11-14
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultrastart — High-Assurance Curated Compute (MaxMax v4.0)

> **Latency Profile**: MEDIUM (~10-15s boot) | **Boot Budget Ceiling**: `<= 40K tokens` (`< 20%` of 200K ECL)
> **Philosophy**: Maximize **verified reasoning quality** (`>= 160K tokens` headroom for multi-track thinking, counter-evidence, and tests), NOT raw Turn-1 file dumps.
> **Use When**: Architecture overhauls, irreversible/high-stakes capital or life decisions, deep research, or red-team audits. Default sessions use `/start` (MinMax v2.0).

> [!IMPORTANT]
> **Context Rot Guardrail (Why v4.0 Replaces Raw Unbounded Boot)**:
> Dumping `.context/CANONICAL.md` (`414 KB`), `CANONICAL_TIER2.md` (`241 KB`), `PROJECTS.md` (`923 KB`), and all `.framework` modules raw injects `~1.72 MB` (`~430K tokens`) on Turn 1 — exceeding the **200K Effective Context Length (ECL)** by `2.15x`, triggering P517 downshift before Turn 1 starts, and degrading attention via Lost-in-the-Middle dilution.
> MaxMax v4.0 spends tokens on **bidirectional search, isolated multi-track reasoning, and verification**, not uncurated text dumps.

## 200K ECL Budget Allocation

- `~15K` Platform overhead (IDE prompt, tools, `AGENTS.md`)
- `<= 40K` Curated High-Signal Boot (`< 20%` of 200K ECL: Core Laws + Active Decisions + Active Switchboard + Trajectory + 3-Vector Search)
- `~145K` Reserved headroom for **~16-18 deep turns**:
  - **Turns 1-3 (Frame)**: Constraints, history, disconfirming evidence (`~5K JIT/turn`)
  - **Turns 4-10 (Deep Work)**: 4-track synthesis & implementation (`~4K output/turn`)
  - **Turns 11-14 (Refine)**: Adversarial stress-test & Track B skeptic attack
  - **Turns 15-18 (Synthesise)**: Verified output, self-audit, `/ultraend` filing

---

## Phase 1: Core & Operational Identity (~13K tokens)

Load in parallel (note: `Operating_Principles.md` is deprecated and merged into `System_Principles.md`):

- `.framework/v8.2-stable/modules/Core_Identity.md` *(Gate: **ABORT** if missing)*
- `.framework/v8.2-stable/modules/Output_Standards.md`
- `.framework/v8.2-stable/modules/System_Principles.md`
- `.framework/v8.2-stable/modules/Constraints_Master.md`

**Domain-Matched Tier 3/4 Modules (load surgically ONLY when objective matches)**:
- Identity / calibration: `Athena_Profile.md`, `Session_Observations.md`
- UI / frontend design: `Design_DNA.md`
- Continuity / infra audit: `DEAD_MAN_SWITCH.md`, `Governance_Audit_2025.md`, `System_Manifest.md`

---

## Phase 2: Surgical Materialized Truth (~10K tokens)

Read **only** high-signal active sections (warn and continue if missing):

1. `.context/CANONICAL.md`: Read **Lines `L1-185`** (Header, §1 System Metrics, §1.1 Success Ledger, §2 Core Laws, §3 Active Decisions) and **Lines `L553-571`** (§6 Key Reference Docs, §7 Active Pipeline).
   - **Never bulk-load** `CANONICAL.md` §4-5 (`390 KB`) or `CANONICAL_TIER2.md` (`241 KB`) at boot — retrieve matching framework rows via Phase 4 search/FTS5.
2. `.context/PROJECTS.md`: Read **active switchboard tables only (`L1009-1067`)** (`Internal Operating Systems`, `Internal Projects`, `External Projects`). Skip `L1-1008` (`851 KB` archive history).
3. `.context/CANONICAL_TIER3.md` *(optional niche precedents, `~2.2 KB`)*.

---

## Phase 3: Trajectory State & Batched Telemetry (~5K tokens)

1. **Read in parallel**:
   - `.context/memory_bank/userContext.md`
   - `.context/memory_bank/productContext.md`
   - `.context/memory_bank/threatPlaybooks.md`
   - `.context/memory_bank/activeContext.md` (Header + last **3** `[[ S__` checkpoints + any unclosed session)
2. **Run single batched telemetry script (`< 1.0s`, zero `RuntimeWarning`)**:
   ```bash
   .agent/scripts/athena-py scripts/boot_status.py
   ```
   Surface exact accountability (`BEH-601/602/603`), maintenance ratio, frame ledger, due decisions, and index health verbatim from execution receipts.
   - Saturday & `beh_601.last_completed` not this week -> `⚠️ Saturday — BEH-601 Solo Session target active.`
   - Sunday & `weekly_audit.last_audit_date` > 7d -> `📊 Weekly execution audit due on /ultraend.`
   - If session touches psychology/behavior, also read `.agent/state/accountability_status.json` + active `BEH-` protocols and flag any `BEH-602` pattern with `3+` weekly triggers (`🚩 Recurring trigger: ...`).

---

## Phase 4: Dual-Vector Semantic Bridge (~8-12K tokens)

### Step 1: Resolve Objective
Priority: **Explicit inline arg** -> **`@seeded` from latest checkpoint** -> **Highest-urgency active row in `PROJECTS.md` (`L1009-1067`)** -> **`Current Focus`** -> **Ask user** (if reached, log `[REFLEXION] Phase 4 reached ASK fallback`).

### Step 2: 3 Parallel Search Vectors (Confirming + Disconfirming + Cross-Domain)
Execute concurrently via `.agent/scripts/athena-py .agent/scripts/smart_search.py` (or `mcp_athena_context_gate`):

```bash
# 1. Primary domain recall (deep)
.agent/scripts/athena-py .agent/scripts/smart_search.py "<resolved objective>" --limit 10 --include-personal --rerank

# 2. Disconfirming / counter-evidence sweep (adversarial floor)
.agent/scripts/athena-py .agent/scripts/smart_search.py "<resolved objective> failure mode ruin post-mortem critique" --limit 5 --include-personal

# 3. Cross-domain isomorphism sweep (Track C fuel: Psychology/Stats, Sales/Arch, Game Theory, etc.)
.agent/scripts/athena-py .agent/scripts/smart_search.py "<adjacent domain keywords>" --limit 5 --include-personal
```

### Step 3: Curated Deep Load
Load full text of the **top 3-5 highest-reranked protocols or case studies** (reranker logit `> 1.0`), full `SKILL.md` for matched skills, and surgical `@decided`/`@learned` blocks of matched sessions. Skip `smart_search` failures gracefully and proceed with Phases 1-3.

---

## Phase 5 & 6: Always-On Deep Execution, Multi-Track Reasoning & Gates

- **Tool Arsenal (No Skip)**: Treat Exocortex, `search_web`, `read_url_content`, browser sub-agent, MCP servers (`athena`, `supabase`, `gitkraken`), `grep_search`, and test/verification runners as mandatory whenever claims can be verified. SNIPER search exemption is **disabled** after `/ultrastart`.
- **Autonomic Depth & 4-Track Scaffold (`Lambda >= 25`)**:
  - `Lambda <= 24`: Direct Domain track.
  - `Lambda 25-40`: **Track A (Domain Expert)** + **Track B (Adversarial Skeptic / Ruin Check)**.
  - `Lambda 41-60`: Tracks A + B + **Track C (Cross-Domain Pattern Matcher)**.
  - `Lambda > 60`: Full **4-Track Synthesis (`A + B + C + D Synthesis`)** via `/ultrathink` + **9-Point Post-Generation Self-Audit** (`Core_Identity` §0.4: formulas cited, Assumption Register, steelmanned alternative, "The Victim" stakeholder map, sensitivity sweep, mechanism vulnerabilities, numerical example, scope boundary, concrete limitations).
- **One-Session-One-Feature & Drift Valve**:
  - If first user query has `Lambda <= 15`: surface Complexity Gate prompt offering `/start`.
  - If query diverges `> 2` clusters (2+ turns in unrelated domain): warn on topic drift and offer `/ultraend` -> `/ultrastart [new topic]`.
  - **P517 Homeostasis Alerts**: `70% (140K)` -> soft density alert; `80% (160K)` -> treat non-critical follow-ups as SNIPER; `90% (180K)` -> run `context-compactor` before responding.
  - User saying `/start` mid-session compacts to `/start` footprint.

## Boot Confirmation

```text
🧠 Deep Boot Complete (MaxMax v4.0 — High-Assurance Curated Compute).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 1] Identity Core            ✅  (<N> framework modules loaded)
[Phase 2] Surgical Truth           ✅  (CANONICAL L1-185 + PROJECTS L1009-1067)
[Phase 3] Trajectory + Telemetry   ✅  (boot_status <1s + <N> checkpoints)
[Phase 4] Dual-Vector Bridge       ✅  (Primary + Counter-Evidence + Cross-Domain)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Boot Budget: ~<XX>K / 200K ECL (<YY>% utilized — target < 20% / <= 40K tokens)
Objective: "<resolved objective>"
⚡ System-2 active | Multi-track ON (Lambda >= 25) | 9-Point Self-Audit ON (Lambda > 60)
```

- References: [/ultraend](ultraend.md), [/ultrathink](ultrathink.md), [/start](start.md), [/end](end.md)

`#workflow` `#boot` `#ultrastart` `#system-2` `#maxmax` `#high-assurance`
