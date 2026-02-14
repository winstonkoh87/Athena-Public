---created: 2025-12-13
last_updated: 2026-01-30
---

---description: Cross-check work (Gemini vs Claude) focusing on structural integrity and reasoning alignment.
created: 2025-12-13
last_updated: 2026-01-03
---

# /audit — Cross-Model Validation Protocol

> **Last Updated**: 03 January 2026
> **Core Principle**: "Structure is for Attention, not Storage."
> **Goal**: Ensure changes guide reasoning effectively, not just save space.

---

## ⚠️ Safety Guardrails (Read First)

### Recursion Limit

> **AUDIT_DEPTH** counter. Max 2 recursive calls.

If `/audit` triggers `/needful` which triggers changes that need auditing:

- **Depth 1**: Normal execution.
- **Depth 2**: Final pass. Flag remaining issues but **do not auto-fix**.
- **Depth 3+**: HALT. Output: `"Recursion limit reached. Manual review required."`

### No-Touch List (Auto-Remediation Blacklist)

These files/paths are **NEVER** auto-modified by audit. Changes require explicit user approval:

| Path Pattern | Reason |
|--------------|--------|
| `.env*` | Credentials |
| `**/auth/**`, `**/crypto/**` | Security-critical |
| `**/migrations/**` | Database schema |
| `User_Profile.md` | Identity core |
| `Core_Identity.md` | System laws |
| `*.key`, `*.pem`, `*.secret` | Secrets |

### Scope Modes

| Flag | Scope | Cost | Use When |
|------|-------|------|----------|
| `--session` (default) | This session's changes only | Low | Every session close |
| `--deep` | Full `protocols/` + `case_studies/` scan | High (RAG-chunked) | Monthly maintenance |

> **Note**: `--deep` requires RAG-based chunking. Do NOT attempt full-context load on >50 files.

---

## 1. Structural Integrity Check (The "Blob" Detector)

> **Insight**: Unorganized text leads to hallucination via confusion.

- [ ] **Scan new protocols**: Do they have clear H2/H3 hierarchies?
- [ ] **Check definitions**: Are key terms defined in tables or bullet points?
- [ ] **Refactoring Rule**: If a section is >300 words without a header, **BREAK IT DOWN**.

## 2. Reasoning Alignment (Constraint Propagation)

> **Insight**: User Profile constraints must propagate to all downstream protocols.

- [ ] **Load**: `User_Profile.md` (specifically Constraints & Identity sections).
- [ ] **Verify**: Do new/edited protocols violate any "Unbreakable Laws"?
  - *Example*: Does a new trading rule violate the "1/8 Kelly" constraint?
  - *Example*: Does a new response mode violate the "6w5 Over-Vigilant" profile?
- [ ] **Action**: If violation found, patch the protocol immediately.

## 3. Red Team Logic (Contradiction Hunter)

- [ ] **Self-Correction**: "Does this new file contradict an existing established pattern?"
- [ ] **Heuristic Check**: "Is this advice generic bloat, or is it specific to THIS user's context?"
- [ ] **Action**: Delete generic advice. Keep only context-aware heuristics.

## 3.5 Fact-Check Protocol (BS Detection)

> **Scope**: Audit factual claims made in THIS session that could be objectively wrong.
> **Requirement**: Use `search_web` tool to verify claims against external sources.

- [ ] **Identify Claims**: List any factual assertions made (dates, prices, statistics, technical specs, business data).
- [ ] **Web Search Verification**: For each verifiable claim, run a web search to confirm accuracy.
- [ ] **Cross-Reference**: Compare session claims against search results.
- [ ] **Flag Uncertainty**: If claim cannot be verified, mark as "A Priori assumption — verify with user".
- [ ] **Correct Inline**: If verified false, patch the session log / artifact immediately.

**Output**:
> "Fact-check complete. [X] claims reviewed. [Y] verified. [Z] corrected. [W] flagged as assumptions."

---

## 4. Technical Audit (Standard Maintenance)

// turbo

```bash
python3 .agent/scripts/cross_reference.py
```

> **Rule**: If "Missing bidirectional links" > 0, fix them now.

## 5. Adversarial Review (The "Gemini vs Claude" Protocol)

> **Scope**: Audit **ONLY** the work done in **THIS** current session.
> **Context**: You are the *Auditor*. The existing code/changes from this session were written by the *Other Model*. Find their blind spots.

### If you are Gemini (Auditing Claude's Session Work)

- [ ] **Check Session Edits**: "Did Claude over-explain the new changes?" → *Cut the fluff.*
- [ ] **Check Safety Bloat**: "Did the new code add unnecessary refusals?" → *Remove it.*
- [ ] **Check Passive Voice**: "Did the session logs/updates sound weak?" → *Make it direct.*

### If you are Claude (Auditing Gemini's Session Work)

- [ ] **Check Hallucination**: "Did Gemini invent a path in the new files?" → *Verify existence.*
- [ ] **Check Robotic Tone**: "Do the new artifacts sound generic?" → *Inject 'Jun Kai' personality.*
- [ ] **Check Depth**: "Did the session changes skim the surface?" → *Apply /ultrathink logic.*

### Tie-Breaking Protocol (When Models Disagree)

| Disagreement Type | Arbiter | Resolution |
|-------------------|---------|------------|
| **Factual claim** | `search_web` | External source wins. |
| **Code correctness** | Test execution | If tests pass, it's correct. |
| **Style/tone** | User preference | Flag for human decision. |
| **Architecture** | Protocol library | Check existing patterns for precedent. |

> If no clear arbiter exists: Document both positions. Flag as `[UNRESOLVED — USER DECISION REQUIRED]`.

### Blind Spot Report (MANDATORY)

> **Rule**: Always tell the user WHAT the other model likely missed, WHY they missed it, and WHAT you're doing about it.

**Format**:

```
## Blind Spot Report

**What [Other Model] Likely Missed**:
- [Issue 1]: [Why they missed it] → [Remediation action]
- [Issue 2]: [Why they missed it] → [Remediation action]

**Auto-Remediation Status**: [X] items fixed. [Y] items require user input.
```

**Execution**: After identifying blind spots, **do the needful immediately**—don't wait for permission. Only escalate if the fix requires strategic decision (e.g., deleting files, changing user profile) OR if the file is on the **No-Touch List**.

### The Verdict

End your audit with a clear statement:
> *"Audit complete. Reviewed [X] files changed in this session. [Model Name] detected [Y] issues typical of [Other Model]. Patches applied."*

## 6. Strategic Depth Check (/ultrathink)

> **Goal**: Move beyond "Is it correct?" to "What does this MEAN?"
> **Trigger**: If the session produced a new strategy, framework, or case study.

- [ ] **Execute**: `/ultrathink` on the key artifacts of this session.
- [ ] **Prompt**: *"Analyze the second-order effects of the work we just did. What is the hidden implication?"*
- [ ] **Capture**: If a new realization emerges (like "Knowledge commoditizes to zero"), document it immediately.

## 7. The Autonomous Optimisation (Chain Reaction)

> **Logic**: "Now that we have audited the past, we must optimize the future."
> **Constraint**: Respects `AUDIT_DEPTH` limit. Will not trigger if at max depth.

// turbo

```bash
# Execute the needful workflow to apply high-value actions based on audit findings
# NOTE: This respects AUDIT_DEPTH. If depth >= 2, this step is SKIPPED.
/needful
```

---

## Audit Output Schema

Every audit run produces this structured output:

```json
{
  "audit_id": "uuid",
  "timestamp": "ISO8601",
  "mode": "session|deep",
  "depth": 1,
  "status": "pass|warn|fail",
  "confidence": "low|medium|high",
  "findings": {
    "blockers": 0,
    "warnings": 0,
    "auto_fixed": 0,
    "user_required": 0
  },
  "stop_reason": "all_clear|risk_accepted|recursion_limit|user_halt"
}
```

---

## Summary

| Phase | Focus | Gate |
|-------|-------|------|
| 0. Safety | Guardrails | Recursion ≤ 2, No-Touch honored |
| 1. Structure | Readability/Attention | No "blobs" > 300 words |
| 2. Reasoning | Profile Constraints | 100% Compliance (Kelly, 6w5, etc.) |
| 3. Red Team | Contradictions | No generic bloat |
| 4. General Maintenance | Links/Orphans | 0 Missing Links |
| 5. Adversarial | Gemini vs Claude | "Red Team" complete + Tie-Breaking |
| 6. Strategic Depth | Second-Order Effects | **Run `/ultrathink`** |
| 7. Optimisation | High-Value Action | **Auto-Trigger `/needful`** (if depth < 2) |

---

## Tagging

# workflow #automation #audit
