---
title: "Path-Specific Rules"
id: 407
type: architecture
author: [AUTHOR] (Stolen from Claude Code)
created: 2026-02-02
source: r/ClaudeAI - "7 Claude Code Power Tips Nobody's Talking About"
tags: [architecture, rules, context, modular, stolen]
---

# Protocol 407: Path-Specific Rules

> **Philosophy**: "Context is king. Load only what's relevant."

## 1. The Core Pattern

**Problem**: Monolithic instruction files (like a giant `CLAUDE.md` or `Core_Identity.md`) load everything into context, wasting tokens on irrelevant rules.

**Solution**: **Modular rule files** that only load when working on matching file paths.

---

## 2. Architecture

### 2.1 Rules Directory Structure

```
.agent/rules/
├── global.md          # Always loads (no paths: field)
├── api.md             # Only loads for src/api/**
├── frontend.md        # Only loads for src/components/**
├── athena-public.md   # Only loads for Athena-Public/**
├── security.md        # Always loads
└── client-work.md     # Only loads for Assignments/**
```

### 2.2 Rule File Format

Each rule file uses YAML frontmatter to specify paths:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.py"
priority: 10
---

# API Development Rules

1. All endpoints must validate input with Pydantic/Zod.
2. Use standard error format: `{"error": {"code": "...", "message": "..."}}`.
3. Log all requests with correlation IDs.
4. Never expose internal error details to clients.
```

### 2.3 Path Matching

| Pattern | Matches |
|---------|---------|
| `src/api/**` | All files under `src/api/` |
| `*.py` | All Python files in root |
| `**/*.test.ts` | All test files anywhere |
| `Athena-Public/**` | All files in public repo |

---

## 3. Implementation

### 3.1 Rule Loader Script

File: `.agent/scripts/load_rules.py`

```python
#!/usr/bin/env python3
"""
load_rules.py - Load path-specific rules for current context.

Usage:
    python3 load_rules.py src/api/routes.py
    # Returns: Contents of global.md + api.md + security.md
"""

import fnmatch
import sys
import yaml
from pathlib import Path

RULES_DIR = Path(__file__).parent.parent / "rules"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1])
                return meta or {}, parts[2].strip()
            except yaml.YAMLError:
                pass
    return {}, content


def matches_path(patterns: list[str], target_path: str) -> bool:
    """Check if target path matches any pattern."""
    for pattern in patterns:
        if fnmatch.fnmatch(target_path, pattern):
            return True
        # Also try relative matching
        if fnmatch.fnmatch(str(Path(target_path).name), pattern):
            return True
    return False


def load_rules_for_path(target_path: str) -> str:
    """Load all applicable rules for a given file path."""
    if not RULES_DIR.exists():
        return ""
    
    applicable_rules = []
    
    for rule_file in RULES_DIR.glob("*.md"):
        content = rule_file.read_text()
        meta, body = parse_frontmatter(content)
        
        paths = meta.get("paths", [])
        priority = meta.get("priority", 50)
        
        # Global rules (no paths specified) always load
        if not paths or matches_path(paths, target_path):
            applicable_rules.append({
                "name": rule_file.stem,
                "priority": priority,
                "content": body
            })
    
    # Sort by priority (lower = first)
    applicable_rules.sort(key=lambda r: r["priority"])
    
    # Combine rules
    output = []
    for rule in applicable_rules:
        output.append(f"## Rules: {rule['name']}\n\n{rule['content']}")
    
    return "\n\n---\n\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: load_rules.py <file_path>", file=sys.stderr)
        sys.exit(1)
    
    target = sys.argv[1]
    rules = load_rules_for_path(target)
    
    if rules:
        print(rules)
    else:
        print("# No applicable rules found")
```

### 3.2 Example Rule Files

**Global Rules** (`.agent/rules/global.md`):

```markdown
---
priority: 0
---

# Global Development Rules

1. Follow Law #1: No irreversible ruin.
2. Run semantic search before major decisions.
3. Quicksave after every substantive exchange.
4. Use atomic writes for all file operations.
```

**API Rules** (`.agent/rules/api.md`):

```markdown
---
paths:
  - "src/api/**"
  - "**/routes/**"
  - "**/endpoints/**"
priority: 20
---

# API Development Rules

1. Validate all inputs before processing.
2. Use consistent error response format.
3. Never expose stack traces to clients.
4. Rate limit all public endpoints.
```

**Client Work Rules** (`.agent/rules/client-work.md`):

```markdown
---
paths:
  - "Assignments/**"
  - "Quotations/**"
  - ".projects/client-*/**"
priority: 10
---

# Client Work Rules

1. Never commit client data to public repos.
2. Anonymize all examples in documentation.
3. Follow scope strictly - no over-delivery.
4. Save all communications in project folder.
```

---

## 4. Integration with Athena

### 4.1 With Protocol 405 (JIT Injection)

Combine with dynamic injection:

```markdown
## Applicable Rules
!`python3 .agent/scripts/load_rules.py "${CURRENT_FILE}"`

## Task
Refactor the authentication module.
```

### 4.2 With Boot Sequence

Add to `/start` workflow:

```bash
# Load rules for currently open files
for file in $(cat .athena/open_files.txt); do
    python3 .agent/scripts/load_rules.py "$file" >> context_rules.md
done
```

---

## 5. Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Protocol created. Stolen from Claude Code path-specific rules. |

---

# protocol #architecture #rules #context #stolen #claude-code
