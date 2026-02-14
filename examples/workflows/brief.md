---created: 2025-12-19
last_updated: 2026-01-30
---

---description: Pre-prompt fact-finding and scope clarification before executing complex tasks
created: 2025-12-19
last_updated: 2026-01-11
---

# /brief v2.1 — Pre-Prompt Clarification Protocol

**Trigger:** User invokes `/brief <task description>` before a complex or underspecified request.

**Philosophy:** Measure twice, cut once. Clarify requirements before wasting tokens on wrong output.

---

## Quick Reference

| Variant | When to Use | Expand? |
|---------|-------------|---------|
| Core Brief | Default — most tasks | No |
| `/brief ++` | Complex multi-step work | Yes |
| `/brief build` | Technical "Build X" tasks | Build Extension |
| `/brief research` | Investigate/analyze tasks | Research Extension |

---

## Phase 1: Router (One Line)

When `/brief` is invoked, first identify the type:

```
Brief Type: [ ] Build  [ ] Research  [ ] Hybrid  [ ] Multi-stakeholder

Hybrid Flow (if selected): [ ] Research → Build  [ ] Build → Research  [ ] Interleaved
```

---

## Phase 1.5: Interview Mode (Iterative Clarification)

> **Source:** [@trq212 viral tweet](https://x.com/trq212/status/2005315275026260309) (1.5M views, Dec 2025)
> **Philosophy:** Don't assume. Interview. Extract tacit knowledge before writing specs.
> **v3.1 Fix:** Iterative questioning (10 max per turn) instead of 50-question dump.

**Trigger:** User invokes `/brief interview` OR `/brief` on underspecified request.

---

### The Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      /brief interview FLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  USER: "I want to build X" (even one line is fine)                   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  TURN 1: AI asks up to 10 questions (most critical first)     │  │
│  │          → User answers                                        │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  TURN 2: AI asks follow-up questions (if needed)               │  │
│  │          → User answers                                        │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  TURN N: Continue until AI is FULLY SATISFIED                  │  │
│  │          → No arbitrary cap. Stop when clarity is achieved.    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  AI writes → .context/specs/[PROJECT]_SPEC.md                  │  │
│  │  User reviews spec → Iterates if needed                        │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  NEW SESSION: Paste spec → Implement                           │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Interview Rules

| Rule | Description |
|------|-------------|
| **Max 10 questions per turn** | Don't overwhelm. Batch intelligently. |
| **Non-obvious questions only** | No "what color?" — ask what the user hasn't thought about. |
| **Iterate until satisfied** | No arbitrary cap. Keep asking until full clarity. |
| **User controls pace** | User can say "that's enough" or "ask me more" at any turn. |
| **No execution during interview** | Only ask + synthesize. Don't build yet. |

---

### Question Categories

| Category | Example Questions |
|----------|-------------------|
| **Scope** | "What does success look like? What's explicitly out of scope?" |
| **Users** | "Who are the primary users? What's their technical sophistication?" |
| **Edge Cases** | "What happens if [X] fails? What's the fallback?" |
| **Data** | "Where does data come from? What's the sensitivity level?" |
| **Integration** | "What does this need to talk to? Any API constraints?" |
| **Constraints** | "What can NOT change? What's the hard deadline?" |
| **Tradeoffs** | "If you had to cut one feature, which would it be?" |
| **Anti-goals** | "What should this explicitly NOT do?" |
| **Ruin Vectors** | "What would make this a disaster? Security/privacy concerns?" |
| **Precedent** | "Any existing examples you like/hate?" |
| **Hidden** | "What am I not asking that I should be?" |

---

### Completion Signal

When interview is complete, AI outputs:

```
✅ Interview Complete
   Questions asked: XX | Turns: Y

📄 Writing spec to: .context/specs/[PROJECT_NAME]_SPEC.md

📋 Key Decisions Captured:
   - [Decision 1]
   - [Decision 2]
   - [Decision 3]

─────────────────────────────────────────────────────
NEXT STEP: Review the spec. When satisfied:

   1. Start a NEW session
   2. Paste or reference: .context/specs/[PROJECT_NAME]_SPEC.md
   3. Say: "Implement this spec"
─────────────────────────────────────────────────────
```

---

## Phase 2: Core Brief (Default)

> **Design Principle:** Progressive Disclosure. This is the *minimum viable brief*. Expand only when complexity demands it.

### Core Brief Checklist

1. **OUTCOME**: What will be true when successful?
2. **AUDIENCE + CONTEXT**: Who uses it, where, and why?
3. **CONSTRAINTS & BOUNDARIES**: Must-haves, must-nots, scope boundaries, source of truth.
4. **DEFINITION OF DONE**: Acceptance criteria, non-goals, quality bar.
5. **DELIVERY**: Format, Length/Depth, Tone, Data sensitivity (Public/Internal/PII).
6. **TIMELINE**: Ship date, Confidence (70/85/95%), Tradeoff priority (Speed/Quality/Scope).
7. **BUDGET**: Time-box (5m / 20m / 1h / Deep dive).

> **Rule:** If `Mode: Ship` is selected, DoD fields become **mandatory**.

---

## Phase 3: Expanded Fields (`/brief ++`)

> **Trigger:** High-effort request (>3 steps), multiple stakeholders, or significant unknowns.

Add these to Core Brief:

1. **INPUTS**: References, anti-examples, source material.
2. **EXECUTION MODE**: Explore/Draft/Revise/Ship, Review path (Reviewers, Rounds, Approval rule).
3. **DEPENDENCIES & UNKNOWNS**: Blockers, assumptions, open decisions (Decider, Veto holders, Approval criterion).

---

## Build Extension (`/brief build`)

> **Trigger:** "Build X", "Code Y", or any technical implementation task.

A. **SYSTEM CONTEXT**: Tech stack, environment, Hosting/runtime constraints, Tech debt acceptance.
B. **INTERFACES**: APIs / data contracts, I/O shapes, Permissions required.
C. **RUIN VECTORS (Law #1 Check)**: Security, Privacy, Data loss, Prod outage risk, Cost blowup, Compliance.
D. **OBSERVABILITY + ROLLBACK**: Logging plan, Known failure modes, Rollback strategy.
E. **TEST PLAN**: Unit/integration/e2e expectations, Acceptance test map.
F. **SEMANTIC PRE-LOAD**: Prior art (3 max), Constraints extracted (5 max), Known pitfalls (5 max), Brief deltas.
G. **ENGINEERING EDGE CASES**: Race conditions, Offline states, Error handling, Data persistence.

---

## Research Extension (`/brief research`)

> **Trigger:** "Find out about X", "Analyze Y", "What is the best Z"

> **Special Flow:** For research, AI can run Semantic Pre-Load FIRST, then draft the brief for user approval.

```
+-------------------------------------------+
|  RESEARCH EXTENSION                       |
+-------------------------------------------+
|                                           |
|  A. RESEARCH QUESTION(S)                  |
|     What must be answered?                |
|     _________________________________     |
|                                           |
|  B. DECISION IT SUPPORTS                  |
|     What choice will be made from this?   |
|     _________________________________     |
|                                           |
|  C. EVALUATION CRITERIA                   |
|     What does "best" mean?                |
|     (cost, accuracy, time, risk, etc.)    |
|     _________________________________     |
|     Lens/Persona:                         |
|       [ ] Neutral  [ ] Skeptic  [ ] Advocate  |
|       [ ] Specific: _______________       |
|                                           |
|  D. METHOD                                |
|     Sources to include:                   |
|     Sources to exclude:                   |
|     Recency requirement (e.g., <2 years): |
|     Source quality bar:                   |
|       [ ] Primary docs  [ ] Peer-reviewed |
|       [ ] Reputable journalism  [ ] Any   |
|     Citation required: [ ] Yes  [ ] No    |
|                                           |
|  E. OUTPUT FORMAT                         |
|     [ ] Recommendation                    |
|     [ ] Options matrix                    |
|     [ ] Annotated bibliography            |
|     [ ] Detailed report                   |
|     [ ] Bulleted summary                  |
|                                           |
|  F. STOPPING RULE                         |
|     When is research "enough"?            |
|     [ ] Time-box: ___ minutes             |
|     [ ] Coverage: ___ sources             |
|     [ ] Confidence: ___% certainty        |
|                                           |
+-------------------------------------------+
```

---

## Semantic Pre-Load Integration

> **Philosophy:** Active grounding, not passive templating.

**Standard Execution Order (Build/General):**

```
┌─────────────────────────────────────────────────┐
│  1. User fills Core Brief                       │
│  2. AI runs: smart_search.py "<brief keywords>" │
│  3. AI populates Pre-Load section:              │
│     - 3 prior art references                    │
│     - 5 key constraints extracted               │
│     - 5 known pitfalls                          │
│  4. AI outputs "Brief Deltas":                  │
│     - New constraints found                     │
│     - New risks                                 │
│     - Recommended scope cuts                    │
│  5. User reviews/approves refined brief         │
│  6. Execute task                                │
└─────────────────────────────────────────────────┘
```

**Research Flow (Inverted):**

```
┌─────────────────────────────────────────────────┐
│  1. User gives topic/question                   │
│  2. AI runs: smart_search.py "<topic>"          │
│  3. AI drafts Research Brief (auto-filled)      │
│  4. User reviews/approves brief                 │
│  5. Execute research                            │
└─────────────────────────────────────────────────┘
```

**Rules:**

- Time-boxed: Max 5 minutes of search
- Skippable: For low-stakes tasks, add `--skip-preload`
- Output-limited: Don't overwhelm with 20 references
- Delta required: Pre-load must output "what changed in the brief"

---

## When to Suggest /brief

If user gives a high-effort request (n > 3 items) that is underspecified:

> "This is a big ask. Want me to `/brief` it first?"

If complexity is extreme:

> "This is complex. Want me to `/brief ++` with full dependency mapping?"

Do not auto-trigger. User controls the gate.

---

## Quick Heuristics

| Situation | Recommended Variant |
|-----------|---------------------|
| Simple content task | Core Brief only |
| Multi-step project | `/brief ++` |
| New feature/code | `/brief build` |
| Investigation/analysis | `/brief research` |
| Underspecified idea | `/brief interview` → `/spec` |
| Client work | Add "Veto holders" field |

---

## Changelog

| Version | Changes |
|---------|---------|
| v3.1 | **Red-team fixes**: Iterative questioning (10 max/turn, no arbitrary cap), added Ruin Vectors to question categories, clearer flow diagram, user-controlled pacing. `/spec` upgraded with Logic/State section, Documentation Rot warning, sample data. |
| v3.0 | **Interview Mode** (AskUserQuestionTool pattern from @trq212). AI-driven interview → writes `_SPEC.md`. New `/spec` workflow for output format. |
| v2.1 | Fixed confidence default (85%), forced tradeoff priority, hybrid direction, budget field, veto holders, semantic pre-load delta, tech debt acceptance, lens/persona, source quality policy, data sensitivity |
| v2.0 | Progressive disclosure, brief types router, build/research extensions, semantic pre-load |
| v1.0 | Basic ASCII box template |

---

## Tagging

# workflow #clarification #brief #scope #interview #spec #v3.1
