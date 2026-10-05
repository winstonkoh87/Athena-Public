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
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from athena.core.lambda_scorer import detect_crisis_signal
except ImportError:
    def detect_crisis_signal(text: str) -> bool:
        return False


def check_crisis_referral(payload: dict | None) -> list[str]:
    """Check that if user prompt triggered crisis signal, assistant response contains 1-767."""
    if not payload or not isinstance(payload, dict):
        return []

    # Honour stop_hook_active to avoid loop
    if payload.get("stop_hook_active"):
        return []

    user_prompt = ""
    assistant_reply = ""

    transcript_path = payload.get("transcript_path")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, encoding="utf-8") as tf:
                lines = tf.readlines()[-30:]
                for line in reversed(lines):
                    try:
                        rec = json.loads(line)
                        msg = rec.get("message", {})
                        role = msg.get("role")
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                        if role == "assistant" and not assistant_reply:
                            assistant_reply = content
                        elif role == "user" and not user_prompt:
                            user_prompt = content
                        if user_prompt and assistant_reply:
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    if not user_prompt:
        user_prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not assistant_reply:
        assistant_reply = payload.get("text") or payload.get("reply") or ""

    if user_prompt and detect_crisis_signal(user_prompt) and "1-767" not in assistant_reply:
        return [
            "Protocol 509 Crisis Referral Mandate: User communicates acute distress/crisis signal, "
            "but your reply lacks the mandatory Samaritans of Singapore crisis hotline ('1-767'). "
            "You MUST include the emergency referral (SOS: 1-767 / IMH: 6389 2222 / 995) at the very start of your message."
        ]

    return []


def check_decision_receipts(payload: dict | None) -> list[str]:
    """Check that assistant output does not contain unreceipted GTO engine claims."""
    if not payload or not isinstance(payload, dict):
        return []

    assistant_reply = ""
    transcript_path = payload.get("transcript_path")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, encoding="utf-8") as tf:
                lines = tf.readlines()[-30:]
                for line in reversed(lines):
                    try:
                        rec = json.loads(line)
                        msg = rec.get("message", {})
                        if msg.get("role") == "assistant":
                            content = msg.get("content", "")
                            if isinstance(content, list):
                                assistant_reply = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                            elif isinstance(content, str):
                                assistant_reply = content
                            if assistant_reply:
                                break
                    except Exception:
                        continue
        except Exception:
            pass

    if not assistant_reply:
        assistant_reply = payload.get("text") or payload.get("reply") or ""

    if not assistant_reply:
        return []

    try:
        from athena.intelligence.gto_engine import find_unreceipted_engine_claims

        receipts_path = REPO_ROOT / ".athena" / "decision_receipts.jsonl"
        unreceipted = find_unreceipted_engine_claims(assistant_reply, receipts_path=receipts_path)
        if unreceipted:
            return [
                f"Decision Receipt Gate: Unreceipted GTO engine claims detected: {unreceipted}. "
                "Obtain a valid receipt (GTO-xxxxxxxx) or tag with [agent-estimate]."
            ]
    except Exception:
        pass

    return []


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


def check_currency_leaks(changed_files: list[str]) -> list[str]:
    # Exclude files that *describe* corruption (audit reports, red-team reviews)
    # rather than *exhibiting* it. These contain illustrative examples like
    # "S$1,181.03 -> S,181.03" which are not actual data corruption.
    AUDIT_EXCLUSIONS = [
        "currency_corruption_report",
        "REDTEAM_REVIEW",
        "IMPLEMENTATION_PLAN",
    ]
    md_files = [
        f for f in changed_files
        if f.endswith(".md") and not any(exc in f for exc in AUDIT_EXCLUSIONS)
    ]
    if not md_files:
        return []

    script = REPO_ROOT / ".agent" / "scripts" / "check_currency_integrity.py"
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
            return [line for line in r.stdout.splitlines() if line.strip() and "❌" not in line and "Remediation" not in line and "✓" not in line]
    except Exception as e:
        return [f"Currency integrity check error: {e}"]
    return []


def _file_matches_pattern(file_path: Path, pattern: str) -> bool:
    """Check if file contains a regex pattern. Returns bool only.

    The file content is read and discarded entirely within this function.
    This is intentional: it prevents tainted file data from flowing to
    any caller's log/output statements (CodeQL py/clear-text-logging).
    """
    try:
        data = file_path.read_text(encoding="utf-8", errors="ignore")
        result = bool(re.search(pattern, data))
        del data
        return result
    except Exception:
        return False


def check_restricted_signatures(changed_files: list[str]) -> list[str]:
    RESTRICTED_PATTERNS = [
        (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API signature"),  # pds:allow
        (r"ghp_[a-zA-Z0-9]{20,}", "GitHub PAT signature"),  # pds:allow
        (r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}", "Supabase/JWT signature"),  # pds:allow
        (r"AIza[0-9A-Za-z-_]{35}", "Google API signature"),  # pds:allow
    ]

    violations = []
    for rel_path in changed_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists() or full_path.is_dir():
            continue
        # Skip scanning gitignored / binary / test mock files
        if any(ign in rel_path for ign in [".git/", "tests/", "node_modules/", ".venv/"]):
            continue

        for pat, label in RESTRICTED_PATTERNS:
            if _file_matches_pattern(full_path, pat):
                violations.append(f"Restricted signature detected in {rel_path}: {label}")
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

    # Read stdin if available (Claude Code Stop event payload)
    stdin_payload = None
    if not sys.stdin.isatty():
        try:
            raw_stdin = sys.stdin.read()
            if raw_stdin.strip():
                stdin_payload = json.loads(raw_stdin)
        except Exception:
            pass

    errors = []

    # 0. Protocol 509 crisis referral check (runs even on zero file changes)
    if stdin_payload:
        crisis_errors = check_crisis_referral(stdin_payload)
        if crisis_errors:
            errors.extend(crisis_errors)

        # 0b. Decision receipt gate
        receipt_errors = check_decision_receipts(stdin_payload)
        if receipt_errors:
            errors.extend(receipt_errors)

    changed_files = get_changed_files()

    if changed_files:
        # 1. LaTeX leaks
        latex_errors = check_latex_leaks(changed_files)
        if latex_errors:
            errors.extend(latex_errors)

        # 2. Restricted signature check
        sig_errors = check_restricted_signatures(changed_files)
        if sig_errors:
            errors.extend(sig_errors)

        # 3. Python syntax
        py_errors = check_python_syntax(changed_files)
        if py_errors:
            errors.extend(py_errors)

        # 4. Currency integrity
        curr_errors = check_currency_leaks(changed_files)
        if curr_errors:
            errors.extend(curr_errors)

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
