#!/usr/bin/env python3
"""
scripts/boot_status.py — Single-Pass Parallel Boot Status Aggregator
===================================================================

Replaces sequential shell invocations during `/start` (accountability_render,
maintenance_ratio, frame_ledger, decisions_due, index_health --boot,
context_summaries, last_boot.log) with one concurrent, warning-free Python
process targeting < 1.0s end-to-end wall time.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(os.environ.get("ATHENA_ROOT") or Path(__file__).resolve().parent.parent)
for _entry in (
    PROJECT_ROOT,
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT / ".agent" / "scripts",
    PROJECT_ROOT / "examples" / "scripts",
):
    _s = str(_entry)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# Soft wall-clock budget for optional remote Gemini API probe inside index_health.
_PROBE_DEADLINE_S = 0.85


def _emit_receipt(name: str, rc: int, summary: str, extra: dict[str, Any] | None = None) -> None:
    """Best-effort receipt emission without failing boot on I/O errors."""
    try:
        from lib import receipts

        receipts.emit(
            name=name,
            argv=sys.argv,
            rc=rc,
            summary=summary,
            extra=extra or {},
        )
    except Exception:
        pass


def _run_accountability() -> dict[str, Any]:
    """Render accountability status card and update .athena/receipts/accountability.json."""
    try:
        from accountability_render import render_accountability

        return render_accountability()
    except Exception as exc:
        return {"status": "error", "summary": f"accountability unavailable ({exc})", "summary_lines": [], "raw": {}}


def _run_maintenance_ratio(days: int = 30) -> dict[str, Any]:
    """Compute recent commit maintenance vs output ratio and emit receipt."""
    try:
        from maintenance_ratio import ADVISORY_THRESHOLD, classify, collect_commits

        commits = collect_commits(days)
        total = len(commits)
        if not commits:
            return {
                "days": days,
                "total_commits": 0,
                "active_total": 0,
                "buckets": {},
                "maintenance_share": 0.0,
                "output_share": 0.0,
                "advisory": False,
                "summary": f"No commits in the last {days} days.",
            }

        buckets = Counter(classify(subject) for _, subject in commits)
        active_total = buckets["maintenance"] + buckets["output"]
        maint_share = buckets["maintenance"] / active_total if active_total > 0 else 0.0
        out_share = buckets["output"] / active_total if active_total > 0 else 0.0
        advisory = active_total > 0 and maint_share > ADVISORY_THRESHOLD
        summary = (
            f"Maintenance: {buckets['maintenance']} ({maint_share:.0%} of active) | "
            f"Output: {buckets['output']} ({out_share:.0%} of active)"
        )
        _emit_receipt(
            name="maintenance_ratio",
            rc=0,
            summary=summary,
            extra={
                "maintenance_share": maint_share,
                "output_share": out_share,
                "active_total": active_total,
                "total_commits": total,
            },
        )
        return {
            "days": days,
            "total_commits": total,
            "active_total": active_total,
            "buckets": dict(buckets),
            "maintenance_share": round(maint_share, 4),
            "output_share": round(out_share, 4),
            "advisory": advisory,
            "summary": summary,
        }
    except Exception as exc:
        return {"days": days, "error": str(exc), "summary": f"maintenance_ratio unavailable ({exc})"}


def _run_frame_ledger() -> dict[str, Any]:
    """Score frame calibration directly in-process (avoids python -m RuntimeWarning)."""
    try:
        from athena.intelligence.frame_ledger import (
            DEFAULT_LEDGER,
            FrameLedger,
            score_frames,
        )

        ledger_path = PROJECT_ROOT / DEFAULT_LEDGER
        return score_frames(FrameLedger(ledger_path).frames())
    except Exception as exc:
        return {"error": str(exc), "kill_switch_status": f"frame_ledger unavailable ({exc})"}


def _run_decisions_due() -> dict[str, Any]:
    """Scan calibration ledger and decision log for overdue reviews and emit receipt."""
    try:
        from decisions_due import check_cal_ledger, check_decision_log, get_current_date

        today = get_current_date()
        cal_due = check_cal_ledger(today)
        dec_due, dateless_count = check_decision_log(today)
        total_due = len(cal_due) + len(dec_due)
        summary = f"Decisions: {total_due} due for review | {dateless_count} dateless legacy"
        _emit_receipt(
            name="decisions_due",
            rc=0,
            summary=summary,
            extra={
                "total_due": total_due,
                "dateless_count": dateless_count,
                "scanned_date": str(today),
            },
        )
        return {
            "scanned_date": str(today),
            "total_due": total_due,
            "dateless_decisions": dateless_count,
            "cal_overdue": cal_due,
            "decisions_due": dec_due,
            "summary": summary,
        }
    except Exception as exc:
        return {"error": str(exc), "summary": f"decisions_due unavailable ({exc})"}


def _local_index_fallback(reason: str) -> dict[str, Any]:
    """Build deterministic local FTS + sync status report when network probe is slow."""
    sync_file = PROJECT_ROOT / ".agent" / "telemetry" / "vector_sync_status.json"
    fts_db = PROJECT_ROOT / ".athena" / "exocortex_fts.db"
    warnings: list[str] = []
    healthy = True

    sync_data: dict[str, Any] | None = None
    if sync_file.exists():
        try:
            sync_data = json.loads(sync_file.read_text(encoding="utf-8"))
            if sync_data.get("status") != "success":
                healthy = False
                warnings.append(f"Last sync status was {sync_data.get('status')}")
        except Exception:
            sync_data = {"status": "unreadable"}

    fts_age_hours: float | None = None
    if fts_db.exists():
        fts_age_hours = round((time.time() - fts_db.stat().st_mtime) / 3600, 1)
        if fts_age_hours > 168:
            warnings.append(f"FTS index is {fts_age_hours}h old (>7 days)")
    else:
        healthy = False
        warnings.append("Local FTS index (.athena/exocortex_fts.db) absent")

    fts_str = f"{fts_age_hours}h old" if fts_age_hours is not None else "absent"
    sync_str = (sync_data or {}).get("status", "ok")
    summary = (
        f"⚡ Index Health: vectors=ok (lag=skipped (fast boot)), fts=ok ({fts_str}), sync={sync_str}, api={reason}"
        if healthy
        else f"⚠️ Index Health Alert: {' | '.join(warnings)}"
    )
    return {
        "healthy": healthy,
        "vector_lag": "skipped (fast boot)",
        "fts_age_hours": fts_age_hours,
        "sync_status": sync_data,
        "api_credit": {"status": "deferred", "code": 0, "message": reason},
        "api_velocity": None,
        "warnings": warnings,
        "summary": summary,
    }


def _run_index_health_thread(result_box: dict[str, Any], done: threading.Event) -> None:
    """Execute index_health.check_health(skip_db_scan=True) inside a daemon thread."""
    try:
        from index_health import check_health

        report = check_health(skip_db_scan=True)
        result_box["report"] = report
        _emit_receipt(
            name="index_health",
            rc=0 if report.get("healthy", True) else 1,
            summary=report.get("summary", ""),
            extra={"healthy": report.get("healthy", True), "vector_lag": report.get("vector_lag")},
        )
    except Exception as exc:
        result_box["report"] = _local_index_fallback(f"probe error ({exc})")
    finally:
        done.set()


def _run_context_summaries(force: bool = False) -> dict[str, Any]:
    """Refresh memory bank summary metadata if stale."""
    try:
        from athena.boot.loaders.context_summaries import generate_summaries

        summaries = generate_summaries(force=force)
        return {
            "files": sorted(summaries.keys()),
            "count": len(summaries),
        }
    except Exception as exc:
        return {"error": str(exc), "count": 0}


def _touch_last_boot_log() -> None:
    """Record fast-boot completion timestamp in .agent/state/last_boot.log."""
    try:
        log_file = PROJECT_ROOT / ".agent" / "state" / "last_boot.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(f"{datetime.now(timezone.utc).isoformat()} fast_boot\n", encoding="utf-8")
    except Exception:
        pass


def gather_boot_status(days: int = 30, force_summaries: bool = False) -> dict[str, Any]:
    """Run all boot telemetry checks concurrently within the fast-boot SLO budget."""
    t0 = time.perf_counter()

    # Launch daemon thread for index_health (may make 1 HTTP probe) so slow DNS/TLS never blocks exit.
    health_box: dict[str, Any] = {}
    health_done = threading.Event()
    health_thread = threading.Thread(
        target=_run_index_health_thread,
        args=(health_box, health_done),
        daemon=True,
        name="boot-index-health",
    )
    health_thread.start()

    futures: dict[str, Future[Any]] = {}
    executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="boot-local")
    try:
        futures["accountability"] = executor.submit(_run_accountability)
        futures["maintenance_ratio"] = executor.submit(_run_maintenance_ratio, days)
        futures["frame_ledger"] = executor.submit(_run_frame_ledger)
        futures["decisions_due"] = executor.submit(_run_decisions_due)
        futures["context_summaries"] = executor.submit(_run_context_summaries, force_summaries)

        payload: dict[str, Any] = {
            name: fut.result(timeout=2.0)
            for name, fut in futures.items()
        }
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    # Wait up to remaining probe budget for index_health, otherwise use instant local fallback.
    remaining = max(0.05, _PROBE_DEADLINE_S - (time.perf_counter() - t0))
    if health_done.wait(timeout=remaining) and "report" in health_box:
        payload["index_health"] = health_box["report"]
    else:
        fallback = _local_index_fallback(f"probe deferred (>{_PROBE_DEADLINE_S:.2f}s fast-boot cap)")
        _emit_receipt(
            name="index_health",
            rc=0 if fallback["healthy"] else 1,
            summary=fallback["summary"],
            extra={"healthy": fallback["healthy"], "vector_lag": fallback["vector_lag"], "deferred": True},
        )
        payload["index_health"] = fallback

    _touch_last_boot_log()
    payload["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return payload


def _format_digest(status: dict[str, Any]) -> str:
    """Render concise operator digest suitable for /start terminal output."""
    acc = status.get("accountability", {})
    mr = status.get("maintenance_ratio", {})
    fl = status.get("frame_ledger", {})
    dd = status.get("decisions_due", {})
    ih = status.get("index_health", {})

    lines = [
        f"⚡ Boot Status ({status.get('elapsed_ms', 0)} ms)",
        f"   Accountability : {acc.get('summary', 'unknown')}",
        f"   Maintenance    : {mr.get('summary', 'unknown')}",
        (
            f"   Frame Ledger   : opened={fl.get('frames_opened', 0)} "
            f"(resolved={fl.get('frames_resolved', 0)}) | {fl.get('kill_switch_status', 'n/a')}"
        ),
        f"   Decisions Due  : {dd.get('summary', 'unknown')}",
        f"   Index Health   : {ih.get('summary', 'unknown')}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Athena fast parallel /start status aggregator")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON payload")
    parser.add_argument("--days", type=int, default=30, help="Commit lookback window for maintenance_ratio")
    parser.add_argument("--force-summaries", action="store_true", help="Force memory bank summary regeneration")
    args = parser.parse_args(argv)

    status = gather_boot_status(days=args.days, force_summaries=args.force_summaries)
    if args.json:
        print(json.dumps(status, indent=2, default=str))
    else:
        print(_format_digest(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
