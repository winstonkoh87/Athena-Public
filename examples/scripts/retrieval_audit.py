#!/usr/bin/env python3
"""
Retrieval Audit — reads retrieval_log.jsonl and reports:
  1. Overall hit/partial/degraded/miss distribution
  2. Source channel contribution (which backends are earning their weight)
  3. Queries that consistently miss (candidates for new embeddings or pruning)
  4. Time-series trend (is retrieval quality improving or degrading?)
  5. Retrieval compliance against non-SNIPER turns
  6. Web channel metrics

Usage:
    python3 .agent/scripts/retrieval_audit.py [--days 14] [--top 20] [--log PATH] [--invocations PATH]
"""

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
DEFAULT_LOG_PATH = PROJECT_ROOT / ".agent" / "telemetry" / "retrieval_log.jsonl"
DEFAULT_INVOCATIONS_PATH = PROJECT_ROOT / ".athena" / "invocations.jsonl"


def resolve_default_path(path: Path) -> Path:
    """Resolve telemetry path with worktree fallback to main repo if missing."""
    if path.exists():
        return path
    try:
        git_common = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        main_root = Path(git_common).resolve().parent
        fallback = main_root / path.relative_to(PROJECT_ROOT)
        if fallback.exists():
            return fallback
    except Exception:
        pass
    return path


def load_entries(days: int = 14, log_path: Optional[Path] = None) -> list[dict]:
    """Load log entries within the given day window."""
    target_path = log_path if log_path is not None else resolve_default_path(DEFAULT_LOG_PATH)
    if not target_path.exists():
        print(f"⚠️  No retrieval log found at {target_path}")
        print("   The log is created automatically when smart_search.py runs.")
        print("   Wait for search invocations to accumulate, then re-run this audit.")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    for line in target_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["ts"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                entries.append(entry)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return entries


def load_invocations(days: int = 14, invocations_path: Optional[Path] = None) -> list[dict]:
    target_path = invocations_path if invocations_path is not None else resolve_default_path(DEFAULT_INVOCATIONS_PATH)
    if not target_path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    try:
        with open(target_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    ts_str = entry.get("timestamp", entry.get("ts", ""))
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts >= cutoff:
                            entries.append(entry)
                    else:
                        entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    pass
    except Exception:
        pass
    return entries


def report(
    entries: list[dict],
    top: int = 20,
    days: int = 14,
    invocations_path: Optional[Path] = None,
) -> None:
    if not entries:
        print("No data to analyze.")
        return

    print(f"\n{'='*60}")
    print(f"📊 RETRIEVAL AUDIT — {len(entries)} queries analyzed")
    print(f"{'='*60}\n")

    # 1. Quality Distribution
    quality_counts = Counter(e.get("quality", "miss") for e in entries)
    total = len(entries)
    print("── 1. RETRIEVAL QUALITY ──")
    quality_labels = {
        "hit": "✅ Hit",
        "partial": "🟡 Partial",
        "degraded": "⚠️ Degraded",
        "miss": "❌ Miss",
    }
    ordered_qualities = ["hit", "partial", "degraded", "miss"]
    for q in quality_counts:
        if q not in ordered_qualities:
            ordered_qualities.append(q)

    for q in ordered_qualities:
        count = quality_counts.get(q, 0)
        pct = (count / total) * 100 if total else 0.0
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        label = quality_labels.get(q, f"❓ {q.capitalize()}")
        print(f"  {label:14s} {bar} {pct:5.1f}% ({count})")
    print()

    # Effective Recall Ratio: hit=1.0, partial=0.5, degraded=0.25 (fallback keywords without vector)
    hit_rate = (
        (quality_counts.get("hit", 0) + quality_counts.get("partial", 0) * 0.5 + quality_counts.get("degraded", 0) * 0.25)
        / max(total, 1)
    ) * 100
    print(f"  📈 Effective Recall Ratio: {hit_rate:.1f}%\n")

    # 2. Source Contribution
    print("── 2. SOURCE CHANNEL CONTRIBUTION ──")
    source_totals = Counter()
    for e in entries:
        for src, count in e.get("sources", {}).items():
            source_totals[src] += count

    total_source_hits = sum(source_totals.values())
    for src, count in source_totals.most_common(top):
        pct = (count / total_source_hits) * 100 if total_source_hits else 0.0
        print(f"  {src:20s} {count:4d} results ({pct:5.1f}%)")
    print()

    # 3. Consistent Misses (queries that always miss)
    print("── 3. CONSISTENT MISSES (candidates for new embeddings) ──")
    query_quality = defaultdict(list)
    for e in entries:
        query_quality[e.get("query", "")].append(e.get("quality", "miss"))

    misses = [
        (q, quals)
        for q, quals in query_quality.items()
        if q and all(qual == "miss" for qual in quals) and len(quals) >= 2
    ]
    if misses:
        for q, quals in sorted(misses, key=lambda x: -len(x[1]))[:top]:
            print(f'  ❌ [{len(quals)}x] "{q}"')
    else:
        print("  (No consistent misses — system is performing well)")
    print()

    # 4. Daily Trend
    print("── 4. DAILY QUALITY TREND ──")
    daily = defaultdict(lambda: defaultdict(int))
    for e in entries:
        day = e.get("ts", "")[:10]
        if not day:
            continue
        q = e.get("quality", "miss")
        daily[day][q] += 1
        daily[day]["total"] += 1

    for day in sorted(daily.keys()):
        d = daily[day]
        total_day = d["total"] or 1
        hr = ((d["hit"] + d["partial"] * 0.5 + d["degraded"] * 0.25) / total_day) * 100
        print(
            f"  {day}  hit={d['hit']:2d}  partial={d['partial']:2d}  degraded={d['degraded']:2d}  miss={d['miss']:2d}  recall={hr:5.1f}%"
        )
    print()

    # 5. Retrieval Compliance
    print("── 5. RETRIEVAL COMPLIANCE ──")
    invocations = load_invocations(days, invocations_path=invocations_path)

    retrieval_turns = sum(
        1 for e in invocations
        if e.get("type") in ("smart_search", "context_gate", "agentic_search")
    ) + len(entries)

    total_turns = len(invocations)
    violation_turns = sum(
        1 for e in invocations
        if e.get("type") == "quicksave" and "violation" in str(e.get("governance", "")).lower()
    )
    non_sniper_turns = max(retrieval_turns + violation_turns, 1)
    compliance_rate = min(retrieval_turns / non_sniper_turns * 100, 100.0)
    target = 90.0
    status = "PASS" if compliance_rate >= target else "BELOW TARGET"

    print(f"  Retrieval turns:   {retrieval_turns}")
    print(f"  Non-SNIPER turns:  {non_sniper_turns}")
    print(f"  Compliance rate:   {compliance_rate:.1f}% (target: {target}%) [{status}]\n")

    # 6. Web Channel Metrics
    print("── 6. WEB CHANNEL METRICS ──")
    from athena.tools.web_triggers import needs_web

    web_required = 0
    web_fired = 0
    web_hit = 0

    for entry in entries:
        sources = entry.get("source_distribution", {})
        if not sources and "sources" in entry:
            sources = entry["sources"]
        web_count = sources.get("web_search", 0)

        intent = entry.get("intent", "")
        query_text = entry.get("query") or entry.get("raw_query") or ""
        req_web, _reason = needs_web(query_text, intent)
        if req_web:
            web_required += 1

        if web_count > 0:
            web_fired += 1
            web_hit += 1

    print(f"  Web required:  {web_required}")
    print(f"  Web fired:     {web_fired}")
    print(f"  Web hit:       {web_hit}\n")


def main():
    parser = argparse.ArgumentParser(description="Athena Retrieval Audit")
    parser.add_argument("--days", type=int, default=14, help="Lookback window in days")
    parser.add_argument("--top", type=int, default=20, help="Top N items to show")
    parser.add_argument("--log", type=Path, default=None, help="Path to retrieval_log.jsonl")
    parser.add_argument("--invocations", type=Path, default=None, help="Path to invocations.jsonl")
    args = parser.parse_args()

    entries = load_entries(args.days, log_path=args.log)
    report(entries, args.top, args.days, invocations_path=args.invocations)


if __name__ == "__main__":
    main()
