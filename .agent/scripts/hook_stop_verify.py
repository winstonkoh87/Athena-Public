#!/usr/bin/env python3
"""
hook_stop_verify.py — Output-Side Stop Hook Verifier
===================================================

Runs on agent turn completion (Stop event) across Claude Code and Antigravity.
Enforces fast deterministic gates on turn-scoped modified files and model text:
  - Gate 0: Protocol 509 crisis referral & GTO decision receipt verification
  - Gate 1: Diff-scoped LaTeX/KaTeX math delimiter leaks
  - Gate 2: API secrets/tokens in changed files
  - Gate 3: Python syntax validity on touched scripts
  - Gate 4: Diff-scoped currency truncation check (when check_currency_integrity.py exists)
  - Advisory: Cited repo path existence check (surfaces systemMessage + warnings)

Contract:
  - Claude Code: exit 2 + JSON {"decision": "block", ...} on violation; exit 0 on allow.
  - Antigravity: exit 0 + JSON {"decision": "continue", "reason": ...} on violation; allow on pass.
"""

from __future__ import annotations

import argparse
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
LIB_DIR = SCRIPTS_DIR / "lib"
for _p in (SRC_DIR, SCRIPTS_DIR, LIB_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from hook_io import (  # noqa: E402
    check_hook_waiver,
    detect_harness,
    emit_stop_allow,
    emit_stop_block,
    extract_turn_texts_universal,
    extract_turn_write_context,
)

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
    r"`((?:src/athena|\.agent/scripts|\.agent/skills|\.agent/workflows|\.agent/config|\.context|scripts|tests|docs)/[A-Za-z0-9_./-]+\.(?:py|md|json|yaml|yml|toml|sh))"
    r"(?::L?\d+(?:-L?\d+)?|#L\d+(?:-L?\d+)?)?`"
)
_FENCED_BLOCK_RE = re.compile(r"```[\s\S]*?```")
_CURRENCY_LINE_RE = re.compile(r":L(\d+):")


def _extract_turn_texts(payload: dict | None) -> tuple[str, str]:
    """Extract (user_prompt, assistant_reply) once from Stop payload or transcript."""
    return extract_turn_texts_universal(payload)


def check_crisis_referral(
    payload: dict | None,
    *,
    user_prompt: str | None = None,
    assistant_reply: str | None = None,
) -> list[str]:
    """Check that if user prompt triggered crisis signal, response includes a crisis helpline."""
    if not payload or not isinstance(payload, dict):
        return []

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
    """Return backticked relative repo paths cited outside fenced code blocks that do not exist on disk."""
    if not text:
        return []

    clean_text = _FENCED_BLOCK_RE.sub("", text)
    root = (repo_root or REPO_ROOT).resolve()
    missing: list[str] = []
    seen: set[str] = set()

    for match in _CITED_PATH_RE.finditer(clean_text):
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


def check_restricted_signatures(
    changed_files: list[str], repo_root: Path | None = None
) -> list[str]:
    RESTRICTED_PATTERNS = [
        (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API signature"),  # pds:allow
        (r"ghp_[a-zA-Z0-9]{20,}", "GitHub PAT signature"),  # pds:allow
        (
            r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}",  # pds:allow
            "Supabase/JWT signature",
        ),
        (r"AIza[0-9A-Za-z-_]{35}", "Google API signature"),  # pds:allow
    ]

    root = repo_root or REPO_ROOT
    violations = []
    for rel_path in changed_files:
        full_path = root / rel_path
        if not full_path.exists() or full_path.is_dir():
            continue
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


def _scope_changed_files(
    stdin_payload: dict | None, *, scan_repo: bool
) -> tuple[list[str], list[str], set[str] | None]:
    """Determine which changed files to verify for this Stop invocation."""
    if stdin_payload is None:
        tracked, untracked = get_changed_files_partitioned()
        return tracked, untracked, set(tracked)

    explicit = stdin_payload.get("changed_files")
    if isinstance(explicit, list):
        files = sorted({str(x).strip() for x in explicit if str(x).strip()})
        return files, [], None

    write_ctx = extract_turn_write_context(stdin_payload, repo_root=REPO_ROOT)
    if write_ctx["has_transcript"]:
        written: set[str] = write_ctx["written_files"]
        had_shell: bool = write_ctx["had_shell_exec"]
        turn_ts: float | None = write_ctx["turn_start_ts"]
        if not written and not had_shell:
            return [], [], set()

        raw_tracked, raw_untracked = get_changed_files_partitioned()

        def _include(rel: str) -> bool:
            if rel in written:
                return True
            if had_shell and turn_ts is not None:
                try:
                    return (REPO_ROOT / rel).stat().st_mtime >= (turn_ts - 2.0)
                except OSError:
                    return False
            return False

        tracked = [f for f in raw_tracked if _include(f)]
        untracked = [f for f in raw_untracked if _include(f)]
        return tracked, untracked, set(tracked)

    if scan_repo or os.environ.get("ATHENA_STOP_SCAN_REPO") == "1":
        tracked, untracked = get_changed_files_partitioned()
        return tracked, untracked, set(tracked)

    return [], [], set()


def main() -> None:
    parser = argparse.ArgumentParser(description="Output-Side Stop Hook Verifier")
    parser.add_argument(
        "--scan-repo",
        action="store_true",
        help="Scan all dirty repo files even when stdin has no transcript",
    )
    args, _ = parser.parse_known_args()

    start_time = time.time()

    stdin_payload = None
    if not sys.stdin.isatty():
        try:
            raw_stdin = sys.stdin.read()
            if raw_stdin.strip():
                parsed = json.loads(raw_stdin)
                if isinstance(parsed, dict):
                    stdin_payload = parsed
        except Exception:
            pass

    harness = detect_harness(stdin_payload)

    crisis_errors: list[str] = []
    sig_errors: list[str] = []
    waivable_errors: list[str] = []
    warnings: list[str] = []

    if stdin_payload:
        user_prompt, assistant_reply = _extract_turn_texts(stdin_payload)
        crisis_errors.extend(
            check_crisis_referral(
                stdin_payload, user_prompt=user_prompt, assistant_reply=assistant_reply
            )
        )
        waivable_errors.extend(
            check_decision_receipts(stdin_payload, assistant_reply=assistant_reply)
        )
        missing_paths = find_missing_cited_paths(assistant_reply, repo_root=REPO_ROOT)
        if missing_paths:
            warnings.extend(f"Cited path not found on disk: {p}" for p in missing_paths)

    tracked_changed, untracked_changed, tracked_set = _scope_changed_files(
        stdin_payload, scan_repo=args.scan_repo
    )
    changed_files = sorted(set(tracked_changed) | set(untracked_changed))

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

        waivable_errors.extend(
            check_latex_leaks(
                changed_files, tracked_set=tracked_set, added_map=shared_added_map
            )
        )
        sig_errors.extend(check_restricted_signatures(changed_files))
        waivable_errors.extend(check_python_syntax(changed_files))
        waivable_errors.extend(
            check_currency_leaks(
                changed_files, tracked_set=tracked_set, added_map=shared_added_map
            )
        )

    if waivable_errors:
        is_reentry = bool(
            stdin_payload
            and (
                stdin_payload.get("stop_hook_active")
                or stdin_payload.get("continuationActive")
            )
        )
        if is_reentry:
            warnings.extend(
                f"Loop guard allowed after retry: {err}" for err in waivable_errors[:5]
            )
            waivable_errors = []
        else:
            waiver = check_hook_waiver("hook_stop_verify", REPO_ROOT)
            if waiver:
                warnings.extend(
                    f"Waived ({waiver}): {err}" for err in waivable_errors[:5]
                )
                waivable_errors = []

    errors = crisis_errors + sig_errors + waivable_errors
    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    if errors:
        reason = (
            "Output Verifier Blocked Completion:\n"
            + "\n".join(f"  - {err}" for err in errors[:10])
            + "\nPlease fix the above violations before completing the turn."
        )
        extra: dict[str, object] = {"latency_ms": elapsed_ms}
        if warnings:
            extra["warnings"] = warnings
        emit_stop_block(reason, harness, extra=extra)
    else:
        extra = {"latency_ms": elapsed_ms}
        if warnings:
            extra["warnings"] = warnings
            extra["systemMessage"] = "WARNING: " + "; ".join(warnings)
        emit_stop_allow(harness, extra=extra)


if __name__ == "__main__":
    main()
