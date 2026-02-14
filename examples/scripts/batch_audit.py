#!/usr/bin/env python3
"""
batch_audit.py — Parallel Audit Orchestrator for /end

Latency Profile: HIGH (user is away, take your time)

Runs audit scripts in parallel where possible for faster /end completion.

Phase 1 (Parallel): Independent detection scripts
Phase 2 (Sequential): Heavy compute that depends on Phase 1
Phase 3 (Sequential): Commit

Usage:
    python3 .agent/scripts/batch_audit.py
    python3 .agent/scripts/batch_audit.py --skip-graphrag  # Skip heavy indexing
"""

import sys
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Configuration ===
SCRIPTS_DIR = Path(__file__).parent

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def run_script(script_name: str, args: list = None) -> tuple[str, bool, float]:
    """Run a Python script and return (name, success, elapsed_seconds)."""
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        elapsed = time.time() - start
        return (script_name, True, elapsed)
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        return (script_name, False, elapsed)
    except FileNotFoundError:
        return (script_name, False, 0.0)


def main():
    skip_graphrag = "--skip-graphrag" in sys.argv or "--quick" in sys.argv
    start_time = time.time()

    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  🔍 BATCH AUDIT ORCHESTRATOR (/end optimization){RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}\n")

    # ════════════════════════════════════════════════════════════════
    # PHASE 1: PARALLEL (Independent detection scripts)
    # ════════════════════════════════════════════════════════════════
    parallel_scripts = [
        "memory_integrity.py",
        "orphan_detector.py",
        "stale_detector.py",
        "cross_reference.py",
    ]

    print(f"{BOLD}Phase 1: Detection (Parallel){RESET}")
    print(f"{DIM}Running {len(parallel_scripts)} scripts concurrently...{RESET}\n")

    phase1_results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_script, s): s for s in parallel_scripts}
        for future in as_completed(futures):
            name, success, elapsed = future.result()
            status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
            print(f"  {status} {name:<25} ({elapsed:.1f}s)")
            phase1_results.append((name, success, elapsed))

    phase1_time = max(r[2] for r in phase1_results) if phase1_results else 0
    print(f"\n{DIM}  Phase 1 wall-clock: {phase1_time:.1f}s (parallel){RESET}")

    # ════════════════════════════════════════════════════════════════
    # PHASE 2: SEQUENTIAL (Heavy compute)
    # ════════════════════════════════════════════════════════════════
    print(f"\n{BOLD}Phase 2: Heavy Compute (Sequential){RESET}\n")

    phase2_results = []

    # Note: compress_sessions.py moved to /refactor workflow (Phase 4.5)
    # to avoid duplicate execution

    # GraphRAG indexing (optional)
    if not skip_graphrag:
        name, success, elapsed = run_script("index_graphrag.py")
        status = f"{GREEN}✓{RESET}" if success else f"{YELLOW}⚠{RESET}"
        print(f"  {status} {name:<25} ({elapsed:.1f}s)")
        phase2_results.append((name, success, elapsed))
    else:
        print(f"  {YELLOW}⊘{RESET} index_graphrag.py         (skipped)")

    phase2_time = sum(r[2] for r in phase2_results) if phase2_results else 0
    print(f"\n{DIM}  Phase 2 wall-clock: {phase2_time:.1f}s{RESET}")

    # ════════════════════════════════════════════════════════════════
    # PHASE 3: FINALIZE
    # ════════════════════════════════════════════════════════════════
    print(f"\n{BOLD}Phase 3: Finalize{RESET}\n")

    phase3_results = []

    # Generate tag index (migrated to src/athena/generators/)
    tag_index_script = (
        Path(__file__).parent.parent.parent
        / "src"
        / "athena"
        / "generators"
        / "generate_tag_index.py"
    )
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(tag_index_script)],
            capture_output=True,
            text=True,
            check=True,
        )
        success = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        success = False
    elapsed = time.time() - start
    name = "generate_tag_index.py"
    status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
    print(f"  {status} {name:<25} ({elapsed:.1f}s)")
    phase3_results.append((name, success, elapsed))

    phase3_time = sum(r[2] for r in phase3_results)

    # ════════════════════════════════════════════════════════════════
    # SUMMARY
    # ════════════════════════════════════════════════════════════════
    total_time = time.time() - start_time
    all_results = phase1_results + phase2_results + phase3_results
    success_count = sum(1 for r in all_results if r[1])
    total_count = len(all_results)

    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"  Scripts run:  {success_count}/{total_count} succeeded")
    print(f"  Phase 1:      {phase1_time:.1f}s (parallel)")
    print(f"  Phase 2:      {phase2_time:.1f}s (sequential)")
    print(f"  Phase 3:      {phase3_time:.1f}s")
    print(f"  {BOLD}Total:       {total_time:.1f}s{RESET}")

    # Compare to sequential
    sequential_estimate = sum(r[2] for r in phase1_results) + phase2_time + phase3_time
    savings = sequential_estimate - total_time
    if savings > 0:
        print(f"\n  {GREEN}⚡ Saved ~{savings:.1f}s vs sequential execution{RESET}")

    print(f"{CYAN}{'=' * 60}{RESET}\n")

    # Return appropriate exit code
    if success_count < total_count:
        failed = [r[0] for r in all_results if not r[1]]
        print(f"{YELLOW}⚠️  Some scripts failed: {', '.join(failed)}{RESET}")
        print(f"{DIM}   Run individually to see errors.{RESET}\n")
        return 1

    print(f"{GREEN}✓ All audits passed. Ready for commit.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
