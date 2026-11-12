#!/usr/bin/env python3
r"""
.agent/scripts/ucds_audit.py
============================

CLI Auditor for Universal Counterparty Dossier Standard (UCDS) Invariants.
Enforces CANONICAL §513, RSC-580 §5.4, and PSY-585 §7.

Usage:
    python3 .agent/scripts/ucds_audit.py --dossier path/to/dossier.md
    python3 .agent/scripts/ucds_audit.py --text "RAW_DOSSIER_MARKDOWN"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure src/ is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from athena.intelligence.ucds_validator import UCDSDossierValidator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit counterparty intelligence dossiers against UCDS invariants (CANONICAL §513)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dossier", type=Path, help="Path to UCDS markdown dossier file.")
    group.add_argument("--text", type=str, help="Raw markdown text of UCDS dossier.")

    args = parser.parse_args()

    if args.dossier:
        if not args.dossier.exists():
            print(f"Error: Dossier file not found: {args.dossier}", file=sys.stderr)
            return 2
        content = args.dossier.read_text(encoding="utf-8")
        target_src = str(args.dossier)
    else:
        content = args.text
        target_src = "<inline text>"

    validator = UCDSDossierValidator()
    report = validator.audit(content)

    print("=" * 60)
    print("=== Universal Counterparty Dossier Standard Audit (CANONICAL §513) ===")
    print("=" * 60)
    print(f"Target Source:     {target_src}")
    print(f"Target Name:       {report.target_name}")
    print(f"Evaluated Track:   {report.track}")
    print(f"Knockout Verdict:  {report.knockout_verdict}")
    print(f"Cashflow Verdict:  {report.directional_cashflow_verdict}")
    print(f"Overall Status:    {'PASS' if report.is_valid else 'FAIL'}")
    print(f"Compliance Score:  {int(report.compliance_score * 100)}%")
    print("-" * 60)

    print("--- 6-Section Completeness ---")
    for sec in report.sections_present:
        print(f"  [x] {sec}")
    for sec in report.sections_missing:
        print(f"  [ ] {sec} (MISSING)")

    print("\n--- 5-State Provenance Distribution ---")
    for tag, count in report.provenance_counts.items():
        print(f"  • {tag:18} : {count}")

    if report.violations:
        print("\n--- Violations (Gating Invariants) ---")
        for v in report.violations:
            print(f"  ❌ {v}")

    if report.warnings:
        print("\n--- Warnings ---")
        for w in report.warnings:
            print(f"  ⚠️ {w}")

    print("=" * 60)
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
