#!/usr/bin/env python3
"""
repair_case_study_links.py
Universal repair of case study links by suffix matching.
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("/Users/[AUTHOR]/Desktop/Project Athena")
CS_DIR = PROJECT_ROOT / ".context/memories/case_studies"


def main():
    # 1. Map current files by their 'suffix' (everything after the ID)
    suffix_to_current = {}
    pattern = re.compile(r"^CS-\d+-(.+)$")

    for f in CS_DIR.glob("CS-*.md"):
        match = pattern.match(f.name)
        if match:
            suffix = match.group(1)
            suffix_to_current[suffix] = f.name

    print(f"Mapped {len(suffix_to_current)} unique case study suffixes.")

    # 2. Universal Pattern for any CS-XXX reference
    # Matches CS-001-name.md
    cs_ref_pattern = re.compile(r"CS-\d+-(.+?\.md)")

    total_files_corrected = 0
    total_refs_corrected = 0

    # We scan all .md files in the whole PROJECT_ROOT/.context
    CONTEXT_DIR = PROJECT_ROOT / ".context"

    for md_file in CONTEXT_DIR.rglob("*.md"):
        content = md_file.read_text()

        def replace_fn(match):
            old_full_name = match.group(0)
            suffix = match.group(1)
            if suffix in suffix_to_current:
                current_full_name = suffix_to_current[suffix]
                if old_full_name != current_full_name:
                    print(f"[{md_file.name}] {old_full_name} -> {current_full_name}")
                    return current_full_name
            return old_full_name

        new_content = cs_ref_pattern.sub(replace_fn, content)

        if new_content != content:
            md_file.write_text(new_content)
            total_files_corrected += 1
            # Simple count of changes
            total_refs_corrected += len(re.findall(cs_ref_pattern, content)) - len(
                re.findall(cs_ref_pattern, new_content)
            )  # This is an approximation

    print(f"\nRepair complete.")
    print(f"Files corrected: {total_files_corrected}")


if __name__ == "__main__":
    main()
