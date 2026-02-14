#!/bin/bash
set -e

# Configuration
PRIVATE_REPO="/Users/[AUTHOR]/Desktop/Project Athena"
PUBLIC_REPO="/Users/[AUTHOR]/Desktop/Project Athena/Athena-Public"
VERSION="v1.0.0"

echo "🚀 Deploying Athena-Public $VERSION..."

# 1. Sync Logic (Simulated for Demo - In real life we'd cp specific files)
# For v1.0.0, we assume files are already staged or we are just tagging.
# Let's just run the git operations as defined in Step 4 of the workflow.

cd "$PUBLIC_REPO"

# Update version (if needed, but assumed done)
# Verify status
git status

# Commit
echo "💾 Committing v1.0.0 Release Candidate..."
git add .
git commit -m "Release $VERSION: The Anti-Fragile Update" --allow-empty

# Tag
echo "🏷️  Tagging $VERSION..."
# Delete if exists locally/remotely to force update (Dev mode)
git tag -d $VERSION 2>/dev/null || true
git push --delete origin $VERSION 2>/dev/null || true

git tag -a $VERSION -m "Release $VERSION"

# Push
echo "🚀 Pushing to GitHub..."
git push origin main
git push origin $VERSION

echo "✅ Deployment Complete: $VERSION"
