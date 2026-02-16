"""
athena.intelligence.sentinel
============================
Implementation of Protocol 420: Sentinel Protocol (Quadrant IV Blind Spot Detection).
Autonomically scans for unknown-unknowns at session boundaries.
"""

import re
from pathlib import Path
from typing import Optional
from athena.core.config import PROJECT_ROOT, CONTEXT_DIR, CANONICAL_PATH

ACTIVE_CONTEXT_PATH = CONTEXT_DIR / "memory_bank" / "activeContext.md"
SESSION_LOGS_DIR = CONTEXT_DIR / "memories" / "session_logs"


def update_active_context(session_id: str, dry_run: bool = False) -> None:
    """Appends a session completion note to the Active Context."""
    if not ACTIVE_CONTEXT_PATH.exists():
        return

    if dry_run:
        print(
            f"  [DRY-RUN] Would append session {session_id} completion to Active Context."
        )
        return

    try:
        active_content = ACTIVE_CONTEXT_PATH.read_text(encoding="utf-8")
        completion_note = f"\n\n## Session {session_id} Completed\n"
        new_content = active_content + completion_note
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

        # 1. Extraction: Find Current Focus
        focus_match = re.search(
            r"## Current Focus\n(.*?)(?=\n##|\Z)", active_content, re.DOTALL
        )
        focus_text = focus_match.group(1).strip() if focus_match else ""

        if not focus_text:
            return "🔭 **Sentinel**: Active Context lacks a clear 'Current Focus'. This risks aimless drift."

        # 2. Divergence Analysis (First Principles)
        # Check if focus contradicts Law #1 (Ruin) or Law #2 (SDR)
        ruin_keywords = ["delete all", "wipe", "force", "ignore safety"]
        if any(kw in focus_text.lower() for kw in ruin_keywords):
            return "🔭 **Sentinel ALERT**: Current focus contains HIGH-RISK keywords. Potential Law #1 Violation."

        # 3. Structural Check: Check for Action Item Overload
        # If > 10 items in activeContext tasks, we are in 'Complexity Hell'
        task_count = len(re.findall(r"- \[ \]", active_content))
        if task_count > 10:
            return f"🔭 **Sentinel**: Complexity Hell detected ({task_count} pending tasks). Recommend pruning before adding new focus."

        return None

    except Exception as e:
        return f"🔭 **Sentinel Error**: {e}"


def check_shutdown_sentinel(session_log_path: Path) -> Optional[str]:
    """Shutdown Phase Sentinel: Checks for unfiled insights or protocol drift."""
    if not session_log_path.exists():
        return None

    try:
        log_content = session_log_path.read_text(encoding="utf-8")

        # 1. Learning Check
        if len(log_content) > 3000 and "[S]" not in log_content:
            return "🔭 **Sentinel**: Substantive session (>3kb) with no System Learnings [S] extracted. Knowledge leak risk."

        # 2. Critical Block Check
        if (
            "[[ S__ |" in log_content
            and "..." in log_content.split("[[ S__ |")[1].split("]]")[0]
        ):
            return "🔭 **Sentinel**: Unfinished Synthesis Block found. Volatile memory risk."

        return None

    except Exception:
        return None
