#!/usr/bin/env python3
"""
Passive Observation Generator
==============================
Auto-generates a summary of what changed during a session by diffing
git state between /start and /end.

At /start: orchestrator.py records git HEAD → .context/.session_start_ref
At /end:   this script diffs from that ref to current HEAD

Inspired by vexp's passive observation — watches what the agent does without
requiring the agent to self-report.

Usage:
    python -m athena.auditors.audit_observations
"""

import subprocess
from datetime import datetime
from pathlib import Path

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
START_REF_FILE = PROJECT_ROOT / ".context" / ".session_start_ref"

# File categories for auto-classification
CATEGORIES = {
    "protocols": [".agent/skills/protocols/", "examples/protocols/", ".framework/"],
    "workflows": [".agent/workflows/", "examples/workflows/"],
    "memory_bank": [".context/memory_bank/"],
    "session_logs": [".context/memories/session_logs/"],
    "insights": [".context/memories/insights/"],
    "case_studies": [".context/memories/case_studies/"],
    "source_code": ["src/athena/"],
    "docs": ["docs/", "wiki/"],
    "config": ["pyproject.toml", ".gitignore", "CONTRIBUTING.md"],
}


def record_start_ref():
    """Record the current git HEAD as the session start reference."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            ref = result.stdout.strip()
            START_REF_FILE.parent.mkdir(parents=True, exist_ok=True)
            START_REF_FILE.write_text(ref)
            return ref
    except Exception:
        pass
    return None


def get_start_ref() -> "str | None":
    """Read the session start reference."""
    if START_REF_FILE.exists():
        return START_REF_FILE.read_text().strip()
    return None


def get_changes_since(start_ref: str) -> dict:
    """Get all file changes between start_ref and current HEAD."""
    changes: dict[str, list[str]] = {"added": [], "modified": [], "deleted": [], "renamed": []}

    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", start_ref, "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            return changes

        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            status = parts[0]
            filepath = parts[1] if len(parts) > 1 else ""

            if status == "A":
                changes["added"].append(filepath)
            elif status == "M":
                changes["modified"].append(filepath)
            elif status == "D":
                changes["deleted"].append(filepath)
            elif status.startswith("R"):
                old_path = filepath
                new_path = parts[2] if len(parts) > 2 else ""
                changes["renamed"].append(f"{old_path} → {new_path}")

    except Exception:
        pass

    # Also get uncommitted changes
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("\t")
                status = parts[0]
                filepath = parts[1] if len(parts) > 1 else ""
                if filepath and filepath not in changes["modified"]:
                    changes["modified"].append(filepath)
    except Exception:
        pass

    return changes


def classify_changes(changes: dict) -> dict[str, list[str]]:
    """Classify changed files into categories."""
    classified: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    classified["other"] = []

    all_files = (
        [(f, "added") for f in changes["added"]]
        + [(f, "modified") for f in changes["modified"]]
        + [(f, "deleted") for f in changes["deleted"]]
        + [(f, "renamed") for f in changes["renamed"]]
    )

    for filepath, action in all_files:
        categorised = False
        for cat, prefixes in CATEGORIES.items():
            for prefix in prefixes:
                if filepath.startswith(prefix) or filepath == prefix:
                    classified[cat].append(f"{action}: {filepath}")
                    categorised = True
                    break
            if categorised:
                break
        if not categorised:
            classified["other"].append(f"{action}: {filepath}")

    # Remove empty categories
    return {k: v for k, v in classified.items() if v}


def get_commit_messages(start_ref: str) -> list[str]:
    """Get commit messages between start_ref and HEAD."""
    try:
        result = subprocess.run(
            ["git", "log", f"{start_ref}..HEAD", "--oneline", "--no-merges"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            return [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
    except Exception:
        pass
    return []


def find_current_session_log() -> "Path | None":
    """Find today's most recent session log."""
    if not SESSION_LOG_DIR.exists():
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    sessions = sorted(SESSION_LOG_DIR.glob(f"{today}-session-*.md"), reverse=True)
    return sessions[0] if sessions else None


def generate_observation_report(
    changes: dict, classified: dict, commits: list[str]
) -> str:
    """Generate a markdown report of session observations."""
    total = sum(len(v) for v in changes.values())
    lines = [
        "",
        "---",
        "",
        "## Auto-Observations",
        "",
        f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')} by `audit_observations`*",
        "",
        f"**{total} files changed** during this session:",
        "",
    ]

    # Commits
    if commits:
        lines.append("### Commits")
        lines.append("")
        for commit in commits:
            lines.append(f"- `{commit}`")
        lines.append("")

    # Classified changes
    category_labels = {
        "protocols": "📋 Protocols",
        "workflows": "⚙️ Workflows",
        "memory_bank": "🧠 Memory Bank",
        "session_logs": "📝 Session Logs",
        "insights": "💡 Insights",
        "case_studies": "📊 Case Studies",
        "source_code": "🐍 Source Code",
        "docs": "📚 Documentation",
        "config": "🔧 Configuration",
        "other": "📁 Other",
    }

    for cat, files in classified.items():
        label = category_labels.get(cat, cat)
        lines.append(f"### {label}")
        lines.append("")
        for f in files[:10]:
            lines.append(f"- {f}")
        if len(files) > 10:
            lines.append(f"- *...and {len(files) - 10} more*")
        lines.append("")

    return "\n".join(lines)


def audit_observations(append_to_log: bool = True):
    """Run the passive observation audit."""
    print(f"\n{BOLD}{CYAN}👁️ PASSIVE OBSERVATION REPORT{RESET}")
    print(f"{CYAN}{'━' * 70}{RESET}")

    start_ref = get_start_ref()
    if not start_ref:
        print(f"{YELLOW}⚠️  No session start reference found.{RESET}")
        print(f"{DIM}   Run /start to record the session starting point.{RESET}")
        print(f"{DIM}   The boot hook writes .context/.session_start_ref{RESET}")
        return

    print(f"{DIM}Session start ref: {start_ref[:8]}...{RESET}\n")

    # Get changes
    changes = get_changes_since(start_ref)
    total = sum(len(v) for v in changes.values())

    if total == 0:
        print(f"{GREEN}✅ No file changes detected since session start.{RESET}")
        return

    # Classify
    classified = classify_changes(changes)
    commits = get_commit_messages(start_ref)

    # Display summary
    print(f"{BOLD}📊 Session Activity:{RESET}")
    if changes["added"]:
        print(f"   {GREEN}+ {len(changes['added'])} files added{RESET}")
    if changes["modified"]:
        print(f"   {YELLOW}~ {len(changes['modified'])} files modified{RESET}")
    if changes["deleted"]:
        print(f"   {RED}- {len(changes['deleted'])} files deleted{RESET}")
    if changes["renamed"]:
        print(f"   {CYAN}→ {len(changes['renamed'])} files renamed{RESET}")
    print()

    if commits:
        print(f"{BOLD}📝 Commits ({len(commits)}):{RESET}")
        for commit in commits[:10]:
            print(f"   {commit}")
        if len(commits) > 10:
            print(f"   {DIM}...and {len(commits) - 10} more{RESET}")
        print()

    # Category breakdown
    print(f"{BOLD}📂 By Category:{RESET}")
    category_labels = {
        "protocols": "Protocols",
        "workflows": "Workflows",
        "memory_bank": "Memory Bank",
        "session_logs": "Session Logs",
        "insights": "Insights",
        "case_studies": "Case Studies",
        "source_code": "Source Code",
        "docs": "Documentation",
        "config": "Configuration",
        "other": "Other",
    }
    for cat, files in classified.items():
        label = category_labels.get(cat, cat)
        print(f"   {label}: {len(files)} changes")

    # Append to session log
    if append_to_log:
        session_log = find_current_session_log()
        if session_log:
            report = generate_observation_report(changes, classified, commits)
            with open(session_log, "a", encoding="utf-8") as f:
                f.write(report)
            print(
                f"\n{GREEN}✅ Auto-observations appended to {session_log.name}{RESET}"
            )
        else:
            print(
                f"\n{YELLOW}⚠️  No session log found for today. Report displayed above only.{RESET}"
            )

    # Cleanup start ref
    if START_REF_FILE.exists():
        START_REF_FILE.unlink()
        print(f"{DIM}   (Start ref cleaned up){RESET}")


if __name__ == "__main__":
    audit_observations()
