#!/usr/bin/env python3
"""
Scan all non-archive .md files in the Athena repo and find broken file:/// links.

Usage examples:
    python3 .agent/scripts/link_integrity.py              # scan and report
    python3 .agent/scripts/link_integrity.py --summary    # compact output
    python3 .agent/scripts/link_integrity.py --fix        # auto-fix rewritable links
"""

import argparse
import json
import os
import re
import urllib.parse
from datetime import datetime, timezone

REPO_ROOT = os.environ.get("ATHENA_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
EXCLUDED_DIRS = {".git", ".claude", ".venv", "node_modules"}
REPORT_DIR = os.path.join(REPO_ROOT, ".context", "audit")
REPORT_PATH = os.path.join(REPORT_DIR, "link_report.json")

# Two patterns:
# 1. Markdown link syntax: ](file:///...) — space is allowed, terminated by )
# 2. Bare/other: file:/// not inside markdown link — stops at whitespace
MARKDOWN_LINK_PATTERN = re.compile(r'\]\((file:///[^)]+)\)')
BARE_LINK_PATTERN = re.compile(r'(?<!\])\(?(file:///[^\s\'">)\]]+)')

def extract_file_links(line):
    """Extract file:/// links from a line, handling unescaped spaces in markdown links."""
    links = []
    # First pass: markdown links (captures spaces)
    md_spans = set()
    for m in MARKDOWN_LINK_PATTERN.finditer(line):
        links.append(m.group(1))
        md_spans.add((m.start(), m.end()))
    # Second pass: bare links not already captured by markdown pattern
    for m in BARE_LINK_PATTERN.finditer(line):
        # Skip if this match overlaps with a markdown match
        overlap = False
        for ms, me in md_spans:
            if ms <= m.start() < me:
                overlap = True
                break
        if not overlap:
            links.append(m.group(1))
    return links

def main():
    parser = argparse.ArgumentParser(description="Check link integrity in markdown files.")
    parser.add_argument("--summary", action="store_true", help="Compact output (counts only)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix rewritable links")
    args = parser.parse_args()

    md_files = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        # Modify dirnames in-place to skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(os.path.join(dirpath, f))

    total_links = 0
    broken_links = 0
    rewritable_links = 0
    missing_links = 0
    details = []
    files_affected = set()

    for filepath in md_files:
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        lines = content.split('\n')
        new_lines = list(lines)
        file_changed = False

        for i, line in enumerate(lines):
            # Find all unique links to safely replace them one by one if fixing
            # If multiple identical links exist on a line, replacing them all at once is fine.
            matches = set(extract_file_links(line))

            replaced_line = line
            for url in matches:
                total_links += 1

                # Strip fragment for path checking
                url_parts = url.split('#', 1)
                url_no_frag = url_parts[0]
                fragment = '#' + url_parts[1] if len(url_parts) > 1 else ''

                if not url_no_frag.startswith("file://"):
                    continue

                path_part = url_no_frag[7:] # remove file://
                decoded_path = urllib.parse.unquote(path_part)

                # Skip false positives: template paths, regex fragments, example URLs
                if any(decoded_path.startswith(p) for p in [
                    "/absolute/", "/full/path/", "/...", "/`",
                    "/.../", "/path/to/", "/[",
                ]):
                    continue
                # Skip very short paths (regex artifacts like file:///`)
                if len(decoded_path) < 5:
                    continue
                # Skip paths from code examples/templates
                if "XX-name" in decoded_path or "[AUTHOR" in decoded_path:
                    continue

                exists = os.path.exists(decoded_path)
                is_broken = False
                category = None
                suggested_fix = None

                # Check if it points to within the repo
                if decoded_path.startswith(REPO_ROOT + "/") or decoded_path == REPO_ROOT:
                    # In-repo absolute link. Considered broken for portability.
                    is_broken = True
                    if exists:
                        category = "REWRITABLE"
                        rewritable_links += 1

                        # Calculate relative path
                        rel_path = os.path.relpath(decoded_path, os.path.dirname(filepath))
                        if not rel_path.startswith('.'):
                            rel_path = './' + rel_path

                        # Re-encode path components
                        # Split path to handle spaces safely without encoding slashes
                        safe_rel_path = urllib.parse.quote(rel_path, safe='./')
                        suggested_fix = safe_rel_path + fragment
                    else:
                        category = "MISSING"
                        missing_links += 1
                else:
                    # External absolute link
                    if not exists:
                        is_broken = True
                        category = "MISSING"
                        missing_links += 1

                if is_broken:
                    broken_links += 1
                    files_affected.add(filepath)
                    details.append({
                        "file": os.path.relpath(filepath, REPO_ROOT),
                        "line": i + 1,
                        "url": url,
                        "decoded_path": decoded_path,
                        "category": category,
                        "suggested_fix": suggested_fix
                    })

                    if args.fix and category == "REWRITABLE" and suggested_fix:
                        replaced_line = replaced_line.replace(url, suggested_fix)
                        file_changed = True

            new_lines[i] = replaced_line

        if file_changed and args.fix:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))

    # Ensure output directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)

    report = {
        "total_links": total_links,
        "broken_links": broken_links,
        "rewritable_links": rewritable_links,
        "missing_links": missing_links,
        "files_affected": len(files_affected),
        "scan_date": datetime.now(timezone.utc).isoformat()
    }

    if not args.summary:
        report["details"] = details

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Output to stdout
    if args.summary:
        print(json.dumps(report, indent=2))
    else:
        print(f"Scan complete. Found {total_links} file:/// links.")
        print(f"Broken links: {broken_links} ({rewritable_links} rewritable, {missing_links} missing)")
        print(f"Affected files: {len(files_affected)}")
        if args.fix:
            print(f"Fixed {rewritable_links} rewritable links.")
        print(f"Full report saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
