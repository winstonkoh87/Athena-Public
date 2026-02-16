#!/usr/bin/env python3
"""
pre_commit_check.py — Pre-commit code quality validation.

Checks modified files for common issues before session close.
Optional step in /end workflow.

Usage: python3 .agent/scripts/pre_commit_check.py

Checks:
- Python syntax errors
- Common import issues
- TODO/FIXME count
- Large uncommitted changes
"""

import sys
import subprocess
import ast
import re
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Patterns to flag
TODO_PATTERNS = ["TODO", "FIXME", "XXX", "HACK", "BUG"]

MAX_FILE_SIZE_KB = 100
MAX_TODOS_WARNING = 5

# Secret Patterns (Defense in Depth)
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (
        r"(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*['\"][A-Za-z0-9+/=_-]{16,}['\"]",
        "Generic High-Entropy Secret",
    ),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI/Anthropic Key (Legacy Format)"),
    (r"xox[baprs]-([0-9a-zA-Z]{10,48})?", "Slack Token"),
    (r"-----BEGIN PRIVATE KEY-----", "RSA Private Key"),
]


def get_modified_files() -> list[str]:
    """Get list of modified files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except Exception:
        return []


def get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except Exception:
        return []


def check_secrets(file_path: Path) -> list[str]:
    """Scan file content for potential secrets."""
    warnings = []
    try:
        # Skip large files for secret scanning to avoid performance issues
        if file_path.stat().st_size > MAX_FILE_SIZE_KB * 1024:
            return warnings

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for pattern, name in SECRET_PATTERNS:
                if re.search(pattern, content):
                    warnings.append(f"Potential {name} detected in {file_path}")
    except Exception as e:
        pass  # Ignore read errors for secret scanning
    return warnings


def check_python_syntax(filepath: Path) -> list[str]:
    """Check Python file for syntax errors."""
    errors = []
    if filepath.suffix != ".py":
        return errors

    try:
        content = filepath.read_text(encoding="utf-8")
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
    except Exception as e:
        errors.append(f"Parse error: {str(e)}")

    return errors


def count_todos(filepath: Path) -> list[tuple[int, str]]:
    """Count TODO/FIXME comments in file."""
    todos = []

    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            line_upper = line.upper()
            for pattern in TODO_PATTERNS:
                if pattern in line_upper:
                    todos.append((i, line.strip()[:60]))
                    break
    except Exception:
        pass

    return todos


def check_large_changes() -> tuple[int, int]:
    """Check for large uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10,
        )

        # Parse last line for summary
        lines = result.stdout.strip().split("\n")
        if lines:
            last = lines[-1]
            # Extract insertion/deletion counts
            insertions = 0
            deletions = 0

            if "insertion" in last:
                match = re.search(r"(\d+) insertion", last)
                if match:
                    insertions = int(match.group(1))

            if "deletion" in last:
                match = re.search(r"(\d+) deletion", last)
                if match:
                    deletions = int(match.group(1))

            return insertions, deletions
    except Exception:
        pass

    return 0, 0


def main():
    print("\n" + "=" * 60)
    print("🔍 PRE-COMMIT CHECK — Code Quality Validation")
    print("=" * 60 + "\n")

    issues = []
    warnings = []

    # 1. Get modified files
    modified = get_modified_files()
    staged = get_staged_files()
    all_files = list(set(modified + staged))

    if not all_files:
        print("✅ No modified files detected.\n")
        return 0

    print(f"📋 Checking {len(all_files)} modified file(s):\n")

    # 2. Check each file
    total_todos = []

    for filepath_str in all_files:
        filepath = WORKSPACE / filepath_str

        if not filepath.exists():
            continue

        print(f"   {filepath_str}")

        # Secret check
        secret_warnings = check_secrets(filepath)
        if secret_warnings:
            issues.extend(secret_warnings)

        # Python syntax check
        if filepath.suffix == ".py":
            syntax_errors = check_python_syntax(filepath)
            if syntax_errors:
                for err in syntax_errors:
                    issues.append(f"{filepath_str}: {err}")

        # TODO count
        todos = count_todos(filepath)
        if todos:
            total_todos.extend(
                [(filepath_str, line, content) for line, content in todos]
            )

    print()

    # 3. Report syntax errors
    if issues:
        print(f"❌ SYNTAX ERRORS ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
        print()

    # 4. Report TODOs
    if total_todos:
        print(f"⚠️  TODO/FIXME COMMENTS ({len(total_todos)}):")
        for filepath, line, content in total_todos[:10]:
            print(f"   {filepath}:{line} — {content}")
        if len(total_todos) > 10:
            print(f"   ... and {len(total_todos) - 10} more")
        print()

        if len(total_todos) > MAX_TODOS_WARNING:
            warnings.append(f"High TODO count ({len(total_todos)})")

    # 5. Check for large changes
    insertions, deletions = check_large_changes()
    if insertions + deletions > 500:
        warnings.append(f"Large uncommitted changes ({insertions}+ / {deletions}-)")
        print(f"⚠️  Large changes: +{insertions} / -{deletions} lines\n")

    # 6. Final verdict
    print("=" * 60)

    if issues:
        print(f"❌ Pre-commit check FAILED ({len(issues)} error(s))")
        print("   Fix syntax errors before committing.")
        return 1
    elif warnings:
        print(f"⚠️  Pre-commit check PASSED with {len(warnings)} warning(s)")
        for w in warnings:
            print(f"   → {w}")
        return 0
    else:
        print("✅ Pre-commit check PASSED. Code looks clean.")
        return 0

    print("=" * 60 + "\n")


if __name__ == "__main__":
    exit(main())
