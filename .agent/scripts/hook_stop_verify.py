#!/usr/bin/env python3
"""
hook_stop_verify.py — Output-Side Stop Hook Verifier
===================================================

Runs on agent turn completion (Stop event) before the user sees the output.
Enforces fast (<3s) deterministic gates on changed files:
  - Gate 0: Protocol 509 crisis referral & GTO decision receipt verification
  - Gate 1: Diff-scoped LaTeX/KaTeX math delimiter leaks
  - Gate 2: API secrets/tokens in changed files
  - Gate 3: Python syntax validity on touched scripts
  - Gate 4: Diff-scoped currency truncation check (when check_currency_integrity.py exists)
  - Advisory: Non-blocking cited repo path check (warnings only)

Contract:
  - If any gate fails: prints JSON {"decision": "block", "reason": ...} + stderr, exits 2
  - If all gates pass: prints JSON {"decision": "allow", ...}, exits 0
"""

from __future__ import annotations

import json
import os
import py_compile
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from athena.core.lambda_scorer import detect_crisis_signal
except ImportError:
    def detect_crisis_signal(text: str) -> bool:
        return False

CRISIS_HOTLINE_TOKENS = (
    "1-767",
    "988",
    "findahelpline.com",
    "6389 2222",
    "995",
    "999",
    "911",
    "112",
)

_CITED_PATH_RE = re.compile(
    r"`((?:src/athena|\.agent/scripts|scripts|tests)/[A-Za-z0-9_./-]+\.(?:py|md|json|yaml|yml|sh))"
    r"(?::L?\d+(?:-L?\d+)?|#L\d+(?:-L?\d+)?)?`"
)
_CURRENCY_LINE_RE = re.compile(r":L(\d+):")


def _extract_turn_texts(payload: dict | None) -> tuple[str, str]:
    """Extract (user_prompt, assistant_reply) once from Stop payload or transcript."""
    if not payload or not isinstance(payload, dict):
        return "", ""

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
                            content = " ".join(
                                c.get("text", "") for c in content if isinstance(c, dict)
                            )
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

    return user_prompt, assistant_reply


def check_crisis_referral(
    payload: dict | None,
    *,
    user_prompt: str | None = None,
    assistant_reply: str | None = None,
) -> list[str]:
    """Check that if user prompt triggered crisis signal, response includes a crisis helpline."""
    if not payload or not isinstance(payload, dict):
        return []

    # Honour stop_hook_active to avoid loop
    if payload.get("stop_hook_active"):
        return []

    if user_prompt is None or assistant_reply is None:
        extracted_prompt, extracted_reply = _extract_turn_texts(payload)
        if user_prompt is None:
            user_prompt = extracted_prompt
        if assistant_reply is None:
            assistant_reply = extracted_reply

    reply_lower = assistant_reply.lower()
    if (
        user_prompt
        and detect_crisis_signal(user_prompt)
        and not any(tok in reply_lower for tok in CRISIS_HOTLINE_TOKENS)
    ):
        return [
            "Protocol 509 Crisis Referral Mandate: User communicates acute distress/crisis signal, "
            "but your reply lacks a crisis helpline referral. "
            "You MUST include emergency support (988 US/Canada, SOS 1-767 / IMH 6389 2222 / 995 SG, "
            "or https://findahelpline.com) at the very start of your message."
        ]

    return []


def check_decision_receipts(
    payload: dict | None,
    *,
    assistant_reply: str | None = None,
) -> list[str]:
    """Check that assistant output does not contain unreceipted GTO engine claims."""
    if not payload or not isinstance(payload, dict):
        return []

    if assistant_reply is None:
        _, assistant_reply = _extract_turn_texts(payload)

    if not assistant_reply:
        return []

    try:
        from athena.intelligence.gto_engine import find_unreceipted_engine_claims

        receipts_path = REPO_ROOT / ".athena" / "decision_receipts.jsonl"
        unreceipted = find_unreceipted_engine_claims(
            assistant_reply, receipts_path=receipts_path
        )
        if unreceipted:
            return [
                f"Decision Receipt Gate: Unreceipted GTO engine claims detected: {unreceipted}. "
                "Obtain a valid receipt (GTO-xxxxxxxx) or tag with [agent-estimate]."
            ]
    except Exception:
        pass

    return []


def find_missing_cited_paths(
    text: str, repo_root: Path | None = None
) -> list[str]:
    """Return backticked relative repo paths cited in text that do not exist on disk."""
    if not text:
        return []

    root = (repo_root or REPO_ROOT).resolve()
    missing: list[str] = []
    seen: set[str] = set()

    for match in _CITED_PATH_RE.finditer(text):
        rel = match.group(1)
        if rel in seen:
            continue
        if "..." in rel or any(ch in rel for ch in "*?<>[]{}"):
            continue
        seen.add(rel)
        if not (root / rel).exists():
            missing.append(rel)

    return missing


def get_changed_files_partitioned(
    repo_root: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Return (tracked_changed, untracked) via a single git status --porcelain call."""
    root = repo_root or REPO_ROOT
    tracked: set[str] = set()
    untracked: set[str] = set()

    try:
        res = subprocess.run(
            ["git", "-c", "core.quotepath=false", "status", "--porcelain", "-uall"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode != 0:
            return [], []

        for raw_line in res.stdout.splitlines():
            line = raw_line.rstrip("\r\n")
            if len(line) < 4:
                continue
            xy = line[:2]
            raw_path = line[3:]
            if ("R" in xy or "C" in xy) and " -> " in raw_path:
                raw_path = raw_path.split(" -> ", 1)[1]
            path = raw_path.strip().strip('"')
            if not path or xy in ("D ", " D", "DD"):
                continue
            full = root / path
            if not full.exists() or full.is_dir():
                continue
            if xy == "??":
                untracked.add(path)
            else:
                tracked.add(path)
    except Exception:
        pass

    return sorted(tracked), sorted(untracked)


def get_changed_files() -> list[str]:
    """Return sorted list of modified, staged, and untracked files."""
    tracked, untracked = get_changed_files_partitioned()
    return sorted(set(tracked) | set(untracked))


def check_latex_leaks(
    changed_files: list[str],
    tracked_set: set[str] | None = None,
    added_map: dict[str, set[int]] | None = None,
) -> list[str]:
    md_files = [f for f in changed_files if f.endswith((".md", ".txt"))]
    if not md_files:
        return []

    script = REPO_ROOT / ".agent" / "scripts" / "check_latex_leak.py"
    if not script.exists():
        return []

    try:
        from check_latex_leak import (
            get_git_added_lines_batch,
            scan_file,
            scan_file_diff,
        )
    except Exception as e:
        return [f"LaTeX check import error: {e}"]

    if added_map is None:
        tracked_md = [f for f in md_files if tracked_set is None or f in tracked_set]
        added_map = get_git_added_lines_batch(tracked_md, repo_root=REPO_ROOT) or {}

    violations: list[str] = []
    for rel_path in md_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            continue
        if tracked_set is not None and rel_path not in tracked_set:
            viols = scan_file(str(full_path))
        elif rel_path in added_map:
            viols = scan_file_diff(
                str(full_path), repo_root=REPO_ROOT, added_lines=added_map[rel_path]
            )
        else:
            viols = scan_file_diff(str(full_path), repo_root=REPO_ROOT)
        if viols:
            violations.append(f"❌ {rel_path}: {len(viols)} violation(s)")
            for line_num, content in viols[:10]:
                violations.append(f"   Line {line_num}: {content}")
    return violations


def check_currency_leaks(
    changed_files: list[str],
    tracked_set: set[str] | None = None,
    added_map: dict[str, set[int]] | None = None,
) -> list[str]:
    # Exclude files that *describe* corruption (audit reports, red-team reviews)
    # rather than *exhibiting* it. These contain illustrative examples like
    # "S$1,181.03 -> S,181.03" which are not actual data corruption.
    AUDIT_EXCLUSIONS = [
        "currency_corruption_report",
        "REDTEAM_REVIEW",
        "IMPLEMENTATION_PLAN",
    ]
    md_files = [
        f
        for f in changed_files
        if f.endswith(".md") and not any(exc in f for exc in AUDIT_EXCLUSIONS)
    ]
    if not md_files:
        return []

    script = REPO_ROOT / ".agent" / "scripts" / "check_currency_integrity.py"
    if not script.exists():
        return []

    try:
        from check_currency_integrity import check_content
        from check_latex_leak import (
            get_git_added_line_numbers,
            get_git_added_lines_batch,
        )
    except Exception as e:
        return [f"Currency integrity check import error: {e}"]

    if added_map is None:
        tracked_md = [f for f in md_files if tracked_set is None or f in tracked_set]
        added_map = get_git_added_lines_batch(tracked_md, repo_root=REPO_ROOT) or {}

    violations: list[str] = []
    for rel_path in md_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            continue
        content = full_path.read_text(encoding="utf-8", errors="replace")
        file_errs = check_content(content, rel_path)
        if not file_errs:
            continue

        if tracked_set is None or rel_path in tracked_set:
            if rel_path in added_map:
                added_lines: set[int] | None = added_map[rel_path]
            else:
                added_lines = get_git_added_line_numbers(str(full_path), repo_root=REPO_ROOT)
            if added_lines is not None:
                filtered: list[str] = []
                for err in file_errs:
                    m = _CURRENCY_LINE_RE.search(err)
                    if m and int(m.group(1)) in added_lines:
                        filtered.append(err)
                file_errs = filtered

        violations.extend(file_errs)
    return violations


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
        (
            r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}",  # pds:allow
            "Supabase/JWT signature",
        ),
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

    errors: list[str] = []
    warnings: list[str] = []

    # 0. Turn-text gates (crisis referral, GTO receipts, non-blocking cited-path check)
    if stdin_payload:
        user_prompt, assistant_reply = _extract_turn_texts(stdin_payload)
        crisis_errors = check_crisis_referral(
            stdin_payload, user_prompt=user_prompt, assistant_reply=assistant_reply
        )
        if crisis_errors:
            errors.extend(crisis_errors)

        receipt_errors = check_decision_receipts(
            stdin_payload, assistant_reply=assistant_reply
        )
        if receipt_errors:
            errors.extend(receipt_errors)

        missing_paths = find_missing_cited_paths(assistant_reply, repo_root=REPO_ROOT)
        if missing_paths:
            warnings.extend(f"Cited path not found on disk: {p}" for p in missing_paths)

    tracked_changed, untracked_changed = get_changed_files_partitioned()
    changed_files = sorted(set(tracked_changed) | set(untracked_changed))
    tracked_set = set(tracked_changed)

    if changed_files:
        shared_added_map: dict[str, set[int]] | None = None
        tracked_md = [f for f in tracked_changed if f.endswith((".md", ".txt"))]
        if tracked_md:
            try:
                from check_latex_leak import get_git_added_lines_batch

                shared_added_map = get_git_added_lines_batch(
                    tracked_md, repo_root=REPO_ROOT
                )
            except Exception:
                shared_added_map = None

        # 1. LaTeX leaks (diff-scoped for tracked files)
        latex_errors = check_latex_leaks(
            changed_files, tracked_set=tracked_set, added_map=shared_added_map
        )
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

        # 4. Currency integrity (diff-scoped for tracked files)
        curr_errors = check_currency_leaks(
            changed_files, tracked_set=tracked_set, added_map=shared_added_map
        )
        if curr_errors:
            errors.extend(curr_errors)

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    if errors:
        reason = (
            "Output Verifier Blocked Completion:\n"
            + "\n".join(f"  - {err}" for err in errors[:10])
            + "\nPlease fix the above violations before completing the turn."
        )
        payload: dict[str, object] = {
            "decision": "block",
            "reason": reason,
            "latency_ms": elapsed_ms,
        }
        if warnings:
            payload["warnings"] = warnings
        print(json.dumps(payload, indent=2))
        # Claude Code hooks: exit 2 = blocking, exit 1 = non-blocking (ignored).
        # stderr is fed back to Claude as the error message on exit 2.
        print(reason, file=sys.stderr)
        sys.exit(2)
    else:
        payload = {"decision": "allow", "latency_ms": elapsed_ms}
        if warnings:
            payload["warnings"] = warnings
        print(json.dumps(payload))
        sys.exit(0)


if __name__ == "__main__":
    main()
