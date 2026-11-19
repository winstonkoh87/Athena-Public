#!/usr/bin/env python3
"""
check_governance_skip.py — Telemetry skip auditor for Meta-Awareness Gate & Governance Parity.

Audits `.athena/invocations.jsonl` records to measure fire rates, detect missing
meta-awareness checks, and verify governance compliance across Claude Code and
Antigravity sessions.

Usage:
    python3 .agent/scripts/check_governance_skip.py [--days 14]
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _REPO_ROOT / "src"
if _SRC_DIR.is_dir() and str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def audit_governance_telemetry(days: int = 14) -> dict:
    invocations_path = os.path.join(os.getcwd(), ".athena", "invocations.jsonl")
    if not os.path.exists(invocations_path):
        return {
            "status": "NO_DATA",
            "message": f"No telemetry log found at {invocations_path}",
            "records_count": 0,
            "fire_rate_pct": 0.0,
            "compliance_band": "N/A",
        }

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    records = []

    with open(invocations_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                ts_str = rec.get("ts")
                if ts_str:
                    rec_dt = datetime.fromisoformat(ts_str)
                    if rec_dt.tzinfo is None:
                        rec_dt = rec_dt.replace(tzinfo=timezone.utc)
                    if rec_dt < cutoff:
                        continue
                records.append(rec)
            except Exception:
                continue

    hook_fires = [r for r in records if r.get("name") == "meta_awareness_gate" or r.get("name") == "meta_awareness_check"]
    class_counts = Counter()
    for r in hook_fires:
        classes = r.get("classes", [])
        for c in classes:
            class_counts[c] += 1

    fire_rate_pct = 0.0
    compliance_band = "N/A"
    try:
        from athena.intelligence.gate_telemetry import GateTelemetryAnalyzer
    except ImportError:
        GateTelemetryAnalyzer = None

    if GateTelemetryAnalyzer is not None:
        summary = GateTelemetryAnalyzer(telemetry_path=Path(invocations_path)).analyze(window_days=days)
        fire_rate_pct = float(summary.fire_rate_pct)
        compliance_band = str(summary.compliance_band)

    return {
        "status": "OK",
        "days": days,
        "total_records": len(records),
        "governance_fires": len(hook_fires),
        "fire_rate_pct": fire_rate_pct,
        "compliance_band": compliance_band,
        "class_breakdown": dict(class_counts),
    }


def main():
    parser = argparse.ArgumentParser(description="Audit Meta-Awareness Gate Governance Telemetry")
    parser.add_argument("--days", type=int, default=14, help="Number of days to audit (default 14)")
    args = parser.parse_args()

    res = audit_governance_telemetry(days=args.days)
    print(f"📊 Governance Telemetry Audit (Last {args.days} days)")
    print(f"   Status:            {res['status']}")
    if res['status'] == "NO_DATA":
        print(f"   Message:           {res['message']}")
        sys.exit(0)

    print(f"   Total Logs:        {res['total_records']}")
    print(f"   Governance Fires:  {res['governance_fires']}")
    print(f"   Fire-Rate:         {res['fire_rate_pct']:.1f}%")
    print(f"   Compliance Band:   {res['compliance_band']}")
    if res['class_breakdown']:
        print("   Class Breakdown:")
        for cls_name, count in sorted(res['class_breakdown'].items()):
            print(f"     - {cls_name}: {count}")
    else:
        print("   Class Breakdown:   None")


if __name__ == "__main__":
    main()
