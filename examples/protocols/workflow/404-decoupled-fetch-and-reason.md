---
title: "Decoupled Fetch & Reason"
id: 404
type: workflow
author: [AUTHOR] (Antigravity)
created: 2026-02-02
tags: [workflow, architecture, glass-box, reasoning, cost-optimization]
---

# Protocol 404: Decoupled Fetch & Reason

> **Philosophy**: "Boot fast. Fetch raw. Reason later."

## 1. The Core Problem

**Constraint**: Most AI agents default to "Black Box" mode—they fetch data invisibly and present a summarized hallucination.
**Risk**:

- **Opacity**: User cannot verify the source data.
- **Cost**: Reasoning tokens are burned on mundane fetching.
- **Context Limit**: The fetching agent's context window limits the depth of synthesis.

## 2. The Solution: Glass Box Architecture

We decouple the **Acquisition Layer** (Fetch) from the **Synthesis Layer** (Reason).

### The Human Conduit (Cost Arbitrage)

**Old Flow (Machine-Driven API Calls):**

```
AG (Athena) --> Gemini 3 Flash API --> Output
               (Paid: $0.01-$0.10/call)
```

**New Flow (Human-Driven API Calls):**

```
AG (Athena) --> Human User --> Gemini Pro UI --> Human User --> AG (Athena)
               (Prep Data)     (FREE)            (Paste JSON)   (Ingest)
```

**Why This Works:**

1. **Zero Cost**: Gemini Advanced/Pro UI is included in subscription.
2. **Infinite Context**: UI handles 1M+ tokens; API chunking is fragile.
3. **Better Reasoning**: Web UI often runs newer/smarter models.
4. **Human QA**: User sees raw data before synthesis, catching hallucinations early.

---

### Phase 1: The Fetch (Acquisition)

- **Role**: Dumb Retriever.
- **Goal**: Maximize raw information density per dollar.
- **Action**:
    1. Run tools (Search, Scrape, DB Query, Git Log).
    2. **DO NOT SUMMARIZE.**
    3. Dump raw outputs to a structured artifact (e.g., `research_dump_topic.md` or `.context/dumps/`).
    4. Return **only** the artifact path to the user.

### Phase 2: The Reason (Synthesis)

- **Role**: Smart Analyst.
- **Goal**: Maximize insight per token.
- **Trigger**: User explicitly requests synthesis *after* seeing the dump.
- **Action**:
    1. Load the artifact into the context window (or Gemini UI).
    2. Apply high-order reasoning (Opus/Gemini Pro).
    3. Produce final output.

## 3. Execution Protocol

**When the user asks for "Research/Find/Check":**

1. **Acknowledge**: "Initiating Protocol 404 (Decoupled Fetch)."
2. **Execute Tools**: Run the necessary scripts.
3. **Write Artifact**:

   ```python
   with open(".context/dumps/research_task.md", "w") as f:
       f.write(raw_tool_output)
   ```

4. **Handoff**:
   > "Data acquired. Raw dump saved to [`research_task.md`](file://...).
   >
   > **Options**:
   > 1. [Review Raw Data]
   > 2. [Synthesize with Gemini] (I will read the file and summarize)"

## 4. Anti-Patterns (What NOT To Do)

- ❌ **The "Helpful" Assistant**: Fetching and summarizing in one breath.
- ❌ **The Invisible Hand**: Running tools without saving the output to a persistent file.
- ❌ **The Context Nuke**: Dumping 100kb of text into the chat stream instead of a file.
