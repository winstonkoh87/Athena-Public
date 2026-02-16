"""
athena.core.flight_recorder
===========================
Immutable Action Log (The Black Box).
Records every high-stakes tool call (Write, Delete, Git) for forensic audit.
"""

import json
import time
import os
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_FILE = PROJECT_ROOT / ".athena" / "flight_recorder.jsonl"


def record_action(
    tool_name: str,
    params: Dict[str, Any],
    status: str = "initiated",
    rationale: str = "",
):
    """
    Writes an action entry to the immutable log.
    """
    entry = {
        "timestamp": time.time(),
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "tool": tool_name,
        "params": params,
        "status": status,
        "rationale": rationale,
        "pid": os.getpid(),
    }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        # We don't want to crash the system if logging fails, but it's a blind spot.
        print(f"⚠️ Flight Recorder Failure: {e}")


if __name__ == "__main__":
    # Test
    record_action("test_action", {"key": "value"}, rationale="Testing flight recorder.")
    print(f"Action recorded to {LOG_FILE}")
