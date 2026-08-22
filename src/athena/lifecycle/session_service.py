"""
athena.lifecycle.session_service
================================
Canonical Session Lifecycle Service for Project Athena.

Owns:
- Session log creation with validated YAML frontmatter
- Checkpoint appending
- Session closing and receipt generation
- Memory/cache invalidation triggers
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from athena.core.cache import invalidate_search_cache
from athena.core.config import SESSIONS_DIR, get_current_session_log
from athena.core.permissions import get_permissions


class SessionService:
    """
    Unified, observable session lifecycle engine.
    """

    def __init__(self, sessions_dir: Path | None = None):
        self.sessions_dir = sessions_dir or SESSIONS_DIR

    def get_current_session(self) -> Path | None:
        """Find and return the active/latest session log file in self.sessions_dir."""
        if not self.sessions_dir.exists():
            return None

        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-session-.*\.md$")
        sessions = sorted(
            [f for f in self.sessions_dir.iterdir() if f.is_file() and pattern.match(f.name)],
            key=lambda x: x.name,
            reverse=True,
        )
        return sessions[0] if sessions else None

    def get_next_session_number(self, date_str: str | None = None) -> int:
        """Find the highest session number for the given date (default today)."""
        target_date = date_str or datetime.now().strftime("%Y-%m-%d")
        if not self.sessions_dir.exists():
            return 1

        pattern = re.compile(rf"^{target_date}-session-(\d{{2,3}})\.md$")
        max_num = 0
        for file in self.sessions_dir.iterdir():
            match = pattern.match(file.name)
            if match:
                max_num = max(max_num, int(match.group(1)))

        return max_num + 1

    def update_forward_lineage(self, prev_session_id: str, current_session_id: str) -> None:
        """Update the previous session's YAML to point to the current session."""
        if not prev_session_id:
            return

        filename = f"{prev_session_id}.md"
        filepath = self.sessions_dir / filename
        if not filepath.exists():
            archive_path = self.sessions_dir / "archive" / filename
            if archive_path.exists():
                filepath = archive_path

        if not filepath.exists():
            return

        try:
            content = filepath.read_text(encoding="utf-8")
            pattern = r"^next_session:.*$"
            replacement = f"next_session: {current_session_id}"
            new_content, count = re.subn(
                pattern, replacement, content, count=1, flags=re.MULTILINE
            )
            if count > 0:
                filepath.write_text(new_content, encoding="utf-8")
        except Exception:
            pass

    def create_session(
        self,
        focus: str | None = None,
        tags: list[str] | None = None,
    ) -> Path:
        """
        Create a new session log with validated YAML frontmatter.
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        time_iso = now.astimezone().isoformat()
        time_display = now.strftime("%H:%M")
        session_num = self.get_next_session_number(today)

        session_id = f"{today}-session-{session_num:02d}"
        filename = f"{session_id}.md"
        filepath = self.sessions_dir / filename

        prev_session_log = self.get_current_session()
        prev_session_id = prev_session_log.stem if prev_session_log else None
        prev_link = f"← {prev_session_id}" if prev_session_id else "None"

        tags_list = tags or ["session"]
        tags_yaml = json.dumps(tags_list)

        template = f"""---
session_id: {session_id}
date: {today}
start: {time_iso}
end:
duration_min:
status: in_progress
verdict:
prev_session: {prev_session_id if prev_session_id else "null"}
next_session:
focus: {focus or "..."}
threads: []
tags: {tags_yaml}
lambda_peak:
lambda_total:
lambda_coverage:
lambda_coverage_n:
lambda_coverage_d:
---

# Session Log: {today} (Session {session_num:02d})

**Date**: {today}
**Time**: {time_display} - ...
**Focus**: {focus or "..."}
**Related Sessions**: {prev_link}

---

## 0. R__ Compressed Context

> Auto-generated on close. Do not manually edit.

```text
[[ R__ |
@focus: {focus or "..."}
@status: in_progress
@decided:
@pending:
@artifacts:
@lambda_peak:
@tags: {', '.join(tags_list)}
]]
```

---

## 1. Checkpoints

> Automatically appended by quicksave. Do not manually write.

---

## 2. Key Decisions & Insights

- **Decision**: ...
- **Insight**: ...

---

## 2.5 Learnings (Compiler Inputs)

> Write explicitly. Ingested and propagated on close.

### Learned (System / Workflow)

- [S] ...

### Learned (About User)

- [U] ...

### Integration Requested

- [X] ...

---

## 3. Action Items & Deferred

| ID | Action | Owner | Status | Thread |
|----|--------|-------|--------|--------|
| {session_id}-A1 | ... | AI / User | Pending | — |

---

## 4. Artifacts & Outputs

- **Created**: ...
- **Modified**: ...

---

## Session Closed

**Status**: ⏳ In Progress
**Time**: ...
**Verdict**: ... (🚀 SQUAD / ⚠️ Partial / 🔴 Blocked)

---

## Tagging

#session #{' #'.join(tags_list)}
"""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        filepath.write_text(template, encoding="utf-8")

        if prev_session_id:
            self.update_forward_lineage(prev_session_id, session_id)

        # Trigger search cache invalidation for freshness
        invalidate_search_cache()

        return filepath

    def append_checkpoint(
        self,
        summary: str,
        bullets: list[str] | None = None,
        log_path: Path | None = None,
    ) -> Path:
        """
        Append a structured checkpoint block to the active session log.
        """
        target_path = log_path or self.get_current_session()
        if not target_path or not target_path.exists():
            raise FileNotFoundError(f"Active session log not found at {target_path}")

        timestamp = datetime.now().strftime("%H:%M")
        block = f"\n### [{timestamp} SGT] Checkpoint\n\n**Summary**: {summary}\n"
        if bullets:
            block += "\n" + "\n".join([f"- {b}" for b in bullets]) + "\n"
        block += "\n---\n"

        with open(target_path, "a", encoding="utf-8") as f:
            f.write(block)

        # Trigger search cache invalidation
        invalidate_search_cache()
        return target_path

    def close_session(
        self,
        session_path: Path | None = None,
        verdict: str = "🚀 SQUAD",
        learnings: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """
        Close a session log, compute metadata, update status, and return a receipt.
        """
        target_path = session_path or self.get_current_session()
        if not target_path or not target_path.exists():
            raise FileNotFoundError("No active session log to close.")

        content = target_path.read_text(encoding="utf-8")
        now = datetime.now()
        end_time_display = now.strftime("%H:%M")
        end_time_iso = now.astimezone().isoformat()

        # Update status in frontmatter if present
        if "status: in_progress" in content:
            content = content.replace("status: in_progress", "status: closed")
        if "end:\n" in content:
            content = content.replace("end:\n", f"end: {end_time_iso}\n")
        if "verdict:\n" in content:
            content = content.replace("verdict:\n", f"verdict: \"{verdict}\"\n")

        # Update Markdown body status
        if "**Status**: ⏳ In Progress" in content:
            content = content.replace(
                "**Status**: ⏳ In Progress",
                f"**Status**: ✅ Closed\n**Time**: {end_time_display} SGT\n**Verdict**: {verdict}",
            )

        # Inject learnings if provided
        if learnings:
            if "[S] ..." in content and learnings.get("system"):
                s_block = "\n".join(f"- [S] {item}" for item in learnings["system"])
                content = content.replace("- [S] ...", s_block)
            if "[U] ..." in content and learnings.get("user"):
                u_block = "\n".join(f"- [U] {item}" for item in learnings["user"])
                content = content.replace("- [U] ...", u_block)

        target_path.write_text(content, encoding="utf-8")

        # Invalidate query cache
        invalidate_search_cache()

        receipt = self.generate_receipt(
            action="close_session",
            status="SUCCESS",
            details={
                "session_id": target_path.stem,
                "closed_at": end_time_iso,
                "verdict": verdict,
                "file_path": str(target_path),
            },
        )
        return receipt

    def recall_session(
        self,
        lines: int = 50,
        redact: bool = True,
    ) -> tuple[Path | None, str]:
        """
        Retrieve tail content of the most recent session log with permission & secret mode support.
        """
        perms = get_permissions()
        perms.gate("recall_session")

        target_path = self.get_current_session()
        if not target_path or not target_path.exists():
            return None, "No active session log found."

        content = target_path.read_text(encoding="utf-8")
        content_lines = content.splitlines()
        tail = content_lines[-lines:] if len(content_lines) > lines else content_lines
        tail_text = "\n".join(tail)

        if redact and perms.secret_mode:
            tail_text = perms.redact(tail_text)

        return target_path, tail_text

    def generate_receipt(
        self,
        action: str,
        status: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate a verifiable, machine-readable receipt for an operational action.
        """
        import uuid

        suffix = uuid.uuid4().hex[:8]
        return {
            "receipt_id": f"rcpt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{suffix}",
            "action": action,
            "status": status,
            "timestamp": datetime.now().astimezone().isoformat(),
            "details": details,
        }


# Singleton accessor
_session_service: SessionService | None = None


def get_session_service() -> SessionService:
    """Singleton accessor for SessionService."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
