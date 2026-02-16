"""
boot.py — Resilient Boot Shim (v2.1)
====================================
INVARIANT: Uses ONLY Python stdlib. This is the recovery layer.
If the SDK is broken, this script must still function.

Update v2.1: Integrated Local Recall Memory (SQLite FTS5) sync on boot.
"""

import os
import sys
import subprocess
from pathlib import Path

# === STDLIB-ONLY SECTION ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_PATH = PROJECT_ROOT / "src"


def recovery_shell():
    """
    Emergency Recovery Shell — runs when SDK import fails.
    Uses ONLY stdlib to provide recovery options.
    """
    print("\n" + "=" * 60)
    print("🚨 ATHENA RECOVERY SHELL")
    print("=" * 60)
    print("The SDK failed to load. Choose a recovery action:\n")
    print("  [1] Re-install dependencies (pip install -e .)")
    print("  [2] Git reset to last commit (git checkout .)")
    print("  [3] Run safe_boot.sh (zero-dependency fallback)")
    print("  [4] Open Python REPL for manual debugging")
    print("  [5] Exit")
    print()

    try:
        choice = input("Enter choice [1-5]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        sys.exit(1)

    if choice == "1":
        print("\n🔧 Running: pip install -e .")
        os.system(f"cd {PROJECT_ROOT} && pip install -e .")
        print("\n✅ Done. Try running boot.py again.")
    elif choice == "2":
        print("\n⚠️  This will discard all uncommitted changes!")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm == "y":
            os.system(f"cd {PROJECT_ROOT} && git checkout .")
            print("✅ Reset complete.")
        else:
            print("Aborted.")
    elif choice == "3":
        safe_boot = PROJECT_ROOT / ".agent" / "scripts" / "safe_boot.sh"
        if safe_boot.exists():
            print(f"\n🔧 Running: {safe_boot}")
            os.system(f"bash {safe_boot}")
        else:
            print("❌ safe_boot.sh not found.")

    elif choice == "4":
        print("\n🐍 Dropping into Python REPL. Use exit() to quit.")
        import code

        code.interact(local={"PROJECT_ROOT": PROJECT_ROOT, "Path": Path})
    else:
        print("Exiting.")
        sys.exit(0)

    sys.exit(0)


def main():
    """
    Main entry point. Attempts SDK boot, falls back to recovery shell.
    """
    # Ensure SDK is on path
    # This needs to be here because the orchestrator might be in the SDK path.
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    SDK_PATH = PROJECT_ROOT / "src"
    sys.path.insert(0, str(SDK_PATH))

    try:
        from athena.boot.orchestrator import main as orchestrator_main

        return orchestrator_main()
    except ImportError as e:
        print(f"❌ Boot Error: Missing modular components: {e}")
        # Fallback to a minimal recovery shell if the orchestrator itself can't be loaded
        print("\n" + "=" * 60)
        print("🚨 ATHENA RECOVERY SHELL (Minimal)")
        print("=" * 60)
        print(
            "The core orchestrator failed to load. This usually means the SDK is not installed or corrupted."
        )
        print("Please try to re-install dependencies or debug manually.\n")
        print("  [1] Re-install dependencies (pip install -e .)")
        print("  [2] Open Python REPL for manual debugging")
        print("  [3] Exit")
        print()

        try:
            choice = input("Enter choice [1-3]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(1)

        if choice == "1":
            print("\n🔧 Running: pip install -e .")
            os.system(f"cd {PROJECT_ROOT} && pip install -e .")
            print("\n✅ Done. Try running boot.py again.")
        elif choice == "2":
            print("\n🐍 Dropping into Python REPL. Use exit() to quit.")
            import code

            code.interact(local={"PROJECT_ROOT": PROJECT_ROOT, "Path": Path})
        else:
            print("Exiting.")
            sys.exit(0)

        sys.exit(0)
    except Exception as e:
        print(f"❌ An unexpected error occurred during boot: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
