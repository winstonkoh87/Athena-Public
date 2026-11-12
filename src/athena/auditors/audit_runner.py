#!/usr/bin/env python3
"""
Audit Runner v1.0
=================
Enforces the /audit workflow with hard guardrails.

Features:
- AUDIT_DEPTH tracking (max 2 recursive calls)
- No-Touch List enforcement
- Generates audit_score.json output
- Parses audit.md for current rules

Usage: python3 audit_runner.py [--session|--deep] [--dry-run]
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Setup Path to import athena
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.core.config import AGENT_DIR, CONTEXT_DIR, PROJECT_ROOT

# Configuration
STATE_FILE = CONTEXT_DIR / "metrics" / "audit_state.json"
SCORE_FILE = CONTEXT_DIR / "metrics" / "audit_score.json"
AUDIT_WORKFLOW = AGENT_DIR / "workflows" / "audit.md"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# No-Touch List (files that cannot be auto-modified)
NO_TOUCH_PATTERNS = [
    ".env*",
    "**/auth/**",
    "**/crypto/**",
    "**/migrations/**",
    "User_Profile.md",
    "Core_Identity.md",
    "*.key",
    "*.pem",
    "*.secret",
]

MAX_AUDIT_DEPTH = 2


def log(level: str, message: str):
    colors = {"INFO": GREEN, "WARN": YELLOW, "ERROR": RED, "HALT": RED, "OK": GREEN}
    color = colors.get(level, RESET)
    print(f"{color}[{level}]{RESET} {message}")


def matches_no_touch(filepath: str) -> bool:
    """Check if a file matches any No-Touch pattern."""
    from fnmatch import fnmatch

    for pattern in NO_TOUCH_PATTERNS:
        # Check basename match
        if fnmatch(os.path.basename(filepath), pattern):
            return True
        # Check full path match
        if fnmatch(filepath, pattern):
            return True
        # Check if pattern is in path
        if "**" in pattern:
            # Convert ** pattern to parts check
            clean_pattern = pattern.replace("**/", "")
            if clean_pattern in filepath:
                return True
    return False


def load_state() -> dict:
    """Load audit state from file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_depth": 0, "session_id": None, "last_run": None}


def save_state(state: dict):
    """Save audit state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def increment_depth() -> tuple[int, bool]:
    """Increment audit depth and return (new_depth, should_halt)."""
    state = load_state()

    # Check if this is a new session (more than 1 hour since last run)
    last_run = state.get("last_run")
    if last_run:
        try:
            last_time = datetime.fromisoformat(last_run)
            if (datetime.now() - last_time).total_seconds() > 3600:
                # New session, reset depth
                state["current_depth"] = 0
                state["session_id"] = str(uuid.uuid4())[:8]
        except Exception:
            pass

    state["current_depth"] = state.get("current_depth", 0) + 1
    state["last_run"] = datetime.now().isoformat()

    if not state.get("session_id"):
        state["session_id"] = str(uuid.uuid4())[:8]

    save_state(state)

    should_halt = state["current_depth"] > MAX_AUDIT_DEPTH
    return state["current_depth"], should_halt


def reset_depth():
    """Reset audit depth to 0."""
    state = load_state()
    state["current_depth"] = 0
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    log("INFO", "Audit depth reset to 0.")


def run_structure_check(files: list[Path]) -> list[dict]:
    """Check for structural issues (blob detection)."""
    issues = []

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            # Check for blobs (>300 words without headers)
            current_section_words = 0
            current_section_start = 0

            for i, line in enumerate(lines):
                if line.startswith("#"):
                    current_section_words = 0
                    current_section_start = i
                else:
                    current_section_words += len(line.split())

                if current_section_words > 300:
                    issues.append({
                        "type": "structure",
                        "severity": "warning",
                        "file": str(file_path),
                        "message": f"Section starting at line {current_section_start + 1} exceeds 300 words without header",
                    })
                    break

        except Exception as e:
            log("WARN", f"Could not read {file_path}: {e}")

    return issues


def run_broken_link_check(files: list[Path]) -> list[dict]:
    """Check for broken internal links."""
    issues = []
    link_pattern = re.compile(r'\[.*?\]\((?!http|mailto)(.*?)\)')

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            source_dir = file_path.parent

            for match in link_pattern.finditer(content):
                link = match.group(1).split('#')[0].strip()
                if not link:
                    continue

                # Normalize path
                if link.startswith("file://"):
                    from urllib.parse import unquote
                    link = unquote(link.replace("file://", ""))

                target = source_dir / link if not os.path.isabs(link) else Path(link)

                if not target.exists():
                    issues.append({
                        "type": "broken_link",
                        "severity": "error",
                        "file": str(file_path),
                        "message": f"Broken link: {link}",
                    })

        except Exception as e:
            log("WARN", f"Could not check links in {file_path}: {e}")

    return issues


def get_session_files() -> list[Path]:
    """Get files modified in this session (last hour)."""
    import subprocess

    try:
        # Get recently modified files from git
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line.endswith(".md"):
                full_path = PROJECT_ROOT / line
                if full_path.exists():
                    files.append(full_path)
        return files
    except Exception:
        # Fallback: get all recently modified .md files
        import time
        one_hour_ago = time.time() - 3600
        files = []
        for root, _, filenames in os.walk(PROJECT_ROOT / ".context"):
            for f in filenames:
                if f.endswith(".md"):
                    path = Path(root) / f
                    if path.stat().st_mtime > one_hour_ago:
                        files.append(path)
        return files


def get_deep_files() -> list[Path]:
    """Get all files for deep scan."""
    files = []
    scan_dirs = [
        PROJECT_ROOT / ".context",
        PROJECT_ROOT / ".agent",
        PROJECT_ROOT / ".framework",
    ]

    for scan_dir in scan_dirs:
        if scan_dir.exists():
            for f in scan_dir.rglob("*.md"):
                files.append(f)

    return files


def generate_audit_score(
    mode: str,
    depth: int,
    issues: list[dict],
    stop_reason: str = "all_clear"
) -> dict:
    """Generate the audit score JSON."""

    blockers = len([i for i in issues if i["severity"] == "blocker"])
    warnings = len([i for i in issues if i["severity"] == "warning"])
    errors = len([i for i in issues if i["severity"] == "error"])

    # Determine status
    if blockers > 0:
        status = "fail"
    elif errors > 5 or warnings > 10:
        status = "warn"
    else:
        status = "pass"

    # Determine confidence
    if mode == "deep":
        confidence = "high"
    elif len(issues) == 0:
        confidence = "medium"
    else:
        confidence = "low"

    score = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "depth": depth,
        "status": status,
        "confidence": confidence,
        "findings": {
            "blockers": blockers,
            "warnings": warnings,
            "errors": errors,
            "auto_fixed": 0,
            "user_required": blockers + errors
        },
        "stop_reason": stop_reason
    }

    return score


def save_audit_score(score: dict):
    """Save audit score to file."""
    SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCORE_FILE, "w") as f:
        json.dump(score, f, indent=2)
    log("INFO", f"Audit score saved to {SCORE_FILE}")


def main():
    print("=" * 70)
    print("  AUDIT RUNNER v1.0 (With Guardrails)  ")
    print("=" * 70)

    # Parse arguments
    mode = "session"
    dry_run = False

    for arg in sys.argv[1:]:
        if arg == "--deep":
            mode = "deep"
        elif arg == "--session":
            mode = "session"
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--reset":
            reset_depth()
            return

    # Check recursion depth
    depth, should_halt = increment_depth()
    log("INFO", f"Audit depth: {depth}/{MAX_AUDIT_DEPTH}")

    if should_halt:
        log("HALT", "Recursion limit reached (depth > 2). Manual review required.")
        score = generate_audit_score(mode, depth, [], "recursion_limit")
        save_audit_score(score)
        print(f"\n{RED}⛔ AUDIT HALTED: Depth {depth} exceeds max {MAX_AUDIT_DEPTH}{RESET}")
        print("Run with --reset to clear depth counter.")
        return

    # Get files to audit
    if mode == "session":
        files = get_session_files()
        log("INFO", f"Session mode: {len(files)} recently modified files")
    else:
        files = get_deep_files()
        log("INFO", f"Deep mode: {len(files)} total files")
        if len(files) > 100:
            log("WARN", f"Deep scan on {len(files)} files. This may take a while.")

    # Check No-Touch List
    no_touch_files = [f for f in files if matches_no_touch(str(f))]
    if no_touch_files:
        log("WARN", f"Skipping {len(no_touch_files)} No-Touch files:")
        for f in no_touch_files[:5]:
            print(f"  - {f.name}")
        if len(no_touch_files) > 5:
            print(f"  ... and {len(no_touch_files) - 5} more")

    files = [f for f in files if not matches_no_touch(str(f))]

    if not files:
        log("INFO", "No files to audit.")
        score = generate_audit_score(mode, depth, [], "all_clear")
        save_audit_score(score)
        return

    # Run checks
    issues = []

    print(f"\n{CYAN}--- STRUCTURE CHECK ---{RESET}")
    structure_issues = run_structure_check(files)
    issues.extend(structure_issues)
    if structure_issues:
        log("WARN", f"Found {len(structure_issues)} structural issues")
    else:
        log("OK", "No structural issues found")

    print(f"\n{CYAN}--- BROKEN LINK CHECK ---{RESET}")
    link_issues = run_broken_link_check(files)
    issues.extend(link_issues)
    if link_issues:
        log("ERROR", f"Found {len(link_issues)} broken links")
    else:
        log("OK", "All links valid")

    # Generate and save score
    score = generate_audit_score(mode, depth, issues)
    save_audit_score(score)

    # Summary
    print("\n" + "=" * 70)
    print(f"\n{GREEN}AUDIT SUMMARY:{RESET}")
    print(f"  Mode: {mode}")
    print(f"  Depth: {depth}/{MAX_AUDIT_DEPTH}")
    print(f"  Files scanned: {len(files)}")
    print(f"  Status: {score['status'].upper()}")
    print(f"  Confidence: {score['confidence']}")
    print(f"  Issues: {len(issues)} total")
    print(f"    - Blockers: {score['findings']['blockers']}")
    print(f"    - Warnings: {score['findings']['warnings']}")
    print(f"    - Errors: {score['findings']['errors']}")

    if dry_run:
        print(f"\n{YELLOW}DRY RUN: No changes made.{RESET}")

    print("=" * 70)

    # Exit code based on status
    if score["status"] == "fail":
        sys.exit(1)
    elif score["status"] == "warn":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
