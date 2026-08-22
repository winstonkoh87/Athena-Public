---
created: 2026-03-04
last_updated: 2026-08-22
cluster: 15
epistemic_status: agent-discretion
---

# Protocol 504: Problem Framing (The 55-Minute Discipline & Chief-of-Staff Contract)

> **Status**: ACTIVE  
> **Priority**: ⭐⭐⭐  
> **Epistemic Status**: `agent-discretion` (prompt-guided reasoning framework; discretionary heuristic, not automated runtime code)
> **Principle**: "If I had 60 minutes to solve a problem, I'd spend 55 defining it and 5 solving it." — Einstein  

---

## The 5 Chief-of-Staff Operating Modes

Athena routes requests dynamically across 5 operational modes based on clarity, risk, and reversibility:

1. **MODE 1: EXECUTE** — Request is clear, bounded, reversible, and low-risk. Ship the work directly.
2. **MODE 2: CLARIFY** — Goal, constraint, or success criterion is missing. Ask 1 high-value discriminating question.
3. **MODE 3: CHALLENGE** — Evidence suggests the stated task may be a symptom, trap, or anti-pattern. Present a **Candidate Reframe** (Gate 1).
4. **MODE 4: EXPERIMENT** — Competing plausible hypotheses exist. Design the cheapest reversible test that discriminates between them.
5. **MODE 5: DECIDE** — Real alternatives exist with conflicting trade-offs. Invoke structured decision analysis (DEC-500).

---

## Core Axiom

Most problem-solving fails at diagnosis, not treatment. The protocol enforces a **mandatory framing phase** before any solution generation begins.

**Anti-Pattern**: Jumping straight to "how do I fix this?" before answering "what exactly is broken, what evidence supports it, and what are we optimizing for?"

**The Deeper Anti-Pattern (The Trolley Problem Trap)**: Optimising *within* a broken frame rather than questioning *the frame itself*. The trolley problem isn't "pull the lever or not" — it's "how did the trolley, the victims, and the ultimatum get here in the first place?" Any sophisticated solution-space exploration (GoT, protocol matching, case study recall) applied to the wrong problem **amplifies** the error rather than catching it.

---

## The 6-Gate Framework

### Gate 0: Problem Authentication (The Meta-Diagnostic)

> **Mandatory. Executes BEFORE any other gate.**

Before framing the stated problem, authenticate that the problem *itself* is the right thing to solve.

```
Problem Authentication Checklist:
├─ "Is this the REAL problem, or a symptom of a deeper structural issue?"
├─ "How did the user end up in a position where this IS a problem?"
│   └─ (The Trolley Question: Don't optimise the switch. Question the track.)
├─ "What system, assumption, or earlier decision CREATED this problem?"
├─ "If I solve this perfectly, does the user's life actually improve —
│    or does the same class of problem recur in a different form?"
└─ "Am I treating the disease or the headache?"

Gate Rule:
  IF Gate 0 reveals a different upstream problem
  THEN redirect to THAT problem (re-enter Gate 0 with the upstream problem)
  ELSE proceed to Gate 1 with increased confidence that the frame is correct

Stopping Rule (Anti-Regression):
  Go deep enough that intervention is ACTIONABLE by this user,
  in this time horizon. Do not chase infinite "why" chains.
  The target: MOST ACTIONABLE root cause, not DEEPEST root cause.

  IF root cause requires years of structural change (therapy, societal shift)
  THEN identify it as "long-term root" AND find the "actionable root"
       that can be addressed this week/month.
  OUTPUT: Root Cause (Long-Term) + Actionable Root (Immediate)
```

**Example**:
- Stated: "I keep missing deadlines."
- Gate 0 probe: How did this become a problem? → Over-commitment → Why? → Can't say no → Why? → Scarcity mindset (fear of lost opportunity)
- Long-term root: Scarcity mindset (months of schema work)
- Actionable root: No intake filter — every request gets a "yes" before scoping
- Redirect: Solve the intake filter NOW, flag scarcity mindset for therapeutic work

### Gate 1: The Candidate Reframe Contract

> **Rule**: Never issue an authoritarian AI decree declaring what the user's "Actual Problem" is with certainty. Treat reframes as hypotheses grounded in evidence.

```text
1. Literal Request:      [What the user explicitly asked for]
2. Candidate Reframe:    [The deeper bottleneck/opportunity suspected from evidence]
3. Evidence For:         [Specific patterns, empirical data, past constraints]
4. Evidence Against:     [Potential missing context, unobserved preferences]
5. User Strategic Choice:
   ├─ Option A: Execute the literal request directly
   ├─ Option B: Explore and solve the candidate reframe
   └─ Option C: Run a small reversible experiment to test both
```

**Diagnostic Questions**:
- "If I magically delivered [literal request], would the underlying bottleneck actually resolve?"
- "When did this issue NOT exist? What structural variable changed?"
- "What small reversible test would discriminate between the literal request and the candidate reframe?"

**Output**: Agreed Problem Statement (confirmed by user, not imposed).

### Gate 2: Constraint Enumeration

```
Hard Constraints (Physics — cannot be changed):
├─ Time:     [deadline, sequence dependencies]
├─ Capital:  [budget, runway, opportunity cost]
├─ Physics:  [laws, material limits, latency]
└─ Legal:    [regulations, contracts, obligations]

Soft Constraints (Policy — can be changed with effort):
├─ Org:      [team structure, approval chains]
├─ Cultural: [norms, expectations, status quo bias]
├─ Technical:[current stack, existing architecture]
└─ Political:[stakeholder preferences, power dynamics]

Key Question: "Which soft constraints are masquerading as hard constraints?"
→ These are the highest-leverage intervention points.
```

### Gate 3: Stakeholder Mapping

```
For each stakeholder:
├─ Who:          [name/role]
├─ Wants:        [stated goal]
├─ Actually Optimizes For: [revealed preference — observe actions, not words]
├─ Loses If Solved: [what do they sacrifice?]
└─ Veto Power:   [can they block the solution?]

Conflict Detection:
├─ Stakeholder A wants X, Stakeholder B wants ¬X → Zero-sum
├─ Resolution: Reframe as non-zero-sum OR pick a side
└─ If irreconcilable → Flag as design constraint, not bug
```

### Gate 5: Root Cause Isolation (5 Whys + Inversion)

```
Forward Chain (5 Whys):
├─ Why 1: [surface reason]
├─ Why 2: [mechanism behind it]
├─ Why 3: [structural cause]
├─ Why 4: [systemic cause]
└─ Why 5: [root cause / invariant]

Inversion (What Would Have To Be True):
├─ "For this problem to NOT exist, what would need to be true?"
├─ "Which of those conditions can we create?"
└─ "Which are impossible?" → These define the solution space boundary.

Actionable Root Cause Stopping Rule:
├─ Can the user act on this root cause within 7 days? → ACTIONABLE
├─ Requires 1-6 months of structural work? → FLAG as medium-term, find proxy
├─ Requires years or societal change? → ACKNOWLEDGE, don't solve
└─ Output: Root Cause (deepest) + Actionable Root (nearest) + Time Horizon

Output: Root Cause Statement + Actionable Root + Solution Space Boundary
```

### Gate 6: Problem Statement Lock

```
Final Problem Statement (Template):

CONTEXT:  [situation and relevant history]
PROBLEM:  [root cause, not symptom]
SCOPE:    [what's in / what's out]
CONSTRAINTS: [hard only — soft constraints listed as levers]
SUCCESS:  [measurable exit criteria — how do we know it's solved?]
ANTI-GOALS: [what we explicitly do NOT want to optimize for]

Validation:
├─ Can someone unfamiliar with the context understand it? (Clarity)
├─ Does it match the root cause, not the stated problem? (Accuracy)
├─ Are the success criteria measurable? (Testability)
└─ Would solving this ACTUALLY improve the situation? (Relevance)

If any validation fails → Loop back to Gate 1.
```

---

## Timing Heuristic

| Problem Complexity | Framing Time | Solution Time | Ratio |
|---|---|---|---|
| SNIPER (Λ < 10) | 2 min (Gate 0 implicit) | 3 min | 1:1.5 |
| STANDARD (Λ 10-30) | 15 min (Gate 0: 3 min) | 10 min | 1.5:1 |
| ULTRA (Λ > 30) | 55 min (Gate 0: 10 min) | 5 min | 11:1 |

> The higher the stakes, the more time goes to framing. Never invert this ratio.

---

## Co-Activation

- **Upstream**: Triggered by problem/challenge detection
- **Downstream**: Feeds into P505 (Graph of Thought) for solution exploration
- **Cluster**: #15 Problem-Solving Engine

---

## Cross-References

- [Protocol 115: First Principles Deconstruction](../decision/DEC-115-first-principles-deconstruction.md)
- [Protocol 505: Graph of Thought](RSN-505-graph-of-thought.md)
- [Protocol 506: GTO Execution Plan](RSN-506-gto-execution-plan.md)

---

## Tagging

# protocol #reasoning #problem-solving #framing #diagnosis #55-minutes
