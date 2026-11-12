---
name: operational-osint
description: Operational open-source intelligence engine for counterparty vetting, corporate registry forensics, digital footprint reconnaissance, and protective OPSEC audits.
argument_hint: "<entity, company, individual, domain, or phone> [context: client | contractor | vendor | partner | opsec]"
epistemic_status: agent-discretion
model: default
context_trigger: "osint, counterparty check, background check, due diligence, vet client, vet vendor, acra check, company check, founder check, opsec audit, investigate domain, trace counterparty"
---

# Operational OSINT (Counterparty Due Diligence & OPSEC Engine)

> "Open-source intelligence is cheap and infinite. In closed games it illuminates the board; in open games it is merely the surface lexicon. Subordinate Tier 1 surface surveillance to Tier 2 physical cash/inventory flows and Tier 3 sovereign enforcement power." — Protocol 580

This skill automates the **5-Layer Counterparty OSINT Stack** and technical digital reconnaissance to vet contractors, high-ticket clients, corporate entities, and platforms before capital, contracts, or credentials are committed. It also performs **Protective OPSEC Audits** to secure the operator's digital footprint.

---

## Triggers

Activate whenever the user:
- Asks to "vet", "check", or "investigate" a company, contractor, vendor, client, or partner.
- Mentions corporate due diligence, ACRA checks, court/litigation sweeps, or background research on an entity.
- Requests domain/URL reconnaissance, phishing payload analysis, or digital footprint mapping.
- Asks to perform an OPSEC review, digital exposure audit, or doxxing vulnerability check.

---

## Phase 1: Intake & Track Bifurcation (Stage 0 Gate)

Identify the target entity, operational track, and primary risk vector:

| Track / Entity Type | Primary Risk Vector | Target Threshold | Required Checks & Cashflow Direction |
|:---|:---|:---|:---|
| **Track A-R: High-Ticket Client (Receivable)** | Non-payment, scope extortion, delayed sign-off | >S$1,000 Contract | Binary Knockout Gate + UCDS; **Front-Load Cash** (100% upfront or 50/50 rolling retainer) |
| **Track A-P: Vendor / Contractor (Payable)** | Deposit abscondment, sub-contractor default, insolvency | >S$10,000 CapEx | Full 5-Layer Stack + Binary Knockout Gate; **Back-Load Cash** (`10/15/25/25/15/10` + 60d retention) |
| **Track A-N: Strategic Node / Founder / JV Partner** | Halo distortion, miscalibrated exit horizon, IP drag | High Variance | Full 6-Section UCDS (SWOT, Operator Utility Vector, "Builds to Exit" vs "Empire Builder", Two-Sided Error) |
| **Residential / Commercial Tenancy (Landlord / Agent)** | Sublet hijacking, deposit abscondment, unauthorized lease | >S$3,000 Deposit | 5-Point Tenancy Shield (CEA register phone match, SLA INLIS, Direct Payee, MCST, IRAS) |
| **Track B: Social / Personal Peer (Boundary Protocol)** | Boundary over-extension, unreciprocated energy | Personal / Social | **STOP commercial OSINT/profiling.** Emit strictly the 4-Part Calibrated Output Contract |
| **Digital Domain / Inbound Link / Web Platform** | Credential phishing, brand impersonation, proxy cloaking | Law #1 Ruin | WHOIS, DNS records, HTTP redirection trace, DMARC |
| **Self-Audit (Operator OPSEC)** | Asset disclosure, statutory bounty exposure, doxxing | Sovereignty | Phone/email footprint, public registry leaks, EXIF metadata |

---

## Phase 2: Execution Pipeline (Track A Only)

### 1. Statutory Registry & Control Perimeter (ACRA / SEC / Corporate Registrar)
- **Tool**: Query via search tools, official portal, or user-provided BizFile PDF.
- **Five-State Provenance Ladder**:
  - Tag each statutory field as `VERIFIED | ATTESTED | ABSENT:LAWFUL | ABSENT:SUSPICIOUS | CONTRADICTED` (distinguishing primary Class A/B registry records from self-reported claims).
  - **Singapore EPC Rule**: A solvent Exempt Private Company (<=20 individual shareholders) is legally exempt from filing financial statements with ACRA. Log missing balance sheets as `ABSENT:LAWFUL`, never as concealment or automatic insolvency.
- **Paid-Up Capital vs. Charges**:
  - Extract declared paid-up capital and check "Charges" for `satisfied` vs `outstanding` bank debentures.
- **Director & UBO History**:
  - Cross-check key directors across past dissolved entities (`People Profile`), distinguishing legitimate closures from serial debt-evasion phoenixing.

### 2. Unfiltered Digital Sentiment & Complaint Enumeration
- **Tool**: `search_web` targeting raw community repositories.
- **Dorking Matrix**:
  - `site:hardwarezone.com.sg "<entity_name>" OR "<director_name>"`
  - `site:reddit.com/r/singapore OR site:reddit.com/r/singaporefi "<entity_name>"`
  - `"<entity_name>" (scam OR delay OR court OR police OR tribunal OR lawsuit)`
  - Xiaohongshu / 小红书 video receipt query: `"<entity_name> 避雷"` (Lightning-rod / avoidance warnings).
- **Complaint Enumeration (Replaces Arbitrary Review Haircuts)**:
  - Do not apply arbitrary percentage discounts to star ratings. Instead, record two countable fields: `n_complaints` and `worst_allegation` in `{none, delay, variation_billing, defect, abandonment, abscondment}`.

### 3. Principal Track Record & Claim Verification
- **Public Footprint Evaluation**:
  - Cross-check public claims (patents, institutional backing, prior exits, reference deliveries) against primary registries (IPOS, SEC EDGAR, YC directory, university/grant rosters).
  - Flag ostentatious luxury consumption decoupled from verifiable commercial output (The Ponzi Signature).

### 4. Regulatory, License & Litigation Sweeps
- **eLitigation / State Courts**: Check for writ of summons, bankruptcy filings, or debt recovery proceedings (distinguish pending claims from adjudicated judgments).
- **Licensing & Demerits**: Check relevant industry registries (HDB DRC licensing/demerits, MOM CheckSafe / Stop-Work Orders, CASE alerts, MAS registers).

### 5. Physical Permanence, Title Forensics & Reference Check (`REFS:`)
- **Address Verification**: Confirm whether operating premises are an owned commercial property (SLA INLIS search), a verified multi-year commercial lease, or a virtual maildrop / residential base.
- **Reference Check (`REFS:`)**: Identify at least two independent prior counterparties or institutional endorsers.

### 6. Real Estate Tenancy Forensics (The 5-Point Shield)
- **Gate 1 (CEA Mobile Number Match)**: Never rely on screenshots of CEA cards or registration numbers alone. Query `eservices.cea.gov.sg/aceas/public-register/`. The mobile phone number contacting you MUST match the CEA register digit-for-digit.
- **Gate 2 (SLA INLIS Title Search)**: Spend S$5.25 on `inlis.gov.sg` (Property Ownership Information) for the exact unit. Extract legal owner full name and NRIC/FIN. Physical access/viewing does NOT prove ownership (sublet hijack attack).
- **Gate 3 (Direct Payee Invariant)**: Under CEA CEPCC regulations, agents are legally prohibited from holding transaction funds. Pay deposits ONLY to the bank/PayNow account matching the INLIS owner.
- **Gate 4 (MCST / Guardhouse Recon)**: Cross-check with condominium management if the unit has active complaints regarding unauthorized transient/short-term rentals.
- **Gate 5 (IRAS Stamp Duty Certificate)**: Verify the tenancy agreement reference code on `mytax.iras.gov.sg` prior to balance disbursement.

---

## Phase 3: Binary Knockout Gates & Directional Risk Inversion

### 1. Non-Compensatory Binary Knockout Gate (Booleans Gate; Scores Only Order)
Immediately trigger **HARD VETO (RED under Law #1)** if ANY of the following is true:
- Active bankruptcy petition or undischarged insolvency.
- Unsatisfied civil court judgment for commercial default or fraud.
- Unlicensed operation in a statutorily regulated trade.
- Demanding personal bank / personal PayNow remittance for a corporate contract.
- Corroborated history of site abandonment or deposit abscondment.

*No amount of charisma, pedigree, or technical capability can offset a triggered knockout gate.*

### 2. Directional Payment Matrix (Preventing Cashflow Inversion)
- **Track A-R (Selling to a Client — Receivable)**:
  - Risk is non-payment after labor delivery. **Front-load cash**: 100% upfront for small tickets; 50/50 rolling retainers or Cash-Before-Delivery (CBD) for core tickets. Labor never outpaces cleared funds.
- **Track A-P (Buying from a Vendor/Contractor — Payable)**:
  - Risk is non-delivery after deposit payment. **Back-load cash**: Parity milestone schedule (`10% deposit / 15% / 25% / 25% / 15% / 10%` completion + 60-day defect retention). Cash disbursements never outpace verified physical work on site.
- **Track A-N (Partnering with a Founder / Node)**:
  - Match contract horizon to their Exit Mode (`Builds to Exit` vs `Empire Builder`). Never sign perpetual rev-shares with a short-cycle campaign operator; align on short-term milestones and clean IP boundaries.

---

## Phase 4: Output Dossier Template — Universal Counterparty Dossier Standard (UCDS)

For all **Track A (`A-R | A-P | A-N`)** evaluations, output the standardized **6-Section UCDS Dossier** and verify structural compliance with `python3 examples/scripts/ucds_audit.py --dossier <dossier.md>`:

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

### Track B: Social & Interpersonal Boundary Contract

When the target is a **personal, social, or everyday peer contact (Track B)**, criminal profiling (`MO / Signature / Staging`), clinical wound stacks, and numeric scorecards are **strictly prohibited**. Emit only the **4-Part Calibrated Output Contract**:
1. **Observed / Reported Behavior** (Stripped of adjectives and mind-reading).
2. **Plausible Interpretations** (Equi-probable benign vs. instrumental base rates).
3. **Epistemic Boundaries** (What the evidence cannot distinguish).
4. **Proportionate Action** (Practical boundary matched to observed reciprocity under Law #3).
