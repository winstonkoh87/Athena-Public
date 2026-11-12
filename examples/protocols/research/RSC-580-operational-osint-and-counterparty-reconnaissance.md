---
name: operational-osint-and-counterparty-reconnaissance
description: Operational OSINT protocol for counterparty vetting, corporate registry forensics, digital footprint reconnaissance, and protective OPSEC audits.
created: 2026-10-05
last_updated: 2026-10-05
tags: [protocol, research, osint, counterparty-risk, due-diligence, opsec]
epistemic_status: code-enforced
---

# Protocol 580: Operational OSINT & Counterparty Reconnaissance

> **Purpose**: Systematic open-source intelligence framework for counterparty vetting, corporate structure verification, digital infrastructure reconnaissance, and protective OPSEC audits.
> **Origin**: Codified from counterparty due diligence, corporate registry forensics, and e-commerce reconnaissance frameworks.
> **Trigger**: Vetting high-ticket counterparties (clients >S$1,000, vendors/contractors >S$10,000, partners), investigating suspicious domains/accounts, or conducting self-footprint OPSEC sweeps.

---

## 1. Foundational Axioms & The Open Game Boundary

Open-source intelligence is cheap, abundant, and represents only the surface lexicon. In strategic analysis, OSINT must never be confused with complete causal truth.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 3-TIER OPEN-GAME CAUSAL HIERARCHY                 │
├────────────────────────────────────────────────────────────────────────┤
│ Tier 1: Surface OSINT         ──► Registries, social feeds, PR copy    │
│ Tier 2: Physical & Flow State ──► Banking pipes, inventory, escrows    │
│ Tier 3: Sovereign Utility     ──► Rule-changing power, legal monopoly  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **The Closed vs. Open Game Trap**:
   - *Closed Games* (chess, sports, regulated exchanges) assume static rules, fixed players, and observable boards. Tier 1 OSINT provides high explanatory power.
   - *Open Games* (commercial disputes, predatory syndicates, cross-border capital, sovereign statecraft) permit adversaries to rewrite the rules, nationalize order books, or ignore contracts.
2. **Subordination Rule**:
   - Tier 1 OSINT establishes the *formal footprint*.
   - Tier 2 Constraints establish the *operative capacity* (can they actually deliver or pay?).
   - Tier 3 Power establishes the *enforceability boundary* (if they default, who holds the ultimate stick?).
3. **Law #1 Compliance (No Irreversible Ruin)**:
   - An unvetted counterparty in high-ticket transactions (>S$10,000 CapEx or S$100,000 renovation/equity) represents an unhedged catastrophic downside. A S$5.50 registry profile or a 15-minute search sweep can prevent six-figure wipeouts.

---

## 2. The 5-Layer Counterparty OSINT Stack

When evaluating commercial entities, corporate vendors, high-ticket clients, or joint-venture partners, execute across all five layers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 5-LAYER COUNTERPARTY OSINT STACK                 │
├────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Statutory Registry (ACRA/BizFile) ──► Capital, Charges, Graveyard│
│ Layer 2: Unfiltered Digital Sentiment     ──► Forums, XHS, Review Haircut│
│ Layer 3: Principal & Lifestyle Forensics   ──► Lifestyle vs Capital Drag│
│ Layer 4: Regulatory Disciplinary Sweeps    ──► Cause Books, MOM, CASE   │
│ Layer 5: Asset Title & Physical Footprint  ──► SLA INLIS, Lease Checks  │
└────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Statutory Registry Forensics (ACRA BizFile+ / Regional Registrar)
- **Five-State Provenance Ladder**:
  - Tag every statutory field as `VERIFIED | ATTESTED | ABSENT:LAWFUL | ABSENT:SUSPICIOUS | CONTRADICTED`.
  - **Singapore EPC Rule**: A solvent Exempt Private Company (<=20 individual shareholders) is statutorily exempt from filing financial statements with ACRA. Log missing balance sheets as `ABSENT:LAWFUL`, never as concealment or automatic insolvency.
  - **Pricing Note**: Verify extract fees at purchase (`[VERIFY-AT-PURCHASE]`, e.g., Business Profile, People Profile, Financial Highlights).
- **Paid-Up Capital vs. Senior Floating Charges**:
  - Compare declared paid-up capital against active registered charges (`satisfied` vs `outstanding` `ALL MONIES` mortgages, debentures, factoring facilities).
  - An entity with low paid-up capital and multiple unsatisfied senior bank debentures leaves unsecured creditors behind the bank in liquidation.
- **The Director Graveyard Check**:
  - Audit the director/shareholder via a People Profile search.
  - Distinguish legitimate business strike-offs from serial phoenixing: opening a Pte Ltd, running it for 3-4 years, accumulating supplier debts, dissolving the shell, and immediately incorporating a new entity with identical branding.
- **Corporate Secretary & Registered Office**:
  - Record whether the registered address is an owned commercial facility, a multi-year lease, a residential base, or a virtual maildrop.

### Layer 2: Unfiltered Community & Complaint Enumeration
Marketing agencies and predatory vendors routinely manufacture digital trust (Google 5-star review farming, influencer gift packages, sponsored articles).
- **Complaint Enumeration (Replaces Arbitrary Review Haircuts)**:
  - Do not apply arbitrary percentage discounts to star ratings. Instead, record two countable metrics per source: `n_complaints` and `worst_allegation` in `{none, delay, variation_billing, defect, abandonment, abscondment}`.
- **Unfiltered Forum Archaeology**:
  - Query local ground-truth hubs: HardwareZone EDMW, Reddit (r/singapore, r/singaporefi), RenoTalk, Lowyat.
  - Search exact keywords: `"<entity_name>" scam`, `"<director_name>" delay`, `"<entity_name>" court`, `"<entity_name>" tribunal`.
- **High-Velocity Video Receipts (Xiaohongshu / TikTok)**:
  - Subcontractors, frustrated clients, and gig workers frequently upload timestamped video documentation of vendor defaults, abandoned sites, and unpaid invoices that never appear on Google index pages.

### Layer 3: Principal Lifestyle & Entity Clustering
- **Lifestyle vs. Balance Sheet Incongruence (The Ponzi Signature)**:
  - Serial bust-out operators project extreme visible wealth: rented supercars, luxury watches, and VIP hospitality tables while operating corporate entities run on negative net working capital.
  - When outward consumer ostentation is decoupled from audited balance-sheet earnings, personal lifestyle is funded via client upfront deposits (cash-flow ponzi).
- **Network & Co-Director Mapping**:
  - Map spouses, siblings, and recurring co-directors across related operating entities to identify shadow ownership structures.

### Layer 4: Regulatory Disciplinary & Litigation Sweeps
- **eLitigation / State Courts Cause Book**:
  - Check for active writ of summons, bankruptcy petitions, or enforcement orders against the entity or key directors.
- **Statutory Authority Debarments**:
  - Ministry of Manpower (MOM): Stop-Work Orders (SWO), workplace safety breaches, debarment from hiring work permit holders.
  - HDB Directory of Renovation Contractors (DRC): Active licensing status and accumulated demerit points.
  - Consumers Association of Singapore (CASE): Consumer alerts, warning notices, or voluntary compliance agreements (VCA).

### Layer 5: Operational & Real Estate Title Forensics (SLA INLIS)
- **Showroom / Facility Ownership Reality**:
  - Commercial entities often advertise expansive multi-story showrooms or regional headquarters.
  - A low-cost title search (e.g. S$5.25 SLA INLIS in Singapore) reveals:
    1. Strata title ownership: Is the facility owned by the company, held personally by a director, or rented on a short-term sub-lease?
    2. Encumbrance status: Which commercial bank holds the title mortgage?
    3. Operational permanence: Owned equity creates structural friction against fleeing; a short-term month-to-month lease allows 48-hour abandonment.

---

## 3. Technical Footprint & Digital Reconnaissance

For digital entities, SaaS vendors, inbound leads, or suspicious cyber interactions:

| Vector | Diagnostic Technique | High-Signal Indicators |
|:---|:---|:---|
| **Domain / WHOIS** | Domain age, registrar, privacy shields, historical DNS | Domains registered <90 days ago claiming "decade of excellence"; shared hosting with blacklisted subnets. |
| **Email Infrastructure** | SPF, DKIM, DMARC records, MX lookup via dig/nslookup | Free webmail masquerading as corporate domains; missing DMARC allowing impersonation; disposable relay nodes. |
| **Deep-Link Deobfuscation** | HTTP redirection trace, `curl -IL`, URL unshorteners | Deep-link cloaking, obfuscated affiliate parameters, phishing reverse-proxies. |
| **Search Operators (Dorking)**| Exact phrases, cached pages, filetype leaks | `site:<domain> filetype:pdf confidential` |
| | | `intext:"<phone_number>" OR intext:"<email>"` |
| | | `site:linkedin.com/in/ "<entity_name>"` |

---

## 4. Protective OPSEC & Counter-OSINT (Defending the Unit)

Intelligence is bidirectional. Operating effectively requires understanding how external actors, platforms, and state authorities collect OSINT on you.

### 4.1 — Optics as Interface
- **Asymmetric Negative EV of Wealth Displays**:
  - Flashing wealth in high-surveillance tax jurisdictions creates zero upside and massive attack surfaces.
  - Public luxury displays arm adversaries with statutory whistleblower bounties and trigger automated audits.
  - **Sovereign Rule**: True sovereignty requires decoupling capital accumulation from audience validation. Maintain high internal net worth with zero outward lifestyle distortion.

### 4.2 — Operational Identifier Decoupling
- **Zero Cross-Contamination**:
  - Never link gaming handles, forum personas, and personal social accounts to real legal names, banking accounts, or formal client contracts.
  - Use dedicated, decoupled communication conduits: separate numbers/SIMs for banking 2FA, freelance client intake, and social transactions.
- **Metadata Scrubbing**:
  - Strip EXIF GPS tags from all images before publishing or sending to counterparties.
  - Clean PDF author properties, comment revision tracks, and username traces from deliverable files (`exiftool`, docx property scrubbers).

---

## 5. Counterparty Risk Architecture (Knockout Gates + 100-Point Audit)

### 5.1 — Non-Compensatory Binary Knockout Gate (Booleans Gate; Scores Only Order)
Before computing a linear point score, evaluate the following binary veto conditions. **If ANY condition is TRUE, the score is immediately overridden to `RED VETO` under Law #1.** High charisma, elite credentials, or positive reviews cannot compensate for a binary knockout:
1. Active bankruptcy, winding-up petition, or undischarged insolvency of key principals.
2. Active unsatisfied civil default judgment or criminal fraud charge.
3. Operating an unlicensed regulated financial, medical, or legal business.
4. Demanding personal bank account transfers or unregulated crypto transfers for a corporate contract.
5. Corroborated physical/video evidence (`VERIFIED`) of project abandonment or deposit theft within the last 36 months.

### 5.2 — 100-Point Linear Audit (Applied Only If All Knockout Gates Clear)
When all binary knockout gates pass (`[CLEAR]`), compute the aggregate score across five dimensions (20 points each):

| Dimension | 20 Points (Clean) | 10 Points (Caution) | 0 Points (Critical Red Flag) |
|:---|:---|:---|:---|
| **1. Statutory Standing** | Established >5y, healthy paid-up capital, 0 debentures (or verified `ABSENT:LAWFUL` EPC) | 1-3y incorporation, minor bank charge, early-stage startup | Shell entity <1y, serial director dissolutions, heavy floating debentures |
| **2. Review Integrity** | Unvarnished positive reviews across multiple raw boards (`n_complaints = 0`) | Bimodal reviews (`n_complaints >= 1`, `worst_allegation: delay / workmanship`) | Severe sentiment haircut, farmed 5-star spam, `worst_allegation: abandonment / non_refund / fraud` |
| **3. Financial Posture** | Modest lifestyle, operational reinvestment, institutional backing | Unclear personal financials, opaque holding structure | Leased luxury assets, negative working capital, deposit-dependency |
| **4. Legal History** | Zero civil/criminal suits, clean regulatory records | Isolated settled commercial dispute, minor demerit | Active civil lawsuits, CASE alerts, MOM stop-work orders, bankruptcy |
| **5. Physical Permanence** | Owned property/facility, long-term verified lease, established HQ | Multi-year commercial tenancy or verified accelerator cohort | Virtual office maildrop, unverifiable operational address |

### 5.3 — Directional Payment Matrix & Triage Verdict
Payment architecture MUST match the cashflow direction identified in Track Selection (never apply vendor back-loading to an accounts-receivable client):

| Score Band | Verdict | Track A-R: Accounts Receivable (Client Paying Us) | Track A-P: Accounts Payable (Us Paying Vendor) | Track A-N: Co-Venture / Network |
|:---|:---|:---|:---|:---|
| **85–100** | **GREEN (Unconditional)** | Standard terms (50% upfront, 50% on delivery) | Standard commercial milestones | Open collaboration; standard mutual NDA |
| **65–84** | **AMBER (Conditional Shield)** | **Front-Load Cash**: 70–100% upfront or prepaid rolling retainer; staged IP handover; kill-switch on unpaid milestones | **Back-Load Cash**: Renovation Parity Shield (`10/15/25/25/15/10`); 60-day defects retention; zero uncollateralized deposits | Non-exclusive scope; strict IP ring-fencing; short-horizon trial project |
| **<65 or Knockout** | **RED (Hard Veto)** | **Walk away** (or 100% cash-in-advance before any labor starts) | **Walk away immediately**. Downside risk violates Law #1. | **Disengage politely**. Zero cap-table or reputational entanglement. |

### 5.4 — Universal Counterparty Dossier Standard (UCDS)
All Track A commercial and network evaluations must be rendered using the 6-Section **Universal Counterparty Dossier Standard (UCDS)** defined in [osint.md](../../workflows/osint.md) and [SKILL.md](../../skills/research/operational-osint/SKILL.md):
1. **Executive Snapshot & Horizon Forecast** (including `Builds to Exit` vs. `Empire Builder` trajectory and functional operator archetype).
2. **Evidence & Statutory Matrix** (using the 5-State Provenance Ladder: `VERIFIED`, `ATTESTED`, `ABSENT:LAWFUL`, `ABSENT:SUSPICIOUS`, `CONTRADICTED`).
3. **Behavioral Mechanics (Track-Appropriate)**.
4. **SWOT Matrix (Strategic Positioning)**.
5. **Operator Utility & Value-to-Us ("So What?")**.
6. **Two-Sided Error Accounting & Contract Shield** (pricing both Type 1 Paranoia Tax and Type 2 Ruin Exposure).

Verify UCDS dossier invariants deterministically with `python3 examples/scripts/ucds_audit.py --dossier <dossier.md>`.

---

## References

- [Protocol 001: Law of Ruin (No Irreversible Ruin)](../safety/SAF-001-law-of-ruin.md)
- [Consigliere Protocol (Pryce Test)](../decision/DEC-197-consiglieri-protocol.md)
