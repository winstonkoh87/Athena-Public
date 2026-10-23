#!/usr/bin/env bash
# scripts/gto_exec.sh — Scoped allowlist executor for GTO computation engines.
# =========================================================================
# Restricts execution strictly to approved numerical and calibration tools:
# 1. gto_engine.py (mcda, eev, kelly, ruin, monte-carlo, decision-mc)
# 2. calibration_score.py
#
# Exit codes:
#   0 = Success
#   1 = Usage error / Missing args
#   2 = BLOCKED: Unapproved action

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <action> [args...]" >&2
  echo "Allowed actions: mcda, eev, kelly, ruin, monte-carlo, decision-mc, robustness, barbell, devaluation, borrow-audit, calibration-score" >&2
  exit 1
fi

ACTION="$1"
shift

case "${ACTION}" in
  mcda|eev|kelly|ruin|monte-carlo|decision-mc|robustness|barbell|devaluation|borrow-audit)
    exec python3 "${REPO_ROOT}/src/athena/intelligence/gto_engine.py" --action "${ACTION}" "$@"
    ;;
  calibration-score)
    exec python3 "${REPO_ROOT}/.agent/scripts/calibration_score.py" "$@"
    ;;
  *)
    echo "Error: Unapproved action '${ACTION}'. gto_exec.sh is strictly restricted to approved GTO engines." >&2
    exit 2
    ;;
esac
