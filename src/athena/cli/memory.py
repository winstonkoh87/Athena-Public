"""
athena.cli.memory
=================

Unified CLI subcommand group for local memory operations:
- `athena memory eval [--json] [--fixtures] [--fail-on-warn]`
- `athena memory verify [--json] [--apply-safe]`
- `athena memory forget <phrase> [--apply] [--include-context] [--include-logs] [--force] [--json]`
- `athena memory taint {status,mark,clear}`
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from athena.core.taint import clear_taint, get_taint_status, mark_tainted
from athena.memory.dream_verifier import (
    apply_safe_dream_pruning,
    verify_pending_learnings,
)
from athena.memory.forget import forget_phrase
from athena.memory.health import evaluate_memory_health, run_memory_fixtures


def register_memory_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register `athena memory ...` subcommands on the root parser."""
    mem_parser = subparsers.add_parser(
        "memory",
        help="Evaluate, verify, quarantine, or forget local agent memory",
    )
    mem_sub = mem_parser.add_subparsers(dest="memory_action", required=True)

    # eval
    eval_p = mem_sub.add_parser("eval", help="Run zero-token memory health evaluation")
    eval_p.add_argument("--fixtures", action="store_true", help="Run synthetic CI isolation/TTL/taint fixtures")
    eval_p.add_argument("--json", action="store_true", help="Emit JSON output")
    eval_p.add_argument("--fail-on-warn", action="store_true", help="Exit 1 if health warnings or fixture failures occur")

    # verify
    ver_p = mem_sub.add_parser("verify", help="Verify pending SYSTEM_LEARNINGS.md rows against session logs")
    ver_p.add_argument("--apply-safe", action="store_true", help="Apply deterministic dedup + expired pruning only")
    ver_p.add_argument("--json", action="store_true", help="Emit JSON output")

    # forget
    fgt_p = mem_sub.add_parser("forget", help="Atomically erase matching literal entries across local memory stores")
    fgt_p.add_argument("phrase", help="Literal case-insensitive phrase to forget")
    fgt_p.add_argument("--apply", action="store_true", help="Apply erasure to disk (default is dry-run)")
    fgt_p.add_argument("--include-context", action="store_true", help="Also scrub activeContext.md and semantic_log.md")
    fgt_p.add_argument("--include-logs", action="store_true", help="Also scrub .context/memories/session_logs/*.md")
    fgt_p.add_argument("--force", action="store_true", help="Allow short (<4 char) phrases")
    fgt_p.add_argument("--json", action="store_true", help="Emit JSON output")

    # taint
    taint_p = mem_sub.add_parser("taint", help="Inspect or manage monotonic inbound taint quarantine")
    taint_sub = taint_p.add_subparsers(dest="taint_action", required=True)

    t_status = taint_sub.add_parser("status", help="Show current session taint status")
    t_status.add_argument("--json", action="store_true", help="Emit JSON output")

    t_mark = taint_sub.add_parser("mark", help="Mark current session monotonically tainted")
    t_mark.add_argument("--source", required=True, help="Untrusted input source identifier")
    t_mark.add_argument("--reason", default="untrusted_input", help="Reason for quarantine")
    t_mark.add_argument("--json", action="store_true", help="Emit JSON output")

    t_clear = taint_sub.add_parser("clear", help="Clear taint with explicit --human-confirm")
    t_clear.add_argument("--human-confirm", action="store_true", help="Required explicit operator confirmation")
    t_clear.add_argument("--json", action="store_true", help="Emit JSON output")

    return mem_parser


def _handle_eval(args: argparse.Namespace, project_root: Path | None) -> int:
    health = evaluate_memory_health(project_root=project_root)
    payload: dict[str, Any] = {"health": health}
    fixtures_ok = True
    if args.fixtures:
        fx = run_memory_fixtures()
        payload["fixtures"] = fx
        fixtures_ok = bool(fx["all_passed"])

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
            f"  TTL/Queue : pending={ttl['system_pending']}, expired={ttl['user_expired'] + ttl['system_expired']}, "
            f"imminent={ttl['imminent_expiring']}, missing_ttl={ttl['date_bound_missing_ttl']}"
        )
        print(f"  Borges    : ratio={bm['ratio']} ({bm['curated_bytes']} / {bm['raw_corpus_bytes']} B)")
        if health["warnings"]:
            for w in health["warnings"]:
                print(f"  WARN: {w}")
        if args.fixtures:
            fx = payload["fixtures"]
            print(f"  Fixtures  : {fx['passed']}/{fx['total']} passed")

    if not fixtures_ok:
        return 1
    if args.fail_on_warn and health["warnings"]:
        return 1
    return 0


def _handle_verify(args: argparse.Namespace, project_root: Path | None) -> int:
    report = verify_pending_learnings(project_root=project_root)
    safe_res = None
    if args.apply_safe:
        safe_res = apply_safe_dream_pruning(project_root=project_root, dry_run=False)
        report = {**report, "apply_safe": safe_res}

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        c = report["counts"]
        print(
            f"Dream Verifier: {report['total_pending']} pending unique rows "
            f"(dupes={report['duplicate_count']})"
        )
        for k, v in c.items():
            print(f"  {k:18s}: {v}")
        if safe_res is not None:
            print(
                f"  Applied safe prune: user_removed={safe_res['user']['removed']}, "
                f"system_removed={safe_res['system']['removed']}"
            )
    return 0


def _handle_forget(args: argparse.Namespace, project_root: Path | None) -> int:
    try:
        res = forget_phrase(
            args.phrase,
            project_root=project_root,
            dry_run=not args.apply,
            include_context=args.include_context,
            include_logs=args.include_logs,
            force=args.force,
        )
    except ValueError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}))
        else:
            print(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        mode = "APPLIED" if not res["dry_run"] else "DRY-RUN"
        print(
            f"[{mode}] forget {res['phrase']!r}: {res['entries_removed']} entries across "
            f"{res['files_matched']}/{res['files_scanned']} files "
            f"(cache_invalidated={res['cache_invalidated']})"
        )
        for d in res["details"]:
            print(f"  - {d['path']}: {d['removed']}")
    return 0


def _handle_taint(args: argparse.Namespace, project_root: Path | None) -> int:
    action = args.taint_action
    if action == "status":
        status = get_taint_status(project_root=project_root)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            state = "TAINTED" if status["tainted"] else "CLEAN"
            print(f"Taint Status [{status['session_id']}]: {state} (sources={len(status['sources'])})")
        return 0

    if action == "mark":
        entry = mark_tainted(args.source, args.reason, project_root=project_root)
        if args.json:
            print(json.dumps(entry, indent=2))
        else:
            print(f"Marked session '{entry['session_id']}' TAINTED (source={args.source}, reason={args.reason})")
        return 0

    if action == "clear":
        try:
            cleared = clear_taint(human_confirm=args.human_confirm, project_root=project_root)
        except ValueError as exc:
            if args.json:
                print(json.dumps({"cleared": False, "error": str(exc)}))
            else:
                print(f"Refused: {exc}")
            return 1
        if args.json:
            print(json.dumps({"cleared": cleared}))
        else:
            print(f"Taint cleared: {cleared}")
        return 0

    return 1


def run_memory_command(args: argparse.Namespace) -> int:
    """Dispatch `athena memory ...` subcommands."""
    project_root = getattr(args, "root", None)
    action = getattr(args, "memory_action", None)
    if action == "eval":
        return _handle_eval(args, project_root)
    if action == "verify":
        return _handle_verify(args, project_root)
    if action == "forget":
        return _handle_forget(args, project_root)
    if action == "taint":
        return _handle_taint(args, project_root)
    return 1
