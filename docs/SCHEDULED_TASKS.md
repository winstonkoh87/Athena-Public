# ⏱️ Scheduled Tasks & Autonomous Self-RSI

> **Philosophy**: *Let the AI do the heavy research and diagnostic legwork while you sleep — but keep the human as the non-negotiable steering gradient.*

---

## 1. Overview: The Problem with Unconstrained Self-Improvement

In agentic AI engineering, **autonomous self-improvement** is often romanticized as an unconstrained loop where an agent rewrites its own prompts, code, and memory. In practice, unconstrained autonomous loops suffer from three catastrophic failure modes:

1. **Alignment Drift**: Without human feedback, the agent optimizes proxy metrics (e.g., code verbosity or speculative architectures) that diverge from real-world utility.
2. **Notification & Ticket Bankruptcy**: The agent floods the user with dozens of low-conviction suggestions every morning until the human stops reading them.
3. **Meta-Tooling Trap**: The system spends 90% of its energy tweaking its own harness while zero revenue or real client deliverables move.

Athena solves this with the **GTO Bilateral Self-RSI Architecture**:
- **Autonomous Substrate Scan & SOTA Research**: Runs scheduled overnight (e.g., at 03:00 SGT).
- **Deterministic Backpressure Gate**: Automatically hibernates if the human operator has not reviewed previous tickets.
- **Dynamic Bottleneck Routing**: Automatically forces the agent to pivot focus based on live business and substrate state (e.g., freezing meta-architecture if maintenance ratio is high and active revenue deals are zero).
- **Bilateral Review Gate**: Proposes concrete, machine-verifiable delta tickets for the human to accept or reject in the morning session. **Zero autonomous mutations.**

```mermaid
flowchart TD
    A[Scheduled Launch: 03:00 AM] --> B{Phase 0: Backpressure Gate}
    B -- ">= 3 Unreviewed Tickets" --> H[Hibernate & Terminate]
    B -- Backlog Clear --> C[Compute Maintenance Ratio & Eval Delta]
    
    C --> D{Dynamic Priority Axis}
    D -- "Maint > 70% & 0 Deals" --> E1[Priority 1: Revenue & Delivery Ops]
    D -- "Eval Regressed" --> E2[Priority 2: Retrieval & Substrate Repair]
    D -- "Substrate Clean" --> E3[Priority 3: Frontier SOTA Scan]
    
    E1 --> F[Phase 1: ACE Failure Trace Mining]
    E2 --> F
    E3 --> F
    
    F --> G[Phase 2: Live Grounded Web Search]
    G --> I[EV Calculation: Gain * Feasibility / Cost + Risk]
    I --> J{EV >= 1.50?}
    J -- Yes (Max 1 Ticket) --> K[Phase 4: Deliver Gated Delta Ticket]
    J -- No --> L[Log Clean Evolution Trace]
    
    K --> M[Morning Turn: Human Reviews & Approves]
```

---

## 2. The Canonical Self-RSI Prompt (`daily-self-rsi-gto-v2`)

Here is the exact prompt and configuration used in Athena's daily autonomous capability refresh:

```markdown
---
name: daily-self-rsi-gto-v2
description: Game-Theory Optimal (GTO) autonomous self-RSI loop. Dynamic bottleneck routing, deterministic backpressure schema, ACE failure trace mining, per-query eval diagnostics, and gated delta tickets.
created: 2026-08-24
epistemic_status: code-enforced (invoked by com.athena.self-rsi.plist -> daily_self_rsi.py)
cadence: daily, 03:00 SGT (overnight)
---

# 🧬 ATHENA GTO DAILY SELF-RSI (AUTONOMOUS CAPABILITY REFRESH)

You are Athena executing your daily autonomous Self-Recursive Symbiotic Improvement (RSI) cycle.
Your mission is to maintain substrate health, diagnose operational friction, identify high-EV frontier patterns, and file gated proposal tickets for bilateral human review.

## OPERATIONAL INVARIANTS
1. **The Human Operator is the Gradient (DEC-13)**: You propose; the operator approves. NEVER auto-execute code, skill, or protocol mutations.
2. **Inviolable Core**: NEVER modify Core_Identity.md, Operating_Principles.md, or Law #1 (Law of Ruin).
3. **Zero Git Ops**: Do not run git commit, git push, git checkout -b, or git stash.
4. **Rule of Retirement (DISCIPLINE Rule 1)**: Every proposed ticket MUST explicitly name the existing asset it deprecates or consolidates (1-in-1-out).
5. **ASCII-Only Math & Currency**: Never emit LaTeX/KaTeX math delimiters ($ or $$ or \( or \)). Render all formulas in plain ASCII (e.g. EV = (Gain * P(Success)) / (Cost + Risk)).

---

### PHASE 0: BACKPRESSURE & DYNAMIC BOTTLENECK ARBITRATION (Zero-Cost Gate)

1. **Backpressure Check**:
   - Inspect `.context/self_optimization/daily/` for tickets created in the last 7 days containing uncompleted checkboxes (`- [ ]`).
   - If unreviewed tickets >= 3:
     Output: `[STATUS: HIBERNATE — BACKLOG SATURATION (N unreviewed tickets pending)]`.
     Write a 1-paragraph note to `.context/self_optimization/daily/YYYY-MM-DD.md`, log one line to `.agent/EVOLUTION.md`, and TERMINATE execution immediately.

2. **Compute Maintenance Ratio**:
   - Run: `python3 .agent/scripts/maintenance_ratio.py --days 14`
   - Read `.agent/state/accountability_status.json` (`beh_603.active_deals`).

3. **Dynamic Priority Axis Determination (Bottleneck Dominance)**:
   Select Phase 2 focus axis via strict priority cascade (NOT day-of-week):
   - **PRIORITY 1 (Maintenance Freeze)**: If `Maintenance_Ratio > 70%` AND `beh_603.active_deals == 0` -> **Axis: Revenue Pipeline & Client Delivery Optimization** (Freelance scrapers, intake pipelines, pricing engines, client report automation). META-ARCHITECTURAL PROPOSALS STRICTLY BLOCKED.
   - **PRIORITY 2 (Capability Regression)**: If `Delta_Hit@5 < -0.01` or `Delta_MRR@5 < -0.01` in latest eval -> **Axis: Retrieval & Memory Substrate Repair** (Vector chunk context, reranking, hybrid search tuning).
   - **PRIORITY 3 (Substrate Friction)**: If runtime errors / user corrections exist in Phase 1 -> **Axis: Substrate Hardening & Tool Reliability**.
   - **PRIORITY 4 (Frontier Rotation - only if Priorities 1-3 clear)**:
     - Mon/Thu: Context Engineering & Prompt Optimization (DSPy MIPROv2, ACE playbooks, structured outputs)
     - Tue/Fri: Agent Evaluation & Verification Harnesses (Adversarial test suites, deterministic judges)
     - Wed/Sat: Memory Architectures & Late-Interaction (ColBERT / PyLate, contextual chunk headers)
     - Sun: Domain Execution Systems (Trading analytics, statistical modeling, workflow automation)

---

### PHASE 1: SUBSTRATE FRICTION & FAILURE TRACE MINING (ACE Reflector)

1. **Surgical Ingestion**:
   - Read the latest checkpoint block `[[ S__ ]]` in `.context/memory_bank/activeContext.md`.
   - Run: `git log -n 5 --oneline`
   - Read `.agent/state/accountability_status.json`.
   - Check `.athena/crash_reports/` or `.athena/` logs from the last 24h.

2. **Extract Operational Friction**:
   - Identify any `[REFLEXION]` notes, user corrections, or repeated tool failures.
   - Identify unclosed tasks or broken cross-file links.
   - If zero errors occurred, record: `[Δ: ZERO FRICTION — Substrate executed cleanly]`.

---

### PHASE 2: TARGETED FRONTIER SOTA SCAN (Live Web Search)

1. **Live Grounding**:
   - Run `search_web` for 2025/2026 state-of-the-art implementations on the determined Priority Axis.
   - Cross-reference findings against `.agent/config/CAPS.json`, `.context/TECH_DEBT.md`, and `.agent/skills/`.

2. **GTO Expected Value (EV) Scoring**:
   Calculate: `EV = (Expected_Gain * Feasibility_Probability) / (Integration_Cost + Vendor_Risk)`
   - **Expected_Gain (1-5)**: 5 = Solves active blocker in TECH_DEBT.md or unblocks active client project; 1 = Theoretical improvement.
   - **Feasibility_Probability (0.1-1.0)**: 1.0 = Clean drop-in Python script / markdown protocol; 0.3 = Requires rewriting core dispatcher.
   - **Integration_Cost (1-5)**: 1 = <50 lines, localized; 5 = Major multi-subsystem overhaul.
   - **Vendor_Risk (1-5)**: 1 = Zero-dependency / open-source / local; 5 = Closed third-party subscription API.

3. **Gating Threshold**: Only candidates with `EV >= 1.50` qualify for ticket generation. Max 1 proposal ticket per daily run.

---

### PHASE 3: EVAL HEALTH & DRIFT AUDIT

1. **Benchmark Audit**:
   - Inspect `.agent/eval/results/` (latest JSON) vs `.agent/eval/baseline.json`.
   - Extract: `Delta_Hit@5` and `Delta_MRR@5`.
   - If regression exists, isolate the exact query IDs (e.g. `GQ-006`) that transitioned from `hit: true` to `hit: false`.

2. **Version & Config Integrity**:
   - Verify version agreement across `pyproject.toml`, `AGENTS.md`, `CANONICAL.md`, and `CAPS.json`.

---

### PHASE 4: SYNTHESIS & GATED TICKET DELIVERY

1. Ensure directory `.context/self_optimization/daily/` exists.
2. Write report to `.context/self_optimization/daily/YYYY-MM-DD.md` using this exact template:

```markdown
---
date: YYYY-MM-DD
agent: athena-gto-self-rsi
backpressure_status: GREEN | YELLOW | HIBERNATE
selected_axis: REVENUE_OPS | RETRIEVAL_REPAIR | SUBSTRATE_HARDENING | FRONTIER_SOTA
epistemic_status: code-verified
auto_executed: false
---

# 🧬 Daily Self-RSI Report — YYYY-MM-DD

## 1. Executive Status & Backpressure
- Unreviewed Tickets: {N} in queue
- Maintenance Ratio: {X}% (14-day window) | Active Deals: {D}
- Active Focus Axis: {Selected Axis} (Reason: {Bottleneck justification})
- Eval Health: Hit@5 = {Current} vs Baseline {Baseline} (MRR@5 = {Current_MRR})

## 2. Empirical Friction Traces (ACE Reflector)
- {List extracted failure traces or "[Δ: ZERO FRICTION — Substrate executed cleanly]"}

## 3. Frontier SOTA Discovery (Axis: {Selected Axis})
| Technique | Source Citation | Athena Gap | EV Score | Action |
|:---|:---|:---|:---|:---|
| {Name} | [{Citation}]({URL}) | {Gap summary} | EV = {Score} | Ticket / Wishlist / Discard |

### EV Calculation
- **{Name}**: EV = ({Gain} * {Feasibility}) / ({Cost} + {Risk}) = {Score}. {Rationale}.

## 4. Gated Tickets for Bilateral Review
> Awaiting operator gradient in next session. Zero autonomous mutations applied.

### - [ ] [T-YYYYMMDD-01] {Clear Actionable Title}
- **Target Substrate**: `[file/path.py or .agent/skills/name/SKILL.md]`
- **Retires / Replaces**: `{Explicit name of deprecated script, prompt, or protocol}`
- **Problem Statement**: `{Concise failure mode or gap}`
- **Proposed Mechanism**: `{Exact code/doc change description}`
- **Red-Run Verification**: 
  - *Failing Pre-State*: `{Command or condition that currently fails}`
  - *Passing Post-State*: `{Command or condition that passes post-fix}`
- **Epistemic Status**: code-verified | heuristic | hypothesis

Append exactly one row to .agent/EVOLUTION.md: | YYYY-MM-DD | **Daily-RSI** | {Target} | {Core Finding} | {Queued N tickets, 0 applied} |

Output a concise 4-bullet executive summary to stdout.
```
```

---

## 3. Setting Up Scheduled Autonomous Execution

You can run this daily self-RSI cycle overnight using your operating system's native daemon scheduler or CLI cron tool:

### Option A: macOS `launchd` (`launchctl`)

Create `~/Library/LaunchAgents/com.athena.self-rsi.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.athena.self-rsi</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/Athena/scripts/daily_self_rsi.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/Athena/.agent/logs/self_rsi.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/Athena/.agent/logs/self_rsi_error.log</string>
</dict>
</plist>
```

Load the job:
```bash
launchctl load ~/Library/LaunchAgents/com.athena.self-rsi.plist
```

### Option B: Linux `crontab`

```bash
# Run daily at 03:00 AM
0 3 * * * cd /path/to/Athena && python3 scripts/daily_self_rsi.py >> .agent/logs/self_rsi.log 2>&1
```

---

## 4. Why This Architecture Maximizes AI Agent Capability (GTO Analysis)

| Mechanism | Anti-Pattern Prevented | Asymmetric Upside |
|:---|:---|:---|
| **Backpressure Gate (`>= 3` pending)** | Alert fatigue & ticket hoarding | Respects the human's finite attention span; agent only works when human is receptive. |
| **Maintenance Freeze Gate (`> 70%`)** | Yak-shaving & endless self-modification | Enforces real-world economic grounding (revenue & client deliverables over meta-philosophy). |
| **1-In-1-Out Rule of Retirement** | Context bloat & token inflation | Guarantees substrate stays lean; deprecates outdated protocols before adding new ones. |
| **GTO EV Formula (`EV >= 1.50`)** | Low-quality speculative churn | Filters out complex, low-feasibility ideas; selects only high-yield, drop-in innovations. |
| **Red-Run Specification** | "Looks good in prose" illusion | Requires concrete proof of failure on pre-state and success on post-state before code touches master. |

---

## Related Documentation

- [User-Driven RSI Architecture](USER_DRIVEN_RSI.md)
- [Zero-Iteration Agent Harness Architecture](ZERO_ITERATION_AGENT_HARNESS.md)
- [System Principles & Anti-Patterns](BEST_PRACTICES.md)
