---

created: 2025-12-31
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-31
last_updated: 2026-01-06
---

# Protocol 247: Red-Team Handoff

> **Status**: ACTIVE  
> **Created**: 31 December 2025  
> **Purpose**: Standardized prompt for external AI to red-team internal work.

---

## When to Use

- Before shipping any artifact (code, protocol, design doc)
- When internal blindness risk is high (>2 hours on same work)
- Cross-checking between AI systems (Gemini ↔ Claude)

---

## The Prompt Template

```markdown
# RED-TEAM REVIEW REQUEST

You are a senior technical reviewer auditing this work for deployment readiness.

## THE ARTIFACT
[Paste or describe the artifact here]

---

## REVIEW FRAMEWORK

### 1. SCORE (0-100)
Rate the artifact on this scale:
- **90-100**: Production-ready. Minor polish only.
- **70-89**: Solid foundation. Gaps are fixable in <1 hour.
- **50-69**: Structural issues. Requires significant rework.
- **0-49**: Fundamentally flawed. Restart recommended.

### 2. FATAL FLAWS (Blockers)
List anything that would PREVENT deployment or cause immediate failure.
Format: `[FATAL] <specific issue> → <consequence if shipped>`

### 3. STRUCTURAL WEAKNESSES (High Priority)
Issues that don't block deployment but degrade quality significantly.
Format: `[HIGH] <specific issue> → <suggested fix>`

### 4. MISSED OPPORTUNITIES (Medium Priority)
Things that would elevate the work from "good" to "excellent."
Format: `[MED] <opportunity> → <implementation hint>`

### 5. NITPICKS (Low Priority)
Minor polish items. Address if time permits.
Format: `[LOW] <issue>`

### 6. THREE HARDEST QUESTIONS
Ask three questions that would expose the weakest assumptions in this work.

---

## RULES
- Be brutally specific. "Could be clearer" is not actionable. "Line 47's variable name `x` should be `user_count`" is.
- Assume the author is competent but blind to their own gaps.
- Prioritize finding REAL problems over being nice.
- If you find nothing wrong, say so — but explain what you tested.
```

---

## Design Rationale

| Element | Purpose |
|---------|---------|
| **Tiered severity** | Forces triage — not all issues are equal |
| **"Consequence if shipped"** | Exposes real-world impact, not theoretical risk |
| **"Suggested fix"** | Makes feedback immediately actionable |
| **Three Hardest Questions** | Surfaces hidden assumptions the author is blind to |
| **"Assume competent but blind"** | Calibrates tone — critical without condescending |

---

## Variants

### Lite Version (Quick Reviews)

```markdown
Score this 0-100. List: (1) Fatal flaws, (2) Top 3 fixes, (3) One question that would break this.
```

### Deep Audit Version

Add to base prompt:

```markdown
### 7. ASSUMPTION AUDIT
List every implicit assumption in this work. Mark each: [SAFE] / [RISKY] / [UNTESTED]

### 8. FAILURE MODE ANALYSIS
If this artifact fails in production, what's the most likely cause?
```

---

## Anti-Patterns

| Pattern | Why It Fails |
|---------|--------------|
| "Rate this and give feedback" | Too vague — gets generic responses |
| No severity tiers | All issues feel equal, can't prioritize |
| Missing "suggested fix" | Feedback without path forward = frustration |
| "Be honest" without structure | Gets either sycophancy or unconstructive criticism |

---

## Integration Points

- [Protocol 159](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/159-verification-before-claim.md): Verification Before Claim
- [/audit workflow](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/audit.md): Cross-model validation

---

# red-team #audit #prompt-engineering #quality-assurance #workflow
