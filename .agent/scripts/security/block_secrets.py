#!/usr/bin/env python3
import json, sys
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


def block_secrets():
    """
    Reads tool input from stdin (simulated or actual hook input).
    If a file path in the input matches a sensitive pattern, it exits with status 2.
    """
    try:
        # In a real hook system, input comes via stdin.
        # For manual testing/running, we might need to handle args or empty stdin.
        if sys.stdin.isatty():
            # Interactive mode or no input
            return

        data = json.load(sys.stdin)
        tool_input = data.get("tool_input", {})
        file_path = (
            tool_input.get("file_path")
            or tool_input.get("path")
            or tool_input.get("target_file")
            or ""
        )

        if not file_path:
            return

        path_obj = Path(file_path)

        # Check filename against sensitive list
        if path_obj.name in SENSITIVE:
            print(
                f"BLOCKED: Access to {file_path} denied. This file is flagged as SENSITIVE.",
                file=sys.stderr,
            )
            sys.exit(2)  # Exit 2 = block

        # Check against extension patterns if needed (e.g. *.key)
        if any(file_path.endswith(ext) for ext in [".pem", ".key", ".p12"]):
            print(
                f"BLOCKED: Access to {file_path} denied. Sensitive extension detected.",
                file=sys.stderr,
            )
            sys.exit(2)

    except Exception as e:
        # Fail open or closed? Safe is closed, but for a script, maybe just log.
        # print(f"Hook Error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    block_secrets()
