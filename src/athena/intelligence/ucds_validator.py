"""
athena.intelligence.ucds_validator
==================================

Universal Counterparty Dossier Standard (UCDS) Validator & Invariant Auditor.
Enforces CANONICAL §513, RSC-580 §5.4, and PSY-585 §7.

Validates counterparty due diligence dossiers against 5 core invariants:
1. Section Completeness: 6 mandatory UCDS sections.
2. Non-Compensatory Binary Knockout Gates ("Booleans Gate; Scores Only Order").
3. Directional Cashflow Inversion (Track A-R front-loaded vs. Track A-P back-loaded).
4. 5-State Provenance Ladder & Singapore EPC Exemption (CA Sec 205B/C).
5. Functional Archetype Quarantine (Permitted in Track A; strictly forbidden in Track B).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TrackType(str, Enum):
    """Counterparty track taxonomy."""
    TRACK_A_R = "Track A-R"  # Client / Accounts Receivable (paying us)
    TRACK_A_P = "Track A-P"  # Vendor / Accounts Payable (us paying them)
    TRACK_A_N = "Track A-N"  # Strategic Node / Founder / JV Partner
    TRACK_B = "Track B"      # Personal / Relational Counterparty


class KnockoutStatus(str, Enum):
    """Binary knockout gate decision."""
    PASS = "PASS"
    FAIL = "FAIL"
    HARD_VETO = "HARD VETO"


# Mandatory UCDS sections
REQUIRED_SECTIONS: list[tuple[str, re.Pattern[str]]] = [
    ("Ground Truth & Perimeter Verification", re.compile(r"(?:1\.\s*)?GROUND TRUTH\s*(?:&|AND)?\s*PERIMETER", re.IGNORECASE)),
    ("The 360-Degree SWOT", re.compile(r"(?:2\.\s*)?(?:THE\s*)?360-DEGREE\s*SWOT|\bSWOT\b", re.IGNORECASE)),
    ("Value To Us (Operator Utility Vector)", re.compile(r"(?:3\.\s*)?VALUE TO US|\bOPERATOR UTILITY VECTOR\b", re.IGNORECASE)),
    ("Horizon Forecast & Exit Profile", re.compile(r"(?:4\.\s*)?HORIZON FORECAST|\bEXIT PROFILE\b", re.IGNORECASE)),
    ("Two-Sided Error Accounting", re.compile(r"(?:5\.\s*)?TWO-SIDED ERROR ACCOUNTING|\bTYPE 1\s*(?:AND|&|VS)\s*TYPE 2\b", re.IGNORECASE)),
    ("Engagement Playbook & Litmus Test", re.compile(r"(?:6\.\s*)?ENGAGEMENT PLAYBOOK|\bLITMUS TEST\b", re.IGNORECASE)),
]

# Provenance states
PROVENANCE_TAGS = ["VERIFIED", "ATTESTED", "ABSENT:LAWFUL", "ABSENT:SUSPICIOUS", "CONTRADICTED"]

# Functional archetypes (quarantined to Track A)
FUNCTIONAL_ARCHETYPES = [
    "tactical engine",
    "institutional bridge",
    "diplomat",
    "campaign operator",
    "builds to exit",
    "empire builder",
    "mercenary",
]


@dataclass
class UCDSAuditReport:
    """Structured compliance report for a UCDS counterparty dossier."""
    target_name: str
    track: str
    knockout_verdict: str
    is_valid: bool
    compliance_score: float  # 0.0 to 1.0
    sections_present: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)
    provenance_counts: dict[str, int] = field(default_factory=dict)
    directional_cashflow_verdict: str = "PASS"
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize audit report to dictionary."""
        return {
            "target_name": self.target_name,
            "track": self.track,
            "knockout_verdict": self.knockout_verdict,
            "is_valid": self.is_valid,
            "compliance_score": round(self.compliance_score, 2),
            "sections_present": self.sections_present,
            "sections_missing": self.sections_missing,
            "provenance_counts": self.provenance_counts,
            "directional_cashflow_verdict": self.directional_cashflow_verdict,
            "violations": self.violations,
            "warnings": self.warnings,
        }


class UCDSDossierValidator:
    """Mechanical validator for Universal Counterparty Dossier Standard (UCDS) compliance."""

    def __init__(self) -> None:
        pass

    def audit(self, text: str) -> UCDSAuditReport:
        """Audit a markdown dossier against UCDS invariants."""
        violations: list[str] = []
        warnings: list[str] = []

        # 1. Header Metadata Extraction
        target_m = re.search(r"^TARGET:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
        target_name = target_m.group(1).strip() if target_m else "UNKNOWN_TARGET"

        track_m = re.search(r"^TRACK:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
        track_raw = track_m.group(1).strip() if track_m else ""

        detected_track = "UNKNOWN"
        if re.search(r"A-R", track_raw, re.IGNORECASE):
            detected_track = TrackType.TRACK_A_R.value
        elif re.search(r"A-P", track_raw, re.IGNORECASE):
            detected_track = TrackType.TRACK_A_P.value
        elif re.search(r"A-N", track_raw, re.IGNORECASE):
            detected_track = TrackType.TRACK_A_N.value
        elif re.search(r"Track\s*B", track_raw, re.IGNORECASE):
            detected_track = TrackType.TRACK_B.value

        if detected_track == "UNKNOWN":
            violations.append("Missing or invalid TRACK declaration (must specify Track A-R, Track A-P, Track A-N, or Track B).")

        # 2. Knockout Gate Evaluation
        knockout_m = re.search(r"^KNOCKOUT GATE:\s*(PASS|FAIL|HARD VETO)(.*)$", text, re.MULTILINE | re.IGNORECASE)
        knockout_verdict = knockout_m.group(1).upper() if knockout_m else "MISSING"

        if knockout_verdict == "MISSING":
            violations.append("Missing KNOCKOUT GATE declaration in header block.")
        elif knockout_verdict in ("FAIL", "HARD VETO"):
            # If knockout gate failed, check if the dossier attempts to recommend proceeding anyway
            proceed_match = re.search(
                r"(?:recommendation|verdict|stance|action):\s*(?:proceed|engage|contract|partner|hire|onboard)",
                text,
                re.IGNORECASE,
            )
            if proceed_match:
                violations.append("Compensatory bypass detected: Knockout Gate is FAIL/HARD VETO, but dossier recommends engagement.")

        # Check for unacknowledged statutory red flags
        statutory_flags = re.search(
            r"\b(active bankruptcy|insolvency petition|unsatisfied civil judgment|unlicensed regulated (?:fund|broker|trade)|corroborated project abandonment)\b",
            text,
            re.IGNORECASE,
        )
        if statutory_flags and knockout_verdict == "PASS":
            violations.append(
                f"Statutory knockout conflict: '{statutory_flags.group(1)}' detected in dossier, but KNOCKOUT GATE is marked PASS."
            )

        # 3. Section Completeness Audit
        sections_present: list[str] = []
        sections_missing: list[str] = []
        for sec_name, pattern in REQUIRED_SECTIONS:
            if pattern.search(text):
                sections_present.append(sec_name)
            else:
                sections_missing.append(sec_name)

        if sections_missing:
            violations.append(f"Missing mandatory UCDS sections: {', '.join(sections_missing)}")

        # 4. Directional Cashflow Inversion Audit
        directional_verdict = "PASS"
        sec6_m = re.search(
            r"(?:ENGAGEMENT PLAYBOOK|LITMUS TEST)(.*?)(?:====================|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        sec6_text = sec6_m.group(1) if sec6_m else text

        if detected_track == TrackType.TRACK_A_R.value:
            # Client / Accounts Receivable: Must mandate front-loaded cash (upfront, retainer, CBD)
            backloaded_client = re.search(
                r"(?:back-load|backweighted|10/15/25|milestone payment upon delivery|payable upon final completion|net 30|net 60)",
                sec6_text,
                re.IGNORECASE,
            )
            frontloaded_client = re.search(
                r"(?:front-load|100% upfront|70% upfront|50/50 rolling retainer|cash before delivery|cbd\b|retainer \+ kill switch)",
                sec6_text,
                re.IGNORECASE,
            )
            if backloaded_client:
                directional_verdict = "FAIL"
                violations.append(
                    "Directional Cashflow Inversion violation: Track A-R (Client Receivable) must mandate front-loaded cash (70%-100% upfront / retainer), but back-loaded terms were specified."
                )
            elif not frontloaded_client:
                warnings.append("Track A-R stance lacks explicit front-loaded cash commitment (e.g. 100% upfront or rolling retainer).")

        elif detected_track == TrackType.TRACK_A_P.value:
            # Vendor / Accounts Payable: Must mandate back-loaded cash (milestones, retention)
            upfront_vendor = re.search(
                r"(?:100% upfront|full payment before start|(?<!zero\s)(?<!no\s)uncollateralized prepayment)",
                sec6_text,
                re.IGNORECASE,
            )
            backloaded_vendor = re.search(
                r"(?:back-load|milestones|10/15/25|retention|progress payments|pay upon delivery|verification)",
                sec6_text,
                re.IGNORECASE,
            )
            if upfront_vendor:
                directional_verdict = "FAIL"
                violations.append(
                    "Directional Cashflow Inversion violation: Track A-P (Vendor Payable) must mandate back-loaded milestones + retention, but 100% uncollateralized upfront payment was specified."
                )
            elif not backloaded_vendor:
                warnings.append("Track A-P stance lacks explicit back-loaded milestone commitment.")

        # 5. Provenance Ladder & Singapore EPC Statutory Exemption
        prov_counts: dict[str, int] = {}
        for tag in PROVENANCE_TAGS:
            count = len(re.findall(re.escape(tag), text, re.IGNORECASE))
            prov_counts[tag] = count

        total_prov = sum(prov_counts.values())
        if total_prov == 0:
            warnings.append("Zero 5-state provenance tags found ([VERIFIED], [ATTESTED], [ABSENT:LAWFUL], etc.).")

        # Singapore EPC Exemption check (CA Sec 205B/C)
        epc_false_positive = re.search(
            r"(?:epc|exempt private company|<=20 shareholders).*?(?:missing (?:financials?|accounts?|balance sheet)|no filing).*?\[?(?:ABSENT:SUSPICIOUS|fraud|suspicious)\]?",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if epc_false_positive:
            violations.append(
                "Singapore EPC Statutory Exemption violation: Under Companies Act Sec 205B/C, solvent EPCs are exempt from filing annual accounts. Missing statements must be tagged ABSENT:LAWFUL, not ABSENT:SUSPICIOUS."
            )

        # 6. Functional Archetype Quarantine
        archetypes_found = []
        for arch in FUNCTIONAL_ARCHETYPES:
            if re.search(r"\b" + re.escape(arch) + r"\b", text, re.IGNORECASE):
                archetypes_found.append(arch)

        if detected_track == TrackType.TRACK_B.value:
            if archetypes_found:
                violations.append(
                    f"Functional Archetype Quarantine breach: Archetypes ({', '.join(archetypes_found)}) are quarantined to Track A commercial dossiers and forbidden in Track B personal evaluations."
                )
            # Check for unanchored decimal personality scores (e.g., SOAM 7.4/10)
            if re.search(r"\b(?:SOAM|social|personality)(?:\s*score)?\s*(?:of|:)?\s*\d+(?:\.\d+)?/10\b", text, re.IGNORECASE):
                violations.append("Unanchored decimal personality/social scoring forbidden in Track B evaluation.")

        # 7. LaTeX Delimiter Leak Check
        if re.search(r"(?<!\$)\$[^\$\n]+?\$(?!\$)|(?<!\\)\\\([^\)]+?\\\)", text):
            violations.append("LaTeX math delimiters detected ($...$ or \\(...\\)). Use plain ASCII only.")

        # Calculate compliance score
        passed_sections = len(sections_present)
        score_base = (passed_sections / len(REQUIRED_SECTIONS)) if REQUIRED_SECTIONS else 1.0
        if violations:
            # Penalize by 0.15 per violation
            compliance_score = max(0.0, score_base - (0.15 * len(violations)))
        else:
            compliance_score = score_base

        is_valid = len(violations) == 0 and len(sections_missing) == 0 and knockout_verdict in ("PASS", "FAIL", "HARD VETO")

        return UCDSAuditReport(
            target_name=target_name,
            track=detected_track,
            knockout_verdict=knockout_verdict,
            is_valid=is_valid,
            compliance_score=compliance_score,
            sections_present=sections_present,
            sections_missing=sections_missing,
            provenance_counts=prov_counts,
            directional_cashflow_verdict=directional_verdict,
            violations=violations,
            warnings=warnings,
        )


def audit_ucds_dossier(text: str) -> UCDSAuditReport:
    """Helper function to audit a UCDS dossier string."""
    validator = UCDSDossierValidator()
    return validator.audit(text)
