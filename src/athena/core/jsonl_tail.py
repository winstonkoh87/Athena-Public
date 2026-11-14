"""Bounded-tail JSONL reader and log-rotation helpers (stdlib-only).

Prevents O(N) full-file scans across MCP tools, Stop/Epistemic hooks, and
shutdown scripts when reading or rotating multi-megabyte JSONL telemetry logs.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def read_jsonl_tail_lines(
    path: Path,
    *,
    max_bytes: int = 65_536,
    max_lines: int = 50,
) -> list[str]:
    """Read up to the last ``max_lines`` non-empty lines using bounded EOF seek."""
    if not path.exists():
        return []
    try:
        size = path.stat().st_size
    except OSError:
        return []
    if size <= 0:
        return []

    read_size = min(size, max_bytes)
    try:
        with open(path, "rb") as f:
            if size > read_size:
                f.seek(size - read_size, os.SEEK_SET)
            raw = f.read(read_size)
    except OSError:
        return []

    if size > read_size:
        nl = raw.find(b"\n")
        if nl != -1:
            raw = raw[nl + 1 :]

    lines = [
        ln.strip()
        for ln in raw.decode("utf-8", errors="replace").splitlines()
        if ln.strip()
    ]
    return lines[-max_lines:] if max_lines > 0 else lines


def read_tail_jsonl_records(
    path: Path,
    *,
    max_bytes: int = 65_536,
    max_lines: int = 50,
) -> list[dict[str, Any]]:
    """Read up to the last ``max_lines`` valid JSON object records from the tail of ``path``."""
    records: list[dict[str, Any]] = []
    for line in read_jsonl_tail_lines(path, max_bytes=max_bytes, max_lines=max_lines):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except Exception:
            continue
    return records


def read_latest_jsonl_record(
    path: Path,
    *,
    max_bytes: int = 65_536,
) -> dict[str, Any] | None:
    """Return the newest valid JSON object from the tail of ``path``."""
    records = read_tail_jsonl_records(path, max_bytes=max_bytes, max_lines=20)
    return records[-1] if records else None


def rotate_jsonl_if_oversized(
    path: Path,
    *,
    max_bytes: int = 5_242_880,
    keep_lines: int = 5_000,
) -> bool:
    """If ``path`` exceeds ``max_bytes``, archive older lines to ``.archive.gz``
    and keep only the newest ``keep_lines`` in the active file.

    Returns True if rotation occurred.
    """
    if not path.exists():
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    if size <= max_bytes:
        return False

    try:
        import gzip

        lines = [
            ln
            for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip()
        ]
        if len(lines) <= keep_lines:
            return False

        archived, retained = lines[:-keep_lines], lines[-keep_lines:]
        archive_path = path.with_suffix(path.suffix + ".archive.gz")
        with gzip.open(archive_path, "at", encoding="utf-8") as gz:
            gz.write("\n".join(archived) + "\n")

        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tf:
                tf.write("\n".join(retained) + "\n")
            os.replace(tmp_name, str(path))
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)
            raise
        return True
    except Exception:
        return False


__all__ = [
    "read_jsonl_tail_lines",
    "read_latest_jsonl_record",
    "read_tail_jsonl_records",
    "rotate_jsonl_if_oversized",
]
