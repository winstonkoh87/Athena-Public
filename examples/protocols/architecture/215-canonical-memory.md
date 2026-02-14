---
created: 2025-12-27
last_updated: 2026-02-14
graphrag_extracted: true
---

# Protocol 215: Canonical Memory Architecture

> **Type**: Architecture Pattern  
> **Status**: Active (Feb 2026)  
> **Related**: Protocol 000 (Core Identity), Protocol 200 (Feature Persistence)
> **Source**: Integration of Letta (MemGPT) Memory Blocks

## 1. The Core Problem: Memory Staleness

AI memory (Vector DB) treats all documents as equal. A session log from 2024 claiming "X=5" competes with a session log from 2025 claiming "X=10". This leads to regression and hallucination of outdated facts.

## 2. The Solution: Memory Blocks (The Letta Model)

We adopt the **Tiered Memory Block** architecture from Letta/MemGPT to enforce strict context boundaries.

### Block A: The Core Block (Immutable Identity)

- **Source**: `Core_Identity.md`, `System_Manifest.md`
- **Mutability**: Read-Only (except via kernel update).
- **Purpose**: Defines *who* the agent is and *how* it thinks.
- **Context Priority**: Highest.

### Block B: The User Block (Mutable Profile)

- **Source**: `userContext.md`, `productContext.md`
- **Mutability**: Read-Write.
- **Purpose**: Stores facts about the User and the Product strategy.
- **Content**: "User prefers robust systems", "Product is a Linux OS for Agents".

### Block C: The Working Block (Current Thread)

- **Source**: `activeContext.md`, Current Session Messages.
- **Mutability**: Highly Volatile.
- **Purpose**: Scratchpad for immediate tasks. Wiped or archived on session end.

### Block D: The Archival Block (Long-Term Storage)

- **Source**: `CANONICAL.md`, Vector DB (RAG).
- **Mutability**: Append-Only (mostly).
- **Purpose**: The "Hard Drive" of the agent. Stores finalized decisions and facts.

---

## 3. The Update Loop (The "Collapse" function)

At the end of a session (or task), if a **new fact** is established or an **old fact** is corrected:

1. **Diff**: Does this contradict `CANONICAL.md`?
2. **Sync**: If yes, update `CANONICAL.md` immediately.
3. **Log**: The Session Log just records *that* we updated it.

## 4. Search Hierarchy (Enforcement)

When answering queries about state (metrics, plans, decisions):

1. **Priority 0**: `CANONICAL.md` (The Truth)
2. **Priority 1**: `project_state.md` (Technicals)
3. **Priority 2**: `TAG_INDEX.md` (Pointers)
4. **Priority 3**: Session Logs (Forensics/Context)

> **Rule**: If `CANONICAL.md` says X and `Session 42` says Y, **X is true**.

## 5. Maintenance

- **Owner**: The AI (Autonomic).
- **Trigger**: `/end`, `/refactor`, or any logic-reversal decision.
