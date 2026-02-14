---
title: "JIT Context Injection"
id: 405
type: workflow
author: [AUTHOR] (Stolen from Claude Code)
created: 2026-02-02
source: r/ClaudeAI - "7 Claude Code Power Tips Nobody's Talking About"
tags: [workflow, prompting, dynamic, preprocessing, stolen]
---

# Protocol 405: JIT Context Injection

> **Philosophy**: "Don't describe the state. Inject the state."

## 1. The Core Pattern

**Problem**: Traditional prompts reference data indirectly ("analyze the current diff"). The AI must then run a tool to fetch the data, wasting a round-trip.

**Solution**: **Preprocess the prompt** to inject live data *before* it reaches the AI.

### Syntax

Use backtick-wrapped commands with `!` prefix inside markdown templates:

```markdown
## Current Changes
!`git diff --stat`

## PR Description
!`gh pr view --json body -q .body`

Analyze these changes for issues.
```

**Execution**: A preprocessor script runs all `!`command`` blocks, replaces them with stdout, and sends the hydrated prompt to the AI.

---

## 2. Implementation

### 2.1 Preprocessor Script

Location: `.agent/scripts/jit_inject.py`

```python
#!/usr/bin/env python3
"""
jit_inject.py - Preprocess prompts with live shell data.

Usage:
    python3 jit_inject.py template.md > hydrated_prompt.md
    cat template.md | python3 jit_inject.py - > hydrated_prompt.md
"""

import re
import subprocess
import sys
from pathlib import Path

PATTERN = r'!\`([^`]+)\`'

def execute_command(cmd: str) -> str:
    """Run shell command, return stdout or error message."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip() if result.returncode == 0 else f"[ERROR: {result.stderr.strip()}]"
    except subprocess.TimeoutExpired:
        return "[ERROR: Command timed out]"
    except Exception as e:
        return f"[ERROR: {e}]"

def hydrate(template: str) -> str:
    """Replace all !`command` patterns with their output."""
    def replacer(match):
        cmd = match.group(1)
        return execute_command(cmd)
    return re.sub(PATTERN, replacer, template)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: jit_inject.py <template.md | ->", file=sys.stderr)
        sys.exit(1)
    
    source = sys.argv[1]
    if source == "-":
        template = sys.stdin.read()
    else:
        template = Path(source).read_text()
    
    print(hydrate(template))
```

### 2.2 Template Example

File: `.agent/skills/templates/pr_review.md`

```markdown
---
name: pr-review
description: Analyze a Pull Request
---

## PR Metadata
!`gh pr view --json title,author,createdAt -q '"\(.title) by \(.author.login) at \(.createdAt)"'`

## Changed Files
!`git diff --name-only HEAD~1`

## Diff Summary
!`git diff --stat HEAD~1`

## Full Diff
!`git diff HEAD~1 | head -500`

---

Analyze this PR for:
1. Code quality issues
2. Security vulnerabilities
3. Breaking changes
4. Missing tests
```

---

## 3. Integration Points

### 3.1 With Protocol 404 (Decoupled Fetch)

Protocol 404 separates Fetch from Reason. Protocol 405 **accelerates Fetch** by embedding it in the prompt itself.

| Phase | 404 (Manual) | 405 (Injected) |
|-------|--------------|----------------|
| Fetch | Run tool → Get output → Show to AI | Preprocessor runs → AI receives hydrated prompt |
| Reason | AI analyzes | AI analyzes |

**Result**: One fewer round-trip.

### 3.2 With Semantic Search

The injection syntax can call internal scripts:

```markdown
## Relevant Sessions
!`python3 .agent/scripts/smart_search.py "authentication" --limit 3 --format brief`
```

---

## 4. Security Considerations

> [!WARNING]
> This pattern executes arbitrary shell commands from markdown files.

**Guardrails**:

1. Only run `jit_inject.py` on **trusted templates** in `.agent/skills/templates/`.
2. Never run on user-provided content.
3. Timeout all commands (30s default).
4. Log all executed commands to `.athena/jit_audit.log`.

---

## 5. Use Cases

| Template | Injected Data |
|----------|---------------|
| `pr_review.md` | `git diff`, PR metadata |
| `debug_session.md` | Error logs, stack trace |
| `deploy_check.md` | `docker ps`, health endpoints |
| `cost_audit.md` | GCP billing API response |
| `codebase_overview.md` | `tree`, `wc -l`, `git log` |

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Protocol created. Stolen from Claude Code `!command` syntax. |

---

# protocol #prompting #dynamic #stolen #claude-code
