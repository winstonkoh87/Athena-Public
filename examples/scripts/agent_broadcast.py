#!/usr/bin/env python3
"""
Agent Broadcast (Protocol 410)

Real-time status broadcasting for multi-agent orchestration.

Usage:
    python3 agent_broadcast.py set working "Implementing Protocol 409"
    python3 agent_broadcast.py get
    python3 agent_broadcast.py watch
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

ATHENA_DIR = Path.home() / ".athena"
STATUS_FILE = ATHENA_DIR / "agent_status.json"

VALID_STATUSES = ["idle", "working", "needs_input", "finished", "error"]


def get_session_id() -> str:
    """Get current session ID from environment or default."""
    return os.environ.get("ATHENA_SESSION_ID", "unknown")


def get_agent_id() -> str:
    """Get agent ID from environment or generate one."""
    return os.environ.get("ATHENA_AGENT_ID", f"agent-{os.getpid()}")


def set_status(
    status: str, task: Optional[str] = None, progress: Optional[dict] = None
):
    """Update agent status for orchestration visibility."""
    if status not in VALID_STATUSES:
        print(f"❌ Invalid status. Must be one of: {VALID_STATUSES}")
        sys.exit(1)

    ATHENA_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "session_id": get_session_id(),
        "agent_id": get_agent_id(),
        "status": status,
        "current_task": task,
        "updated_at": datetime.now().isoformat(),
        "progress": progress,
    }

    STATUS_FILE.write_text(json.dumps(data, indent=2))
    print(f"📡 Status: {status}" + (f" — {task}" if task else ""))


def get_status() -> Optional[dict]:
    """Get current agent status."""
    if not STATUS_FILE.exists():
        print("⚠️  No status file found")
        return None

    data = json.loads(STATUS_FILE.read_text())

    print(f"📊 Agent Status:")
    print(f"   Session: {data.get('session_id')}")
    print(f"   Agent:   {data.get('agent_id')}")
    print(f"   Status:  {data.get('status')}")
    print(f"   Task:    {data.get('current_task', 'N/A')}")
    print(f"   Updated: {data.get('updated_at')}")

    if data.get("progress"):
        p = data["progress"]
        print(f"   Progress: {p.get('completed', 0)}/{p.get('total', '?')}")

    return data


def watch_status(interval: float = 1.0):
    """Watch for status changes."""
    print("👀 Watching for status changes (Ctrl+C to stop)...")

    last_data = None
    while True:
        try:
            if STATUS_FILE.exists():
                data = json.loads(STATUS_FILE.read_text())
                if data != last_data:
                    os.system("clear" if os.name == "posix" else "cls")
                    print(f"📡 Agent Status (live)")
                    print("=" * 40)
                    print(f"Session: {data.get('session_id')}")
                    print(f"Agent:   {data.get('agent_id')}")
                    print(f"Status:  {data.get('status')}")
                    print(f"Task:    {data.get('current_task', 'N/A')}")
                    print(f"Updated: {data.get('updated_at')}")
                    last_data = data
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Stopped watching")
            break


def clear_status():
    """Clear agent status."""
    if STATUS_FILE.exists():
        STATUS_FILE.unlink()
        print("✅ Status cleared")
    else:
        print("⚠️  No status to clear")


def main():
    if len(sys.argv) < 2:
        print("Agent Broadcast (Protocol 410)")
        print("")
        print("Usage:")
        print("  agent_broadcast.py set <status> [task] [completed] [total]")
        print("  agent_broadcast.py get")
        print("  agent_broadcast.py watch")
        print("  agent_broadcast.py clear")
        print("")
        print(f"Valid statuses: {', '.join(VALID_STATUSES)}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "set":
        if len(sys.argv) < 3:
            print("❌ Usage: agent_broadcast.py set <status> [task]")
            sys.exit(1)

        status = sys.argv[2]
        task = sys.argv[3] if len(sys.argv) > 3 else None

        progress = None
        if len(sys.argv) > 5:
            progress = {"completed": int(sys.argv[4]), "total": int(sys.argv[5])}

        set_status(status, task, progress)

    elif command == "get":
        get_status()

    elif command == "watch":
        watch_status()

    elif command == "clear":
        clear_status()

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
