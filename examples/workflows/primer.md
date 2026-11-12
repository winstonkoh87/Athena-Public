---
description: Generate comprehensive AI system briefing for external audit
created: 2025-12-18
last_updated: 2026-07-22
---
# /primer — External Audit Briefing (Hardened)

> **Purpose**: Full self-disclosure for external review. Control Framework focus.
> **Output 1**: `docs/audit/SYSTEM_PRIMER_FULL.md` (Internal Ops Brief)
> **Output 2**: `docs/audit/SYSTEM_PRIMER_REDACTED.md` (External Audit Brief)
> **Audience**:
>
> - Internal: System self-reference (Ops)
> - External: AI Auditor / Public Audit (Governance)

---

## Execution Protocol

When `/primer` is invoked:

// turbo-all

### Phase 1: Read Full System Context

Load the following files (in order):

1. **Governance & Risk**
   - `notes/profile/Constraints_Master.md` (Risk Tiers, Ethics, Boundaries)
   - `docs/audit/RISK_REGISTER.md` (Threat Model)
   - `docs/audit/DATA_GOVERNANCE.md` (Policy)

2. **Core Identity**
   - `.framework/v7.0/modules/Core_Identity.md` (Laws #0-5, ICR/HITLO Model, COS)

3. **User Context (FULL DISCLOSURE)**
   - `notes/profile/User_Profile_Core.md` (Identity, Bio, Typology)
   - `notes/profile/System_Principles.md` (Decision frameworks, values)
   - `notes/profile/[PRIVATE_MODULE].md` ([PRIVATE_MODULE], history)
   - `notes/profile/Business_Frameworks.md` (Mental models, strategies)
   - `notes/profile/Session_Observations.md` (Calibration patterns, cases)

4. **Architecture**
   - `.framework/v8.2-stable/modules/System_Manifest.md`
   - `.context/PROJECTS.md` (Tech stack, active patterns)
   - List active workflows in `.agent/workflows/`
   - List protocols in `.agent/skills/protocols/` (count + categories)

5. **Memory & Skill Index**
   - `.context/PROTOCOL_SUMMARIES.md` (Protocol/topic discovery)
   - `.agent/skills/SKILL_INDEX.md` (Capability registry)

6. **Metrics**
   - Check latest session log for session count, calibration score
   - Run `python3 .agent/scripts/analyze_cost.py` for token economics

---

### Phase 2: Compile Dual-Track Documents

#### Track A: Internal Ops Brief (Full Disclosure)

Generate `docs/audit/SYSTEM_PRIMER_FULL.md`.
- **Content**: EVERYTHING listed above (Sections 1-9).
- **Header**: `> CLASSIFICATION: L3 SYSTEM EYES ONLY`
- **Psychology**: Include raw "[NAME]" profiles, L5 schema details, [PRIVATE_CONCEPT].
- **Risk**: Include specific R00X triggers and financial thresholds.

#### Track B: External Audit Brief (Redacted)

Generate `docs/audit/SYSTEM_PRIMER_REDACTED.md`.
- **Content**: Sections 1-9, but SANITIZED.
- **Header**: `> CLASSIFICATION: PUBLIC / AUDITABLE`
- **Redactions**:
  - Replace specific net worth/financials with "Threshold defined".
  - Replace "[NAME]" and raw L5 trauma details with "Shadow Persona" and "Core Wound".
  - Remove any mention of specific individuals or private legal cases.
  - Summarize R00X triggers abstractly (e.g. "Impulse Control Event").
- **Focus**: Prove *Controls* exist, without exposing *Vulnerabilities*.

> **Design Principle**:
>
> - Internal = Raw Truth (for debugging).
> - External = Proof of Competence (for trust).

---

### Phase 3: Save & Verify

1. Create `docs/audit/SYSTEM_PRIMER_FULL.md` (Ops)
2. Create `docs/audit/SYSTEM_PRIMER_REDACTED.md` (Audit)
3. Git commit: `docs: generate dual-track system primers (ops/audit)`
4. Confirm: "✅ Primer generated. Ready for external audit."

---

## Tagging

# workflow #audit #primer #governance #risk-management
