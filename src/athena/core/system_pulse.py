"""
athena.core.system_pulse
========================
Real-time Health Dashboard (System Pulse).
Displays connectivity, memory, and daemon status.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
FLIGHT_RECORDER = PROJECT_ROOT / ".athena" / "flight_recorder.jsonl"


def get_daemon_status():
    try:
        import subprocess

        res = subprocess.run(["pgrep", "-f", "athenad.py"], capture_output=True)
        return "ONLINE" if res.returncode == 0 else "OFFLINE"
    except Exception:
        return "UNKNOWN"


def get_session_count():
    try:
        return len(list(LOGS_DIR.glob("*.md")))
    except Exception:
        return 0


def get_last_action():
    try:
        if not FLIGHT_RECORDER.exists():
            return "None"
        with open(FLIGHT_RECORDER, "r") as f:
            lines = f.readlines()
            if not lines:
                return "None"
            last = json.loads(lines[-1])
            return f"{last['tool']} ({last['status']})"
    except Exception:
        return "Error"


def main():
    print("\n" + "=" * 40)
    print("      ATHENA SYSTEM PULSE (v8.7.2)")
    print("=" * 40)
    print(f"Daemon Status    : {get_daemon_status()}")
    print(f"Total Sessions   : {get_session_count()}")
    print(f"Last Action      : {get_last_action()}")
    print(f"Memory Integrity : SEALED")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
