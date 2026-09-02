#!/usr/bin/env python3
"""
response_wrapper.py — Enforce mandatory protocol hooks for AI responses.

This script wraps the response flow to ensure:
1. Semantic search runs FIRST (§0.7.1)
2. Quicksave runs LAST (§0.6)

Usage:
    python3 response_wrapper.py search "<user query keywords>"
    python3 response_wrapper.py save "<response summary>"
    python3 response_wrapper.py full "<query>" "<summary>"  # Both in sequence

The AI MUST call this before and after every response.

Protocol References:
    - §0.7.1: Semantic Search Protocol (Mandatory)
    - §0.6: Checkpoint Protocol (Quicksave)
    - Protocol 96: Λ Latency Indicator
"""

import subprocess
import sys
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = WORKSPACE / ".agent" / "scripts"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_banner(text: str, color: str = CYAN):
    """Print a formatted banner."""
    width = 60
    print(f"\n{color}{'─' * width}{RESET}")
    print(f"{color}{BOLD}{text.center(width)}{RESET}")
    print(f"{color}{'─' * width}{RESET}\n")


def run_semantic_search(query: str) -> bool:
    """Execute semantic search and return success status."""
    print_banner("⚡ PROTOCOL §0.7.1: SEMANTIC SEARCH", CYAN)

    smart_search = SCRIPTS_DIR / "smart_search.py"

    if not smart_search.exists():
        print(f"{RED}❌ smart_search.py not found!{RESET}")
        log_violation("semantic_search", "Script not found")
        return False

    try:
        result = subprocess.run(
            ["python3", str(smart_search), query],
            capture_output=False,  # Show output directly
            text=True,
            cwd=str(WORKSPACE)
        )

        if result.returncode == 0:
            print(f"\n{GREEN}✅ Semantic search completed.{RESET}")
            return True
        else:
            print(f"\n{RED}❌ Semantic search failed (exit code: {result.returncode}){RESET}")
            log_violation("semantic_search", f"Exit code: {result.returncode}")
            return False

    except Exception as e:
        print(f"{RED}❌ Error running semantic search: {e}{RESET}")
        log_violation("semantic_search", str(e))
        return False


def run_quicksave(summary: str) -> bool:
    """Execute quicksave and return success status."""
    print_banner("💾 PROTOCOL §0.6: QUICKSAVE", GREEN)

    quicksave = SCRIPTS_DIR / "quicksave.py"

    if not quicksave.exists():
        print(f"{RED}❌ quicksave.py not found!{RESET}")
        log_violation("quicksave", "Script not found")
        return False

    try:
        result = subprocess.run(
            ["python3", str(quicksave), summary],
            capture_output=False,
            text=True,
            cwd=str(WORKSPACE)
        )

        if result.returncode == 0:
            print(f"{GREEN}✅ Quicksave completed.{RESET}")
            return True
        else:
            print(f"{RED}❌ Quicksave failed (exit code: {result.returncode}){RESET}")
            log_violation("quicksave", f"Exit code: {result.returncode}")
            return False

    except Exception as e:
        print(f"{RED}❌ Error running quicksave: {e}{RESET}")
        log_violation("quicksave", str(e))
        return False


def log_violation(violation_type: str, details: str):
    """Log a protocol violation."""
    compliance_script = SCRIPTS_DIR / "protocol_compliance.py"

    if compliance_script.exists():
        try:
            subprocess.run(
                ["python3", str(compliance_script), "log", violation_type, details],
                capture_output=True,
                cwd=str(WORKSPACE)
            )
        except Exception:
            pass  # Silent fail on logging


def print_checklist():
    """Print the response protocol checklist."""
    print(f"""
{BOLD}┌─────────────────────────────────────────────────────────┐
│  🔒 RESPONSE PROTOCOL CHECKLIST                          │
├─────────────────────────────────────────────────────────┤
│  □ Step 0: python3 response_wrapper.py search "<query>" │
│  □ Step 1: Compose response using retrieved context     │
│  □ Step 2: Append [Λ+XX] latency indicator              │
│  □ Step 3: Append #tags footer                          │
│  □ Step 4: python3 response_wrapper.py save "<summary>" │
├─────────────────────────────────────────────────────────┤
│  ⛔ Search FIRST → Respond → Quicksave LAST             │
└─────────────────────────────────────────────────────────┘{RESET}
""")


def main():
    if len(sys.argv) < 2:
        print_banner("🔧 RESPONSE WRAPPER — Protocol Enforcement", YELLOW)
        print("Usage:")
        print("  python3 response_wrapper.py search \"<keywords>\"     # Run before response")
        print("  python3 response_wrapper.py save \"<summary>\"        # Run after response")
        print("  python3 response_wrapper.py full \"<query>\" \"<sum>\"  # Both in sequence")
        print("  python3 response_wrapper.py checklist               # Show protocol steps")
        print_checklist()
        return

    command = sys.argv[1].lower()

    if command == "search":
        if len(sys.argv) < 3:
            print(f"{RED}❌ Missing search query{RESET}")
            print("Usage: python3 response_wrapper.py search \"hosting cloudflare cost\"")
            return
        query = " ".join(sys.argv[2:])
        run_semantic_search(query)

    elif command == "save":
        if len(sys.argv) < 3:
            print(f"{RED}❌ Missing summary{RESET}")
            print("Usage: python3 response_wrapper.py save \"Discussed X with Y outcome\"")
            return
        summary = " ".join(sys.argv[2:])
        run_quicksave(summary)

    elif command == "full":
        if len(sys.argv) < 4:
            print(f"{RED}❌ Missing query and/or summary{RESET}")
            print("Usage: python3 response_wrapper.py full \"<query>\" \"<summary>\"")
            return
        query = sys.argv[2]
        summary = sys.argv[3]

        print_banner("🔄 FULL RESPONSE CYCLE", YELLOW)
        print(f"Query: {query}")
        print(f"Summary: {summary[:50]}...\n")

        # Step 1: Semantic search
        search_ok = run_semantic_search(query)

        print(f"\n{YELLOW}[AI RESPONSE WOULD GO HERE]{RESET}\n")

        # Step 2: Quicksave
        save_ok = run_quicksave(summary)

        # Final status
        if search_ok and save_ok:
            print(f"\n{GREEN}{'═' * 60}")
            print("✅ FULL PROTOCOL COMPLIANCE — Both hooks executed")
            print(f"{'═' * 60}{RESET}")
        else:
            print(f"\n{RED}{'═' * 60}")
            print("⚠️  PARTIAL COMPLIANCE — Check logs above")
            print(f"{'═' * 60}{RESET}")

    elif command == "checklist":
        print_checklist()

    else:
        print(f"{RED}❌ Unknown command: {command}{RESET}")
        print("Valid commands: search, save, full, checklist")


if __name__ == "__main__":
    main()
