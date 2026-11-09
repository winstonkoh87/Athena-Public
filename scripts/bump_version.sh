#!/usr/bin/env bash
# bump_version.sh — Athena-Public version sync tool
# Usage: ./scripts/bump_version.sh <old_version> <new_version>
# Example: ./scripts/bump_version.sh 9.4.9 9.5.0
#
# Bumps version references across all docs, wiki, and agent files.
# Excludes CHANGELOG.md (historical entries should keep their original version).

set -euo pipefail

# --- Argument Validation ---
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <old_version> <new_version>"
  echo "Example: $0 9.4.9 9.5.0"
  exit 1
fi

OLD_VERSION="$1"
NEW_VERSION="$2"

# Validate version format (X.Y.Z)
if ! echo "$OLD_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "❌ Invalid old version format: $OLD_VERSION (expected X.Y.Z)"
  exit 1
fi
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "❌ Invalid new version format: $NEW_VERSION (expected X.Y.Z)"
  exit 1
fi

# --- Resolve repo root ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Target files: v-prefixed versions (e.g., v9.5.1) ---
# These files use "v9.X.Y" format in badges, headers, etc.
VPREFIXED_FILES=(
  # Wiki (canonical docs mirror)
  "docs/wiki/FAQ.md"
  "docs/wiki/Getting-Started.md"
  "docs/wiki/Home.md"
  "docs/wiki/Workflow-Reference.md"
  "docs/wiki/Philosophy.md"
  "docs/wiki/Use-Cases.md"
  # Wiki (legacy fallbacks)
  "Athena-Public.wiki/FAQ.md"
  "Athena-Public.wiki/Getting-Started.md"
  "Athena-Public.wiki/Home.md"
  "Athena-Public.wiki/Workflow-Reference.md"
  "Athena-Public.wiki/Philosophy.md"
  "Athena-Public.wiki/Use-Cases.md"
  # Wiki (mirror)
  "wiki/FAQ.md"
  "wiki/Getting-Started.md"
  "wiki/Home.md"
  "wiki/Workflow-Reference.md"
  "wiki/Philosophy.md"
  "wiki/Use-Cases.md"
  # Docs
  "docs/ARCHITECTURE.md"
  "docs/SPEC_SHEET.md"
  # Root
  "AGENTS.md"
  "README.md"
)

# --- Target files: bare versions (e.g., 9.5.1, no 'v' prefix) ---
# These files use "9.X.Y" format in YAML/TOML/Python values.
BARE_FILES=(
  "athena.yaml"
  "pyproject.toml"
  "src/athena/__init__.py"
)

# --- Execution ---
echo "🔄 Athena-Public Version Bump"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  From: v${OLD_VERSION}"
echo "  To:   v${NEW_VERSION}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

UPDATED=0
SKIPPED=0
MISSING=0

# --- Pass 1: v-prefixed files ---
echo "📋 Pass 1: v-prefixed files (vX.Y.Z)"
for file in "${VPREFIXED_FILES[@]}"; do
  filepath="${REPO_ROOT}/${file}"
  
  if [[ ! -f "$filepath" ]]; then
    echo "⚠️  Missing: $file"
    ((MISSING++))
    continue
  fi
  
  if grep -q "v${OLD_VERSION}" "$filepath" 2>/dev/null; then
    sed -i '' "s/v${OLD_VERSION}/v${NEW_VERSION}/g" "$filepath"
    echo "✅ Updated: $file"
    ((UPDATED++))
  else
    echo "⏭️  Skipped: $file (no v${OLD_VERSION} found)"
    ((SKIPPED++))
  fi
done

# --- Pass 2: bare version files ---
echo ""
echo "📋 Pass 2: bare version files (X.Y.Z)"
for file in "${BARE_FILES[@]}"; do
  filepath="${REPO_ROOT}/${file}"
  
  if [[ ! -f "$filepath" ]]; then
    echo "⚠️  Missing: $file"
    ((MISSING++))
    continue
  fi
  
  # Use word-boundary-safe pattern to avoid partial matches
  if grep -q "\"${OLD_VERSION}\"\|'${OLD_VERSION}'\|: ${OLD_VERSION}" "$filepath" 2>/dev/null; then
    sed -i '' "s/\"${OLD_VERSION}\"/\"${NEW_VERSION}\"/g; s/'${OLD_VERSION}'/'${NEW_VERSION}'/g; s/: ${OLD_VERSION}/: ${NEW_VERSION}/g" "$filepath"
    echo "✅ Updated: $file"
    ((UPDATED++))
  else
    echo "⏭️  Skipped: $file (no ${OLD_VERSION} found)"
    ((SKIPPED++))
  fi
done

# --- CLAUDE.md is a symlink to AGENTS.md — auto-propagated ---
if [[ -L "${REPO_ROOT}/CLAUDE.md" ]]; then
  echo "🔗 CLAUDE.md (symlink → AGENTS.md) — auto-propagated"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Updated: ${UPDATED} files"
echo "  Skipped: ${SKIPPED} files"
echo "  Missing: ${MISSING} files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --- Verify no old versions remain (excluding CHANGELOG) ---
REMAINING=$(grep -rl "v${OLD_VERSION}" "${REPO_ROOT}" \
  --include="*.md" --include="*.yaml" --include="*.toml" --include="*.py" \
  2>/dev/null | grep -v CHANGELOG | grep -v '.git/' | grep -v 'bump_version.sh' || true)

if [[ -n "$REMAINING" ]]; then
  echo ""
  echo "⚠️  WARNING: v${OLD_VERSION} still found in:"
  echo "$REMAINING"
  echo "These may need manual review."
else
  echo ""
  echo "✅ Clean — no remaining v${OLD_VERSION} references (excluding CHANGELOG)."
fi

echo ""
echo "Next: git add -A && git commit -m \"chore: bump v${OLD_VERSION} → v${NEW_VERSION}\""
