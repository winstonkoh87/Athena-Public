#!/usr/bin/env python3
"""
calibration_score.py — Weekly Calibration Scorer
=================================================

Parses CALIBRATION_LEDGER.md, computes Brier score and log-loss
for all resolved predictions, and outputs a calibration report.

Usage:
    python3 .agent/scripts/calibration_score.py
    python3 .agent/scripts/calibration_score.py --update  # Append score to ledger

Audit Ref: Capability Upgrade CAL-001
"""

import math
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER_PATH = PROJECT_ROOT / ".context" / "calibration" / "CALIBRATION_LEDGER.md"


def parse_ledger(path: Path) -> list[dict]:
    """Parse all predictions from the calibration ledger."""
    content = path.read_text(encoding="utf-8")
    predictions = []

    # Match each ### CAL-XXX block
    blocks = re.split(r"### (CAL-\d+)", content)

    for i in range(1, len(blocks), 2):
        cal_id = blocks[i]
        body = blocks[i + 1]

        pred = {"id": cal_id}

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

        for key, pattern in patterns.items():
            match = re.search(pattern, body)
            if match:
                pred[key] = match.group(1).strip()

        # Convert probability to float
        if "probability" in pred:
            try:
                pred["probability"] = float(pred["probability"])
            except ValueError:
                pred["probability"] = 0.5

        predictions.append(pred)

    return predictions


def validate_pre_registration(predictions: list[dict]) -> list[str]:
    """Validate pre-registration integrity: predictions must be logged before resolution.

    Checks:
    1. Every resolved prediction has a source_session field
    2. source_session date (from session log filename) precedes resolved_date
    3. Flags predictions without source_session as unverifiable
    """
    SESSION_LOG_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
    warnings = []

    for p in predictions:
        if p.get("outcome") not in ("true", "false", "partial"):
            continue  # Only check resolved predictions

        cal_id = p["id"]
        source = p.get("source_session", "")
        resolved_raw = p.get("resolved_date", "")

        # Extract date from resolved_date (format: "2026-07-29 — TRUE. ...")
        resolved_date = None
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", resolved_raw)
        if date_match:
            try:
                resolved_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            except ValueError:
                pass

        if not source:
            warnings.append(
                f"  ⚠️ {cal_id}: No source_session — cannot verify pre-registration."
            )
            continue

        # Extract session ID (e.g., "S661" from "S661" or "session 2026-06-18 (TD-046 close)")
        session_match = re.search(r"S(\d+)", source)
        source_date = None

        if session_match:
            # Try to find the session log file to extract its date
            session_num = session_match.group(1)
            for log_file in SESSION_LOG_DIR.glob(f"*session-{session_num}.md") if SESSION_LOG_DIR.exists() else []:
                # Filename format: YYYY-MM-DD-session-NNN.md
                fname_date = re.search(r"(\d{4}-\d{2}-\d{2})", log_file.name)
                if fname_date:
                    try:
                        source_date = datetime.strptime(fname_date.group(1), "%Y-%m-%d")
                    except ValueError:
                        pass
                    break
        else:
            # Try to extract date directly from source field
            source_date_match = re.search(r"(\d{4}-\d{2}-\d{2})", source)
            if source_date_match:
                try:
                    source_date = datetime.strptime(source_date_match.group(1), "%Y-%m-%d")
                except ValueError:
                    pass

        if source_date and resolved_date:
            if source_date > resolved_date:
                warnings.append(
                    f"  ❌ {cal_id}: PRE-REGISTRATION VIOLATION — source date "
                    f"{source_date.strftime('%Y-%m-%d')} is AFTER resolution date "
                    f"{resolved_date.strftime('%Y-%m-%d')}. Prediction may be retroactive."
                )
            elif source_date == resolved_date:
                warnings.append(
                    f"  ⚠️ {cal_id}: Same-day source and resolution — "
                    f"pre-registration integrity ambiguous."
                )
        elif not source_date and resolved_date:
            # Couldn't verify source date — just flag it
            warnings.append(
                f"  ℹ️ {cal_id}: Source '{source}' — session log not found, "
                f"pre-registration not mechanically verified."
            )

    return warnings


def compute_scores(predictions: list[dict]) -> dict:
    """Compute Brier score, log-loss, and calibration buckets."""
    resolved = [
        p for p in predictions
        if p.get("outcome") in ("true", "false", "partial")
    ]

    # void = premise never materialized (cancelled bet); excluded from scoring AND from pending.
    pending_n = len([p for p in predictions if p.get("outcome") == "pending"])
    voided_n = len([p for p in predictions if p.get("outcome") == "void"])

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
    buckets = defaultdict(lambda: {"count": 0, "hits": 0})

    for p in resolved:
        prob = p["probability"]
        outcome_map = {"true": 1.0, "false": 0.0, "partial": 0.5}
        actual = outcome_map.get(p["outcome"], 0.5)

        # Brier score: (probability - outcome)^2
        brier_sum += (prob - actual) ** 2

        # Log-loss: -(actual * log(prob) + (1-actual) * log(1-prob))
        # Clamp to avoid log(0)
        prob_clamped = max(min(prob, 0.999), 0.001)
        if actual == 1.0:
            log_loss_sum += -math.log(prob_clamped)
        elif actual == 0.0:
            log_loss_sum += -math.log(1 - prob_clamped)
        else:
            # Partial: weighted
            log_loss_sum += -(
                actual * math.log(prob_clamped)
                + (1 - actual) * math.log(1 - prob_clamped)
            )

        # Calibration bucket (rounded to nearest 0.1)
        bucket = round(prob, 1)
        buckets[bucket]["count"] += 1
        buckets[bucket]["hits"] += actual

    n = len(resolved)
    brier = brier_sum / n
    log_loss = log_loss_sum / n

    # Calibration: for each bucket, actual_rate vs predicted_rate
    calibration = {}
    for bucket, data in sorted(buckets.items()):
        actual_rate = data["hits"] / data["count"] if data["count"] > 0 else 0
        calibration[bucket] = {
            "predicted": bucket,
            "actual": round(actual_rate, 3),
            "n": data["count"],
            "gap": round(abs(bucket - actual_rate), 3),
        }

    return {
        "total": len(predictions),
        "resolved": n,
        "pending": pending_n,
        "voided": voided_n,
        "brier": round(brier, 4),
        "log_loss": round(log_loss, 4),
        "calibration": calibration,
    }


def domain_breakdown(predictions: list[dict]) -> dict:
    """Break down scores by domain."""
    by_domain = defaultdict(list)
    for p in predictions:
        domain = p.get("domain", "unknown")
        by_domain[domain].append(p)

    return {
        domain: compute_scores(preds)
        for domain, preds in by_domain.items()
    }


def print_report(scores: dict, by_domain: dict, predictions: list[dict], pre_reg_warnings: list[str] | None = None):
    """Print a formatted calibration report."""
    print("=" * 60)
    print("  ATHENA CALIBRATION REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    print(f"  Total predictions:  {scores['total']}")
    print(f"  Resolved:           {scores['resolved']}")
    print(f"  Pending:            {scores['pending']}")
    if scores.get("voided"):
        print(f"  Voided (excluded):  {scores['voided']}  (premise never materialized)")
    print()

    if scores["brier"] is not None:
        print(f"  Brier Score:        {scores['brier']:.4f}  ", end="")
        if scores["brier"] < 0.1:
            print("(excellent)")
        elif scores["brier"] < 0.2:
            print("(good)")
        elif scores["brier"] < 0.25:
            print("(average)")
        else:
            print("(needs improvement)")

        print(f"  Log-Loss:           {scores['log_loss']:.4f}")
        print()

        if scores["calibration"]:
            print("  Calibration Buckets:")
            print(f"  {'Predicted':>10} {'Actual':>8} {'N':>4} {'Gap':>6}")
            print(f"  {'-'*10} {'-'*8} {'-'*4} {'-'*6}")
            for bucket, data in scores["calibration"].items():
                gap_marker = " ⚠️" if data["gap"] > 0.15 else ""
                print(
                    f"  {data['predicted']:>10.1f} "
                    f"{data['actual']:>8.3f} "
                    f"{data['n']:>4} "
                    f"{data['gap']:>6.3f}{gap_marker}"
                )
            print()

        # Domain breakdown
        print("  Domain Breakdown:")
        for domain, dscores in by_domain.items():
            if dscores["resolved"] > 0:
                print(
                    f"    {domain:>12}: Brier={dscores['brier']:.4f} "
                    f"(n={dscores['resolved']})"
                )
            else:
                print(f"    {domain:>12}: no resolved predictions yet")

    else:
        print("  No resolved predictions yet. Resolve some and re-run.")

    # Pending predictions — split overdue (deadline passed, still unresolved) from upcoming.
    # Overdue is the silent killer of the loop: deadlines pass, nobody resolves, the metric
    # never computes. Surface them loudly so /end's Calibration Sweep can't skip them.
    pending = [p for p in predictions if p.get("outcome") == "pending"]
    today = datetime.now().strftime("%Y-%m-%d")

    def _due(p):
        return str(p.get("deadline", "9999-12-31"))

    overdue = sorted([p for p in pending if _due(p) < today], key=_due)
    upcoming = sorted([p for p in pending if _due(p) >= today], key=_due)

    if overdue:
        print()
        print(f"  ⚠️  OVERDUE — RESOLVE NOW ({len(overdue)}): deadline passed, still pending.")
        print("      These block the metric from ever computing. Set outcome true/false/partial.")
        for p in overdue:
            print(f"    ❗ {p['id']}: {p.get('claim', '?')[:60]}... (due: {_due(p)})")

    if upcoming:
        print()
        print("  Pending Predictions (upcoming):")
        for p in upcoming:
            print(f"    {p['id']}: {p.get('claim', '?')[:60]}... (due: {_due(p)})")

    # Pre-registration integrity
    if pre_reg_warnings:
        print()
        print("  🔒 PRE-REGISTRATION INTEGRITY:")
        for w in pre_reg_warnings:
            print(w)
    elif scores["resolved"] and scores["resolved"] > 0:
        print()
        print("  🔒 Pre-registration: All resolved predictions verified.")

    print()
    print("=" * 60)


def main():
    if not LEDGER_PATH.exists():
        print(f"❌ Ledger not found at {LEDGER_PATH}")
        sys.exit(1)

    predictions = parse_ledger(LEDGER_PATH)
    scores = compute_scores(predictions)
    by_domain = domain_breakdown(predictions)
    pre_reg_warnings = validate_pre_registration(predictions)
    print_report(scores, by_domain, predictions, pre_reg_warnings)

    # Optional: append to ledger
    if "--update" in sys.argv and scores["brier"] is not None:
        week = datetime.now().strftime("%Y-W%V")
        row = (
            f"| {week} | {scores['total']} | {scores['resolved']} "
            f"| {scores['brier']:.4f} | {scores['log_loss']:.4f} "
            f"| {'✅' if scores['brier'] < 0.2 else '⚠️'} |"
        )
        print("\n📝 Append this row to the Weekly Calibration Score table:")
        print(f"   {row}")


if __name__ == "__main__":
    main()
