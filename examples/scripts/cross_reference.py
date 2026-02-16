#!/usr/bin/env python3
"""
Cross-Reference Audit Script v2.0
===================================
Post-GraphRAG version: Bidirectional link enforcement REMOVED.
With TAG_INDEX + Knowledge Graph, semantic connections are inferred.

Now only checks:
1. Broken links (link points to non-existent file)
2. Tag-connection status (confirms semantic clustering is working)

Usage: python3 cross_reference.py
"""

import os
import re
from collections import defaultdict
from urllib.parse import unquote

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directories to scan
SCAN_DIRS = [
    os.path.join(PROJECT_ROOT, ".context"),
    os.path.join(PROJECT_ROOT, ".agent"),
    os.path.join(PROJECT_ROOT, ".framework"),
]

# Tag index path
TAG_INDEX_PATH = os.path.join(PROJECT_ROOT, ".context", "TAG_INDEX.md")

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def log(level, message):
    colors = {"INFO": GREEN, "WARN": YELLOW, "ERROR": RED, "SUGGEST": CYAN}
    color = colors.get(level, RESET)
    print(f"{color}[{level}]{RESET} {message}")


def parse_tag_index():
    """Parse TAG_INDEX.md to build file → tags mapping."""
    file_to_tags = defaultdict(set)
    
    if not os.path.exists(TAG_INDEX_PATH):
        return file_to_tags
    
    try:
        with open(TAG_INDEX_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse the Reverse Index section (File → Tags)
        reverse_pattern = re.compile(r'\|\s*`([^`]+\.md)`\s*\|\s*([^|]+)\|')
        
        for match in reverse_pattern.finditer(content):
            filename = match.group(1)
            tags_str = match.group(2)
            tags = re.findall(r'#([\w-]+)', tags_str)
            
            for tag in tags:
                file_to_tags[filename].add(tag)
                
    except Exception as e:
        log("WARN", f"Could not parse TAG_INDEX: {e}")
    
    return file_to_tags


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


def normalize_path(path, source_dir):
    """Normalize a path for comparison."""
    # Handle file:// prefix
    if path.startswith("file://"):
        path = path.replace("file://", "")
    # URL decode
    path = unquote(path)
    # Remove anchors
    path = path.split('#')[0].strip()
    
    if not path:
        return None
    
    # Handle relative paths
    if not os.path.isabs(path):
        path = os.path.join(source_dir, path)
    
    # Resolve to absolute
    path = os.path.abspath(path)
    return path


def check_links(md_files):
    """Check all links for broken references."""
    broken_links = []
    valid_links = 0
    
    link_pattern = re.compile(r'\[.*?\]\((?!http|mailto)(.*?)\)')
    
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            source_dir = os.path.dirname(file_path)
            matches = link_pattern.findall(content)
            
            for link in matches:
                if not link.strip():
                    continue
                    
                normalized = normalize_path(link, source_dir)
                if normalized:
                    if os.path.exists(normalized):
                        valid_links += 1
                    else:
                        broken_links.append((file_path, link, normalized))
                        
        except Exception as e:
            log("ERROR", f"Could not read {file_path}: {e}")
    
    return broken_links, valid_links


def count_tagged_files(file_to_tags, md_files):
    """Count how many files are covered by TAG_INDEX."""
    from fnmatch import fnmatch
    
    tagged_count = 0
    
    for file_path in md_files:
        basename = os.path.basename(file_path)
        for pattern in file_to_tags.keys():
            if '*' in pattern or '?' in pattern:
                if fnmatch(basename, pattern):
                    tagged_count += 1
                    break
            elif basename == pattern:
                tagged_count += 1
                break
    
    return tagged_count


def relative_path(path):
    """Convert absolute path to relative from PROJECT_ROOT."""
    return os.path.relpath(path, PROJECT_ROOT)


def main():
    print("=" * 70)
    print("  CROSS-REFERENCE AUDIT v2.0 (Post-GraphRAG)  ")
    print("=" * 70)
    print(f"{CYAN}Note: Bidirectional link enforcement removed.{RESET}")
    print(f"{CYAN}Semantic connections now handled by TAG_INDEX + Knowledge Graph.{RESET}\n")
    
    # Get all markdown files
    md_files = get_all_md_files()
    log("INFO", f"Found {len(md_files)} markdown files to analyze.")
    
    # Parse TAG_INDEX
    file_to_tags = parse_tag_index()
    tagged_count = count_tagged_files(file_to_tags, md_files)
    tag_coverage = (tagged_count / len(md_files)) * 100 if md_files else 0
    
    if file_to_tags:
        log("INFO", f"TAG_INDEX coverage: {tagged_count}/{len(md_files)} files ({tag_coverage:.1f}%)")
    else:
        log("WARN", "TAG_INDEX not found or empty.")
    
    # Check for broken links
    print("\n--- BROKEN LINKS CHECK ---")
    broken_links, valid_links = check_links(md_files)
    
    if broken_links:
        for source, link, normalized in broken_links:
            log("ERROR", f"{relative_path(source)}")
            log("ERROR", f"  ↳ Broken: {link}")
        print(f"\n{RED}Found {len(broken_links)} broken links.{RESET}")
    else:
        log("INFO", f"All {valid_links} internal links are valid. ✓")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"\n{GREEN}SUMMARY:{RESET}")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  TAG_INDEX coverage: {tag_coverage:.1f}%")
    print(f"  Valid links: {valid_links}")
    print(f"  Broken links: {len(broken_links)}")
    
    if broken_links:
        print(f"\n{RED}⚠️ Fix broken links before commit.{RESET}")
    else:
        print(f"\n{GREEN}✓ All checks passed.{RESET}")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
