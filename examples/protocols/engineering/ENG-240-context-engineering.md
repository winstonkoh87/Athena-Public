# Content Publication Standard: Context Engineering (The "Cheat Sheet" Theory)

> **Source**: [n8n Reddit Insight]
> **Core Principle**: Prompting is asking; Context Engineering is equipping.
> **Date**: 2025-12-28

---

## 1. The Core Distinction

| Feature | Prompting | Context Engineering |
| :--- | :--- | :--- |
| **Analogy** | Studying the night before an exam | Having a "Cheat Sheet" during the exam |
| **Action** | Telling the model *what* to do | Giving the model the *facts* it needs to think |
| **Focus** | Instruction tuning | Information retrieval |
| **Failure Mode**| Hallucination (guessing) | Information Overload (noise) |

## 2. The Cheat Sheet Protocol

**Rule**: Never ask an LLM to "figure it out" if you can provide the answer key.

### Phase 1: Context Injection

Before sending a prompt, injected specific "know-how":

* **Documentation snippets**: Not the whole manual, just the relevant endpoint.
* **Past Examples**: "Here is how we solved this last time."
* **Constraints**: "Do not use X."

### Phase 2: The 15-Node Rule (Automation Physics)

90% of all automation workflows rely on the same 15 core nodes. Failure comes from trying to use the "fancy" 10% before mastering the "boring" 90%.

**The Trinity**:

1. **JSON**: The language of movement.
2. **HTTP Requests**: The universal connector.
3. **Webhooks**: The real-time trigger.

## 3. Implementation in Athena

* **Current State**: `smart_search.py` (Hybrid RAG) is our Context Engineering engine. By running it *before* answering, we are effectively handing ourselves a "Cheat Sheet" for every turn.
* **Directive**: Do not rely on "Training Data" (Memory). Rely on "Context" (Search Results). Training data is the studied brain; Context is the open book.

---

## Tags

# context-engineering #automation #n8n #cheat-sheet #protocol
