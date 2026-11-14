"""Unified SQLite connection and database path helpers for Athena."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_SQLITE_TIMEOUT = 5.0
_VALID_SYNCHRONOUS_MODES = frozenset({"OFF", "NORMAL", "FULL", "EXTRA"})


def connect_sqlite(
    db_path: str | Path,
    *,
    timeout: float = DEFAULT_SQLITE_TIMEOUT,
    wal: bool = True,
    synchronous: str | None = "NORMAL",
    check_same_thread: bool = True,
    row_factory: Any = None,
) -> sqlite3.Connection:
    """Open a SQLite connection configured with busy_timeout, optional WAL mode, and sync mode."""
    conn = sqlite3.connect(
        str(db_path),
        timeout=timeout,
        check_same_thread=check_same_thread,
    )
    busy_ms = max(0, int(round(timeout * 1000)))
    conn.execute(f"PRAGMA busy_timeout={busy_ms}")
    if wal:
        conn.execute("PRAGMA journal_mode=WAL")
    if synchronous is not None:
        sync_mode = synchronous.upper()
        if sync_mode not in _VALID_SYNCHRONOUS_MODES:
            conn.close()
            raise ValueError(f"Unsupported SQLite synchronous mode: {synchronous!r}")
        conn.execute(f"PRAGMA synchronous={sync_mode}")
    if row_factory is not None:
        conn.row_factory = row_factory
    return conn


def resolve_athena_db_path(project_root: Path | None = None) -> Path:
    """Resolve the active Athena SQLite database path (.athena/athena.db or .agent/inputs/athena.db)."""
    if project_root is None:
        from athena.core.config import PROJECT_ROOT

        root = PROJECT_ROOT
    else:
        root = Path(project_root)

    candidates = (
        root / ".athena" / "athena.db",
        root / ".agent" / "inputs" / "athena.db",
    )
    for candidate in candidates:
        try:
            if candidate.exists() and candidate.stat().st_size > 0:
                return candidate
        except OSError:
            continue
    return candidates[0]


__all__ = [
    "DEFAULT_SQLITE_TIMEOUT",
    "connect_sqlite",
    "resolve_athena_db_path",
]
