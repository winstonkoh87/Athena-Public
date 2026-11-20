#!/usr/bin/env python3
"""PreToolUse (Edit|Write) hook blocking durable memory writes while session is tainted."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from athena.core.taint import is_protected_memory_path, is_tainted  # noqa: E402


def block_tainted_memory() -> None:
    """Inspect hook stdin JSON; exit 2 on tainted protected memory write or malformed input (fail-closed)."""
    try:
        if sys.stdin.isatty():
            return

        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object on stdin")

        tool_input = data.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            raise ValueError("Expected tool_input JSON object")

        file_path = (
            tool_input.get("file_path")
            or tool_input.get("path")
            or tool_input.get("target_file")
            or ""
        )
        if not file_path:
            return

        root_override = (
            os.environ.get("ATHENA_ROOT")
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or ""
        ).strip()
        project_root = Path(root_override) if root_override else REPO_ROOT

        if is_tainted(project_root=project_root) and is_protected_memory_path(
            str(file_path), project_root=project_root
        ):
            print(
                f"BLOCKED (taint quarantine): Durable memory write to {file_path} "
                "denied while session is tainted.",
                file=sys.stderr,
            )
            sys.exit(2)

    except SystemExit:
        raise
    except Exception as exc:
        print(
            f"BLOCKED (fail-closed): Taint memory gate error while inspecting input: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    block_tainted_memory()
