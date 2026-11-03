"""
athena.intelligence.spec_gate
==============================
Upstream Specification Contract Gate (CANONICAL §507 / TD-078).

Enforces the 90/10 Upstream Specification Primacy Law and P vs NP
Verification Asymmetry Invariant. Mechanically validates that a project or
deliverable's `SPECIFICATION.md` locks all 4 mandatory pillars:

1. Physical Envelope: Word count limits, slide caps, video timing windows.
2. Disciplinary Lexicon: Syllabus models, allowed frameworks, prohibited boundaries.
3. Frozen Empirical Telemetry: Primary datasets, raw files, verified timestamps.
4. Submission Binary Contract: Target deliverable formats and archive quarantine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SpecPillarResult:
    """Audit result for a single specification pillar."""
    pillar_name: str
    satisfied: bool
    score: float
    evidence: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pillar_name": self.pillar_name,
            "satisfied": self.satisfied,
            "score": round(self.score, 2),
            "evidence": self.evidence,
            "missing": self.missing,
        }


@dataclass
class SpecVerificationResult:
    """Aggregate result from Upstream Specification Gate validation."""
    spec_path: str
    passed: bool
    overall_score: float
    pillars: dict[str, SpecPillarResult] = field(default_factory=dict)
    missing_pillars: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_path": self.spec_path,
            "passed": self.passed,
            "overall_score": round(self.overall_score, 2),
            "pillars": {k: v.to_dict() for k, v in self.pillars.items()},
            "missing_pillars": self.missing_pillars,
            "metadata": self.metadata,
        }


class UpstreamSpecGate:
    """
    Deterministic validator enforcing CANONICAL Entry §507 upstream spec standards.
    Zero-dependency, offline-first.
    """

    # --- Regex Patterns for 4 Core Pillars ---

    # Pillar 1: Physical Envelope
    RE_WORD_COUNT = re.compile(
        r"(?:word\s*count|words|word\s*limit|word\s*allowance|ceiling|floor)[\s:\-–—]+(?:\d+[\d,]*\s*[-–—to]+\s*\d+[\d,]*|\d+[\d,]*)|\b\d+[\d,]*\s*words\b",
        re.IGNORECASE,
    )
    RE_SLIDE_CAP = re.compile(
        r"(?:slide\s*count|slides|slide\s*cap|content\s*slides|deck\s*limit)[\s:\-–—]+(?:\d+[\d,]*|\d+[\d,]*\s*slides?)|\b\d+\s*content\s*slides\b|\b\d+\s*slides\b",
        re.IGNORECASE,
    )
    RE_VIDEO_TIMING = re.compile(
        r"(?:video|timing|duration|runtime|run\s*time|time\s*window)[\s:\-–—]+(?:\d+[\d.]*\s*(?:min|mins|minutes|sec|seconds)|(?:\d+m\s*\d+s))|\b\d+\s*(?:min|mins|minutes|seconds)\b",
        re.IGNORECASE,
    )

    # Pillar 2: Disciplinary Lexicon & Scope Boundaries
    RE_DISCIPLINARY = re.compile(
        r"\b(?:syllabus|course|module|framework|theory|models?|rubrics?|standards?|ISO\s*\d+|APA\s*7th|curriculum|disciplinary|lexicon|kinematics?|equations?)\b",
        re.IGNORECASE,
    )
    RE_SCOPE_BOUNDARY = re.compile(
        r"\b(?:strictly\s*out\s*of\s*scope|out\s*of\s*scope|prohibited|forbidden|prototype\s*demarcation|demarcation|non-scope|anti-scope|zero\s*marks?|scope\s*matrix|negative\s*scope)\b",
        re.IGNORECASE,
    )

    # Pillar 3: Frozen Empirical Telemetry
    RE_EMPIRICAL_DATA = re.compile(
        r"\b(?:empirical|telemetry|ground\s*truth|raw\s*evidence|raw_evidence|primary\s*field|interviews?|surveys?|scraped|datasets?|data\s*source|live\s*feed|drift|excursions?|measurements?|sensors?|supplier\s*interviews?)\b",
        re.IGNORECASE,
    )
    RE_FROZEN_PROVENANCE = re.compile(
        r"\b(?:last\s*updated|verified\s*timestamps?|timestamps?|frozen\s*snapshot|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b)\b",
        re.IGNORECASE,
    )

    # Pillar 4: Submission Binary Contract & Quarantine
    RE_BINARY_FORMATS = re.compile(
        r"\b(?:\.docx|\.pptx|\.pdf|\.xlsx|\.zip|\.py|\.html|\.mp4|\.mov)\b",
        re.IGNORECASE,
    )
    RE_QUARANTINE_BOUNDARY = re.compile(
        r"\b(?:quarantine|quarantined|deliverables/archive|archive/|auxiliary\s*notes|defense\s*notes|cheat\s*sheet|staging\s*boundary)\b",
        re.IGNORECASE,
    )

    @classmethod
    def verify_content(
        cls, content: str, spec_path: str = "SPECIFICATION.md"
    ) -> SpecVerificationResult:
        """Evaluate raw markdown specification content against the 4 pillars."""
        metadata = cls._extract_metadata(content)
        pillars: dict[str, SpecPillarResult] = {}

        # 1. Physical Envelope
        env_evidence: list[str] = []
        env_missing: list[str] = []
        m_wc = cls.RE_WORD_COUNT.findall(content)
        m_sc = cls.RE_SLIDE_CAP.findall(content)
        m_vt = cls.RE_VIDEO_TIMING.findall(content)

        if m_wc:
            env_evidence.append(f"Word envelope: {m_wc[0].strip()}")
        if m_sc:
            env_evidence.append(f"Slide envelope: {m_sc[0].strip()}")
        if m_vt:
            env_evidence.append(f"Timing envelope: {m_vt[0].strip()}")

        if env_evidence:
            pillars["physical_envelope"] = SpecPillarResult(
                pillar_name="Physical Envelope",
                satisfied=True,
                score=1.0,
                evidence=env_evidence,
                missing=[],
            )
        else:
            env_missing.append(
                "Missing word count limits, slide caps, or video timing window"
            )
            pillars["physical_envelope"] = SpecPillarResult(
                pillar_name="Physical Envelope",
                satisfied=False,
                score=0.0,
                evidence=[],
                missing=env_missing,
            )

        # 2. Disciplinary Lexicon
        lex_evidence: list[str] = []
        lex_missing: list[str] = []
        m_disc = cls.RE_DISCIPLINARY.findall(content)
        m_bound = cls.RE_SCOPE_BOUNDARY.findall(content)

        if m_disc:
            lex_evidence.append(
                f"Syllabus / Disciplinary anchors: {', '.join(sorted(set(m_disc))[:4])}"
            )
        else:
            lex_missing.append("No explicit syllabus models or disciplinary frameworks declared")

        if m_bound:
            lex_evidence.append(
                f"Scope boundary / Prohibitions: {', '.join(sorted(set(m_bound))[:3])}"
            )
        else:
            lex_missing.append("No explicit out-of-scope boundaries or negative scope declared")

        lex_satisfied = bool(m_disc and m_bound)
        lex_score = (0.5 if m_disc else 0.0) + (0.5 if m_bound else 0.0)
        pillars["disciplinary_lexicon"] = SpecPillarResult(
            pillar_name="Disciplinary Lexicon",
            satisfied=lex_satisfied,
            score=lex_score,
            evidence=lex_evidence,
            missing=lex_missing,
        )

        # 3. Frozen Empirical Telemetry
        tel_evidence: list[str] = []
        tel_missing: list[str] = []
        m_emp = cls.RE_EMPIRICAL_DATA.findall(content)
        m_prov = cls.RE_FROZEN_PROVENANCE.findall(content)

        if m_emp:
            tel_evidence.append(
                f"Empirical data source: {', '.join(sorted(set(m_emp))[:3])}"
            )
        else:
            tel_missing.append("No primary empirical dataset or raw telemetry source declared")

        if m_prov:
            tel_evidence.append(
                f"Frozen temporal anchor: {', '.join(sorted(set(m_prov))[:3])}"
            )
        else:
            tel_missing.append("No frozen date/timestamp or snapshot version declared")

        tel_satisfied = bool(m_emp and m_prov)
        tel_score = (0.5 if m_emp else 0.0) + (0.5 if m_prov else 0.0)
        pillars["frozen_telemetry"] = SpecPillarResult(
            pillar_name="Frozen Empirical Telemetry",
            satisfied=tel_satisfied,
            score=tel_score,
            evidence=tel_evidence,
            missing=tel_missing,
        )

        # 4. Submission Binary Contract
        bin_evidence: list[str] = []
        bin_missing: list[str] = []
        m_bin = cls.RE_BINARY_FORMATS.findall(content)
        m_quar = cls.RE_QUARANTINE_BOUNDARY.findall(content)

        if m_bin:
            bin_evidence.append(
                f"Deliverable formats: {', '.join(sorted(set(m_bin))[:4])}"
            )
        else:
            bin_missing.append("No explicit deliverable binaries (.docx, .pdf, .pptx, etc.) declared")

        if m_quar:
            bin_evidence.append(
                f"Quarantine / packaging: {', '.join(sorted(set(m_quar))[:3])}"
            )
        else:
            bin_missing.append("No archive quarantine or auxiliary staging demarcation")

        bin_satisfied = bool(m_bin and m_quar)
        bin_score = (0.5 if m_bin else 0.0) + (0.5 if m_quar else 0.0)
        pillars["submission_contract"] = SpecPillarResult(
            pillar_name="Submission Binary Contract",
            satisfied=bin_satisfied,
            score=bin_score,
            evidence=bin_evidence,
            missing=bin_missing,
        )

        # Aggregate metrics
        total_score = sum(p.score for p in pillars.values()) / len(pillars)
        all_satisfied = all(p.satisfied for p in pillars.values())
        missing_pillars = [name for name, p in pillars.items() if not p.satisfied]

        return SpecVerificationResult(
            spec_path=spec_path,
            passed=all_satisfied,
            overall_score=total_score,
            pillars=pillars,
            missing_pillars=missing_pillars,
            metadata=metadata,
        )

    @classmethod
    def verify_file(cls, path: str | Path) -> SpecVerificationResult:
        """Load and verify a SPECIFICATION.md file from disk."""
        target_path = Path(path).resolve()
        if not target_path.exists():
            return SpecVerificationResult(
                spec_path=str(target_path),
                passed=False,
                overall_score=0.0,
                pillars={},
                missing_pillars=[
                    "physical_envelope",
                    "disciplinary_lexicon",
                    "frozen_telemetry",
                    "submission_contract",
                ],
                metadata={},
            )

        content = target_path.read_text(encoding="utf-8")
        return cls.verify_content(content, spec_path=str(target_path))

    @classmethod
    def verify_directory(cls, dir_path: str | Path) -> SpecVerificationResult:
        """Find SPECIFICATION.md in the target directory and verify it."""
        base = Path(dir_path).resolve()
        candidate = base / "SPECIFICATION.md"
        if candidate.exists():
            return cls.verify_file(candidate)

        # Search immediate children
        for p in base.glob("*.md"):
            if "spec" in p.name.lower():
                return cls.verify_file(p)

        return SpecVerificationResult(
            spec_path=str(base / "SPECIFICATION.md"),
            passed=False,
            overall_score=0.0,
            pillars={},
            missing_pillars=[
                "physical_envelope",
                "disciplinary_lexicon",
                "frozen_telemetry",
                "submission_contract",
            ],
            metadata={},
        )

    @classmethod
    def format_ascii_report(cls, result: SpecVerificationResult) -> str:
        """Render human-readable, ASCII-only verification report."""
        lines = [
            "============================================================",
            "=== Upstream Specification Contract Gate (CANONICAL §507) ===",
            "============================================================",
            f"Target Spec:       {result.spec_path}",
            f"Overall Verdict:   {'PASS' if result.passed else 'FAIL'}",
            f"Compliance Score:  {int(result.overall_score * 100)}% ({sum(1 for p in result.pillars.values() if p.satisfied)}/{len(result.pillars)} pillars)",
        ]

        if result.metadata:
            meta_str = ", ".join(f"{k}: {v}" for k, v in result.metadata.items())
            lines.append(f"Metadata:          {meta_str}")

        lines.append("\n--- Pillar Audit Breakdown ---")
        for key, p in result.pillars.items():
            mark = "[x]" if p.satisfied else "[ ]"
            verdict = "PASS" if p.satisfied else "FAIL"
            score_pct = int(p.score * 100)
            lines.append(f"{mark} {p.pillar_name:<26} {verdict} ({score_pct}%)")
            for ev in p.evidence:
                lines.append(f"    ├─ Evidence: {ev}")
            for mi in p.missing:
                lines.append(f"    └─ Missing:  {mi}")

        if result.missing_pillars:
            lines.append("\n⚠️ Gate Blocked: Missing upstream specification invariants.")
            lines.append("   Deliverable compilation prohibited until spec is sealed.")
        else:
            lines.append("\n⚡ Upstream Specification Sealed: Authorized for compilation.")

        lines.append("============================================================")
        return "\n".join(lines)

    @staticmethod
    def _extract_metadata(content: str) -> dict[str, str]:
        """Extract academic course, student, institution, and project metadata."""
        meta: dict[str, str] = {}
        for line in content.splitlines()[:25]:
            line = line.strip()
            if not line.startswith(">"):
                continue
            cleaned = line.lstrip("> *#").strip()
            if ":" in cleaned:
                parts = cleaned.split(":", 1)
                k = parts[0].strip().replace("*", "")
                v = parts[1].strip().replace("*", "").replace("`", "")
                if k and v:
                    meta[k] = v
        return meta
