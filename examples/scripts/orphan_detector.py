#!/usr/bin/env python3
"""
Orphan Detector Script
======================
Scans all markdown files and identifies "orphans" — files with zero inbound links.
These are files that exist but are never referenced, making them invisible.

Usage: python3 orphan_detector.py

Config: .agent/config/orphan_exclusions.yaml
"""

import os
import re
from collections import defaultdict
from urllib.parse import unquote
from pathlib import Path

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = Path(PROJECT_ROOT) / ".agent" / "config" / "orphan_exclusions.yaml"

# Directories to scan
SCAN_DIRS = [
    os.path.join(PROJECT_ROOT, ".context"),
    os.path.join(PROJECT_ROOT, ".agent"),
    os.path.join(PROJECT_ROOT, ".framework"),
]


def load_exclusions() -> tuple[list[str], list[str]]:
    """Load exclusions from YAML config or use defaults."""
    # Default exclusions (fallback if config doesn't exist)
    default_files = [
        "README.md",
        "SKILL_INDEX.md",
        "System_Manifest.md",
        "User_Profile.md",
        "Core_Identity.md",
        "Output_Standards.md",
        "Constraints_Master.md",
        "TAG_INDEX.md",
        "WORKFLOW_INDEX.md",
    ]
    default_dirs = [
        "session_logs",
        "journals",
        "graphrag_env",
        "cache",
        "archive",
        "__pycache__",
    ]
    
    if CONFIG_FILE.exists():
        try:
            import yaml
            config = yaml.safe_load(CONFIG_FILE.read_text())
            return (
                config.get("entry_points", default_files),
                config.get("excluded_dirs", default_dirs)
            )
        except ImportError:
            pass  # yaml not installed, use defaults
        except Exception:
            pass  # config parse error, use defaults
    
    return default_files, default_dirs


EXCLUSIONS, EXCLUDED_DIRS = load_exclusions()

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def log(level, message):
    colors = {"INFO": GREEN, "WARN": YELLOW, "ERROR": RED, "ORPHAN": CYAN}
    color = colors.get(level, RESET)
    print(f"{color}[{level}]{RESET} {message}")


def get_all_md_files():
    """Recursively find all .md files in scan directories."""
    md_files = []
    for root_dir in SCAN_DIRS:
        if not os.path.exists(root_dir):
            continue
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
    return md_files


def normalize_path(path):
    """Normalize a path for comparison."""
    if path.startswith("file://"):
        path = path.replace("file://", "")
    path = unquote(path)
    path = path.split('#')[0].strip()
    if path and os.path.exists(path):
        path = os.path.abspath(path)
    return path


def extract_links(file_path):
    """Extract all markdown links and table path references from a file."""
    # Pattern 1: Standard markdown links [text](path)
    link_pattern = re.compile(r'\[.*?\]\((?!http|mailto)(.*?)\)')
    # Pattern 2: Backtick paths in tables like | col | `path/to/file.md` | col |
    table_path_pattern = re.compile(r'`([^`]+\.md)`')
    # Pattern 3: Shorthand protocol paths like `protocols/01-name.md`
    protocol_shorthand = re.compile(r'`(protocols/[^`]+\.md)`')
    
    links = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract markdown links
        matches = link_pattern.findall(content)
        for link in matches:
            normalized = normalize_path(link)
            if normalized:
                # Resolve relative to file
                abs_link = os.path.normpath(os.path.join(os.path.dirname(file_path), normalized))
                if os.path.exists(abs_link):
                    links.append(abs_link)
                # Fallback: check relative to root
                elif os.path.exists(os.path.join(PROJECT_ROOT, normalized)):
                    links.append(os.path.join(PROJECT_ROOT, normalized))
        
        # Extract table path references
        table_matches = table_path_pattern.findall(content)
        for path in table_matches:
            # 1. Try relative to file
            abs_path = os.path.normpath(os.path.join(os.path.dirname(file_path), path))
            if os.path.exists(abs_path):
                links.append(abs_path)
                continue
            
            # 2. Try relative to project root
            root_path = os.path.join(PROJECT_ROOT, path)
            if os.path.exists(root_path):
                links.append(root_path)
                continue
            
            # 3. Try removing leading dot if present (e.g. .agent -> agent)
            if path.startswith("."):
                 root_path_clean = os.path.join(PROJECT_ROOT, path.lstrip("./"))
                 if os.path.exists(root_path_clean):
                     links.append(root_path_clean)

        # Extract shorthand protocol references (expand to full path)
        protocol_matches = protocol_shorthand.findall(content)
        for path in protocol_matches:
            full_path = os.path.join(PROJECT_ROOT, ".agent", "skills", path)
            if os.path.exists(full_path):
                links.append(os.path.abspath(full_path))
                
    except Exception as e:
        log("ERROR", f"Could not read {file_path}: {e}")
    
    return links


def find_orphans(md_files):
    """Find files that have no inbound links."""
    # Build inbound link map
    inbound_count = defaultdict(int)
    
    # Initialize all files with 0 inbound
    for f in md_files:
        inbound_count[os.path.abspath(f)] = 0
    
    # Count inbound links
    for file_path in md_files:
        links = extract_links(file_path)
        for link in links:
            if link in inbound_count:
                inbound_count[link] += 1
    
    # Find orphans (0 inbound)
    orphans = []
    for file_path, count in inbound_count.items():
        if count == 0:
            basename = os.path.basename(file_path)
            # Check basename exclusion
            if basename in EXCLUSIONS:
                continue
            # Check directory exclusion
            if any(excluded_dir in file_path for excluded_dir in EXCLUDED_DIRS):
                continue
            orphans.append(file_path)
    
    return orphans


def relative_path(path):
    """Convert absolute path to relative from PROJECT_ROOT."""
    return os.path.relpath(path, PROJECT_ROOT)


def main():
    print("=" * 70)
    print("  ORPHAN DETECTOR (BIONIC)  ")
    print("=" * 70)
    
    # Get all markdown files
    md_files = get_all_md_files()
    log("INFO", f"Scanning {len(md_files)} markdown files...")
    
    # Find orphans
    orphans = find_orphans(md_files)
    
    print("\n--- ORPHAN FILES (Zero Inbound Links) ---")
    
    if orphans:
        for orphan in sorted(orphans):
            log("ORPHAN", f"{relative_path(orphan)}")
        
        print(f"\n{YELLOW}Total: {len(orphans)} orphan files found.{RESET}")
        print(f"\n{CYAN}Action: Consider linking these files from relevant documents,")
        print(f"or archive them if they are no longer needed.{RESET}")
    else:
        log("INFO", "No orphan files found. All files are connected. ✓")
    
    print("\n" + "=" * 70)
    print(f"\n{GREEN}SUMMARY:{RESET}")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Orphans found: {len(orphans)}")
    print(f"  Exclusions: {len(EXCLUSIONS)} (entry point files)")
    print("=" * 70)


if __name__ == "__main__":
    main()
