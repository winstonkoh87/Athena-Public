#!/usr/bin/env bash
# ==============================================================================
# install_hooks.sh — Athena Enforcement Portability Installer
# ==============================================================================
# Sets core.hooksPath to .agent/hooks, verifies executable permissions on all
# hook scripts, and runs a diagnostic self-check.
#
# Usage:
#   ./.agent/scripts/install_hooks.sh
# ==============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🔧 Installing Athena Git Hooks & Portability Settings..."

# 1. Configure git core.hooksPath
git config core.hooksPath .agent/hooks
echo "  ✅ git config core.hooksPath set to .agent/hooks"

# 2. Ensure executable permissions on all hook scripts
chmod +x .agent/hooks/* 2>/dev/null || true
chmod +x .agent/scripts/*.py 2>/dev/null || true
chmod +x .agent/scripts/*.sh 2>/dev/null || true
echo "  ✅ Executable permissions granted on hooks & scripts"

# 3. Verify .claude/settings.json exists and is valid JSON
if [ -f ".claude/settings.json" ]; then
    python3 -c "import json; json.load(open('.claude/settings.json'))" 2>/dev/null && \
        echo "  ✅ .claude/settings.json syntax valid" || \
        echo "  ⚠️  .claude/settings.json contains invalid JSON"
else
    echo "  ⚠️  .claude/settings.json missing"
fi

# 4. Run harness score self-check
if [ -f ".agent/scripts/harness_score.py" ]; then
    python3 .agent/scripts/harness_score.py --check --min=35.0
fi

echo "🚀 Portability installation complete!"
