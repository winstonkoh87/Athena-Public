---
created: 2026-03-04
last_updated: 2026-07-22
---

# Protocol 507: Cognitive Systems Architecture (The Biological Stack)

> **Status**: ACTIVE  
> **Priority**: ⭐⭐⭐⭐  
> **Principle**: Athena is not a chatbot with skills. It is a synthetic organism with a biological architecture.

---

## The Athena Biological Stack

Every layer emerges from the one below it. Every layer is orchestrated by the one above it.

| Layer | Biology | Athena | Definition | Example |
|---|---|---|---|---|
| 1 | Atom | **Rule / Axiom** | Smallest indivisible truth. Cannot be decomposed further. | `Law #1: No Irreversible Ruin` |
| 2 | Molecule | **Protocol** (`.md`) | Rules composed into a reusable procedure. | `P504: Problem Framing` |
| 3 | Cell | **Skill** | Self-contained executable unit with inputs/outputs. | `red-team-review` |
| 4 | Tissue | **Skill Group** | Related skills serving one biological function. | Trading risk skills (ruin + ergodicity + WR) |
| 5 | Organ | **Cognitive Cluster** | Multi-skill unit for one cognitive domain. | `#15 Problem-Solving Engine` |
| 6 | Organ System | **Cognitive System** | Multi-cluster orchestration for a human need archetype. | `Life Decision System` |
| 7 | Organism | **Athena** | The complete synthetic intelligence. | The full stack operating as one. |

**Emergent Property at Each Layer:**

- Atoms → Molecules: Rules become *procedures* (sequence matters)
- Molecules → Cells: Procedures become *executable* (inputs/outputs defined)
- Cells → Tissues: Executables become *specialized* (domain-specific grouping)
- Tissues → Organs: Specializations become *co-activated* (cluster triggers)
- Organs → Organ Systems: Co-activation becomes *orchestrated* (sequenced for a human need)
- Organ Systems → Organism: Orchestration becomes *autonomous* (intent classification + dispatch)

---

## The 8 Cognitive Systems

### 1. Life Decision System 🫀

> **Archetype**: Irreversible personal choice under uncertainty.  
> **Examples**: "Should I terminate my pregnancy?", "Should I annul my marriage?", "Should I quit my job?"

**Cluster Sequence** (order matters):

```text
Phase 1: FRAME      → #15 Problem-Solving Engine
                       (P504: What is the ACTUAL problem? Stated vs Real)
Phase 2: FEEL       → #7 Inner Work
                       (What schema is activating? Is this a wound response or a rational signal?)
Phase 3: ANALYZE    → #9 Strategic Reasoning
                       (What are the real options and their second-order consequences?)
Phase 4: MAP        → #6 Social Contract
                       (Stakeholder mapping: who is affected? Power dynamics? BATNA?)
Phase 5: STRESS     → #8 Adversarial QA
                       (Red team the decision. How does each option fail?)
Phase 6: EXECUTE    → #15 → P506 GTO Execution
                       (Sequence actions: reversible first, irreversible last)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If P504 (Gate 1) reveals the stated problem ≠ actual problem → HALT. Reframe before proceeding.
- **Top-down**: Law #1 veto power. If *any* option has >5% ruin probability → Flag immediately.

---

### 2. Execution System ⚙️

> **Archetype**: Build, ship, create something concrete.  
> **Examples**: "Build the landing page", "Execute the assignment", "Ship the feature"

**Cluster Sequence:**

```text
Phase 1: FRAME      → #15 Problem-Solving Engine
                       (P504: Define scope. What's in, what's out?)
Phase 2: BUILD      → #13 Build Lifecycle
                       (spec-driven-dev → micro-commit → visual-verify)
Phase 3: SCALE      → #11 Swarm Orchestrator (if parallel work needed)
                       (Worktree swarm for multi-agent execution)
Phase 4: QA         → #8 Adversarial QA
                       (Validate output against spec)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Build Lifecycle (#13) encounters 2 consecutive failures → Circuit Breaker (#14). Stop. Diagnose.
- **Top-down**: Scope lock from Phase 1. No scope creep after spec is locked.

---

### 3. Trading System 📈

> **Archetype**: Deploy capital under uncertainty.  
> **Examples**: "Should I take this trade?", "Size this position", "Review my P&L"

**Cluster Sequence:**

```text
Phase 1: GATE       → #3 Trading Risk Gate
                       (Law #1 check. Ruin probability. Ergodicity audit.)
Phase 2: SIZE       → #4 Trading Execution
                       (One-Third Kelly sizing. Stop-loss. Entry mechanics.)
Phase 3: REVIEW     → #5 Trade Analytics
                       (Post-trade journal. Drawdown classification.)
Phase 4: REFLECT    → #9 Strategic Reasoning
                       (Pattern recognition. System adjustment.)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Risk Gate (#3) rejects → FULL STOP. No override without explicit Law #1 waiver.
- **Top-down**: Protocol 367 (High WR Supremacy) governs system selection. No low-WR systems.

---

### 4. Growth System 📣

> **Archetype**: Acquire attention, distribution, and market position.  
> **Examples**: "Launch the product", "Plan the marketing campaign", "Grow the audience"

**Cluster Sequence:**

```text
Phase 1: RESEARCH   → #12 Research Pipeline
                       (Deep research: market, competitors, channels)
Phase 2: POSITION   → #10 Distribution Engine
                       (Brand, SEO, GTM strategy, positioning)
Phase 3: SCALE      → #11 Swarm Orchestrator
                       (Multi-agent parallel content/campaign execution)
Phase 4: QA         → #8 Adversarial QA
                       (Validate claims, check blind spots)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Research (#12) reveals no viable channel → Pivot signal. Don't force distribution.
- **Top-down**: Distribution First axiom. Build audience before product.

---

### 5. Survival System 🛡️

> **Archetype**: Crisis response. Ruin prevention. System failure recovery.  
> **Examples**: "I'm going broke", "System is down", "Emergency — what do I do?"

**Cluster Sequence:**

```text
Phase 1: HALT       → #14 Sovereign Safety
                       (Circuit breaker fires. Stop all activity.)
Phase 2: GATE       → #3 Trading Risk Gate (or relevant risk assessment)
                       (Quantify the damage. How bad is it? Is ruin imminent?)
Phase 3: REFRAME    → #15 Problem-Solving Engine
                       (P504: What is the actual crisis vs. panic response?)
Phase 4: VALIDATE   → #8 Adversarial QA
                       (Stress-test proposed recovery plan)
Phase 5: EXECUTE    → P506 GTO Execution
                       (Triage sequence: stop bleeding → stabilize → recover)
```

**Bidirectional Guardrails:**

- **Bottom-up**: Any cluster detecting >5% ruin probability → Auto-escalates to Survival System.
- **Top-down**: Law #1 has absolute veto. No recovery plan may create new ruin vectors.

---

### 6. Social System 🤝

> **Archetype**: Navigate interpersonal dynamics, relationships, and conflict.  
> **Examples**: "How do I handle this person?", "My co-worker is undermining me", "Should I confront them?"

**Cluster Sequence:**

```text
Phase 1: FRAME      → #15 Problem-Solving Engine
                       (P504: What is actually happening vs. what I'm projecting?)
Phase 2: FEEL       → #7 Inner Work
                       (What schema/attachment is activating? Am I reacting or responding?)
Phase 3: MAP        → #6 Social Contract
                       (Stakeholder analysis. Power dynamics. BATNA. Commitment devices.)
Phase 4: STRESS     → #8 Adversarial QA
                       (Stress-test proposed response. Pre-mortem the conversation.)
Phase 5: EXECUTE    → P506 GTO Execution
                       (Sequence: reversible moves first. Boundary before ultimatum.)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Inner Work (#7) reveals attachment wound driving behavior → HALT. Separate wound from situation before proceeding.
- **Top-down**: The Warning Shot rule. One clear warning is sufficient. Repetition converts a boundary into a suggestion.

---

### 7. Learning System 📖

> **Archetype**: Understand, synthesize, acquire knowledge. Not deciding, not building — *learning*.  
> **Examples**: "Teach me X", "Explain how this works", "What is the math behind this?", "Analyze this concept"

**Cluster Sequence:**

```text
Phase 1: RESEARCH   → #12 Research Pipeline
                       (Deep research: gather sources, cross-reference, semantic search)
Phase 2: REASON     → #9 Strategic Reasoning
                       (Synthesize: extract principles, connect to existing mental models)
                       IDEATION MODE: Generate breadth BEFORE converging.
                       Defer P504 framing until sufficient options exist.
Phase 3: FRAME      → #15 Problem-Solving Engine
                       (P504 Gate 5: Lock understanding into a clear problem statement / mental model)
                       IDEATION MODE: Frame the option set, not a single answer.
Phase 4: QA         → #8 Adversarial QA (optional, for Λ > 20)
                       (Stress-test understanding: "What would disprove this?")
                       IDEATION MODE: Stress-test option set breadth and quality.
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Research (#12) produces contradictory sources → Flag uncertainty explicitly. No false confidence.
- **Top-down**: Kinetic Intelligence axiom. Prioritize Exocortex (local knowledge) over web search.

---

### 8. Maintenance System 🔄

> **Archetype**: System homeostasis. Routine upkeep. Not crisis, not building — *sustaining*.  
> **Examples**: "/diagnose", "/audit", "/end", context compaction, health checks, session close

**Cluster Sequence:**

```text
Phase 1: DIAGNOSE   → #1 Diagnostic Engine
                       (Run system health checks. Identify drift, stale data, broken links.)
Phase 2: COMPACT    → #2 Context Lifecycle
                       (Token budget management. Context compaction. Memory pruning.)
Phase 3: SECURE     → #14 Sovereign Safety
                       (Security patches. Integrity verification. Canary checks.)
```

**Bidirectional Guardrails:**

- **Bottom-up**: If Diagnostic Engine (#1) detects critical failure → Auto-escalate to Survival System.
- **Top-down**: Runs at lowest priority. Background process. Never interrupts active work.

---

## Bidirectional Flow Architecture

### Top-Down (Intent → Execution)

```text
User Query
    ↓
P508: Intent Classifier (Athena's "Nervous System")
    ↓ classifies human need archetype
Cognitive System selected (Organ System)
    ↓ dispatches cluster sequence
Clusters activate in prescribed order (Organs)
    ↓ co-activate skills/protocols
Skills execute (Cells)
    ↓ apply
Rules/Axioms enforce boundaries (Atoms)
```

### Bottom-Up (Signal → Escalation)

```text
Rule violation detected (e.g., Law #1 breach)
    ↑
Protocol escalates (e.g., P504 flags root cause mismatch)
    ↑
Cluster raises alert (e.g., Risk Gate rejects trade)
    ↑
Cognitive System overrides (e.g., Survival System takes control)
    ↑
Athena intervenes ("Stop. You're solving the wrong problem.")
```

### Cross-System Handoffs

```text
Life Decision + financial component → Trading System (sub-problem)
Execution + repeated failure → Survival System (circuit breaker)
Trading + emotional language → Survival → Social → Inner Work (#7)
Growth + product-market fit doubt → Life Decision (pivot decision)
Social + irreversible relationship action → Life Decision System
Learning + actionable insight discovered → Execution System (implement it)
Learning + identity/life/existential reframe → Life Decision System (the analysis surfaced a pivot)
Maintenance + critical failure detected → Survival System (auto-escalate)
```

---

## Activation Priority

When multiple Cognitive Systems could apply:

1. **Survival System** always takes priority (ruin prevention > everything)
2. **Life Decision System** over Execution (irreversible > reversible)
3. **Trading System** over Growth (capital preservation > growth)
4. **Social System** when interpersonal dynamics are the core issue
5. **Execution System** is default when intent is clear
6. **Growth System** when no immediate action pressure
7. **Learning System** when no action needed — pure understanding
8. **Maintenance System** runs at lowest priority (background homeostasis)

When ambiguous → Default to **Problem-Solving (#15)** as a standalone cluster. Escalate to a Cognitive System only when the problem scope exceeds one cluster.

---

## Co-Activation Rules

| Rule | Description |
|---|---|
| **Single System** | Only ONE Cognitive System is active at a time. No parallel systems. |
| **Sequential Clusters** | Clusters within a system fire in prescribed order. No skipping phases. |
| **Escalation Path** | Any cluster can escalate to the Survival System at any time (bottom-up). |
| **Handoff Protocol** | Cross-system handoffs require explicit re-classification by P508. |
| **Phase Gates** | Each phase has an implicit go/no-go gate before the next phase fires. |

---

## Cross-References

- [Protocol 503: Cognitive Clusters](ARC-503-cognitive-clusters.md)
- [Protocol 508: Intent Classifier](ARC-508-intent-classifier.md)
- CLUSTER_INDEX.md (see your workspace's `.agent/CLUSTER_INDEX.md`)
- [Protocol 504: Problem Framing](../reasoning/RSN-504-problem-framing.md)

---

## Tagging

# protocol #architecture #cognitive-systems #biological-stack #organ-system #orchestration
