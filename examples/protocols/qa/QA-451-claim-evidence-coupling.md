---
id: QA-451
title: Claim-Evidence Coupling Gate
category: qa
status: active
tags: [telemetry, verification, claims, evidence, anti-theater, audit, session-close]
created: 2026-08-27
last_updated: 2026-08-27
origin: "Epistemic Rigor & Anti-Telemetry-Theater Directive"
dependencies: ["ARC-159 (Verification Before Claim)", "DEC-185 (Premise Validation Gate)"]
---

# QA-451: Claim-Evidence Coupling Gate

> **Domain**: Quality Assurance / Epistemic Auditing / Verification  
> **Prime Directive**: Any assertion of protocol firing, engine calculation, mathematical modeling, or historical precedent MUST be coupled directly with verifiable evidence artifacts. Assertions without proof are unverified narration.  
> **Anti-Theater Rule**: Listing protocol IDs, cluster sequences, or theoretical formulas to create the cosmetic illusion of rigor without executing the underlying mechanics is strictly prohibited.  
> **Related Protocols**: [ARC-159: Verification Before Claim](../architecture/ARC-159-verification-before-claim.md), [DEC-185: Premise Validation Gate](../decision/DEC-185-premise-validation-gate.md)

---

## 1. Core Mandate: Coupling Requirement

Every analytical report, case study, advisory output, or session log generated within Athena that claims mechanical execution must satisfy the **Claim-Evidence Coupling Gate**.

```
CLAIM-EVIDENCE COUPLING PRINCIPLE:
┌─────────────────────────────────────────────────────────┐
│ Claim without Evidence  = Cosmetic Telemetry (Zero Value)│
│ Claim + Evidence Link   = Auditable Rigor (High Value)  │
│                                                         │
│ RULE: If a calculation or protocol activation is       │
│       asserted in text, the exact mechanical footprint  │
│       MUST appear in the output.                        │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Required Evidence Types

Claims are classified into four distinct categories. Each category requires an explicit evidence artifact:

| Claim Category | Assertion Pattern | Mandatory Evidence Artifact | Non-Compliant Example (Disallowed) |
|:---|:---|:---|:---|
| **1. Protocol Activation** | "Protocol DEC-330 activated", "Cluster #15 -> #7 -> #9 fired" | • Clickable path to protocol file (`file:///...`)<br>• Specific rule/threshold quoted<br>• Explicit evaluation against case data | "Fired DEC-330 and STR-121 during analysis." *(No rules quoted, no linkage)* |
| **2. Mathematical Engine** | "EEV is +$2.38/hr", "Kelly fraction is 5.2%", "Monte Carlo 95% CI" | • Complete itemized math table<br>• Explicit inputs, formula, and intermediate steps<br>• Full parameter definitions | "Ran EEV engine and determined setup is positive." *(No table or inputs)* |
| **3. Case Precedent** | "Matches Case CS-42 pattern", "Precedent from Session 12" | • Precise Case ID / Session ID<br>• Verifiable file link or exact section citation<br>• Explicit parallel mapping of variables | "Historical case precedents confirm this thesis." *(Vague, unlinked)* |
| **4. Financial Projection** | "Net cash proceeds: S$180K", "Expected annual yield: 8.4%" | • Complete netting schedule breakdown<br>• Itemized deductions (fees, taxes, CPF accrued interest, debt payoff) | "Expected upside is S$200K-400K after sale." *(Gross estimate without deductions)* |

---

## 3. Epistemic Tagging Standards

Every technical or empirical claim in case studies and analytical summaries must carry an explicit epistemic status tag:

```
┌─────────────────────────┐
│     EPISTEMIC TAGS      │
├─────────────────────────┤
│ [VERIFIED]              │ ◄── Artifact attached, calculated, verified
├─────────────────────────┤
│ [NARRATED, UNVERIFIED]  │ ◄── Claim made without attached proof
├─────────────────────────┤
│ [INFERRED]              │ ◄── Deductive inference; plausible but not mechanical
└─────────────────────────┘
```

### Tagging Definitions:
1. `[VERIFIED]`:
   - The evidence artifact is directly present in the file (e.g., full mathematical breakdown, exact code execution snippet, verified file link with quoted section).
2. `[NARRATED, UNVERIFIED]`:
   - An assertion of fact, precedent, or protocol firing made in prose where no underlying mathematical table, citation, or telemetry log is attached.
3. `[INFERRED]`:
   - A logical deduction or probabilistic assessment based on known principles, clearly identified as an inference rather than an empirical calculation.

---

## 4. Session Close (`/end`) Enforcement Gate

During session wrap-up or whenever case studies/protocols are committed to the repository, the following audit rule is enforced:

```
SESSION CLOSE AUDIT WORKFLOW:
┌─────────────────────────────────────────────────────────┐
│ Scan new/updated Case Studies & Advisories for Claims:  │
│                                                         │
│ 1. Scan for protocol activation claims                  │
│    (e.g., "Protocol XYZ fired", "Cluster ABC applied")  │
│                                                         │
│ 2. Check for attached evidence artifact:                │
│    ├─ Evidence attached? ──► Tag: [VERIFIED]            │
│    └─ No evidence?       ──► Tag: [NARRATED, UNVERIFIED]│
│                                                         │
│ 3. MANDATE: Resolve or tag all unverified claims        │
│    BEFORE final git commit.                             │
└─────────────────────────────────────────────────────────┘
```

> **Enforcement Rule**: If an agent writes a case study stating that "11 protocols were activated" or "Cluster #15 fired", but the text lacks the step-by-step audit trail, the agent MUST prepend `[NARRATED, UNVERIFIED]` to that section before the commit is finalized.

---

## 5. Audit Checklist & Verification Matrix

Before finalizing any case study or strategic advisory document, run this 5-point verification check:

| # | Verification Question | Pass Requirement | Status |
|:--|:---|:---|:---|
| **1** | Did every cited protocol include a clickable file link and the exact rule applied? | Every protocol ID has a valid `file:///...` path and rule reference. | [ ] |
| **2** | Did every financial or probability projection include an itemized calculation block? | Full equation and inputs displayed in ASCII table. | [ ] |
| **3** | Are all referenced case studies identifiable by exact ID and section? | No vague references ("previous cases show..."). | [ ] |
| **4** | Are unverified assertions explicitly labeled as `[NARRATED, UNVERIFIED]`? | Zero unverified claims disguised as verified facts. | [ ] |
| **5** | Is the document completely free of cosmetic telemetry strings? | No empty "Cluster #1→#2→#3" decorations. | [ ] |

---

## 6. Anti-Patterns & Telemetry Theater

| Anti-Pattern | Manifestation | Corrective Directive |
|:---|:---|:---|
| **Telemetry Theater** | Decorating headers with strings like `[Cluster #15→#7→#9 Active] [11 Protocols Fired]` without showing how those protocols altered the output. | Remove the decorative string OR provide the specific rule activation trace for each protocol. |
| **Phantom Math** | Stating "Running Kelly Criterion / Monte Carlo indicates 65% allocation" without displaying the Kelly equation or probability inputs. | Attach the complete equation block with all variables (`b`, `p`, `q`, `f*`). |
| **Ghost Precedent** | Appealing to authority via "As proven in previous Athena sessions" without supplying the exact session number and transcript anchor. | Link the exact file path or redact the appeal to precedent. |
| **Gross Upside Handwaving** | Quoting round revenue or profit numbers without itemized netting (ignoring taxes, fees, and CPF refunds). | Execute [DEC-449 Matrimonial Asset Netting Calculator](../decision/DEC-449-matrimonial-asset-netting.md) or standard financial deduction schedules. |

---

## Tags

#qa #telemetry #verification #claims #evidence #anti-theater #audit #epistemics
