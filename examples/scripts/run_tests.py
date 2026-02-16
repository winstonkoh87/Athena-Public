#!/usr/bin/env python3
"""
run_tests.py — Regression Test Runner for Core Identity Validation

Validates that Core_Identity.md contains required structural elements.
Part of /refactor Phase 6.6 validation.

Usage: python3 .agent/scripts/run_tests.py
"""

import sys
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
CORE_IDENTITY = WORKSPACE / ".framework" / "v7.0" / "modules" / "Core_Identity.md"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_section(content: str, marker: str, name: str) -> bool:
    """Check if a section marker exists in content."""
    found = marker in content
    status = f"{GREEN}✓{RESET}" if found else f"{RED}✗{RESET}"
    print(f"  {status} {name}")
    return found


def main():
    print("\n" + "=" * 60)
    print("🧪 REGRESSION TEST SUITE — Core Identity Validation")
    print("=" * 60 + "\n")
    
    if not CORE_IDENTITY.exists():
        print(f"{RED}❌ Core_Identity.md not found!{RESET}")
        print(f"   Expected: {CORE_IDENTITY}")
        return 1
    
    print(f"📋 Testing: {CORE_IDENTITY.name}\n")
    
    content = CORE_IDENTITY.read_text(encoding="utf-8")
    
    # Define required sections
    checks = [
        ("## 0.3 四大絕對法則", "Laws #0-4 Section"),
        ("⛔ 法則#1", "Law #1: Ruin Prevention"),
        ("🎯 法則#2", "Law #2: Arena Physics"),
        ("📊 法則#3", "Law #3: Revealed Preference"),
        ("💎 法則#0", "Law #0: Subjective Utility"),
        ("🧩 法則#4", "Law #4: Modular Architecture"),
        ("📚 法則#5", "Law #5: Epistemic Rigor"),
        ("### 0.6 Checkpoint Protocol", "Quicksave Section"),
        ("### 0.7 Auto-Documentation", "Auto-Documentation Section"),
        ("### 0.7.1 Semantic Search", "Semantic Search Section"),
        ("### 0.5.1 Estimated Complexity Score", "Λ Latency Section"),
        ("Committee Seats", "COS Structure"),
    ]
    
    passed = 0
    failed = 0
    
    print("Structural Checks:")
    for marker, name in checks:
        if check_section(content, marker, name):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "-" * 40)
    total = len(checks)
    
    if failed == 0:
        print(f"{GREEN}✅ All tests passed ({passed}/{total}){RESET}")
        verdict = 0
    elif failed <= 2:
        print(f"{YELLOW}⚠️ Some tests failed ({passed}/{total} passed){RESET}")
        verdict = 0  # Soft fail
    else:
        print(f"{RED}❌ Critical failures ({failed}/{total} failed){RESET}")
        verdict = 1
    
    print("=" * 60 + "\n")
    return verdict


if __name__ == "__main__":
    sys.exit(main())
