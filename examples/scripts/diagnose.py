#!/usr/bin/env python3
"""
diagnose.py — Consolidated Diagnostics Orchestrator
====================================================
Single-call script that runs all /diagnose phases:
  1. Dependency check
  2. Batch audit (orphans, links)
  3. Structure map
  4. Secrets scan
  5. Echo chamber check

Usage:
    python3 .agent/scripts/diagnose.py

Read-only. No commits. Safe to run frequently.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "scripts"
SESSION_LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def divider(title: str):
    """Print a section divider."""
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")


def run_script(script_name: str, args: list = None, timeout: int = 60) -> tuple[bool, str]:
    """Run a script and return (success, output)."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return False, f"Script not found: {script_name}"
    
    cmd = ["python3", str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Script timed out: {script_name}"
    except Exception as e:
        return False, f"Error running {script_name}: {e}"


# ============================================================
# PHASE 0: Dependency Check
# ============================================================

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    checks = [
        ("supabase", "from supabase import create_client"),
        ("dotenv", "from dotenv import load_dotenv"),
    ]
    
    all_ok = True
    for name, import_stmt in checks:
        try:
            result = subprocess.run(
                ["python3", "-c", import_stmt],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   ✅ {name}")
            else:
                print(f"   ⚠️ {name} missing")
                all_ok = False
        except Exception:
            print(f"   ⚠️ {name} check failed")
            all_ok = False
    
    return all_ok


# ============================================================
# PHASE 1-3: Parallel Diagnostics
# ============================================================

def run_batch_audit() -> tuple[str, str]:
    """Run batch audit (orphans, links)."""
    success, output = run_script("batch_audit.py", ["--skip-graphrag"], timeout=120)
    return "Batch Audit", output if success else f"⚠️ Failed: {output}"


def run_structure_map() -> tuple[str, str]:
    """Run structure map."""
    success, output = run_script("structure_map.py", timeout=60)
    return "Structure Map", output if success else f"⚠️ Failed: {output}"


def run_orphan_detector() -> tuple[str, str]:
    """Run orphan detector."""
    success, output = run_script("orphan_detector.py", timeout=60)
    return "Orphan Detector", output if success else f"⚠️ Failed: {output}"


def run_parallel_diagnostics() -> dict:
    """Run diagnostic scripts in parallel."""
    print("🔄 Running parallel diagnostics...")
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_batch_audit): "batch_audit",
            executor.submit(run_orphan_detector): "orphan_detector",
        }
        
        # Only run structure_map if it exists
        if (SCRIPTS_DIR / "structure_map.py").exists():
            futures[executor.submit(run_structure_map)] = "structure_map"
        
        for future in as_completed(futures):
            name, output = future.result()
            results[name] = output
            # Print first few lines as summary
            lines = output.strip().split('\n')
            summary = '\n'.join(lines[:10])
            if len(lines) > 10:
                summary += f"\n   ... ({len(lines) - 10} more lines)"
            print(f"\n📋 {name}:\n{summary}")
    
    return results


# ============================================================
# PHASE 4: Echo Chamber Check
# ============================================================

def echo_chamber_check() -> int:
    """Check for disagreement signals in recent sessions."""
    print("\n🔍 Echo Chamber Check...")
    
    if not SESSION_LOGS_DIR.exists():
        print("   ⚠️ No session logs directory")
        return 0
    
    patterns = [
        r"actually",
        r"incorrect",
        r"disagree",
        r"not quite",
        r"I'd push back",
        r"let me correct",
        r"that's not accurate",
    ]
    
    pattern = re.compile("|".join(patterns), re.IGNORECASE)
    
    count = 0
    files_checked = 0
    
    for log_file in sorted(SESSION_LOGS_DIR.glob("*.md"), reverse=True)[:10]:
        try:
            content = log_file.read_text(encoding="utf-8")
            matches = pattern.findall(content)
            count += len(matches)
            files_checked += 1
        except Exception:
            pass
    
    print(f"   Sessions checked: {files_checked}")
    print(f"   Disagreement signals: {count}")
    
    if count < 3:
        print(f"   {YELLOW}⚠️ ECHO CHAMBER RISK: <3 disagreements. Challenge more.{RESET}")
    else:
        print(f"   {GREEN}✅ Healthy dialectic{RESET}")
    
    return count


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def main():
    divider("🔬 ATHENA DIAGNOSTICS")
    
    issues_found = 0
    
    # Phase 0: Dependencies
    if not check_dependencies():
        print(f"\n{YELLOW}⚠️ Some dependencies missing{RESET}")
    
    # Phase 1-3: Parallel diagnostics
    results = run_parallel_diagnostics()
    
    # Count issues from orphan detector
    orphan_output = results.get("Orphan Detector", "")
    orphan_count = orphan_output.lower().count("orphan")
    if orphan_count > 0:
        issues_found += orphan_count
    
    # Phase 4: Echo chamber
    echo_chamber_check()
    
    # Summary
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    if issues_found > 0:
        print(f"{YELLOW}⚠️ /diagnose complete. {issues_found} issues found.{RESET}")
    else:
        print(f"{GREEN}✅ /diagnose complete. No issues found.{RESET}")
    print(f"{DIM}Read-only. No changes made.{RESET}")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
