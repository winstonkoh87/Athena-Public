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
- **Paid-Up Capital vs. Senior Floating Charges**:
  - Compare declared paid-up capital against active registered charges (`ALL MONIES` mortgages, debentures, factoring facilities).
  - An entity with S$100,000 paid-up capital but multiple senior bank debentures is operating entirely on borrowed bank leverage. The bank takes 100% of liquidated assets in bankruptcy before unsecured creditors see S$0.01.
- **The Director Graveyard Check**:
  - Audit the director/shareholder via a People Profile search.
  - Detect patterns of serial phoenixing: opening a Pte Ltd, running it for 3-4 years, accumulating supplier debts, dissolving or striking off the shell, and immediately incorporating a new entity with identical branding.
- **Corporate Secretary & Registered Office**:
  - Is the registered address a commercial shophouse/office, or a mass-incorporation virtual maildrop shared with 5,000 shell companies?

### Layer 2: Unfiltered Community & Review Laundering Forensics
Marketing agencies and predatory vendors routinely manufacture digital trust (Google 5-star review farming, influencer gift packages, sponsored articles).
- **The Sentiment Haircut**:
  - Compare curated surfaces (Google Maps: 4.8 stars) against independent aggregators (Hometrust, Glassdoor, local complaint boards: 5.0 to 6.5 / 10). A 30% to 40% haircut indicates baseline operational friction.
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

## 5. Counterparty Risk Scorecard (100-Point Audit)

When completing an OSINT evaluation on a counterparty, compute the aggregate score across five dimensions (20 points each):

| Dimension | 20 Points (Clean) | 10 Points (Caution) | 0 Points (Critical Red Flag) |
|:---|:---|:---|:---|
| **1. Statutory Standing** | Established >5y, healthy paid-up capital, 0 debentures | 1-3y incorporation, minor bank charge | Shell entity <1y, serial director dissolutions, heavy debentures |
| **2. Review Integrity** | Unvarnished positive reviews across multiple raw boards | Bimodal reviews (some complaints, mostly resolved) | Severe sentiment haircut, farmed 5-star spam, video receipts of default |
| **3. Financial Posture** | Modest lifestyle, operational reinvestment | Unclear personal financials, opaque holding structure | Leased luxury assets, negative working capital, deposit-dependency |
| **4. Legal History** | Zero civil/criminal suits, clean regulatory records | Isolated settled dispute, minor demerit | Active civil lawsuits, CASE alerts, MOM stop-work orders, bankruptcy |
| **5. Physical Permanence** | Owned property/facility, long-term verified lease | Multi-year commercial tenancy | Virtual office maildrop, unverifiable operational address |

### Triage Verdict:
- **Score 85–100 (Green / Unconditional)**: Standard commercial terms.
- **Score 65–84 (Amber / Conditional Pass)**: Enforce **Contract Risk Inversion** (e.g., Back-heavy schedule: 10/15/25/25/15/10; milestone escrows; zero uncollateralized advances).
- **Score <65 (Red / Hard Veto)**: Walk away. Downside risk exceeds all possible commercial upside under Law #1.

---

## References

- [Protocol 001: Law of Ruin (No Irreversible Ruin)](../safety/SAF-001-law-of-ruin.md)
- [Consigliere Protocol (Pryce Test)](../decision/DEC-197-consiglieri-protocol.md)
