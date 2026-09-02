#!/usr/bin/env python3
"""
Athena Quickstart: Session Commit Demo
=======================================

This script demonstrates the session logging pattern.
Shows how Athena captures decisions and insights at session end.

Usage:
    python examples/quickstart/03_commit.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for development mode
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from athena.core.config import PROJECT_ROOT


def generate_session_log(summary: str, decisions: list, artifacts: list = None):
    """
    Generate a session log in Athena's format.
    
    This is the structure that gets saved at `/end`:
    - YAML frontmatter with metadata
    - Markdown body with decisions and artifacts
    """
    now = datetime.now()
    session_id = now.strftime("%Y-%m-%d-session-XX")

    # YAML frontmatter
    frontmatter = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "session_id": session_id,
        "summary": summary,
        "decisions": decisions,
        "artifacts": artifacts or [],
    }

    # Build markdown
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - \"{item}\"")
        else:
            lines.append(f"{key}: \"{value}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# Session Log: {now.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("## Summary")
    lines.append(summary)
    lines.append("")

    if decisions:
        lines.append("## Key Decisions")
        for d in decisions:
            lines.append(f"- {d}")
        lines.append("")

    if artifacts:
        lines.append("## Artifacts Created")
        for a in artifacts:
            lines.append(f"- `{a}`")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("🔒 ATHENA SESSION COMMIT DEMO")
    print("=" * 60)

    # Example session data
    summary = "Explored SDK architecture and tested hybrid search."
    decisions = [
        "Set max daily loss: 2% of account (hard stop)",
        "No revenge trading after 2 consecutive losses",
        "Use RRF fusion with 4 sources for search"
    ]
    artifacts = [
        "protocols/trading/risk_limits.md",
        "session_logs/2025-12-30-session-04.md"
    ]

    print("\n📝 Generating session log...")
    print("-" * 40)

    log_content = generate_session_log(summary, decisions, artifacts)
    print(log_content)

    print("-" * 40)
    print("\n✅ Session log generated")
    print("\n💡 In a real session, this would be:")
    print("   1. Written to .context/memories/session_logs/")
    print("   2. Embedded to Supabase pgvector")
    print("   3. Committed to git")
    print("   4. The /end workflow handles all of this automatically")

    # Show where it would go
    log_path = PROJECT_ROOT / ".context" / "memories" / "session_logs"
    if log_path.exists():
        print(f"\n📂 Session logs directory: {log_path}")
    else:
        print("\n📂 Default path would be: .context/memories/session_logs/")

    print("\n" + "=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
