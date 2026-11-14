---
description: Maximum depth mode v4.2 — Isolated Multi-Track Parallel Reasoning (Swarm, API Orchestrator, or HITL)
created: 2025-12-12
last_updated: 2026-11-14
---

# /ultrathink — Execution Script (MaxMax v4.2)

> [!CAUTION]
> **ENFORCEMENT CONTRACT**: Never substitute a single-pass essay within one shared context window. High-stakes `/ultrathink` requires **independent parallel tracks** (`A Domain Expert`, `B Adversarial Skeptic / Law #1 Ruin`, `C Cross-Domain Pattern Matcher`, `D Zero-Point First Principles`) with an adversarial **Convergence Gate (`>= 85`)** before final synthesis.

## Activation Thresholds

| Query Complexity | Workflow |
|:---|:---|
| `Lambda <= 30` | Direct `context_gate` grounded answer |
| `Lambda 31-60` | `/think` — Structured internal multi-angle analysis |
| `Lambda > 60` or high-stakes irreversible | **`/ultrathink`** — Internal CoT + Mandatory Parallel Tracks |

---

## Phase 1: Prime (Context Gathering)

1. **Mandatory Exocortex Grounding**:
   ```bash
   .agent/scripts/athena-py .agent/scripts/smart_search.py "<extract keywords from query>" --limit 5 --include-personal --rerank
   ```
2. **Internal CoT Pre-Flight**: Deconstruct axioms -> 3-angle Lateral Prism -> Preliminary Plan -> Flaw Hunt -> Initial Hypothesis.
3. **Stage Context Artifact**: Write the preliminary hypothesis, retrieved search hits, and active user constraints (`Law #1 Ruin`, equity/fuse limits, calibration rules) to `.agent/state/ultrathink_context.md` *(gitignored, workspace-isolated)*.

---

## Phase 2: Execute (Parallel Tracks — Choose Execution Path)

### Option A: Antigravity Native Swarm / Isolated Subagents *(Recommended — USD 0 extra API cost)*
Spin up **isolated parallel workers** via `swarm` (`native_swarm` board) or `invoke_subagent` so each track evaluates `.agent/state/ultrathink_context.md` with fresh zero-sycophancy context:
- **Track A (`domain-expert`)**: Frameworks, math, empirical workspace precedent.
- **Track B (`adversarial-skeptic`)**: Attack premises, blind spots, Law #1 ruin probability & severity.
- **Track C (`cross-domain`)**: Isomorphic structural parallels (game theory, systems, physics, history).
- **Track D (`zero-point`)**: Question problem ontology and hidden framing traps.
Run adversarial critique until **Convergence Score >= 85** (max 3 rounds) before `@coordinator` synthesizes.

### Option B: Automated External API Orchestrator (`parallel_orchestrator.py`)
```bash
.agent/scripts/athena-py .agent/scripts/parallel_orchestrator.py "<the user's query>" \
  --context-file .agent/state/ultrathink_context.md \
  --output .context/state/ultrathink/ultrathink_$(date +%Y%m%d_%H%M%S).md \
  --json
```
Read the generated output file completely before synthesizing.

### Option C: HITL Manual Sandbox *(Zero API / Manual UI)*
Output the 4 structured track prompts + staged context inside a fenced ````text` block for the user to run externally and paste back.

---

## Phase 3: Deposit (Synthesis & Persistence)

1. Present clean synthesis: **Convergence Score & iterations**, **Track agreements**, **Resolved conflicts**, **Track B Ruin/Risk integration**, and **Final decision/recommendation with explicit confidence & falsifiers**.
2. **Quicksave**:
   ```bash
   .agent/scripts/athena-py .agent/scripts/quicksave.py --stdin <<'EOF'
   Executed /ultrathink on: <brief query summary>. Convergence score: <score>. Key insight: <one-liner>.
   EOF
   ```
3. **Auto-Document**: File novel reusable insights as case studies or protocols per `Core_Identity` Auto-Documentation rules.

## Stability Controls

| Trigger | Action |
|:---|:---|
| `Convergence Score >= 85` | **OUTPUT** (Adversarial Gate Passed) |
| `Iterations > 3` | **HALT** (Convergence cap reached; surface residual disagreement) |
| **Law #1 Ruin Risk Detected** | **ESCALATE IMMEDIATELY** (Track B Veto) |
| **Orchestrator script fails** | **REPORT VERBATIM** (never fabricate/simulate track outputs) |

`#workflow` `#safety` `#ultrathink` `#v4.2` `#parallel-orchestrator`
