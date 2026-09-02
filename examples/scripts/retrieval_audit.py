#!/usr/bin/env python3
"""
Retrieval Audit — reads retrieval_log.jsonl and reports:
  1. Overall hit/partial/miss distribution
  2. Source channel contribution (which backends are earning their weight)
  3. Queries that consistently miss (candidates for new embeddings or pruning)
  4. Time-series trend (is retrieval quality improving or degrading?)

Usage:
    python3 .agent/scripts/retrieval_audit.py [--days 14] [--top 20]
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
LOG_PATH = PROJECT_ROOT / ".agent" / "telemetry" / "retrieval_log.jsonl"
INVOCATIONS_PATH = PROJECT_ROOT / ".athena" / "invocations.jsonl"


def load_entries(days: int = 14) -> list[dict]:
    """Load log entries within the given day window."""
    if not LOG_PATH.exists():
        print(f"⚠️  No retrieval log found at {LOG_PATH}")
        print("   The log is created automatically when smart_search.py runs.")
        print("   Wait for search invocations to accumulate, then re-run this audit.")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    for line in LOG_PATH.read_text().splitlines():
        try:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["ts"])
            if ts >= cutoff:
                entries.append(entry)
        except (json.JSONDecodeError, KeyError):
            continue
    return entries


def load_invocations(days: int = 14) -> list[dict]:
    if not INVOCATIONS_PATH.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    try:
        with open(INVOCATIONS_PATH) as f:
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


def report(entries: list[dict], top: int = 20, days: int = 14) -> None:
    if not entries:
        print("No data to analyze.")
        return

    print(f"\n{'='*60}")
    print(f"📊 RETRIEVAL AUDIT — {len(entries)} queries analyzed")
    print(f"{'='*60}\n")

    # 1. Quality Distribution
    quality_counts = Counter(e["quality"] for e in entries)
    total = len(entries)
    print("── 1. RETRIEVAL QUALITY ──")
    for q in ["hit", "partial", "miss"]:
        count = quality_counts.get(q, 0)
        pct = (count / total) * 100
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        label = {"hit": "✅ Hit", "partial": "🟡 Partial", "miss": "❌ Miss"}[q]
        print(f"  {label:12s} {bar} {pct:5.1f}% ({count})")
    print()

    # Effective Recall Ratio
    hit_rate = ((quality_counts.get("hit", 0) + quality_counts.get("partial", 0) * 0.5) / total) * 100
    print(f"  📈 Effective Recall Ratio: {hit_rate:.1f}%\n")

    # 2. Source Contribution
    print("── 2. SOURCE CHANNEL CONTRIBUTION ──")
    source_totals = Counter()
    for e in entries:
        for src, count in e.get("sources", {}).items():
            source_totals[src] += count

    total_source_hits = sum(source_totals.values())
    for src, count in source_totals.most_common(top):
        pct = (count / total_source_hits) * 100
        print(f"  {src:20s} {count:4d} results ({pct:5.1f}%)")
    print()

    # 3. Consistent Misses (queries that always miss)
    print("── 3. CONSISTENT MISSES (candidates for new embeddings) ──")
    query_quality = defaultdict(list)
    for e in entries:
        query_quality[e["query"]].append(e["quality"])

    misses = [(q, quals) for q, quals in query_quality.items()
              if all(qual == "miss" for qual in quals) and len(quals) >= 2]
    if misses:
        for q, quals in sorted(misses, key=lambda x: -len(x[1]))[:top]:
            print(f"  ❌ [{len(quals)}x] \"{q}\"")
    else:
        print("  (No consistent misses — system is performing well)")
    print()

    # 4. Daily Trend
    print("── 4. DAILY QUALITY TREND ──")
    daily = defaultdict(lambda: {"hit": 0, "partial": 0, "miss": 0, "total": 0})
    for e in entries:
        day = e["ts"][:10]
        daily[day][e["quality"]] += 1
        daily[day]["total"] += 1

    for day in sorted(daily.keys()):
        d = daily[day]
        hr = ((d["hit"] + d["partial"] * 0.5) / d["total"]) * 100
        print(f"  {day}  hit={d['hit']:2d}  partial={d['partial']:2d}  miss={d['miss']:2d}  recall={hr:5.1f}%")
    print()

    # 5. Retrieval Compliance
    print("── 5. RETRIEVAL COMPLIANCE ──")
    invocations = load_invocations(days)

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
    web_required = 0
    web_fired = 0
    web_hit = 0

    for entry in entries:
        sources = entry.get("source_distribution", {})
        if not sources and "sources" in entry:
            sources = entry["sources"]
        web_count = sources.get("web_search", 0)

        intent = entry.get("intent", "")
        if intent in ("GENERAL", "PERSONALISED_DECISION"):
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
    args = parser.parse_args()

    entries = load_entries(args.days)
    report(entries, args.top, args.days)


if __name__ == "__main__":
    main()
