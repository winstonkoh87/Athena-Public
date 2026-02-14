---
description: Unified Test Runner with Self-Healing capabilities. Detects test command, runs suite, and triggers deeper debugging on failure.
created: 2026-02-13
tags: [workflow, testing, qa, automation]
---

# /test — Universal Test Runner & Self-Healer

> **Latency Profile**: MEDIUM
> **Purpose**: "Red, Green, Refactor."
> **Mechanism**: Auto-detects test framework, runs suite, attempts diagnosis on failure.

## Phase 1: Tech Stack Detection

// turbo

```bash
if [ -f "package.json" ]; then
  TEST_CMD="npm test"
  echo "✅ Detected Node.js (npm test)"
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  TEST_CMD="pytest"
  echo "✅ Detected Python (pytest)"
else
  echo "⚠️ No standard test config found. Defaulting to 'echo No tests found'"
  TEST_CMD="echo 'No tests configured'"
fi
```

## Phase 2: Execution

// turbo

```bash
echo "🚀 Running tests..."
$TEST_CMD > .agent/temp/test_output.log 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All tests passed."
  cat .agent/temp/test_output.log | tail -n 5
else
  echo "❌ Tests FAILED. Exit code: $EXIT_CODE"
  echo "🔍 Analyzing failure..."
  cat .agent/temp/test_output.log | tail -n 20
  echo "💡 Recommendation: Run '/fix' to analyze .agent/temp/test_output.log"
fi
```

## Phase 3: Logging

// turbo

```bash
echo "$(date +%Y-%m-%d-%H:%M),test,$EXIT_CODE" >> .context/metrics/test_log.csv
```
