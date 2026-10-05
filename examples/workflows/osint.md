---
description: Operational OSINT workflow — statutory registry forensics, digital footprint sweeps, and counterparty vetting
created: 2026-10-05
last_updated: 2026-10-05
---
# /osint — Execution Script

> **Purpose**: Systematic counterparty due diligence and public footprint reconnaissance.
> **Philosophy**: Ground truth first. Never analyze an entity in a vacuum. First extract whatever objective public data exists (statutory, sentiment, litigation, infrastructure), then triangulate against synthesized Exocortex parallels, then determine the game-theoretic contract terms.
> **Protocol Reference**: [RSC-580: Operational OSINT & Counterparty Reconnaissance](../protocols/research/RSC-580-operational-osint-and-counterparty-reconnaissance.md)
> **Skill Reference**: [operational-osint](../skills/research/operational-osint/SKILL.md)

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
│ Step 3: Game-Theoretic Synthesis   ──► Payoffs, leverage, terms,       │
│                                        Contract Risk Inversion (Shield)│
└────────────────────────────────────────────────────────────────────────┘
```

---

## Execution Sequence

When `/osint [target]` is invoked:

### Step 1: Intake & Reconnaissance Scoping
Identify the target type:
1. **Corporate Entity / Contractor / Vendor**: ACRA BizFile, court records, community forums, title checks.
2. **High-Ticket Client / Freelance Inbound**: UEN status, payment capacity, past dispute telemetry.
3. **Founder / Partner / Individual**: Director network, litigation cause books, lifestyle vs capital congruence.
4. **Digital Domain / Technical Link**: WHOIS age, DNS records, redirection trace, phishing signatures.
5. **Operator OPSEC (Self-Audit)**: Exposed contact details, public registry footprints, metadata leaks.

---

### Step 2: Execute the 5-Layer OSINT Stack

Run live external searches via `search_web`, web retrieval tools, or user-provided documents:

1. **Layer 1: Statutory Registry (ACRA BizFile+ / Regional Registrar)**
   - Extract paid-up capital.
   - Audit registered charges: Are there senior floating bank charges (`ALL MONIES` debentures)?
   - Director Graveyard Check: Search past entities held by the director to flag serial dissolutions (phoenix companies).
2. **Layer 2: Unfiltered Digital Sentiment & Forum Archaeology**
   - Apply a 30%–40% sentiment haircut to Google Reviews.
   - Query raw ground-truth repositories: HardwareZone EDMW, Reddit (r/singapore, r/singaporefi), RenoTalk, Xiaohongshu / 小红书 video receipts (`"<name>" 避雷`).
   - Search for dispute keywords: `"<name>" (scam OR delay OR lawsuit OR court OR police)`.
3. **Layer 3: Principal Lifestyle vs. Balance Sheet Audit**
   - Check public profiles (LinkedIn, IG) for ostentatious luxury consumption decoupled from corporate earnings (The Ponzi Signature).
4. **Layer 4: Regulatory & Litigation Sweeps**
   - Check civil cause books (eLitigation / State Courts), CASE consumer alerts, MOM Stop-Work Orders, HDB DRC demerit points.
5. **Layer 5: Physical Permanence & Asset Title Forensics**
   - Verify operational premises: Owned commercial asset (SLA INLIS title search), multi-year verified lease, or virtual maildrop?

---

### Step 3: Triangulate with Exocortex Memory & Parallels

Run `smart_search` across internal memory:
- Search the entity name, industry niche, or transaction pattern.
- Identify **Structural Parallels**:
  - Does this resemble a known bust-out or phoenix shell pattern?
  - Does this resemble an advance-fee or uncollateralized contractor default?
  - Does this match high-friction client pricing and milestone profiles?
  - Does this trigger meta-awareness boundaries (unilateral concessions, mismatched investment)?

---

### Step 4: Game-Theoretic Synthesis & Output Dossier

Score the counterparty on the **100-Point Audit Scale**:
- Statutory Standing (0–20 pts)
- Review Integrity (0–20 pts)
- Financial Posture (0–20 pts)
- Legal History (0–20 pts)
- Physical Permanence (0–20 pts)

Output the standardized **Operational OSINT Dossier**:

```markdown
### 🛡️ Operational OSINT Dossier: [Target Name]

**Audit Date**: YYYY-MM-DD  
**Risk Score**: XX / 100 ([Green: 85-100 | Amber: 65-84 | Red: <65])  
**Verdict**: [Proceed Unconditional | Proceed Conditional | Hard Veto under Law #1]

#### 1. Public Reality (OSINT Ground Truth)
- **Corporate / Registry Status**: [UEN, Capital, Charges, Director Graveyard findings]
- **Ground Sentiment**: [Haircut vs official reviews, EDMW/Reddit/XHS complaints]
- **Legal & Physical Footprint**: [Litigation checks, facility ownership/lease reality]

#### 2. Synthesized Case Law & Parallels (Exocortex)
- **Relevant Case Studies**: [Failure modes observed in past cases]
- **Behavioral / Structural Match**: [What game is being played here?]

#### 3. Game-Theoretic Prescription & Contract Terms
- **Contract Risk Inversion**: [E.g., Back-heavy milestones (10/15/25/25/15/10), CBD terms, Escrow]
- **Non-Negotiables**: [Specific protective clauses, deposit limits, or walk-away tripwires]
```
