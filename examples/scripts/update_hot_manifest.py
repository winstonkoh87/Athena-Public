#!/usr/bin/env python3
"""
update_hot_manifest.py
======================
Analyzes recent activity to update hot_manifest.json with the most relevant files.
Restored and Upgraded for v8.2-Stable.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".context" / "cache" / "hot_manifest.json"

# Core files that should ALWAYS be in the manifest (v8.2 Updated)
CORE_FILES = [
    {
        "name": "Core_Identity.md",
        "path": ".framework/v8.2-stable/modules/Core_Identity.md",
        "purpose": "Core laws and identity",
    },
    {
        "name": "project_state.md",
        "path": ".context/project_state.md",
        "purpose": "Current task and state",
    },
    {
        "name": "SKILL_INDEX.md",
        "path": ".agent/SKILL_INDEX.md",
        "purpose": "Skill registration",
    },
]


def get_recent_files(limit=5):
    """Finds recently modified markdown files in .agent and .context."""
    files = []
    search_dirs = [
        PROJECT_ROOT / ".agent" / "skills" / "protocols",
        PROJECT_ROOT / ".context" / "memories" / "session_logs",
        PROJECT_ROOT / ".framework" / "v8.2-stable" / "modules",
    ]

    all_files = []
    for d in search_dirs:
        if d.exists():
            for f in d.glob("**/*.md"):
                # Skip archive folders
                if "archive" in str(f):
                    continue
                all_files.append((f, f.stat().st_mtime))

    # Sort by mtime descending
    all_files.sort(key=lambda x: x[1], reverse=True)

    for f, _ in all_files[:limit]:
        try:
            rel_path = f.relative_to(PROJECT_ROOT)
            files.append(
                {
                    "name": f.name,
                    "path": str(rel_path),
                    "purpose": "Recent activity prefetch",
                }
            )
        except ValueError:
            pass  # Skip if not relative to root

    return files


def main():
    print("🔄 Updating hot_manifest.json (v8.2-Stable)...")

    # Start with core files
    manifest_files = list(CORE_FILES)

    # Add recent files
    recent = get_recent_files(limit=7)

    # Avoid duplicates
    existing_paths = {f["path"] for f in manifest_files}
    for r in recent:
        if r["path"] not in existing_paths:
            manifest_files.append(r)
            existing_paths.add(r["path"])

    manifest = {
        "version": "1.2",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "description": "Dynamic hot files prefetched for instant context loading. (v8.2 Optimized)",
        "files": manifest_files,
    }

    # Ensure cache dir exists
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"✅ Manifest updated with {len(manifest_files)} files.")
    for f in manifest_files:
        print(f"   - {f['name']}")


if __name__ == "__main__":
    main()
