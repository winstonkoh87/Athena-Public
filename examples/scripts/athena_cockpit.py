#!/usr/bin/env python3
"""
athena_cockpit.py (Neural Cockpit)
==================================
Rich-based Terminal UI Dashboard for Project Athena.
Provides real-time visibility into system metrics, memory, and session state.

Usage: python3 athena_cockpit.py [--live]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
except ImportError:
    print("⚠️  Rich library not installed. Run: pip install rich")
    sys.exit(1)

# --- Path Discovery ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.core.config import (
    CONTEXT_DIR,
    SESSIONS_DIR,
    AGENT_DIR,
    FRAMEWORK_DIR,
    MEMORY_DIR,
)

console = Console()


def count_files(directory: Path, pattern: str = "*") -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def get_recent_sessions(limit: int = 5) -> list:
    if not SESSIONS_DIR.exists():
        return []
    sessions = sorted(SESSIONS_DIR.glob("*.md"), key=os.path.getmtime, reverse=True)
    return [s.name for s in sessions[:limit]]


def get_current_session() -> str:
    sessions = get_recent_sessions(1)
    return sessions[0] if sessions else "No active session"


def get_governance_score() -> int:
    violation_file = CONTEXT_DIR / "protocol_violations.json"
    if not violation_file.exists():
        return 100
    try:
        data = json.loads(violation_file.read_text())
        violations = data.get("violations", [])
        high_sev = len([v for v in violations if v.get("severity") == "high"])
        return max(0, 100 - (high_sev * 5))
    except Exception:
        return 100


def get_graphrag_status() -> tuple:
    """Returns (status_str, size_mb)"""
    graph_file = AGENT_DIR / "graphrag" / "knowledge_graph.gpickle"
    if graph_file.exists():
        size = graph_file.stat().st_size / (1024 * 1024)
        return (f"[green]Active[/green]", f"{size:.1f} MB")
    return ("[red]Inactive[/red]", "0 MB")


def get_vector_db_status() -> str:
    """Check if Supabase connection is configured."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        content = env_file.read_text()
        if "SUPABASE_URL" in content and "SUPABASE_SERVICE_ROLE_KEY" in content:
            return "[green]Configured[/green]"
    return "[yellow]Check .env[/yellow]"


def get_last_boot() -> str:
    log_file = AGENT_DIR / "state" / "last_boot.log"
    if log_file.exists():
        try:
            dt = datetime.fromtimestamp(log_file.stat().st_mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    return "Unknown"


def build_dashboard() -> Layout:
    """Build the main dashboard layout."""
    layout = Layout()

    # --- Metrics Table ---
    metrics = Table(title="📊 Core Metrics", box=box.ROUNDED, show_header=False)
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Value", style="bold")

    protocols = count_files(AGENT_DIR / "skills" / "protocols", "**/*.md")
    sessions = count_files(SESSIONS_DIR, "*.md")
    scripts = count_files(AGENT_DIR / "scripts", "*.py")

    metrics.add_row("Protocols", str(protocols))
    metrics.add_row("Sessions", str(sessions))
    metrics.add_row("Scripts", str(scripts))
    metrics.add_row("Integrity", f"{get_governance_score()}%")

    # --- System Status Table ---
    status = Table(title="⚡ System Status", box=box.ROUNDED, show_header=False)
    status.add_column("Component", style="cyan")
    status.add_column("Status")

    graph_status, graph_size = get_graphrag_status()
    status.add_row("GraphRAG", f"{graph_status} ({graph_size})")
    status.add_row("VectorDB", get_vector_db_status())
    status.add_row("Last Boot", get_last_boot())
    status.add_row("Session", get_current_session())

    # --- Recent Sessions ---
    recent = Table(title="📝 Recent Sessions", box=box.ROUNDED)
    recent.add_column("Session", style="dim")
    for s in get_recent_sessions(5):
        recent.add_row(s)

    # --- Build Layout ---
    layout.split_column(
        Layout(
            Panel(
                Text(
                    "🏛️ PROJECT ATHENA | NEURAL COCKPIT",
                    justify="center",
                    style="bold cyan",
                ),
                box=box.DOUBLE,
            ),
            size=3,
        ),
        Layout(name="main"),
        Layout(
            Panel(
                Text(
                    "⚡ v8.2-Stable | 08 Feb 2026 | Memory Prism Active",
                    justify="center",
                    style="dim",
                ),
                box=box.SIMPLE,
            ),
            size=3,
        ),
    )

    layout["main"].split_row(Layout(metrics), Layout(status), Layout(recent))

    return layout


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Athena Neural Cockpit")
    parser.add_argument("--live", action="store_true", help="Enable live refresh mode")
    args = parser.parse_args()

    if args.live:
        import time

        with Live(build_dashboard(), refresh_per_second=1, console=console) as live:
            try:
                while True:
                    time.sleep(5)
                    live.update(build_dashboard())
            except KeyboardInterrupt:
                pass
    else:
        console.print(build_dashboard())
        console.print()


if __name__ == "__main__":
    main()
