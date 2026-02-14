---

created: 2026-01-16
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-16
last_updated: 2026-01-16
---

# Protocol 080: The Signal Filter Paradox (Context Compression)

> **Origin**: Derived from "The Compression Paradox" (2026 findings on Mistral/LLM attention mechanisms).
> **Principle**: `Information Density > Information Volume`.

## The Paradox

Adding more context **decreases** reasoning accuracy.

- **Full Context (25k tokens)**: ~30% Accuracy (Noise dilution).
- **Compressed Context (5k tokens)**: ~97% Accuracy (Signal concentration).

## The Mechanism: "Context Noise"

LLM Attention heads are not infinite. When you flood the context window with "related but non-essential" data, you dilute the attention weights assigned to the **Critical Instruction**.

- **Dilution**: The model "reads" everything but "attends" to nothing specific.
- **Compression**: Forcing data through a compression filter (summarization/extraction) acts as a **High-Pass Filter**, removing the low-frequency noise and leaving only the high-frequency signal.

## Operational Directives (Direct Application)

### 1. The "20% Rule"

If you are passing >5,000 tokens of context, you must ask: **"Can this be compressed by 80% without losing the 'Killer Fact'?"**

- **Action**: Do not dump 5 files. Dump the *summaries* of 5 files + the *exact code snippet* of the 1 relevant function.

### 2. The "Pre-Flight Compression" Step

Before asking a complex reasoning question, run a `summarize` pass on the context data.

- **Bad**: `read_file(all_logs.txt)` -> "Analyze this."
- **Good**: `read_file(all_logs.txt)` -> "Extract only lines with ERROR or CRITICAL" -> "Analyze these specific lines."

### 3. "Signal Density" as a Metric

Evaluate prompts not by length, but by **Density**.

- **Low Density**: "Here is the entire codebase, help me fix the bug." (Lazy).
- **High Density**: "Here is the stack trace, the specific function `foo()`, and the `User` class definition. Fix the `NullPointer`." (Bionic).

## Strategic Implication

We are moving from **"Big Data" (RAG)** to **"Smart Data" (Compressed RAG)**.
The Bionic Agent (Athena/Antigravity) must act as the **Compression Engine** for the LLM, ensuring only 99% pure signal enters the inference window.
