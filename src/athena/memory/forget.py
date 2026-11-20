"""
athena.memory.forget
====================

Atomic cross-layer memory erasure (`athena memory forget <phrase>`).

Removes literal case-insensitive matches across local memory stores
(`.athena/memory/USER_PROFILE.yaml`, `.athena/memory/SYSTEM_LEARNINGS.md`,
and optionally `.context/memory_bank/` and session logs), then scrubs local
search caches and SQLite FTS rows so erased facts never ghost back into recall.

Dry-run by default; requires `dry_run=False` (`--apply`) to mutate disk.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from athena.core import config
from athena.core.cache import invalidate_search_cache
from athena.memory import learnings as learnings_mod
from athena.memory.learnings import _ROW_DATE_RE, atomic_write_text

logger = logging.getLogger(__name__)

yaml: Any = None
try:
    import yaml as _yaml

    yaml = _yaml
    _YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    _HAS_YAML = True
except ImportError:
    _YAML_LOADER = None
    _HAS_YAML = False


def _rel_display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _forget_user_profile(
    user_file: Path,
    needle_lower: str,
    *,
    dry_run: bool,
) -> int:
    if not user_file.is_file() or not _HAS_YAML or _YAML_LOADER is None:
        return 0

    raw_text = user_file.read_text(encoding="utf-8", errors="replace")
    data = yaml.load(raw_text, Loader=_YAML_LOADER)
    if not isinstance(data, dict):
        return 0

    raw_notes = data.get("notes")
    if not isinstance(raw_notes, list) or not raw_notes:
        return 0

    header_lines: list[str] = []
    for line in raw_text.splitlines():
        if line.startswith("#") or not line.strip():
            header_lines.append(line)
        else:
            break
    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    kept_notes: list[Any] = []
    removed = 0
    for item in raw_notes:
        if isinstance(item, dict):
            haystack = " ".join(
                str(v)
                for k, v in item.items()
                if k in ("learned", "session", "note", "text", "topic") or isinstance(v, str)
            ).lower()
        else:
            haystack = str(item or "").lower()

        if needle_lower in haystack:
            removed += 1
        else:
            kept_notes.append(item)

    if removed > 0 and not dry_run:
        new_data = dict(data)
        new_data["notes"] = kept_notes
        yaml_str = yaml.dump(new_data, sort_keys=False, allow_unicode=True)
        header_block = "\n".join(header_lines) + "\n\n" if header_lines else ""
        atomic_write_text(user_file, header_block + yaml_str, mode=0o600)

    return removed


def _forget_system_learnings(
    system_file: Path,
    needle_lower: str,
    *,
    dry_run: bool,
) -> int:
    if not system_file.is_file():
        return 0

    raw_text = system_file.read_text(encoding="utf-8", errors="replace")
    lines = raw_text.splitlines()
    kept_lines: list[str] = []
    removed = 0

    for line in lines:
        stripped = line.strip()
        is_row = bool(_ROW_DATE_RE.match(stripped))
        if is_row and needle_lower in line.lower():
            removed += 1
            continue
        kept_lines.append(line)

    if removed > 0 and not dry_run:
        trailing = "\n" if raw_text.endswith("\n") or kept_lines else ""
        atomic_write_text(system_file, "\n".join(kept_lines) + trailing, mode=0o600)

    return removed


def _forget_markdown_lines(
    md_file: Path,
    needle_lower: str,
    *,
    dry_run: bool,
) -> int:
    if not md_file.is_file():
        return 0

    raw_text = md_file.read_text(encoding="utf-8", errors="replace")
    lines = raw_text.splitlines()
    kept_lines: list[str] = []
    removed = 0

    for line in lines:
        if needle_lower in line.lower():
            removed += 1
            continue
        kept_lines.append(line)

    if removed > 0 and not dry_run:
        trailing = "\n" if raw_text.endswith("\n") or kept_lines else ""
        atomic_write_text(md_file, "\n".join(kept_lines) + trailing, mode=0o600)

    return removed


def _escape_like(needle_lower: str) -> str:
    escaped = needle_lower.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _scrub_caches(root: Path, needle_lower: str) -> bool:
    learnings_mod._STORE_CACHE.clear()
    try:
        invalidate_search_cache()
    except Exception as exc:
        logger.debug("Global search cache invalidation skipped: %s", exc)

    cache_file = root / ".agent" / "cache" / "search_cache.json"
    if cache_file.is_file():
        try:
            atomic_write_text(cache_file, json.dumps({}, indent=2) + "\n", mode=0o600)
        except OSError as exc:
            logger.debug("Local search cache scrub failed for %s: %s", cache_file, exc)

    fts_db = root / ".athena" / "exocortex_fts.db"
    if fts_db.is_file():
        like_pat = _escape_like(needle_lower)
        try:
            with sqlite3.connect(fts_db) as conn:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
                if "search_index" in tables:
                    conn.execute(
                        "DELETE FROM search_index "
                        "WHERE lower(content) LIKE ? ESCAPE '\\' OR lower(title) LIKE ? ESCAPE '\\'",
                        (like_pat, like_pat),
                    )
                    conn.commit()
        except sqlite3.Error as exc:
            logger.debug("FTS cache scrub skipped for %s: %s", fts_db, exc)

    return True


def forget_phrase(
    phrase: str,
    *,
    project_root: Path | None = None,
    dry_run: bool = True,
    include_context: bool = False,
    include_logs: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Erase literal case-insensitive matches across local memory stores and caches."""
    cleaned = str(phrase or "").strip()
    if not cleaned:
        raise ValueError("Phrase cannot be empty")
    if len(cleaned) < 4 and not force:
        raise ValueError("Phrase must be at least 4 characters (pass force=True to override)")

    root = Path(project_root) if project_root is not None else config.PROJECT_ROOT
    needle_lower = cleaned.lower()

    user_file = root / ".athena" / "memory" / "USER_PROFILE.yaml"
    system_file = root / ".athena" / "memory" / "SYSTEM_LEARNINGS.md"

    details: list[dict[str, Any]] = []
    files_scanned = 0
    files_matched = 0
    entries_removed = 0

    def _record(path: Path, count: int) -> None:
        nonlocal files_scanned, files_matched, entries_removed
        if path.is_file():
            files_scanned += 1
        if count > 0:
            files_matched += 1
            entries_removed += count
            details.append({"path": _rel_display(path, root), "removed": count})

    _record(user_file, _forget_user_profile(user_file, needle_lower, dry_run=dry_run))
    _record(system_file, _forget_system_learnings(system_file, needle_lower, dry_run=dry_run))

    if include_context:
        for ctx_file in (
            root / ".context" / "memory_bank" / "activeContext.md",
            root / ".context" / "memory_bank" / "semantic_log.md",
        ):
            _record(ctx_file, _forget_markdown_lines(ctx_file, needle_lower, dry_run=dry_run))

    if include_logs:
        logs_dir = root / ".context" / "memories" / "session_logs"
        if logs_dir.is_dir():
            for log_file in sorted(logs_dir.glob("*.md")):
                _record(log_file, _forget_markdown_lines(log_file, needle_lower, dry_run=dry_run))

    cache_invalidated = False
    if not dry_run and entries_removed > 0:
        cache_invalidated = _scrub_caches(root, needle_lower)

    return {
        "phrase": cleaned,
        "dry_run": dry_run,
        "files_scanned": files_scanned,
        "files_matched": files_matched,
        "entries_removed": entries_removed,
        "cache_invalidated": cache_invalidated,
        "details": details,
    }
