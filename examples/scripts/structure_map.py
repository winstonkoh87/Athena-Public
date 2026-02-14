#!/usr/bin/env python3
"""
structure_map.py — Workspace Structure Actuator (v2.0)

Upgraded from passive visualizer to active actuator.
Detects anomalies and can execute recommended fixes.

Features:
- Visual tree structure with annotations
- Anomaly detection (stale, heavy, orphan, empty)
- Actionable recommendations
- Auto-fix mode (--fix)
- JSON report mode (--json)

Usage:
    python3 .agent/scripts/structure_map.py              # Visualize + diagnose
    python3 .agent/scripts/structure_map.py --diagnose   # Show recommendations only
    python3 .agent/scripts/structure_map.py --fix        # Execute safe fixes
    python3 .agent/scripts/structure_map.py --json       # JSON report for CI
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# === Configuration ===
ROOT_DIR = Path.cwd()
ARCHIVE_DIR = ROOT_DIR / ".archive"
IGNORE_DIRS = {
    ".git", "__pycache__", ".DS_Store", "node_modules", "venv", ".venv", 
    "env", ".idea", ".vscode", ".archive"
}
IGNORE_FILES = {".DS_Store"}

# Thresholds
HEAVY_SIZE_MB = 5.0
STALE_DAYS = 60
VERY_STALE_DAYS = 180
EMPTY_DIR_THRESHOLD = 0  # Dirs with 0 files

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"
MAGENTA = "\033[95m"


# === Anomaly Detection ===

def get_size_and_count(path: Path) -> tuple[int, int]:
    """Recursively get total size (bytes) and file count."""
    total_size = 0
    file_count = 0
    try:
        if path.is_file():
            return path.stat().st_size, 1
        for p in path.iterdir():
            if p.name in IGNORE_DIRS or p.name in IGNORE_FILES:
                continue
            s, c = get_size_and_count(p)
            total_size += s
            file_count += c
    except (PermissionError, FileNotFoundError):
        pass
    return total_size, file_count


def get_age_days(path: Path) -> Optional[float]:
    """Get file/dir age in days."""
    try:
        return (time.time() - path.stat().st_mtime) / (24 * 3600)
    except Exception:
        return None


def detect_anomalies(directory: Path) -> list[dict]:
    """Scan for all anomalies in workspace."""
    anomalies = []
    
    def scan(path: Path):
        try:
            for entry in path.iterdir():
                if entry.name in IGNORE_DIRS or entry.name in IGNORE_FILES:
                    continue
                
                rel_path = str(entry.relative_to(ROOT_DIR))
                
                if entry.is_dir():
                    size, count = get_size_and_count(entry)
                    size_mb = size / (1024 * 1024)
                    age = get_age_days(entry)
                    
                    # Heavy directory
                    if size_mb > HEAVY_SIZE_MB:
                        anomalies.append({
                            "type": "heavy",
                            "path": rel_path,
                            "size_mb": round(size_mb, 2),
                            "action": "compress_or_archive",
                            "severity": "warning" if size_mb < 20 else "critical"
                        })
                    
                    # Empty directory
                    if count == EMPTY_DIR_THRESHOLD:
                        anomalies.append({
                            "type": "empty",
                            "path": rel_path,
                            "action": "delete",
                            "severity": "info"
                        })
                    
                    # Stale cluster (all children stale)
                    if age and age > VERY_STALE_DAYS:
                        anomalies.append({
                            "type": "stale_cluster",
                            "path": rel_path,
                            "age_days": int(age),
                            "action": "archive",
                            "severity": "warning"
                        })
                    
                    scan(entry)
                    
                else:  # File
                    age = get_age_days(entry)
                    size = entry.stat().st_size
                    
                    # Very stale file
                    if age and age > VERY_STALE_DAYS:
                        anomalies.append({
                            "type": "stale_file",
                            "path": rel_path,
                            "age_days": int(age),
                            "action": "review_or_archive",
                            "severity": "info"
                        })
                    
                    # Large file
                    size_mb = size / (1024 * 1024)
                    if size_mb > HEAVY_SIZE_MB:
                        anomalies.append({
                            "type": "heavy_file",
                            "path": rel_path,
                            "size_mb": round(size_mb, 2),
                            "action": "compress_or_gitignore",
                            "severity": "warning"
                        })
                        
        except PermissionError:
            pass
    
    scan(directory)
    return anomalies


# === Actions (Actuators) ===

def archive_path(path: Path, dry_run: bool = False) -> bool:
    """Move path to .archive with timestamp."""
    try:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = ARCHIVE_DIR / f"{path.name}_{timestamp}"
        
        if dry_run:
            print(f"  [DRY RUN] Would archive: {path} → {dest}")
            return True
        
        shutil.move(str(path), str(dest))
        print(f"  {GREEN}✓ Archived:{RESET} {path} → {dest}")
        return True
    except Exception as e:
        print(f"  {RED}✗ Failed:{RESET} {e}")
        return False


def delete_empty_dir(path: Path, dry_run: bool = False) -> bool:
    """Delete empty directory."""
    try:
        if dry_run:
            print(f"  [DRY RUN] Would delete empty: {path}")
            return True
        
        path.rmdir()
        print(f"  {GREEN}✓ Deleted empty:{RESET} {path}")
        return True
    except Exception as e:
        print(f"  {RED}✗ Failed:{RESET} {e}")
        return False


def execute_fixes(anomalies: list[dict], dry_run: bool = False):
    """Execute safe auto-fixes for detected anomalies."""
    print(f"\n{BOLD}🔧 Executing Fixes{' (DRY RUN)' if dry_run else ''}{RESET}\n")
    
    fixed = 0
    skipped = 0
    
    for anomaly in anomalies:
        path = ROOT_DIR / anomaly["path"]
        
        if anomaly["type"] == "empty":
            if delete_empty_dir(path, dry_run):
                fixed += 1
            else:
                skipped += 1
                
        elif anomaly["type"] == "stale_cluster" and anomaly["age_days"] > VERY_STALE_DAYS:
            if archive_path(path, dry_run):
                fixed += 1
            else:
                skipped += 1
        else:
            # Other anomalies need manual review
            skipped += 1
    
    print(f"\n{GREEN}Fixed: {fixed}{RESET}, {YELLOW}Skipped (needs review): {skipped}{RESET}")


# === Display ===

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        mb = size_bytes / (1024 * 1024)
        if mb > HEAVY_SIZE_MB:
            return f"{RED}{mb:.1f}MB{RESET}"
        return f"{mb:.1f}MB"


def get_age_status(path: Path) -> str:
    age = get_age_days(path)
    if age is None:
        return ""
    if age > VERY_STALE_DAYS:
        return f"{RED}stale ({int(age)}d){RESET}"
    if age > STALE_DAYS:
        return f"{YELLOW}aging ({int(age)}d){RESET}"
    if age < 1:
        return f"{GREEN}fresh{RESET}"
    return ""


def print_tree(directory: Path, prefix: str = ""):
    """Recursively print directory tree with annotations."""
    try:
        entries = sorted([e for e in directory.iterdir() 
                         if e.name not in IGNORE_DIRS and e.name not in IGNORE_FILES],
                         key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        
        if entry.is_dir():
            size, count = get_size_and_count(entry)
            size_str = format_size(size)
            print(f"{prefix}{connector}{BOLD}{CYAN}{entry.name}/{RESET} {DIM}({count} files, {size_str}){RESET}")
            print_tree(entry, prefix + ("    " if is_last else "│   "))
        else:
            size = entry.stat().st_size
            size_str = format_size(size)
            age_str = get_age_status(entry)
            annot = f"{DIM}{size_str}"
            if age_str:
                annot += f", {age_str}"
            annot += f"{RESET}"
            print(f"{prefix}{connector}{entry.name} {annot}")


def print_recommendations(anomalies: list[dict]):
    """Print actionable recommendations."""
    if not anomalies:
        print(f"\n{GREEN}✓ No anomalies detected. Workspace is clean.{RESET}\n")
        return
    
    print(f"\n{BOLD}📋 Recommendations ({len(anomalies)} issues){RESET}\n")
    
    # Group by severity
    critical = [a for a in anomalies if a["severity"] == "critical"]
    warnings = [a for a in anomalies if a["severity"] == "warning"]
    info = [a for a in anomalies if a["severity"] == "info"]
    
    if critical:
        print(f"{RED}🔴 CRITICAL ({len(critical)}){RESET}")
        for a in critical[:5]:
            print(f"   • [{a['type']}] {a['path']} → {a['action']}")
    
    if warnings:
        print(f"{YELLOW}🟡 WARNING ({len(warnings)}){RESET}")
        for a in warnings[:5]:
            detail = f"{a.get('size_mb', '')}MB" if 'size_mb' in a else f"{a.get('age_days', '')}d"
            print(f"   • [{a['type']}] {a['path']} ({detail}) → {a['action']}")
    
    if info:
        print(f"{DIM}🔵 INFO ({len(info)}){RESET}")
        for a in info[:5]:
            print(f"   {DIM}• [{a['type']}] {a['path']} → {a['action']}{RESET}")
    
    print(f"\n{DIM}Run with --fix to auto-remediate safe issues.{RESET}\n")


def main():
    args = set(sys.argv[1:])
    
    # JSON mode for CI
    if "--json" in args:
        anomalies = detect_anomalies(ROOT_DIR)
        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "root": str(ROOT_DIR),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }, indent=2))
        return
    
    print(f"\n{BOLD}🗺️  Workspace Structure Actuator v2.0{RESET}")
    print(f"{DIM}Root: {ROOT_DIR}{RESET}")
    
    # Detect anomalies
    anomalies = detect_anomalies(ROOT_DIR)
    
    # Fix mode
    if "--fix" in args:
        execute_fixes(anomalies, dry_run=("--dry-run" in args))
        return
    
    # Diagnose only mode
    if "--diagnose" in args:
        print_recommendations(anomalies)
        return
    
    # Default: tree + recommendations
    print()
    print_tree(ROOT_DIR)
    print(f"\n{DIM}Legend: {RED}Heavy (>5MB){RESET}{DIM}, {YELLOW}Aging (>{STALE_DAYS}d){RESET}{DIM}, {RED}Stale (>{VERY_STALE_DAYS}d){RESET}{DIM}, {GREEN}Fresh (<24h){RESET}")
    print_recommendations(anomalies)


if __name__ == "__main__":
    main()
