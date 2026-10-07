#!/usr/bin/env python3
"""
verify_canon_citations.py — Canonical Citation Verifier
=======================================================

Scans markdown files for `§NNN` citations and verifies each one resolves
to an actual named entry in CANONICAL.md. § numbers represent line numbers,
which can shift on edits, making them fragile references.

Known limitation: Protocol files use §NNN to reference Law numbers (e.g.,
§0 = Law #0), not CANONICAL line numbers. Use --min-ref 50 to suppress
these false positives (CANONICAL table entries start around line 50+).

Usage:
    python3 .agent/scripts/verify_canon_citations.py --all
    python3 .agent/scripts/verify_canon_citations.py --all --min-ref 50
    python3 .agent/scripts/verify_canon_citations.py file1.md file2.md
    python3 .agent/scripts/verify_canon_citations.py --all --fix-suggestions
"""

import argparse
import re
import sys
from pathlib import Path


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for p in [current, current.parent, current.parent.parent]:
        if (p / ".context" / "CANONICAL.md").exists():
            return p
    return current.parent

PROJECT_ROOT = find_project_root()
CONTEXT_DIR = PROJECT_ROOT / ".context"
CANONICAL_FILE = CONTEXT_DIR / "CANONICAL.md"

def load_canonical_lines() -> list[str]:
    """Load CANONICAL.md lines, padding index 0 so indices match line numbers."""
    if not CANONICAL_FILE.exists():
        print(f"Error: {CANONICAL_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(CANONICAL_FILE, encoding="utf-8") as f:
        return [""] + f.read().splitlines()

def parse_canonical_entry(line: str) -> dict | None:
    """Parse a CANONICAL.md table row. Returns a dict if valid, else None."""
    line = line.strip()
    if not line.startswith("|"):
        return None
    # Skip separator lines
    if re.match(r"^\|\s*:?-+.*\|", line):
        return None

    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3:
        return None

    name = parts[1].replace("**", "").strip()
    if not name or name in ["Metric", "Framework", "Law", "Decision"]:
        return None

    # Try to extract session
    session = None
    session_match = re.search(r"\b(S\d+)\b", line)
    if session_match:
        session = session_match.group(1)
    else:
        # Look for Session \d+
        session_match = re.search(r"Session\s+(\d+)", line, re.IGNORECASE)
        if session_match:
            session = f"S{session_match.group(1)}"

    # Try to extract fingerprint
    fp = None
    fp_match = re.search(r"fp:\s*([a-f0-9]+)", line, re.IGNORECASE)
    if fp_match:
        fp = fp_match.group(1)

    return {
        "name": name,
        "session": session,
        "fp": fp
    }

STOPWORDS = frozenset([
    "the", "and", "for", "with", "from", "that", "this", "over", "into",
    "under", "about", "your", "have", "been", "were", "what", "when",
    "where", "which", "will", "would", "could", "should",
    "invariant", "invariants", "protocol", "protocols", "model", "models",
    "rule", "rules", "trap", "traps", "law", "laws", "doctrine", "system",
])


def extract_distinctive_words(text: str) -> set[str]:
    """Extract distinctive words (4+ letters, lowercase, excluding stoplist)."""
    words = re.findall(r"[a-z]{4,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def is_canonical_citation(line: str, match_start: int, match_end: int) -> bool:
    """Check if §NNN is a CANONICAL citation (in a CANONICAL link or within 80 chars)."""
    # 1. Check if §NNN is inside a markdown link [...](...)
    for link_match in re.finditer(r"\[([^\]]*)\]\(([^)]*)\)", line):
        l_start, l_end = link_match.span()
        if l_start <= match_start and match_end <= l_end:
            link_text = link_match.group(1) + " " + link_match.group(2)
            return "canonical" in link_text.lower()

    # 2. If not inside a markdown link, check proximity (within 80 chars)
    start_win = max(0, match_start - 80)
    end_win = min(len(line), match_end + 80)
    window = line[start_win:end_win]
    return "canonical" in window.lower()


def check_text_citations(
    text: str,
    canonical_lines: list[str] | None = None,
    filename: str = "<stdin>",
    min_ref: int = 0,
) -> list[dict]:
    """Inspect lines of text for CANONICAL citations and return findings."""
    if canonical_lines is None:
        canonical_lines = load_canonical_lines()
    max_line = len(canonical_lines) - 1
    citation_pattern = re.compile(r"§(\d+)")
    findings: list[dict] = []

    for i, line in enumerate(text.splitlines(), 1):
        for match in citation_pattern.finditer(line):
            cited_line_num = int(match.group(1))
            if cited_line_num < min_ref:
                continue

            if not is_canonical_citation(line, match.start(), match.end()):
                continue

            if 1 <= cited_line_num <= max_line:
                canon_line = canonical_lines[cited_line_num]
                entry = parse_canonical_entry(canon_line)

                if entry:
                    name = entry["name"]
                    session = entry["session"]
                    fp = entry["fp"]

                    title_words = extract_distinctive_words(name)
                    line_words = extract_distinctive_words(line)
                    shared_words = title_words & line_words

                    ref_parts = []
                    if session:
                        ref_parts.append(session)
                    if fp:
                        ref_parts.append(f"fp: {fp}")
                    ref_str = f" ({', '.join(ref_parts)})" if ref_parts else ""

                    if not shared_words:
                        # Check if the title matches an entry within a ±10 line shift window (line numbers drift on edits)
                        shifted_entry = None
                        start_win = max(1, cited_line_num - 10)
                        end_win = min(max_line, cited_line_num + 10)
                        for win_line_num in range(start_win, end_win + 1):
                            if win_line_num == cited_line_num:
                                continue
                            win_line = canonical_lines[win_line_num]
                            cand_entry = parse_canonical_entry(win_line)
                            if cand_entry:
                                cand_words = extract_distinctive_words(cand_entry["name"])
                                # Check cand_words and full raw title cell for formerly-named entries
                                raw_title = win_line.split("|")[1] if "|" in win_line else cand_entry["name"]
                                cand_full_words = extract_distinctive_words(raw_title)
                                if (cand_words | cand_full_words) & line_words:
                                    shifted_entry = (win_line_num, cand_entry)
                                    break
                        if shifted_entry:
                            win_line_num, cand_entry = shifted_entry
                            msg = f"{filename}:{i}  §{cited_line_num} → VALID (shifted to line {win_line_num}): '{cand_entry['name']}'"
                            findings.append({
                                "file": filename,
                                "line": i,
                                "cited_line": cited_line_num,
                                "status": "VALID",
                                "name": cand_entry["name"],
                                "session": cand_entry["session"],
                                "fp": cand_entry["fp"],
                                "message": msg,
                            })
                        else:
                            msg = f"{filename}:{i}  §{cited_line_num} → MISMATCH: line {cited_line_num} is '{name}'{ref_str}, citing line does not match title"
                            findings.append({
                                "file": filename,
                                "line": i,
                                "cited_line": cited_line_num,
                                "status": "MISMATCH",
                                "name": name,
                                "session": session,
                                "fp": fp,
                                "message": msg,
                            })
                    else:
                        msg = f"{filename}:{i}  §{cited_line_num} → VALID: '{name}'{ref_str}"
                        findings.append({
                            "file": filename,
                            "line": i,
                            "cited_line": cited_line_num,
                            "status": "VALID",
                            "name": name,
                            "session": session,
                            "fp": fp,
                            "message": msg,
                        })
                else:
                    msg = f"{filename}:{i}  §{cited_line_num} → INVALID: line {cited_line_num} does not contain a named entry in CANONICAL.md"
                    findings.append({
                        "file": filename,
                        "line": i,
                        "cited_line": cited_line_num,
                        "status": "INVALID",
                        "name": None,
                        "session": None,
                        "fp": None,
                        "message": msg,
                    })
            else:
                msg = f"{filename}:{i}  §{cited_line_num} → INVALID: line {cited_line_num} does not exist in CANONICAL.md"
                findings.append({
                    "file": filename,
                    "line": i,
                    "cited_line": cited_line_num,
                    "status": "INVALID",
                    "name": None,
                    "session": None,
                    "fp": None,
                    "message": msg,
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify §NNN citations in markdown files.")
    parser.add_argument("files", nargs="*", type=Path, help="Markdown files to scan")
    parser.add_argument("--all", action="store_true", help="Scan .context/ and .agent/ recursively for .md files")
    parser.add_argument("--fix-suggestions", action="store_true", help="Output recommended replacement text")
    parser.add_argument("--min-ref", type=int, default=0, help="Skip §NNN where NNN < this value (use 50 to suppress protocol Law # self-refs)")

    args = parser.parse_args()

    if not args.files and not args.all:
        parser.print_help()
        return 1

    files_to_scan = []
    if args.all:
        for d in [PROJECT_ROOT / ".context", PROJECT_ROOT / ".agent"]:
            if d.exists():
                files_to_scan.extend(d.rglob("*.md"))
    else:
        for f in args.files:
            f_path = Path(f)
            if f_path.is_file():
                files_to_scan.append(f_path)
            else:
                f_path = PROJECT_ROOT / f
                if f_path.is_file():
                    files_to_scan.append(f_path)
                else:
                    print(f"Warning: File {f} not found.", file=sys.stderr)

    # Remove duplicates
    files_to_scan = list({f.resolve() for f in files_to_scan})

    if not files_to_scan:
        print("No files to scan.", file=sys.stderr)
        return 0

    canonical_lines = load_canonical_lines()
    has_error = False

    for md_file in sorted(files_to_scan):
        try:
            with open(md_file, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)
            continue

        try:
            rel_path = md_file.relative_to(PROJECT_ROOT)
        except ValueError:
            rel_path = md_file

        findings = check_text_citations(content, canonical_lines, str(rel_path), args.min_ref)
        for finding in findings:
            print(finding["message"])
            if finding["status"] in ("INVALID", "MISMATCH"):
                has_error = True

            if args.fix_suggestions and finding["status"] == "VALID" and finding["name"]:
                name = finding["name"]
                session = finding["session"]
                fp = finding["fp"]
                sugg_ref_parts = []
                if session:
                    sugg_ref_parts.append(session)
                if fp:
                    sugg_ref_parts.append(f"fp: {fp[:8]}")
                sugg_ref_str = f" ({', '.join(sugg_ref_parts)})" if sugg_ref_parts else ""
                short_name = name.split("&")[0].strip() if "&" in name else name
                if len(short_name) > 30:
                    short_name = short_name[:27] + "..."
                print(f"  ⚠️  Fragile: §{finding['cited_line']} is a line number that shifts on edits. Recommend: '{short_name}{sugg_ref_str}'")

    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
