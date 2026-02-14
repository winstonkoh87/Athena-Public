#!/usr/bin/env python3
"""
athena.boot.orchestrator
=========================
Modular boot sequence orchestrator.
Replaces the monolithic .agent/scripts/boot.py
"""

import sys
from datetime import datetime
from pathlib import Path
from athena.boot.loaders.ui import UILoader
from athena.boot.loaders.state import StateLoader
from athena.boot.loaders.identity import IdentityLoader
from athena.boot.loaders.memory import MemoryLoader
from athena.boot.loaders.system import SystemLoader
from athena.boot.loaders.prefetch import PrefetchLoader
from athena.boot.constants import (
    PROJECT_ROOT,
    RED,
    GREEN,
    YELLOW,
    CYAN,
    BOLD,
    DIM,
    RESET,
)


def main():
    # Phase 0: Check for --verify flag
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        # We can implement a verify mode here later if needed
        # For now, just pass
        pass

    # Phase 1: Watchdog & Pre-flight
    StateLoader.enable_watchdog()
    UILoader.divider("⚡ ATHENA BOOT SEQUENCE")

    StateLoader.check_prior_crashes()
    StateLoader.check_canary_overdue()

    # Phase 1.5: System Sync & Boot Timestamp Update
    SystemLoader.sync_ui()
    try:
        last_boot_log = PROJECT_ROOT / ".agent" / "state" / "last_boot.log"
        last_boot_log.parent.mkdir(parents=True, exist_ok=True)
        with open(last_boot_log, "w") as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        print(f"   ⚠️  Boot Log Update Fail: {e}")

    # Phase 2: Integrity
    if not IdentityLoader.verify_semantic_prime():
        return 1

    # Phase 3: Memory Recall
    last_session = MemoryLoader.recall_last_session()

    # Phase 3.5: Semantic Compaction (Protocol 415)
    try:
        sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
        from compact_context import compact_active_context

        print(f"   🧹 Compacting Context...", end="\r")
        compact_active_context()
        print(f"   🧹 Context Compacted.    ")
    except Exception as e:
        print(f"   ⚠️  Compaction Fail: {e}")

    # Phase 4: Session Creation
    session_id = MemoryLoader.create_session()

    # Phase 5: Audit (Reset)
    try:
        sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
        from semantic_audit import reset_audit

        reset_audit()
    except Exception:
        pass

    # Phase 6 & 7: Optimized Context & Semantic Activation (Parallel)
    from concurrent.futures import ThreadPoolExecutor
    from athena.core.health import HealthCheck

    def run_health_check_wrapper():
        if not HealthCheck.run_all():
            print(
                f"{RED}⚠️  System health check failed. Proceeding with caution...{RESET}"
            )

    with ThreadPoolExecutor(max_workers=8) as executor:
        # 1. Non-blocking context capture
        executor.submit(MemoryLoader.capture_context)

        # 2. Semantic priming (most expensive)
        semantic_future = executor.submit(MemoryLoader.prime_semantic)

        # 3. Protocol injection
        executor.submit(IdentityLoader.inject_auto_protocols, "startup session boot")

        # 4. Search cache pre-warming (new)
        executor.submit(MemoryLoader.prewarm_search_cache)

        # 5. System Health Check (Moved to background)
        executor.submit(run_health_check_wrapper)

        # 6. Prefetch (Moved to background)
        executor.submit(PrefetchLoader.prefetch_hot_files)

    # Display remaining sync items
    MemoryLoader.display_learnings_snapshot()
    IdentityLoader.display_cognitive_profile()
    IdentityLoader.display_cos_status()

    # Phase 8: Sidecar Launch (Sovereign Index)
    try:
        import subprocess

        sidecar_path = PROJECT_ROOT / ".agent" / "scripts" / "sidecar.py"
        subprocess.Popen(
            [sys.executable, str(sidecar_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"   🛡️  Sidecar Launched (PID: Independent)")
    except Exception as e:
        print(f"   ⚠️  Sidecar Fail: {e}")

    # Disable watchdog
    StateLoader.disable_watchdog()

    # Final Summary
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{GREEN}{BOLD}⚡ Ready.{RESET} Session: {session_id}")
    print(
        f"{DIM}⚖️  Law #6 Reminder: Run 'python3 .agent/scripts/quicksave.py \"...\"' after completing work.{RESET}"
    )
    print(f"{BOLD}{'─' * 60}{RESET}\n")

    # Display Memory Bank Context
    memory_bank_path = PROJECT_ROOT / ".context" / "memory_bank" / "activeContext.md"
    if memory_bank_path.exists():
        print(f"\n{CYAN}{BOLD}🧠 Active Context (Memory Bank):{RESET}")
        try:
            content = memory_bank_path.read_text().strip()
            # Indent content for readability
            indented_content = "\n".join(f"   {line}" for line in content.splitlines())
            print(f"{DIM}{indented_content}{RESET}")

            # Sentinel Phase (Protocol 420)
            from athena.intelligence.sentinel import check_boot_sentinel

            sentinel_msg = check_boot_sentinel()
            if sentinel_msg:
                print(f"\n{YELLOW}{sentinel_msg}{RESET}")

        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
