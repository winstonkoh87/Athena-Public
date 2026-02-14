---created: 2026-01-02
last_updated: 2026-01-30
---

---description: Research Arbitrage Workflow (NotebookLM Method)
created: 2026-01-02
last_updated: 2026-01-02
---

# Research Arbitrage Workflow

> **Source**: CS-200 (Paul James)
> **Purpose**: Transform raw research (URLs, PDFs) into high-value "Structured Intelligence" deliverables.
> **Value**: Turns "reading" (free) into "intelligence" ($$$).

## Phase 1: Ingest (The Raw Material)

**Trigger**: Users asks for "Research on [Topic]" or "Competitor Analysis".

1. **Sourcing**:
    - Use `/research` or `/search` to find 5-10 high-quality URLs/PDFs.
    - *Constraint*: Must be primary sources (Whitepapers, Competitor Homepages, 10k Filings).
2. **Aggregation**:
    - Dump all text/links into a single "Source Context".

## Phase 2: Arbitrage (The Structure)

**Command**: "Structure this into a [Format]."

**High-Value Formats**:

1. **The Comparison Matrix**:
    - Columns: Competitors. Rows: Features, Pricing, Positioning.
2. **The Trend Radar**:
    - Columns: Trend, Impact (High/Med/Low), Timeline (Now/Next/Later).
3. **The Gap Analysis**:
    - Columns: Market Need, Current Solutions, The Gap (Opportunity).

**Prompt**:
> "Act as a McKinsey Analyst. Take these sources.
> Produce a Markdown Table comparing [X] vs [Y].
> Highlight the 'White Space' opportunity in the final column."

## Phase 3: Deliverable (The Asset)

**Packaging**:

1. **Intelligence Brief**:
    - Executive Summary (BLUF).
    - The Structured Table (from Phase 2).
    - Strategic Recommendations (3 bullets).
2. **Export**:
    - Save as `reports/[Topic]_Brief.md`.
    - Offer as PDF.

## Tags

# research #consulting #arbitrage #notebooklm #deliverables
