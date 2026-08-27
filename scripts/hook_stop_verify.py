#!/usr/bin/env python3
"""
hook_stop_verify.py — Output-Side Stop Hook Verifier
===================================================

Runs on agent turn completion (Stop event) before the user sees the output.
Enforces fast (<3s) deterministic gates on changed files:
  - Gate 1: LaTeX/KaTeX math delimiter leaks
  - Gate 2: API secrets/tokens in committed diffs
  - Gate 3: Python syntax validity on touched scripts

Contract:
  - If any gate fails: exits with {"decision": "block", "reason": "..."}
  - If all gates pass: exits with {"decision": "allow"}
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_changed_files() -> list[str]:
    changed = set()
    try:
        # Unstaged changes
        r1 = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if r1.returncode == 0:
            for line in r1.stdout.splitlines():
                if line.strip():
                    changed.add(line.strip())

        # Staged changes (git diff --cached)
        r_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if r_staged.returncode == 0:
            for line in r_staged.stdout.splitlines():
                if line.strip():
                    changed.add(line.strip())

        # Untracked files
        r2 = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if r2.returncode == 0:
            for line in r2.stdout.splitlines():
                if line.strip():
                    changed.add(line.strip())
    except Exception:
        pass
    return sorted(changed)


def check_latex_leaks(changed_files: list[str]) -> list[str]:
    md_files = [f for f in changed_files if f.endswith((".md", ".txt"))]
    if not md_files:
        return []

    script = REPO_ROOT / ".agent" / "scripts" / "check_latex_leak.py"
    if not script.exists():
        return []

    try:
        r = subprocess.run(
            [sys.executable, str(script)] + md_files,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if r.returncode != 0:
            return [line for line in r.stdout.splitlines() if line.strip()]
    except Exception as e:
        return [f"LaTeX check error: {e}"]
    return []


def check_secrets(changed_files: list[str]) -> list[str]:
    SECRET_PATTERNS = [
        (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API Key"),  # pds:allow
        (r"ghp_[a-zA-Z0-9]{20,}", "GitHub Personal Access Token"),  # pds:allow
        (r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}", "Supabase/JWT Secret Key"),  # pds:allow
        (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),  # pds:allow
    ]

    violations = []
    for rel_path in changed_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists() or full_path.is_dir():
            continue
        # Skip scanning gitignored / binary / test mock files
        if any(ign in rel_path for ign in [".git/", "tests/", "node_modules/", ".venv/"]):
            continue

        try:
            content = full_path.read_text(encoding="utf-8", errors="ignore")
            for pat, secret_type in SECRET_PATTERNS:
                if re.search(pat, content):
                    violations.append(f"Secret detected in {rel_path}: {secret_type}")
        except Exception:
            pass
    return violations


def check_python_syntax(changed_files: list[str]) -> list[str]:
    py_files = [f for f in changed_files if f.endswith(".py")]
    violations = []
    for rel_path in py_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            continue
        try:
            import py_compile
            py_compile.compile(str(full_path), doraise=True)
        except py_compile.PyCompileError as e:
            violations.append(f"Python syntax error in {rel_path}: {e}")
        except Exception:
            pass
    return violations


def main():
    start_time = time.time()
    changed_files = get_changed_files()

    if not changed_files:
        print(json.dumps({"decision": "allow", "latency_ms": round((time.time() - start_time) * 1000, 1)}))
        sys.exit(0)

    errors = []

    # 1. LaTeX leaks
    latex_errors = check_latex_leaks(changed_files)
    if latex_errors:
        errors.extend(latex_errors)

    # 2. Secrets check
    secret_errors = check_secrets(changed_files)
    if secret_errors:
        errors.extend(secret_errors)

    # 3. Python syntax
    py_errors = check_python_syntax(changed_files)
    if py_errors:
        errors.extend(py_errors)

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    if errors:
        reason = (
            "Output Verifier Blocked Completion:\n"
            + "\n".join(f"  - {err}" for err in errors[:10])
            + "\nPlease fix the above violations before completing the turn."
        )
        payload = {"decision": "block", "reason": reason, "latency_ms": elapsed_ms}
        print(json.dumps(payload, indent=2))
        # Claude Code hooks: exit 2 = blocking, exit 1 = non-blocking (ignored).
        # stderr is fed back to Claude as the error message on exit 2.
        print(reason, file=sys.stderr)
        sys.exit(2)
    else:
        payload = {"decision": "allow", "latency_ms": elapsed_ms}
        print(json.dumps(payload))
        sys.exit(0)


if __name__ == "__main__":
    main()
