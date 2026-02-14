---
description: Semantic Lossless Compression for Long-Term Memory (Stolen from SimpleMem).
tags: #memory #compression #svo #simplemem #protocol-104
version: 1.0
---

# Protocol 104: Semantic Memory Compression

> **Purpose**: Convert high-volume chat logs into low-volume "Atomic Facts" to prevent context window bloat while retaining high-fidelity recall.
> **Origin**: Derived from `SimpleMem` (Semantic Structured Compression).

## The Theory of Semantic Compression

Raw text is 80% noise (grammar, politeness, repetition) and 20% signal (entities, relations, states).
We use **Subject-Verb-Object (SVO)** triples to distill the signal.

**Raw**: "I think I want to switch from using Notion to using Obsidian because Notion is too slow for me."
**Compressed**: `[User, prefers, Obsidian], [User, dislikes, Notion (reason: latency)]`

---

## 1. Compression Rules

### Rule 1: Resolution of Coreferences

* "I" -> **User**
* "You" -> **Athena**
* "It" -> **[Specific Entity]**

### Rule 2: Absolute Temporal Grounding

* "Tomorrow" -> `2026-02-14` (Calculated from session date)
* "Last week" -> `2026-02-06`

### Rule 3: Atomic Fact Extraction

Break complex sentences into independent facts.

* *Input*: "My cat Luna is sick, so I can't work on the API today."
* *Facts*:
    1. `[User.Cat, name, Luna]`
    2. `[Luna, status, Sick]`
    3. `[User, status, Unavailable (Context: Caretaking)]`
    4. `[Project.API, status, Delayed]`

### Rule 4: Noise Filtration

Discard:

* Greetings ("Hi, how are you?")
* Acknowedgments ("Okay, thanks.")
* Meta-talk ("Can you help me with...")

---

## 2. The Compression Prompt

Use this prompt in `memory_compressor.py`:

```text
You are a Semantic Compressor.
Input: A user message or conversation log.
Output: A list of ATOMIC FACTS in generic SVO logic.

Format:
- [Entity] [Relation] [Value/Entity] (Context/Time)

Constraints:
1. Use "User" and "Athena" as primary entities.
2. Resolve all relative dates to ISO 8601.
3. Ignore chit-chat.
4. If an opinion is expressed, capture the *reason* in parentheses.
```

---

## 3. Storage Schema

Store facts in `.context/memory_bank/user_profile.md` (for User) or `.context/memory_bank/project_state.md` (for Projects).

**Example Entry**:

```markdown
- [2026-02-13] User rejected Mem0 (Reason: SaaS dependency).
- [2026-02-13] User approved SimpleMem integration strategy.
```

---
**Tags**: #protocol #memory #compression #ai #svo #simplemem #context-management
