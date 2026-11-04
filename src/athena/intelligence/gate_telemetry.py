"""
athena.intelligence.gate_telemetry
==================================

Telemetry analysis and fire-rate monitoring engine for Meta-Awareness & Governance Gates (TD-069b M2).
Parses the runtime telemetry stream (.athena/invocations.jsonl) to monitor:
1. Aggregate prompt throughput vs. gate intervention frequency (Fire-Rate).
2. Per-class structural distribution (T1-INBOUND through T5-FELT).
3. Compliance band bounds:
   - LOW (< 10%): Gate is under-firing; risk of un-intercepted left-tail assumptions.
   - NORMAL (10% - 30%): Calibrated baseline per hook_meta_awareness_gate contract.
   - SATURATED (> 30%): Gate is over-firing; causes operator warning fatigue.

Zero-delimiters: strictly plain ASCII output.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass
class TelemetrySummary:
    window_days: int
    total_prompts: int
    total_fires: int
    fire_rate_pct: float
    compliance_band: str
    class_counts: dict[str, int] = field(default_factory=dict)
    class_shares: dict[str, float] = field(default_factory=dict)


@dataclass
class OutputContractAudit:
    contract_satisfied: bool
    adherence_score: float
    elements_present: list[str]
    missing_elements: list[str]
    verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_satisfied": self.contract_satisfied,
            "adherence_score": self.adherence_score,
            "elements_present": self.elements_present,
            "missing_elements": self.missing_elements,
            "verdict": self.verdict,
        }


SUBSTANCE_DECODE_PILLARS = [
    (
        "prior",
        r"\b(?:prior|base\s+rate|arena\s+base\s+rate|arena\s+prior|historical\s+base\s+rate)\b",
        "Base-Rate Prior (Arena Base Rate)",
    ),
    (
        "discriminators",
        r"\b(?:discriminator(?:s)?|verifiable\s+detail(?:s)?|observable\s+update(?:s)?|observable\s+discriminator(?:s)?|signals?\s+observed)\b",
        "Observable Discriminators",
    ),
    (
        "sign_check",
        r"\b(?:sign\s+check|mp-?16|inflating|deflating|flip\s+the\s+sign)\b",
        "Sign Check (MP-16 Inflating/Deflating Audit)",
    ),
    (
        "payoff_action",
        r"\b(?:payoff-?weighted|payoff\s+valuation|asymmetric\s+upside|ergodic(?:ity)?|ev\s*=|asymmetry)\b",
        "Payoff-Weighted Action / Asymmetry",
    ),
]


def evaluate_substance_decode_adherence(text: str) -> dict[str, Any]:
    """
    Evaluates whether model output satisfies the substance-decode output contract (TD-069b M3).
    Checks for the 4 core pillars:
      1. Base-Rate Prior
      2. Observable Discriminators
      3. Sign Check (MP-16)
      4. Payoff-Weighted Action
    """
    if not text:
        return OutputContractAudit(
            contract_satisfied=False,
            adherence_score=0.0,
            elements_present=[],
            missing_elements=[p[0] for p in SUBSTANCE_DECODE_PILLARS],
            verdict="FAIL",
        ).to_dict()

    present: list[str] = []
    missing: list[str] = []

    for name, pattern, _ in SUBSTANCE_DECODE_PILLARS:
        if re.search(pattern, text, re.IGNORECASE):
            present.append(name)
        else:
            missing.append(name)

    score = len(present) / len(SUBSTANCE_DECODE_PILLARS)
    satisfied = score >= 0.75  # Requires at least 3 of 4 pillars

    if satisfied:
        verdict = "PASS"
    elif score >= 0.5:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    return OutputContractAudit(
        contract_satisfied=satisfied,
        adherence_score=round(score, 2),
        elements_present=present,
        missing_elements=missing,
        verdict=verdict,
    ).to_dict()


class GateTelemetryAnalyzer:
    """
    Parses and aggregates runtime gate invocation records from invocations.jsonl.
    """

    def __init__(self, telemetry_path: Path | str | None = None):
        if telemetry_path is None:
            self.telemetry_path = Path.cwd() / ".athena" / "invocations.jsonl"
        else:
            self.telemetry_path = Path(telemetry_path).resolve()

    def _parse_ts(self, ts_raw: str | None) -> datetime | None:
        if not ts_raw:
            return None
        try:
            # Handle ISO formats
            cleaned = ts_raw.replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    def analyze(self, window_days: int = 7) -> TelemetrySummary:
        """
        Calculates windowed fire-rate metrics and per-class distributions.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=window_days)

        total_prompts = 0
        total_fires = 0
        class_counter: Counter[str] = Counter()

        if self.telemetry_path.exists():
            try:
                with open(self.telemetry_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                        except Exception:
                            continue

                        ts = self._parse_ts(record.get("ts") or record.get("timestamp"))
                        if ts is not None and ts < cutoff:
                            continue

                        rec_type = record.get("type")
                        trigger = record.get("trigger")
                        name = record.get("name")

                        # Prompt counting (Claude Code UserPromptSubmit or AgentGate prompt hooks)
                        if (rec_type == "prompt" or trigger == "UserPromptSubmit") and rec_type != "hook":
                            total_prompts += 1

                        # Gate fire counting
                        if rec_type == "hook" and name == "meta_awareness_gate":
                            total_fires += 1
                            classes = record.get("classes") or []
                            for c in classes:
                                class_counter[c] += 1
            except Exception:
                pass

        # Calculate rate and band
        if total_prompts > 0:
            rate = (total_fires / total_prompts) * 100.0
        else:
            rate = 0.0

        if rate < 10.0:
            band = "LOW (<10%)"
        elif rate <= 30.0:
            band = "NORMAL (10-30%)"
        else:
            band = "SATURATED (>30%)"

        class_counts = dict(class_counter)
        class_shares = {
            cls: (count / total_fires * 100.0) if total_fires > 0 else 0.0
            for cls, count in class_counts.items()
        }

        return TelemetrySummary(
            window_days=window_days,
            total_prompts=total_prompts,
            total_fires=total_fires,
            fire_rate_pct=round(rate, 2),
            compliance_band=band,
            class_counts=class_counts,
            class_shares={k: round(v, 2) for k, v in class_shares.items()},
        )

    def render_ascii_report(self, window_days: int = 7) -> str:
        """
        Renders a human-readable plain ASCII telemetry summary report.
        """
        summary = self.analyze(window_days=window_days)
        lines = [
            f"=== Meta-Awareness Gate Telemetry ({summary.window_days}d Window) ===",
            f"Prompts: {summary.total_prompts} | Fires: {summary.total_fires} | Fire-Rate: {summary.fire_rate_pct}%",
            f"Band: {summary.compliance_band}",
            "",
            "--- Class Breakdown ---",
        ]

        if not summary.class_counts:
            lines.append("  (Zero gate fires recorded in window)")
        else:
            for cls in sorted(summary.class_counts.keys()):
                count = summary.class_counts[cls]
                share = summary.class_shares.get(cls, 0.0)
                lines.append(f"  {cls:<15}: {count:>4} fires ({share:>5.1f}%)")

        return "\n".join(lines)

    def audit_output_contract(self, text: str) -> OutputContractAudit:
        """
        Audits output text against substance-decode contract (TD-069b M3).
        """
        d = evaluate_substance_decode_adherence(text)
        return OutputContractAudit(
            contract_satisfied=d["contract_satisfied"],
            adherence_score=d["adherence_score"],
            elements_present=d["elements_present"],
            missing_elements=d["missing_elements"],
            verdict=d["verdict"],
        )

    def render_contract_report(self, text: str) -> str:
        """
        Renders an ASCII verification report for output contract adherence.
        """
        audit = self.audit_output_contract(text)
        lines = [
            "=== Substance-Decode Output Contract Audit (TD-069b M3) ===",
            f"Verdict:            {audit.verdict}",
            f"Contract Satisfied: {audit.contract_satisfied}",
            f"Adherence Score:    {int(audit.adherence_score * 100)}% ({len(audit.elements_present)}/4 pillars)",
            f"Pillars Present:    {', '.join(audit.elements_present) if audit.elements_present else 'None'}",
            f"Pillars Missing:    {', '.join(audit.missing_elements) if audit.missing_elements else 'None'}",
        ]
        return "\n".join(lines)
