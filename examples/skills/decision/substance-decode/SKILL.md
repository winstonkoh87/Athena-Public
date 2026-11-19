---
name: substance-decode
description: "Two-direction meta-awareness engine: decode operative reality behind official narratives (inbound) and simulate audience framing and downside asymmetry before outward acts (outbound)."
vibe: "Strip the cover story. Check the incentives and base rates."
context_trigger: "substance decode, narrative, incentives, negotiation, red flag, counterparty, email, post, framing, meta-awareness"
auto-invoke: true
model: default
meta_patterns: [MP-5, MP-7, MP-9, MP-13, MP-18]
---

# Substance Decode — Meta-Awareness Engine

> **Axiom (MP-5: Form-Substance Gap)**: Stated framing is an output of incentives, not a neutral summary of reality. Analyze structure, base rates, and payoff matrices before reacting to surface wording.

---

## When to Use

- **Inbound events**: Unscheduled "quick chats", unexpected contract/SLA edits, vague scope changes, unilateral delays, flattering urgency, or sudden policy explanations.
- **Outbound acts**: High-stakes emails, public posts, pricing proposals, counteroffers, or irreversible commitments.
- **Trigger alignment**: Pairs with `athena.core.gate_meta` (`T1-INBOUND` through `T8-MULTILINGUAL`) and `.agent/scripts/hook_meta_awareness_gate.py`.

---

## Part 1: Inbound Decode (Actor & Structure Analysis)

When interpreting a message, proposal, or narrative from another party, run these five steps in order:

1. **Separate Event from Narrative**:
   - Strip adjectives and intent claims. Write the bare observable facts (who initiated, what changed, what deadline was imposed, what liability shifted).
2. **Map Incentives (Cui Bono)**:
   - Ask who captures upside if you accept the surface frame, and who bears downside if the base case fails.
3. **Pull Arena Base Rates Before Reasoning**:
   - Anchor on empirical priors for that arena (see Library below) rather than giving 100% weight to this counterparty's explanation.
4. **Identify Empirical Discriminators**:
   - Specify 1–3 falsifiable observable tests that distinguish benign explanations from adversarial/extractive ones (e.g., willingness to sign mutual caps, written scope sign-off, escrow/deposit compliance).
5. **Compute Payoff-Weighted Action**:
   - Choose the move that minimizes uncompensated downside and preserves optionality while gathering discriminating evidence.

---

## Part 2: Outbound Simulation (Pre-Send Gate)

Before sending a high-leverage message, publishing a post, or locking in terms:

1. **Audience Frame Simulation**: How does an uncharitable, skeptical, or indifferent reader interpret this literally?
2. **Information Leakage Audit**: What constraint, desperation, or leverage concession does the draft reveal unnecessarily?
3. **Asymmetry & Reversibility Check**: Compare upside of sending now vs. upside of waiting 24 hours or softening irreversible commitments.
4. **Gate Execution**: If reversibility is low (`reversibility <= 2`), run full `frame_open(...)` (Strict mode) and `decision_screen(...)` before acting.

---

## Part 3: Generic Arena Base-Rate Library

| Arena | Surface Narrative | Common Operative Base-Rate Patterns | Empirical Discriminator |
|:------|:------------------|:-------------------------------------|:------------------------|
| **Employment / HR** | "Quick alignment chat", "restructuring", "culture fit" | Role elimination, PIP setup, compensation freeze, or political repositioning | Agenda transparency, written role metrics, severance/notice terms |
| **Commercial / Client** | "We just need a quick tweak", "great exposure", "standard terms" | Scope creep without budget, unpriced rush risk, delayed invoicing | Paid change-order acceptance, milestone deposit before work starts |
| **Vendor / SLA & Warranty** | "Enterprise guarantee", "standard limitation of liability" | Asymmetric risk transfer (uncapped user indemnity, broad exclusions) | Bilateral liability cap parity, objective acceptance tests, exit SLA |
| **Partnership / Equity** | "Let's shake hands and sort paperwork later", "50/50 vibes" | Ambiguous IP ownership, asymmetrical labor vs. vesting commitments | Signed IP assignment, vesting cliffs, dead-man / buyout formula |
| **Public Comms / Social** | "Setting the record straight", "calling them out publicly" | Permanent reputational tail risk for zero economic EV (short-gamma act) | Expected dollar/relationship EV of posting vs. private direct channel |

---

## Part 4: Fail-Closed Guardrails

- Never optimize inside a counterparty's pre-framed binary ("Option A or Option B") without first calling `frame_open(..., lite=True)` to inspect omitted options (`status_quo`, exit, counter-frame).
- Pair qualitative substance decoding with quantitative `decision_screen` and track resolved forecasts with `calibration_status`.
