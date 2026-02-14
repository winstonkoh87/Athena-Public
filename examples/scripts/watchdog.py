#!/usr/bin/env python3
"""
Codex Watchdog
Monitors file sizes and alerts on potential bloat issues.
Run periodically or on /start to catch problems early.
"""

import os
import sys

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thresholds (in tokens, estimated as chars/4)
THRESHOLDS = {
    "warning": 8000,    # Yellow alert
    "critical": 15000,  # Red alert
    "danger": 25000,    # Action required
}

# Files to monitor (relative paths)
MONITORED_FILES = [
    ".agent/skills/SKILL_INDEX.md",
    ".framework/v7.0/modules/Core_Identity.md",
    ".framework/v7.0/Output_Standards.md",
    ".context/profile/User_Profile.md",
    ".context/profile/Constraints_Master.md",
    ".context/System_Manifest.md",
]

# Directories to scan for large files
SCAN_DIRS = [
    ".context/memories/session_logs",
    ".context/memories/case_studies",
    ".agent/skills/protocols",
]

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def estimate_tokens(filepath):
    """Estimates token count from file size."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return len(content) // 4
    except Exception:
        return 0


def get_status(tokens):
    """Returns status emoji and color based on token count."""
    if tokens >= THRESHOLDS["danger"]:
        return "🔴", RED, "DANGER"
    elif tokens >= THRESHOLDS["critical"]:
        return "🟠", RED, "CRITICAL"
    elif tokens >= THRESHOLDS["warning"]:
        return "🟡", YELLOW, "WARNING"
    else:
        return "🟢", GREEN, "OK"


def scan_directory(dir_path, top_n=5):
    """Scans directory and returns largest files."""
    results = []
    
    if not os.path.exists(dir_path):
        return results
    
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        if os.path.isfile(filepath) and filename.endswith('.md'):
            tokens = estimate_tokens(filepath)
            results.append((filename, tokens, filepath))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def main():
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}              🔍 CODEX WATCHDOG                                 {RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    issues_found = 0
    
    # Check core files
    print(f"{BOLD}Core Files:{RESET}\n")
    
    for rel_path in MONITORED_FILES:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        filename = os.path.basename(rel_path)
        
        if not os.path.exists(full_path):
            print(f"  {YELLOW}?{RESET} {filename}: Not found")
            continue
        
        tokens = estimate_tokens(full_path)
        emoji, color, status = get_status(tokens)
        
        if status != "OK":
            issues_found += 1
        
        status_str = f"{color}{status}{RESET}" if status != "OK" else f"{DIM}{status}{RESET}"
        print(f"  {emoji} {filename:<35} │ {tokens:>6,} tokens  [{status_str}]")
    
    print()
    
    # Scan directories for large files
    print(f"{BOLD}Directory Scans (Top 3 per directory):{RESET}\n")
    
    for rel_dir in SCAN_DIRS:
        full_dir = os.path.join(PROJECT_ROOT, rel_dir)
        dir_name = os.path.basename(rel_dir)
        
        results = scan_directory(full_dir, top_n=3)
        
        if not results:
            print(f"  {DIM}📁 {dir_name}: Empty or not found{RESET}")
            continue
        
        print(f"  📁 {dir_name}/")
        for filename, tokens, _ in results:
            emoji, color, status = get_status(tokens)
            if status != "OK":
                issues_found += 1
                print(f"     {emoji} {filename:<30} │ {tokens:>6,} tokens  [{color}{status}{RESET}]")
            else:
                print(f"     {emoji} {filename:<30} │ {tokens:>6,} tokens")
        print()
    
    # Summary
    print(f"{DIM}{'─' * 60}{RESET}")
    
    if issues_found == 0:
        print(f"\n{GREEN}✓ All clear. No bloat detected.{RESET}\n")
    else:
        print(f"\n{YELLOW}⚠️  {issues_found} file(s) exceeding thresholds.{RESET}")
        print(f"{DIM}Consider:{RESET}")
        print(f"  • Trimming verbose content")
        print(f"  • Moving details to separate files")
        print(f"  • Running compress_session.py for old logs\n")
    
    # Threshold legend
    print(f"{DIM}Thresholds: 🟢 <{THRESHOLDS['warning']:,} │ 🟡 <{THRESHOLDS['critical']:,} │ 🟠 <{THRESHOLDS['danger']:,} │ 🔴 ≥{THRESHOLDS['danger']:,} tokens{RESET}\n")
    
    return issues_found


if __name__ == "__main__":
    issues = main()
    sys.exit(1 if issues > 0 else 0)
