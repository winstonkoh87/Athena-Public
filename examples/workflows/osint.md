---
description: Operational OSINT workflow — statutory registry forensics, digital footprint sweeps, and Universal Counterparty Dossier Standard (UCDS)
created: 2026-10-05
last_updated: 2026-11-13
---
# /osint — Execution Script

> **Purpose**: Systematic counterparty due diligence, public footprint reconnaissance, and Universal Counterparty Dossier Standard (UCDS) compilation.
> **Philosophy**: Ground truth first. Never analyze an entity in a vacuum. First extract whatever objective public data exists (statutory, sentiment, litigation, infrastructure), run binary knockout gates, then compile the 6-Section UCDS (or route personal contacts to the Track B 4-Part Boundary Contract).
> **Protocol Reference**: [RSC-580: Operational OSINT & Counterparty Reconnaissance](../protocols/research/RSC-580-operational-osint-and-counterparty-reconnaissance.md)
> **Skill Reference**: [operational-osint](../skills/research/operational-osint/SKILL.md)
> **Validator**: `python3 examples/scripts/ucds_audit.py --dossier <dossier.md>`

---

## The 3-Tier Cognitive Intake Funnel

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 3-TIER INTAKE FUNNEL                        │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Public Reality (OSINT) ──► Registries, Reviews, Litigation,│
│                                        Footprint, Domain/DNS           │
│ Step 2: Internal Exocortex Recall  ──► Synthesized parallels, past case│
│                                        studies, failure signatures     │
│ Step 3: Game-Theoretic Synthesis   ──► Knockout Gates, SWOT, Utility,  │
│                                        Directional Payment Terms       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Execution Sequence

When `/osint [target]` is invoked:

### Step 1: Intake & Track Bifurcation (Stage 0 Gate)
Classify the target into one of five operational tracks before running reconnaissance:
1. **Track A-R — Client / Accounts Receivable**: Inbound commercial client (>S$1,000). Primary risk: non-payment, scope extortion. Mandate: **Front-load cash** (labor never outpaces cleared funds).
2. **Track A-P — Vendor / Contractor / Accounts Payable**: Commercial vendor or contractor (>S$10,000). Primary risk: deposit abscondment, insolvency, non-delivery. Mandate: **Back-load cash** (parity milestones `10/15/25/25/15/10` + 60-day defect retention).
3. **Track A-N — Strategic Node / Founder / JV Partner**: Founder, potential co-builder, or ecosystem node. Primary risk: halo distortion, miscalibrated horizon expectations, IP leakage. Mandate: **Full 6-Section UCDS** (SWOT, Operator Utility Vector, "Builds to Exit" vs "Empire Builder" horizon, Two-Sided Error Accounting).
4. **Track B — Social / Interpersonal Peer**: Colleagues, acquaintances, dating prospects, informal networkers. **STOP commercial OSINT and criminal profiling.** Route exclusively to the **4-Part Calibrated Output Contract** (Observed Behavior -> Plausible Base Rates -> Epistemic Limits -> Proportionate Boundaries).
5. **Technical Link / Operator OPSEC (Self-Audit)**: WHOIS age, DNS records, redirection trace, or exposed personal contact/metadata audit.

---

### Step 2: Execute the 5-Layer OSINT Stack (Track A Only)

Run live external searches via `search_web`, web retrieval tools, or user-provided documents:

1. **Layer 1: Statutory Registry & Control Perimeter (ACRA BizFile+ / SEC / Registrar)**
   - Record every statutory field using the **5-State Provenance Ladder**: `VERIFIED | ATTESTED | ABSENT:LAWFUL | ABSENT:SUSPICIOUS | CONTRADICTED` (or mark self-reported marketing claims explicitly as unverified staging).
   - *Singapore EPC Rule*: A solvent Exempt Private Company (<=20 individual shareholders) is legally exempt from filing financial statements with ACRA. Log missing balance sheets as `ABSENT:LAWFUL`, never as concealment or automatic insolvency.
   - Audit registered charges (`satisfied` vs `outstanding`), UBO/director turnover in the last 12 months, and past entity strike-offs (context for phoenixing vs legitimate closure).
2. **Layer 2: Unfiltered Digital Sentiment & Complaint Enumeration**
   - Query raw ground-truth repositories: HardwareZone EDMW, Reddit (r/singapore, r/singaporefi), RenoTalk, Xiaohongshu / 小红书 video receipts (`"<name>" 避雷`).
   - Search for dispute keywords: `"<name>" (scam OR delay OR lawsuit OR court OR police)`.
   - Replace arbitrary percentage review haircuts with two countable metrics: `n_complaints` and `worst_allegation` in `{none, delay, variation_billing, defect, abandonment, abscondment}`.
3. **Layer 3: Principal Track Record & Claim Verification**
   - Cross-check public claims (patents, institutional backing, prior exits, reference deliveries) against primary registries (IPOS, SEC EDGAR, YC directory, university/grant rosters).
   - Check public profiles for ostentatious luxury consumption decoupled from verifiable corporate earnings (The Ponzi Signature).
4. **Layer 4: Regulatory, License & Litigation Perimeter**
   - Check civil cause books (eLitigation / State Courts — distinguish pending claims from adjudicated judgments), CASE consumer alerts, MOM CheckSafe / Stop-Work Orders, HDB DRC demerit points, and MAS registers.
5. **Layer 5: Physical Permanence & Reference Verification (`REFS:`)**
   - Verify operational premises: Owned commercial asset (SLA INLIS title search), multi-year verified lease, or virtual maildrop / residential base?
   - Identify at least two independent references or institutional endorsers (`REFS:`).

---

### Step 3: Binary Knockout Gate & Exocortex Triangulation

1. **Non-Compensatory Binary Knockout Gate (Booleans Gate; Scores Only Order)**:
   - Immediately trigger **HARD VETO (RED)** if ANY of the following holds:
     - Active bankruptcy petition or undischarged insolvency.
     - Unsatisfied court default judgment for commercial non-payment or fraud.
     - Unlicensed operation in a statutorily regulated trade (e.g., MAS, CEA, HDB DRC).
     - Demanding personal bank / personal PayNow remittance for a corporate contract.
     - Credible, corroborated evidence of site abandonment or deposit abscondment.
   - *No amount of charisma, pedigree, or technical capability can offset a triggered knockout gate.*
2. **Exocortex Recall (`smart_search`)**:
   - Search internal memory for entity name, industry niche, and structural parallels: bust-out or phoenix shell patterns, uncollateralized contractor default signatures, high-friction client milestone structures, or unilateral concession traps.

---

### Step 4: Output Dossier — The Universal Counterparty Dossier Standard (UCDS)

For all **Track A (`A-R | A-P | A-N`)** evaluations, emit the standardized **6-Section UCDS Dossier** and verify structural compliance with `python3 examples/scripts/ucds_audit.py --dossier <dossier.md>`:

```markdown
================================================================================
                    COUNTERPARTY INTELLIGENCE DOSSIER (UCDS)
================================================================================
TARGET:         [Full Legal / Known Name]
ROLE / ENTITY:  [Current Title, Legal Entity Name, UEN / Registration Status]
TRACK:          [Track A-R (Client) | Track A-P (Vendor) | Track A-N (Node/Founder)]
KNOCKOUT GATE:  [PASS | FAIL -> HARD VETO (Law #1)]
ARCHETYPE:      [Non-Decisional Functional Label: e.g. Tactical Engine / Diplomat]
OPERATING MODE: [Campaign Operator ("Builds to Exit") | Empire Builder | Mercenary]
================================================================================

1. GROUND TRUTH & PERIMETER VERIFICATION
   • Verified Facts [VERIFIED]:     [Statutory status, verified IP/patents, confirmed backing]
   • Marketing / Staging [ATTESTED]:[Self-reported claims vs. operative structural reality]
   • Unobtainables:                 [ABSENT:LAWFUL (e.g. EPC accounts) | ABSENT:SUSPICIOUS]
   • Complaint Tally:               [n_complaints | worst_allegation: none/delay/defect/abandonment]
   • References (REFS):             [Verified institutional endorsers or prior counterparties]

2. THE 360-DEGREE SWOT
   • Strengths:     [Verified execution horsepower, proprietary IP, unfair advantages]
   • Weaknesses:    [Internal blind spots, demographic/procurement friction, bottlenecks]
   • Opportunities: [Asymmetric doors or synergies opened for our ecosystem]
   • Threats:       [Downside tail risk, compliance/SEC drag, attention leakage]

3. VALUE TO US (The Operator Utility Vector)
   • Direct Utility (Now):    [Immediate revenue, technical sparring, live market intel]
   • Long-Term Optionality:   [Strategic call options, sovereign/VC network bridge]
   • Energy / Friction Ratio: [Maintenance cost vs. autonomous output]

4. HORIZON FORECAST & EXIT PROFILE ("BUILDS TO EXIT" vs. "EMPIRE BUILDER")
   • Terminal Stance:         [24-36m M&A Liquidity Sprint vs. 10-Year Domain Steward]
   • 3-to-5 Year Branches:    [Probabilistic career/company scenarios & base rates]
   • Behavioral Invariants:   [What this operator will NEVER do based on revealed preference]
   • Contractual Horizon Rule:[How to align term length and IP boundaries to their clock]

5. TWO-SIDED ERROR ACCOUNTING (Type 1 vs. Type 2)
   • Type 1 Error (False Positive / Paranoia Tax):
     - Cost of rejecting/dismissing them if they are legitimate.
   • Type 2 Error (False Negative / Ruin Trap):
     - Maximum irrecoverable damage if they default or are fraudulent.
   • Re-Entry Condition:      [What observable milestone changes the current verdict]

6. ENGAGEMENT PLAYBOOK & LITMUS TEST
   • Directional Payment / Commercial Stance:
     - [Track A-R Client: Front-load cash (100% upfront or 50/50 rolling retainer)]
     - [Track A-P Vendor: Back-load cash (10/15/25/25/15/10 + 60d retention)]
     - [Track A-N Partner/Peer: Short-cycle milestones, clean IP demarcation]
   • Conversational Protocol: [Talk mechanism-to-mechanism; what triggers respect vs friction]
   • The Litmus Test:         [Single mechanism question or standard constraint to verify]
================================================================================
```

---

### Step 5: Track B — Social & Interpersonal Boundary Contract

When `/osint` or profiling is requested on a **personal, social, or everyday peer contact (Track B)**, criminal profiling (`MO / Signature / Staging`), clinical wound stacks, and numeric personality scorecards are **strictly prohibited**. Emit only the **4-Part Calibrated Output Contract**:
1. **Observed / Reported Behavior**: Strictly what was said or done, stripped of adjectives.
2. **Plausible Interpretations (Equi-Probable Base Rates)**: Both the benign/ordinary situational reading and the instrumental reading.
3. **Epistemic Boundaries**: What the evidence cannot distinguish.
4. **Proportionate Action**: Practical boundary matched to observed reciprocity without character demonization.

### Escalation

- Pass verified `red_endowments` and observable counterparty leverage into [`/wargame`](wargame.md) when adversarial counter-moves must be stress-tested.
