"""
athena.memory.dream_verifier
============================

Deterministic (0 LLM tokens) transcript verifier and safe pruning driver
for `/dream` consolidation over `.athena/memory/SYSTEM_LEARNINGS.md`.

Verdicts:
- PRUNE_EXPIRED: non-pinned learning whose `expires_at` timestamp has passed.
- UNVERIFIED_CLAIM: completion/success claim contradicted by unresolved failure
  signals in its corresponding session log (prevents Pokémon-Red false memories).
- ALREADY_CODIFIED: substantive token overlap (>= 70% on >= 4 tokens) already
  present in `.context/CANONICAL.md`.
- READY_TO_GRADUATE: corresponding session log found with no unresolved failure.
- NEEDS_REVIEW: no corresponding session log on disk to verify against.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from athena.core import config
from athena.memory.learnings import (
    _to_utc_now,
    compact_learnings_stores,
    get_learnings_stats,
    is_expired,
    load_raw_system_learnings,
    load_system_learnings,
)

_OPTIMISTIC_CLAIM_RE = re.compile(
    r"\b(?:fixed|resolved|shipped|passing|passed|verified|green|eliminated|cured|completed)\b",
    re.IGNORECASE,
)
_CONTRADICTION_SIGNAL_RE = re.compile(
    r"\b(?:FAILED|AssertionError|Traceback|reverted|rolled back|exit code [1-9]|BLOCKED|broken|rejected)\b",
    re.IGNORECASE,
)
_RECOVERY_SIGNAL_RE = re.compile(
    r"\b(?:all passed|0 failed|tests? green|fixed after|resolved after|passing now)\b",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[a-z0-9]{3,}")
_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "are",
        "was",
        "were",
        "have",
        "has",
        "had",
        "not",
        "use",
        "using",
        "when",
        "into",
        "over",
        "only",
        "all",
        "per",
        "via",
    }
)

VERDICT_ORDER = (
    "PRUNE_EXPIRED",
    "UNVERIFIED_CLAIM",
    "ALREADY_CODIFIED",
    "READY_TO_GRADUATE",
    "NEEDS_REVIEW",
)


def _tokenize_substantive(text: str) -> set[str]:
    return {tok for tok in _WORD_RE.findall((text or "").lower()) if tok not in _STOPWORDS}


def _build_canonical_windows(canonical_path: Path) -> tuple[list[tuple[int, set[str]]], list[tuple[int, set[str]]]]:
    if not canonical_path.exists():
        return [], []
    lines = canonical_path.read_text(encoding="utf-8", errors="replace").splitlines()
    line_tokens = [_tokenize_substantive(line) for line in lines]
    single_lines: list[tuple[int, set[str]]] = []
    multi_windows: list[tuple[int, set[str]]] = []
    for idx, toks in enumerate(line_tokens):
        line_num = idx + 1
        if toks:
            single_lines.append((line_num, toks))
        # Rolling 3-line window catches rules split across wrapped bullets/tables
        if idx + 1 < len(line_tokens):
            merged = set(toks) | line_tokens[idx + 1]
            if idx + 2 < len(line_tokens):
                merged |= line_tokens[idx + 2]
            if merged:
                multi_windows.append((line_num, merged))
    return single_lines, multi_windows


def _find_canonical_match(
    learning_text: str,
    windows: tuple[list[tuple[int, set[str]]], list[tuple[int, set[str]]]],
) -> str | None:
    tokens = _tokenize_substantive(learning_text)
    single_lines, multi_windows = windows
    if len(tokens) < 4 or (not single_lines and not multi_windows):
        return None
    for candidate_list in (single_lines, multi_windows):
        best_line: int | None = None
        best_ratio = 0.0
        for line_num, win_tokens in candidate_list:
            ratio = len(tokens & win_tokens) / len(tokens)
            if ratio >= 0.70 and ratio > best_ratio:
                best_ratio = ratio
                best_line = line_num
        if best_line is not None:
            return f"CANONICAL.md#L{best_line}"
    return None


def _index_session_logs(logs_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    if not logs_dir.exists():
        return index
    for candidate_dir in (logs_dir, logs_dir / "archive"):
        if not candidate_dir.is_dir():
            continue
        for entry in candidate_dir.iterdir():
            if entry.is_file() and entry.suffix == ".md":
                index.setdefault(entry.stem, entry)
    return index


def _resolve_session_log(session_id: str, logs_dir: Path, log_index: dict[str, Path]) -> Path | None:
    sid = (session_id or "").strip()
    if not sid or sid == "unknown":
        return None
    direct = logs_dir / f"{sid}.md"
    if direct.is_file():
        return direct
    archived = logs_dir / "archive" / f"{sid}.md"
    if archived.is_file():
        return archived
    if sid in log_index:
        return log_index[sid]
    suffix = f"-{sid}"
    for stem, path in log_index.items():
        if stem.endswith(suffix):
            return path
    return None


def _find_unresolved_contradictions(log_path: Path) -> list[str]:
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    contradiction_lines: list[int] = []
    last_recovery_line = 0
    for idx, line in enumerate(lines, 1):
        if _CONTRADICTION_SIGNAL_RE.search(line):
            contradiction_lines.append(idx)
        if _RECOVERY_SIGNAL_RE.search(line):
            last_recovery_line = idx

    unresolved = [ln for ln in contradiction_lines if ln > last_recovery_line]
    if not unresolved:
        return []
    return [f"{log_path.name}#L{ln}" for ln in unresolved[:3]]


def verify_pending_learnings(
    *,
    project_root: Path | None = None,
    system_path: Path | None = None,
    user_path: Path | None = None,
    session_logs_dir: Path | None = None,
    canonical_path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Deterministically verify pending SYSTEM_LEARNINGS.md rows at zero LLM token cost."""
    root = Path(project_root) if project_root is not None else None
    sys_file = (
        system_path
        if system_path is not None
        else ((root / ".athena" / "memory" / "SYSTEM_LEARNINGS.md") if root else config.SYSTEM_LEARNINGS_FILE)
    )
    usr_file = (
        user_path
        if user_path is not None
        else ((root / ".athena" / "memory" / "USER_PROFILE.yaml") if root else config.USER_PROFILE_FILE)
    )
    logs_dir = (
        session_logs_dir
        if session_logs_dir is not None
        else ((root / ".context" / "memories" / "session_logs") if root else config.SESSIONS_DIR)
    )
    canon_file = (
        canonical_path
        if canonical_path is not None
        else ((root / ".context" / "CANONICAL.md") if root else config.CANONICAL_PATH)
    )

    now_utc = _to_utc_now(now)
    raw_rows = load_raw_system_learnings(sys_file)
    deduped_rows = load_system_learnings(sys_file)
    duplicate_count = max(0, len(raw_rows) - len(deduped_rows))
    stats = get_learnings_stats(user_path=usr_file, system_path=sys_file, now=now_utc)

    canonical_windows = _build_canonical_windows(canon_file)
    log_index = _index_session_logs(logs_dir)

    counts: dict[str, int] = dict.fromkeys(VERDICT_ORDER, 0)
    by_verdict: dict[str, list[dict[str, Any]]] = {verdict: [] for verdict in VERDICT_ORDER}
    items: list[dict[str, Any]] = []

    for row in deduped_rows:
        if row.get("integrated"):
            continue

        learning_text = str(row.get("learning") or "")
        pinned = bool(row.get("pinned"))
        expires_at = row.get("expires_at")
        log_path = _resolve_session_log(str(row.get("session") or ""), logs_dir, log_index)

        evidence_lines: list[str] = []
        canonical_line: str | None = None

        if not pinned and is_expired(expires_at, now_utc):
            verdict = "PRUNE_EXPIRED"
        else:
            if _OPTIMISTIC_CLAIM_RE.search(learning_text) and log_path is not None:
                evidence_lines = _find_unresolved_contradictions(log_path)
            if evidence_lines:
                verdict = "UNVERIFIED_CLAIM"
            else:
                canonical_line = _find_canonical_match(learning_text, canonical_windows)
                if canonical_line is not None:
                    verdict = "ALREADY_CODIFIED"
                elif log_path is not None:
                    verdict = "READY_TO_GRADUATE"
                else:
                    verdict = "NEEDS_REVIEW"

        item: dict[str, Any] = {
            "date": row.get("date", ""),
            "session": row.get("session", ""),
            "line_num": row.get("line_num", 0),
            "learning": learning_text,
            "pinned": pinned,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "verdict": verdict,
            "evidence_lines": evidence_lines,
            "canonical_line": canonical_line,
            "session_log": log_path.name if log_path is not None else None,
        }
        counts[verdict] += 1
        by_verdict[verdict].append(item)
        items.append(item)

    return {
        "counts": counts,
        "duplicate_count": duplicate_count,
        "total_pending": len(items),
        "stats": stats,
        "items": items,
        "by_verdict": by_verdict,
    }


def apply_safe_dream_pruning(
    *,
    project_root: Path | None = None,
    system_path: Path | None = None,
    user_path: Path | None = None,
    dry_run: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Deterministically deduplicate stores and prune non-pinned expired entries only."""
    root = Path(project_root) if project_root is not None else None
    sys_file = (
        system_path
        if system_path is not None
        else ((root / ".athena" / "memory" / "SYSTEM_LEARNINGS.md") if root else config.SYSTEM_LEARNINGS_FILE)
    )
    usr_file = (
        user_path
        if user_path is not None
        else ((root / ".athena" / "memory" / "USER_PROFILE.yaml") if root else config.USER_PROFILE_FILE)
    )
    return compact_learnings_stores(
        user_path=usr_file,
        system_path=sys_file,
        dry_run=dry_run,
        prune_expired=True,
        now=now,
    )
