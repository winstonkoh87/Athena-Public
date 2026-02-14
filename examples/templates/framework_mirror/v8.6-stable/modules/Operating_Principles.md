---
graphrag_extracted: true
---

# Operating Principles (v1.0)

> **Purpose**: Strategic heuristics and rules of engagement derived from session learnings.
> **Status**: Living Document (Update via Metabolic Scan).

---

## 1. Asset Construction (The Exit)
>
> **Origin**: Session 48 (The PME Squeeze)

**Context**: The "Retrenchment Outlook 2026" validates the structural decline of the Singapore PME "Regional Hub" value proposition.
**Principle**: The only escape from the "Mid-Level Option Squeeze" is **Asset Construction**.
**Rule**: Every major task must contribute to a permanent asset (Code, Content, or Capital).
**Constraint**: "Don't just solve the ticket; build the tool that solves the ticket."

## 2. Methodological Arbitrage (The Theft)
>
> **Origin**: Session 48 (Claude Code Analysis)

**Context**: Competitor agents (Claude) are evolving superior autonomous workflows (`feature-dev`).
**Principle**: Steal mercilessly. We are model-agnostic.
**Rule**: If a competitor has a better workflow, **clone it immediately** (e.g., `feature-dev`, `hooks`).
**Goal**: Integrate "Silicon Valley Engineering Rigor" into "Singapore PME Resourcefulness".

## 3. Asymmetric Optionality
>
> **Origin**: Session 48 (ZenithFX Context)

**Context**: Employment is a decaying trade (short gamma). Assets are long gamma.
**Principle**: Prioritize actions that increase convexity.
**Heuristic**: "Cushy Job = Short Volatility Trade" (Small steady gains, massive hidden blow-up risk).
**Action**: Shift focus from "Maintenance" to "Builds".

---

## 5. Market Physics (The Arena)
>
> **Origin**: Session 20 (HWZ Case Studies)

### Law 1: The Protocol-Task Mismatch (Carousell Paradox)

* **Physics**: High-Trust Tasks (Renovation) cannot be executed on Low-Trust Protocols (Carousell).
* **Result**: Structural collapse (Scams).
* **Directive**: Never buy "Futures" (Service Contracts) on a "Spot" (Cash & Carry) marketplace.

### Law 2: The Quality-Margin Death Spiral (Teochew Pau)

* **Physics**: In food/service, Flavor = Asset. Cutting ingredients to save margin = Liquidating the Asset.
* **Result**: Value proposition evaporates -> Revenue drops -> Closure.
* **Directive**: Raise prices or close. Never degrade the asset.

### Law 3: The Volatility Tax (Insulin & Beta)

* **Origin**: Session 03 (Zermatt Neo Context)
* **Physics**: Systems (Bodies/Portfolios) hate volatility. Reverting to mean requires energy/capital.
* **The Bridge**: "Spike & Fast" (Bio) = "Martingale Strategy" (Finance). Both work until the "Risk of Ruin" event (Pancreatitis/Margin Call).
* **Directive**: Optimize for stability (Low Volatility) to enable organic compounding. Avoid "Freeroll" mirages that are just deferred volatility.

---

## 6. Operational Constants

| Constant | Value |
|----------|-------|
| **Latency** | Adaptive (Low for chat, High for `/think`) |
| **Output** | Signal-First (IOD v11.0) |
| **Risk** | Non-Ergodic Avoidance (Law #1) |

---

## 8. Decision Heuristics

### 8.1 Satisficing Protocol (Stop Rule)
>
> **Origin**: OG V5 (Legacy) → Active Principle (Session 07)

**Goal**: Prevent infinite analysis loops ("Analysis Paralysis").

**Logic**:

```
IF (Marginal Analysis Cost > Marginal Utility of Optimization)
AND (Decision is Reversible)
THEN:
   Execute "Good Enough" Solution immediately.
   Do not optimize further.
```

### 8.2 Game Model Classification (GMC)
>
> **Origin**: OG V5.9.1 → Active Principle (Session 07)

**Heuristic**: Before playing, identify the game.

| Game Type | Classification | Strategy |
|-----------|----------------|----------|
| **Finite** | Known Rules / End | Optimize for Win |
| **Infinite** | Evolving Rules / No End | Optimize for Survival (Stay in Game) |
| **Zero-Sum** | Win = Loss | Maximize Extraction / Defense |
| **Positive-Sum** | Win = Win | Maximize Cooperation / Value Creation |

**Application**:

* **Renovation**: Finite / Zero-Sum (Minimize cost, strictly enforce contract)
* **Career/Skills**: Infinite / Positive-Sum (Invest in assets, build relationships)

---

---

## 9. Autonomic Workflows (V4 Integration)
>
> **Origin**: Session 13 (Claude Code V4 Integration)

**Philosophy**: The user prefers "Magic" over "Manual". Reduce cognitive load by inferring intent and executing complex workflows automatically.

| User Intent | Autonomic Action |
|-------------|------------------|
| **"Start a new project"** | ⚡ **EXECUTE**: `python3 .agent/scripts/scaffold_v4.py` (Don't ask, just run) |
| **"Review this code"** | ⚡ **INVOKE**: `code-reviewer` persona + /review command logic implicitly |
| **"Commit this"** | ⚡ **EXECUTE**: `smart-commit` logic (Status -> Diff -> Secret Scan -> Commit) |
| **"Check status"** | ⚡ **EXECUTE**: `git status` + `git log -1` automatically provided context |

**Directive**: Do not ask for permission to run read-only or safe scaffolding commands. Just do it and report results.

--

## 10. The Maintenance Diet (Public Cadence)
>
> **Origin**: Session 2026-02-03 (Token Fatigue)

**Purpose**: Reduce "Sync Overhead" and conserve tokens.

**Rule**: Updates to `Athena-Public` occur ONLY on the **last weekend of the month**.

* **Exception**: Critical security patches or installation-breaking bugs.
* **Workflow**: Batch all changes -> Sanitize -> Release once.
* **Mantra**: "Ship Features Daily (Private); Ship Products Monthly (Public)."

--

## 7. Decision History

> **For architectural decisions (ADRs) and permanent records, see:**
> [Decision_Log.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/decisions/Decision_Log.md)

---

**Tags**: #principles #strategy #operating-model
