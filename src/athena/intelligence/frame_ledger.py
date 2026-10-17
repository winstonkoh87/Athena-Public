"""
athena.intelligence.frame_ledger
================================

Deterministic ledger + contract validator for the Problem-Framing layer
(Cluster #15: RSN-504 -> RSN-505 -> RSN-506).

Why this module exists
----------------------
Before this module, the "55-minute problem framing" pipeline was pure prose:

  * Zero runtime artifacts named in RSN-504/505/506 appear anywhere in the
    3,162-file memory corpus (0 hits for "Candidate Reframe", "Literal
    Request", "Problem Statement Lock", "Kill Criteria", "Reversibility
    score").
  * No object anywhere in code represents a frame, a reframe, a hypothesis
    set, a pre-registered exit criterion, or a kill criterion.

This module makes the pipeline *executable and auditable* without any LLM,
network, or third-party dependency:

  1. FRAME CONTRACT (R1-R10) - machine-checkable gates. A frame that cannot
     be falsified, has no rival hypothesis, has no numeric exit criteria, or
     has no declared value-of-information is REJECTED, not admired.
  2. VOI STOP RULE - the anti-rumination gate. Deliberation must out-earn a
     cheap probe, or the verdict is PROBE / EXECUTE, not FRAME.
  3. APPEND-ONLY LEDGER - every frame is pre-registered (id, priors, exit
     criteria, kill criteria) BEFORE the outcome is known, then resolved
     later. Pre-registration is what separates evidence from vibes.
  4. SCORING - Brier score on *frames*, skill vs the 0.25 coin-flip
     baseline, pivot rate, pending rot, and the thesis's own kill switch
     (<15% improvement over 50+ resolved frames -> abandon the pipeline).
  5. ADOPTION SCAN - recomputes the adoption metric that exposed the gap
     (protocol-artifact markers per session) so the fix is monitored, not
     assumed.

Stdlib only. ASCII output only (repo convention: no LaTeX delimiters).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = [
    "Hypothesis",
    "FrameRecord",
    "Violation",
    "ValidationResult",
    "ValidationError",
    "build_frame",
    "validate_frame",
    "compute_evi",
    "FrameLedger",
    "score_frames",
    "scan_adoption",
    "ADOPTION_MARKERS",
    "TIER_CAPS",
    "MODES",
    "main",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODES: dict[int, str] = {
    1: "EXECUTE",
    2: "CLARIFY",
    3: "CHALLENGE",
    4: "EXPERIMENT",
    5: "DECIDE",
}

# Framing budget caps (minutes) per compute tier. Source: RSN-504 timing
# heuristic, which is now ENFORCED here rather than merely narrated.
TIER_CAPS: dict[str, int] = {"SNIPER": 2, "STANDARD": 15, "ULTRA": 55}

# The pipeline's own published kill switch (problem_solving_thesis.md 6.0).
THESIS_MIN_SKILL = 0.15
THESIS_MIN_N = 50

# Self-sealing language: phrases that convert a hypothesis into something
# that cannot be falsified because counter-evidence is re-absorbed as
# confirmation. Used ONLY against the `falsifier` field. If your stated
# falsifier is one of these, you have not stated a falsifier.
#
# The list is deliberately split so that legitimate falsifiers survive:
#   * DIRECT   - sealing regardless of context
#   * INTERNAL - an internal entity (part/protector/subconscious...) attributed
#                with resistance/denial; combined with RESISTANCE below
#   * RESISTANCE / CONFIRM - only sealing when they appear together
SELF_SEALING_PATTERNS: tuple[str, ...] = (
    r"\bsubconscious\w*\b",
    r"\bunconscious\w*\b",
    r"\bnot ready to (see|admit|hear)\b",
    r"\bwouldn'?t admit\b",
    r"\bis protecting (the|a|him|her|them)\b",
    r"\bthat'?s (just )?the \w+ talking\b",
    r"\bif (he|she|they|you) (really|truly) wanted\b",
    r"\bconfirm\w* (the|my|our|your) (hypothesis|diagnosis|theory|point|frame|suspicion)\b",
    r"\bproves? (the|my|our|your) (hypothesis|diagnosis|theory|point|frame)\b",
    r"\bof course (he|she|they|you) (would|will|did)\b",
    r"\b(evidence|proof|sign)s? of (denial|resistance|avoidance)\b",
    r"\bis (denial|resistance|avoidance)\b",
)

_INTERNAL_ENTITY_RE = re.compile(
    r"\b(part|protector|manager|firefighter|exile|subconscious|unconscious|inner child|wound)\b"
)
_RESISTANCE_RE = re.compile(r"\bresist\w*|\bdenial\b|\bdenies\b|\bdenying\b|\brefus\w+ to (see|admit|acknowledge)\b|\bavoids? (the topic|acknowledging|it)\b")

# Numeric + date detection for exit criteria. A criterion without a number
# and a date is not pre-registration; it is a mood.
#
# The number check strips date-like tokens first, otherwise "2026-10-07"
# would satisfy a criterion whose threshold is pure fog ("more than before").
_DATE_TOKEN_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"|\bwithin \d+ (day|week|month)s?\b"
    r"|\bby (week|month|quarter|Q[1-4])\b"
    r"|\bdays?\b|\bweeks?\b|\bmonths?\b"
)
# The deadline requirement is stricter than the stripping pattern: a bare
# "per week" inside a threshold is not a deadline.
_DEADLINE_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"|\bwithin \d+ (day|week|month)s?\b"
    r"|\bby (end of )?(the )?(week|month|quarter|Q[1-4])\b"
    r"|\bby \d{4}-\d{2}\b"
)
_NUMBER_RE = re.compile(r"\d")
_WORD_NUMBER_RE = re.compile(
    r"\b(twice|thrice|double|triple|half)\b|\b(one|two|three|four|five|six|seven|eight|nine|ten)\b"
)
_DATE_RE = _DEADLINE_RE

# Adoption markers: the literal artifacts the protocols say they produce.
ADOPTION_MARKERS: tuple[str, ...] = (
    "Candidate Reframe",
    "Literal Request",
    "Problem Statement Lock",
    "Constraint Enumeration",
    "Kill Criteria",
    "Kill Signal",
    "Reversibility Score",
    "Reversibility scoring",
    "Graph of Thought",
    "Rival Hypothesis",
    "Discriminating Test",
    "Pre-registered",
    "frame_id",
)

CORPUS_SCAN_DIRS: tuple[str, ...] = (
    ".context/memories/session_logs",
    ".context/memories/case_studies",
    ".context/memories/insights",
)
CORPUS_SCAN_FILES: tuple[str, ...] = (
    ".context/PROJECTS.md",
    ".context/CALIBRATION_LEDGER.md",
)

DEFAULT_LEDGER = Path(".context/ledger/frames.jsonl")
DEFAULT_REPORT = Path(".context/calibration/FRAME_CALIBRATION.md")


class ValidationError(ValueError):
    """Raised when a frame record fails a BLOCK-severity contract rule."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Hypothesis:
    """One rival explanation, with a prior and a way to die."""

    id: str
    statement: str
    prior: float
    falsifier: str
    test: str = ""
    status: str = "open"  # open | supported | killed
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Violation:
    code: str
    message: str
    severity: str  # BLOCK | WARN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    frame_id: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(v.severity == "BLOCK" for v in self.violations)

    @property
    def blockers(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "BLOCK"]

    @property
    def warnings(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "WARN"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "ok": self.ok,
            "blockers": [v.to_dict() for v in self.blockers],
            "warnings": [v.to_dict() for v in self.warnings],
        }

    def to_ascii(self) -> str:
        head = (
            f"FRAME CONTRACT [{self.frame_id}]: "
            f"{'PASS' if self.ok else 'REJECTED'}"
            f"  (blockers={len(self.blockers)} warnings={len(self.warnings)})"
        )
        lines = [head, "-" * len(head)]
        for v in self.violations:
            lines.append(f"  [{v.severity:5}] {v.code}: {v.message}")
        if not self.violations:
            lines.append("  No violations. Frame may be locked.")
        return "\n".join(lines)


@dataclass
class FrameRecord:
    """A pre-registered problem frame.

    Invariant: everything needed to later judge this frame is written BEFORE
    the outcome is observed. Nothing here is allowed to be narrated.
    """

    id: str
    created: str
    literal_request: str
    candidate_reframe: str
    tier: str = "STANDARD"
    mode: int = 3
    session: str = ""
    evidence_for: str = ""
    evidence_against: str = ""
    hypotheses: list[Hypothesis] = field(default_factory=list)
    discriminating_test: str = ""
    hard_constraints: list[str] = field(default_factory=list)
    soft_constraints: list[str] = field(default_factory=list)
    soft_masquerading: str = ""
    success_criteria: list[dict[str, str]] = field(default_factory=list)
    review_date: str = ""
    kill_criteria: list[str] = field(default_factory=list)
    anti_goals: list[str] = field(default_factory=list)
    framing_budget_min: int = 0
    p_flip: float = 0.0
    delta_payoff: float = 0.0
    info_cost: float = 0.0
    cost_of_delay_per_day: float = 0.0
    baseline_counterfactual: str = ""
    origin: str = "user"  # user | audit
    surviving_branches: list[dict[str, Any]] = field(default_factory=list)
    loop_budget: dict[str, Any] = field(default_factory=dict)
    reversibility: int = 3  # 1 (irreversible) .. 5 (trivial to undo)
    ruin_receipt: str = ""
    outcome_band: dict[str, float] = field(default_factory=dict)
    status: str = "open"  # open | locked | resolved | abandoned
    resolution: dict[str, Any] = field(default_factory=dict)

    # -- serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["hypotheses"] = [h.to_dict() for h in self.hypotheses]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FrameRecord:
        payload = dict(data)
        payload["hypotheses"] = [
            h if isinstance(h, Hypothesis) else Hypothesis(**h)
            for h in payload.get("hypotheses", [])
        ]
        # `_`-prefixed keys are human metadata/comments in the seed files.
        for key in [k for k in payload if k.startswith("_")]:
            payload.pop(key)
        if "origin" not in payload:
            blob = " ".join(
                str(payload.get(k, "")) for k in ("session", "literal_request", "candidate_reframe")
            ).lower()
            payload["origin"] = "audit" if ("redteam" in blob or "red-team" in blob) else "user"
        known = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        unknown = set(payload) - known
        if unknown:
            raise ValidationError(f"unknown frame fields: {sorted(unknown)}")
        return cls(**payload)

    # -- derived -----------------------------------------------------------

    @property
    def prior_sum(self) -> float:
        return round(sum(h.prior for h in self.hypotheses), 6)

    @property
    def top_hypothesis(self) -> Hypothesis | None:
        if not self.hypotheses:
            return None
        return max(self.hypotheses, key=lambda h: h.prior)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def deterministic_frame_id(literal_request: str, session: str = "", created: str = "") -> str:
    """Stable id so re-running a frame does not create duplicates."""
    seed = "|".join([literal_request.strip().lower(), session.strip(), created.strip()])
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8].upper()
    return f"FR-{digest}"


def build_frame(payload: dict[str, Any], session: str = "") -> FrameRecord:
    """Build a FrameRecord from a JSON payload, filling derived defaults."""
    data = dict(payload)
    data.setdefault("session", session)
    data.setdefault("created", _now_iso())
    if not data.get("id"):
        data["id"] = deterministic_frame_id(
            str(data.get("literal_request", "")), str(data.get("session", "")), str(data.get("created", ""))
        )
    data.setdefault("tier", "STANDARD")
    data["tier"] = str(data["tier"]).upper()
    # Budget defaults to the tier cap, which is the most generous legal value;
    # the validator WARNs if it exceeds the cap.
    if not data.get("framing_budget_min"):
        data["framing_budget_min"] = TIER_CAPS.get(str(data["tier"]).upper(), 15)
    return FrameRecord.from_dict(data)


# ---------------------------------------------------------------------------
# Value of information (the anti-rumination stop rule)
# ---------------------------------------------------------------------------


@dataclass
class VOIResult:
    p_flip: float
    delta_payoff: float
    info_cost: float
    framing_cost: float
    gross_evi: float
    net_evi: float
    framing_evi: float
    verdict: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_ascii(self) -> str:
        return "\n".join(
            [
                "============================================================",
                "   VALUE-OF-INFORMATION STOP RULE (anti-rumination gate)    ",
                "============================================================",
                f"  P(information changes the decision)   : {self.p_flip:.2f}",
                f"  Payoff swing if it does               : {self.delta_payoff:,.2f}",
                f"  Cost of acquiring the information     : {self.info_cost:,.2f}",
                f"  Cost of the framing itself            : {self.framing_cost:,.2f}",
                "------------------------------------------------------------",
                f"  Gross expected value of information   : {self.gross_evi:,.2f}",
                f"  Net EV of information (after cost)    : {self.net_evi:,.2f}",
                f"  Net EV of framing (after delay cost)  : {self.framing_evi:,.2f}",
                f"  VERDICT                               : {self.verdict}",
                "------------------------------------------------------------",
                f"  {self.rationale}",
                "============================================================",
            ]
        )


def compute_evi(
    p_flip: float,
    delta_payoff: float,
    info_cost: float,
    framing_minutes: float = 0.0,
    cost_of_delay_per_day: float = 0.0,
    probe_available: bool = True,
) -> VOIResult:
    """Deterministic value-of-information stop rule.

    EVI = P(decision flips) x |payoff swing| - cost of the information.

    Verdicts:
      EXECUTE - the information is not worth buying; commit to the current
                best action now. (Framing further is pure rumination.)
      PROBE   - the cheap test out-earns deliberation; run the reversible
                experiment instead of spending more minutes thinking.
      FRAME   - deliberation genuinely out-earns the alternative; the
                framing budget is justified.
    """
    for name, value in (
        ("p_flip", p_flip),
        ("delta_payoff", delta_payoff),
        ("info_cost", info_cost),
        ("framing_minutes", framing_minutes),
        ("cost_of_delay_per_day", cost_of_delay_per_day),
    ):
        if value < 0:
            raise ValidationError(f"{name} must be >= 0 (got {value})")
    if p_flip > 1:
        raise ValidationError(f"p_flip must be <= 1 (got {p_flip})")

    framing_cost = (framing_minutes / (60 * 8)) * cost_of_delay_per_day  # 8h working day
    gross = p_flip * abs(delta_payoff)
    net = gross - info_cost
    framing_net = net - framing_cost

    if net <= 0:
        verdict = "EXECUTE"
        rationale = (
            "Information value does not cover its cost. Neither more analysis nor a probe is "
            "justified: act on the current best option and record the outcome."
        )
    elif framing_net <= 0 and probe_available:
        verdict = "PROBE"
        rationale = (
            "A cheap reversible probe out-earns deliberation. Replace the framing budget with "
            "the discriminating test (RSN-504 Mode 4 / RSN-505 Phase 2)."
        )
    else:
        verdict = "FRAME"
        rationale = "Deliberation out-earns the alternatives; spend the framing budget, then lock."

    return VOIResult(
        p_flip=p_flip,
        delta_payoff=delta_payoff,
        info_cost=info_cost,
        framing_cost=round(framing_cost, 4),
        gross_evi=round(gross, 4),
        net_evi=round(net, 4),
        framing_evi=round(framing_net, 4),
        verdict=verdict,
        rationale=rationale,
    )


# ---------------------------------------------------------------------------
# Contract validation (R1-R10)
# ---------------------------------------------------------------------------


def _is_self_sealing(text: str) -> str | None:
    """Return the sealing phrase if `text` cannot serve as a falsifier."""
    low = text.lower()
    for pattern in SELF_SEALING_PATTERNS:
        m = re.search(pattern, low)
        if m:
            return m.group(0)
    resistance = _RESISTANCE_RE.search(low)
    internal = _INTERNAL_ENTITY_RE.search(low)
    if resistance and internal:
        return f"{internal.group(0)} + {resistance.group(0)}"
    return None


def _criterion_is_measurable(criterion: dict[str, str]) -> bool:
    """A criterion must carry both a measurable quantity and a date/limit.

    Dates are stripped before the quantity check so a criterion whose only
    digit is its own deadline ('ship more, by 2026-10-07') fails.
    """
    blob = " ".join(str(v) for v in criterion.values())
    if not _DATE_RE.search(blob):
        return False
    prose = _DATE_TOKEN_RE.sub(" ", blob)
    return bool(_NUMBER_RE.search(prose) or _WORD_NUMBER_RE.search(prose))


def validate_frame(frame: FrameRecord) -> ValidationResult:
    """The machine-checkable frame contract.

    Every rule below exists because its absence is an observed failure mode,
    not because it is elegant. Codes map to the audit's F-findings.
    """
    v: list[Violation] = []

    # R1 - rival hypotheses with normalised priors (F-05: single-narrative lock)
    if len(frame.hypotheses) < 2:
        v.append(
            Violation(
                "R1",
                f"{len(frame.hypotheses)} hypothesis/hypotheses declared. A frame with one "
                "hypothesis is a belief, not a diagnosis. Declare >= 2 rivals.",
                "BLOCK",
            )
        )
    if frame.hypotheses and abs(frame.prior_sum - 1.0) > 0.01:
        v.append(
            Violation(
                "R1b",
                f"priors sum to {frame.prior_sum:.4f}, expected 1.0 (+/-0.01). Unnormalised priors "
                "hide the fact that the frame is a guess.",
                "BLOCK",
            )
        )
    if frame.hypotheses and any(h.prior <= 0 for h in frame.hypotheses):
        v.append(
            Violation(
                "R1c",
                "every rival must carry a non-zero prior; a rival at 0.0 is decorative and is "
                "never allowed to surprise you.",
                "BLOCK",
            )
        )

    # R2 - falsifiability, and NO self-sealing falsifiers (F-03)
    for h in frame.hypotheses:
        if not h.falsifier.strip():
            v.append(Violation("R2", f"{h.id}: no falsifier. Unfalsifiable.", "BLOCK"))
            continue
        sealed = _is_self_sealing(h.falsifier)
        if sealed:
            v.append(
                Violation(
                    "R2b",
                    f"{h.id}: falsifier contains self-sealing language ('{sealed}'). This is a "
                    "protection racket, not a falsifier: no observation can ever kill it.",
                    "BLOCK",
                )
            )
        if not h.test.strip():
            v.append(
                Violation(
                    "R2c",
                    f"{h.id}: falsifier has no test attached. Name the observation/probe that "
                    "would produce it.",
                    "WARN",
                )
            )

    # R3 - measurable, pre-registered exit criteria (F-06)
    if not frame.success_criteria:
        v.append(Violation("R3", "no success criteria declared.", "BLOCK"))
    for crit in frame.success_criteria:
        if not _criterion_is_measurable(crit):
            v.append(
                Violation(
                    "R3b",
                    f"exit criterion '{crit}' has no number and/or no date. 'Works partially' is "
                    "vibes. Specify metric + threshold + by-when.",
                    "BLOCK",
                )
            )
    if not frame.review_date.strip():
        v.append(Violation("R3c", "no review date/trigger: the frame can never be scored.", "BLOCK"))

    # R4 - kill criteria, defined before execution (F-06)
    if not frame.kill_criteria:
        v.append(Violation("R4", "no kill criteria. Without them this is a hope.", "BLOCK"))
    overlap = {x.strip().lower() for x in frame.kill_criteria} & {
        str(c.get("metric", "")).strip().lower() for c in frame.success_criteria
    }
    if overlap:
        v.append(
            Violation(
                "R4b",
                f"kill criteria reuse success metrics verbatim: {sorted(overlap)}. Restate as the "
                "abort threshold, not the goal.",
                "WARN",
            )
        )

    # R5 - framing budget enforced against the tier cap (F-04: the 11:1 ratio was narrated)
    cap = TIER_CAPS.get(frame.tier, 15)
    if frame.framing_budget_min > cap:
        v.append(
            Violation(
                "R5",
                f"framing budget {frame.framing_budget_min} min exceeds the {frame.tier} cap of "
                f"{cap} min. Budgets are caps, not aspirations.",
                "BLOCK",
            )
        )
    if frame.framing_budget_min <= 0:
        v.append(Violation("R5b", "no framing budget declared.", "WARN"))

    # R6 - the VOI stop rule (F-02: 55 minutes was unconditional)
    voi = compute_evi(
        frame.p_flip,
        frame.delta_payoff,
        frame.info_cost,
        frame.framing_budget_min,
        frame.cost_of_delay_per_day,
    )
    if voi.verdict != "FRAME":
        v.append(
            Violation(
                "R6",
                f"VOI stop rule says {voi.verdict}, not FRAME (net EV of information = "
                f"{voi.net_evi:,.2f}). Framing more is negative-expected-value here.",
                "BLOCK",
            )
        )

    # R7 - mode integrity (F-07: modes were labels with no obligations)
    if frame.mode not in MODES:
        v.append(Violation("R7", f"unknown mode {frame.mode}; expected one of {sorted(MODES)}.", "BLOCK"))
    if frame.mode == 3 and not (frame.evidence_for.strip() and frame.evidence_against.strip()):
        v.append(
            Violation(
                "R7b",
                "Mode 3 (CHALLENGE) requires BOTH evidence_for and evidence_against. A reframe "
                "with only supporting evidence is advocacy.",
                "BLOCK",
            )
        )
    if frame.mode == 4 and not frame.discriminating_test.strip():
        v.append(Violation("R7c", "Mode 4 (EXPERIMENT) requires a discriminating_test.", "BLOCK"))

    # R8 - baseline counterfactual (F-09: no control group, so no validation)
    if not frame.baseline_counterfactual.strip():
        v.append(
            Violation(
                "R8",
                "no baseline_counterfactual. Without a declared 'what would the default answer "
                "have been', the frame can never be shown to beat anything.",
                "BLOCK",
            )
        )

    # R9 - constraint hygiene: hard vs soft, and the masquerade field (F-08)
    if frame.hard_constraints and not frame.soft_constraints and not frame.soft_masquerading.strip():
        v.append(
            Violation(
                "R9",
                "hard constraints listed but no soft constraints and no masquerade field. The "
                "highest-leverage lever class was never examined.",
                "WARN",
            )
        )

    # R10 - discriminating test at frame level
    if not frame.discriminating_test.strip():
        v.append(
            Violation(
                "R10",
                "no frame-level discriminating test: nothing here separates the candidate reframe "
                "from the literal request.",
                "BLOCK",
            )
        )

    # R11 - loop budget present for Loop 2 iteration discipline (2026-10-17 Plan T3.1 / A3)
    lb = frame.loop_budget if isinstance(frame.loop_budget, dict) else {}
    has_cap = float(lb.get("max_rounds", 0) or 0) > 0 or float(lb.get("max_hours", 0) or 0) > 0
    has_signal = bool(str(lb.get("success_signal", "")).strip())
    if not (has_cap and has_signal):
        v.append(
            Violation(
                "R11",
                "no valid loop_budget (requires max_rounds or max_hours > 0 plus non-empty "
                "success_signal). Loop 2 cannot start without an iteration budget.",
                "BLOCK",
            )
        )

    # R12 - at least 2 surviving branches including 1 contingency with revive_trigger (T3.1 / A4)
    branches = frame.surviving_branches if isinstance(frame.surviving_branches, list) else []
    has_contingency = any(
        isinstance(b, dict)
        and bool(b.get("contingency"))
        and bool(str(b.get("revive_trigger", "")).strip())
        for b in branches
    )
    if len(branches) < 2 or not has_contingency:
        v.append(
            Violation(
                "R12",
                "surviving_branches must declare >= 2 branches including >= 1 contingency branch "
                "with a non-empty revive_trigger (RSN-505:85 / RSN-506:76).",
                "BLOCK",
            )
        )

    # R13 - reversibility 1-5; score <= 2 requires verified GTO receipt ID or [agent-estimate] (T3.1 / A1)
    rev = int(frame.reversibility) if isinstance(frame.reversibility, int) else 0
    if not (1 <= rev <= 5):
        v.append(
            Violation(
                "R13",
                f"reversibility must be between 1 and 5 (got {frame.reversibility}).",
                "BLOCK",
            )
        )
    elif rev <= 2:
        rec_str = frame.ruin_receipt.strip()
        is_agent_est = (
            "[agent-estimate]" in rec_str.lower()
            and len(rec_str.lower().replace("[agent-estimate]", "").strip()) >= 5
        )
        is_verified_receipt = False
        if rec_str and not is_agent_est:
            from athena.intelligence.gto_engine import get_receipts_path

            rpath = get_receipts_path()
            if rpath.exists():
                for rline in rpath.read_text(encoding="utf-8").splitlines():
                    rline = rline.strip()
                    if not rline:
                        continue
                    try:
                        robj = json.loads(rline)
                        if robj.get("receipt_id") == rec_str:
                            is_verified_receipt = True
                            break
                    except json.JSONDecodeError:
                        continue
        if not (is_agent_est or is_verified_receipt):
            v.append(
                Violation(
                    "R13",
                    f"reversibility={rev} (<=2) requires a verified receipt_id in "
                    f"decision_receipts.jsonl or '[agent-estimate] <basis>' (got '{rec_str}').",
                    "BLOCK",
                )
            )

    return ValidationResult(frame_id=frame.id, violations=v)


def assert_valid(frame: FrameRecord) -> ValidationResult:
    """Validate and raise on any BLOCK violation."""
    result = validate_frame(frame)
    if not result.ok:
        raise ValidationError(result.to_ascii())
    return result


# ---------------------------------------------------------------------------
# Ledger (append-only, event-sourced)
# ---------------------------------------------------------------------------


class FrameLedger:
    """Append-only JSONL ledger of frame events.

    Events:
      {"kind": "frame",      "ts": ..., "frame": {...}}
      {"kind": "resolution", "ts": ..., "id": ..., "resolution": {...}}
      {"kind": "pivot",      "ts": ..., "id": ..., "reason": ...}

    Append-only matters: the pre-registration must be immutable after the
    fact. Resolution is a *new event*, never an edit.
    """

    def __init__(self, path: Path | str = DEFAULT_LEDGER):
        self.path = Path(path)

    # -- io ---------------------------------------------------------------

    def events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def _append(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event.setdefault("ts", _now_iso())
        line = json.dumps(event, ensure_ascii=True, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    # -- queries ----------------------------------------------------------

    def frames(self) -> list[FrameRecord]:
        records: dict[str, FrameRecord] = {}
        for ev in self.events():
            if ev.get("kind") == "frame" and isinstance(ev.get("frame"), dict):
                rec = FrameRecord.from_dict(ev["frame"])
                records[rec.id] = rec
        for ev in self.events():
            if ev.get("kind") == "resolution" and ev.get("id") in records:
                rec = records[ev["id"]]
                rec.resolution = ev.get("resolution", {})
                rec.status = "resolved"
        return sorted(records.values(), key=lambda r: r.created)

    def get(self, frame_id: str) -> FrameRecord | None:
        for rec in self.frames():
            if rec.id == frame_id:
                return rec
        return None

    # -- mutations --------------------------------------------------------

    def open(self, frame: FrameRecord, *, lock: bool = False) -> ValidationResult:
        """Register a frame. Validates first; only BLOCK-clean frames are stored."""
        result = validate_frame(frame)
        if not result.ok:
            return result
        if self.get(frame.id) is not None:
            raise ValidationError(f"frame {frame.id} already registered (append-only ledger)")
        if lock:
            frame.status = "locked"
        self._append({"kind": "frame", "frame": frame.to_dict()})
        return result

    def lock(self, frame_id: str) -> FrameRecord:
        rec = self.get(frame_id)
        if rec is None:
            raise ValidationError(f"unknown frame {frame_id}")
        result = validate_frame(rec)
        if not result.ok:
            raise ValidationError(result.to_ascii())
        rec.status = "locked"
        self._append({"kind": "frame", "frame": rec.to_dict()})
        return rec

    def pivot(self, frame_id: str, reason: str) -> None:
        if self.get(frame_id) is None:
            raise ValidationError(f"unknown frame {frame_id}")
        self._append({"kind": "pivot", "id": frame_id, "reason": reason})

    def resolve(
        self,
        frame_id: str,
        supported: Iterable[str],
        *,
        killed: Iterable[str] = (),
        regret: float | None = None,
        note: str = "",
        decided_action: str = "",
        classification: str = "",
        observed_value: float | None = None,
    ) -> dict[str, Any]:
        """Record the observed outcome. Never edits the original frame."""
        rec = self.get(frame_id)
        if rec is None:
            raise ValidationError(f"unknown frame {frame_id}")
        supported_set = {s.strip() for s in supported}
        killed_set = {k.strip() for k in killed}
        known = {h.id for h in rec.hypotheses}
        unknown = (supported_set | killed_set) - known
        if unknown:
            raise ValidationError(f"unknown hypothesis ids: {sorted(unknown)}")
        if not supported_set and not killed_set:
            raise ValidationError("resolution must mark at least one hypothesis supported or killed")

        norm_class = classification.strip().upper() if classification else ""
        if norm_class == "LUCK":
            band = rec.outcome_band if isinstance(rec.outcome_band, dict) else {}
            if "min" not in band or "max" not in band or observed_value is None:
                raise ValidationError(
                    "LUCK classification rejected: requires a pre-registered outcome_band "
                    "{'min', 'max'} on the frame and an observed_value at resolution (T3.2 / A7)."
                )
            lo, hi = float(band["min"]), float(band["max"])
            if not (lo <= float(observed_value) <= hi):
                raise ValidationError(
                    f"LUCK classification rejected: observed_value {observed_value} is outside "
                    f"pre-registered outcome_band [{lo}, {hi}]. Default to PROCESS or INFORMATION."
                )

        scored: dict[str, int] = {}
        for h in rec.hypotheses:
            if h.id in supported_set:
                scored[h.id] = 1
            elif h.id in killed_set:
                scored[h.id] = 0
        brier = sum((h.prior - scored[h.id]) ** 2 for h in rec.hypotheses if h.id in scored) / max(
            len(scored), 1
        )
        top = rec.top_hypothesis
        resolution = {
            "resolved_at": _now_iso(),
            "review_date_planned": rec.review_date,
            "supported": sorted(supported_set),
            "killed": sorted(killed_set),
            "scored": scored,
            "brier": round(brier, 4),
            "top_hypothesis": top.id if top else None,
            "frame_hit": bool(top and top.id in supported_set),
            "regret": regret,
            "note": note,
            "decided_action": decided_action,
            "classification": norm_class,
            "observed_value": observed_value,
        }
        self._append({"kind": "resolution", "id": frame_id, "resolution": resolution})
        return resolution


# ---------------------------------------------------------------------------
# Scoring and calibration
# ---------------------------------------------------------------------------


def score_frames(frames: list[FrameRecord]) -> dict[str, Any]:
    """Aggregate the frame-quality metrics that the pipeline previously lacked."""
    resolved = [f for f in frames if f.resolution]
    opened = len(frames)
    user_opened = sum(1 for f in frames if f.origin == "user")
    audit_opened = sum(1 for f in frames if f.origin != "user")
    briers = [f.resolution["brier"] for f in resolved if "brier" in f.resolution]
    hits = [bool(f.resolution.get("frame_hit")) for f in resolved]

    brier = round(statistics.fmean(briers), 4) if briers else None
    skill = round(1 - (brier / 0.25), 4) if brier is not None else None

    mode_counts: dict[str, int] = {}
    tier_counts: dict[str, int] = {}
    for f in frames:
        mode_counts[MODES.get(f.mode, str(f.mode))] = mode_counts.get(MODES.get(f.mode, str(f.mode)), 0) + 1
        tier_counts[f.tier] = tier_counts.get(f.tier, 0) + 1

    regret_values = [
        float(f.resolution["regret"]) for f in resolved if f.resolution.get("regret") is not None
    ]

    kill_switch: str
    if len(resolved) < THESIS_MIN_N:
        kill_switch = (
            f"INSUFFICIENT DATA ({len(resolved)}/{THESIS_MIN_N} resolved frames; "
            f"user_frames_opened={user_opened}, audit_frames_opened={audit_opened}). "
            "The thesis's own kill switch cannot be evaluated yet - keep collecting, do not claim efficacy."
        )
    elif skill is not None and skill < THESIS_MIN_SKILL:
        kill_switch = (
            f"KILL SWITCH FIRED: skill {skill:.2%} < {THESIS_MIN_SKILL:.0%} over {len(resolved)} "
            "resolved frames. Per problem_solving_thesis.md 6.0, abandon the heavy pipeline and "
            "revert to light diagnostics."
        )
    else:
        kill_switch = f"PAST KILL SWITCH (skill {skill:.2%} over {len(resolved)} resolved frames)."

    return {
        "frames_opened": opened,
        "user_frames_opened": user_opened,
        "audit_frames_opened": audit_opened,
        "frames_resolved": len(resolved),
        "pending_rot": opened - len(resolved),
        "frame_hit_rate": round(sum(hits) / len(hits), 4) if hits else None,
        "mean_brier": brier,
        "baseline_brier": 0.25,
        "skill_vs_coinflip": skill,
        "mean_regret": round(statistics.fmean(regret_values), 3) if regret_values else None,
        "mode_distribution": dict(sorted(mode_counts.items())),
        "tier_distribution": dict(sorted(tier_counts.items())),
        "kill_switch_status": kill_switch,
    }


# ---------------------------------------------------------------------------
# Adoption scan (operationalises the audit's F-01 finding)
# ---------------------------------------------------------------------------


def scan_adoption(
    root: Path | str = ".",
    dirs: Iterable[str] = CORPUS_SCAN_DIRS,
    files: Iterable[str] = CORPUS_SCAN_FILES,
) -> dict[str, Any]:
    """Count protocol-artifact markers across the memory corpus.

    This is the metric that exposed the gap: the pipeline's named artifacts
    must actually appear in the record. A protocol that is never written
    down never happened.
    """
    root = Path(root)
    corpus: list[Path] = []
    for d in dirs:
        base = root / d
        if base.is_dir():
            corpus.extend(sorted(base.rglob("*.md")))
    for f in files:
        p = root / f
        if p.is_file():
            corpus.append(p)

    marker_hits: dict[str, int] = dict.fromkeys(ADOPTION_MARKERS, 0)
    files_with_any = 0
    for path in corpus:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        hit_any = False
        for marker in ADOPTION_MARKERS:
            count = text.lower().count(marker.lower())
            if count:
                marker_hits[marker] += count
                hit_any = True
        files_with_any += int(hit_any)

    total_markers = sum(marker_hits.values())
    sessions = sum(1 for p in corpus if "session_logs" in p.as_posix())
    per_100 = round(100 * total_markers / sessions, 3) if sessions else 0.0

    return {
        "corpus_files": len(corpus),
        "session_files": sessions,
        "files_with_any_marker": files_with_any,
        "file_adoption_ratio": round(files_with_any / len(corpus), 4) if corpus else 0.0,
        "total_marker_hits": total_markers,
        "markers_per_100_sessions": per_100,
        "cold_markers": sorted([m for m, n in marker_hits.items() if n == 0]),
        "marker_hits": dict(sorted(marker_hits.items(), key=lambda kv: -kv[1])),
    }


def adoption_to_ascii(scan: dict[str, Any]) -> str:
    lines = [
        "============================================================",
        "        PROTOCOL ADOPTION SCAN (Cluster #15 artifacts)       ",
        "============================================================",
        f"  Corpus files scanned              : {scan['corpus_files']}",
        f"  Session logs scanned              : {scan['session_files']}",
        f"  Files containing ANY frame marker : {scan['files_with_any_marker']} "
        f"({scan['file_adoption_ratio']:.2%})",
        f"  Total marker hits                 : {scan['total_marker_hits']}",
        f"  Markers per 100 sessions          : {scan['markers_per_100_sessions']}",
        "------------------------------------------------------------",
        "  Marker counts (top):",
    ]
    for marker, count in list(scan["marker_hits"].items())[:8]:
        lines.append(f"    {count:>6}  {marker}")
    cold = scan["cold_markers"]
    lines.append(f"  Cold markers (0 hits): {len(cold)} -> {', '.join(cold[:8])}")
    lines.append("============================================================")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def calibration_report(ledger: FrameLedger, *, adoption_root: Path | str = ".") -> str:
    frames = ledger.frames()
    stats = score_frames(frames)
    adoption = scan_adoption(adoption_root)

    lines = [
        "# Frame Calibration Ledger (generated)",
        "",
        f"> Generated: {_now_iso()}  |  Source: `{ledger.path}`",
        "> Regenerate: `python3 -m athena.intelligence.frame_ledger report --write`",
        "",
        "## Frame Quality (the previously missing measurement)",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| Frames opened | {stats['frames_opened']} |",
        f"| Frames resolved | {stats['frames_resolved']} |",
        f"| Pending rot (opened - resolved) | {stats['pending_rot']} |",
        f"| Frame hit rate (top hypothesis survived) | {stats['frame_hit_rate']} |",
        f"| Mean Brier (frames) | {stats['mean_brier']} |",
        f"| Coin-flip baseline Brier | {stats['baseline_brier']} |",
        f"| Skill vs coin flip | {stats['skill_vs_coinflip']} |",
        f"| Mean self-reported regret (0-10) | {stats['mean_regret']} |",
        f"| Mode distribution | {stats['mode_distribution']} |",
        f"| Tier distribution | {stats['tier_distribution']} |",
        "",
        f"**Kill switch status**: {stats['kill_switch_status']}",
        "",
        "## Protocol Adoption (does the pipeline actually execute?)",
        "",
        f"- Corpus files: {adoption['corpus_files']}",
        f"- Files containing any Cluster #15 artifact marker: "
        f"{adoption['files_with_any_marker']} ({adoption['file_adoption_ratio']:.2%})",
        f"- Markers per 100 session logs: {adoption['markers_per_100_sessions']}",
        f"- Cold markers (zero occurrences): {', '.join(adoption['cold_markers']) or 'none'}",
        "",
        "## Open Frames",
        "",
        "| Frame | Tier | Mode | Literal request | Top hypothesis | Review date |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for f in frames:
        if f.status == "resolved":
            continue
        top = f.top_hypothesis
        lines.append(
            f"| `{f.id}` | {f.tier} | {MODES.get(f.mode, f.mode)} | "
            f"{f.literal_request[:60]} | {top.id if top else '-'} | {f.review_date} |"
        )
    if stats["frames_opened"] == 0:
        lines.append("| - | - | - | (no frames registered yet) | - | - |")

    lines += [
        "",
        "## Resolved Frames",
        "",
        "| Frame | Brier | Hit | Supported | Regret | Note |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for f in frames:
        if f.status != "resolved":
            continue
        r = f.resolution
        lines.append(
            f"| `{f.id}` | {r.get('brier')} | {r.get('frame_hit')} | "
            f"{', '.join(r.get('supported', []))} | {r.get('regret')} | {str(r.get('note', ''))[:50]} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_payload(path: str) -> dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cmd_open(args: argparse.Namespace) -> int:
    ledger = FrameLedger(args.ledger)
    payload = _load_payload(args.from_json)
    frame = build_frame(payload, session=args.session)
    result = ledger.open(frame, lock=args.lock)
    print(result.to_ascii())
    if result.ok:
        print(f"\nRegistered {frame.id} -> {ledger.path}")
        return 0
    return 2


def _cmd_validate(args: argparse.Namespace) -> int:
    ledger = FrameLedger(args.ledger)
    if args.id:
        frame = ledger.get(args.id)
        if frame is None:
            print(f"unknown frame {args.id}", file=sys.stderr)
            return 3
    else:
        frame = build_frame(_load_payload(args.from_json), session=args.session)
    result = validate_frame(frame)
    print(result.to_ascii())
    voi = compute_evi(
        frame.p_flip,
        frame.delta_payoff,
        frame.info_cost,
        frame.framing_budget_min,
        frame.cost_of_delay_per_day,
    )
    print()
    print(voi.to_ascii())
    return 0 if result.ok else 2


def _cmd_resolve(args: argparse.Namespace) -> int:
    ledger = FrameLedger(args.ledger)
    resolution = ledger.resolve(
        args.id,
        supported=args.supported.split(",") if args.supported else [],
        killed=args.killed.split(",") if args.killed else [],
        regret=args.regret,
        note=args.note,
        decided_action=args.action,
    )
    print(json.dumps(resolution, indent=2, sort_keys=True))
    return 0


def _cmd_pivot(args: argparse.Namespace) -> int:
    ledger = FrameLedger(args.ledger)
    ledger.pivot(args.id, args.reason)
    print(f"pivot recorded for {args.id}")
    return 0


def _cmd_calibrate(args: argparse.Namespace) -> int:
    stats = score_frames(FrameLedger(args.ledger).frames())
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


def _cmd_adoption(args: argparse.Namespace) -> int:
    scan = scan_adoption(args.root)
    if args.json:
        print(json.dumps(scan, indent=2, sort_keys=True))
    else:
        print(adoption_to_ascii(scan))
    if args.ratchet is not None and scan["markers_per_100_sessions"] < args.ratchet:
        print(
            f"\nRATCHET FAIL: {scan['markers_per_100_sessions']} < required {args.ratchet} "
            "markers per 100 sessions.",
            file=sys.stderr,
        )
        return 2
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    ledger = FrameLedger(args.ledger)
    text = calibration_report(ledger, adoption_root=args.root)
    if args.write:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, target)
        print(f"wrote {target}")
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="frame_ledger",
        description="Pre-register, validate, and score problem frames (Cluster #15 enforcement).",
    )
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="path to the JSONL ledger")
    sub = parser.add_subparsers(dest="command", required=True)

    p_open = sub.add_parser("open", help="validate and register a new frame")
    p_open.add_argument("--from-json", required=True, help="frame JSON file ('-' for stdin)")
    p_open.add_argument("--session", default="")
    p_open.add_argument("--lock", action="store_true", help="mark locked on insert")
    p_open.set_defaults(func=_cmd_open)

    p_val = sub.add_parser("validate", help="run the R1-R10 contract + VOI stop rule")
    p_val.add_argument("--id")
    p_val.add_argument("--from-json")
    p_val.add_argument("--session", default="")
    p_val.set_defaults(func=_cmd_validate)

    p_res = sub.add_parser("resolve", help="record the observed outcome")
    p_res.add_argument("--id", required=True)
    p_res.add_argument("--supported", default="", help="comma-separated hypothesis ids")
    p_res.add_argument("--killed", default="", help="comma-separated hypothesis ids")
    p_res.add_argument("--regret", type=float, default=None)
    p_res.add_argument("--note", default="")
    p_res.add_argument("--action", default="")
    p_res.set_defaults(func=_cmd_resolve)

    p_piv = sub.add_parser("pivot", help="record a frame-level pivot (diagnosis was wrong)")
    p_piv.add_argument("--id", required=True)
    p_piv.add_argument("--reason", required=True)
    p_piv.set_defaults(func=_cmd_pivot)

    p_cal = sub.add_parser("calibrate", help="Brier / hit rate / kill-switch status")
    p_cal.set_defaults(func=_cmd_calibrate)

    p_adopt = sub.add_parser("adoption", help="scan the corpus for Cluster #15 artifacts")
    p_adopt.add_argument("--root", default=".")
    p_adopt.add_argument("--json", action="store_true")
    p_adopt.add_argument("--ratchet", type=float, default=None, help="fail if below this floor")
    p_adopt.set_defaults(func=_cmd_adoption)

    p_rep = sub.add_parser("report", help="generate the frame calibration report")
    p_rep.add_argument("--write", action="store_true")
    p_rep.add_argument("--out", default=str(DEFAULT_REPORT))
    p_rep.add_argument("--root", default=".")
    p_rep.set_defaults(func=_cmd_report)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
