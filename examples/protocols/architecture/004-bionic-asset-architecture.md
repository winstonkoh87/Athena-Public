---

created: 2025-12-31
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-31
last_updated: 2025-12-31
---

# Protocol 004: Bionic Asset Architecture

> **Type**: Architectural Standard  
> **Purpose**: Preventing "Vibe Entropy" by enforcing Asset Classes and Promotion Rules.  
> **Origin**: Session 07 (Dec 2025) - "The Disposability of Intelligence" Analysis  
> **Status**: MANDATORY  
> **Tags**: #architecture #bionic-stack #capabilities #knowledge-management

---

## 1. The Bionic Asset Stack

To prevent "Vibe Coding" (High Velocity, Zero Asset), all intellectual output must be classified into one of three asset classes.

| Asset Class | Purpose | Location | Nature |
| :--- | :--- | :--- | :--- |
| **Protocol** | **Strategy (The "Why/Think")**<br>Mental models, heuristics, decision frameworks. | `.agent/protocols/` | **Abstract / Cognitive**<br>*Installs software in the Human mind.* |
| **Capability** | **Tool (The "How/Do")**<br>Executable scripts, reproducible automations. | `.agent/capabilities/` | **Concrete / Executable**<br>*Installs software in the Machine.* |
| **Evidence** | **Proof (The "Past")**<br>Case studies, logs, audits. | `.context/case_studies/` | **Historical / Static**<br>*Validates the Strategy.* |

> **The Rule**: "No Orphan Assets." Everything must fit this taxonomy. If it's code, it's a Capability. If it's a concept, it's a Protocol. If it happened, it's Evidence.

---

## 2. The Capability Standard (Definition of "Done")

A script in `.agent/scripts/` is a "Draft." A script in `.agent/capabilities/` is a **Product**.

To be a **Capability**, it must satisfy the **Reproducibility Contract**:

1. **Self-Contained**: Must run without "magic" local state.
2. **Documented**: Must include a standard Metadata Header.
3. **Dependency-Aware**: Must state its requirements (e.g., `pip install x`).

### Standard Capability Header (Template)

```python
"""
CAPABILITY: [Name]
ID: [CAP-XXX]
Purpose: [One sentence description]
Inputs: [File paths, Arguments]
Outputs: [Files created, Terminal output]
Dependencies: [e.g., python3, requests, beautifulsoup4]
Usage: python3 script_name.py [args]

Lifecycle: [Active / Deprecated / Beta]
"""
```

---

## 3. The Promotion Protocol (The "Rule of Three")

Do not hoard "junk scripts." Use the **Rule of Three** to determine when to **Codify**.

| Frequency | Action | State |
| :--- | :--- | :--- |
| **1st Use** | Manual / Ad-hoc Script | **Vibe Code** (Disposable) |
| **2nd Use** | Copy-Paste / Recall | **Pattern** (Emerging) |
| **3rd Use** | **PROMOTE TO CAPABILITY** | **Asset** (Permanent) |

**Promotion Checklist:**

1. [ ] Clean the code (remove hardcoded paths).
2. [ ] Add the Metadata Header.
3. [ ] Save to `.agent/capabilities/[CAP-Name].py` (or `.md`).
4. [ ] Register in `SKILL_INDEX` (Auto-generated).

---

## 4. Lifecycle Management

Capabilities must be maintained or killed.

| State | Definition | Action |
| :--- | :--- | :--- |
| **Active** | Verified working today. | Use freely. |
| **Beta** | Experimental / In-testing. | Use with caution. |
| **Deprecated** | Replaced or obsolete. | Keep for reference, but warn on use. |
| **Archived** | Broken / Incompatible. | Move to `archive/` folder. |

---

## 5. The "Knowledge Cycle" (Compounding Loop)

1. **Vibe (Explore)**: Fast, messy iteration to solve the problem once.
2. **Codify (Consolidate)**: Apply "The Rule of Three." If valuable, clean and file it.
3. **Install (Automate)**: Update the Workflow/Protocol to reference the new Capability.

> **Result**: Intelligence becomes **Capital**, not just **Labor**.

---

## Tagging

# protocol #architecture #capabilities #asset-management #anti-entropy
