#!/usr/bin/env python3
"""
athena.cli.doctor — System Health Diagnostics
===============================================

Comprehensive health check inspired by OpenClaw's `doctor` command.
Runs 15 diagnostic checks across environment, workspace, memory,
git, daemon, and database layers.

Usage:
    athena doctor           # Full interactive diagnostics
    athena doctor --fix     # Auto-repair fixable issues
    athena doctor --json    # Machine-readable output
    athena doctor --quiet   # Summary only

Pattern credit: OpenClaw (openclaw/openclaw) doctor.md
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ─── ANSI Colors ─────────────────────────────────────────────
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ─── Check Result Types ─────────────────────────────────────
PASS = "pass"
WARN = "warn"
FAIL = "fail"
SKIP = "skip"


class CheckResult:
    """Result of a single diagnostic check."""

    def __init__(self, name: str, status: str, message: str, details: str = ""):
        self.name = name
        self.status = status
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        d = {"name": self.name, "status": self.status, "message": self.message}
        if self.details:
            d["details"] = self.details
        return d

    def __str__(self) -> str:
        icons = {
            PASS: f"{GREEN}✅",
            WARN: f"{YELLOW}⚠️ ",
            FAIL: f"{RED}❌",
            SKIP: f"{DIM}⏭️ ",
        }
        icon = icons.get(self.status, "  ")
        line = f"   {icon} {self.name}: {self.message}{RESET}"
        if self.details and self.status != PASS:
            line += f"\n      {DIM}{self.details}{RESET}"
        return line


# ─── Utility ─────────────────────────────────────────────────
def _find_project_root(start: Path | None = None) -> Path:
    """Walk up from start to find .athena_root or .agent/ marker."""
    current = start or Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".athena_root").exists() or (parent / ".agent").exists():
            return parent
    return current


def _run(cmd: list[str], cwd: str = None, timeout: int = 10) -> tuple[int, str]:
    """Run a command and return (returncode, combined output)."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout"
    except FileNotFoundError:
        return 127, "command not found"
    except Exception as e:
        return 1, str(e)


# ═══════════════════════════════════════════════════════════════
# DIAGNOSTIC CHECKS (0–14)
# ═══════════════════════════════════════════════════════════════


def check_00_environment(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check Python version and key dependencies."""
    results = []

    # Python version
    v = sys.version_info
    if v.major == 3 and v.minor >= 10:
        results.append(CheckResult("Python", PASS, f"{v.major}.{v.minor}.{v.micro}"))
    else:
        results.append(
            CheckResult("Python", WARN, f"{v.major}.{v.minor} (recommend 3.10+)")
        )

    # Virtual environment
    venv_path = root / ".venv"
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        results.append(CheckResult("Virtual Env", PASS, "Active"))
    elif venv_path.exists():
        results.append(
            CheckResult(
                "Virtual Env",
                WARN,
                "Found but not activated",
                f"Run: source {venv_path}/bin/activate",
            )
        )
    else:
        results.append(
            CheckResult("Virtual Env", WARN, "Not found (using global Python)")
        )

    # Key dependencies
    deps = {
        "dotenv": "from dotenv import load_dotenv",
        "supabase": "from supabase import create_client",
        "yaml": "import yaml",
    }
    for name, stmt in deps.items():
        code, _ = _run([sys.executable, "-c", stmt], timeout=5)
        if code == 0:
            results.append(CheckResult(f"Dep: {name}", PASS, "Installed"))
        else:
            results.append(
                CheckResult(
                    f"Dep: {name}", WARN, "Missing (optional)", f"pip install {name}"
                )
            )

    return results


def check_01_workspace_marker(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check for .athena_root marker file."""
    marker = root / ".athena_root"
    if marker.exists():
        return [CheckResult("Workspace Marker", PASS, ".athena_root found")]

    if fix:
        marker.touch()
        return [
            CheckResult("Workspace Marker", PASS, "Created .athena_root (auto-fix)")
        ]

    return [
        CheckResult(
            "Workspace Marker", WARN, "Missing .athena_root", "Run: athena doctor --fix"
        )
    ]


def check_02_directory_structure(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check required directory structure."""
    results = []
    required_dirs = {
        ".agent": "Agent scripts and workflows",
        ".agent/scripts": "Automation scripts",
        ".agent/workflows": "Workflow definitions",
        ".context": "Context and memory",
        ".context/memory_bank": "Memory bank (4 pillars)",
        ".context/memories/session_logs": "Session log archive",
    }

    for d, desc in required_dirs.items():
        path = root / d
        if path.exists():
            results.append(CheckResult(f"Dir: {d}", PASS, "Found"))
        elif fix:
            path.mkdir(parents=True, exist_ok=True)
            results.append(CheckResult("Dir: " + d, PASS, "Created (auto-fix)"))
        else:
            results.append(
                CheckResult(f"Dir: {d}", FAIL, f"Missing — {desc}", f"mkdir -p {d}")
            )

    return results


def check_03_config_integrity(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check .env file and config permissions."""
    results = []

    env_file = root / ".env"
    if env_file.exists():
        results.append(CheckResult("Config: .env", PASS, "Found"))

        # Permission check (should be 600 for security)
        try:
            mode = oct(env_file.stat().st_mode)[-3:]
            if mode in ("600", "400"):
                results.append(CheckResult("Config: .env perms", PASS, "Mode " + mode))
            else:
                if fix:
                    env_file.chmod(0o600)
                    results.append(
                        CheckResult("Config: .env perms", PASS, "Fixed to 600")
                    )
                else:
                    results.append(
                        CheckResult(
                            "Config: .env perms",
                            WARN,
                            f"Mode {mode} (should be 600)",
                            "chmod 600 .env",
                        )
                    )
        except Exception:
            pass

        # Check for key env vars
        try:
            content = env_file.read_text()
            for var in ["SUPABASE_URL", "SUPABASE_ANON_KEY"]:
                if var in content:
                    results.append(CheckResult(f"Env: {var}", PASS, "Set"))
                else:
                    results.append(
                        CheckResult(f"Env: {var}", WARN, "Not set (optional for cloud)")
                    )
        except Exception:
            pass
    else:
        results.append(
            CheckResult(
                "Config: .env", WARN, "Missing (optional)", "cp .env.example .env"
            )
        )

    return results


def check_04_memory_bank(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check Memory Bank 4 pillars."""
    results = []
    pillars = {
        "activeContext.md": "Current focus and session state",
        "userContext.md": "Core user profile",
        "productContext.md": "Product philosophy and goals",
        "systemPatterns.md": "Architecture patterns",
    }

    bank_dir = root / ".context" / "memory_bank"

    if not bank_dir.exists():
        if fix:
            bank_dir.mkdir(parents=True, exist_ok=True)
        return [CheckResult("Memory Bank", FAIL, "Directory missing", str(bank_dir))]

    for filename, desc in pillars.items():
        path = bank_dir / filename
        if path.exists():
            size = path.stat().st_size
            if size > 50:
                results.append(
                    CheckResult(f"Pillar: {filename}", PASS, f"{size:,} bytes")
                )
            else:
                results.append(
                    CheckResult(f"Pillar: {filename}", WARN, "Exists but nearly empty")
                )
        else:
            results.append(
                CheckResult(f"Pillar: {filename}", WARN, f"Missing — {desc}")
            )

    return results


def check_05_session_integrity(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check session log health."""
    results = []
    logs_dir = root / ".context" / "memories" / "session_logs"

    if not logs_dir.exists():
        return [CheckResult("Sessions", WARN, "No session_logs directory")]

    # Count session files
    session_files = sorted(logs_dir.glob("*.md"), reverse=True)

    results.append(CheckResult("Session Files", PASS, f"{len(session_files)} total"))

    # Check most recent session
    if session_files:
        latest = session_files[0]
        size = latest.stat().st_size
        if size < 100:
            results.append(
                CheckResult(
                    "Latest Session",
                    WARN,
                    f"{latest.name} is only {size} bytes (stub?)",
                )
            )
        else:
            results.append(
                CheckResult("Latest Session", PASS, f"{latest.name} ({size:,} bytes)")
            )

        # Check for 1-line stub (OpenClaw pattern)
        try:
            lines = latest.read_text().strip().split("\n")
            if len(lines) <= 1:
                results.append(
                    CheckResult(
                        "Session Content",
                        WARN,
                        "Latest session has only 1 line (not accumulating)",
                    )
                )
        except Exception:
            pass

    return results


def check_06_orphan_detection(root: Path, fix: bool = False) -> list[CheckResult]:
    """Quick orphan scan using existing orphan_detector.py."""
    detector = root / ".agent" / "scripts" / "orphan_detector.py"
    if not detector.exists():
        return [CheckResult("Orphan Scan", SKIP, "orphan_detector.py not found")]

    code, output = _run([sys.executable, str(detector)], cwd=str(root), timeout=30)

    if code == 0:
        # Parse orphan count from output
        orphan_count = output.lower().count("orphan")
        if orphan_count == 0 or "0 orphans" in output.lower():
            return [CheckResult("Orphan Scan", PASS, "No orphans detected")]
        else:
            return [CheckResult("Orphan Scan", WARN, "Orphans detected", output[:200])]
    else:
        return [
            CheckResult("Orphan Scan", WARN, "Scan failed (non-critical)", output[:100])
        ]


def check_07_dead_links(root: Path, fix: bool = False) -> list[CheckResult]:
    """Scan activeContext.md for broken file:// links."""
    ctx = root / ".context" / "memory_bank" / "activeContext.md"
    if not ctx.exists():
        return [CheckResult("Dead Links", SKIP, "No activeContext.md")]

    try:
        content = ctx.read_text()
        # Regex handles spaces by capturing until ')' or end of line
        links = re.findall(r"file://([^\)\n]+)", content)
        broken = []
        for link in links:
            path = Path("/" + link.replace("%20", " "))
            if not path.exists():
                broken.append(str(path))

        if broken:
            detail = "\n".join(f"  → {b}" for b in broken[:5])
            if len(broken) > 5:
                detail += f"\n  ... and {len(broken) - 5} more"
            return [
                CheckResult(
                    "Dead Links", WARN, f"{len(broken)} broken file:// links", detail
                )
            ]
        else:
            return [
                CheckResult(
                    "Dead Links", PASS, f"{len(links)} links checked, all valid"
                )
            ]
    except Exception as e:
        return [CheckResult("Dead Links", WARN, f"Scan error: {e}")]


def check_08_secret_scan(root: Path, fix: bool = False) -> list[CheckResult]:
    """Scan staged files for potential secrets."""
    secret_patterns = [
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub PAT"),
        (r"sk-[a-zA-Z0-9]{48}", "OpenAI/Anthropic Key"),
        (r"eyJ[a-zA-Z0-9_-]{20,}\.eyJ[a-zA-Z0-9_-]{20,}", "JWT/Supabase Key"),
        (r"AIza[a-zA-Z0-9_-]{35}", "Gemini/Google API Key"),
        (r"-----BEGIN PRIVATE KEY-----", "Private Key"),  # pds:allow — scanner pattern definition
    ]

    # Check staged files
    code, output = _run(["git", "diff", "--cached", "--name-only"], cwd=str(root))
    if code != 0 or not output.strip():
        return [CheckResult("Secret Scan", PASS, "No staged files to scan")]

    staged = [f.strip() for f in output.split("\n") if f.strip()]
    findings = []

    for filepath in staged:
        full = root / filepath
        if not full.exists() or full.stat().st_size > 100_000:
            continue
        try:
            content = full.read_text(errors="ignore")
            for pattern, name in secret_patterns:
                if re.search(pattern, content):
                    findings.append(f"{filepath}: {name}")
        except Exception:
            pass

    if findings:
        detail = "\n".join(f"  🔴 {f}" for f in findings[:5])
        return [
            CheckResult(
                "Secret Scan",
                FAIL,
                f"{len(findings)} potential secret(s) staged!",
                detail,
            )
        ]
    else:
        return [CheckResult("Secret Scan", PASS, f"{len(staged)} staged files clean")]


def check_09_git_health(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check git repository health."""
    results = []

    # Is git repo?
    code, _ = _run(["git", "rev-parse", "--git-dir"], cwd=str(root))
    if code != 0:
        return [CheckResult("Git", FAIL, "Not a git repository")]

    results.append(CheckResult("Git Repo", PASS, "Initialized"))

    # Stale lock file
    lock = root / ".git" / "index.lock"
    if lock.exists():
        if fix:
            lock.unlink()
            results.append(
                CheckResult("Git Lock", PASS, "Removed stale index.lock (auto-fix)")
            )
        else:
            results.append(
                CheckResult(
                    "Git Lock",
                    WARN,
                    "Stale .git/index.lock found",
                    "rm .git/index.lock",
                )
            )
    else:
        results.append(CheckResult("Git Lock", PASS, "No stale locks"))

    # Remote configured?
    code, output = _run(["git", "remote", "-v"], cwd=str(root))
    if "origin" in output:
        results.append(CheckResult("Git Remote", PASS, "origin configured"))
    else:
        results.append(CheckResult("Git Remote", WARN, "No remote 'origin' configured"))

    # Dirty working tree
    code, output = _run(["git", "status", "--porcelain"], cwd=str(root))
    if output.strip():
        lines = output.strip().split("\n")
        results.append(
            CheckResult("Git Status", WARN, f"{len(lines)} uncommitted file(s)")
        )
    else:
        results.append(CheckResult("Git Status", PASS, "Clean working tree"))

    return results


def check_10_daemon_status(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check if athenad.py process is running."""
    code, output = _run(["pgrep", "-f", "athenad.py"])
    if code == 0 and output.strip():
        pids = output.strip().split("\n")
        return [CheckResult("Daemon", PASS, f"athenad running (PID: {pids[0]})")]
    else:
        return [
            CheckResult(
                "Daemon",
                WARN,
                "athenad not running",
                "python3 -m athena.core.athenad &",
            )
        ]


def check_11_database(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check Supabase connectivity (if configured)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        return [CheckResult("Database", SKIP, "Supabase not configured (optional)")]

    try:
        code, output = _run(
            [
                sys.executable,
                "-c",
                f"from supabase import create_client; c = create_client('{url}', '{key}'); print('ok')",
            ],
            timeout=10,
        )
        if code == 0 and "ok" in output:
            return [CheckResult("Database", PASS, "Supabase connected")]
        else:
            return [
                CheckResult(
                    "Database", WARN, "Supabase connection failed", output[:100]
                )
            ]
    except Exception as e:
        return [CheckResult("Database", WARN, f"Connection error: {e}")]


def check_12_echo_chamber(root: Path, fix: bool = False) -> list[CheckResult]:
    """Check disagreement signals in recent sessions."""
    logs_dir = root / ".context" / "memories" / "session_logs"
    if not logs_dir.exists():
        return [CheckResult("Echo Chamber", SKIP, "No session logs")]

    patterns = [
        r"actually",
        r"incorrect",
        r"disagree",
        r"not quite",
        r"push back",
        r"not accurate",
    ]
    pattern = re.compile("|".join(patterns), re.IGNORECASE)

    count = 0
    checked = 0
    for log_file in sorted(logs_dir.glob("*.md"), reverse=True)[:10]:
        try:
            content = log_file.read_text(encoding="utf-8")
            count += len(pattern.findall(content))
            checked += 1
        except Exception:
            pass

    if count < 3:
        return [
            CheckResult(
                "Echo Chamber",
                WARN,
                f"{count} disagreements in {checked} sessions (low!)",
                "Challenge more premises per session",
            )
        ]
    else:
        return [
            CheckResult(
                "Echo Chamber",
                PASS,
                f"{count} disagreements in {checked} sessions — healthy",
            )
        ]


def check_13_stale_context(root: Path, fix: bool = False) -> list[CheckResult]:
    """Warn if activeContext.md is stale (>7 days since modification)."""
    ctx = root / ".context" / "memory_bank" / "activeContext.md"
    if not ctx.exists():
        return [CheckResult("Context Freshness", WARN, "activeContext.md missing")]

    mtime = datetime.fromtimestamp(ctx.stat().st_mtime)
    age = datetime.now() - mtime
    if age > timedelta(days=7):
        return [
            CheckResult(
                "Context Freshness",
                WARN,
                f"activeContext.md is {age.days} days old",
                "Update at next /start to capture current focus",
            )
        ]
    else:
        return [
            CheckResult(
                "Context Freshness",
                PASS,
                f"Updated {age.days}d {age.seconds // 3600}h ago",
            )
        ]


def check_14_workspace_tips(root: Path, fix: bool = False) -> list[CheckResult]:
    """Suggest git backup and memory system if missing."""
    results = []

    # Git backup suggestion
    code, _ = _run(["git", "rev-parse", "--git-dir"], cwd=str(root))
    if code != 0:
        results.append(
            CheckResult(
                "Backup",
                WARN,
                "Workspace is not under git",
                "git init && git remote add origin <your-repo> (recommended private GitHub/GitLab)",
            )
        )
    else:
        results.append(CheckResult("Backup", PASS, "Workspace under git"))

    # Memory system check
    bank = root / ".context" / "memory_bank"
    if not bank.exists():
        results.append(
            CheckResult(
                "Memory System",
                WARN,
                "No memory bank found",
                "See docs: Athena-Public/docs/YOUR_FIRST_AGENT.md",
            )
        )
    else:
        results.append(CheckResult("Memory System", PASS, "Memory bank configured"))

    return results


# ═══════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

ALL_CHECKS = [
    ("Environment", check_00_environment),
    ("Workspace Marker", check_01_workspace_marker),
    ("Directory Structure", check_02_directory_structure),
    ("Config Integrity", check_03_config_integrity),
    ("Memory Bank", check_04_memory_bank),
    ("Session Integrity", check_05_session_integrity),
    ("Orphan Detection", check_06_orphan_detection),
    ("Dead Links", check_07_dead_links),
    ("Secret Scan", check_08_secret_scan),
    ("Git Health", check_09_git_health),
    ("Daemon Status", check_10_daemon_status),
    ("Database", check_11_database),
    ("Echo Chamber", check_12_echo_chamber),
    ("Context Freshness", check_13_stale_context),
    ("Workspace Tips", check_14_workspace_tips),
]


def run_doctor(
    root: Path | None = None,
    fix: bool = False,
    output_json: bool = False,
    quiet: bool = False,
) -> int:
    """Run all diagnostic checks and return exit code (0=healthy, 1=issues)."""
    root = root or _find_project_root()
    start = time.time()

    all_results: list[CheckResult] = []
    json_output: list[dict] = []

    if not quiet and not output_json:
        print(f"\n{BOLD}{CYAN}{'═' * 60}{RESET}")
        print(f"{BOLD}{CYAN}  🩺 ATHENA DOCTOR — System Diagnostics{RESET}")
        print(f"{BOLD}{CYAN}{'═' * 60}{RESET}")
        print(f"   {DIM}Root: {root}{RESET}")
        if fix:
            print(f"   {GREEN}🔧 Auto-fix mode enabled{RESET}")
        print()

    for section_name, check_fn in ALL_CHECKS:
        if not quiet and not output_json:
            print(f"{BOLD}   ┌─ {section_name}{RESET}")

        try:
            results = check_fn(root, fix=fix)
        except Exception as e:
            results = [CheckResult(section_name, FAIL, f"Check crashed: {e}")]

        all_results.extend(results)

        if output_json:
            for r in results:
                json_output.append(r.to_dict())
        elif not quiet:
            for r in results:
                print(str(r))
            print()

    # Summary
    elapsed = time.time() - start
    passes = sum(1 for r in all_results if r.status == PASS)
    warns = sum(1 for r in all_results if r.status == WARN)
    fails = sum(1 for r in all_results if r.status == FAIL)
    skips = sum(1 for r in all_results if r.status == SKIP)

    if output_json:
        summary = {
            "root": str(root),
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "summary": {"pass": passes, "warn": warns, "fail": fails, "skip": skips},
            "checks": json_output,
        }
        print(json.dumps(summary, indent=2))
    else:
        print(f"{BOLD}{'─' * 60}{RESET}")
        parts = [f"{GREEN}✅ {passes} passed{RESET}"]
        if warns:
            parts.append(f"{YELLOW}⚠️  {warns} warnings{RESET}")
        if fails:
            parts.append(f"{RED}❌ {fails} failed{RESET}")
        if skips:
            parts.append(f"{DIM}⏭️  {skips} skipped{RESET}")

        print(f"   {' │ '.join(parts)}")
        print(f"   {DIM}Completed in {elapsed:.1f}s{RESET}")

        if fails > 0:
            print(
                f"\n   {RED}Run {BOLD}athena doctor --fix{RESET}{RED} to auto-repair fixable issues.{RESET}"
            )
        elif warns > 3:
            print(
                f"\n   {YELLOW}Some warnings found. Run {BOLD}athena doctor --fix{RESET}{YELLOW} to address.{RESET}"
            )
        else:
            print(f"\n   {GREEN}System healthy. 🟢{RESET}")

        print(f"{BOLD}{'─' * 60}{RESET}\n")

    return 1 if fails > 0 else 0


# Allow direct execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Athena System Diagnostics")
    parser.add_argument("--fix", action="store_true", help="Auto-repair fixable issues")
    parser.add_argument(
        "--json", dest="output_json", action="store_true", help="JSON output"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Summary only")
    parser.add_argument("--root", type=Path, default=None, help="Project root")

    args = parser.parse_args()
    sys.exit(
        run_doctor(
            root=args.root, fix=args.fix, output_json=args.output_json, quiet=args.quiet
        )
    )
