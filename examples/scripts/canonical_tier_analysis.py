#!/usr/bin/env python3
"""
CANONICAL Progressive Disclosure Analyzer — A6 (MCDA Rank #2)

Scans Section 4 of CANONICAL.md, classifies each framework entry by domain,
and outputs a recommended tiering for progressive disclosure:

  Tier 1 (Always Boot): Universal laws, identity truths, session mechanics
  Tier 2 (Domain-Triggered): Trading, Business/Pricing, Psychology, Content
  Tier 3 (On-Demand): Historical case-specific, cross-domain niche

This does NOT modify CANONICAL.md. It produces a report + a machine-readable
tier_map.json that the boot sequence can use for conditional loading.

Usage:
    python3 .agent/scripts/canonical_tier_analysis.py [--output tier_map.json]
"""

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CANONICAL_PATH = PROJECT_ROOT / ".context" / "CANONICAL.md"

# Domain classification keywords
DOMAIN_KEYWORDS = {
    "trading": [
        "trading", "kelly", "stop loss", "volatility", "drawdown", "bankroll",
        "grid", "martingale", "sizing", "atr", "pips", "ruin", "r:r", "win rate",
        "ergodic", "stochastic", "xauusd", "gbpusd", "eurusd", "barbell",
        "free-roll", "partial", "capital velocity", "carnot", "iron triangle",
        "swap", "layer", "pip", "broker", "margin", "lot size"
    ],
    "business_pricing": [
        "pricing", "capstone", "anchor", "client", "scope", "retainer",
        "agency", "consulting", "diagnostic", "$/hr", "revenue", "invoice",
        "service", "quote", "freelance", "cogs", "margin", "sow", "lead",
        "funnel", "conversion", "cpc", "cac", "disrespect fee", "grace protocol",
        "collect before deliver", "cbd", "fixer", "discovery gem", "pre-quote",
        "batch delivery"
    ],
    "psychology": [
        "schema", "ifs", "nervous system", "selection bias", "boy-shaped",
        "imperviousness", "sycophancy", "consiglieri", "darvo", "therapy",
        "reciprocity", "mismatch", "pryce", "ghost protocol", "pain threshold",
        "emotional", "dignity premium", "permission engine", "hope override"
    ],
    "architecture": [
        "protocol", "workflow", "canonical", "boot", "context", "ecl",
        "token", "graphrag", "embedding", "retrieval", "skill loading",
        "context_trigger", "progressive disclosure", "attention", "200k",
        "one-session", "pre-paid compute", "flat-rate", "maximum depth",
        "iteration arbitrage", "cross-model", "ultrastart"
    ],
    "content_marketing": [
        "seo", "content", "listing", "carousell", "resonance", "painmax",
        "schwartz", "awareness", "hook", "distribution", "audience",
        "reddit", "ugc", "youtube", "geo alpha", "barnacle"
    ],
    "real_estate_geo": [
        "fnb", "landlord", "lease", "renovation", "food fair", "rental",
        "jb", "singapore", "dental", "status tax", "geographic", "platform physics"
    ],
}

# Tier classification rules
TIER_1_KEYWORDS = [
    "law #", "immutable", "core law", "decision sovereignty", "200k ecl",
    "one-session", "pre-paid compute", "maximum depth", "context density",
    "law of ruin", "circuit breaker", "aoy", "collect before deliver",
    "data compounding", "bionic", "symbiotic rsi", "fixer",
]

TIER_3_KEYWORDS = [
    "session s", "cs-", "case study", "food fair", "tom & stefanie",
    "mr hainan", "topayo", "zenith", "[CLIENT]", "shubhra",
    "fnb", "pregnancy guy", "chia boon teck", "jimmy mcgill",
    "mq a", "siva",
]


def classify_domain(text: str) -> str:
    """Classify a framework entry into a domain by keyword density."""
    text_lower = text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return "general"
    return max(scores, key=scores.get)


def classify_tier(name: str, text: str) -> int:
    """Classify into tier 1/2/3 based on universality and specificity."""
    combined = (name + " " + text).lower()

    # Tier 1: Universal principles that apply every session
    for kw in TIER_1_KEYWORDS:
        if kw in combined:
            return 1

    # Tier 3: Case-specific historical entries
    tier3_score = sum(1 for kw in TIER_3_KEYWORDS if kw in combined)
    if tier3_score >= 2:
        return 3

    # Default: Tier 2 (domain-triggered)
    return 2


def parse_section_4() -> list[dict]:
    """Parse Section 4 table rows from CANONICAL.md."""
    text = CANONICAL_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    entries = []
    in_section_4 = False

    for i, line in enumerate(lines):
        if line.startswith("## 4. Strategic Frameworks"):
            in_section_4 = True
            continue
        if line.startswith("## 5."):
            break
        if not in_section_4:
            continue

        # Parse table rows (skip header/separator)
        if line.startswith("|") and "---" not in line and "Framework" not in line:
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]  # Remove empty strings
            if len(parts) >= 3:
                name = parts[0].replace("**", "").strip()
                protocol_ref = parts[1].strip()
                description = parts[2].strip()

                domain = classify_domain(description)
                tier = classify_tier(name, description)
                char_count = len(description)

                entries.append({
                    "line": i + 1,
                    "name": name,
                    "protocol": protocol_ref,
                    "domain": domain,
                    "tier": tier,
                    "chars": char_count,
                })

    return entries


def report(entries: list[dict], output_path: str | None = None) -> None:
    """Print analysis report and optionally save tier map."""
    print(f"\n{'='*70}")
    print("📊 CANONICAL PROGRESSIVE DISCLOSURE ANALYSIS")
    print(f"{'='*70}\n")

    total = len(entries)
    total_chars = sum(e["chars"] for e in entries)
    print(f"Total Section 4 entries: {total}")
    print(f"Total character volume:  {total_chars:,} chars (~{total_chars // 1024}KB)")
    print()

    # Tier distribution
    tier_counts = Counter(e["tier"] for e in entries)
    tier_chars = {t: sum(e["chars"] for e in entries if e["tier"] == t) for t in [1, 2, 3]}

    print("── TIER DISTRIBUTION ──")
    for t in [1, 2, 3]:
        label = {1: "Always Boot", 2: "Domain-Triggered", 3: "On-Demand"}[t]
        count = tier_counts.get(t, 0)
        chars = tier_chars.get(t, 0)
        print(f"  Tier {t} ({label:17s}): {count:3d} entries, {chars:6,d} chars (~{chars // 1024}KB)")

    boot_savings = tier_chars.get(2, 0) + tier_chars.get(3, 0)
    print(f"\n  🎯 Potential boot savings: ~{boot_savings:,} chars (~{boot_savings // 1024}KB)")
    print(f"     = {(boot_savings / total_chars * 100):.0f}% of Section 4 removed from boot context")
    print()

    # Domain distribution
    print("── DOMAIN DISTRIBUTION ──")
    domain_counts = Counter(e["domain"] for e in entries)
    for domain, count in domain_counts.most_common():
        print(f"  {domain:20s}: {count:3d} entries")
    print()

    # Tier 3 candidates (largest entries by char count — most savings per archival)
    print("── TOP 10 TIER 3 CANDIDATES (highest boot savings if deferred) ──")
    tier3 = sorted([e for e in entries if e["tier"] == 3], key=lambda x: -x["chars"])
    for e in tier3[:10]:
        print(f"  [{e['chars']:,} chars] L{e['line']}: {e['name']}")
    print()

    # Tier 1 entries (always boot — these should be reviewed for correctness)
    print("── TIER 1 (ALWAYS BOOT) ──")
    for e in sorted([e for e in entries if e["tier"] == 1], key=lambda x: x["line"]):
        print(f"  L{e['line']}: {e['name']} ({e['domain']})")
    print()

    # Save tier map
    if output_path:
        tier_map = {
            "meta": {
                "total_entries": total,
                "total_chars": total_chars,
                "tier_counts": dict(tier_counts),
                "boot_savings_chars": boot_savings,
            },
            "entries": entries,
        }
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(tier_map, indent=2, ensure_ascii=False))
        print(f"  💾 Tier map saved to: {out}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CANONICAL Progressive Disclosure Analyzer")
    parser.add_argument("--output", "-o", default=None, help="Path to save tier_map.json")
    args = parser.parse_args()

    entries = parse_section_4()
    report(entries, args.output)


if __name__ == "__main__":
    main()
