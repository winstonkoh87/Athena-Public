#!/usr/bin/env python3
"""
scripts/memory_eval.py — Zero-Token Memory Health & Transcript Verifier CLI
===========================================================================

Evaluates startup memory footprint, cross-layer shingle overlap, TTL hygiene,
Borges's Map Trap ratio, synthetic scope/taint fixtures, and `/dream` transcript
verification without invoking any LLM APIs.

Usage:
    python3 scripts/memory_eval.py
    python3 scripts/memory_eval.py --fixtures --json
    python3 scripts/memory_eval.py --verify --json
    python3 scripts/memory_eval.py --fixtures --fail-on-warn
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from athena.memory.dream_verifier import verify_pending_learnings  # noqa: E402
from athena.memory.health import (  # noqa: E402
    evaluate_memory_health,
    run_memory_fixtures,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Zero-token memory health evaluator, fixture runner, and transcript verifier."
    )
    parser.add_argument("--root", type=Path, default=None, help="Override project root path")
    parser.add_argument("--fixtures", action="store_true", help="Run 4 deterministic isolation/TTL/taint fixtures")
    parser.add_argument("--verify", action="store_true", help="Run deterministic /dream pending learnings verifier")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit 1 on warnings or fixture failures")
    args = parser.parse_args(argv)

    root = args.root or PROJECT_ROOT
    health = evaluate_memory_health(project_root=root)
    payload: dict[str, Any] = {"health": health}

    fixtures_ok = True
    if args.fixtures:
        fx = run_memory_fixtures()
        payload["fixtures"] = fx
        fixtures_ok = bool(fx["all_passed"])

    if args.verify:
        payload["verify"] = verify_pending_learnings(project_root=root)

    if args.json:
        print(json.dumps(payload, indent=2, default=str))
    else:
        fp = health["startup_footprint"]
        ov = health["cross_layer_overlap"]
        ttl = health["ttl_hygiene"]
        bm = health["borges_map"]
        print(f"Memory Health: {health['status'].upper()}")
        print(
            f"  Startup   : userContext={fp['user_context_bytes']}B, "
            f"active_surgical={fp['active_surgical_bytes']}B, canonical={fp['canonical_bytes']}B"
        )
        print(f"  Overlap   : {ov['overall_overlap_pct']}% across {len(ov['layers_evaluated'])} layers")
        print(
            f"  TTL/Queue : pending={ttl['system_pending']}, "
            f"expired={ttl['user_expired'] + ttl['system_expired']}, "
            f"imminent={ttl['imminent_expiring']}, missing_ttl={ttl['date_bound_missing_ttl']}"
        )
        print(f"  Borges    : ratio={bm['ratio']} ({bm['curated_bytes']} / {bm['raw_corpus_bytes']} B)")
        if health["warnings"]:
            for w in health["warnings"]:
                print(f"  WARN: {w}")
        if args.fixtures:
            fx = payload["fixtures"]
            print(f"  Fixtures  : {fx['passed']}/{fx['total']} passed")
        if args.verify:
            ver = payload["verify"]
            print(f"  Verify    : {ver['counts']} (dupes={ver['duplicate_count']})")

    if not fixtures_ok:
        return 1
    if args.fail_on_warn and health["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
