#!/usr/bin/env python3
"""
athena.tools.public_sync
=======================
Automated Dependency-Aware Deployment to Athena-Public.
Parses links, follows dependencies, sanitizes content.
"""

import os
import re
import shutil
import argparse
import sys
from pathlib import Path
from typing import Set, List

# Fix sys.path for SDK access
SDK_PATH = Path(__file__).resolve().parent.parent.parent
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

# SDK Imports
from athena.core.config import PROJECT_ROOT


# Config
PUBLIC_REPO_ROOT = PROJECT_ROOT / "Athena-Public"
PUBLIC_DOCS = PUBLIC_REPO_ROOT / "docs"


# Maps private directories to public ones
PATH_MAP = {
    ".agent/skills/protocols": PUBLIC_DOCS / "protocols",
    ".agent/workflows": PUBLIC_DOCS / "workflows",
    ".context/memories/case_studies": PUBLIC_DOCS / "case-studies",
    ".framework": PUBLIC_DOCS / "framework",
}


# Patterns
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\((file:///Users/[AUTHOR]/Desktop/Project%20Athena/([^\)]+))\)')

class SyncOrchestrator:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.visited = set()
        self.to_sync = set()

    def find_dependencies(self, file_path: Path):
        """Recursively find all linked .md files within the workspace."""
        if file_path in self.visited or not file_path.exists():
            return
        
        self.visited.add(file_path)
        self.to_sync.add(file_path)
        
        content = file_path.read_text(encoding="utf-8")
        matches = LINK_PATTERN.findall(content)
        
        for label, full_url, rel_path in matches:
            # rel_path is like '.agent/skills/protocols/272-fear-based-advertising.md'
            decoded_rel = rel_path.replace('%20', ' ')
            dep_path = (PROJECT_ROOT / decoded_rel).resolve()
            
            if dep_path.suffix == ".md":
                self.find_dependencies(dep_path)

    def sanitize_content(self, content: str, source_file: Path) -> str:
        """Replace absolute file:/// links with relative docs links and strip PII."""
        
        def replace_link(match):
            label = match.group(1)
            rel_path = match.group(3).replace('%20', ' ')
            
            # Determine public destination based on MAP
            dest_dir = None
            found_key = None
            for key, public_path in PATH_MAP.items():
                if rel_path.startswith(key):
                    dest_dir = public_path
                    found_key = key
                    break
            
            if not dest_dir:
                return f"[{label}](INTERNAL_LINK_REDACTED)"
            
            # Calculate relative path in public repo
            # We assume all public files are in docs/* subfolders
            # This is a simplification; a more robust version would use os.path.relpath
            filename = os.path.basename(rel_path)
            subfolder = dest_dir.name
            return f"[{label}](../{subfolder}/{filename})"

        # 1. Links
        content = LINK_PATTERN.sub(replace_link, content)
        
        # 2. PII / Specifics (Placeholder for more robust rules)
        # Replaces common PII patterns if found
        content = content.replace("[AUTHOR]", "[Creator]")
        
        return content

    def execute_sync(self):
        """Perform the actual file operations."""
        print(f"🔄 Syncing {len(self.to_sync)} files to {PUBLIC_REPO_ROOT.name}...")
        
        for source in self.to_sync:
            # Find destination
            rel_source = source.relative_to(PROJECT_ROOT)
            dest = None
            
            for key, public_path in PATH_MAP.items():
                if str(rel_source).startswith(key):
                    dest = public_path / source.name
                    break
            
            if not dest:
                # Skip files outside our map (e.g. system files)
                continue
                
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                content = source.read_text(encoding="utf-8")
                sanitized = self.sanitize_content(content, source)
                dest.write_text(sanitized, encoding="utf-8")
                print(f"  ✅ Published: {dest.relative_to(PUBLIC_REPO_ROOT)}")
            else:
                print(f"  [DRY] Would publish: {dest.relative_to(PUBLIC_REPO_ROOT)}")

def main():
    parser = argparse.ArgumentParser(description="Athena Public Sync (Dependency Aware)")
    parser.add_argument("files", nargs="+", help="Files to sync")
    parser.add_argument("--dry-run", action="store_true", help="Preview sync")
    args = parser.parse_args()

    orchestrator = SyncOrchestrator(dry_run=args.dry_run)
    
    for f in args.files:
        path = Path(f).resolve()
        orchestrator.find_dependencies(path)
        
    orchestrator.execute_sync()

if __name__ == "__main__":
    main()
