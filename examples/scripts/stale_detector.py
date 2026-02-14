#!/usr/bin/env python3
"""
Stale Detector Script
=====================
Scans all markdown files and identifies "stale" files — those not modified
in the last N days. Stale files may contain outdated information.

Usage: python3 stale_detector.py [--days=30]
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_STALE_DAYS = 30

# Directories to scan
SCAN_DIRS = [
    os.path.join(PROJECT_ROOT, ".context"),
    os.path.join(PROJECT_ROOT, ".agent"),
    os.path.join(PROJECT_ROOT, ".framework"),
]

# Exclusions (files that are OK to be stale - reference docs, etc.)
EXCLUSIONS = [
    "README.md",
]

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"
RESET = "\033[0m"


def log(level, message):
    colors = {"INFO": GREEN, "WARN": YELLOW, "ERROR": RED, "STALE": CYAN, "FRESH": GRAY}
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


def get_file_age_days(file_path):
    """Get the age of a file in days since last modification."""
    try:
        mtime = os.path.getmtime(file_path)
        age = time.time() - mtime
        return int(age / 86400)  # Convert seconds to days
    except Exception:
        return -1


def find_stale_files(md_files, stale_days):
    """Find files older than stale_days."""
    stale = []
    fresh = []
    
    for file_path in md_files:
        basename = os.path.basename(file_path)
        if basename in EXCLUSIONS:
            continue
        
        age = get_file_age_days(file_path)
        if age >= stale_days:
            stale.append((file_path, age))
        else:
            fresh.append((file_path, age))
    
    # Sort by age (oldest first)
    stale.sort(key=lambda x: -x[1])
    
    return stale, fresh


def relative_path(path):
    """Convert absolute path to relative from PROJECT_ROOT."""
    return os.path.relpath(path, PROJECT_ROOT)


def format_age(days):
    """Format age in human-readable form."""
    if days == 0:
        return "today"
    elif days == 1:
        return "1 day ago"
    elif days < 30:
        return f"{days} days ago"
    elif days < 60:
        return "~1 month ago"
    elif days < 365:
        months = days // 30
        return f"~{months} months ago"
    else:
        years = days // 365
        return f"~{years} year(s) ago"


def main():
    # Parse arguments
    stale_days = DEFAULT_STALE_DAYS
    for arg in sys.argv[1:]:
        if arg.startswith("--days="):
            try:
                stale_days = int(arg.split("=")[1])
            except ValueError:
                pass
    
    print("=" * 70)
    print("  STALE DETECTOR (BIONIC)  ")
    print("=" * 70)
    print(f"  Threshold: {stale_days} days")
    print("=" * 70)
    
    # Get all markdown files
    md_files = get_all_md_files()
    log("INFO", f"Scanning {len(md_files)} markdown files...")
    
    # Find stale files
    stale, fresh = find_stale_files(md_files, stale_days)
    
    print(f"\n--- STALE FILES (>{stale_days} days old) ---")
    
    if stale:
        for file_path, age in stale:
            log("STALE", f"{relative_path(file_path)} ({format_age(age)})")
        
        print(f"\n{YELLOW}Total: {len(stale)} stale files found.{RESET}")
        print(f"\n{CYAN}Action: Review these files and either:")
        print(f"  - Update them with current information")
        print(f"  - Archive/delete if no longer relevant{RESET}")
    else:
        log("INFO", f"No stale files found. All files updated within {stale_days} days. ✓")
    
    print("\n" + "=" * 70)
    print(f"\n{GREEN}SUMMARY:{RESET}")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Stale (>{stale_days}d): {len(stale)}")
    print(f"  Fresh (<{stale_days}d): {len(fresh)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
