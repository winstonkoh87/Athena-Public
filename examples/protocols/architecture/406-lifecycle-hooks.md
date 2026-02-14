---
title: "Lifecycle Hooks"
id: 406
type: architecture
author: [AUTHOR] (Stolen from Claude Code)
created: 2026-02-02
source: r/ClaudeAI - "7 Claude Code Power Tips Nobody's Talking About"
tags: [architecture, hooks, middleware, guardrails, stolen]
---

# Protocol 406: Lifecycle Hooks

> **Philosophy**: "Intercept everything. Trust nothing."

## 1. The Core Pattern

**Problem**: AI agents execute tools without systematic pre/post checks. Security, linting, and validation happen inconsistently (or not at all).

**Solution**: **Hook system** that intercepts tool calls at two points:

1. **PreToolUse**: Before execution (can block)
2. **PostToolUse**: After execution (can trigger follow-ups)

---

## 2. Architecture

### 2.1 Hook Configuration

Location: `.athena/hooks.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "run_command|Bash",
        "hooks": [
          { "type": "command", "command": ".agent/scripts/hooks/pre_command_check.sh" }
        ]
      },
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          { "type": "command", "command": ".agent/scripts/hooks/pre_write_check.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          { "type": "command", "command": ".agent/scripts/hooks/post_lint.sh" }
        ]
      },
      {
        "matcher": "git commit",
        "hooks": [
          { "type": "command", "command": ".agent/scripts/hooks/post_commit_review.sh" }
        ]
      }
    ]
  }
}
```

### 2.2 Hook Behavior

| Exit Code | Meaning |
|-----------|---------|
| 0 | Continue execution |
| 1 | Log warning, continue |
| 2 | **Block action** (PreToolUse only) |

### 2.3 Hook Input

Hooks receive JSON on stdin:

```json
{
  "tool": "write_to_file",
  "timestamp": "2026-02-02T03:30:00+08:00",
  "arguments": {
    "TargetFile": "/path/to/file.py",
    "CodeContent": "..."
  }
}
```

---

## 3. Example Hooks

### 3.1 Pre-Command Security Check

File: `.agent/scripts/hooks/pre_command_check.sh`

```bash
#!/bin/bash
# Block dangerous commands

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.arguments.CommandLine // empty')

# Blocklist
if echo "$CMD" | grep -qE 'rm -rf /|sudo|chmod 777|curl.*\|.*sh'; then
    echo "🚫 BLOCKED: Dangerous command pattern detected" >&2
    exit 2
fi

exit 0
```

### 3.2 Post-Write Linting

File: `.agent/scripts/hooks/post_lint.sh`

```bash
#!/bin/bash
# Auto-lint after file writes

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.arguments.TargetFile // empty')

if [[ "$FILE" == *.py ]]; then
    black "$FILE" --quiet 2>/dev/null || true
    ruff check "$FILE" --fix --quiet 2>/dev/null || true
elif [[ "$FILE" == *.js ]] || [[ "$FILE" == *.ts ]]; then
    prettier --write "$FILE" 2>/dev/null || true
elif [[ "$FILE" == *.md ]]; then
    # Skip markdown linting for now
    :
fi

exit 0
```

### 3.3 Secret Scan (Pre-Write)

File: `.agent/scripts/hooks/pre_write_check.sh`

```bash
#!/bin/bash
# Scan for secrets before writing

INPUT=$(cat)
CONTENT=$(echo "$INPUT" | jq -r '.arguments.CodeContent // empty')

# Check for common secret patterns
if echo "$CONTENT" | grep -qE 'sk-[a-zA-Z0-9]{20,}|AKIA[A-Z0-9]{16}|ghp_[a-zA-Z0-9]{36}'; then
    echo "🚫 BLOCKED: Potential secret detected in file content" >&2
    exit 2
fi

exit 0
```

---

## 4. Integration with Athena

### 4.1 Wrapper Script

Since Antigravity/Athena doesn't have native hooks, we implement via wrapper:

File: `.agent/scripts/tool_wrapper.py`

```python
#!/usr/bin/env python3
"""
Wrapper that intercepts tool calls and runs hooks.

This is a CONCEPT - actual integration depends on platform capabilities.
"""

import json
import subprocess
from pathlib import Path

HOOKS_CONFIG = Path(__file__).parent.parent.parent / ".athena" / "hooks.json"

def load_hooks():
    if HOOKS_CONFIG.exists():
        return json.loads(HOOKS_CONFIG.read_text())
    return {"hooks": {}}

def run_hooks(phase: str, tool_name: str, arguments: dict) -> bool:
    """Run matching hooks. Returns False if action should be blocked."""
    config = load_hooks()
    hooks = config.get("hooks", {}).get(phase, [])
    
    payload = json.dumps({
        "tool": tool_name,
        "arguments": arguments
    })
    
    for hook_group in hooks:
        import re
        if re.search(hook_group["matcher"], tool_name, re.IGNORECASE):
            for hook in hook_group["hooks"]:
                if hook["type"] == "command":
                    result = subprocess.run(
                        hook["command"],
                        shell=True,
                        input=payload,
                        text=True,
                        capture_output=True
                    )
                    if result.returncode == 2:
                        print(f"⛔ Hook blocked action: {result.stderr}")
                        return False
    return True
```

### 4.2 Manual Invocation

Until native support exists, invoke hooks manually in workflows:

```bash
# Before running a command
echo '{"tool":"run_command","arguments":{"CommandLine":"rm -rf temp/"}}' | \
    .agent/scripts/hooks/pre_command_check.sh
```

---

## 5. Future: Native Platform Support

If/when Antigravity adds hook support, migrate to:

```json
// .gemini/hooks.json or equivalent
{
  "PreToolUse": [...],
  "PostToolUse": [...]
}
```

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Protocol created. Stolen from Claude Code hook architecture. |

---

# protocol #architecture #hooks #security #stolen #claude-code
