#!/usr/bin/env python3
"""
athena_status.py
================
CLI Dashboard for Project Athena.
Provides a high-level overview of system metrics, recent activity, and health.
"""

import os
import sys
from pathlib import Path
import glob
from datetime import datetime

# ANSI Colors
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def count_files(directory, pattern="*"):
    path = PROJECT_ROOT / directory
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def get_recent_sessions(limit=5):
    path = PROJECT_ROOT / ".context/memories/session_logs/"
    if not path.exists():
        return []
    sessions = sorted(path.glob("*.md"), key=os.path.getmtime, reverse=True)
    return [s.name for s in sessions[:limit]]


def get_governance_score():
    violation_file = PROJECT_ROOT / ".context" / "protocol_violations.json"
    if not violation_file.exists():
        return 100
    try:
        import json

        data = json.loads(violation_file.read_text())
        violations = data.get("violations", [])
        # Simple score: 100 - (10 * high_severity_count)
        # Simple score: 100 - (5 * high_severity_count)
        high_sev = len([v for v in violations if v.get("severity") == "high"])
        return max(0, 100 - (high_sev * 5))
    except Exception:
        return 100


def get_system_health():
    state_file = PROJECT_ROOT / ".context/project_state.md"
    if not state_file.exists():
        return "Unknown"

    with open(state_file, "r") as f:
        content = f.read()
        for line in content.split("\n"):
            if "Health**" in line or "Health:" in line:
                val = line.split(":")[-1].strip()
                return val.replace("**", "").strip()
    return "Unknown"


def get_last_boot_time():
    log_file = PROJECT_ROOT / ".agent" / "state" / "last_boot.log"
    if not log_file.exists():
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(log_file.stat().st_mtime)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"


def get_graphrag_status():
    graph_file = PROJECT_ROOT / ".agent" / "graphrag" / "knowledge_graph.gpickle"
    if graph_file.exists():
        size = graph_file.stat().st_size / (1024 * 1024)
        return f"{GREEN}Active ({size:.1f} MB){RESET}"
    return f"{RED}Inactive{RESET}"


def main():
    print(f"\n{BOLD}{CYAN}🏛️  PROJECT ATHENA | SYSTEM DASHBOARD{RESET}")
    print(f"{CYAN}{'━' * 60}{RESET}")

    # Section: Core Metrics
    protocols = count_files(".agent/skills/protocols", "**/*.md")
    sessions = count_files(".context/memories/session_logs", "*.md")
    scripts = count_files(".agent/scripts", "*.py")
    health = get_system_health()
    last_boot = get_last_boot_time()
    graph_status = get_graphrag_status()
    gov_score = get_governance_score()

    col1 = f"{BOLD}Metrics:{RESET}\n"
    col1 += f"  📂 Protocols:  {BLUE}{protocols}{RESET}\n"
    col1 += f"  📝 Sessions:   {GREEN}{sessions}{RESET}\n"
    col2 = f"{BOLD}Status:{RESET}\n"
    col2 += f"  🕒 Last Boot:  {DIM}{last_boot}{RESET}\n"
    col2 += f"  🕸️  GraphRAG:   {graph_status}\n"
    col2 += f"  📍 Root:       {DIM}{PROJECT_ROOT.name}/{RESET}\n"
    col2 += f"  🛡️  Integrity:  {BOLD}{GREEN if gov_score > 90 else YELLOW}{gov_score}%{RESET}\n"

    col1 += f"  ⚙️  Scripts:    {YELLOW}{scripts}{RESET}\n"
    col1 += f"  ❤️  Health:     {BOLD}{GREEN if '100' in health or '98' in health else YELLOW}{health}{RESET}"

    # Print columns (simple side-by-side)
    lines1 = col1.split("\n")
    lines2 = col2.split("\n")
    for l1, l2 in zip(lines1, lines2):
        print(f"{l1:<30} {l2}")
    print()

    # Section: Recent Activity
    print(f"{BOLD}Recent Sessions:{RESET}")
    recent = get_recent_sessions(limit=3)
    for s in recent:
        print(f"  • {s}")
    print()

    print(f"{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{GREEN}⚡ System Active and Calibrated.{RESET}\n")


if __name__ == "__main__":
    main()
