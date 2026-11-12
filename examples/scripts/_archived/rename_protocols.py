#!/usr/bin/env python3
"""Protocol Naming Migration Script

Problem: 20+ numeric prefixes collide across different domain directories.
Example: 106-stealth-acquisition.md (acquisition/) and 106-distribution-physics.md (business/)
         Both are "Protocol 106" — ambiguous for search.

Solution: Prepend the domain directory as a 3-letter uppercase prefix to each filename.
Example: 106-stealth-acquisition.md → ACQ-106-stealth-acquisition.md
         106-distribution-physics.md → BUS-106-distribution-physics.md

This makes every filename globally unique while preserving the numeric prefix for
backward-compatible references ("Protocol 106" still finds the file, but the domain
prefix disambiguates).

Usage:
    python3 rename_protocols.py --dry-run   # Preview changes
    python3 rename_protocols.py --execute    # Apply changes
"""

import sys
from pathlib import Path

# Domain → 3-letter prefix mapping
DOMAIN_PREFIXES = {
    "acquisition":       "ACQ",
    "architecture":      "ARC",
    "archive":           "ARX",  # skip renaming — these are already archived
    "business":          "BUS",
    "case-studies":      "CST",
    "coding":            "COD",
    "communication":     "COM",
    "community":         "CMY",
    "content":           "CNT",
    "creation":          "CRE",
    "decision":          "DEC",
    "design":            "DES",
    "diagnostics":       "DIA",
    "economics":         "ECO",
    "engineering":       "ENG",
    "finance":           "FIN",
    "health":            "HLT",
    "leadership":        "LDR",
    "learning":          "LRN",
    "maintenance":       "MNT",
    "marketing":         "MKT",
    "memory":            "MEM",
    "meta":              "MTA",
    "pattern-detection": "PAT",
    "psychology":        "PSY",
    "quality":           "QAL",
    "reasoning":         "RSN",
    "research":          "RSC",
    "safety":            "SAF",
    "singapore":         "SGP",
    "social":            "SOC",
    "strategy":          "STR",
    "trading":           "TRD",
    "verification":      "VER",
    "workflow":          "WFL",
}

SKIP_DOMAINS = {"archive"}  # Don't rename archived files

PROTOCOLS_ROOT = Path(".agent/skills/protocols")


def collect_renames(root: Path) -> list[tuple[Path, Path]]:
    """Collect all (old_path, new_path) pairs."""
    renames = []
    for domain_dir in sorted(root.iterdir()):
        if not domain_dir.is_dir():
            continue
        domain_name = domain_dir.name
        if domain_name in SKIP_DOMAINS:
            continue
        prefix = DOMAIN_PREFIXES.get(domain_name)
        if not prefix:
            print(f"  ⚠️  No prefix mapping for domain '{domain_name}' — SKIPPING")
            continue

        for md_file in sorted(domain_dir.glob("*.md")):
            old_name = md_file.name
            # Skip files that already have a domain prefix
            if old_name[:3].isupper() and old_name[3] == "-":
                continue
            new_name = f"{prefix}-{old_name}"
            renames.append((md_file, md_file.parent / new_name))
    return renames


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--execute"):
        print(__doc__)
        sys.exit(1)

    dry_run = sys.argv[1] == "--dry-run"
    renames = collect_renames(PROTOCOLS_ROOT)

    if not renames:
        print("No renames needed — all files already have domain prefixes.")
        return

    # Stats
    collisions_before = count_collisions(PROTOCOLS_ROOT)

    print(f"{'DRY RUN' if dry_run else 'EXECUTING'}: {len(renames)} renames")
    print(f"Collisions before: {collisions_before}")
    print()

    for old_path, new_path in renames:
        rel_old = old_path.relative_to(PROTOCOLS_ROOT)
        rel_new = new_path.relative_to(PROTOCOLS_ROOT)
        if dry_run:
            print(f"  {rel_old}  →  {rel_new}")
        else:
            old_path.rename(new_path)
            print(f"  ✅ {rel_old}  →  {rel_new}")

    if not dry_run:
        collisions_after = count_collisions(PROTOCOLS_ROOT)
        print(f"\nCollisions after: {collisions_after}")
        print(f"Resolved: {collisions_before - collisions_after}")


def count_collisions(root: Path) -> int:
    """Count how many numeric prefixes map to more than one file."""
    import re
    from collections import Counter

    prefixes = []
    for md_file in root.rglob("*.md"):
        name = md_file.name
        # Extract numeric prefix (skip domain prefix if present)
        match = re.match(r'(?:[A-Z]{3}-)?(\d+)', name)
        if match:
            prefixes.append(match.group(1))

    counter = Counter(prefixes)
    return sum(count - 1 for count in counter.values() if count > 1)


if __name__ == "__main__":
    main()
