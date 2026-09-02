#!/usr/bin/env python3
"""
compact_context.py — Active Context Compactor (v3.0)
=====================================================
Prunes activeContext.md to keep it lean for boot token budgets.

Head/Tail Preservation (v3.0, from research):
- HEAD (## Current Focus, ## Active Tasks): NEVER pruned — identity/state.
- TAIL (## System Status): NEVER pruned — operational health.
- MIDDLE (## Recent Context, session markers): Target for aggressive pruning.

Trigger Rule: Run compaction when activeContext.md > 8,000 tokens OR > 100 lines.

Fixes applied:
- v2.0: Index-based line removal (no duplicate-line bugs).
- v2.0: Session completion marker pruning (prevents unbounded growth).
- v3.0: Head/tail preservation + documented trigger thresholds.
"""

import datetime
import os
import re
import shutil
from pathlib import Path

# Config
CONTEXT_FILE = ".context/memory_bank/activeContext.md"
MAX_VISIBLE_COMPLETED = 3
MAX_SESSION_MARKERS = 3
MAX_RECENT_CONTEXT_ENTRIES = 5  # Max session-level narrative blocks in Recent Context
MAX_RECENT_CONTEXT_AGE_HOURS = 48  # Prune narrative blocks older than this
SESSION_LOG_DIR = ".context/memories/session_logs"
SESSION_LOG_ARCHIVE = ".context/memories/session_logs/archive"
SESSION_ARCHIVE_DAYS = 7

# Compaction Trigger Thresholds (documented rule from research)
COMPACT_TOKEN_TRIGGER = 8_000  # Trigger compaction above this token count
COMPACT_LINE_TRIGGER = 100  # Trigger compaction above this line count

# Protected Sections (head/tail preservation — NEVER pruned)
# These section headers define the boundaries of protected content.
PROTECTED_HEAD_SECTIONS = {"## Current Focus", "## Active Tasks"}
PROTECTED_TAIL_SECTIONS = {"## System Status"}


def compact_active_context(aggressive: bool = False):
    """
    Scans activeContext.md and prunes:
    1. Completed [x] tasks beyond the last MAX_VISIBLE_COMPLETED.
    2. '## Session XXXX Completed' markers beyond the last MAX_SESSION_MARKERS.

    Args:
        aggressive: If True, use tighter limits (1 each) for token budget recovery.
    """
    max_completed = 1 if aggressive else MAX_VISIBLE_COMPLETED
    max_markers = 1 if aggressive else MAX_SESSION_MARKERS

    base_path = Path(os.getcwd())
    file_path = base_path / CONTEXT_FILE

    if not file_path.exists():
        print(f"❌ Error: {CONTEXT_FILE} not found.")
        return

    content = file_path.read_text(encoding="utf-8")
    modified = False

    # --- Phase 1: Prune completed tasks (index-based) ---
    sections = re.split(r"(^## .*$)", content, flags=re.MULTILINE)

    out_sections = []
    compacted_items = []

    for i in range(len(sections)):
        part = sections[i]

        # Check if this part is the body of "Active Tasks"
        is_active_task_body = False
        if i > 0 and "## Active Tasks" in sections[i - 1]:
            is_active_task_body = True

        if is_active_task_body:
            body_lines = part.splitlines()

            # Find indices of all completed tasks
            completed_indices = [
                idx
                for idx, line in enumerate(body_lines)
                if line.strip().startswith("- [x]")
            ]

            if len(completed_indices) > max_completed:
                num_to_remove = len(completed_indices) - max_completed
                indices_to_remove = set(completed_indices[:num_to_remove])
                compacted_items.extend(
                    body_lines[idx] for idx in sorted(indices_to_remove)
                )

                # Rebuild block excluding removed indices
                kept_lines = [
                    line
                    for idx, line in enumerate(body_lines)
                    if idx not in indices_to_remove
                ]
                out_sections.append("\n".join(kept_lines))
                modified = True
                print(f"✅ Compacted {num_to_remove} completed tasks.")
            else:
                out_sections.append(part)
        else:
            out_sections.append(part)

    final_content = "".join(out_sections)

    # Append compacted items to Recent Context if any
    if compacted_items:
        log_header = "## Recent Context"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        compaction_block = f"\n- **Compacted {timestamp}**:\n" + "\n".join(
            [f"  {item.strip().replace('- [x]', '- ')}" for item in compacted_items]
        )

        if log_header in final_content:
            parts = final_content.split(log_header)
            final_content = parts[0] + log_header + "\n" + compaction_block + parts[1]
        else:
            final_content += f"\n\n{log_header}\n{compaction_block}\n"

    # --- Phase 2: Prune session completion markers ---
    session_pattern = re.compile(r"^## Session \S+ Completed$", re.MULTILINE)
    session_markers = list(session_pattern.finditer(final_content))

    if len(session_markers) > max_markers:
        # Keep only the last N markers, remove the rest
        markers_to_remove = session_markers[:-max_markers]
        # Remove in reverse order to preserve indices
        for marker in reversed(markers_to_remove):
            # Remove the marker line and any trailing whitespace
            start = marker.start()
            end = marker.end()
            # Also consume trailing newlines
            while end < len(final_content) and final_content[end] == "\n":
                end += 1
            final_content = final_content[:start] + final_content[end:]
            modified = True

        removed_count = len(markers_to_remove)
        print(f"✅ Pruned {removed_count} old session completion markers.")

    # --- Phase 3: Prune old Recent Context narrative entries ---
    max_entries = 2 if aggressive else MAX_RECENT_CONTEXT_ENTRIES
    age_limit_hours = 24 if aggressive else MAX_RECENT_CONTEXT_AGE_HOURS

    # Split on the Recent Context header
    rc_header = "## Recent Context"
    if rc_header in final_content:
        rc_parts = final_content.split(rc_header, 1)
        rc_body = rc_parts[1]

        # Find the next ## header to bound the Recent Context section
        next_header_match = re.search(r"^## (?!Recent Context)", rc_body, re.MULTILINE)
        if next_header_match:
            rc_section = rc_body[: next_header_match.start()]
            rc_remainder = rc_body[next_header_match.start() :]
        else:
            rc_section = rc_body
            rc_remainder = ""

        # Parse date-stamped entries (e.g. "- **Session 2026-02-20 (Evening)**:" or "- **Compacted 2026-02-20**:")
        date_pattern = re.compile(
            r"^- \*\*(?:Session|Compacted)\s+(\d{4}-\d{2}-\d{2})",
            re.MULTILINE,
        )

        entries = list(date_pattern.finditer(rc_section))
        if entries:
            now = datetime.datetime.now()
            cutoff = now - datetime.timedelta(hours=age_limit_hours)

            # Determine start/end byte offsets for each entry
            entry_spans = []
            for i, match in enumerate(entries):
                start = match.start()
                end = (
                    entries[i + 1].start() if i + 1 < len(entries) else len(rc_section)
                )
                try:
                    entry_date = datetime.datetime.strptime(match.group(1), "%Y-%m-%d")
                except ValueError:
                    continue
                entry_spans.append((start, end, entry_date))

            # Split into keep and prune
            to_keep = [s for s in entry_spans if s[2] >= cutoff]
            to_prune = [s for s in entry_spans if s[2] < cutoff]

            # Also enforce max entries (keep most recent N)
            if len(to_keep) > max_entries:
                # Sort by date descending, keep only the most recent
                to_keep.sort(key=lambda x: x[2], reverse=True)
                overflow = to_keep[max_entries:]
                to_keep = to_keep[:max_entries]
                to_prune.extend(overflow)

            if to_prune:
                # Rebuild the section from kept entries only
                to_keep.sort(key=lambda x: x[0])  # Restore original order
                kept_text = "".join(rc_section[s[0] : s[1]] for s in to_keep)

                # Also preserve any non-date-stamped content before the first entry
                preamble = rc_section[: entries[0].start()] if entries else ""

                new_rc_section = preamble + kept_text
                final_content = rc_parts[0] + rc_header + new_rc_section + rc_remainder
                modified = True
                print(
                    f"✅ Pruned {len(to_prune)} old Recent Context entries (>{age_limit_hours}h or >{max_entries} cap)."
                )

    # --- Write Back ---
    if modified:
        file_path.write_text(final_content, encoding="utf-8")
        print("✅ activeContext.md compacted successfully.")
    else:
        print("⚡ No compaction needed.")


def archive_old_sessions():
    """
    Moves session logs older than SESSION_ARCHIVE_DAYS to the archive directory.
    """
    base_path = Path(os.getcwd())
    log_dir = base_path / SESSION_LOG_DIR
    archive_dir = base_path / SESSION_LOG_ARCHIVE

    if not log_dir.exists():
        return

    archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.datetime.now() - datetime.timedelta(days=SESSION_ARCHIVE_DAYS)
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-session-\d+\.md")
    archived = 0

    for f in log_dir.glob("*-session-*.md"):
        match = pattern.match(f.name)
        if match:
            try:
                file_date = datetime.datetime.strptime(match.group(1), "%Y-%m-%d")
                if file_date < cutoff:
                    shutil.move(str(f), str(archive_dir / f.name))
                    archived += 1
            except ValueError:
                continue

    if archived > 0:
        print(
            f"📦 Archived {archived} session logs (>{SESSION_ARCHIVE_DAYS} days old)."
        )


if __name__ == "__main__":
    compact_active_context()
    archive_old_sessions()
