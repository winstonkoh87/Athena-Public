#!/usr/bin/env python3
"""
quicksave.py — SDK Shim
========================
Saves a checkpoint to the current session log via athena.sessions.
"""

import sys
from pathlib import Path

from lib.shared_utils import setup_paths, log_violation

setup_paths()


def main():
    import argparse
    from athena.core.governance import get_governance
    from athena.sessions import append_checkpoint, log_to_decision_ledger

    parser = argparse.ArgumentParser(description="Athena Quicksave (SDK Shim)")
    parser.add_argument("summary", help="Summary of activity")
    parser.add_argument("--bullets", nargs="+", help="Optional bullet points")
    parser.add_argument(
        "--decision", action="store_true", help="Log to decision ledger too"
    )
    args = parser.parse_args()

    # Governance: Check if Triple-Lock protocol was followed
    gov = get_governance()
    semantic = gov._state.get("semantic_search_performed", False)
    web = gov._state.get("web_search_performed", False)

    if not (semantic and web):
        missing = []
        if not semantic:
            missing.append("Semantic Search")
        if not web:
            missing.append("Web Research")

        print(
            f"\033[91m⚠️  TRIPLE-LOCK VIOLATION: Quicksave initiated. Missing: {', '.join(missing)}.\033[0m"
        )
        # Log violation via shared util
        log_violation(
            "triple_lock", f"Quicksave triggered. Missing: {', '.join(missing)}"
        )

    gov.verify_exchange_integrity()  # Resets state regardless of result

    try:
        log_path = append_checkpoint(args.summary, args.bullets)
        print(f"✅ Quicksave → {log_path.name}")

        # [Protocol 104] Semantic Compression Hook (Fire-and-Forget)
        try:
            import subprocess

            print("🧠 Compressing memory... (Background)", end="", flush=True)

            # Run the compressor script in fire-and-forget mode
            # It will self-append to .context/memory_bank/semantic_log.md
            cmd = [
                "python3",
                ".agent/scripts/memory_compressor.py",
                f"{args.summary} {' '.join(args.bullets) if args.bullets else ''}",
                "--output-file",
                ".context/memory_bank/semantic_log.md",
            ]

            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            print("\r✅ Memory Compression queued.")

        except Exception as e:
            print(f"\r⚠️  Compression trigger error: {e}")

        # [Protocol 105] LightRAG Indexing Hook
        # REMOVED: Redundant. The Athena Daemon (athenad.py) watches for file changes
        # and handles indexing asynchronously. We don't need to block here.

        if args.decision or "[CIRCUIT" in args.summary:
            log_to_decision_ledger(args.summary)
            print("⚖️  Decision logged to ledger.")

        # [Protocol: Edit-Then-Validate] (Copilot Rule)
        try:
            import subprocess

            print("🔍 Validating changes...", end="", flush=True)

            # Check for python files in git diff
            diff = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True
            )
            changed_files = [f for f in diff.stdout.splitlines() if f.endswith(".py")]

            if changed_files:
                # Run ruff check as a lightweight validator
                lint = subprocess.run(
                    ["ruff", "check"] + changed_files, capture_output=True, text=True
                )
                if lint.returncode == 0:
                    print("\r✅ Validation Passed (Ruff).")
                else:
                    print(
                        f"\r❌ Validation Failed! Errors detected in: {', '.join(changed_files)}"
                    )
                    print(lint.stdout[:500])  # Show first 500 chars of errors
            else:
                print("\rℹ️  No source files to validate.")
        except Exception as e:
            print(f"\r⚠️  Validation skipped: {e}")

    except Exception as e:
        print(f"❌ Quicksave failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
