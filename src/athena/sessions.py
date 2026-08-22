"""
athena.sessions
===============

Unified session lifecycle and checkpointing logic.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from athena.core.config import CONTEXT_DIR, SESSIONS_DIR, get_current_session_log


def parse_yaml_frontmatter(content: str) -> tuple[dict[str, Any], int]:
    """Extract YAML frontmatter from session log. Returns (metadata, body_start_index)."""
    import yaml

    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, 0

    yaml_content = match.group(1)
    body_start = match.end()

    try:
        metadata = yaml.safe_load(yaml_content)
        return metadata or {}, body_start
    except Exception:
        # Fallback: simple key-value parsing
        metadata = {}
        for line in yaml_content.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                if value and value != "null":
                    metadata[key] = value
        return metadata, body_start


def recall_last_session() -> Path | None:
    """
    Find and return the most recent session log file. Delegates to canonical SessionService.
    """
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().get_current_session()


def get_next_session_number(date_str: str | None = None) -> int:
    """Find the highest session number for today and return the next one. Delegates to canonical SessionService."""
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().get_next_session_number(date_str=date_str)


def update_forward_lineage(prev_session_id: str, current_session_id: str):
    """Update the previous session's YAML to point to the current session. Delegates to canonical SessionService."""
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().update_forward_lineage(prev_session_id, current_session_id)


def create_session(
    focus: str | None = None,
    tags: list[str] | None = None,
) -> Path:
    """Create a new session log with template. Delegates to canonical SessionService."""
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().create_session(focus=focus, tags=tags)


def close_session(
    session_path: Path | None = None,
    verdict: str = "🚀 SQUAD",
    learnings: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Close a session log and return a receipt. Delegates to canonical SessionService."""
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().close_session(
        session_path=session_path, verdict=verdict, learnings=learnings
    )


# Common Pattern constants for extraction
PLACEHOLDER_PATTERNS = [
    "**Insight**: ...",
    "**Decision**: ...",
    "**Pattern**: ...",
    "TODO:",
    "PLACEHOLDER",
]


def extract_lambda_stats(content: str) -> dict:
    """Parse [Λ+XX] tags to compute cognitive load metrics."""
    matches = re.findall(r"\[Λ\+(\d+)\]", content)
    values = [int(v) for v in matches]

    # Identify checkpoint headers (supports '### ⚡ Checkpoint [time]' and '### [time] Checkpoint')
    checkpoint_headers = re.findall(
        r"### (⚡ )?\[?\d{2}:\d{2}\s?(SGT)?\]? Checkpoint|### (⚡ )?Checkpoint \[?\d{2}:\d{2}\s?(SGT)?\]?",
        content,
    )
    checkpoint_count = len(checkpoint_headers)

    if not values:
        return {
            "peak": 0,
            "total": 0,
            "coverage": f"0/{checkpoint_count}",
            "coverage_n": 0,
            "coverage_d": checkpoint_count,
        }

    return {
        "peak": max(values),
        "total": sum(values),
        "coverage": f"{len(values)}/{checkpoint_count}",
        "coverage_n": len(values),
        "coverage_d": checkpoint_count,
    }


def extract_learnings(content: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """Extract [S], [U], [X], [L] learnings from the session log."""
    system_learnings = []
    user_learnings = []
    integration_requests = []
    local_learnings = []

    # Find Learnings section
    learnings_match = re.search(
        r"## 2\.5 Learnings.*?(?=\n## [^2]|\Z)", content, re.DOTALL
    )
    if not learnings_match:
        return [], [], [], []

    section = learnings_match.group(0)
    for match in re.findall(r"- \[S\]\s*(.+)", section):
        if match.strip() and match.strip() != "...":
            system_learnings.append(match.strip())

    for match in re.findall(r"- \[U\]\s*(.+)", section):
        if match.strip() and match.strip() != "...":
            user_learnings.append(match.strip())

    for match in re.findall(r"- \[X\]\s*(?!✅)(.+)", section):
        if match.strip() and match.strip() != "...":
            integration_requests.append(match.strip())

    for match in re.findall(r"- \[L\]\s*(.+)", section):
        if match.strip() and match.strip() != "...":
            local_learnings.append(match.strip())

    return system_learnings, user_learnings, integration_requests, local_learnings


def append_checkpoint(
    summary: str, bullets: list[str] | None = None, log_path: Path | None = None
) -> Path:
    """
    Append a checkpoint block to the session log. Delegates to canonical SessionService.
    """
    from athena.lifecycle.session_service import get_session_service

    return get_session_service().append_checkpoint(
        summary=summary, bullets=bullets, log_path=log_path
    )


def log_to_decision_ledger(summary: str, rationale: str | None = None):
    """
    Log high-stakes decisions to DECISION_LOG.md.
    """
    ledger_path = CONTEXT_DIR / "DECISION_LOG.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"\n## [{timestamp}] {summary}\n"
    if rationale:
        entry += f"**Rationale**: {rationale}\n"
    entry += "---\n"

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(entry)


def update_session_metadata(
    new_tokens: int = 0,
    thread_id: str | None = None,
    log_path: Path | None = None,
):
    """
    Update YAML frontmatter in session log.
    """
    if log_path is None:
        log_path = get_current_session_log()

    if not log_path or not log_path.exists():
        return

    content = log_path.read_text(encoding="utf-8")

    # Simple YAML extraction (assumes it starts with ---)
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml

                frontmatter = yaml.safe_load(parts[1]) or {}

                # Update logic
                frontmatter["tokens"] = frontmatter.get("tokens", 0) + new_tokens
                if thread_id:
                    frontmatter["thread_id"] = thread_id

                new_content = "---\n" + yaml.dump(frontmatter) + "---\n" + parts[2]
                log_path.write_text(new_content, encoding="utf-8")
        except Exception:
            # Fallback if YAML is malformed
            pass
