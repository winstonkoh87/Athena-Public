---
graphrag_extracted: true
---

# RED-TEAM REVIEW — v3.0

> **Purpose**: Pre-mortem analysis — find how this artefact fails *before* it ships.
> **Scope**: Internal circulation + personal consumption. Calibrate accordingly.

---

## ARTEFACT METADATA (Required)

| Field | Value |
|-------|-------|
| **Name** | |
| **Version / Date / Commit** | |
| **Owner** | |
| **Type** | `Code` / `Prose` / `Strategy` / `Design` / `Email` / `Other` |
| **Intended Audience** | |
| **Intended Decision** | `Ship` / `Publish` / `Send` / `Present` / `Other` |
| **Constraints** | (time, legal, tone, length, etc.) |

---

## THE ARTEFACT

*[Paste or link the content here]*

---

## PHASE 1: CONTEXT BEFORE CRITIQUE

> *Critique without context is noise.*

**Assumptions (max 3 bullets):**
1.
2.
3.

**What I optimized for in this review:**

- [ ] Accuracy / Correctness
- [ ] Safety / Security
- [ ] Reputation / Trust
- [ ] Persuasion / Clarity
- [ ] Speed / Actionability
- [ ] Other: ___

---

## PHASE 2: SEVERITY-WEIGHTED FINDINGS

Rate each issue by **blast radius** — how much damage if shipped.

### 🔴 CRITICAL (Blockers)

Issues causing **immediate failure**, security breach, legal exposure, or reputational harm.

- **Threshold**: Would you mass-recall this product? Data leak? Factual error in high-stakes domain?
- **Format**: `[CRITICAL]` "<exact quote>" → Consequence if shipped → Mitigation

*If none found: `[NONE FOUND]` — explain what you tested.*

---

### 🟠 HIGH (Degraded Quality)

Issues that **significantly reduce value** but don't break deployment.

- **Threshold**: Would a senior colleague flag this in review?
- **Format**: `[HIGH]` "<exact quote>" → Mitigation in ≤10 min: ___| Proper fix:___ (est: ___)

*If none found: `[NONE FOUND]`*

---

### 🟡 MEDIUM (Missed Upside)

Opportunities to elevate from "good" to "excellent."

- **Threshold**: Would this make the portfolio version?
- **Format**: `[MED]` <opportunity> → Implementation hint

*If none found: `[NONE FOUND]`*

---

### 🟢 LOW (Polish)

Minor style/formatting issues.

- **Threshold**: Would you fix this with 5 extra minutes?
- **Format**: `[LOW]` <issue>

*If none found: `[NONE FOUND]`*

---

## PHASE 3: TEST COVERAGE

> *"None found" ≠ "None exist"*

| Dimension Checked | Coverage | Notes |
|-------------------|----------|-------|
| Factual accuracy | ☐ Full ☐ Partial ☐ None | |
| Security/Privacy | ☐ Full ☐ Partial ☐ None | |
| Legal/Compliance | ☐ Full ☐ Partial ☐ None | |
| Reputational risk | ☐ Full ☐ Partial ☐ None | |
| Usability/Clarity | ☐ Full ☐ Partial ☐ None | |
| Edge cases | ☐ Full ☐ Partial ☐ None | |

**What I did NOT test (known blind spots):**
-

---

## PHASE 4: SCORE

### Scoring Rubric (Mechanical)

| Severity | Deduction per Issue |
|----------|---------------------|
| 🔴 CRITICAL | -30 |
| 🟠 HIGH | -10 |
| 🟡 MEDIUM | -3 |
| 🟢 LOW | -1 |

**Calculation**: 100 - (deductions) = Score (floor at 0)

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Ship it. Minor polish only. | ✅ Deploy |
| 75-89 | Solid. Fix HIGHs before deploy. | 🔧 Patch & ship |
| 50-74 | Structural gaps. Rework required. | ⚠️ Hold |
| 0-49 | Fundamentally broken. | 🚫 Restart |

---

**Your Score**: [ ] / 100

**Findings Summary**:

- 🔴 CRITICAL:
- 🟠 HIGH:
- 🟡 MEDIUM:
- 🟢 LOW:

**One-Line Justification**:

---

## PHASE 5: ADVERSARIAL PROBES

Ask **three questions** a hostile critic would ask to undermine this work:

1.
2.
3.

---

## PHASE 6: STEELMAN

> *This prevents over-criticism. If you can't steelman it, your critique may be unfair.*

**What is the strongest argument FOR shipping this as-is?**

---

## PHASE 7: RISK REGISTER (Optional)

| Risk | Severity | Likelihood | Detection Difficulty | Mitigation | Owner |
|------|----------|------------|----------------------|------------|-------|
| | 🔴/🟠/🟡/🟢 | High/Med/Low | Easy/Hard | | |

---

## RULES

1. **Quote directly.** No vague complaints. Cite the exact text you're critiquing.
2. **Prioritize real problems.** Don't invent issues to fill sections.
3. **Empty sections are allowed.** `[NONE FOUND]` is a valid answer — with explanation.
4. **Assume competence; stress-test as if attacked.** Default: this is professional-grade work. Find reasons to downgrade, not reasons to dismiss.
5. **Time-box fixes.** Every HIGH must have a mitigation in ≤10 min. Proper fix can take longer — state the estimate.
6. **Be conservative with CRITICAL.** If it doesn't break the user experience or cause legal/reputational harm, it's HIGH, not CRITICAL.

---

## ANTI-PATTERNS (What NOT to do)

❌ "This could be better" — *How? Be specific.*
❌ Inventing problems to seem thorough
❌ Critiquing style when substance is the issue
❌ Ignoring context (audience, constraints, purpose)
❌ Severity inflation (calling everything CRITICAL)
❌ Unstated assumptions leading to misaligned critique
❌ Claiming "none found" without stating what was tested

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | — | Initial template |
| v2.0 | — | Added Steelman, Anti-Patterns, Adversarial Probes |
| v3.0 | 2026-01-04 | Added: Artefact Metadata, Explicit Assumptions, Test Coverage, Scoring Rubric, Risk Register, Mitigation vs Proper Fix distinction |
