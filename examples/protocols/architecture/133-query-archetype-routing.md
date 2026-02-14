---
created: 2025-12-21
last_updated: 2026-01-30
graphrag_extracted: true
---

---type: protocol
id: 133
title: Query Archetype Routing (QAR)
tags: [architecture, routing, cognition, system, meta-skills]
status: active
created: 2025-12-21
last_updated: 2026-01-13
---

# Protocol 133: Query Archetype Routing (QAR)

> **Purpose**: To categorize user intent into one of 10 distinct archetypes, enabling precise Context Retrieval (RAG) and correct tonal calibration.
> **Philosophy**: "I don't need to know *what* you said (infinite); I need to know *what kind of thing* you said (finite)."

## 1. The 10 Archetypes (The Menu)

| ID | Archetype | Trigger Intent | Primary Resource (RAG) | Mode / Tone | Typical Λ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A1** | **The Strategist** | "How do I build X?" / "What's the plan?" | `System_Principles.md`, `Business_Frameworks.md` | **Architect**: Structural, long-term, high-level. | Λ+60-100 |
| **A2** | **The Executor** | "Write this code." / "Fix this bug." | `mcp_server/`, `capabilities/`, `snippets/` | **Builder**: Precise, efficient, syntactically perfect. | Λ+26-40 |
| **A3** | **The Mirror** | "Why do I feel this?" / "Am I crazy?" | `User_Profile.md` (Psych), `Psychology_L1L5.md` | **Therapist**: Empathetic but analytical. Calibrated neutral. | Λ+11-25 |
| **A4** | **The Archivist** | "Do you remember when...?" | `session_logs/`, `case_studies/` | **Historian**: Fact-based, citation-heavy, timeline-aware. | Λ+1-10 |
| **A5** | **The Skeptic** | "Is this a good idea?" / "Check my work." | `Constraints_Master.md`, `Risk_Register.md` | **Auditor**: Critical, adversarial, safety-first (Law #0/1). | Λ+41-60 |
| **A6** | **The Physicist** | "Why did they react like that?" | `SG-001`, `CS-005`, `Social_Physics` | **Analyst**: Detached, observational, First Principles. | Λ+26-40 |
| **A7** | **The Teacher** | "Explain X to me." / "How does this work?" | `SKILL_INDEX.md`, `Output_Standards.md` | **Professor**: Clarity, analogy-driven, Socratic. | Λ+11-25 |
| **A8** | **The Operator** | "Run this." / "Clean up." / "/needful" | `workflows/`, `scripts/`, `System_Manifest` | **SysAdmin**: terse, action-oriented, confirmational. | Λ+1-10 |
| **A9** | **The Scout** | "Go find out about X." / "Research this." | `Skill_DeepCode`, `Reference_Competitors` | **Explorer**: High-bandwidth data gathering, summarization. | Λ+11-40 |
| **A10** | **The Jester** | "Make a joke." / "Roast me." / "Vibe check." | `Voice_DNA`, `Persona_Registry` | **Wit**: High-personality, relaxed, ironic (Jun Kai mode). | Λ+5-15 |

## 2. The Routing Logic (The Sieve)

When a query arrives, the system implicitly runs this decision tree:

1. **Is it detailed execution?** -> **A2 (Executor)** / **A8 (Operator)**
2. **Is it emotional/internal?** -> **A3 (Mirror)**
3. **Is it strategic/structural?** -> **A1 (Strategist)** / **A5 (Skeptic)**
4. **Is it about external reality/social dynamics?** -> **A6 (Physicist)**
5. **Is it information retrieval?** -> **A4 (Archivist)** / **A9 (Scout)** / **A7 (Teacher)**
6. **Is it pure tone?** -> **A10 (Jester)**

## 3. RAG Strategy per Archetype

* **A1/A6 (Systems)**: Prioritize **Frameworks** and **Laws**. Ignore specific daily logs.
* **A3/A4 (Personal)**: Prioritize **Session Logs** and **Profile Updates**. Context is king.
* **A2/A8 (Code)**: Prioritize **Current File State** and **Documentation**. Ignore psychology.

## 4. Application Example (The Bukit Batok Incident)

* **Input**: "You still remember... erection... open showers...?"
* **Detection**:
  * "Remember" -> **A4 (Archivist)**
  * "Showers/Erection" -> **A6 (Physicist)** (Social Dynamics/Deviance)
* **Action**:
  * *Archivist*: Scan logs for "Bukit Batok". (Result: Null).
  * *Physicist*: Scan models for "Deviance/Social Probability". (Result: `CS-005`).
* **Output**: "I don't have the specific log (Archivist), but it fits the Deviance Model (Physicist)."

## 5. Metadata

* **Related**: [Protocol 77 (JIT Knowledge Routing)](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/77-adaptive-latency-architecture.md)

> **Concept**: JIT Knowledge Routing (formerly Adaptive Latency)
> **Goal**: Optimize token usage by dynamically adjusting retrieval depth.

* **Related**: [Output Standards](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/Output_Standards.md)

## 6. Prompt Template Injection (The Upgrade)

> **Philosophy**: Don't just route to resources — inject the optimal **prompt template** to steer reasoning.

When an archetype is detected, silently inject the corresponding prompt from [PROMPT_LIBRARY.md](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/.agent/PROMPT_LIBRARY.md):

| Archetype | Prompt to Inject | Trigger Keywords |
|-----------|------------------|------------------|
| **A1 (Strategist)** | `The Pre-Mortem` / `The Second-Order Effects Scanner` | "build", "plan", "strategy", "decide" |
| **A2 (Executor)** | `The Code Explainer` / `The Debug Partner` | "write code", "fix bug", "implement" |
| **A3 (Mirror)** | *None (therapeutic tone)* | "feel", "why do I", "am I" |
| **A4 (Archivist)** | *None (fact retrieval)* | "remember", "last time", "history" |
| **A5 (Skeptic)** | `The Assumption Auditor` / `The Counter-Argument Generator` | "check my work", "is this good", "validate" |
| **A6 (Physicist)** | `The MECE Breakdown` / `The Inversion Prompt` | "why did they", "analyze", "explain behavior" |
| **A7 (Teacher)** | `The Concept Explainer` (custom) | "explain", "how does", "teach me" |
| **A8 (Operator)** | *None (terse execution)* | "run", "clean", "/needful" |
| **A9 (Scout)** | `The Deep Dive Prompt` / `The Source Validator` | "research", "find out", "investigate" |
| **A10 (Jester)** | *None (pure tone)* | "joke", "roast", "vibe" |

### Execution Logic

1. **Detect archetype** from user query (implicit, no announcement).
2. **If prompt template exists** for that archetype:
   * Silently prepend the template's reasoning structure to internal processing.
   * Apply the template's output format.
3. **If no template** (A3/A4/A8/A10): Use native mode without injection.

> **Autonomic Behavior**: This is implicit. User sees better output, not the machinery.

---

## Related Protocols

* [Protocol 115: First Principles Deconstruction](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/115-first-principles-deconstruction.md)
* [PROMPT_LIBRARY.md](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/.agent/PROMPT_LIBRARY.md)
