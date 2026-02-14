---
created: 2025-12-12
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: bs-detection-protocol
description: Systematic validation checklist for knowledge extraction. Identifies naming collisions, internal contradictions, operational friction, and psychological mismatches.
created: 2025-12-12
last_updated: 2026-01-05
---

# Protocol 47: BS Detection (Knowledge Validation)

> **Source**: /ultrathink validation of ZenithFX Primer (Dec 2025)  
> **Trigger When**: Synthesizing knowledge from multiple documents, validating frameworks, or reviewing extracted insights

---

## Purpose

When extracting frameworks from large document corpora, apply this checklist to identify "bullshit" — well-intentioned but flawed concepts that should be rejected or revised before operationalization.

---

## The BS Detection Checklist

### 1. Naming Collision Check

**Question**: Does the term conflict with industry-standard definitions?

| Signal | Example | Action |
|--------|---------|--------|
| Acronym already in use | "SIP" (used for Systematic Investment Plan) | Rename to avoid confusion |
| Overloaded term | "Alpha" meaning different things | Add qualifier or context |

---

### 2. Internal Contradiction Check

**Question**: Does this concept contradict foundational principles in the same corpus?

| Signal | Example | Action |
|--------|---------|--------|
| Risk % exceeds survival doctrine | Q4's 8% risk vs Q2's "RoR < 5%" | Reject or downgrade |
| Strategy conflicts with stated psychology | Low WR system for validation-seeker | Deprecate for operator |

**Method**: Cross-reference new concept against "Law 0" or "First Principles" sections.

---

### 3. Operational Friction Check

**Question**: Can this be executed in real-time, or is it a "lab-only" metric?

| Category | Use | Examples |
|----------|-----|----------|
| **Live Ops** | During trade execution | Checklists, Sizing, ATR stops |
| **Lab/Review** | Post-trade analysis | Execution Efficiency, Capture Rate, Process Grading |

**Action**: Split primers into "Cockpit" (real-time) and "Lab" (review) sections.

---

### 4. Psychological Fit Check

**Question**: Does this align with the operator's known profile, or is it aspirational noise?

| Operator Profile | Good Fit | Bad Fit |
|------------------|----------|---------|
| INTJ-6w5 (Needs validation) | High WR systems | Low WR "faith-based" systems |
| High Compulsivity (70-90%) | External kill-switches | Self-enforced discipline |

**Action**: Mark incompatible frameworks as "REJECTED for Operator" or require external enforcement.

---

## Application

When running `/ultrathink` or `/research` on a knowledge corpus:

1. Extract frameworks as normal
2. Run each through the 4-point BS Detection Checklist
3. Flag issues with severity:
   - **DANGEROUS**: Could cause ruin (e.g., over-Kelly risk)
   - **CONFUSING**: Naming or structural issues (e.g., SIP collision)
   - **FRICTION**: Operational impracticality (won't be used in real-time)
   - **OBSOLETE**: Already rejected or superseded

4. Document findings before finalizing any primer or protocol

---

## Example Output

```
## BS Detection Report

1. **8% Risk Tier** → DANGEROUS
   - Contradicts Q2 survival doctrine
   - Verdict: Remove, cap at 4%

2. **"SIP-V1" Naming** → CONFUSING
   - Collides with "Systematic Investment Plan"
   - Verdict: Rename to "RW-ATR"

3. **Execution Efficiency Metric** → FRICTION
   - Cannot calculate in real-time
   - Verdict: Move to "Lab/Review" section

4. **System 2 (Low WR)** → OBSOLETE
   - Rejected for INTJ-6w5 operator in Q4
   - Verdict: Deprecate
```

---

> **Core Principle**: A framework is only as useful as its operational validity. If it can't be executed, contradicts survival, or conflicts with operator psychology, it's bullshit — no matter how elegant the theory.

---

## Tagging

#protocol #framework #process #47-bs-detection

## Related Protocols

- [Protocol 115: First Principles Deconstruction](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/115-first-principles-deconstruction.md)
