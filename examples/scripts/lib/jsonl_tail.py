"""Thin compatibility shim — canonical implementation lives in athena.core.jsonl_tail."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from athena.core.jsonl_tail import (
        read_jsonl_tail_lines,
        read_latest_jsonl_record,
        read_tail_jsonl_records,
        rotate_jsonl_if_oversized,
    )
except ImportError:
    _here = Path(__file__).resolve()
    for _parent in _here.parents:
        _src = _parent / "src"
        if (_src / "athena" / "core" / "jsonl_tail.py").is_file():
            if str(_src) not in sys.path:
                sys.path.insert(0, str(_src))
            break
    from athena.core.jsonl_tail import (
        read_jsonl_tail_lines,
        read_latest_jsonl_record,
        read_tail_jsonl_records,
        rotate_jsonl_if_oversized,
    )

__all__ = [
    "read_jsonl_tail_lines",
    "read_latest_jsonl_record",
    "read_tail_jsonl_records",
    "rotate_jsonl_if_oversized",
]
