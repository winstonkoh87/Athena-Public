---

created: 2025-12-22
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-22
last_updated: 2026-01-05
---

# Protocol 141: Claim Atomization Audit

> **Status**: ACTIVE  
> **Version**: 1.0  
> **Created**: 2025-12-22  
> **Source**: Harvested from Brainqub3 (2025)

---

## Purpose

Prevent AI hallucinations from reaching deliverables by decomposing outputs into verifiable atomic claims before release. This operationalizes [Law #5: Epistemic Rigor](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/Core_Identity.md) with a structured process.

---

## Trigger Conditions

| Context | Action |
|---------|--------|
| External-facing deliverable (report, case study, public content) | **Mandatory** |
| Internal analysis with external claims | **Recommended** |
| Quick responses with no external facts | **Skip** |

---

## The 4-Phase Audit

### Phase 1: Decompose

Break the output into individual atomic claims.

**Heuristic**: If a sentence makes an assertion, it's a claim.

```
Input: "Deloitte faced sanctions in 2025 after submitting a $290K report with fabricated references."

Claims:
1. Deloitte faced sanctions
2. This occurred in 2025
3. The report cost $290K
4. The report contained fabricated references
```

### Phase 2: Classify

Tag each claim by type:

| Tag | Definition | Verification Requirement |
|-----|------------|--------------------------|
| `[external-fact]` | Verifiable against public sources | **Must cite** |
| `[internal-analysis]` | Derived from user data/context | Mark as internal |
| `[opinion]` | Subjective judgment | Mark as opinion |
| `[framework]` | Named methodology/theory | Cite creator |

### Phase 3: Verify

| Claim Type | Action |
|------------|--------|
| `[external-fact]` | Search for corroborating source. Cite or remove. |
| `[framework]` | Verify creator and year. Add to [References.md](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/references/References.md). |
| `[internal-analysis]` | Ensure logic chain is sound. No citation needed. |
| `[opinion]` | Explicitly mark as opinion. No citation needed. |

### Phase 4: Score

Aggregate verification results:

| Score | Meaning | Action |
|-------|---------|--------|
| **High (>80%)** | Most claims verified or properly marked | ✅ Clear for delivery |
| **Medium (50-80%)** | Some gaps | ⚠️ Review flagged claims |
| **Low (<50%)** | Significant unverified claims | ❌ Do not deliver. Remediate. |

---

## Quick Checklist (Pre-Delivery)

- [ ] All `[external-fact]` claims have inline citations
- [ ] All `[framework]` references cite creator + year
- [ ] All `[internal-analysis]` claims are marked as such
- [ ] No orphan statistics (numbers without sources)
- [ ] Confidence score calculated

---

## Relationship to Other Protocols

| Protocol | Relationship |
|----------|--------------|
| [Law #5: Epistemic Rigor](file:///Users/[AUTHOR]/Desktop/Project Athena/.framework/v7.0/modules/Core_Identity.md) | This protocol operationalizes Law #5 |
| [Protocol 140: Base Rate Audit](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/140-base-rate-audit.md) | Verify statistical claims against base rates |
| [Protocol 75: Synthetic Parallel Reasoning](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/decision/75-synthetic-parallel-reasoning.md) | Track B (Adversarial) naturally performs claim verification |

---

## References

- Brainqub3. (2025). *How to Catch AI Hallucinations BEFORE Your Client Does*. YouTube.
- Liu, N. F., et al. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. arXiv.

---

## Tagging

# verification #law-5 #hallucination #quality #protocol
