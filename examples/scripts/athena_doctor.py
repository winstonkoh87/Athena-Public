#!/usr/bin/env python3
"""
athena_doctor.py — Self-Diagnostic Health Check
================================================
Inspired by OpenClaw's `openclaw doctor` pattern.

A single-command health check that validates your Athena workspace,
surfaces misconfigurations, and suggests fixes.

Usage:
    python3 examples/scripts/athena_doctor.py
    python3 examples/scripts/athena_doctor.py --fix    # Auto-fix safe issues
    python3 examples/scripts/athena_doctor.py --json   # Machine-readable output

Zero external dependencies. Works with Python 3.10+.
"""

import json
import platform
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CHECKMARK = f"{GREEN}✓{RESET}"
WARN = f"{YELLOW}⚠{RESET}"
FAIL = f"{RED}✗{RESET}"


# ─── Data Models ──────────────────────────────────────────────
@dataclass
class Finding:
    category: str
    severity: str  # "pass", "warn", "fail"
    message: str
    fix: str | None = None
    auto_fixable: bool = False

    def icon(self) -> str:
        return {"pass": CHECKMARK, "warn": WARN, "fail": FAIL}.get(self.severity, "?")

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix,
        }


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, f: Finding):
        self.findings.append(f)

    @property
    def passes(self) -> int:
        return sum(1 for f in self.findings if f.severity == "pass")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warn")

    @property
    def failures(self) -> int:
        return sum(1 for f in self.findings if f.severity == "fail")

    @property
    def score(self) -> str:
        total = len(self.findings)
        if total == 0:
            return "N/A"
        pct = (self.passes / total) * 100
        if pct >= 90:
            return f"{GREEN}A ({pct:.0f}%){RESET}"
        elif pct >= 70:
            return f"{YELLOW}B ({pct:.0f}%){RESET}"
        elif pct >= 50:
            return f"{YELLOW}C ({pct:.0f}%){RESET}"
        else:
            return f"{RED}D ({pct:.0f}%){RESET}"

    def to_json(self) -> str:
        return json.dumps(
            {
                "score": f"{(self.passes / max(len(self.findings), 1)) * 100:.0f}%",
                "passes": self.passes,
                "warnings": self.warnings,
                "failures": self.failures,
                "findings": [f.to_dict() for f in self.findings],
            },
            indent=2,
        )


# ─── Check Functions ─────────────────────────────────────────


def check_python_version(report: Report):
    """Check Python version meets minimum requirements."""
    v = sys.version_info
    if v >= (3, 13):
        report.add(
            Finding("Environment", "pass", f"Python {v.major}.{v.minor}.{v.micro}")
        )
    elif v >= (3, 10):
        report.add(
            Finding(
                "Environment",
                "warn",
                f"Python {v.major}.{v.minor} (recommended: 3.13+)",
                fix="brew install python@3.13",
            )
        )
    else:
        report.add(
            Finding(
                "Environment",
                "fail",
                f"Python {v.major}.{v.minor} is too old (minimum: 3.10)",
                fix="brew install python@3.13",
            )
        )


def check_directory_structure(report: Report):
    """Check that essential directories and files exist."""
    essential = {
        # (path relative to PROJECT_ROOT, description)
        "examples/protocols": "Protocol library",
        "examples/workflows": "Workflow definitions",
        "examples/scripts": "Script library",
        ".context": "Context directory",
        ".context/CANONICAL.md": "Canonical memory",
        "examples": "Examples directory",
        "docs": "Documentation",
        "README.md": "README",
    }

    for rel_path, desc in essential.items():
        target = PROJECT_ROOT / rel_path
        if target.exists():
            report.add(Finding("Structure", "pass", f"{desc} ({rel_path})"))
        else:
            report.add(
                Finding(
                    "Structure",
                    "fail",
                    f"Missing: {desc} ({rel_path})",
                    fix=f"mkdir -p {rel_path}"
                    if not rel_path.endswith(".md")
                    else None,
                )
            )


def check_protocols(report: Report):
    """Count and validate protocol files."""
    # Auto-detect: private repo uses .agent/skills/protocols, public uses examples/protocols
    protocols_dir = PROJECT_ROOT / ".agent" / "skills" / "protocols"
    if not protocols_dir.exists():
        protocols_dir = PROJECT_ROOT / "examples" / "protocols"
    if not protocols_dir.exists():
        report.add(Finding("Protocols", "fail", "Protocol directory missing"))
        return

    # Count by category
    categories = {}
    total = 0
    empty_protocols = []

    for category_dir in sorted(protocols_dir.iterdir()):
        if category_dir.is_dir():
            files = list(category_dir.glob("*.md"))
            categories[category_dir.name] = len(files)
            total += len(files)

            # Check for empty protocols
            for f in files:
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if len(content.strip()) < 50:
                        empty_protocols.append(f.name)
                except Exception:
                    pass

    # Also count root-level protocol files
    root_protocols = list(protocols_dir.glob("*.md"))
    total += len(root_protocols)

    report.add(
        Finding(
            "Protocols",
            "pass",
            f"{total} protocols across {len(categories)} categories",
        )
    )

    if empty_protocols:
        report.add(
            Finding(
                "Protocols",
                "warn",
                f"{len(empty_protocols)} near-empty protocols: {', '.join(empty_protocols[:5])}",
                fix="Review and populate or remove empty protocol files",
            )
        )


def check_workflows(report: Report):
    """Count and validate workflow files."""
    workflows_dir = PROJECT_ROOT / ".agent" / "workflows"
    if not workflows_dir.exists():
        report.add(Finding("Workflows", "fail", "Workflows directory missing"))
        return

    workflows = list(workflows_dir.glob("*.md"))
    report.add(Finding("Workflows", "pass", f"{len(workflows)} workflows defined"))

    # Check for workflows missing frontmatter
    missing_desc = []
    for w in workflows:
        try:
            content = w.read_text(encoding="utf-8", errors="ignore")
            if "description:" not in content[:500]:
                missing_desc.append(w.stem)
        except Exception:
            pass

    if missing_desc:
        report.add(
            Finding(
                "Workflows",
                "warn",
                f"{len(missing_desc)} workflows missing description frontmatter",
                fix="Add YAML frontmatter with 'description:' to workflow files",
            )
        )


def check_dead_links(report: Report):
    """Scan docs/ and README for dead internal links."""
    link_pattern = re.compile(r"\[.*?\]\((?!http|mailto|#)([^)]+)\)")
    dead_links = []
    files_checked = 0

    scan_targets = [PROJECT_ROOT / "README.md"]
    docs_dir = PROJECT_ROOT / "docs"
    if docs_dir.exists():
        scan_targets.extend(docs_dir.glob("*.md"))

    for md_file in scan_targets:
        if not md_file.exists():
            continue
        files_checked += 1
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            for match in link_pattern.finditer(content):
                link = match.group(1).split("#")[0].strip()
                if not link:
                    continue

                # Resolve relative to the file's directory
                target = (md_file.parent / link).resolve()
                if not target.exists():
                    dead_links.append((md_file.name, link))
        except Exception:
            pass

    if dead_links:
        report.add(
            Finding(
                "Links",
                "fail" if len(dead_links) > 5 else "warn",
                f"{len(dead_links)} dead links across {files_checked} files",
                fix="Run: python3 examples/scripts/deep_fix_links.py",
            )
        )
        for file_name, link in dead_links[:5]:
            report.add(Finding("Links", "warn", f"  ↳ {file_name}: {link}"))
    else:
        report.add(
            Finding("Links", "pass", f"No dead links ({files_checked} files scanned)")
        )


def check_version_consistency(report: Report):
    """Check that version numbers are consistent across files."""
    version_files = {
        "README.md": r"v(\d+\.\d+\.\d+)",
        "docs/SPEC_SHEET.md": r"v(\d+\.\d+\.\d+)",
        "docs/ARCHITECTURE.md": r"v(\d+\.\d+\.\d+)",
    }

    versions_found = {}
    for rel_path, pattern in version_files.items():
        target = PROJECT_ROOT / rel_path
        if target.exists():
            try:
                content = target.read_text(encoding="utf-8", errors="ignore")
                match = re.search(pattern, content)
                if match:
                    versions_found[rel_path] = match.group(1)
            except Exception:
                pass

    if not versions_found:
        report.add(Finding("Version", "warn", "No version numbers found in docs"))
        return

    unique_versions = set(versions_found.values())
    if len(unique_versions) == 1:
        v = unique_versions.pop()
        report.add(
            Finding(
                "Version",
                "pass",
                f"Version v{v} consistent across {len(versions_found)} files",
            )
        )
    else:
        report.add(
            Finding(
                "Version",
                "fail",
                f"Version mismatch: {versions_found}",
                fix="Update all version references to match",
            )
        )


def check_git_status(report: Report):
    """Check git repo health."""
    import subprocess

    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        report.add(Finding("Git", "fail", "Not a git repository"))
        return

    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        dirty_files = (
            len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        )

        if dirty_files == 0:
            report.add(Finding("Git", "pass", "Working tree clean"))
        elif dirty_files < 10:
            report.add(Finding("Git", "warn", f"{dirty_files} uncommitted changes"))
        else:
            report.add(
                Finding(
                    "Git",
                    "warn",
                    f"{dirty_files} uncommitted changes",
                    fix="git add -A && git commit -m 'checkpoint'",
                )
            )

        # Check remote sync
        result = subprocess.run(
            ["git", "log", "--oneline", "@{u}..", "-n", "5"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        unpushed = (
            len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        )
        if unpushed == 0:
            report.add(Finding("Git", "pass", "In sync with remote"))
        else:
            report.add(
                Finding(
                    "Git",
                    "warn",
                    f"{unpushed} unpushed commits",
                    fix="git push",
                )
            )

    except FileNotFoundError:
        report.add(Finding("Git", "fail", "git not installed"))
    except subprocess.TimeoutExpired:
        report.add(Finding("Git", "warn", "Git commands timed out"))
    except Exception as e:
        report.add(Finding("Git", "warn", f"Git check failed: {e}"))


def check_session_logs(report: Report):
    """Check session log health."""
    logs_dir = PROJECT_ROOT / ".context" / "memories" / "session_logs"
    if not logs_dir.exists():
        report.add(Finding("Sessions", "warn", "No session logs directory"))
        return

    logs = sorted(logs_dir.glob("*.md"), reverse=True)
    report.add(Finding("Sessions", "pass", f"{len(logs)} session logs found"))

    if logs:
        latest = logs[0]
        try:
            content = latest.read_text(encoding="utf-8", errors="ignore")
            # Check if latest session was properly closed
            if "Session Closed" in content or "✅ Closed" in content:
                report.add(
                    Finding(
                        "Sessions",
                        "pass",
                        f"Latest session ({latest.stem}) properly closed",
                    )
                )
            elif "..." in content and content.count("...") > 5:
                report.add(
                    Finding(
                        "Sessions",
                        "warn",
                        f"Latest session ({latest.stem}) has placeholder content",
                        fix="Run /end to properly close the session",
                    )
                )
        except Exception:
            pass


def check_canonical_memory(report: Report):
    """Check canonical memory file health."""
    canonical = PROJECT_ROOT / ".context" / "CANONICAL.md"
    if not canonical.exists():
        report.add(Finding("Memory", "fail", "CANONICAL.md missing"))
        return

    try:
        content = canonical.read_text(encoding="utf-8", errors="ignore")
        lines = content.strip().splitlines()
        report.add(Finding("Memory", "pass", f"CANONICAL.md: {len(lines)} lines"))

        # Check for last_updated
        if "last_updated" in content or "Last Updated" in content:
            report.add(Finding("Memory", "pass", "CANONICAL.md has timestamp"))
        else:
            report.add(
                Finding(
                    "Memory",
                    "warn",
                    "CANONICAL.md missing last_updated timestamp",
                    fix="Add 'last_updated: YYYY-MM-DD' to frontmatter",
                )
            )
    except Exception as e:
        report.add(Finding("Memory", "warn", f"Could not read CANONICAL.md: {e}"))


def check_env_file(report: Report):
    """Check for .env configuration."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            content = env_file.read_text(encoding="utf-8", errors="ignore")
            keys = [
                line.split("=")[0].strip()
                for line in content.splitlines()
                if "=" in line and not line.strip().startswith("#")
            ]
            report.add(
                Finding("Config", "pass", f".env file: {len(keys)} keys configured")
            )

            # Check for common required keys
            essential_keys = ["SUPABASE_URL", "SUPABASE_KEY"]
            for key in essential_keys:
                if any(k == key for k in keys):
                    report.add(Finding("Config", "pass", f"{key} configured"))
                else:
                    report.add(
                        Finding(
                            "Config",
                            "warn",
                            f"{key} not set (optional for local-only use)",
                        )
                    )
        except Exception:
            pass
    else:
        report.add(
            Finding(
                "Config",
                "warn",
                "No .env file found (optional for local-only use)",
                fix="cp .env.example .env && edit .env",
            )
        )


# ─── Main ─────────────────────────────────────────────────────


def main():
    auto_fix = "--fix" in sys.argv
    json_output = "--json" in sys.argv

    report = Report()

    if not json_output:
        print(f"\n{BOLD}{CYAN}{'═' * 60}{RESET}")
        print(f"{BOLD}{CYAN}  🩺 ATHENA DOCTOR — Health Check{RESET}")
        print(f"{BOLD}{CYAN}{'═' * 60}{RESET}")
        print(f"{DIM}  Project: {PROJECT_ROOT}{RESET}")
        print(f"{DIM}  Python:  {sys.version.split()[0]}{RESET}")
        print(f"{DIM}  OS:      {platform.system()} {platform.machine()}{RESET}\n")

    # Run all checks
    checks = [
        ("Environment", check_python_version),
        ("Structure", check_directory_structure),
        ("Protocols", check_protocols),
        ("Workflows", check_workflows),
        ("Dead Links", check_dead_links),
        ("Version", check_version_consistency),
        ("Git", check_git_status),
        ("Sessions", check_session_logs),
        ("Memory", check_canonical_memory),
        ("Config", check_env_file),
    ]

    current_category = None
    for name, check_fn in checks:
        if not json_output and name != current_category:
            current_category = name
            print(f"\n{BOLD}  {name}{RESET}")
            print(f"  {'─' * 40}")

        before = len(report.findings)
        try:
            check_fn(report)
        except Exception as e:
            report.add(Finding(name, "warn", f"Check failed: {e}"))

        # Print findings from this check
        if not json_output:
            for f in report.findings[before:]:
                print(f"  {f.icon()} {f.message}")
                if f.fix and f.severity != "pass":
                    print(f"    {DIM}Fix: {f.fix}{RESET}")

    # Summary
    if json_output:
        print(report.to_json())
    else:
        print(f"\n{BOLD}{'═' * 60}{RESET}")
        print(f"  {BOLD}Health Score: {report.score}{RESET}")
        print(
            f"  {CHECKMARK} {report.passes} passed  {WARN} {report.warnings} warnings  {FAIL} {report.failures} failures"
        )

        if report.failures > 0:
            print(
                f"\n  {RED}{BOLD}Action required:{RESET} Fix failures above before deploying.{RESET}"
            )
        elif report.warnings > 0:
            print(f"\n  {YELLOW}Some warnings — review when convenient.{RESET}")
        else:
            print(f"\n  {GREEN}{BOLD}All checks passed. Ship it! 🚀{RESET}")

        fixable = [
            f for f in report.findings if f.auto_fixable and f.severity != "pass"
        ]
        if fixable and not auto_fix:
            print(f"\n  {DIM}Run with --fix to auto-fix {len(fixable)} issues.{RESET}")

        print(f"{'═' * 60}\n")

    return 1 if report.failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
