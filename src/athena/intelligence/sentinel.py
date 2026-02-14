"""
athena.intelligence.sentinel
============================
Implementation of Protocol 420: Sentinel Protocol (Quadrant IV Blind Spot Detection).
Autonomically scans for unknown-unknowns at session boundaries.
"""

from pathlib import Path
from typing import Optional
from athena.core.config import PROJECT_ROOT, CONTEXT_DIR, CANONICAL_PATH

ACTIVE_CONTEXT_PATH = CONTEXT_DIR / "memory_bank" / "activeContext.md"
SESSION_LOGS_DIR = CONTEXT_DIR / "memories" / "session_logs"


def update_active_context(session_id: str, dry_run: bool = False) -> None:
    """
    Appends a session completion note to the Active Context.
    """
    if not ACTIVE_CONTEXT_PATH.exists():
        return

    if dry_run:
        print(
            f"  [DRY-RUN] Would append session {session_id} completion to Active Context."
        )
        return

    try:
        # Read existing content
        active_content = ACTIVE_CONTEXT_PATH.read_text(encoding="utf-8")

        # Append the session completion note
        completion_note = f"\n\n## Session {session_id} Completed\n"
        new_content = active_content + completion_note

        # Write updated content back
        ACTIVE_CONTEXT_PATH.write_text(new_content, encoding="utf-8")

    except Exception as e:
        print(f"Error updating active context for session {session_id}: {e}")


def check_boot_sentinel() -> Optional[str]:
    """
    Boot Phase Sentinel: Cross-references Active Context against Canonical Constraints.
    """
    if not ACTIVE_CONTEXT_PATH.exists() or not CANONICAL_PATH.exists():
        return None

    try:
        active_content = ACTIVE_CONTEXT_PATH.read_text(encoding="utf-8")
        canonical_content = CANONICAL_PATH.read_text(encoding="utf-8")

        # 1. Detection: Focus Check
        focus_section = ""
        if "## Current Focus" in active_content:
            focus_section = (
                active_content.split("## Current Focus")[1].split("##")[0].strip()
            )

        if not focus_section:
            return "🔭 **Sentinel**: Active Context lacks a clear 'Current Focus'. This risks aimless drift usage."

        # 2. Heuristic: Code vs Strategy Balance
        is_coding_focus = any(
            kw in focus_section.lower()
            for kw in ["code", "refactor", "implement", "debug", "fix"]
        )
        if is_coding_focus and "Law #1" in canonical_content:
            # Check if recent inputs suggest strategic blindspots (simulated for now)
            pass

        return None

    except Exception:
        return None


def check_shutdown_sentinel(session_log_path: Path) -> Optional[str]:
    """
    Shutdown Phase Sentinel: Checks for unfiled insights or protocol drift.
    """
    if not session_log_path.exists():
        return None

    try:
        log_content = session_log_path.read_text(encoding="utf-8")

        # 1. Check for missing learnings in a substantive session
        if len(log_content) > 2000 and "[S]" not in log_content:
            return "🔭 **Sentinel**: Substantive session detected (>2kb) but no System Learnings [S] extracted. Knowledge leak risk."

        return None

    except Exception:
        return None
