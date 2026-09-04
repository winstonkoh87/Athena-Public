---
created: 2025-12-24
last_updated: 2026-09-05
graphrag_extracted: true
---

# Protocol 171: Cross-Model Validation (Tri-Lateral Iteration Engine)

> **Created**: 24 December 2025  
> **Updated**: 5 September 2026  
> **Category**: Verification  
> **Status**: Active  

---

## Purpose

Reduce single-model blind spots by using multiple SOTA LLMs as adversarial peer reviewers. This protocol treats public agent benchmarks and arena infrastructure as empirical grounds for cross-validation.

**Extended Pattern (v2.1)**: The **Tri-Lateral Iteration Engine** formalizes a structured dialectic where:

- **Confidence ≈ Σ(convergence × independence × evidence)** — Convergence suggests confidence; evidence confirms it
- **Risk ≈ shared blind spots + Δ(divergent claims)** — Disagreement reveals territory worth investigating

> *Upgraded 28 Dec 2025*: Added Phase 2.5 (Evidence Pass) and epistemically hardened core formula. Convergence alone is not proof—models share training data.

---

## SOTA Model Reference

> **⚠️ RUNTIME VERIFICATION MANDATE (2026-09-04)**: Do NOT hardcode a static SOTA model
> table. Leaderboards turn over rapidly. A verification protocol
> that ships stale model rankings violates its own core rule.
>
> **At invocation time**: check live agentic evaluation infrastructure ([Agent Arena Leaderboard](https://arena.ai/leaderboard/agent) or [LMArena](https://lmarena.ai)), or use `search_web`
> for "Agent Arena leaderboard 2026" / "LMArena 2026". Date-stamp the result.
> Select the top 2–3 models for adversarial peer review based on the live leaderboard.
>
> **Empirical Calibration Snapshot (2 September 2026 — [Arena AI Agent Leaderboard](https://arena.ai/leaderboard/agent))**:  
> *Based on 2,188,416 real-world agentic sessions across 58 models, evaluating tool orchestration, steerability, bash recovery, and confirmed task completion.*
>
> | Tier | Models & Signals | Best Strategic Role in Athena |
> |:---|:---|:---|
> | **Tier 1: Frontier Agentic Orchestration** | • **Claude Opus 5 (High)** (#1, Net Impr: +13.74%, Steerability: 16.00%)<br>• **Claude Opus 5 (Max)** (#2, Net Impr: +11.69%, Bash Recovery: 15.50%)<br>• **Claude Fable 5 (High)** (#3, Net Impr: +10.61%)<br>• **GPT 5.6 Sol (xHigh)** (#4, Net Impr: +9.49%, Praise: 21.62%) | **Primary Synthesis & Execution Engine**: Deep structured reasoning, complex context management, resilient multi-step code generation. |
> | **Tier 2: Adversarial Audit & Peer Review** | • **Claude Opus 4.8 (High)** (#5, Net Impr: +9.22%)<br>• **Kimi K3 (Max)** (#6, Net Impr: +8.71%, #1 Confirmed Success: 16.90%)<br>• **GPT 5.5 (xHigh)** (#7, Net Impr: +7.53%, Bash Recovery: 13.54%)<br>• **Claude Sonnet 5 (High)** (#8, Net Impr: +7.51%) | **Hostile Red-Team & Verification**: Adversarial audit, cognitive bias checks, and rigorous task outcome validation. |
> | **Tier 3: Cost-Optimal & Rapid Counter-Audits** | • **GLM 5.2 (Max)** (#10, Net Impr: +6.23%, $0.48/task)<br>• **Grok 4.5** (#12, Net Impr: +6.17%)<br>• **Gemini 3.8 Flash (High)** (#15, Net Impr: +5.94%, $0.22/task, Praise: 14.78%)<br>• **DeepSeek V4 Pro (High)** (#16, Net Impr: +5.91%, $0.23/task) | **High-Frequency Pre-Flight & Fast Auditing**: High token velocity, cost-effective second-opinion passes, and sanity checks. |
>
> *This snapshot is for calibration context only — run live verification at execution time.*

---

## When to Use

| Trigger | Action |
|:---|:---|
| High-stakes decision (>$10K impact) | Mandatory cross-validation |
| Quantitative analysis (NPV, probabilities) | At least 2 models |
| Novel/unfamiliar domain | 3+ models recommended |
| Contradicts prior belief (updating priors) | External validation required |
| Irreversible / path-dependent | Validate even if <$10K |
| High fact density (dates, laws, regulations) | Mandatory—LLMs hallucinate facts |

---

## Execution (The 3-Phase Loop)

### Phase 1: Internal (Primary Model)

1. **Frame**: Build the context, hypothesis, and initial draft.
2. **Route**: User (Layer 2) inspects. If "High Stakes" are detected -> **Go to Phase 2**.

### Phase 2: Outsource (3rd Party SOTA)

1. **Select**: Choose top adversarial models from live leaderboards (e.g., **Claude Opus 5 (High)** or **GPT 5.6 Sol (xHigh)** for architectural cross-checks; **Kimi K3 (Max)** for task outcome verification; **Gemini 3.8 Flash (High)** for rapid counter-audits).
2. **Prompt**: *"Act as a hostile regulatory auditor and a pessimistic investor. Your goal is to kill this deal. List the top 3 existential risks the author ignored. Be ruthless."*
3. **Execute**: Run blind or adversarial check.

> ⚠️ **Data Handling**: Do not send PII or confidential deal terms to public sandboxes. For sensitive work, use enterprise API accounts or internal deployments.

### Phase 2.5: Evidence Pass (Required for High-Stakes)

Models validate *reasoning*, but many errors are **fact errors** (regulations, unit economics, market size). This phase grounds the analysis in primary sources.

1. **Identify** the 5 "load-bearing assumptions" — facts the conclusion depends on
2. **Verify** each with:
   - Primary source / official document
   - Direct measurement / call / quote
   - Or mark explicitly as "unknown" + run sensitivity analysis
3. **Flag** any assumption that cannot be verified — it's a risk, not a fact

### Phase 3: Integrate (Synthesis)

1. **Compare**: Identify deltas between Internal (Phase 1) and External (Phase 2).
2. **Update**: Adjust probabilities/conclusions.
3. **Finalize**: Commit to decision.

### Visual Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    TRI-LATERAL ITERATION ENGINE                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 1: GENESIS                                                   │  ║
║  │  ┌──────────────┐                                                   │  ║
║  │  │ User Query   │──────►┌──────────────────┐                        │  ║
║  │  └──────────────┘       │  Primary Model   │                        │  ║
║  │                         │ (Claude Opus 5 / │                        │  ║
║  │                         │   GPT 5.6 Sol)   │                        │  ║
║  │                         │  • Deep context  │                        │  ║
║  │                         │  • Full reasoning│                        │  ║
║  │                         └────────┬─────────┘                        │  ║
║  └──────────────────────────────────┼──────────────────────────────────┘  ║
║                                     ▼                                     ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 2: ADVERSARIAL AUDIT                                         │  ║
║  │          ┌─────────────────┐     ┌─────────────────┐                │  ║
║  │          │  Gemini 3.8 /   │     │   GPT 5.5 /     │                │  ║
║  │          │   Kimi K3 Max   │     │  Claude Fable 5 │                │  ║
║  │          │ "Red team this" │     │ "What's wrong?" │                │  ║
║  │          └────────┬────────┘     └────────┬────────┘                │  ║
║  │                   └───────────┬───────────┘                         │  ║
║  │                               ▼                                     │  ║
║  │                    ┌──────────────────────┐                         │  ║
║  │                    │  Critique Synthesis  │                         │  ║
║  │                    │  • Safety gaps       │                         │  ║
║  │                    │  • Missing nuance    │                         │  ║
║  │                    │  • Wrong assumptions │                         │  ║
║  │                    └──────────┬───────────┘                         │  ║
║  └───────────────────────────────┼─────────────────────────────────────┘  ║
║                                  ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 3: SYNTHESIS                                                 │  ║
║  │                    ┌──────────────────────┐                         │  ║
║  │                    │  Convergence Check   │                         │  ║
║  │                    └──────────┬───────────┘                         │  ║
║  │              ┌────────────────┼────────────────┐                    │  ║
║  │              ▼                ▼                ▼                    │  ║
║  │     ┌────────────────┐ ┌────────────┐ ┌────────────────┐            │  ║
║  │     │ ALL CONVERGE   │ │  DIVERGE   │ │ PARTIAL AGREE  │            │  ║
║  │     │ = High Conf.   │ │ = Edge Case│ │ = Investigate  │            │  ║
║  │     └───────┬────────┘ └─────┬──────┘ └───────┬────────┘            │  ║
║  │             │                ▼                │                     │  ║
║  │             │       ┌────────────────┐        │                     │  ║
║  │             │       │ Human Arbiter  │◄───────┘                     │  ║
║  │             │       │   (Winston)    │                              │  ║
║  │             │       └───────┬────────┘                              │  ║
║  │             └───────────────┼───────────────────┘                   │  ║
║  └─────────────────────────────┼───────────────────────────────────────┘  ║
║                                ▼                                          ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  OUTPUT: Truth ≈ Σ(convergent) + Δ(divergent to investigate)        ║  ║
║  ║  ┌─────────────────┐    ┌─────────────────┐                         ║  ║
║  ║  │ Protocol Update │    │   Case Study    │                         ║  ║
║  ║  └─────────────────┘    └─────────────────┘                         ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Quality = f(Primary Depth × Adversarial Diversity × Synthesis Discipline)
```

---

## Case Studies

### Case Study 1: BCM Due Diligence

**Primary (Opus 4.8 / Opus 5)**:

- Failure probability: 15%
- Best case probability: 20%
- Expected NPV: +$9,600

**After Cross-Validation (Gemini-3.8-Flash + Grok-4.5 / GPT-5.5)**:

- Failure probability: **40%** (+25%)
- Best case probability: **5%** (-15%)
- Expected NPV: **-$7,300** (NPV FLIPPED)

**Lesson**: Single-model optimism bias was significant. Cross-validation saved potential $16,900 decision error.

### Case Study 2: Child Aggression Response (28 Dec 2025)

**Primary (Opus 4.8 / Opus 5)**: Rated 9.5/10 response on behavioral psychology.

**After Cross-Validation (Gemini 3.8 Flash + GPT 5.5)**:

| Issue | Original | Calibrated |
|:---|:---|:---|
| Extinction framing | "Violence gets no reaction" | "Minimize attention *while ensuring safety*" |
| Restraint advice | No guardrails | "Only with training; escalate if overpowered" |
| Neurology framing | "Rule out first" | "Comprehensive assessment (medical + family + trauma)" |

**Lesson**: Response was *analytically correct* but not *implementation safe*. Standard is "safe to copy-paste by least trained reader."

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|:---|:---|
| Cherry-pick agreeing models | Use blind selection |
| Ignore disagreement | Investigate divergence |
| Only validate "risky" choices | Validate surprising confirmations too |
| Treat convergence as proof | Treat convergence as a *prior* until evidence confirms |
| Share sensitive data to public tools | Use approved/secured environments for audits |

---

## Integration

- Links to: **Protocol 159** (Verification Before Claim)
- Links to: [Protocol 75](../decision/DEC-75-synthetic-parallel-reasoning.md) (Parallel Reasoning)
- Used in: `/due-diligence`, `/ultrathink`
- Benchmark references: [docs/REFERENCES.md](../../../docs/REFERENCES.md)

---

## Tagging

# cross-model-validation #tri-lateral-iteration #agent-arena #lmarena #verification #peer-review #adversarial-ensembling #opus-5 #gpt-5.6 #fable-5 #kimi-k3 #gemini-3.8-flash #sota-models #bias-correction #hitlo
