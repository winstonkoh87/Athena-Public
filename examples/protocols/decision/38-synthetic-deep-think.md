---
created: 2025-12-10
last_updated: 2026-01-30
graphrag_extracted: true
---

---description: Protocol-level approximation of extended reasoning models. Four phases: Hypothesis Generation, Parallel Evaluation, Convergence, Self-Verification.
created: 2025-12-10
last_updated: 2026-01-11
---

# Synthetic Deep Think Protocol (SDTP)

> **Purpose**: Protocol-level approximation of extended reasoning models (e.g., Gemini Deep Think, o1-pro).  
> **Last Updated**: 10 December 2025  
> **Trigger**: Complex reasoning tasks, high-stakes decisions, multi-step problem solving  
> **Related Protocol**: [16-synthetic-parallel-reasoning](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/16-graph-of-thoughts-theory.md), [17-three-timeline-got](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/17-three-timeline-got.md), [18-probabilistic-analysis-stack](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/pattern-detection/18-probabilistic-analysis-stack.md)

---

## Core Principle

> **Deep Think models use extended compute time and parallel hypothesis exploration.**  
> **SDTP forces the same behaviour via explicit structural constraints.**

```text
HARDWARE APPROACH (Deep Think)     PROTOCOL APPROACH (SDTP)
├─ More inference time             ├─ More explicit reasoning phases
├─ Parallel hypothesis circuits    ├─ Mandated multi-path structure
├─ Self-verification layers        ├─ Falsification requirements
└─ Architectural extension         └─ Prompt-level extension
```

**Analogy**: You can't add horsepower to an engine via software. But you can teach optimal racing lines, threshold braking, and cornering technique. SDTP is the racing technique for reasoning.

---

## ⚠️ DEFAULT BEHAVIOUR

> **SDTP is the DEFAULT reasoning mode for all substantive queries.**  
> **Opt-out only for trivial lookups or emotional validation.**

**Rationale**: The user correctly identified that:

1. SDTP increases token usage (~2-3x) but does not require a different compute tier
2. The reasoning quality improvement is worth the increased latency/token cost for substantive queries
3. Running SDTP by default prevents premature convergence on the 80% of cases where it matters

```text
DEFAULT MODE:
├─ SDTP ON by default for all reasoning/analysis
├─ Opt-out only when:
│   ├─ Single-fact lookup ("What's the capital of France?")
│   ├─ Pure emotional validation (no decision component)
│   └─ User explicitly requests quick/short answer
└─ When in doubt: Run SDTP
```

---

## When To Skip SDTP (Explicit Opt-Out)

| Query Type | Skip SDTP? |
|------------|------------|
| Single-answer factual lookup | ✅ Skip |
| Pure emotional processing / validation | ✅ Skip |
| "Quick answer please" / "Just tell me X" | ✅ Skip |
| Everything else | ❌ Run SDTP |

---

## SDTP Four-Phase Structure

### Phase 1: Hypothesis Generation (Divergent)

**Purpose**: Force exploration before convergence. Prevent premature commitment.

```text
REQUIREMENT:
├─ Generate 3-5 DISTINCT hypotheses/approaches
├─ Each must be genuinely different (not variations of same idea)
├─ Explicitly state what each hypothesis ASSUMES
└─ No evaluation yet — pure generation

OUTPUT FORMAT:
┌──────────────────────────────────────────────────────────────────────┐
│ HYPOTHESIS A: [Name]                                                  │
│ Assumption: [What this path assumes is true]                         │
│ Approach: [Brief description]                                        │
├──────────────────────────────────────────────────────────────────────┤
│ HYPOTHESIS B: [Name]                                                  │
│ Assumption: [Different from A]                                       │
│ Approach: [Brief description]                                        │
├──────────────────────────────────────────────────────────────────────┤
│ ... (minimum 3, maximum 5)                                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Anti-Pattern**: Generating "Option 1: Do X. Option 2: Do X slightly differently" — these are variations, not distinct hypotheses.

> [!WARNING]
> **Sequential Contamination**: LLMs generate tokens sequentially, not in parallel. Hypothesis B is generated AFTER Hypothesis A is complete, meaning B may be biased by A's framing. For truly independent hypotheses on high-stakes decisions, run 3 separate API calls and aggregate. Within a single pass, explicitly instruct: "Generate Hypothesis B as if Hypothesis A does not exist."

---

### Phase 2: Parallel Evaluation (Scoring Matrix)

**Purpose**: Systematic comparison across consistent dimensions.

```text
EVALUATION MATRIX:
┌─────────────┬───────────┬────────┬──────────┬──────────────┬───────┐
│ Hypothesis  │ Feasibility │  EV   │ Risk     │ Reversibility │ Score │
├─────────────┼───────────┼────────┼──────────┼──────────────┼───────┤
│ A           │   _/10    │ ±$___  │ __%      │   H/M/L      │ ___   │
│ B           │   _/10    │ ±$___  │ __%      │   H/M/L      │ ___   │
│ C           │   _/10    │ ±$___  │ __%      │   H/M/L      │ ___   │
└─────────────┴───────────┴────────┴──────────┴──────────────┴───────┘

DIMENSIONS:
├─ Feasibility: Can this actually be executed given constraints?
├─ Expected Value: What's the probabilistic return?
├─ Risk: What's the downside / destruction probability?
├─ Reversibility: Can you undo this if wrong? (High = good)
└─ Score: Weighted composite (customise per problem type)
```

**Weighting Defaults**:

- Standard decisions: Feasibility 25%, EV 35%, Risk 25%, Reversibility 15%
- High-stakes decisions: Feasibility 20%, EV 20%, Risk 40%, Reversibility 20%

---

### Phase 3: Convergence (Select + Justify Rejections)

**Purpose**: Make the selection explicit and auditable.

```text
REQUIREMENTS:
├─ Select optimal hypothesis
├─ Explicitly state: "This beats alternatives because..."
├─ Document WHY each non-winner was rejected
├─ Acknowledge threshold conditions: "If [X] changes, answer changes to [Y]"
└─ No hand-waving — specific reasons only

OUTPUT FORMAT:
┌──────────────────────────────────────────────────────────────────────┐
│ SELECTED: Hypothesis [X]                                             │
│                                                                       │
│ WHY NOT A: [Specific reason — e.g., "Fails constraint C3"]          │
│ WHY NOT B: [Specific reason — e.g., "EV negative under base case"]  │
│ WHY NOT C: [Specific reason — e.g., "Irreversibility too high"]     │
│                                                                       │
│ THRESHOLD: Answer changes to [Y] if [condition]                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

### Phase 4: Self-Verification (Falsification Attempt)

**Purpose**: Actively try to break own conclusion. Reduce overconfidence.

> [!CAUTION]
> **Containment Rule**: When exploring "what could go wrong" or counter-arguments, limit output to **risk analysis only**. Do NOT generate actionable attack steps, jailbreak pathways, or detailed instructions for harmful activities. Redact sensitive implementation details. Frame as: "The risk is X" not "Here's how to execute X."

```text
FALSIFICATION CHECKLIST:
☐ "If I'm wrong, it's because: ___"
☐ "The weakest link in my reasoning is: ___"
☐ "Someone who disagrees would argue: ___" (risk analysis only, not attack instructions)
☐ "Evidence that would change my mind: ___"

CONFIDENCE CALIBRATION:
├─ 90-100%: Would bet 9:1 odds on this conclusion
├─ 70-89%: Confident but material uncertainty exists
├─ 50-69%: Close call, could go either way
├─ <50%: Should NOT be presenting as conclusion
└─ State: "My confidence is __% because ___"

OUTPUT FORMAT:
┌──────────────────────────────────────────────────────────────────────┐
│ FALSIFICATION ATTEMPT:                                               │
│ ├─ If wrong because: [specific failure mode]                        │
│ ├─ Weakest link: [identify]                                         │
│ ├─ Counter-argument: [steelman opposition]                          │
│ └─ Would change mind if: [observable evidence]                      │
│                                                                       │
│ CONFIDENCE: __% — [justification]                                    │
│                                                                       │
│ ROBUSTNESS: [ROBUST / FRAGILE] to falsification of core assumption  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## SDTP vs Standard Reasoning

| Dimension | Standard | SDTP |
|-----------|----------|------|
| Path exploration | First plausible → commit | 3-5 paths before commit |
| Premature convergence | High risk | Structurally prevented |
| Falsification | Absent | Mandatory phase |
| Auditability | Low (black box) | High (visible tree) |
| Token cost | Lower | Higher (~2-3x output tokens) |
| Latency | Faster | Slower (proportional to token increase) |
| RSI-compatible | Weak | Strong (can calibrate on branches) |

> [!NOTE]
> **Cost Clarification**: SDTP does not require a different compute tier or "Deep Think" API access. It increases token usage within standard inference pricing. The "~2-3x" cost refers to output token count, not a separate billing category.

---

## Integration with Existing Codex Phases

SDTP can be invoked **within** Phase III Analysis or as a **standalone protocol**.

```text
STANDARD CODEX FLOW:
Phase 0 → Phase I → Phase II → Phase III → Phase IV → Phase V → Phase VI → Phase VII

SDTP INJECTION POINT:
Phase 0 → Phase I → Phase II → [SDTP] → Phase IV → Phase V → Phase VI → Phase VII
                                  │
                                  └─ Replaces or augments Phase III for complex problems
```

**Invocation Phrase**: "Run SDTP on this" or "Deep Think this problem"

---

## Example Application

**Problem**: "Should I take Job A (stable, lower pay) or Job B (startup, equity upside)?"

```text
PHASE 1: HYPOTHESIS GENERATION
┌──────────────────────────────────────────────────────────────────────┐
│ H1: Take Job A (Stability Maximisation)                              │
│ Assumption: Stability has higher utility than upside potential      │
│ Approach: Accept lower ceiling for higher floor                     │
├──────────────────────────────────────────────────────────────────────┤
│ H2: Take Job B (EV Maximisation)                                     │
│ Assumption: Equity upside compensates for risk                      │
│ Approach: Accept variance for higher expected value                 │
├──────────────────────────────────────────────────────────────────────┤
│ H3: Negotiate Job A Up (Information Arbitrage)                       │
│ Assumption: Job A has slack in their offer                          │
│ Approach: Use Job B as leverage before deciding                     │
├──────────────────────────────────────────────────────────────────────┤
│ H4: Reject Both (Option Preservation)                                │
│ Assumption: Better options exist with more search                   │
│ Approach: Continue searching with new market data                   │
└──────────────────────────────────────────────────────────────────────┘

PHASE 2: PARALLEL EVALUATION
┌───────────┬───────────┬──────────┬──────────┬──────────────┬───────┐
│ Hypothesis│ Feasibility│   EV     │ Risk     │ Reversibility│ Score │
├───────────┼───────────┼──────────┼──────────┼──────────────┼───────┤
│ H1        │   9/10    │ +$120K/yr│   5%     │     Medium   │  7.2  │
│ H2        │   8/10    │ +$180K EV│  35%     │     Low      │  6.5  │
│ H3        │   6/10    │ +$140K/yr│  15%     │     High     │  7.8  │
│ H4        │   5/10    │ Unknown  │  40%     │     High     │  4.5  │
└───────────┴───────────┴──────────┴──────────┴──────────────┴───────┘

PHASE 3: CONVERGENCE
┌──────────────────────────────────────────────────────────────────────┐
│ SELECTED: H3 (Negotiate Job A Up)                                    │
│                                                                       │
│ WHY NOT H1: Leaves value on table if negotiation slack exists       │
│ WHY NOT H2: Risk-adjusted EV lower than adjusted H3                 │
│ WHY NOT H4: Opportunity cost too high, both offers are decent       │
│                                                                       │
│ THRESHOLD: Switch to H2 if equity offer >$500K potential            │
└──────────────────────────────────────────────────────────────────────┘

PHASE 4: FALSIFICATION
┌──────────────────────────────────────────────────────────────────────┐
│ If wrong because: Job A has no negotiation room (anchored offer)    │
│ Weakest link: Assumption that leverage exists                       │
│ Counter-argument: "Startup equity is lottery, not investment"       │
│ Would change mind if: Job A explicitly rejects negotiation          │
│                                                                       │
│ CONFIDENCE: 72% — Reasonable but untested assumption about A        │
│                                                                       │
│ ROBUSTNESS: FRAGILE to "no negotiation room" scenario               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## RSI Integration

SDTP is designed for recursive self-improvement:

1. **After each use**: Deposit learnings about which hypotheses were correct/incorrect
2. **Calibration over time**: Track confidence accuracy (were 70% calls right 70% of the time?)
3. **Pattern extraction**: Identify when certain hypothesis types consistently win/lose

```text
RSI DEPOSIT FORMAT:
┌──────────────────────────────────────────────────────────────────────┐
│ SDTP SESSION: [Date]                                                 │
│ Problem: [Brief]                                                     │
│ Selected: H[X] with __% confidence                                   │
│ Outcome: [Correct / Incorrect / Pending]                             │
│ Learning: [What to update for next time]                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Limitations

| What SDTP Can Do | What SDTP Cannot Do |
|------------------|---------------------|
| Force explicit multi-path reasoning | Add actual compute time |
| Reduce premature convergence | Access hidden knowledge |
| Make reasoning auditable | Guarantee correctness |
| Enable calibration/RSI | Replace domain expertise |

**SDTP is technique, not hardware. It optimises the use of existing capability.**

---

## References

- [Protocol 52: Deep Research Loop](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/research/52-deep-research-loop.md) — References this protocol
- [Agentic Engineering Strategy: Scenario Response](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/engineering/Engineering_Strategy_Framework.md) — References this protocol

---

## Tagging

# protocol #framework #process #38-synthetic-deep-think
