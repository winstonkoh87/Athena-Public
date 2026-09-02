#!/usr/bin/env python3
"""
Athena Invocation Telemetry Logger
===================================
Appends a single JSONL record per workflow/skill/protocol invocation.
Designed to be called from any agent or hook.

Usage:
    python log_invocation.py --type workflow --name do --trigger "user command"
    python log_invocation.py --type skill --name red-team-review --trigger "auto: context match"
    python log_invocation.py --type protocol --name 075 --trigger "skill reference"

Output: Appends to .athena/invocations.jsonl
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = REPO_ROOT / ".athena" / "invocations.jsonl"


def log_invocation(
    invocation_type: str,
    name: str,
    trigger: str = "",
    session_id: str = "",
    tokens_in: int = 0,
    tokens_out: int = 0,
    latency_ms: int = 0,
    user_reaction: str = "",
    metadata: dict | None = None,
) -> dict:
    """Append a single invocation record to the JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": invocation_type,  # workflow | skill | protocol
        "name": name,
        "trigger": trigger,  # "user command" | "auto: context match" | "skill reference"
        "session_id": session_id,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency_ms,
        "user_reaction": user_reaction,  # "accepted" | "rejected" | "modified" | ""
    }
    if metadata:
        record["metadata"] = metadata

    # Ensure directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return record


def main():
    parser = argparse.ArgumentParser(
        description="Log an Athena invocation to telemetry"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["workflow", "skill", "protocol"],
        help="Type of invocation",
    )
    parser.add_argument("--name", required=True, help="Name of the invoked item")
    parser.add_argument(
        "--trigger", default="", help='How it was triggered (e.g., "user command")'
    )
    parser.add_argument("--session-id", default="", help="Current session ID")
    parser.add_argument("--tokens-in", type=int, default=0, help="Input tokens")
    parser.add_argument("--tokens-out", type=int, default=0, help="Output tokens")
    parser.add_argument("--latency-ms", type=int, default=0, help="Latency in ms")
    parser.add_argument(
        "--user-reaction", default="", help="User reaction to output"
    )

    args = parser.parse_args()
    record = log_invocation(
        invocation_type=args.type,
        name=args.name,
        trigger=args.trigger,
        session_id=args.session_id,
        tokens_in=args.tokens_in,
        tokens_out=args.tokens_out,
        latency_ms=args.latency_ms,
        user_reaction=args.user_reaction,
    )
    print(f"✅ Logged: {record['type']}/{record['name']} at {record['timestamp']}")


if __name__ == "__main__":
    main()
