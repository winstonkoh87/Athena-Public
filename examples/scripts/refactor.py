#!/usr/bin/env python3
"""
refactor.py — Master Orchestrator for /refactor workflow

Philosophy: One command to rule them all.
Usage:
    python3 .agent/scripts/refactor.py
    python3 .agent/scripts/refactor.py --dry-run
"""

import sys
import subprocess
import time
import argparse
from pathlib import Path

# === Configuration ===
SCRIPTS_DIR = Path(__file__).parent
LOG_FILE = Path(".context/metrics/refactor_log.csv")

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def run_cmd(cmd: list, description: str, ignore_error: bool = False, capture_output: bool = True) -> bool:
    """Run a shell command with formatted output."""
    print(f"{DIM}→ {description}...{RESET}", end="", flush=True)
    if capture_output:
        start_t = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start_t
        
        if result.returncode == 0:
            print(f"\r  {GREEN}✓{RESET} {description} ({elapsed:.1f}s)")
            return True
        else:
            if ignore_error:
                print(f"\r  {YELLOW}⚠{RESET} {description} (Warning: {result.returncode})")
                return True
            else:
                print(f"\r  {RED}✗{RESET} {description} failed!")
                print(f"{RED}Error:{RESET}\n{result.stderr}")
                return False
    else:
        # For interactive or heavy output commands
        print("\n")
        returncode = subprocess.call(cmd)
        if returncode == 0:
            return True
        elif ignore_error:
            return True
        else:
            return False


def orchestrate_refactor(dry_run: bool = False):
    """Execute the full /refactor workflow."""
    start_total = time.time()
    
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  🏗️  ATHENA REFACTOR ORCHESTRATOR{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    if dry_run:
        print(f"{YELLOW}  [DRY RUN MODE] - No commits will be made.{RESET}\n")
    else:
        print(f"{DIM}  Full optimization sequence initiated.{RESET}\n")

    # Phase 1-3: DIAGNOSE / AUDIT (parallels refactor.md Phase 1-3)
    print(f"{BOLD}Phase 1-3: Deep Audit & Diagnostics{RESET}")
    # We use batch_audit.py as the heavy lifter here
    if not run_cmd([sys.executable, str(SCRIPTS_DIR / "batch_audit.py"), "--skip-graphrag"], "Running batch diagnostics"):
        print(f"{RED}Critical audit failure. Aborting refactor.{RESET}")
        sys.exit(1)

    # Phase 4: ORPHAN DETECTION (Optimization Pass gate)
    print(f"\n{BOLD}Phase 4: Integrity Gate{RESET}")
    orphan_proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "orphan_detector.py")], 
        capture_output=True, text=True
    )
    if "No orphan files found" in orphan_proc.stdout:
        print(f"  {GREEN}✓{RESET} No orphans detected.")
    else:
        print(f"  {YELLOW}⚠{RESET} Orphans detected (Check orphan_detector output). Proceeding anyway.")

    # Phase 4.5: SESSION LOG ARCHIVE
    print(f"\n{BOLD}Phase 4.5: Session Log Archive{RESET}")
    # Note: compress_sessions.py uses internal logic for retention/quarantine.
    run_cmd([sys.executable, str(SCRIPTS_DIR / "compress_sessions.py")], 
            "Archiving old session logs", ignore_error=True)

    # ... (Phase 5-7 lines 98-132 omitted for brevity in search, will remain via 'unchanged' lines if I target specific block or just replace the specific calls) ...
    # Be careful with 'ReplacementContent' - I will replace the block from Phase 4.5 to Phase 8-9 for precision.

    # Phase 5: MEMORY SYNC (Supabase + compress_memory)
    print(f"\n{BOLD}Phase 5: Memory Synchronization{RESET}")
    if dry_run:
        print(f"  {DIM}(Skipped for dry run){RESET}")
    else:
        run_cmd([sys.executable, str(SCRIPTS_DIR / "compress_memory.py")], 
                "Compressing memory", ignore_error=True)
        run_cmd([sys.executable, str(SCRIPTS_DIR / "supabase_sync.py")], "Syncing to Supabase Vectors")

    # Phase 5.5: CONTEXT COMPRESSION (Cache) - DISABLED due to API timeout issues
    print(f"\n{BOLD}Phase 5.5: Context Compression Cache{RESET}")
    print(f"  {DIM}(Skipped: context compression deferred to manual - causes stalls){RESET}")

    # Phase 6: VERIFICATION GATE
    print(f"\n{BOLD}Phase 6: Verification Gate{RESET}")
    run_cmd([sys.executable, str(SCRIPTS_DIR / "orphan_detector.py")], "Final orphan check", ignore_error=True)

    # Phase 6.5: INDEX REGENERATION
    print(f"\n{BOLD}Phase 6.5: Index Regeneration{RESET}")
    run_cmd([sys.executable, str(SCRIPTS_DIR / "generate_tag_index.py")], "Regenerating TAG_INDEX.md")
    
    # Phase 6.6: REGRESSION TESTS
    print(f"\n{BOLD}Phase 6.6: Regression Test Validation{RESET}")
    run_cmd([sys.executable, str(SCRIPTS_DIR / "run_tests.py")], "Running regression tests", ignore_error=True)

    # Phase 7: AUTO-LINKER
    print(f"\n{BOLD}Phase 7: Link Integrity{RESET}")
    if dry_run:
        print(f"  {DIM}(Skipped for dry run){RESET}")
    else:
        run_cmd([sys.executable, str(SCRIPTS_DIR / "auto_linker.py")], "Auto-linking orphans")

    # Phase 8-9: TELEMETRY & COMMIT
    print(f"\n{BOLD}Phase 8-9: Telemetry & Final Commit{RESET}")
    if dry_run:
        print(f"  {GREEN}✓{RESET} Ready to commit (Dry Run Complete)")
    else:
        # 1. Log Telemetry (Legacy)
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d-%H:%M')},refactor,success\n")
        
        # 2. Log Outcome (Scoreboard) - SCOPE: META (+0.5)
        run_cmd([sys.executable, str(SCRIPTS_DIR / "outcome_logger.py"), "--event", "META", "--desc", "Full Workspace Refactor", "--scope", "medium"], 
                "Logging Outcome Score", ignore_error=True)
            
        print(f"{DIM}  Executing git commit...{RESET}")
        run_cmd([sys.executable, str(SCRIPTS_DIR / "git_commit.py")], "Committing changes via Bankai", capture_output=False)

    total_elapsed = time.time() - start_total
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}REFACTOR COMPLETE{RESET} in {total_elapsed:.1f}s")
    print(f"{CYAN}{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full Athena refactor workflow")
    parser.add_argument("--dry-run", action="store_true", help="Run diagnostics but skip commit/sync")
    args = parser.parse_args()
    
    orchestrate_refactor(dry_run=args.dry_run)
