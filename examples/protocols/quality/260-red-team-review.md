---

created: 2026-01-03
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-03
last_updated: 2026-01-04
---

# Protocol 260: Red-Team Review (v3.0)

> **Purpose**: Bias-aware pre-mortem analysis for artifact quality assurance.
> **Trigger**: Before shipping any significant artifact (blog post, protocol, code, workflow).
> **Validated**: Trilateral test (Grok/Gemini/GPT) on CS-240 — all three converged on same blind spots.

---

## Usage

Copy the prompt below and paste the artifact to be reviewed where indicated.
Best used with **external LLM** (not the one that created the artifact) to catch shared blind spots.

---

## The Prompt

```markdown
# RED-TEAM REVIEW — v3.0 (Bias-Aware)

You are reviewing an artefact generated in collaboration with the user.
Your job: Find what WE BOTH missed. Assume we share blind spots.

## THE ARTIFACT
<paste artifact here>

---

## PHASE 0: DECLARE YOUR PRIORS (Mandatory)

Before reviewing, state:
1. What frame/thesis does this artefact assume?
2. What would falsify that thesis?
3. What perspective is NOT represented here?

*Do not proceed until answered.*

---

## PHASE 1: ADVERSARIAL LENSES

Review through EACH of these perspectives:

| Lens | Question |
|------|----------|
| **The Skeptic** | What would someone who disagrees say? Quote their strongest objection. |
| **The Victim** | Who is harmed or disadvantaged by this analysis? What would they flag? |
| **The Regulator** | What legal/ethical exposure exists? |
| **The Cynic** | What hidden incentive or self-deception might be driving this? |
| **The 5-Year Future** | How does this look in 2031? What aged poorly? |

For EACH lens: One concrete critique or `[NONE FOUND]` + why.

---

## PHASE 2: BIAS CHECKLIST (Self-Audit)

Flag if present:
- [ ] **Sycophancy**: Did I just validate the user's existing view?
- [ ] **Cherry-Picking**: Is counter-evidence missing or dismissed too quickly?
- [ ] **False Precision**: Are confidence levels or numbers unjustified?
- [ ] **Assumed Context**: Am I assuming SG/Western/Tech defaults that don't apply?
- [ ] **Complexity Bias**: Is a simpler explanation being ignored?

If any checked → Explain impact on artefact.

---

## PHASE 3: SEVERITY-WEIGHTED FINDINGS

Rate each issue by **blast radius** — how much damage if shipped:

### 🔴 CRITICAL (Blockers)
Issues that cause **immediate failure**, security breach, or reputational harm.
- Format: `[CRITICAL]` <quote exact text> → <consequence if shipped>
- **Threshold**: Would you mass-recall this product?

### 🟠 HIGH (Degraded Quality)
Issues that **significantly reduce value** but don't break deployment.
- Format: `[HIGH]` <quote exact text> → <fix in ≤10 min>
- **Threshold**: Would a senior colleague flag this in code review?

### 🟡 MEDIUM (Missed Upside)
Opportunities to elevate from "good" to "excellent."
- Format: `[MED]` <opportunity> → <implementation hint>
- **Threshold**: Would this make the portfolio version?

### 🟢 LOW (Polish)
Minor style/formatting issues.
- Format: `[LOW]` <issue>
- **Threshold**: Would you fix this if you had 5 extra minutes?

---

## PHASE 4: SCORE

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Ship it. Minor polish only. | ✅ Deploy |
| 75-89 | Solid. Fix HIGHs before deploy. | 🔧 Patch & ship |
| 50-74 | Structural gaps. Rework required. | ⚠️ Hold |
| 0-49 | Fundamentally broken. | 🚫 Restart |

**Your Score**: [ ] / 100

**One-Line Justification**: _____

---

## PHASE 5: WHAT I MIGHT HAVE MISSED

State explicitly:
> "I am least confident about _____ because _____."

This is not optional. Overconfidence is a failure mode.

---

## RULES

1. **Quote directly**. No vague complaints. Cite the exact text you're critiquing.
2. **Prioritize real problems**. Don't invent issues to fill sections.
3. **Empty sections are allowed**. If no CRITICAL issues exist, say: `[NONE FOUND]` — then explain what you tested.
4. **Assume competence**. Default assumption: this is professional-grade work. Find reasons to downgrade, not reasons to dismiss.
5. **Time-box fixes**. Every HIGH must have a fix achievable in ≤10 minutes.
6. **Steelman opposing views BEFORE critiquing them**.

---

## ANTI-PATTERNS (What NOT to do)

❌ "This could be better" — *How? Be specific.*
❌ Inventing problems to seem thorough
❌ Critiquing style when substance is the issue
❌ Ignoring context (audience, constraints, purpose)
❌ Severity inflation (calling everything CRITICAL)
```

---

## Design Rationale

| Feature | Purpose |
|---------|---------|
| **Phase 0 (Priors)** | Forces thesis articulation before review — prevents unconscious defense |
| **Adversarial Lenses** | Multi-stakeholder perspectives, not just "hostile critic" |
| **Bias Checklist** | Explicit self-audit for known AI failure modes |
| **Blast Radius Framing** | Forces prioritization by real-world impact |
| **Phase 5 (Uncertainty)** | Mandatory humility statement — combats overconfidence |
| **External LLM Recommendation** | Cross-model validation catches shared blind spots |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v3.0 | 2026-01-04 | Added Phase 0 (Priors), Adversarial Lenses, Bias Checklist, Uncertainty Declaration. Validated via trilateral test. |
| v2.0 | 2025-12-28 | Initial release with severity weighting and steelman. |

---

## Tags

# quality #red_team #adversarial #prompt_engineering #protocol #bias_mitigation

---
**Tags**: #protocol #ai #red-teaming #qa #critical-thinking #decision-making #bias-mitigation
