#!/usr/bin/env python3
"""
Case Study ID Remediation Script
Renames duplicate CS-XXX files to unique IDs starting from CS-400.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

CASE_STUDY_DIR = Path(".context/memories/case_studies")
START_NEW_ID = 400


def main():
    # Find all case study files
    cs_files = list(CASE_STUDY_DIR.glob("CS-*.md"))

    # Group by ID
    id_to_files = defaultdict(list)
    pattern = re.compile(r"^CS-(\d+)-(.+\.md)$")

    for f in cs_files:
        match = pattern.match(f.name)
        if match:
            cs_id = int(match.group(1))
            suffix = match.group(2)
            id_to_files[cs_id].append((f, suffix))

    # Find collisions (IDs with more than one file)
    collisions = {k: v for k, v in id_to_files.items() if len(v) > 1}

    print(f"Found {len(collisions)} ID collisions")

    # Assign new IDs
    new_id = START_NEW_ID
    renames = []

    for old_id, files in sorted(collisions.items()):
        # Keep the first file with original ID, rename the rest
        for filepath, suffix in files[1:]:
            new_name = f"CS-{new_id:03d}-{suffix}"
            new_path = CASE_STUDY_DIR / new_name
            renames.append((filepath, new_path))
            print(f"Rename: {filepath.name} -> {new_name}")
            new_id += 1

    print(f"\nTotal renames: {len(renames)}")
    print("\nExecuting renames...")

    for old_path, new_path in renames:
        old_path.rename(new_path)
        print(f"✓ {old_path.name} -> {new_path.name}")

    print("\n✅ Remediation complete!")


if __name__ == "__main__":
    main()
