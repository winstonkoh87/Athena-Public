---
name: diagnostic-first-refactoring
description: Analyze codebase structure before making changes — the "Surgeon's Scan" pattern
who: Any AI coding agent
what: Read-only workspace scan before executing refactoring changes
when: Before any /refactor or structural code change
where: Target codebase or module
why: Prevents blind edits that break unknown dependencies
how: 1. Map file structure → 2. Identify dependencies → 3. Check test coverage → 4. Plan changes → 5. Execute with verification
---

# Diagnostic-First Refactoring (Surgeon's Scan)

> **Core Principle**: Understand before you cut.

## Protocol

1. **Scan**: Map the target module's file structure and dependencies
2. **Diagnose**: Identify coupling, dead code, and test coverage gaps
3. **Plan**: Design the refactoring sequence (dependency-safe order)
4. **Execute**: Apply changes with verification at each step
5. **Verify**: Run tests, check for regressions

## Anti-Patterns

- ❌ Editing files without reading them first
- ❌ Refactoring multiple modules simultaneously
- ❌ Skipping the dependency scan
- ❌ Not running tests after each change

## Related Protocols

- DIAG-001: Knowledge-Action Gap
- DIAG-002: Baseline Check
- DIAG-003: Frame Collision
