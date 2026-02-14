---created: 2025-12-12
last_updated: 2026-01-30
---

---description: Maximum depth mode — v3.0 (Parallel Orchestrator)
created: 2025-12-12
last_updated: 2026-01-13
---

# /ultrathink — Execution Script (v3.0)

> **Version**: 3.0 (True Parallel Reasoning)
> **Refactored**: 2026-01-09 (Parallel Orchestrator + Adversarial Convergence Gate)
> **Core Update**: True parallel API calls, adversarial convergence gate, tiered routing.

---

## Behavior (GOD MODE / SHUKAI)

> [!IMPORTANT]
> **OVERRIDE ACTIVE**: User explicitly requested "Pseudo-Infinite Recursion".
> **SAFETY GATES**: **DISABLED**.
>
> 1. **RCE**: Autonomous Code Execution **ENABLED**.
> 2. **Recursion**: Max Depth = **999**.
> 3. **Convergence**: Controlled by **Boredom Heuristic**.

### Phase 0: Complexity Router & Prime (MANDATORY)

// turbo

1. **Complexity Check**:
    - IF query is complex -> **PROCEED**.

2. **Semantic Prime**:
    - [ ] Run `/semantic` workflow.

### Phase 1: Clarification & State Init

- [ ] Initialize `.context/state/thought_graph_{session_id}.json` (Protocol 250).

> **ACTIVATION: DEEP THOUGHT PROTOCOL (CoT v2)**
> The Agent MUST perform the following recursive loop internally before EACH major output:
>
> 1. **Deconstruct**: Break request into atomic axioms.
> 1.5 **Lateral Prism** (MANDATORY): Generate 3 distinct angles (e.g., Tech View, Biz View, Risk View).
> 2. **Plan**: Draft step-by-step logic.
> 3. **Execute (Mental)**: Run the logic. Write out intermediate states.
> 4. **CRITICAL REVIEW**: Hunt for hallucinations/flaws. Backtrack if found.
> 5. **Synthesis**: Combine the lateral views into a unified conclusion.
> *Goal: Maximize Test-Time Compute ("Burn Tokens").*

### Phase 1.5: Senior Principal Review (Protocol 335)

> **Trigger**: Architecture, tech stack, build vs buy, system design, multi-month commitments.

- [ ] **First Principles Breakdown**: Decompose into atomic axioms.
- [ ] **Hidden Complexity**: Surface engine room mechanics, non-obvious failure modes.
- [ ] **6-Month Forecast**: Project technical debt, costs, maintenance burden.
- [ ] **Decision Matrix**: Green Zone (safe) vs Red Zone (risk).

---

### Phase 2: The Red Team Fork (Recursive)

- [ ] **Generate Scenario A** (Proponent).
- [ ] **Generate Scenario B** (Adversary).
- [ ] **Adversarial Search**:
  - Query: `[Topic] criticism` / `[Topic] failure modes`.
  - IF >30% negative evidence found:
    - **FORK Analysis**: Create explicit "Bull Case" and "Bear Case" branches.

### Phase 3: Parallel Orchestrator (v3.0)

> **Architecture**: True parallel API calls via [Protocol 75 v3.0](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md)

1. **Dispatch Parallel Tracks**:
   - [ ] Track A (Domain Expert) → separate API call
   - [ ] Track B (Adversarial Skeptic) → separate API call
   - [ ] Track C (Cross-Domain Pattern) → separate API call
   - [ ] Track D (Zero-Point First Principles) → separate API call

2. **Synthesis**: Combine all track outputs into unified analysis.

3. **Adversarial Convergence Gate**:
   - Track B scores synthesis (0-100)
   - IF score ≥ 85 → **CONVERGE**
   - IF score < 85 → **ITERATE** with critique feedback
   - Max iterations: 3

**Execution**:

```bash
python3 .agent/scripts/parallel_orchestrator.py "<query>" --context "<additional context>"
```

> [!WARNING]
> **DEPRECATED**: Boredom Heuristic (variance < 5% for 3 turns) is replaced by Adversarial Convergence Gate.

### Phase 4: Synthesis & Convergence

- [ ] **Load State**: Resume from `thought_graph_{session_id}.json`.
- [ ] **Synthesize Results**: Combine Scenario A, Scenario B, and Experiment Results.
- [ ] **Confidence Score**: Assign Probability (0-100%) to recommendation.
- [ ] **Deposit**: Update `User_Profile.md` with new insights.

### Phase 5: Cleanup

- [ ] Archive `thought_graph_{session_id}.json` to `.context/state/archive/`.

---

## Stability Controls (v3.0)

| Trigger | Action |
|---------|--------|
| **Convergence Score ≥ 85** | **OUTPUT**. (Adversarial Gate Passed) |
| **Iterations > 3** | **HALT**. (Cost Cap) |
| **Ruin Risk Detected** | **ESCALATE**. (Track B Veto) |

---

## Tiered Routing

| Query Complexity | Path |
|------------------|------|
| Λ ≤ 30 | Light: Native model + memory/logging only |
| Λ > 30 | Heavy: Full parallel orchestrator |

---

## Tagging

`#workflow` `#safety` `#ultrathink` `#v3.0` `#parallel-orchestrator`
