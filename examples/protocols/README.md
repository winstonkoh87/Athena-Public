# Athena Protocols

> [!NOTE]
> **These are reference implementations from a production AI-agent system (1,079+ sessions).**
>
> Use them to understand the *pattern* — not as prescriptions. Your protocols will reflect your own context, domain, and decision history.
>
> See [Creating Your Own Protocols](#creating-new-protocols) to build yours.

Protocols are reusable thinking patterns that standardize how an AI agent reasons about specific domains. **200 protocols across 17 categories.**

## Featured Protocols

| ID | Name | Category | Purpose |
|----|------|----------|---------|
| **77** | Adaptive Latency | Architecture | Scale reasoning depth to query complexity |
| **96** | Latency Indicator | Architecture | Append [Λ+XX] to show cognitive effort |
| **130** | Vibe Coding | Workflow | Iterative UI development by "feel" |
| **133** | Query Archetype Routing | Architecture | Route queries to optimal processing paths |
| **158** | Entity Lookup First | Architecture | Always lookup entities before analyzing |
| **159** | Verification Before Claim | Architecture | Verify facts before stating them |
| **168** | Context-Driven Development | Engineering | Let context guide implementation |
| **200** | Feature Context Persistence | Architecture | Track features across sessions |
| **202** | Recovery Patterns | Architecture | Graceful degradation strategies |
| **240** | Context Engineering | Engineering | Manage context window efficiently |
| **408** | Autonomous Contribution Engine | Workflow | Transform user insights into contributions |
| **416** | Agent Swarm | Workflow | Parallel multi-agent orchestration |

## Categories

### 🏗️ Architecture (56 protocols)

System design, token management, context handling, state machines.

[Browse Architecture Protocols →](architecture/)

### ⚙️ Engineering (21 protocols)

Code patterns, TDD, git workflows, UI development, infrastructure.

[Browse Engineering Protocols →](engineering/)

### 🧭 Decision (30 protocols)

Decision frameworks, reasoning patterns, multi-criteria analysis, risk assessment.

[Browse Decision Protocols →](decision/)

### 📋 Workflow (22 protocols)

Session management, automation, agentic loops, multi-agent coordination.

[Browse Workflow Protocols →](workflow/)

### 🧠 Meta (12 protocols)

Protocols about protocols — self-improvement, auditing, optimization.

[Browse Meta Protocols →](meta/)

### 🔍 Pattern Detection (10 protocols)

Analytical heuristics — BS detection, form-substance gaps, depth analysis.

[Browse Pattern Detection Protocols →](pattern-detection/)

### 🎯 Strategy (9 protocols)

Competitive positioning, min-max optimization, ecosystem analysis.

[Browse Strategy Protocols →](strategy/)

### 💼 Business (8 protocols)

Unit economics, flywheel architecture, first-principles analysis.

[Browse Business Protocols →](business/)

### 🛡️ Safety (8 protocols)

Risk management, circuit breakers, governance, recovery architecture.

[Browse Safety Protocols →](safety/)

### 💻 Coding (5 protocols)

Spec-driven development, semantic search standards, structured decoding.

[Browse Coding Protocols →](coding/)

### 🔬 Research (5 protocols)

Deep investigation, cyborg methodology, agentic absorption.

[Browse Research Protocols →](research/)

### 🧪 Verification (3 protocols)

Testing, claim atomization, cross-model validation.

[Browse Verification Protocols →](verification/)

### 🧩 Reasoning (3 protocols)

Deep thinking, re-reading strategies, senior-principal review.

[Browse Reasoning Protocols →](reasoning/)

### 💾 Memory (3 protocols)

Semantic compression, graph memory architecture, compaction.

[Browse Memory Protocols →](memory/)

### 🎨 Design (2 protocols)

UI/UX patterns — liquid glass physics, mockup flow.

[Browse Design Protocols →](design/)

### 🎭 Creation (2 protocols)

Creative methodology — metaphorical design, latent cluster activation.

[Browse Creation Protocols →](creation/)

### ✅ Quality (1 protocol)

Code review standards — red team review.

[Browse Quality Protocols →](quality/)

## Protocol Format

Each protocol follows this structure:

```markdown
---
id: 77
name: Adaptive Latency Architecture
category: architecture
status: active
---

# Protocol 77: Adaptive Latency Architecture

## Purpose
[What problem this solves]

## When to Use
[Trigger conditions]

## Implementation
[Step-by-step process]

## Examples
[Concrete usage examples]
```

## Creating New Protocols

Use the [protocol template](../templates/protocol_template.md) to create new protocols.

Assign the next available ID and add an entry to this index.
