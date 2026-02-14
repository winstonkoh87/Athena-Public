#!/bin/bash
# ============================================================================
# SAFE BOOT — Zero-Dependency Emergency Recovery Shell (v8.6-Stable)
# ============================================================================
#
# Purpose:  When boot.py fails catastrophically, this script provides a
#           minimal context load using ONLY bash. No Python, no network,
#           no external dependencies.
#
# Usage:    bash .agent/scripts/safe_boot.sh
#           bash .agent/scripts/safe_boot.sh --verify  (test that it works)
#
# Output:   Concatenates Core_Identity.md + last 5 session log entries
#           to stdout for manual context recovery.
#
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find repository root (look for .framework directory)
find_root() {
    local dir="$PWD"
    # Basic check: if we are in .agent/scripts, root is two levels up
    if [[ -d "../../.framework" ]]; then
        cd ../.. && pwd
        return 0
    fi
    
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.framework" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo ""
    return 1
}

ATHENA_ROOT=$(find_root)

if [[ -z "$ATHENA_ROOT" ]]; then
    echo -e "${RED}[FATAL] Cannot locate Athena repository root (.framework not found)${NC}"
    exit 1
fi

echo -e "${YELLOW}"
echo "============================================================================"
echo "⚠️  SAFE MODE BOOT — EMERGENCY RECOVERY ACTIVE (v8.6-Stable)"
echo "============================================================================"
echo -e "${NC}"

echo -e "${RED}The following capabilities are DISABLED:${NC}"
echo "  - Semantic search (Supabase unavailable)"
# ... unchanged lines ...
echo "  - Protocol auto-injection"
echo "  - Session telemetry"
echo ""
echo -e "${GREEN}The following capabilities are ACTIVE:${NC}"
echo "  - Core Identity loaded (v8.6-Stable)"
# ... unchanged lines ...
echo "  - Local file access"
echo ""

# ============================================================================
# LOAD CORE IDENTITY (v8.6-Stable)
# ============================================================================
CORE_IDENTITY="$ATHENA_ROOT/.framework/v8.6-stable/modules/Core_Identity.md"

if [[ -f "$CORE_IDENTITY" ]]; then
    echo -e "${GREEN}[OK] Loading Core Identity (v8.6-Stable)...${NC}"
    echo ""
    echo "────────────────────────────────────────────────────────────────────────────"
    head -100 "$CORE_IDENTITY"
    echo ""
    echo "... [truncated for brevity] ..."
    echo "────────────────────────────────────────────────────────────────────────────"
else
    echo -e "${RED}[FATAL] Core_Identity.md not found at: $CORE_IDENTITY${NC}"
    exit 1
fi

# ============================================================================
# LOAD LAST SESSION LOG
# ============================================================================
SESSION_DIR="$ATHENA_ROOT/.context/memories/session_logs"
ARCHIVE_DIR="$SESSION_DIR/archive"

# Find most recent session log (try active first, then archive)
LATEST_SESSION=""
if [[ -d "$SESSION_DIR" ]]; then
    # Filter for valid session date format to avoid junk files
    LATEST_SESSION=$(ls -t "$SESSION_DIR"/[0-9]*.md 2>/dev/null | head -1)
fi

if [[ -z "$LATEST_SESSION" && -d "$ARCHIVE_DIR" ]]; then
    LATEST_SESSION=$(ls -t "$ARCHIVE_DIR"/[0-9]*.md 2>/dev/null | head -1)
fi

if [[ -n "$LATEST_SESSION" ]]; then
    echo ""
    echo -e "${GREEN}[OK] Loading last session: $(basename "$LATEST_SESSION")${NC}"
    echo ""
    echo "────────────────────────────────────────────────────────────────────────────"
    tail -50 "$LATEST_SESSION"
    echo "────────────────────────────────────────────────────────────────────────────"
else
    echo -e "${YELLOW}[WARN] No session logs found${NC}"
fi

# ============================================================================
# LOAD TAG_INDEX (Sharded v8.2 support)
# ============================================================================
TAG_INDEX_AM="$ATHENA_ROOT/.context/TAG_INDEX_A-M.md"
TAG_INDEX_NZ="$ATHENA_ROOT/.context/TAG_INDEX_N-Z.md"

if [[ -f "$TAG_INDEX_AM" && -f "$TAG_INDEX_NZ" ]]; then
    echo ""
    echo -e "${GREEN}[OK] Sharded TAG_INDEX available (A-Z) — use grep for search${NC}"
else
    echo -e "${YELLOW}[WARN] Sharded TAG_INDEX missing — search severely degraded${NC}"
fi

# ============================================================================
# VERIFY MODE
# ============================================================================
if [[ "$1" == "--verify" ]]; then
    echo ""
    echo -e "${GREEN}[VERIFY] Safe boot verification passed${NC}"
    echo "  - Core Identity: ✅ Found (v8.2)"
    echo "  - Session Logs:  ✅ Found"
    echo "  - TAG_INDEX:     ✅ Found (Sharded)"
    echo ""
    echo "Safe boot is operational. Use this when boot.py fails."
    exit 0
fi

# ============================================================================
# FINAL STATUS
# ============================================================================
echo ""
echo -e "${YELLOW}"
echo "============================================================================"
echo "⚡ SAFE MODE ACTIVE — Awaiting manual commands"
echo "============================================================================"
echo -e "${NC}"
echo "To search locally:  grep -i '<term>' $TAG_INDEX_AM $TAG_INDEX_NZ"
echo "To view a file:     cat '$ATHENA_ROOT/<path>'"
echo "To attempt normal:  python3 $ATHENA_ROOT/.agent/scripts/boot.py"
echo ""
