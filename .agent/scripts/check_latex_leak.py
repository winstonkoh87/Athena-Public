#!/usr/bin/env python3
"""
check_latex_leak.py — Currency-safe detector for accidental LaTeX/KaTeX math rendering leaks.

Usage:
  python3 .agent/scripts/check_latex_leak.py --all
  python3 .agent/scripts/check_latex_leak.py --changed
  python3 .agent/scripts/check_latex_leak.py --diff-only [<file_path>...]
  python3 .agent/scripts/check_latex_leak.py <file_path>...
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# Always-flag patterns
EXPLICIT_LATEX_PATTERNS = [
    r"\\text\{",
    r"\\\(",
    r"\\\[",
    r"\$\$[^\$]+\$\$",
]

# Dollar pair extractor: match $...$ where inner does not contain newline or $
DOLLAR_PAIR_PATTERN = re.compile(r"\$([^\$\n]+)\$")

def remove_code_spans(text):
    """Strip fenced code blocks and inline code spans before scanning."""
    # Strip ```...``` fenced code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Strip `...` inline code spans
    text = re.sub(r"`[^`\n]+`", "", text)
    return text

def is_latex_leak(line):
    """Return True if line contains a KaTeX/LaTeX math leak."""
    line = remove_code_spans(line)

    # Check explicit LaTeX tags
    for pat in EXPLICIT_LATEX_PATTERNS:
        if re.search(pat, line):
            return True

    # Pre-strip numeric currency (e.g., $100, S$1,300, US$10K, $0.07, S$-557.53, -$500) and currency rates ($/hr) to prevent false pairing
    clean_line = re.sub(r"(?:[A-Za-z]{1,3}\$?|\$)?-?\$?[0-9]+[\d\.,]*(?:k|K|m|M)?", "", line)
    clean_line = re.sub(r"\$/(?:hr|h|day|month|year|lot|pip|MTok)\b", "", clean_line)

    # Check dollar pairs
    matches = DOLLAR_PAIR_PATTERN.findall(clean_line)
    for inner in matches:
        inner_trimmed = inner.strip()
        if not inner_trimmed:
            continue

        # Ignore ALL-CAPS shell identifiers (e.g. $HOME, $PATH)
        if re.match(r"^[A-Z0-9_]+$", inner_trimmed):
            continue

        # Flag if starts with \ or contains math operators / symbols \ ^ _ = ( )
        if inner_trimmed.startswith("\\") or any(char in inner_trimmed for char in r"\^_=()"):
            return True

    return False

def scan_file(file_path):
    if not os.path.exists(file_path):
        return []

    violations = []
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    in_fenced_block = False
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue

        if is_latex_leak(line):
            violations.append((idx, line.strip()))

    return violations


_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def get_git_added_line_numbers(
    file_path: str, repo_root: Path | None = None
) -> set[int] | None:
    """Return 1-based line numbers added/modified vs HEAD, or None to fall back to full scan."""
    target = Path(file_path)
    try:
        if repo_root is not None:
            root = Path(repo_root).resolve()
            resolved = target.resolve() if target.is_absolute() else (root / target).resolve()
        else:
            anchor = target.resolve()
            probe_dir = anchor if anchor.is_dir() else anchor.parent
            if not probe_dir.exists():
                probe_dir = Path.cwd()
            top = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(probe_dir),
                capture_output=True,
                text=True,
                timeout=3,
            )
            if top.returncode != 0 or not top.stdout.strip():
                return None
            root = Path(top.stdout.strip()).resolve()
            resolved = anchor

        if not resolved.exists() or resolved.is_dir():
            return set()

        try:
            rel_path = resolved.relative_to(root).as_posix()
        except ValueError:
            return None

        head_ok = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if head_ok.returncode != 0:
            return None

        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel_path],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if tracked.returncode != 0:
            return None

        diff = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "-U0", "HEAD", "--", rel_path],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if diff.returncode != 0:
            return None

        added: set[int] = set()
        cur_line = 0
        in_hunk = False
        for raw_line in diff.stdout.splitlines():
            m = _HUNK_HEADER_RE.match(raw_line)
            if m:
                cur_line = int(m.group(1))
                in_hunk = True
                continue
            if not in_hunk:
                continue
            if raw_line.startswith("+"):
                added.add(cur_line)
                cur_line += 1
            elif raw_line.startswith(" "):
                cur_line += 1
        return added
    except Exception:
        return None


def get_git_added_lines_batch(
    rel_paths: list[str], repo_root: Path | None = None
) -> dict[str, set[int]] | None:
    """Batch-fetch 1-based added/modified line numbers vs HEAD for tracked paths.

    Returns {rel_path: set_of_lines}, or None if git/HEAD is unavailable.
    """
    if not rel_paths:
        return {}
    root = (repo_root or Path.cwd()).resolve()
    try:
        head_ok = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if head_ok.returncode != 0:
            return None

        diff = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "-U0", "HEAD", "--", *rel_paths],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if diff.returncode != 0:
            return None

        added_map: dict[str, set[int]] = {p: set() for p in rel_paths}
        current_file: str | None = None
        cur_line = 0
        in_hunk = False
        for raw_line in diff.stdout.splitlines():
            if raw_line.startswith("diff --git "):
                in_hunk = False
                current_file = None
                continue
            if not in_hunk:
                if raw_line.startswith("+++ b/"):
                    current_file = raw_line[6:]
                elif raw_line == "+++ /dev/null":
                    current_file = None
                else:
                    m = _HUNK_HEADER_RE.match(raw_line)
                    if m:
                        cur_line = int(m.group(1))
                        in_hunk = True
                continue

            m = _HUNK_HEADER_RE.match(raw_line)
            if m:
                cur_line = int(m.group(1))
                continue
            if current_file is None:
                continue
            if raw_line.startswith("+"):
                added_map.setdefault(current_file, set()).add(cur_line)
                cur_line += 1
            elif raw_line.startswith(" "):
                cur_line += 1
        return added_map
    except Exception:
        return None


def scan_file_diff(
    file_path: str,
    repo_root: Path | None = None,
    added_lines: set[int] | None = None,
) -> list[tuple[int, str]]:
    """Scan only lines added vs HEAD for tracked files; full scan for untracked files."""
    if added_lines is None:
        added_lines = get_git_added_line_numbers(file_path, repo_root=repo_root)
    if added_lines is None:
        resolved = Path(file_path)
        if not resolved.is_absolute() and repo_root is not None:
            resolved = Path(repo_root) / resolved
        return scan_file(str(resolved))
    if not added_lines:
        return []

    target = Path(file_path)
    if not target.is_absolute() and repo_root is not None:
        target = Path(repo_root) / target
    if not target.exists():
        return []

    violations: list[tuple[int, str]] = []
    with open(target, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    in_fenced_block = False
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue

        if idx in added_lines and is_latex_leak(line):
            violations.append((idx, line.strip()))

    return violations


def get_include_files():
    files = []
    base_dirs = ["AGENTS.md", ".agent", ".framework", ".context"]

    exclude_markers = [
        ".context/memories/",
        "/archive/",
        "/.archive/",
        "/archive_skills/",
        "/node_modules/",
        "/.git/",
        "/.venv/",
    ]

    for item in base_dirs:
        if os.path.isfile(item):
            files.append(item)
        elif os.path.isdir(item):
            for root, _, filenames in os.walk(item):
                for fn in filenames:
                    if fn.endswith(".md"):
                        full_path = os.path.join(root, fn)
                        if not any(ex in full_path for ex in exclude_markers):
                            files.append(full_path)
    return sorted(set(files))


def get_changed_files():
    """Get list of modified/staged/untracked markdown and text files from git."""
    changed = set()
    exts = (".md", ".txt", ".json", ".yaml", ".yml")
    try:
        # Check unstaged modifications against HEAD
        r1 = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if r1.returncode == 0:
            for line in r1.stdout.splitlines():
                if line.strip().endswith(exts):
                    changed.add(line.strip())

        # Check staged files (git diff --cached)
        r_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5
        )
        if r_staged.returncode == 0:
            for line in r_staged.stdout.splitlines():
                if line.strip().endswith(exts):
                    changed.add(line.strip())

        # Check untracked files
        r2 = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=5
        )
        if r2.returncode == 0:
            for line in r2.stdout.splitlines():
                if line.strip().endswith(exts):
                    changed.add(line.strip())
    except Exception:
        pass
    return sorted(changed)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 .agent/scripts/check_latex_leak.py "
            "[--all | --changed | --diff-only [<file_path>...] | <file_path>...]"
        )
        sys.exit(1)

    diff_only = False
    if sys.argv[1] == "--all":
        target_files = get_include_files()
    elif sys.argv[1] == "--changed":
        target_files = get_changed_files()
        if not target_files:
            print("✅ Clean: No changed markdown/text files to scan.")
            sys.exit(0)
    elif sys.argv[1] == "--diff-only":
        diff_only = True
        target_files = sys.argv[2:] or get_changed_files()
        if not target_files:
            print("✅ Clean: No changed markdown/text files to scan.")
            sys.exit(0)
    else:
        target_files = sys.argv[1:]

    total_violations = 0
    for fpath in target_files:
        viols = scan_file_diff(fpath) if diff_only else scan_file(fpath)
        if viols:
            total_violations += len(viols)
            print(f"❌ {fpath}: {len(viols)} violation(s)")
            for line_num, content in viols[:10]:
                print(f"   Line {line_num}: {content}")

    if total_violations > 0:
        print(f"\nTotal violations found: {total_violations}")
        sys.exit(1)
    else:
        print("✅ Clean: Zero LaTeX leaks found across all scanned files.")
        sys.exit(0)


if __name__ == "__main__":
    main()
