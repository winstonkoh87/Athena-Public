---

created: 2025-12-31
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-31
last_updated: 2025-12-31
---

# System Architecture Specification (V2.1 - Human-Centric)

> **Status**: Active (V2.1)
> **Core Philosophy**: "Bionic Co-Founder" (Active Support, No Policing)

## 1. Core Identity & Laws

The system operates under the 5 Immutable Laws defined in `Core_Identity.md`. This document specifies the *technical architecture* that upholds those laws.

* **Law #0 (Subjective Utility)**: The user is the final judge of value. Metrics are for *insight*, not *judgment*.
* **Law #1 (Ruin Prevention)**: The system prioritizes data safety and system integrity above all else.

## 2. JIT Knowledge Routing (formerly Adaptive Latency)

To verify or "think" about complex topics, the system uses **Outcome-Driven Retrieval**.

* **Concept**: Only retrieve what is necessary to move the *current* task forward.
* **Mechanism**: Use `query_codex` or `search_web` only when the context window is insufficient.
* **Goal**: Preservation of "Flow State".

## 3. Data Hygiene & Metabolism

The system maintains a clean workspace to reduce cognitive load.

* **Session Rotation**: The system proactively suggests ending sessions when context gets messy (>30 messages).
* **Compression**: Old sessions are compressed into summaries (`compress_sessions.py`).
* **Quicksave**: User can trigger `/save` to commit state instantly.

## 4. The Outcome Ledger (Velocity Tracker)
>
> *Reframed from "Scoreboard" to "Tracker".*

The **Outcome Ledger** (`outcomes.log`) is a passive logging tool designed to help the user visualize their own output. It is **not** a policing tool.

### 4.1 Philosophy

* **Mirror, Not Judge**: The ledger reflects what happened. It does not validate, uncap, or reject entries.
* **High Trust**: If the user logs a "SHIP", it is a ship.
* **Anti-Hawthorne**: The goal is to maximize *utility*, not *points*.

### 4.2 Metrics (For User Reference)

* **SHIP (+5)**: Deploying to production or finishing a major artifact.
* **MERGE (+3)**: Integrating code.
* **DECIDE (+2)**: Making a hard decision.
* **META (+0.5)**: Maintenance, planning, refactoring.

## 5. Auditability

* **Compression Receipts**: When data is deleted/compressed, a receipt is generated to prove what was removed.
* **Git History**: All changes are versioned.

## 6. Execution vs. Planning

* **Planning Mode**: Focus on `implementation_plan.md` strategy.
* **Execution Mode**: Focus on `task.md` completion and shipping code.
* **Verification Mode**: focus on `verification_matrix.md` and testing.

---
**Version History**

* V2.0: Shift to "Active Project Manager" (Active Archival)
* V2.1: Human-Centric Refactor (Removed "Anti-Gaming/Policing")

## Related Protocols

- [Protocol 128: Internal Family Systems](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/psychology/128-internal-family-systems.md)
