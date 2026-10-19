---
date: 2026-10-20
last_updated: 2026-10-20
---

# Top 10 Protocols — Re-Ranked (October 2026)

> **Date**: 20 October 2026  
> **Methodology**: Heatmap-weighted MCDA (705 sessions scanned) + code-enforced execution infrastructure + cross-domain pattern validation  
> **Sessions Analyzed**: 2,100+ (705 systematically parsed via `protocol_heatmap.py`)  
> **Key Shift**: June 2026 optimized for behavioral habituation. October 2026 elevates **code-enforced execution infrastructure** (`gto_engine.py`, `frame_ledger.py`, Protocol 500 capstone) and **empirical frontline telemetry** (P000 Ultimate Auditor and P002 Context is King).

These are the 10 most impactful protocols from the Athena framework, re-ranked based on actual usage data, deterministic code-enforcement, and observed behavioral outcomes across 2,100+ sessions.

---

## What Changed Since the June 2026 Ranking

The June 2026 ranking transitioned Athena from *theoretical importance* to *behavioral evidence* across 411 sessions.

Between June and October 2026, Athena underwent its most substantial architectural evolution (v10.0):

1. **Deterministic Execution Layer**: Protocol 500 evolved from a conceptual matrix into `gto_engine.py` (3,000 LOC, 107 tests), screening decisions deterministically with SHA-256 receipts.
2. **Problem Framing Machine Contract**: Protocols 504–506 crystallized into `frame_ledger.py` (57 tests), enforcing Value of Information (VOI) stop rules and R1–R13 falsification gates before expensive computation begins.
3. **Telemetry Maturity**: Systematic parsing across 705 session logs revealed that **P000 (Ultimate Auditor)** is the #1 most referenced protocol in the system (104 references), and **P002 (Context is King)** is #3 (88 references).
4. **Code-Enforced Life Safety**: Protocol 509 was hardcoded into runtime IDE hooks, establishing an absolute, zero-bypass survival gate.

---

## MCDA Methodology

### Criteria Weights

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| **Ruin Prevention** | 30% | Law #1. Non-negotiable survival filter across financial, legal, psychological, and systemic risk. |
| **Empirical Behavioral Impact** | 30% | Did this protocol demonstrably change how decisions are executed and outcomes secured? |
| **Usage Frequency** | 25% | Heatmap telemetry across 705 systematically parsed session logs. |
| **Cross-Domain Universality** | 15% | Does this protocol operate invariantly across 5+ domains (trading, software, pricing, operations, personal)? |

### Scoring Scale

| Score | Meaning |
|-------|---------|
| **5** | Best-in-class (top 5% of all protocols / system invariant) |
| **4** | Strong (top 20% / frequent load-bearing protocol) |
| **3** | Good (average / domain-specific powerhouse) |
| **2** | Below average |
| **1** | Weak / narrow use case |

---

## The Rankings

| Rank | Protocol | June Rank | Δ | Weighted Score |
|:-----|:---------|:----------|:--|:---------------|
| **1** | **P001: Law of Ruin (No Irreversible Ruin)** | 1 | — | **5.00** |
| **2** | **P000: Ultimate Auditor (Zero-Blind-Spot Architecture)** | *Unranked* | ⬆ NEW | **4.85** |
| **3** | **PAT-574: Substance Decode Lens (Form-Substance Gap)** | 2 | ⬇ 1 | **4.70** |
| **4** | **P002: Context is King (Retrieval-Led Grounding)** | *Unranked* | ⬆ NEW | **4.55** |
| **5** | **P003: Revealed Preference (Actions > Words)** | 3 | ⬇ 2 | **4.45** |
| **6** | **P500: GTO Problem Solver (Strategic Matrix v4.3 & Decision Engine)** | *Unranked* | ⬆ NEW | **4.45** |
| **7** | **P193: Ergodicity Check (Time-Average vs Ensemble-Average)** | 4 | ⬇ 3 | **4.05** |
| **8** | **P504–506: Problem Framing Layer & Frame Ledger (VOI & Falsifiers)** | *Unranked* | ⬆ NEW | **4.00** |
| **9** | **P509: Crisis & Life-Safety Screen** | *Unranked* | ⬆ NEW | **4.00** |
| **10** | **P048: Circuit Breaker (Systemic Pause)** | 7 | ⬇ 3 | **3.80** |

---

## Detailed Scoring Matrix

| Protocol | Ruin Prevention (30%) | Behavioral Impact (30%) | Usage Frequency (25%) | Cross-Domain (15%) | **Total** |
|----------|:---------------------:|:-----------------------:|:---------------------:|:------------------:|:---------:|
| **P001: Law of Ruin** | 5 | 5 | 5 (228 refs: 95 P001 + 133 Law#1) | 5 | **5.00** |
| **P000: Ultimate Auditor** | 5 | 5 | 5 (104 refs — #1 in heatmap) | 4 | **4.85** |
| **PAT-574: Substance Decode** | 4 | 5 | 5 (46 skill + 7 direct refs) | 5 | **4.70** |
| **P002: Context is King** | 4 | 5 | 5 (88 refs — #3 in heatmap) | 4 | **4.55** |
| **P003: Revealed Preference** | 4 | 5 | 4 (38 refs + 9 Law#3 refs) | 5 | **4.45** |
| **P500: GTO Problem Solver** | 5 | 4 | 4 (7 direct + gto_engine runtime) | 5 | **4.45** |
| **P193: Ergodicity Check** | 5 | 4 | 3 (trading + career allocation) | 4 | **4.05** |
| **P504–506: Problem Framing** | 4 | 4 | 4 (Cluster #15 + frame_ledger) | 4 | **4.00** |
| **P509: Crisis & Life Safety** | 5 | 4 | 4 (21 refs + code-enforced hook) | 2 | **4.00** |
| **P048: Circuit Breaker** | 5 | 4 | 2 (emergency pause backstop) | 4 | **3.80** |

---

## The 5 Promotions (Why They Entered)

### P000: Ultimate Auditor (Zero-Blind-Spot Architecture) → Rank #2

* **What it does**: Enforces an adversarial pre-mortem, bias sweep, and red-team audit before committing resources or finalizing deliverables.
* **Old status**: Unranked (was considered an audit utility rather than a core protocol).
* **Why it rose**: Across 705 parsed sessions, P000 is the **#1 most referenced protocol in the entire system (104 references)**. Every implementation plan (`/plan`), proposal review, and critical artifact runs through P000's zero-blind-spot lens.
* **Behavioral evidence**: Prevented premature client delivery, caught unhandled trade execution edge cases, and anchored the red-team review workflow.

### P002: Context is King (Retrieval-Led Grounding) → Rank #4

* **What it does**: Mandates that the system ground every non-trivial decision in local ground-truth files and retrieved telemetry rather than relying on LLM pre-training weights or ungrounded assumptions.
* **Old status**: Unranked.
* **Why it rose**: Generated **88 references** across session logs (#3 in the heatmap). Law #2 is the operational discipline that prevents hallucination, ensures state persistence, and protects system integrity.
* **Behavioral evidence**: The shift from generic prompt-based advice to data-backed decisions (e.g., pricing analysis using historical job telemetry, trading journal reconciliation) is entirely driven by P002.

### P500: GTO Problem Solver (Strategic Matrix v4.3 & Decision Engine) → Rank #6

* **What it does**: Capstone strategic decision framework. Evaluates real-world dilemmas under Knightian ambiguity using Expected Economic Value (EEV), One-Third Kelly sizing, absorbing-barrier ruin modeling, and MCDA.
* **Old status**: Unranked (conceptual stage in June).
* **Why it rose**: Transformed from prose into an executable Python engine (`gto_engine.py`, 3,000 LOC, 107 tests). Emits tamper-evident SHA-256 decision receipts, bridging mathematical game theory directly into runtime tool calls.
* **Behavioral evidence**: Used to size trading risk, evaluate complex client engagements, and price counterparty negotiations.

### P504–506: Problem Framing Layer & Frame Ledger → Rank #8

* **What it does**: Imposes a 5-gate diagnostic before solution design: Problem Statement Lock, Value of Information (VOI) anti-rumination stop rule, rival hypothesis engineering, and falsifiable exit criteria.
* **Old status**: Unranked.
* **Why it rose**: Shipped in `frame_ledger.py` (57 tests). Prevents the #1 cognitive error in knowledge work: solving the wrong problem with high efficiency.
* **Behavioral evidence**: Eliminated speculative drafting on unconfirmed client proposals and truncated open deliberation loops when expected information value was negative.

### P509: Crisis & Life-Safety Screen → Rank #9

* **What it does**: Universal life-safety override. Immediately prioritizes life safety and professional crisis resources over all agent tasks upon detecting any distress signals.
* **Old status**: Unranked.
* **Why it rose**: Elevated to an absolute, non-negotiable hard rule. Enforced deterministically in runtime IDE lifecycle hooks.
* **Behavioral evidence**: 21 references. Acts as the system's foundational ethical boundary.

---

## The 5 Demotions (Why They Dropped)

| Protocol | Old Rank | New Rank | Reason |
|:---------|:---------|:---------|:-------|
| **MP-15 carrier: Preparation Asymmetry** | 5 | Dropped | MP-15 is a *meta-pattern*, not a protocol file. Its concrete operational enforcement is now directly carried by P000 (pre-mortem auditor) and P504 (problem framing). |
| **P75: Synthetic Parallel Reasoning** | 6 | Dropped | High token and latency overhead (4 parallel tracks). Heatmap telemetry shows near-zero invocations in recent sessions; superseded by focused `/ultrathink` and P500 decision screening. |
| **BUS-96: Income Hierarchy** | 8 | Dropped to #13 | The "Hand-Stop-Mouth-Stop" heuristic remains an effective career compass, but it is a periodic orientation model rather than a daily operational engine. |
| **P140: Base Rate Audit** | 9 | Dropped | Fully absorbed into PAT-574 (Substance Decode Lens) and Strategic Matrix v4.3. Maintaining both in the Top 10 was redundant. |
| **DEC-330: Aoy's Fried Rice** | 10 | Re-anchored | In the codebase, DEC-330 formally represents Economic Expected Value (EEV non-linear utility), which has been integrated into P500's `gto_engine.py`. |

---

## The Stability Test

### Protocols that held their rank (or nearly)

| Protocol | Old | New | Signal |
|:---------|:----|:----|:-------|
| **P001: Law of Ruin** | 1 | 1 | Unassailable. 228 references across logs. Law #1 status. |
| **PAT-574: Substance Decode** | 2 | 3 | Core analytical differentiator. 46 skill invocations. |
| **P003: Revealed Preference** | 3 | 5 | Actions > Words. 38 references + 9 Law#3 references. |
| **P193: Ergodicity Check** | 4 | 7 | Foundational mathematics for survival under non-ergodic multiplicative processes. |
| **P048: Circuit Breaker** | 7 | 10 | Rock-solid emergency backstop across trading, spending, and work domains. |

---

## What This Ranking Reveals About Evolution

```
Original (Jun 6):   Safety → Decision → Reasoning → Engineering
June 17 Ranking:    Safety → Pattern Detection → Behavioral → Meta-Pattern → Decision
October 20 Ranking: Safety & Auditing → Substance Decode → Grounded Reality → Machine Decision Infrastructure
```

**Translation**:
* The early ranking was **theoretical** (what sounds intellectually profound).
* The June ranking was **behavioral** (what changed human habits).
* The October ranking is **structural and code-enforced** (what is backed by deterministic Python engines, machine gates, and frontline session frequency).

The top protocols in October are either non-negotiable survival gates (P001, P193, P048, P509), empirical reality filters (P000, PAT-574, P002, P003), or deterministic decision software (P500, P504–506).

---

## How to Use These Protocols

### For ChatGPT / Claude / Cursor / Antigravity Users

1. **Copy** the protocol markdown file from the [protocol library](../examples/protocols/).
2. **Mount** into your IDE's system instructions or rules (`AGENTS.md` / `.cursorrules` / `CLAUDE.md`).
3. The model adopts the decision constraints immediately.

### For Athena Users

These protocols run automatically via the skill and MCP runtime:

- `/plan` → Triggers P000 (Ultimate Auditor / Pre-Mortem)
- `decision_screen` → Invokes P500 via `gto_engine.py` (EEV, 1/3 Kelly, Ruin Screen)
- `frame_open` / `frame_validate` → Enforces P504–506 via `frame_ledger.py`
- `/start` → Executes P002 (Context is King) JIT memory load

---

## Cross-References

- [Full Protocol Library](../examples/protocols/) — All active protocols
- [Architecture Overview](ARCHITECTURE.md) — System design
- [References](REFERENCES.md) — Academic grounding and DOI verifications
- [Getting Started](GETTING_STARTED.md) — Setup guide

---

> *"The protocols that survive aren't the ones that sound profound in a prompt. They're the ones that compile into code, stop irreversible ruin at runtime, and get invoked by reflex when stakes are real."*

---

Part of [Project Athena](https://github.com/winstonkoh87/Athena-Public)
