"""
athena.intelligence.evidence_contract
====================================

Deterministic Evidence Lineage Schema & Epistemic Provenance Gate (TD-084).

Prevents corroboration inflation where agent-authored design proposals
(e.g., CS-043, CS-448, CS-453) or superseded claims are retrieved and treated
as independent empirical behavioral observations in profiling prompts (PSY-585).
Enforces calibrated interpersonal evaluation and halts pseudo-scientific fabrication.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ClaimKind(str, Enum):
    """Epistemic classification of an evidence claim."""
    OBSERVATION = "observation"                  # Direct sensory or documentary fact
    REPORTED_STATEMENT = "reported_statement"    # Counterparty or witness utterance
    INFERENCE = "inference"                      # Deductive or inductive conclusion
    RECOMMENDATION = "recommendation"            # Tactical or strategic guidance
    DESIGN_PROPOSAL = "design_proposal"          # Agent-authored brand/marketing concept


class ClaimStatus(str, Enum):
    """Lifecycle and veracity status of a claim."""
    ACTIVE = "active"                            # Verified and current
    DISPUTED = "disputed"                        # Contested by counter-evidence
    SUPERSEDED = "superseded"                    # Overridden by newer observations
    LEGACY_UNREVIEWED = "legacy_unreviewed"      # Historical data unvalidated


@dataclass
class EvidenceClaim:
    """Atomic unit of evidenced observation or proposal."""
    claim_id: str
    claim_kind: ClaimKind
    statement: str
    source_refs: list[str] = field(default_factory=list)
    evidence_family_id: str = ""
    status: ClaimStatus = ClaimStatus.ACTIVE
    epistemic_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize claim to dictionary representation."""
        data = asdict(self)
        data["claim_kind"] = self.claim_kind.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceClaim:
        """Construct EvidenceClaim from dictionary."""
        return cls(
            claim_id=data["claim_id"],
            claim_kind=ClaimKind(data["claim_kind"]),
            statement=data.get("statement", ""),
            source_refs=list(data.get("source_refs", [])),
            evidence_family_id=data.get("evidence_family_id", ""),
            status=ClaimStatus(data.get("status", ClaimStatus.ACTIVE.value)),
            epistemic_note=data.get("epistemic_note", ""),
        )


def extract_evidence_claims_from_frontmatter(
    metadata: dict[str, Any],
    source_ref: str = "",
    default_statement: str = "",
) -> list[EvidenceClaim]:
    """Extract structured evidence claims from YAML frontmatter metadata."""
    kind_raw = metadata.get("claim_kind")
    if not kind_raw:
        return []

    try:
        kind = ClaimKind(kind_raw.lower().strip())
    except ValueError:
        kind = ClaimKind.INFERENCE

    epistemic_note = str(metadata.get("epistemic_note", ""))
    claim_id = f"CLM-{abs(hash(source_ref or default_statement)) % 1000000:06d}"

    claim = EvidenceClaim(
        claim_id=claim_id,
        claim_kind=kind,
        statement=default_statement or epistemic_note or "Frontmatter tagged claim",
        source_refs=[source_ref] if source_ref else [],
        evidence_family_id=f"FAM-{source_ref.split('/')[-1].split('.')[0]}" if source_ref else "",
        status=ClaimStatus.ACTIVE,
        epistemic_note=epistemic_note,
    )
    return [claim]


def filter_claims_for_profiling(
    claims: list[EvidenceClaim],
    allowed_kinds: set[ClaimKind] | None = None,
) -> list[EvidenceClaim]:
    """Filter claims to prevent corroboration inflation in behavioral profiling.

    Strictly suppresses DESIGN_PROPOSAL, SUPERSEDED, and DISPUTED claims from
    being fed into behavioral investigative analysis (PSY-585) engines.
    """
    if allowed_kinds is None:
        allowed_kinds = {
            ClaimKind.OBSERVATION,
            ClaimKind.REPORTED_STATEMENT,
            ClaimKind.INFERENCE,
        }

    filtered = []
    for c in claims:
        # Exclude unapproved kinds (specifically DESIGN_PROPOSAL)
        if c.claim_kind not in allowed_kinds:
            continue
        # Exclude superseded and disputed claims from profiling context
        if c.status in {ClaimStatus.SUPERSEDED, ClaimStatus.DISPUTED}:
            continue
        filtered.append(c)
    return filtered


def validate_interpersonal_calibration(text: str) -> dict[str, Any]:
    """Validate interpersonal analysis text against calibration anti-patterns.

    Asserts:
    1. Absence of fabricated psychometric percentiles (e.g., 'Machiavellianism 94th percentile').
    2. Rejection of unevidenced childhood wound attributions without verified historical lineage.
    3. Positive control: Preserves decisive protective triggers for genuine fraud/breach signals.
    """
    violations = []

    # 1. Detect fabricated psychometric percentiles
    percentile_pattern = re.compile(
        r"(?:percentile|\b\d{1,2}%\b).*?\b(narcissis|machiavell|psychopath|dark triad|sociopath|borderline|histrionic|neuroticism)\b|"
        r"\b(narcissis|machiavell|psychopath|dark triad|sociopath|borderline|histrionic|neuroticism)\b.*?(?:percentile|\b\d{1,2}%\b)",
        re.IGNORECASE,
    )
    if percentile_pattern.search(text):
        violations.append("Fabricated psychometric percentile detected without standardized clinical inventory.")

    # 2. Detect unevidenced childhood wound attributions
    childhood_wound_pattern = re.compile(
        r"\b(childhood wound|childhood trauma|scholastic humiliation|elementary school wound|nursery trauma)\b",
        re.IGNORECASE,
    )
    if childhood_wound_pattern.search(text):
        violations.append("Unverified childhood wound attribution without primary historical lineage.")

    # 3. Positive control check: genuine fraud / contract breach signals
    fraud_pattern = re.compile(
        r"\b(\$1\s+paid-up|\$1\s+shell|shell entity|personal guarantee|guaranteed.*return|guaranteed.*annualized|cis\b|regulatory evasion)\b",
        re.IGNORECASE,
    )
    protective_triggered = False
    protective_rec = ""
    if fraud_pattern.search(text):
        protective_triggered = True
        protective_rec = "Protective action verified: decisive contractual halt or disengagement mandated."

    return {
        "calibrated": len(violations) == 0,
        "violations": violations,
        "protective_action_triggered": protective_triggered,
        "protective_recommendation": protective_rec,
    }
