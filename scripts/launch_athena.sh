#!/bin/bash
# launch_athena.sh
# ============================================================================
# Purpose: Launch the Active OS Daemon (Athena Sidecar/Watcher)
# Usage:   ./launch_athena.sh [--background]
# ============================================================================

set -e

# Resolve Project Root (Assuming this script is in Athena-Public/scripts/)
# Structure: Project Athena/Athena-Public/scripts/launch_athena.sh
# Root:      Project Athena/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Locate Daemon Script
DAEMON_SCRIPT="$PROJECT_ROOT/src/athena/core/athenad.py"

if [[ ! -f "$DAEMON_SCRIPT" ]]; then
    echo "❌ Error: Daemon script not found at $DAEMON_SCRIPT"
    exit 1
fi

echo "🚀 Launching Athena Daemon..."
echo "   Target: $DAEMON_SCRIPT"

if [[ "$1" == "--background" ]]; then
    # Run in background and detach
    nohup python3 "$DAEMON_SCRIPT" > "$PROJECT_ROOT/athenad.log" 2>&1 &
    PID=$!
    echo "✅ Athena Daemon started in background."
    echo "   PID: $PID"
    echo "   Log: $PROJECT_ROOT/athenad.log"
    
    echo "$PID" > "$PROJECT_ROOT/.athenad.pid"
elif [[ "$1" == "--stop" ]]; then
    # Stop the daemon
    PID_FILE="$PROJECT_ROOT/.athenad.pid"
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🛑 Stopping Athena Daemon (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            echo "✅ Daemon stopped."
        else
            echo "⚠️  Daemon process $PID not found. Cleaning up pidfile."
            rm "$PID_FILE"
        fi
    else
        echo "⚠️  No .athenad.pid found. Is the daemon running?"
    fi
else
    # Run in foreground
    python3 "$DAEMON_SCRIPT"
fi
