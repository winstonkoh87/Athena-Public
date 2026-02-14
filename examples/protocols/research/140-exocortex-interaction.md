# Protocol 140: Exocortex Interaction

> **Role**: Knowledge Retrieval & Integration System  
> **Source**: DBPedia Long Abstracts (Flash-RAG)  
> **Latency**: Zero-Latency (Local SQLite FTS)

## 1. Core Philosophy: "Flash-RAG"

The Exocortex is **not** a general browsing tool. It is a **deterministic, local knowledge extension**.

- **Boot Fast**: No external API calls for basic facts.
- **Load Later**: Only fetch full articles if the abstract is insufficient.
- **Citation**: Every inserted fact **must** be traceable to its source URL.
- **Target**: Solves **Quadrant 4 (Unknown Unknowns)** by linking across domains.

## 2. Modes of Interaction

### A. The "Lookup" (Fact-Check)

*Intent: Quick verification of a specific entity or concept.*

- **Command**: `python3 .agent/scripts/exocortex.py search "Term"`
- **Output**: Top 3-5 matches with summaries.
- **Integration**: Insert simple facts directly into the conversation or document.

### B. The "Synthesis" (Deep Dive)

*Intent: Generating a grounded report or comparing concepts.*

- **Process**:
    1. **Extract**: Identify key terms.
    2. **Query**: Search Exocortex for each term.
    3. **Filter (The 3-Sigma Rule)**: Apply the **0.3% Heuristic**.
        - *Principle*: Trillions of data points exist. Only the top **0.3% (>3SD)** is relevant to Athena.
        - *Action*: Discard generic noise. Retain only **high-signal**, **novel**, or **critical** facts.
    4. **Synthesize**: Combine into a cohesive narrative.
    5. **Rank**: Apply MCDA if comparing options (see Section 4).

## 3. Citation Standard (APA 7 Extended)

Athena treats the Exocortex as a verified database.

**Format**:
> Statement of fact [(Source Title, Year)](URL).

**Example**:
> The **Exocortex** framework allows for offloading cognitive processes to external systems [(Exocortex, 2022)](https://en.wikipedia.org/wiki/Exocortex).

**Rules**:

1. **Always Link**: The URL is the source of truth.
2. **Date**: Use "n.d." if the specific revision date is unknown, or the dump year (2022) for static data.
3. **Verbosity**: Keep citations minimal to avoid clutter, but present.

## 4. Ranking Framework (MCDA & Pairwise)

When the user asks to "rank" or "compare" items found in the Exocortex (e.g., "Best Python Frameworks"), strict evaluation matrices are used.

### Multi-Criteria Decision Analysis (MCDA)

*Also known as: Believability Weighted Decision Making*

Assign weights to critical dimensions. **"User Relevance" is always the highest weighted factor (50%).**

| Framework | Popularity (Abstract) | Performance (Inferred) | **User Relevance** | **Score** |
| :--- | :--- | :--- | :--- | :--- |
| **Django** | High (9) | Medium (7) | **Low (Overkill)** | **6.5** |
| **FastAPI** | High (9) | High (9) | **High (Speed)** | **9.2** |
| **Flask** | High (8) | Medium (6) | **Medium** | **7.5** |

*Methodology*:

1. **Scan Abstracts**: Search for keywords like "popular", "fast", "standard", "legacy".
2. **Qualitative Scoring**: Convert keywords to 1-10 scores (e.g., "fast" = 8, "high performance" = 10).
3. **Compute**: Weighted sum.

### Pairwise Comparison

If $N < 5$, use a tournament sort.

- **Django vs FastAPI**: Django wins on "completeness", FastAPI wins on "speed".
- **Selection**: Choose based on User Context (Constraint: "Speed" vs "Time to Market").

## 5. System Prompts & Triggers

- **Trigger**: User asks "What is X?", "Compare X and Y", "Fact check this".
- **Action**: Auto-run `exocortex.py search`.
- **Response**: "According to the Exocortex..."

---
*Compliance: High. This protocol governs all static knowledge usage.*
