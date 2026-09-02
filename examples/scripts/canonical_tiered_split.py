#!/usr/bin/env python3
"""
CANONICAL Section 4 Tiered Split — TD-021 Implementation

Reads tier_map.json and CANONICAL.md to produce three tiered files:
  - CANONICAL_TIER1.md  (Always Boot — universal laws, identity, session mechanics)
  - CANONICAL_TIER2.md  (Domain-Triggered — trading, business, psychology, etc.)
  - CANONICAL_TIER3.md  (On-Demand — historical case-specific, cross-domain niche)

Also rewrites CANONICAL.md Section 4 to contain ONLY Tier 1 entries,
with a note pointing to Tier 2/3 files for on-demand loading.

Usage:
    python3 .agent/scripts/canonical_tiered_split.py [--dry-run]
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CANONICAL_PATH = PROJECT_ROOT / ".context" / "CANONICAL.md"
TIER_MAP_PATH = PROJECT_ROOT / ".agent" / "telemetry" / "tier_map.json"
OUTPUT_DIR = PROJECT_ROOT / ".context"

TIER_LABELS = {
    1: "Always Boot — Universal laws, identity truths, session mechanics",
    2: "Domain-Triggered — Loaded when query matches trading, business, psychology, content, architecture, or geo domains",
    3: "On-Demand — Historical case-specific, cross-domain niche. Retrievable via Exocortex search.",
}


def load_tier_map() -> dict:
    """Load the tier classification map."""
    return json.loads(TIER_MAP_PATH.read_text(encoding="utf-8"))


def parse_canonical() -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Parse CANONICAL.md into four sections:
    - before_section4: lines before Section 4
    - section4_header: the Section 4 header + table header lines
    - section4_rows: the actual table data rows
    - after_section4: lines after Section 4
    """
    lines = CANONICAL_PATH.read_text(encoding="utf-8").splitlines(keepends=True)

    before = []
    header = []
    rows = []
    after = []

    state = "before"

    for i, line in enumerate(lines):
        if state == "before":
            if line.startswith("## 4. Strategic Frameworks"):
                state = "header"
                header.append(line)
            else:
                before.append(line)
        elif state == "header":
            header.append(line)
            # After the separator line (|---|---|---|), switch to rows
            if "---" in line and "|" in line:
                state = "rows"
        elif state == "rows":
            if line.startswith("## 5.") or (line.startswith("---") and not line.strip().startswith("|")):
                state = "after"
                after.append(line)
            elif line.strip() == "":
                # blank line before the next section
                rows.append(line)
            else:
                rows.append(line)
        elif state == "after":
            after.append(line)

    return before, header, rows, after


def classify_rows(rows: list[str], tier_map: dict) -> dict[int, list[str]]:
    """Classify each row into its tier based on the tier_map entries."""
    entries = tier_map["entries"]

    # Build a lookup: framework name -> tier
    name_to_tier = {}
    for entry in entries:
        name_to_tier[entry["name"].lower().strip()] = entry["tier"]

    tiered = {1: [], 2: [], 3: []}

    for row in rows:
        if not row.strip() or not row.strip().startswith("|"):
            continue

        # Extract framework name from the first column
        parts = [p.strip() for p in row.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue

        name = parts[0].replace("**", "").strip().lower()

        # Look up tier
        tier = name_to_tier.get(name, 2)  # Default to Tier 2 if not found
        tiered[tier].append(row)

    return tiered


def generate_tier_file(tier: int, header_lines: list[str], rows: list[str]) -> str:
    """Generate content for a tier file."""
    label = TIER_LABELS[tier]

    lines = []
    lines.append(f"# CANONICAL Section 4 — Tier {tier}\n")
    lines.append("\n")
    lines.append(f"> **Classification**: {label}\n")
    lines.append("> **Source**: Split from CANONICAL.md Section 4 (TD-021, 2026-05-09)\n")
    lines.append(f"> **Entries**: {len(rows)}\n")

    if tier == 1:
        lines.append("> **Load**: ALWAYS — included in every /start and /ultrastart boot.\n")
    elif tier == 2:
        lines.append("> **Load**: When query domain matches (trading, business/pricing, psychology, content/marketing, architecture, real estate/geo).\n")
    else:
        lines.append("> **Load**: On explicit request or Exocortex search hit only.\n")

    lines.append("\n")
    lines.append("| Framework | Protocol | Core Principle |\n")
    lines.append("| :--- | :--- | :--- |\n")

    for row in rows:
        lines.append(row if row.endswith("\n") else row + "\n")

    lines.append("\n")
    lines.append("---\n")
    lines.append("\n")
    lines.append("> **Navigation**: [CANONICAL.md](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL.md) · ")
    lines.append("[Tier 1](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL_TIER1.md) · ")
    lines.append("[Tier 2](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL_TIER2.md) · ")
    lines.append("[Tier 3](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL_TIER3.md)\n")

    return "".join(lines)


def rewrite_canonical_section4(before: list[str], header: list[str],
                                 tiered: dict[int, list[str]], after: list[str]) -> str:
    """Rewrite CANONICAL.md with only Tier 1 in Section 4, plus navigation to Tier 2/3."""
    result = []

    # Everything before Section 4
    result.extend(before)

    # Section 4 header (modified)
    result.append("## 4. Strategic Frameworks (Active) — Tier 1: Always Boot\n")
    result.append("\n")
    result.append("> **Progressive Disclosure (TD-021)**: This section contains only **Tier 1** frameworks\n")
    result.append("> (universal laws and identity truths loaded every session). Domain-specific frameworks\n")
    result.append("> are in [CANONICAL_TIER2.md](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL_TIER2.md)\n")
    result.append("> (156 entries, ~54KB — loaded when domain matches). Historical/niche frameworks are in\n")
    result.append("> [CANONICAL_TIER3.md](file:///Users/[AUTHOR]/Project%20Athena/.context/CANONICAL_TIER3.md)\n")
    result.append("> (3 entries, ~1KB — on-demand via Exocortex).\n")
    result.append(">\n")
    result.append("> **Boot savings**: ~55KB (~69%) of Section 4 deferred from /start boot context.\n")
    result.append("\n")
    result.append("| Framework | Protocol | Core Principle |\n")
    result.append("| :--- | :--- | :--- |\n")

    for row in tiered[1]:
        result.append(row if row.endswith("\n") else row + "\n")

    result.append("\n")

    # Section 5 onwards
    result.extend(after)

    return "".join(result)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CANONICAL Section 4 Tiered Split")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing files")
    args = parser.parse_args()

    # Load data
    tier_map = load_tier_map()
    before, header, rows, after = parse_canonical()

    # Classify rows
    tiered = classify_rows(rows, tier_map)

    print(f"\n{'='*60}")
    print("📊 CANONICAL SECTION 4 TIERED SPLIT")
    print(f"{'='*60}\n")

    for t in [1, 2, 3]:
        label = TIER_LABELS[t]
        count = len(tiered[t])
        chars = sum(len(r) for r in tiered[t])
        print(f"  Tier {t} ({label[:30]:30s}): {count:3d} entries, {chars:6,d} chars (~{chars//1024}KB)")

    total_t2t3 = sum(len(r) for r in tiered[2]) + sum(len(r) for r in tiered[3])
    print(f"\n  🎯 Boot savings: ~{total_t2t3:,d} chars (~{total_t2t3//1024}KB) removed from /start context")

    if args.dry_run:
        print("\n  [DRY RUN] No files written.")
        return

    # Write tier files
    for t in [1, 2, 3]:
        path = OUTPUT_DIR / f"CANONICAL_TIER{t}.md"
        content = generate_tier_file(t, header, tiered[t])
        path.write_text(content, encoding="utf-8")
        print(f"\n  💾 Written: {path.relative_to(PROJECT_ROOT)} ({len(tiered[t])} entries)")

    # Rewrite CANONICAL.md
    new_canonical = rewrite_canonical_section4(before, header, tiered, after)
    CANONICAL_PATH.write_text(new_canonical, encoding="utf-8")
    print("  💾 Rewritten: .context/CANONICAL.md (Section 4 now Tier 1 only)")

    # Update tier_map.json with execution metadata
    tier_map["meta"]["split_executed"] = True
    tier_map["meta"]["split_date"] = "2026-05-09"
    tier_map["meta"]["files"] = {
        "tier1": ".context/CANONICAL_TIER1.md",
        "tier2": ".context/CANONICAL_TIER2.md",
        "tier3": ".context/CANONICAL_TIER3.md",
    }
    TIER_MAP_PATH.write_text(json.dumps(tier_map, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  💾 Updated: .agent/telemetry/tier_map.json (split_executed=true)")

    print("\n✅ TD-021 split complete.")


if __name__ == "__main__":
    main()
