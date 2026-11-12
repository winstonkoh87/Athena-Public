#!/usr/bin/env python3
"""
Staleness Detector
==================
Scans session logs and memory bank files for references to other Athena files
(protocols, case studies, insights, etc.) and flags any where the referenced
file has been modified AFTER the reference was written.

Inspired by vexp's auto-stale detection for dependency graph observations.

Usage:
    python -m athena.auditors.audit_staleness
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

from athena.core.config import get_protocol_dirs, iter_protocol_files

# ── ANSI Colors ──
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ── Configuration ──
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SESSION_LOG_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
MEMORY_BANK_DIR = PROJECT_ROOT / ".context" / "memory_bank"

# Patterns that indicate a file reference in session logs / memory bank
FILE_REF_PATTERNS = [
    # CS-378-prompt-arbitrage.md style (case study references)
    re.compile(r"\b(CS-\d{3}[-\w]*\.md)\b"),
    # Protocol references like "Protocol 162" or "protocol-162"
    re.compile(r"[Pp]rotocol[\s-]+(\d{2,4})\b"),
    # Direct .md file references
    re.compile(r"\b([\w-]+\.md)\b"),
    # Skill references like skills/protocols/...
    re.compile(r"(skills/protocols/[\w/-]+\.md)"),
]

# Directories to search for referenced files
SEARCH_DIRS = [
    PROJECT_ROOT / ".context" / "memories" / "case_studies",
    PROJECT_ROOT / ".context" / "memories" / "insights",
    *get_protocol_dirs(PROJECT_ROOT),
    PROJECT_ROOT / ".context" / "memory_bank",
    PROJECT_ROOT / "docs",
]


def get_file_last_modified_git(filepath: Path) -> datetime | None:
    """Get the last modification date of a file from git log."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip()
            dt = datetime.fromisoformat(date_str)
            # Strip timezone info for comparison with naive session dates
            return dt.replace(tzinfo=None)
    except Exception:
        pass
    return None


def get_file_last_modified_fs(filepath: Path) -> datetime | None:
    """Fallback: get last modification date from filesystem."""
    try:
        return datetime.fromtimestamp(filepath.stat().st_mtime)
    except Exception:
        return None


def extract_session_date(filename: str) -> datetime | None:
    """Extract date from session log filename like 2026-02-22-session-03.md."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return None


def find_referenced_file(ref: str) -> Path | None:
    """Search for a referenced file across known directories."""
    direct_repo = PROJECT_ROOT / ref
    if direct_repo.is_file():
        return direct_repo

    search_dirs: list[Path] = []
    seen: set[Path] = set()
    for d in [*SEARCH_DIRS, *get_protocol_dirs(PROJECT_ROOT)]:
        if d.exists() and d not in seen:
            seen.add(d)
            search_dirs.append(d)

    ref_name = Path(ref).name
    for search_dir in search_dirs:
        candidate = search_dir / ref
        if candidate.is_file():
            return candidate
        for match in sorted(search_dir.rglob(ref_name)):
            if match.is_file():
                return match
    return None


def resolve_protocol_ref(protocol_num: str) -> Path | None:
    """Resolve a protocol number like '162', '530', or '409' to its file path."""
    raw = str(protocol_num).strip()
    if not raw:
        return None
    if raw.isdigit():
        normalized = raw.lstrip("0") or "0"
        pattern = re.compile(
            rf"^(?:[A-Za-z]+-(?:[A-Za-z]+-)?)?0*{re.escape(normalized)}(?=[-_.]|$)",
            re.IGNORECASE,
        )
    else:
        pattern = re.compile(
            rf"(?:^|[-_]){re.escape(raw)}(?=[-_.]|$)",
            re.IGNORECASE,
        )

    for match in iter_protocol_files(PROJECT_ROOT):
        if pattern.search(match.stem):
            return match
    return None


def scan_file_for_refs(filepath: Path) -> list[tuple[str, Path]]:
    """Extract file references from a markdown file."""
    refs: list[tuple[str, Path]] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return refs

    seen = set()
    for pattern in FILE_REF_PATTERNS:
        for match in pattern.finditer(content):
            ref = match.group(1) if match.lastindex else match.group(0)

            # Skip self-references and common false positives
            if ref == filepath.name:
                continue
            if ref in seen:
                continue
            if ref in ("README.md", "CHANGELOG.md", "LICENSE.md", "CONTRIBUTING.md"):
                continue

            seen.add(ref)

            # Try to resolve
            if ref.isdigit():
                resolved = resolve_protocol_ref(ref)
            else:
                resolved = find_referenced_file(ref)

            if resolved and resolved.exists():
                refs.append((ref, resolved))

    return refs


def audit_staleness():
    """Run the staleness audit across all session logs."""
    print(f"\n{BOLD}{CYAN}🔍 STALENESS DETECTOR{RESET}")
    print(f"{CYAN}{'━' * 70}{RESET}")
    print(
        f"{DIM}Scanning session logs for references to files that changed after the session...{RESET}\n"
    )

    if not SESSION_LOG_DIR.exists():
        print(f"{YELLOW}⚠️  No session logs found at {SESSION_LOG_DIR}{RESET}")
        return

    stale_refs = []
    total_refs_checked = 0

    # Scan session logs
    for log_file in sorted(SESSION_LOG_DIR.glob("*.md")):
        session_date = extract_session_date(log_file.name)
        if not session_date:
            continue

        refs = scan_file_for_refs(log_file)
        for ref_name, ref_path in refs:
            total_refs_checked += 1
            ref_modified = get_file_last_modified_git(
                ref_path
            ) or get_file_last_modified_fs(ref_path)

            if ref_modified and ref_modified > session_date:
                days_stale = (ref_modified - session_date).days
                stale_refs.append(
                    {
                        "session": log_file.name,
                        "session_date": session_date,
                        "reference": ref_name,
                        "ref_path": ref_path,
                        "ref_modified": ref_modified,
                        "days_stale": days_stale,
                    }
                )

    # Output results
    if stale_refs:
        # Sort by staleness (most stale first)
        stale_refs.sort(key=lambda x: x["days_stale"], reverse=True)

        print(
            f"{BOLD}{'Session':<35} {'Reference':<30} {'Days Stale':<12} {'Severity'}{RESET}"
        )
        print(f"{'─' * 90}")

        for ref in stale_refs:
            severity = (
                "🔴 HIGH"
                if ref["days_stale"] > 7
                else "🟡 MED"
                if ref["days_stale"] > 2
                else "🟢 LOW"
            )
            severity_color = (
                RED
                if ref["days_stale"] > 7
                else YELLOW
                if ref["days_stale"] > 2
                else GREEN
            )

            print(
                f"  {ref['session']:<33} "
                f"{ref['reference']:<28} "
                f"{ref['days_stale']:<10}d "
                f"{severity_color}{severity}{RESET}"
            )

        print(f"\n{'─' * 90}")
        print(f"{BOLD}📊 Summary:{RESET}")
        print(f"   References checked: {total_refs_checked}")
        print(f"   {RED}Stale references:    {len(stale_refs)}{RESET}")
        print(
            f"   {GREEN}Fresh references:    {total_refs_checked - len(stale_refs)}{RESET}"
        )
        print(
            f"\n{YELLOW}💡 Stale references may contain outdated information. Re-evaluate in your next session.{RESET}"
        )
    else:
        print(
            f"{GREEN}✅ All {total_refs_checked} references are fresh. No staleness detected.{RESET}"
        )


if __name__ == "__main__":
    audit_staleness()
