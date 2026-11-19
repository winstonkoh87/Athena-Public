"""
athena.intelligence.calibration
===============================

Pre-registered prediction calibration engine (Brier score, log-loss, buckets,
domain breakdown, overdue detection, and pre-registration integrity audit).

Stdlib only. ASCII output only (no LaTeX delimiters).
"""

from __future__ import annotations

import math
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from athena.core.config import PROJECT_ROOT

__all__ = [
    "get_calibration_ledger_path",
    "parse_ledger",
    "validate_pre_registration",
    "compute_scores",
    "domain_breakdown",
    "get_calibration_status",
    "format_calibration_report",
]


def get_calibration_ledger_path() -> Path:
    """Resolve CALIBRATION_LEDGER.md via env overrides, ATHENA_ROOT, or PROJECT_ROOT."""
    env_cal = os.environ.get("ATHENA_CAL_LEDGER_PATH")
    if env_cal:
        return Path(env_cal).resolve()
    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        return Path(env_root).resolve() / ".context" / "calibration" / "CALIBRATION_LEDGER.md"
    return PROJECT_ROOT / ".context" / "calibration" / "CALIBRATION_LEDGER.md"


def parse_ledger(path: Path) -> list[dict[str, Any]]:
    """Parse all ### CAL-XXX prediction blocks from a calibration ledger markdown file."""
    content = path.read_text(encoding="utf-8")
    predictions: list[dict[str, Any]] = []

    blocks = re.split(r"### (CAL-\d+)", content)
    patterns = {
        "claim": r"\*\*Claim\*\*:\s*(.+)",
        "probability": r"\*\*Probability\*\*:\s*([\d.]+)",
        "deadline": r"\*\*Deadline\*\*:\s*(.+)",
        "domain": r"\*\*Domain\*\*:\s*(.+)",
        "rationale": r"\*\*Rationale\*\*:\s*(.+)",
        "outcome": r"\*\*Outcome\*\*:\s*(.+)",
        "resolved_date": r"\*\*Resolved\*\*:\s*(.+)",
        "source_session": r"\*\*Source\*\*:\s*(.+)",
    }

    for i in range(1, len(blocks), 2):
        cal_id = blocks[i]
        body = blocks[i + 1]
        pred: dict[str, Any] = {"id": cal_id}

        for key, pattern in patterns.items():
            match = re.search(pattern, body)
            if match:
                pred[key] = match.group(1).strip()

        if "probability" in pred:
            try:
                pred["probability"] = float(pred["probability"])
            except ValueError:
                pred["probability"] = 0.5
        else:
            pred["probability"] = 0.5

        predictions.append(pred)

    return predictions


def validate_pre_registration(
    predictions: list[dict[str, Any]],
    session_log_dir: Path | None = None,
) -> list[str]:
    """Validate pre-registration integrity: predictions must be logged before resolution."""
    log_dir = session_log_dir or (PROJECT_ROOT / ".context" / "memories" / "session_logs")
    warnings: list[str] = []

    for p in predictions:
        outcome = str(p.get("outcome", "")).lower()
        if outcome not in ("true", "false", "partial"):
            continue

        cal_id = str(p["id"])
        source = str(p.get("source_session", ""))
        resolved_raw = str(p.get("resolved_date", ""))

        resolved_date = None
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", resolved_raw)
        if date_match:
            try:
                resolved_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            except ValueError:
                pass

        if not source:
            warnings.append(
                f"  [WARN] {cal_id}: No source_session -- cannot verify pre-registration."
            )
            continue

        session_match = re.search(r"S(\d+)", source)
        source_date = None

        if session_match:
            session_num = session_match.group(1)
            if log_dir.exists():
                for log_file in log_dir.glob(f"*session-*{session_num}.md"):
                    fname_date = re.search(r"(\d{4}-\d{2}-\d{2})", log_file.name)
                    if fname_date:
                        try:
                            source_date = datetime.strptime(fname_date.group(1), "%Y-%m-%d")
                        except ValueError:
                            pass
                        break
        else:
            source_date_match = re.search(r"(\d{4}-\d{2}-\d{2})", source)
            if source_date_match:
                try:
                    source_date = datetime.strptime(source_date_match.group(1), "%Y-%m-%d")
                except ValueError:
                    pass

        if source_date and resolved_date:
            if source_date > resolved_date:
                warnings.append(
                    f"  [FAIL] {cal_id}: PRE-REGISTRATION VIOLATION -- source date "
                    f"{source_date.strftime('%Y-%m-%d')} is AFTER resolution date "
                    f"{resolved_date.strftime('%Y-%m-%d')}. Prediction may be retroactive."
                )
            elif source_date == resolved_date:
                warnings.append(
                    f"  [WARN] {cal_id}: Same-day source and resolution -- "
                    f"pre-registration integrity ambiguous."
                )
        elif not source_date and resolved_date:
            warnings.append(
                f"  [INFO] {cal_id}: Source '{source}' -- session log not found, "
                f"pre-registration not mechanically verified."
            )

    return warnings


def compute_scores(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Brier score, log-loss, and 0.1-wide calibration buckets."""
    resolved = [
        p for p in predictions
        if str(p.get("outcome", "")).lower() in ("true", "false", "partial")
    ]
    pending_n = len([p for p in predictions if str(p.get("outcome", "")).lower() == "pending"])
    voided_n = len([p for p in predictions if str(p.get("outcome", "")).lower() == "void"])

    if not resolved:
        return {
            "total": len(predictions),
            "resolved": 0,
            "pending": pending_n,
            "voided": voided_n,
            "brier": None,
            "log_loss": None,
            "calibration": {},
        }

    brier_sum = 0.0
    log_loss_sum = 0.0
    buckets: dict[float, dict[str, float]] = defaultdict(lambda: {"count": 0.0, "hits": 0.0})
    outcome_map = {"true": 1.0, "false": 0.0, "partial": 0.5}

    for p in resolved:
        prob = float(p.get("probability", 0.5))
        actual = outcome_map.get(str(p.get("outcome", "")).lower(), 0.5)

        brier_sum += (prob - actual) ** 2

        prob_clamped = max(min(prob, 0.999), 0.001)
        if actual == 1.0:
            log_loss_sum += -math.log(prob_clamped)
        elif actual == 0.0:
            log_loss_sum += -math.log(1.0 - prob_clamped)
        else:
            log_loss_sum += -(
                actual * math.log(prob_clamped)
                + (1.0 - actual) * math.log(1.0 - prob_clamped)
            )

        bucket = round(prob, 1)
        buckets[bucket]["count"] += 1
        buckets[bucket]["hits"] += actual

    n = len(resolved)
    calibration: dict[float, dict[str, Any]] = {}
    for bucket, data in sorted(buckets.items()):
        cnt = int(data["count"])
        actual_rate = data["hits"] / cnt if cnt > 0 else 0.0
        calibration[bucket] = {
            "predicted": bucket,
            "actual": round(actual_rate, 3),
            "n": cnt,
            "gap": round(abs(bucket - actual_rate), 3),
        }

    return {
        "total": len(predictions),
        "resolved": n,
        "pending": pending_n,
        "voided": voided_n,
        "brier": round(brier_sum / n, 4),
        "log_loss": round(log_loss_sum / n, 4),
        "calibration": calibration,
    }


def domain_breakdown(predictions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Compute calibration scores grouped by domain."""
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in predictions:
        domain = str(p.get("domain", "unknown"))
        by_domain[domain].append(p)
    return {domain: compute_scores(preds) for domain, preds in by_domain.items()}


def get_calibration_status(
    ledger_path: Path | str | None = None,
    *,
    as_of: str | None = None,
    session_log_dir: Path | None = None,
) -> dict[str, Any]:
    """Return complete calibration telemetry without crashing on unconfigured workspaces."""
    path = Path(ledger_path).resolve() if ledger_path is not None else get_calibration_ledger_path()
    if not path.exists():
        return {
            "status": "unconfigured",
            "ledger_path": str(path),
            "total": 0,
            "resolved": 0,
            "pending": 0,
            "voided": 0,
            "brier": None,
            "log_loss": None,
            "calibration": {},
            "by_domain": {},
            "overdue_ids": [],
            "overdue": [],
            "upcoming_ids": [],
            "upcoming": [],
            "pre_registration_warnings": [],
        }

    predictions = parse_ledger(path)
    scores = compute_scores(predictions)
    by_domain = domain_breakdown(predictions)
    pre_reg_warnings = validate_pre_registration(predictions, session_log_dir=session_log_dir)

    today = (as_of or datetime.now().strftime("%Y-%m-%d"))[:10]
    pending = [p for p in predictions if str(p.get("outcome", "")).lower() == "pending"]

    def _due(p: dict[str, Any]) -> str:
        raw = str(p.get("deadline", "9999-12-31")).strip()
        m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
        return m.group(0) if m else "9999-12-31"

    overdue_items = sorted([p for p in pending if _due(p) < today], key=_due)
    upcoming_items = sorted([p for p in pending if _due(p) >= today], key=_due)

    def _compact_item(p: dict[str, Any]) -> dict[str, str]:
        return {
            "id": str(p["id"]),
            "deadline": _due(p),
            "domain": str(p.get("domain", "unknown")),
            "claim": str(p.get("claim", "?"))[:80],
        }

    return {
        "status": "ok",
        "ledger_path": str(path),
        **scores,
        "by_domain": by_domain,
        "overdue_ids": [str(p["id"]) for p in overdue_items],
        "overdue": [_compact_item(p) for p in overdue_items],
        "upcoming_ids": [str(p["id"]) for p in upcoming_items],
        "upcoming": [_compact_item(p) for p in upcoming_items],
        "pre_registration_warnings": pre_reg_warnings,
    }


def format_calibration_report(status: dict[str, Any]) -> str:
    """Render an ASCII-only calibration report from get_calibration_status()."""
    lines = [
        "=" * 60,
        "  ATHENA CALIBRATION REPORT",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
    ]

    if status.get("status") == "unconfigured":
        lines.extend([
            f"  Ledger not found at: {status.get('ledger_path')}",
            "  Calibration is unconfigured in this workspace (0 resolved predictions).",
            "",
            "=" * 60,
        ])
        return "\n".join(lines)

    lines.extend([
        f"  Total predictions:  {status['total']}",
        f"  Resolved:           {status['resolved']}",
        f"  Pending:            {status['pending']}",
    ])
    if status.get("voided"):
        lines.append(f"  Voided (excluded):  {status['voided']}  (premise never materialized)")
    lines.append("")

    brier = status.get("brier")
    if brier is not None:
        if brier < 0.1:
            band = "(excellent)"
        elif brier < 0.2:
            band = "(good)"
        elif brier < 0.25:
            band = "(average)"
        else:
            band = "(needs improvement)"
        lines.append(f"  Brier Score:        {brier:.4f}  {band}")
        lines.append(f"  Log-Loss:           {status['log_loss']:.4f}")
        lines.append("")

        cal_buckets = status.get("calibration") or {}
        if cal_buckets:
            lines.append("  Calibration Buckets:")
            lines.append(f"  {'Predicted':>10} {'Actual':>8} {'N':>4} {'Gap':>6}")
            lines.append(f"  {'-' * 10} {'-' * 8} {'-' * 4} {'-' * 6}")
            for _, data in sorted(cal_buckets.items()):
                gap_marker = " [!]" if data["gap"] > 0.15 else ""
                lines.append(
                    f"  {data['predicted']:>10.1f} "
                    f"{data['actual']:>8.3f} "
                    f"{data['n']:>4} "
                    f"{data['gap']:>6.3f}{gap_marker}"
                )
            lines.append("")

        lines.append("  Domain Breakdown:")
        for domain, dscores in (status.get("by_domain") or {}).items():
            if dscores["resolved"] > 0:
                lines.append(
                    f"    {domain:>12}: Brier={dscores['brier']:.4f} (n={dscores['resolved']})"
                )
            else:
                lines.append(f"    {domain:>12}: no resolved predictions yet")
    else:
        lines.append("  No resolved predictions yet. Resolve some and re-run.")

    overdue = status.get("overdue") or []
    if overdue:
        lines.extend([
            "",
            f"  [!] OVERDUE -- RESOLVE NOW ({len(overdue)}): deadline passed, still pending.",
            "      Set outcome true/false/partial in CALIBRATION_LEDGER.md.",
        ])
        for item in overdue:
            lines.append(f"    ! {item['id']}: {item['claim'][:60]}... (due: {item['deadline']})")

    upcoming = status.get("upcoming") or []
    if upcoming:
        lines.extend(["", "  Pending Predictions (upcoming):"])
        for item in upcoming:
            lines.append(f"    {item['id']}: {item['claim'][:60]}... (due: {item['deadline']})")

    warnings = status.get("pre_registration_warnings") or []
    if warnings:
        lines.extend(["", "  PRE-REGISTRATION INTEGRITY:"])
        lines.extend(warnings)
    elif status.get("resolved", 0) > 0:
        lines.extend(["", "  Pre-registration: All resolved predictions verified."])

    lines.extend(["", "=" * 60])
    return "\n".join(lines)
