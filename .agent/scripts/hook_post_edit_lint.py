#!/usr/bin/env python3
"""
hook_post_edit_lint.py — Single-File PostToolUse Edit/Write Linter
==================================================================

Non-blocking (always exit 0) PostToolUse hook for Claude Code Edit|Write.
Checks ONLY the single file touched by the tool call (no git status scan):
  1. Python syntax validity (`py_compile`)
  2. Diff-scoped LaTeX / KaTeX delimiter leaks on Markdown/text files
  3. Diff-scoped currency truncation check on Markdown files
  4. Restricted API token/secret patterns (via hook_stop_verify.check_restricted_signatures)

When violations exist, emits `hookSpecificOutput.additionalContext` so the agent
fixes the single hot file on the very next step instead of failing at Stop.
"""

from __future__ import annotations

import json
import os
import py_compile
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPTS_DIR / "lib"
REPO_ROOT = SCRIPTS_DIR.parent.parent
for _p in (SCRIPTS_DIR, LIB_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from hook_io import (  # noqa: E402
    extract_file_path,
    extract_tool_call,
    read_hook_stdin,
)

AUDIT_EXCLUSIONS = (
    "currency_corruption_report",
    "REDTEAM_REVIEW",
    "IMPLEMENTATION_PLAN",
)

_CURRENCY_LINE_RE = re.compile(r":L(\d+):")


def _resolve_root() -> Path:
    root_override = (
        os.environ.get("ATHENA_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or ""
    ).strip()
    return Path(root_override).resolve() if root_override else REPO_ROOT.resolve()


def lint_single_file(file_path: str, repo_root: Path | None = None) -> list[str]:
    """Run fast deterministic lint checks on a single edited file."""
    root = (repo_root or _resolve_root()).resolve()
    candidate = Path(file_path)
    full_path = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if not full_path.exists() or full_path.is_dir():
        return []

    try:
        rel_path = full_path.relative_to(root).as_posix()
    except ValueError:
        rel_path = str(full_path)

    issues: list[str] = []

    if full_path.suffix == ".py":
        try:
            py_compile.compile(str(full_path), doraise=True)
        except py_compile.PyCompileError as exc:
            issues.append(f"Python syntax error in {rel_path}: {exc}")
        except Exception:
            pass

    if full_path.suffix in (".md", ".txt"):
        added_lines: set[int] | None = None
        latex_script = REPO_ROOT / ".agent" / "scripts" / "check_latex_leak.py"
        if latex_script.exists():
            try:
                from check_latex_leak import get_git_added_line_numbers, scan_file_diff

                added_lines = get_git_added_line_numbers(str(full_path), repo_root=root)
                viols = scan_file_diff(
                    str(full_path), repo_root=root, added_lines=added_lines
                )
                for line_num, content in viols[:5]:
                    issues.append(f"LaTeX leak in {rel_path}:{line_num}: {content}")
            except Exception:
                pass

        if full_path.suffix == ".md" and not any(exc in rel_path for exc in AUDIT_EXCLUSIONS):
            curr_script = REPO_ROOT / ".agent" / "scripts" / "check_currency_integrity.py"
            if curr_script.exists():
                try:
                    from check_currency_integrity import check_content

                    content = full_path.read_text(encoding="utf-8", errors="replace")
                    file_errs = check_content(content, rel_path)
                    if file_errs:
                        if added_lines is not None:
                            filtered = []
                            for err in file_errs:
                                m = _CURRENCY_LINE_RE.search(err)
                                if m and int(m.group(1)) in added_lines:
                                    filtered.append(err)
                            file_errs = filtered
                        issues.extend(file_errs[:5])
                except Exception:
                    pass

    try:
        from hook_stop_verify import check_restricted_signatures

        issues.extend(check_restricted_signatures([rel_path], repo_root=root))
    except Exception:
        pass

    return issues


def main() -> None:
    data, err = read_hook_stdin(fail_closed_on_empty=False)
    if err is not None or data is None:
        sys.exit(0)

    try:
        _, tool_args = extract_tool_call(data)
    except Exception:
        sys.exit(0)

    file_path = extract_file_path(tool_args)
    if not file_path:
        sys.exit(0)

    issues = lint_single_file(file_path)
    if issues:
        msg = (
            f"Post-edit lint detected issues in {file_path} (fix on next step):\n"
            + "\n".join(f"  - {issue}" for issue in issues[:8])
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": msg,
                    }
                }
            )
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
