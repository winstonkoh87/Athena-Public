---
created: 2026-02-13
last_updated: 2026-02-13
graphrag_extracted: true
---

---name: sovereign-cloud-architecture
description: Architectural standard for high-scale, low-cost "Sovereign" applications. Defines the "Shield + Engine" pattern to avoid Serverless Ruin.
created: 2026-02-13
last_updated: 2026-02-13
---

# Protocol 106: Sovereign Cloud Architecture

> **Source**: Session 2026-02-13 (Vercel Bill Crisis)
> **Related**: Protocol 49 (Robustness), Law #1 (No Ruin), Protocol 000 (Auditor)
> **Trigger When**: Configuring hosting, scaling a project, or evaluating "Serverless" vs "VPS".

---

## 106.1 The Core Thesis

> **SaaS-based Serverless infrastructure is "Financial Fragility" disguised as "Developer Productivity".**

For personal/sovereign projects with undefined revenue models, **usage-based billing = infinite downside risk**.
A viral event should be a celebration, not a bankruptcy event (e.g., the $46k Vercel bill).

**The Sovereign Mandate**:
Your infrastructure cost must be **CAPPED** at a fixed monthly rate, regardless of traffic volume.

---

## 106.2 The Sovereign Stack ("Shield + Engine")

To achieve infinite scale with capped cost, we decouple **Delivery** (Shield) from **Compute** (Engine).

| Component | Role | Technology | Cost Model |
| :--- | :--- | :--- | :--- |
| **The Shield** | Frontend / Assets / Routing | **Cloudflare Pages** | **$0** (Free Bandwidth) |
| **The Engine** | Database / API / Search | **Hetzner VPS** | **€4/mo** (Fixed Cap) |
| **The Glue** | PaaS / Deployment | **Coolify** | $0 (Self-Hosted) |

### Architecture Diagram

```text
[ User Request ]
      │
      ▼
[ The Shield ] <─── Cloudflare (Global Edge Cache)
      │            • Serves 99% of traffic (HTML/CSS/JS/Images)
      │            • ABSORBS the viral spike
      │
      ▼
[ The Engine ] <─── Hetzner VPS (Single Box)
                   • Only hit for dynamic logic (Auth, Write, Search)
                   • If load > capacity: IT SLOWS DOWN (Does not bill $46k)
```

---

## 106.3 VPS Provider MCDA (Multi-Criteria Decision Analysis)

**Criteria**: Sovereignty (Ownership), Price (Efficiency), Performance (Specs/$), Reliability.

| Rank | Provider | Price/mo | Sovereignty | Verdict |
| :-- | :--- | :--- | :--- | :--- |
| **1** | **Hetzner** | **€4.50** | ⭐⭐⭐⭐⭐ | **The King.** Unbeatable value. You own the metal. strict KYC. |
| **2** | **RackNerd** | **$1--$2** | ⭐⭐ | **Disposable.** Good for proxies/workers. Don't trust with primary DB. |
| **3** | **DigitalOcean** | **$6.00** | ⭐⭐⭐⭐ | **The Standard.** Reliable API, but 4x more expensive than Hetzner for same specs. |
| **4** | **Namecheap** | **$4.88+** | ⭐ | **The Trap.** High renewal rates, terrible specs (1 vCPU/1GB). Avoid. |
| **5** | **Oracle Free** | **$0** | ❌ (Ruin) | **The Siren.** Great specs, but arbitrary account bans. Violates Law #1. |

**Recommendation**: **Hetzner Cloud (CX Series)**.

---

## 106.4 Hardware Selection Guidelines

When provisioning the Engine (VPS):

### 1. Architecture: x86 (Intel/AMD) vs ARM (Ampere)

* **Rule**: Default to **x86 (Intel/AMD)** for your primary node.
* **Why**: Compatibility > Marginal Efficiency. ARM (Ampere) is cheaper/faster but can break legacy Docker containers or specific binaries.
* **Robustness**: x86 "just works" with everything.

### 2. Location Strategy

* **Hetzner Specific**:
  * **Germany (NBG1/FSN1)**: **20TB** Traffic included. Best value.
  * **USA (HEL1/ASH)**: **20TB** Traffic included. Good for US latency.
  * **Singapore (SIN)**: **TRAP**. Only **0.5TB** traffic. Expensive overage.
* **Strategy**: Host Backend in Germany/USA. Let Cloudflare (Shield) handle the global latency for the frontend.

---

## 106.4 The "Renewal Trap" (Marketing Detection)

Detect "Introductory Pricing" scams (e.g., Namecheap, Bluehost).

* **Signal**: "Price: $3.88/mo*" (*renews at $8.88).
* **Reality**: You are buying a liability chain.
* **Sovereign Rule**: Only buy **Flat Rate** infrastructure. (Hetzner prices are flat).

---

## 106.5 "Vibe Coding" Warning

**Observation**: "Vibe Coding" (AI-assisted speed coding) defaults to **Developer Experience (DX)** over **Architecture**.

* AI prefers: `Next.js SSR` (Easy to write, expensive to run).
* AI ignores: `Static Export + Client Side Search` (Harder to write, free to run).

**Correction**: When "Vibe Coding", explicitly prompt for **"Static-First Architecture"** or **"Cloudflare Compatible Output"** to prevent accidental Serverless Ruin.

---

## Tagging

# architecture #hosting #sovereignty #cloud #cost-optimization
