#!/usr/bin/env python3
"""
calibration_score.py — Weekly Calibration Scorer (CLI example wrapper)
======================================================================

Thin CLI wrapper around `athena.intelligence.calibration`.

Usage:
    python3 examples/scripts/calibration_score.py
    python3 examples/scripts/calibration_score.py --update
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from athena.intelligence.calibration import (  # noqa: E402
    compute_scores,
    domain_breakdown,
    format_calibration_report,
    get_calibration_status,
    parse_ledger,
    validate_pre_registration,
)

LEDGER_PATH = PROJECT_ROOT / ".context" / "calibration" / "CALIBRATION_LEDGER.md"

__all__ = [
    "parse_ledger",
    "validate_pre_registration",
    "compute_scores",
    "domain_breakdown",
    "main",
]


def main() -> int:
    if not LEDGER_PATH.exists():
        print(f"Ledger not found at {LEDGER_PATH} (status: unconfigured)")
        return 0

    status = get_calibration_status(ledger_path=LEDGER_PATH)
    print(format_calibration_report(status))

    if "--update" in sys.argv and status.get("brier") is not None:
        week = datetime.now().strftime("%Y-W%V")
        badge = "PASS" if status["brier"] < 0.2 else "WARN"
        row = (
            f"| {week} | {status['total']} | {status['resolved']} "
            f"| {status['brier']:.4f} | {status['log_loss']:.4f} "
            f"| {badge} |"
        )
        print("\nAppend this row to the Weekly Calibration Score table:")
        print(f"   {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
