#!/usr/bin/env python3
"""
decision_ledger.py — Closed-Loop Decision Outcome & Calibration Ledger
======================================================================

Records strategic decisions with explicit predictions, confidence levels,
and verification horizons. Closes the learning loop by auditing outcomes
against predictions and calculating Brier calibration scores.

Storage: .context/audit/decision_ledger.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = PROJECT_ROOT / ".context" / "audit"
LEDGER_PATH = AUDIT_DIR / "decision_ledger.jsonl"


def ensure_storage() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        LEDGER_PATH.touch()


def load_entries() -> list[dict[str, Any]]:
    ensure_storage()
    entries = []
    with open(LEDGER_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def save_entries(entries: list[dict[str, Any]]) -> None:
    ensure_storage()
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def log_decision(
    title: str,
    decision: str,
    domain: str,
    expected_outcome: str,
    confidence: float,
    horizon_days: int = 30,
    rejected_alt: str = "",
    rationale: str = "",
) -> dict[str, Any]:
    ensure_storage()
    now_dt = datetime.now(timezone.utc)
    verify_dt = now_dt + timedelta(days=horizon_days)

    date_str = now_dt.strftime("%Y-%m-%d")
    entries = load_entries()
    today_count = sum(1 for e in entries if e.get("created_at", "").startswith(date_str))
    dec_id = f"DEC-{date_str}-{today_count + 1:02d}"

    entry = {
        "decision_id": dec_id,
        "created_at": now_dt.isoformat(),
        "title": title,
        "domain": domain,
        "decision": decision,
        "rejected_alternative": rejected_alt,
        "rationale": rationale,
        "confidence": max(0.0, min(1.0, confidence)),
        "expected_outcome": expected_outcome,
        "verification_date": verify_dt.strftime("%Y-%m-%d"),
        "status": "pending",
        "actual_outcome": None,
        "brier_score": None,
        "resolved_at": None,
    }

    entries.append(entry)
    save_entries(entries)
    return entry


def check_overdue(as_of_date: str | None = None) -> list[dict[str, Any]]:
    entries = load_entries()
    ref_date = as_of_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue = [
        e
        for e in entries
        if e.get("status") == "pending"
        and e.get("verification_date")
        and e.get("verification_date") <= ref_date
    ]
    return overdue


def resolve_decision(
    decision_id: str,
    outcome: str,
    success: bool,
) -> dict[str, Any]:
    entries = load_entries()
    target = None
    for e in entries:
        if e.get("decision_id") == decision_id:
            target = e
            break

    if not target:
        raise ValueError(f"Decision ID '{decision_id}' not found in ledger.")

    p = target.get("confidence", 0.5)
    y = 1.0 if success else 0.0
    brier = (p - y) ** 2

    target["status"] = "validated" if success else "refuted"
    target["actual_outcome"] = outcome
    target["brier_score"] = round(brier, 4)
    target["resolved_at"] = datetime.now(timezone.utc).isoformat()

    save_entries(entries)
    return target


def calculate_stats() -> dict[str, Any]:
    entries = load_entries()
    total = len(entries)
    pending = sum(1 for e in entries if e.get("status") == "pending")
    validated = sum(1 for e in entries if e.get("status") == "validated")
    refuted = sum(1 for e in entries if e.get("status") == "refuted")
    resolved = validated + refuted

    brier_scores = [
        e["brier_score"] for e in entries if e.get("brier_score") is not None
    ]
    avg_brier = sum(brier_scores) / len(brier_scores) if brier_scores else 0.0
    accuracy = (validated / resolved * 100.0) if resolved > 0 else 0.0

    return {
        "total_decisions": total,
        "pending": pending,
        "resolved": resolved,
        "validated": validated,
        "refuted": refuted,
        "accuracy_percent": accuracy,
        "mean_brier_score": round(avg_brier, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Athena Closed-Loop Decision Outcome & Calibration Ledger"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a new strategic decision")
    log_parser.add_argument("--title", required=True, help="Decision title")
    log_parser.add_argument("--decision", required=True, help="Chosen action")
    log_parser.add_argument(
        "--domain",
        choices=["trading", "business", "personal", "engineering", "academic"],
        default="business",
    )
    log_parser.add_argument(
        "--expected-outcome",
        required=True,
        help="Observable, falsifiable expected outcome",
    )
    log_parser.add_argument(
        "--confidence",
        type=float,
        required=True,
        help="Confidence level between 0.0 and 1.0",
    )
    log_parser.add_argument(
        "--horizon-days",
        type=int,
        default=30,
        help="Days until verification (default: 30)",
    )
    log_parser.add_argument("--rejected-alt", default="", help="Rejected alternative")
    log_parser.add_argument("--rationale", default="", help="Decision rationale")
    log_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Check overdue command
    overdue_parser = subparsers.add_parser(
        "check-overdue", help="Check for decisions due for review"
    )
    overdue_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a past decision")
    resolve_parser.add_argument("--id", required=True, help="Decision ID (e.g. DEC-2026-08-26-01)")
    resolve_parser.add_argument("--outcome", required=True, help="Actual observed outcome")
    resolve_parser.add_argument(
        "--success", action="store_true", help="Whether prediction was validated"
    )
    resolve_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show calibration stats")
    stats_parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.command == "log":
        entry = log_decision(
            title=args.title,
            decision=args.decision,
            domain=args.domain,
            expected_outcome=args.expected_outcome,
            confidence=args.confidence,
            horizon_days=args.horizon_days,
            rejected_alt=args.rejected_alt,
            rationale=args.rationale,
        )
        if args.json:
            print(json.dumps(entry, indent=2))
        else:
            print(f"Logged Decision [{entry['decision_id']}]: {entry['title']}")
            print(f"  Confidence: {entry['confidence'] * 100:.1f}% | Due: {entry['verification_date']}")
            print(f"  Expected: {entry['expected_outcome']}")
        return 0

    elif args.command == "check-overdue":
        overdue = check_overdue()
        if args.json:
            print(json.dumps(overdue, indent=2))
        else:
            if not overdue:
                print("No decisions currently overdue for outcome review.")
            else:
                print("============================================================")
                print("           DECISIONS OVERDUE FOR OUTCOME REVIEW             ")
                print("============================================================")
                for o in overdue:
                    print(f"[{o['decision_id']}] {o['title']} (Due: {o['verification_date']})")
                    print(f"  Expected: {o['expected_outcome']}")
                    print(f"  Resolve via: python3 .agent/scripts/decision_ledger.py resolve --id {o['decision_id']} --outcome '...' --success")
                    print("------------------------------------------------------------")
        return 0

    elif args.command == "resolve":
        res = resolve_decision(args.id, args.outcome, args.success)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status_str = "VALIDATED" if args.success else "REFUTED"
            print(f"Resolved [{res['decision_id']}]: {status_str}")
            print(f"  Brier Score: {res['brier_score']:.4f} (0.0 = perfect calibration)")
        return 0

    elif args.command == "stats":
        stats = calculate_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("============================================================")
            print("          DECISION CALIBRATION ACCURACY SCOREBOARD          ")
            print("============================================================")
            print(f"  Total Logged Decisions   : {stats['total_decisions']}")
            print(f"  Pending Verifications    : {stats['pending']}")
            print(f"  Resolved Decisions       : {stats['resolved']}")
            print(f"  Prediction Accuracy      : {stats['accuracy_percent']:.1f}%")
            print(f"  Mean Brier Score         : {stats['mean_brier_score']:.4f} (Lower = Better)")
            print("============================================================")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
