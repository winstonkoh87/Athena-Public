#!/usr/bin/env python3
"""PreToolUse (Read|Edit|Write) hook blocking reads/writes to sensitive credential files."""

import json
import sys
from pathlib import Path

# Config: Sensitive file patterns to block
SENSITIVE = {
    ".env",
    ".env.local",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
    ".pem",
    ".key",
}


def block_secrets() -> None:
    """Inspect hook stdin JSON; exit 2 on sensitive files or malformed input (fail-closed)."""
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

        path_obj = Path(file_path)

        if path_obj.name in SENSITIVE:
            print(
                f"BLOCKED: Access to {file_path} denied. This file is flagged as SENSITIVE.",
                file=sys.stderr,
            )
            sys.exit(2)

        if any(file_path.endswith(ext) for ext in (".pem", ".key", ".p12")):
            print(
                f"BLOCKED: Access to {file_path} denied. Sensitive extension detected.",
                file=sys.stderr,
            )
            sys.exit(2)

    except Exception as exc:
        print(
            f"BLOCKED (fail-closed): Secret protection gate error while inspecting input: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    block_secrets()
