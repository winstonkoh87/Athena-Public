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

# Locate Daemon Script (Sidecar is the current active watcher)
DAEMON_SCRIPT="$PROJECT_ROOT/.agent/scripts/sidecar.py"

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
    
    # Save PID (Optional)
    echo "$PID" > "$PROJECT_ROOT/.athenad.pid"
else
    # Run in foreground
    python3 "$DAEMON_SCRIPT"
fi
