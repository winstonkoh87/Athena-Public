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

## Phase 1: Intake & Reconnaissance Scoping

Identify the target entity and primary risk vector:

| Entity Type | Primary Risk Vector | Target Threshold | Required Checks |
|:---|:---|:---|:---|
| **Commercial Contractor / Interior Design** | Deposit abscondment, sub-contractor default, insolvency | >S$10,000 CapEx | Full 5-Layer Stack (ACRA, Forums, XHS, INLIS, HDB DRC) |
| **High-Ticket Freelance / Consulting Client** | Payment refusal, scope inflation, regulatory exposure | >S$1,000 Contract | ACRA / Corporate status, LinkedIn, eLitigation, Payment terms |
| **Joint Venture / Co-Founder / Business Partner** | Serial shell phoenixing, debt encumbrances, reputation drag | High Variance | People Profile director history, debt charges, lifestyle audit |
| **Digital Domain / Inbound Link / Web Platform** | Credential phishing, brand impersonation, proxy cloaking | Law #1 Ruin | WHOIS, DNS records, HTTP redirection trace, DMARC |
| **Self-Audit (Operator OPSEC)** | Asset disclosure, statutory bounty exposure, doxxing | Sovereignty | Phone/email footprint, public registry leaks, EXIF metadata |

---

## Phase 2: Execution Pipeline

### 1. Statutory Registry Forensics (ACRA / Corporate Registrar)
- **Tool**: Query via search tools, official portal, or user-provided BizFile PDF.
- **Paid-Up Capital vs. Charges**:
  - Extract declared paid-up capital.
  - Check "Charges" section for `ALL MONIES` debentures or banking liens. If total registered banking charges dwarf paid-up capital, entity is leveraged to the brink.
- **Director History (The Graveyard Check)**:
  - Cross-check key directors across past dissolved entities.
  - Flag any history of serial struck-off entities within 3-4 years (phoenix company pattern).

### 2. Unfiltered Digital Sentiment & Laundering Forensics
- **Tool**: `search_web` targeting raw community repositories.
- **Dorking Matrix**:
  - `site:hardwarezone.com.sg "<entity_name>" OR "<director_name>"`
  - `site:reddit.com/r/singapore OR site:reddit.com/r/singaporefi "<entity_name>"`
  - `"<entity_name>" (scam OR delay OR court OR police OR tribunal OR lawsuit)`
  - Xiaohongshu / 小红书 video receipt query: `"<entity_name> 避雷"` (Lightning-rod / avoidance warnings).
- **Sentiment Haircut**:
  - Calculate delta between sponsored Google Reviews (often farmed 4.8+) and aggregator/forum ratings. Apply 30% to 40% discount to official review averages.

### 3. Principal Lifestyle vs. Balance Sheet Audit
- **Public Footprint Evaluation**:
  - Review public social profiles (LinkedIn, IG, Facebook) of key founders.
  - Check for ostentatious luxury consumption (supercars, VIP nightlife, luxury watches) that is unanchored to proven corporate profitability (The Ponzi Signature).

### 4. Regulatory & Litigation Sweeps
- **eLitigation / State Courts**: Check for pending writ of summons, bankruptcy filings, or debt recovery proceedings.
- **Licensing & Demerits**: Check relevant industry registries (e.g. HDB DRC licensing and demerit points, MOM workplace safety orders, CASE alerts).

### 5. Physical Permanence & Title Forensics
- **Address Verification**: Confirm whether the operating premises are an owned commercial property (SLA INLIS search), a verified multi-year commercial lease, or a virtual maildrop.

---

## Phase 3: Risk Scoring & Contract Risk Inversion

Score the counterparty on the **100-Point Audit Scale** (see Protocol 580):
- **Statutory Standing** (0–20 pts)
- **Review Integrity** (0–20 pts)
- **Financial Posture** (0–20 pts)
- **Legal History** (0–20 pts)
- **Physical Permanence** (0–20 pts)

### Triage Verdict & Action Matrix:
- **Green (85–100 pts)**: Proceed under standard commercial terms.
- **Amber (65–84 pts)**: Conditional approval with **Contract Risk Inversion**:
  - Back-heavy milestone schedule (e.g. 10% deposit / 15% / 25% / 25% / 15% / 10% completion retention).
  - Escrow or Cash-Before-Delivery (CBD) tranches for client work.
  - Zero uncollateralized pre-payments for materials.
- **Red (<65 pts)**: **HARD VETO under Law #1**. Immediate disengagement.

---

## Phase 4: Output Dossier Template

When reporting findings, format output into this clean dossier:

```markdown
### 🛡️ Operational OSINT Dossier: [Entity / Counterparty Name]

**Audit Date**: YYYY-MM-DD  
**Overall Risk Score**: XX / 100 ([Green / Amber / Red])  
**Recommendation**: [Proceed Unconditional | Proceed Conditional | Hard Veto]

#### 1. Statutory & Corporate Profile
- **Entity**: [Name] (UEN: [Number]) | Status: [Live / Dissolved]
- **Paid-Up Capital vs. Charges**: [Paid-up capital] vs. [Senior charges / Bank liens]
- **Director Graveyard Check**: [Clean / Serial dissolutions detected]

#### 2. Digital Sentiment & Ground Truth
- **Official vs. Raw Sentiment**: [Google rating] vs. [Forum / XHS / Aggregator findings]
- **Key Community Grievances**: [Specific complaints or clean operational record]

#### 3. Legal & Regulatory Standing
- **Litigation / Regulatory Status**: [Clean / Active suits / CASE notices / MOM orders]
- **Physical Footprint**: [Owned / Multi-year lease / Virtual office]

#### 4. Red Flags & Vulnerabilities
- [Red flag 1 or 'None detected']
- [Red flag 2]

#### 5. Strategic Prescription (Contract Hardening)
- [Specific milestone structure, payment terms, or protective clauses to enforce]
```
