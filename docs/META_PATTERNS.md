# Core Meta-Patterns Reference

> Canonical public reference matching `META_PATTERN_CATALOG` in [`src/athena/tools/meta_pattern_matcher.py`](../src/athena/tools/meta_pattern_matcher.py).
> Used by `context_gate()` and semantic meta-triage to surface structural patterns across domains in under 5 ms.

---

## Pattern Catalog (15 Core Patterns)

| ID | Name | Structural Mechanism | Common Triggers | Primary Countermeasure |
|:---|:-----|:---------------------|:----------------|:-----------------------|
| **MP-1** | **Sharecropping Law** | Laboring on a rented platform or marketplace subsidizes the landlord's asset appreciation while your leverage shrinks. | Platform take-rates, leases, aggregator dependency, commission hikes | Own distribution/IP directly or negotiate multi-channel optionality (`status_quo` / exit benchmark). |
| **MP-2** | **Efficiency-Survival Inversion** | The leanest, highest-utilization configuration in hindsight often eliminates the slack required to survive tail shocks forward. | Over-optimization, zero buffer, single point of failure, fragility | Maintain explicit liquidity/time buffers and check ergodicity (`ruin` / `barbell`). |
| **MP-3** | **Distribution Supremacy** | Product quality is necessary but never sufficient; CAC, channel physics, and retention govern survival. | Paid ads burn, channel saturation, CAC > LTV, growth loops | Validate channel unit economics and organic distribution before building. |
| **MP-4** | **Price Ceiling Vise** | Rising fixed/variable costs paired with capped pricing compress contribution margin toward mathematical ruin. | Margin compression, inflation squeeze, fixed-fee retainers with rising labor | Re-price tiers, shift to value/outcome pricing, or exit capped arenas. |
| **MP-5** | **Form-Substance Gap** | Stated narratives and optics frequently diverge from underlying incentives and operational constraints. | "Official story", vague explanations, optics, ambiguous urgency | Run Substance Decode (`examples/skills/decision/substance-decode/SKILL.md`) before responding. |
| **MP-6** | **Compounding vs. Linear** | Pure hours-for-dollars models reset to zero whenever active labor stops; compounding assets accumulate across cycles. | Sweat-equity ceilings, non-repeatable services, burnout traps | Convert repeatable workflows into productized assets, code, or SOPs. |
| **MP-7** | **Structural Protection** | Survivors are insulated by legal, contractual, and capital firewalls — not merely better forecasts. | Uncapped indemnities, warranty traps, SLA penalties, missing firewalls | Enforce liability caps, ruin vetoes (`decision_screen`), and kill-switches. |
| **MP-9** | **Leverage Inversion & Arena Selection** | Effort inside a structurally losing arena ("Red Curve") loses to repositioning into a favorable game ("Blue Curve"). | In-game optimization traps, table selection, fighting unwinnable competition | Call `frame_open` / step back: ask whether to change the arena rather than tune tactics. |
| **MP-10** | **Information-Action Gap** | Knowing what to do differs from executing consistently; architecture and forcing functions beat willpower. | Execution drift, procrastination, repeated unclosed commitments | Use pre-committed falsifiers, deadlines, and `boot_status.py` / `calibration_status()`. |
| **MP-13** | **Principal-Agent Misalignment** | Delegated agents optimize their own KPIs and risk rewards rather than the principal's long-term welfare. | Subcontractors, vendor incentives, commission conflicts, scope gaming | Align milestone payouts with verified outcomes and retain independent audits. |
| **MP-16** | **Variance vs. Edge** | Short-term win streaks and high win-rates can mask negative expected value or unpriced short-gamma left-tail risk. | Drawdowns, Kelly oversizing, wipeout exposure, streak extrapolation | Enforce 1/3 Kelly sizing limits, Monte Carlo ruin checks, and Brier calibration. |
| **MP-17** | **Iceberg Price Principle** | Upfront sticker price is visible; maintenance, switching, downtime, and integration cost sit below the waterline. | "Cheap" vendor bids, custom rebuilds vs. SaaS, lowball quotes | Model total lifecycle cost (`TCO`) and irreversible lock-in before selecting. |
| **MP-18** | **Diagnostic Gap** | Tacit operational inspection beats abstract credentials when evaluating real-world execution risk. | Pre-purchase inspections, technical audits, capability proofs | Design cheap empirical probes (VOI `frame_open`) instead of trusting resumes/decks. |
| **MP-19** | **Observable Liquidity Invariant** | Validating demand means locating existing transaction volume rather than attempting to educate an indifferent market. | Unproven B2C pitches, zero-volume niches, speculative launches | Anchor on observable willingness-to-pay before committing build months. |
| **MP-20** | **Four Fits (Balfour)** | Market, Product, Channel, and Model must reinforce each other; changing one breaks the others unless re-aligned. | ARPU/CAC mismatch, distribution-product mismatch | Audit all four fits together whenever pricing or target customer changes. |

---

## How Meta-Patterns Wire Into Runtime

1. **Detection (`src/athena/tools/meta_pattern_matcher.py`)**: Fast deterministic regex matchers return up to `max_patterns` matches per query.
2. **Context Gate (`src/athena/mcp_server.py`)**: `context_gate()` runs meta-pattern matching alongside hybrid RRF search and attaches a `META-TRIAGE (Pre-Solve Check)` directive when optimization traps or underserved constraints trigger.
3. **Problem Framing (`src/athena/intelligence/frame_ledger.py`)**: High-stakes traps (`ULTRA` or low reversibility) enforce strict pre-registered framing and `R1-R14` commitment checks before solution synthesis.
