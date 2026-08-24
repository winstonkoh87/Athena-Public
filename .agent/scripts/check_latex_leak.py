#!/usr/bin/env python3
"""
check_latex_leak.py — Currency-safe detector for accidental LaTeX/KaTeX math rendering leaks.

Usage:
  python3 .agent/scripts/check_latex_leak.py --all
  python3 .agent/scripts/check_latex_leak.py <file_path>...
"""

import sys
import os
import re

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
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
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
    return sorted(list(set(files)))

def get_changed_files():
    """Get list of modified/staged/untracked markdown and text files from git."""
    import subprocess
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
    return sorted(list(changed))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 .agent/scripts/check_latex_leak.py [--all | --changed | <file_path>...]")
        sys.exit(1)
        
    if sys.argv[1] == "--all":
        target_files = get_include_files()
    elif sys.argv[1] == "--changed":
        target_files = get_changed_files()
        if not target_files:
            print("✅ Clean: No changed markdown/text files to scan.")
            sys.exit(0)
    else:
        target_files = sys.argv[1:]
        
    total_violations = 0
    for fpath in target_files:
        viols = scan_file(fpath)
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
