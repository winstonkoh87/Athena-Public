---

created: 2025-12-25
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-25
last_updated: 2025-12-31
---

# Protocol 181: SDR Diagnostic (Strategic-Tactical Ratio)

> **Status**: ACTIVE  
> **Source**: Zero-Point Codex (Dec 2025)  
> **Trigger**: Repeated failure despite effort, frustration with results, "working hard but not winning"

---

## Philosophy

> **"Most failures aren't tactical—they're playing the wrong game."**

SDR distinguishes between **A-Type failures** (bad luck in a winnable game) and **B-Type failures** (structural mismatch with the arena). The difference determines whether to persist or exit.

---

## Core Formula

```text
SDR = Strategic Gap ÷ Tactical Gap

Where:
- Strategic Gap = Mismatch between your capital and the arena's requirements
- Tactical Gap = Room for improvement in execution within current arena
```

---

## SDR Interpretation Matrix

| SDR Ratio | Failure Type | Diagnosis | Action |
|-----------|--------------|-----------|--------|
| **< 2:1** | A-Type (Variance) | Winnable game, bad luck | Persist ✅ |
| **2-5:1** | Reconnaissance Zone | Something's off | Investigate 🟡 |
| **> 5:1** | B-Type (Structural) | Wrong table entirely | Exit ❌ |

---

## Diagnostic Protocol (5 Questions)

### Step 1: Measure Strategic Gap

```text
Q1: Does this arena reward your specific capital type?
    - Your strengths: [list 3-5]
    - Arena rewards: [list 3-5]
    - Overlap: ___% 

Q2: What's the base success rate for people like you in this arena?
    - Industry/domain average: ___%
    - Your demographic's rate: ___%
    
Q3: Are structural barriers beyond your control?
    - Credentials required you lack? Y/N
    - Network access blocked? Y/N
    - Demographic mismatch? Y/N
```

### Step 2: Measure Tactical Gap

```text
Q4: How much room for execution improvement exists?
    - Current skill level: __/10
    - Ceiling skill level: __/10
    - Gap: __ points

Q5: If you executed perfectly, would outcome change significantly?
    - Perfect execution success rate: ___%
    - Current success rate: ___%
    - Tactical ceiling lift: ___%
```

### Step 3: Calculate SDR

```text
Strategic Gap Score: (3 - overlap%) + (3 - base_rate/30) + structural_barriers
Tactical Gap Score: skill_gap + (perfect_vs_current / 10)

SDR = Strategic Gap Score ÷ Tactical Gap Score
```

---

## Singapore Multipliers

When operating in Singapore, apply these multipliers:

| Factor | Multiplier | Reasoning |
|--------|------------|-----------|
| Credential gatekeeping | ×2.5 | Paper trumps ability |
| Small market | ×1.8 | Everyone knows everyone |
| Randy Dilemma (L4) | ×2.0 | System optimizes against you |

**Singapore SDR = Base SDR × (2.5 × 1.8 × 2.0) = Base × 9.0**

---

## Classic Cases

### Case 1: SIT Graduate (650 Applications)

```text
Arena: Singapore tech job market
Capital: SIT degree, skills, English
Strategic Gap: High (SIT < NUS/NTU signal, local market oversaturated)
Tactical Gap: Low (resume/interview already optimized)

SDR = 7:1 → B-Type Failure
Action: Exit arena (EU/remote markets) ✅
```

### Case 2: 38yo in Youth-Optimized Market

```text
Arena: Young gay dating scene (18-25 target)
Capital: Resources, experience, maturity
Strategic Gap: Extreme (age mismatch structural)
Tactical Gap: Minimal (presentation already optimized)

SDR = 8:1 → B-Type Failure
Action: Shift to age-appropriate arena ✅
```

### Case 3: Qualified Job Applicant

```text
Arena: Relevant industry, skills match
Capital: Credentials, experience, network
Strategic Gap: Low (capital-arena alignment good)
Tactical Gap: Medium (interview skills improvable)

SDR = 1.5:1 → A-Type Variance
Action: Continue, refine tactics ✅
```

---

## The Boxer Fallacy ⚠️

> **"When SDR > 5:1, 'working harder' is the most efficient path to destruction."**

The boxer who keeps getting hit thinks "I need to punch better."
Reality: He's in the wrong weight class.

**Detection**: Pattern of increasing effort + decreasing returns = Boxer Fallacy active.

---

## Decision Tree

```text
Calculate SDR
    │
    ├── SDR < 2:1
    │   └── A-Type: Persist. Refine tactics.
    │
    ├── SDR 2-5:1
    │   └── Reconnaissance: Run 4B probe before committing more.
    │
    └── SDR > 5:1
        └── B-Type: Exit immediately. Find new arena.
            └── Sunk cost is irrelevant. Future EV is all that matters.
```

---

## Integration

- Use with [Protocol 180: Utility Function Analysis](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/180-utility-function-analysis.md) for stakeholder mapping
- Use with [Protocol 40: Frame vs Structural Problem](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/40-frame-vs-structural-problem.md) for diagnosis
- Feeds into table exit decisions per Law #2

---

## Tags

# protocol #sdr #strategic-tactical-ratio #a-type #b-type #table-selection #law-2

## Related Protocols

- [Protocol 124: SDR Diagnosis](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/124-sdr-diagnosis.md)
