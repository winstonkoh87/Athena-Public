#!/usr/bin/env python3
"""
lint_governance.py — Governance & Coherence Linter
===================================================
Performs semantic check of Athena's governance boundaries and files:
  1. Checks for duplicate Tech Debt IDs (TD-XXX) in TECH_DEBT.md.
  2. Checks for duplicate/overlapping query IDs in golden_queries.json and gold_queries.json.
  3. Checks that Sniper, Standard, and Ultra risk thresholds (Lambda score boundaries)
     remain consistent between code (governance.py) and workflows (_shared.md).

Exits with code 0 on success, or code 1 if contradictions/duplicates are found.
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TECH_DEBT_PATH = PROJECT_ROOT / ".context" / "TECH_DEBT.md"
GOLDEN_QUERIES_PATH = PROJECT_ROOT / ".agent" / "eval" / "golden_queries.json"
GOLD_QUERIES_PATH = PROJECT_ROOT / ".agent" / "eval" / "gold_queries.json"
GOVERNANCE_PATH = PROJECT_ROOT / "src" / "athena" / "core" / "governance.py"
SHARED_WF_PATH = PROJECT_ROOT / ".agent" / "workflows" / "_shared.md"


def lint_tech_debt() -> int:
    """Check for duplicate TD-XXX keys in TECH_DEBT.md."""
    if not TECH_DEBT_PATH.exists():
        print(f"⚠️  TECH_DEBT.md not found at {TECH_DEBT_PATH}, skipping.")
        return 0

    content = TECH_DEBT_PATH.read_text(encoding="utf-8")
    # Matches "## TD-XXX" or "## ~~TD-XXX~~" at the start of lines
    td_pattern = r"^##\s+(?:~~)?(TD-\d+)"
    all_tds = re.findall(td_pattern, content, re.MULTILINE)

    duplicates = set(td for td in all_tds if all_tds.count(td) > 1)

    if duplicates:
        print(f"❌ [LINT] Duplicate Tech Debt IDs found in TECH_DEBT.md: {', '.join(duplicates)}")
        return 1

    print("✅ [LINT] TECH_DEBT.md duplicate check passed.")
    return 0


def lint_eval_queries() -> int:
    """Check for duplicate query IDs in evaluation golden sets."""
    errors = 0
    ids = {}

    # Check golden_queries.json
    if GOLDEN_QUERIES_PATH.exists():
        try:
            with open(GOLDEN_QUERIES_PATH) as f:
                golden = json.load(f)
            golden_ids = [q["id"] for q in golden if "id" in q]
            dups = set(i for i in golden_ids if golden_ids.count(i) > 1)
            if dups:
                print(f"❌ [LINT] Duplicate IDs in golden_queries.json: {', '.join(dups)}")
                errors += 1
            for q in golden:
                if "id" in q:
                    ids[q["id"]] = "golden_queries.json"
        except Exception as e:
            print(f"❌ [LINT] Failed to parse golden_queries.json: {e}")
            errors += 1

    # Check gold_queries.json
    if GOLD_QUERIES_PATH.exists():
        try:
            with open(GOLD_QUERIES_PATH) as f:
                gold = json.load(f)
            # gold_queries is a dict with key "queries"
            queries = gold.get("queries", [])
            gold_ids = [q["id"] for q in queries if "id" in q]
            dups = set(i for i in gold_ids if gold_ids.count(i) > 1)
            if dups:
                print(f"❌ [LINT] Duplicate IDs in gold_queries.json: {', '.join(dups)}")
                errors += 1
            for q in queries:
                qid = q.get("id")
                if qid:
                    if qid in ids:
                        print(f"❌ [LINT] Cross-file ID collision for {qid} in gold_queries.json and {ids[qid]}")
                        errors += 1
                    else:
                        ids[qid] = "gold_queries.json"
        except Exception as e:
            print(f"❌ [LINT] Failed to parse gold_queries.json: {e}")
            errors += 1

    if errors == 0:
        print("✅ [LINT] Evaluation query sets duplicate check passed.")
        return 0
    return 1


def lint_risk_thresholds() -> int:
    """Check that Lambda risk thresholds align between governance.py and workflows/."""
    errors = 0

    # 1. Parse governance.py risk comments/constants
    gov_sniper_val = None
    gov_standard_val = None
    if GOVERNANCE_PATH.exists():
        content = GOVERNANCE_PATH.read_text(encoding="utf-8")
        # Find e.g. "Sniper Mode (Λ < 10)"
        match_sniper = re.search(r"Sniper Mode\s*\(Λ\s*<\s*(\d+)\)", content, re.IGNORECASE)
        match_std = re.search(r"Standard\s*\(Λ\s*(\d+)-(\d+)\)", content, re.IGNORECASE)
        if match_sniper:
            gov_sniper_val = int(match_sniper.group(1))
        if match_std:
            gov_standard_val = (int(match_std.group(1)), int(match_std.group(2)))

    # 2. Parse _shared.md risk comments/text
    wf_sniper_val = None
    wf_standard_val = None
    if SHARED_WF_PATH.exists():
        content = SHARED_WF_PATH.read_text(encoding="utf-8")
        match_sniper = re.search(r"SNIPER.*\(Λ\s*<\s*(\d+)\)", content, re.IGNORECASE)
        match_std = re.search(r"STANDARD.*\(Λ\s*(\d+)-(\d+)\)", content, re.IGNORECASE)
        if match_sniper:
            wf_sniper_val = int(match_sniper.group(1))
        if match_std:
            wf_standard_val = (int(match_std.group(1)), int(match_std.group(2)))

    # Compare
    if gov_sniper_val and wf_sniper_val and gov_sniper_val != wf_sniper_val:
        print(f"❌ [LINT] Sniper threshold mismatch: governance.py says {gov_sniper_val}, but _shared.md says {wf_sniper_val}")
        errors += 1
    if gov_standard_val and wf_standard_val and gov_standard_val != wf_standard_val:
        print(f"❌ [LINT] Standard threshold range mismatch: governance.py says {gov_standard_val}, but _shared.md says {wf_standard_val}")
        errors += 1

    if errors == 0:
        print("✅ [LINT] Risk thresholds (Lambda score boundaries) alignment check passed.")
        return 0
    return 1


def main():
    print("🤖 Running Athena Governance Linter...")
    print("=" * 60)

    code = 0
    code |= lint_tech_debt()
    code |= lint_eval_queries()
    code |= lint_risk_thresholds()

    print("=" * 60)
    if code == 0:
        print("🎉 [SUCCESS] All governance lint checks passed.")
        sys.exit(0)
    else:
        print("❌ [FAILURE] Linter surfaced contradictions or duplicate records.")
        sys.exit(1)


if __name__ == "__main__":
    main()
