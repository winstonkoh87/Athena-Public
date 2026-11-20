"""
athena.memory.learnings
=======================

Local-only learning store loader, deduplicator, compactor, and search engine for:
- .athena/memory/USER_PROFILE.yaml (`[U]` session learnings, personal privacy wall)
- .athena/memory/SYSTEM_LEARNINGS.md (`[S]` system/workflow learnings)

Privacy invariant: these files stay strictly local and are never uploaded to cloud
vector stores. `USER_PROFILE.yaml` retrieval is gated behind `include_personal=True`.
"""

from __future__ import annotations

import logging
import math
import os
import re
import tempfile
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from athena.core.models import SearchResult

try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    _fcntl = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

yaml: Any = None
try:
    import yaml as _yaml

    yaml = _yaml
    _YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    _HAS_YAML = True
except ImportError:
    _YAML_LOADER = None
    _HAS_YAML = False

_ROW_DATE_RE = re.compile(r"^\|\s*(20\d{2}-\d{2}-\d{2})\s*\|")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
_INLINE_EXPIRES_RE = re.compile(r"\[(?:expires|expires_at)\s*:\s*([0-9T:+-]{10,32}(?:Z)?)\]", re.IGNORECASE)
_INLINE_PINNED_RE = re.compile(r"\[pinned\]", re.IGNORECASE)
_DATE_BOUND_HINT_RE = re.compile(
    r"\b(?:20\d{2}-\d{2}-\d{2}|deadline|expires|expiring|until\s+\d|due\s+(?:on|by)\s+\d|"
    r"by\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b)",
    re.IGNORECASE,
)
_ISO_DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CONFIDENCE_RANK = {"low": 1, "medium": 2, "high": 3}

_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "is",
        "in",
        "to",
        "of",
        "a",
        "an",
        "on",
        "at",
        "by",
        "or",
        "not",
        "with",
        "from",
        "what",
        "how",
        "why",
        "when",
        "where",
        "who",
        "should",
        "can",
        "could",
        "would",
        "do",
        "does",
        "did",
        "my",
        "me",
        "i",
        "it",
        "this",
        "that",
        "are",
        "was",
        "were",
        "be",
        "been",
    }
)

# Cache parsed stores keyed by (kind, resolved_path, mtime_ns, size)
_STORE_CACHE: dict[tuple[str, str, int, int], dict[str, Any]] = {}
_MAX_CACHE_ENTRIES = 16


def _resolve_store_path(kind: str, override: Path | None = None) -> Path:
    if override is not None:
        return Path(override)
    import athena.core.config as cfg

    if kind == "user":
        return Path(cfg.USER_PROFILE_FILE)
    return Path(cfg.SYSTEM_LEARNINGS_FILE)


def _stat_sig(path: Path) -> tuple[int, int] | None:
    try:
        st = path.stat()
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def _cache_put(key: tuple[str, str, int, int], value: dict[str, Any]) -> None:
    if len(_STORE_CACHE) >= _MAX_CACHE_ENTRIES:
        _STORE_CACHE.clear()
    _STORE_CACHE[key] = value


def normalize_learning_text(text: str) -> str:
    """Normalize learning text for idempotent deduplication across sessions."""
    collapsed = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return collapsed.rstrip(".;:")


def _is_integrated_status(status: str) -> bool:
    s = (status or "").strip().lower()
    return bool(s) and "pending" not in s


@contextmanager
def _advisory_file_lock(lock_path: Path) -> Iterator[None]:
    """Acquire an advisory exclusive flock around disk mutations when available."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lock_fh:
        if _fcntl is not None:
            _fcntl.flock(lock_fh.fileno(), _fcntl.LOCK_EX)
        try:
            yield
        finally:
            if _fcntl is not None:
                try:
                    _fcntl.flock(lock_fh.fileno(), _fcntl.LOCK_UN)
                except OSError as exc:
                    logger.debug("flock unlock skipped for %s: %s", lock_path, exc)


def atomic_write_text(path: Path, text: str, mode: int = 0o600) -> None:
    """Atomically write UTF-8 text via advisory lock, fsync, chmod, and os.replace."""
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    lock_path = resolved.parent / f".{resolved.name}.lock"

    with _advisory_file_lock(lock_path):
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=resolved.parent,
                prefix=f".{resolved.name}.",
                suffix=".tmp",
                delete=False,
            ) as tmp_fh:
                tmp_path = Path(tmp_fh.name)
                tmp_fh.write(text)
                tmp_fh.flush()
                os.fsync(tmp_fh.fileno())
            os.chmod(tmp_path, mode)
            os.replace(tmp_path, resolved)
        except Exception:
            if tmp_path is not None and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError as cleanup_exc:
                    logger.debug("Temp file cleanup failed for %s: %s", tmp_path, cleanup_exc)
            raise


def _to_utc_now(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def parse_expires_at(value: Any = None, text: str = "") -> datetime | None:
    """Parse an explicit YAML/JSON expires_at value or inline `[expires_at:...]` tag to UTC."""
    candidate: Any = value
    if candidate is None and text:
        m = _INLINE_EXPIRES_RE.search(text)
        if m:
            candidate = m.group(1)

    if candidate is None or candidate == "":
        return None
    if isinstance(candidate, datetime):
        if candidate.tzinfo is None:
            return candidate.replace(tzinfo=timezone.utc)
        return candidate.astimezone(timezone.utc)
    if isinstance(candidate, date):
        return datetime(candidate.year, candidate.month, candidate.day, 23, 59, 59, tzinfo=timezone.utc)

    raw = str(candidate).strip()
    if not raw:
        return None
    if _ISO_DATE_ONLY_RE.match(raw):
        try:
            parsed_d = date.fromisoformat(raw)
        except ValueError:
            return None
        return datetime(parsed_d.year, parsed_d.month, parsed_d.day, 23, 59, 59, tzinfo=timezone.utc)

    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        parsed_dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed_dt.tzinfo is None:
        return parsed_dt.replace(tzinfo=timezone.utc)
    return parsed_dt.astimezone(timezone.utc)


def is_expired(expires_at: datetime | None, now: datetime | None = None) -> bool:
    """Return True if expires_at has passed relative to UTC now."""
    if expires_at is None:
        return False
    exp_utc = expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at.astimezone(timezone.utc)
    return _to_utc_now(now) >= exp_utc


def is_imminent(
    expires_at: datetime | None,
    now: datetime | None = None,
    hours: float = 72.0,
) -> bool:
    """Return True if expires_at is unexpired and within the next `hours` hours."""
    if expires_at is None:
        return False
    now_utc = _to_utc_now(now)
    exp_utc = expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at.astimezone(timezone.utc)
    delta_s = (exp_utc - now_utc).total_seconds()
    return 0.0 < delta_s <= hours * 3600.0


def _parse_system_row(line: str, line_num: int) -> dict[str, Any] | None:
    stripped = line.strip()
    if not _ROW_DATE_RE.match(stripped):
        return None
    inner = stripped[1:-1] if stripped.endswith("|") else stripped[1:]
    left = inner.split("|", 2)
    if len(left) < 3:
        return None
    date_val, session_val, rest = left[0].strip(), left[1].strip(), left[2]
    right = rest.rsplit("|", 1)
    if len(right) != 2:
        return None
    learning_val, status_val = right[0].strip(), right[1].strip()
    if not learning_val:
        return None
    return {
        "date": date_val,
        "session": session_val,
        "learning": learning_val,
        "status": status_val or "⏳ Pending",
        "integrated": _is_integrated_status(status_val),
        "line_num": line_num,
        "norm": normalize_learning_text(learning_val),
        "expires_at": parse_expires_at(None, learning_val),
        "pinned": bool(_INLINE_PINNED_RE.search(learning_val)),
    }


def _dedup_system_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    index_by_norm: dict[str, int] = {}
    for row in rows:
        norm = row["norm"]
        if not norm:
            continue
        existing_idx = index_by_norm.get(norm)
        if existing_idx is None:
            index_by_norm[norm] = len(deduped)
            deduped.append(row)
            continue
        existing = deduped[existing_idx]
        # Prefer integrated (non-Pending) rows; otherwise prefer the newer entry.
        if row["integrated"] or not existing["integrated"]:
            deduped[existing_idx] = row
    return deduped


def _load_system_bundle(path: Path | None = None) -> dict[str, Any]:
    resolved = _resolve_store_path("system", path)
    sig = _stat_sig(resolved)
    if sig is None:
        return {"kind": "system", "raw_count": 0, "rows": [], "idf": None, "tokens_list": None, "texts_lower": None}

    cache_key = ("system", str(resolved.resolve()), sig[0], sig[1])
    cached = _STORE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        text = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"kind": "system", "raw_count": 0, "rows": [], "idf": None, "tokens_list": None, "texts_lower": None}

    raw_rows: list[dict[str, Any]] = []
    for line_num, line in enumerate(text.splitlines(), 1):
        parsed = _parse_system_row(line, line_num)
        if parsed is not None:
            raw_rows.append(parsed)

    deduped = _dedup_system_rows(raw_rows)
    bundle = {
        "kind": "system",
        "raw_count": len(raw_rows),
        "raw_rows": raw_rows,
        "rows": deduped,
        "tokens_list": None,
        "idf": None,
        "texts_lower": None,
    }
    _cache_put(cache_key, bundle)
    return bundle


def _dedup_user_notes(notes: list[Any]) -> tuple[list[dict[str, Any]], int]:
    raw_count = 0
    deduped: list[dict[str, Any]] = []
    index_by_norm: dict[str, int] = {}

    for item in notes:
        if isinstance(item, dict):
            learned = str(item.get("learned") or "").strip()
            session = str(item.get("session") or "unknown").strip()
            confidence = str(item.get("confidence") or "medium").strip().lower()
            entry = {
                **item,
                "learned": learned,
                "session": session,
                "confidence": confidence,
            }
        else:
            learned = str(item or "").strip()
            entry = {
                "learned": learned,
                "session": "unknown",
                "confidence": "medium",
            }
        if not learned:
            continue
        raw_count += 1
        norm = normalize_learning_text(learned)
        entry["_norm"] = norm
        entry["_expires_dt"] = parse_expires_at(entry.get("expires_at"), learned)
        entry["_pinned"] = bool(entry.get("pinned")) or bool(_INLINE_PINNED_RE.search(learned))
        existing_idx = index_by_norm.get(norm)
        if existing_idx is None:
            index_by_norm[norm] = len(deduped)
            deduped.append(entry)
            continue
        existing = deduped[existing_idx]
        cur_rank = _CONFIDENCE_RANK.get(entry["confidence"], 1)
        prev_rank = _CONFIDENCE_RANK.get(existing.get("confidence", "medium"), 1)
        if cur_rank >= prev_rank:
            deduped[existing_idx] = entry

    return deduped, raw_count


def _load_user_bundle(path: Path | None = None) -> dict[str, Any]:
    resolved = _resolve_store_path("user", path)
    sig = _stat_sig(resolved)
    if sig is None or not _HAS_YAML or _YAML_LOADER is None:
        return {"kind": "user", "raw_count": 0, "notes": [], "idf": None, "tokens_list": None, "texts_lower": None}

    cache_key = ("user", str(resolved.resolve()), sig[0], sig[1])
    cached = _STORE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        raw_text = resolved.read_text(encoding="utf-8", errors="replace")
        data = yaml.load(raw_text, Loader=_YAML_LOADER)
    except Exception:
        return {"kind": "user", "raw_count": 0, "notes": [], "idf": None, "tokens_list": None, "texts_lower": None}

    if not isinstance(data, dict):
        return {"kind": "user", "raw_count": 0, "notes": [], "idf": None, "tokens_list": None, "texts_lower": None}

    raw_notes = data.get("notes") or []
    if not isinstance(raw_notes, list):
        raw_notes = []

    deduped, raw_count = _dedup_user_notes(raw_notes)
    bundle = {
        "kind": "user",
        "raw_count": raw_count,
        "notes": deduped,
        "tokens_list": None,
        "idf": None,
        "texts_lower": None,
    }
    _cache_put(cache_key, bundle)
    return bundle


def _tokenize_text(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw in _TOKEN_RE.findall(text.lower()):
        if len(raw) >= 2 and raw not in _STOPWORDS:
            tokens.add(raw)
        if "-" in raw:
            for part in raw.split("-"):
                if len(part) >= 2 and part not in _STOPWORDS:
                    tokens.add(part)
    return tokens


def _tokenize_query(query: str) -> list[str]:
    seen: set[str] = set()
    keywords: list[str] = []
    for raw in _TOKEN_RE.findall((query or "").lower()):
        if len(raw) >= 2 and raw not in _STOPWORDS and raw not in seen:
            seen.add(raw)
            keywords.append(raw)
    return keywords


def _build_idf_index(texts_lower: list[str]) -> tuple[list[set[str]], dict[str, float]]:
    doc_freq: Counter[str] = Counter()
    tokens_list: list[set[str]] = []
    for text in texts_lower:
        toks = _tokenize_text(text)
        tokens_list.append(toks)
        for tok in toks:
            doc_freq[tok] += 1
    n_docs = max(1, len(texts_lower))
    idf = {tok: math.log((n_docs + 1) / (df + 1)) + 1.0 for tok, df in doc_freq.items()}
    return tokens_list, idf


def _ensure_idf(bundle: dict[str, Any]) -> None:
    """Lazily populate pre-lowercased strings, token sets, and IDF weights for search."""
    if bundle.get("idf") is not None:
        return
    if bundle.get("kind") == "user":
        texts_lower = [f"{n['session']} {n['learned']}".lower() for n in bundle["notes"]]
    else:
        texts_lower = [
            f"{r['date']} {r['session']} {r['learning']} {r['status']}".lower()
            for r in bundle["rows"]
        ]
    tokens_list, idf = _build_idf_index(texts_lower)
    bundle["texts_lower"] = texts_lower
    bundle["tokens_list"] = tokens_list
    bundle["idf"] = idf


def _keyword_matches_entry(kw: str, entry_tokens: set[str], text_lower: str) -> bool:
    return (
        kw in entry_tokens
        or kw in text_lower
        or ("-" in kw and kw.replace("-", " ") in text_lower)
    )


_INTERNAL_USER_KEYS = frozenset({"_norm", "_expires_dt", "_pinned"})


def _strip_internal_user_keys(entry: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in entry.items() if k not in _INTERNAL_USER_KEYS}


def load_system_learnings(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and deduplicate `[S]` rows from SYSTEM_LEARNINGS.md."""
    return [dict(r) for r in _load_system_bundle(path)["rows"]]


def load_raw_system_learnings(path: Path | None = None) -> list[dict[str, Any]]:
    """Load all raw `[S]` rows from SYSTEM_LEARNINGS.md prior to deduplication."""
    bundle = _load_system_bundle(path)
    return [dict(r) for r in bundle.get("raw_rows", bundle.get("rows", []))]


def load_user_learnings(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and deduplicate `[U]` note entries from USER_PROFILE.yaml."""
    return [_strip_internal_user_keys(entry) for entry in _load_user_bundle(path)["notes"]]


def search_learnings(
    query: str,
    *,
    include_personal: bool = True,
    limit_user: int = 3,
    limit_system: int = 3,
    user_path: Path | None = None,
    system_path: Path | None = None,
    now: datetime | None = None,
    include_expired: bool = False,
) -> dict[str, list[SearchResult]]:
    """Search local learning stores and return scored SearchResult lists by channel."""
    keywords = _tokenize_query(query)
    if not keywords:
        return {"user_profile": [], "system_learnings": []}

    now_utc = _to_utc_now(now)
    min_hits = len(keywords) if len(keywords) <= 2 else max(2, math.ceil(len(keywords) * 0.5))
    results: dict[str, list[SearchResult]] = {
        "user_profile": [],
        "system_learnings": [],
    }

    if include_personal and limit_user > 0:
        u_bundle = _load_user_bundle(user_path)
        _ensure_idf(u_bundle)
        u_notes = u_bundle["notes"]
        u_texts_lower = u_bundle["texts_lower"]
        u_tokens_list = u_bundle["tokens_list"]
        u_idf = u_bundle["idf"]
        total_u_idf = sum(u_idf.get(k, 1.5) for k in keywords) or float(len(keywords))
        n_u = max(1, len(u_notes))

        scored_user: list[SearchResult] = []
        for idx, note in enumerate(u_notes):
            pinned = bool(note.get("_pinned"))
            expires_dt = note.get("_expires_dt")
            if not include_expired and not pinned and is_expired(expires_dt, now_utc):
                continue

            text_lower = u_texts_lower[idx]
            entry_tokens = u_tokens_list[idx]
            matched = [k for k in keywords if _keyword_matches_entry(k, entry_tokens, text_lower)]
            if len(matched) < min_hits:
                continue
            cov = len(matched) / len(keywords)
            idf_cov = sum(u_idf.get(k, 1.5) for k in matched) / total_u_idf
            recency_bonus = 0.02 * ((idx + 1) / n_u)
            conf_bonus = 0.02 if note.get("confidence") == "high" else 0.0
            pin_bonus = 0.04 if pinned else 0.0
            imminent_bonus = 0.03 if (not pinned and is_imminent(expires_dt, now_utc)) else 0.0
            score = round(
                min(1.0, 0.65 * cov + 0.31 * idf_cov + recency_bonus + conf_bonus + pin_bonus + imminent_bonus),
                4,
            )
            scored_user.append(
                SearchResult(
                    id=f"UserLearning:{note['session']}#{idx}",
                    content=f"[{note['session']}] {note['learned']}",
                    source="user_profile",
                    score=score,
                    metadata={
                        "path": ".athena/memory/USER_PROFILE.yaml",
                        "session": note["session"],
                        "confidence": note["confidence"],
                        "claim_kind": "observation",
                        "pinned": pinned,
                        "expires_at": expires_dt.isoformat() if expires_dt else None,
                    },
                )
            )
        scored_user.sort(key=lambda r: r.score, reverse=True)
        results["user_profile"] = scored_user[:limit_user]

    if limit_system > 0:
        s_bundle = _load_system_bundle(system_path)
        _ensure_idf(s_bundle)
        s_rows = s_bundle["rows"]
        s_texts_lower = s_bundle["texts_lower"]
        s_tokens_list = s_bundle["tokens_list"]
        s_idf = s_bundle["idf"]
        total_s_idf = sum(s_idf.get(k, 1.5) for k in keywords) or float(len(keywords))
        n_s = max(1, len(s_rows))

        scored_sys: list[SearchResult] = []
        for idx, row in enumerate(s_rows):
            pinned = bool(row.get("pinned"))
            expires_dt = row.get("expires_at")
            if not include_expired and not pinned and is_expired(expires_dt, now_utc):
                continue

            text_lower = s_texts_lower[idx]
            entry_tokens = s_tokens_list[idx]
            matched = [k for k in keywords if _keyword_matches_entry(k, entry_tokens, text_lower)]
            if len(matched) < min_hits:
                continue
            cov = len(matched) / len(keywords)
            idf_cov = sum(s_idf.get(k, 1.5) for k in matched) / total_s_idf
            recency_bonus = 0.02 * ((idx + 1) / n_s)
            status_bonus = 0.02 if row["integrated"] else 0.0
            pin_bonus = 0.04 if pinned else 0.0
            imminent_bonus = 0.03 if (not pinned and is_imminent(expires_dt, now_utc)) else 0.0
            score = round(
                min(1.0, 0.65 * cov + 0.31 * idf_cov + recency_bonus + status_bonus + pin_bonus + imminent_bonus),
                4,
            )
            scored_sys.append(
                SearchResult(
                    id=f"SystemLearning:{row['session']}:L{row['line_num']}",
                    content=f"[{row['date']} | {row['session']} | {row['status']}] {row['learning']}",
                    source="system_learnings",
                    score=score,
                    metadata={
                        "path": ".athena/memory/SYSTEM_LEARNINGS.md",
                        "session": row["session"],
                        "date": row["date"],
                        "status": row["status"],
                        "pinned": pinned,
                        "expires_at": expires_dt.isoformat() if expires_dt else None,
                    },
                )
            )
        scored_sys.sort(key=lambda r: r.score, reverse=True)
        results["system_learnings"] = scored_sys[:limit_system]

    return results


def get_learnings_stats(
    user_path: Path | None = None,
    system_path: Path | None = None,
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """Return raw, unique, duplicate, pending, integrated, and TTL hygiene learning counts."""
    now_utc = _to_utc_now(now)
    u_bundle = _load_user_bundle(user_path)
    s_bundle = _load_system_bundle(system_path)

    user_notes = u_bundle["notes"]
    system_rows = s_bundle["rows"]

    user_total = u_bundle["raw_count"]
    user_unique = len(user_notes)
    system_total = s_bundle["raw_count"]
    system_unique = len(system_rows)
    system_integrated = sum(1 for r in system_rows if r["integrated"])
    system_pending = system_unique - system_integrated

    user_expired = sum(
        1 for n in user_notes if not n.get("_pinned") and is_expired(n.get("_expires_dt"), now_utc)
    )
    system_expired = sum(
        1 for r in system_rows if not r.get("pinned") and is_expired(r.get("expires_at"), now_utc)
    )
    imminent_expiring = sum(
        1 for n in user_notes if not n.get("_pinned") and is_imminent(n.get("_expires_dt"), now_utc)
    ) + sum(
        1 for r in system_rows if not r.get("pinned") and is_imminent(r.get("expires_at"), now_utc)
    )
    date_bound_missing_ttl = sum(
        1
        for n in user_notes
        if not n.get("_pinned") and n.get("_expires_dt") is None and _DATE_BOUND_HINT_RE.search(n.get("learned", ""))
    ) + sum(
        1
        for r in system_rows
        if not r["integrated"]
        and not r.get("pinned")
        and r.get("expires_at") is None
        and _DATE_BOUND_HINT_RE.search(r.get("learning", ""))
    )

    return {
        "user_total": user_total,
        "user_unique": user_unique,
        "user_dupes": max(0, user_total - user_unique),
        "system_total": system_total,
        "system_unique": system_unique,
        "system_dupes": max(0, system_total - system_unique),
        "system_pending": system_pending,
        "system_integrated": system_integrated,
        "user_expired": user_expired,
        "system_expired": system_expired,
        "imminent_expiring": imminent_expiring,
        "date_bound_missing_ttl": date_bound_missing_ttl,
    }


def _compact_user_file(
    resolved: Path,
    dry_run: bool,
    *,
    prune_expired: bool = False,
    now: datetime | None = None,
) -> dict[str, int]:
    if not resolved.exists() or not _HAS_YAML or _YAML_LOADER is None:
        return {"before": 0, "after": 0, "removed": 0, "expired_removed": 0}

    now_utc = _to_utc_now(now)
    raw_text = resolved.read_text(encoding="utf-8")
    data = yaml.load(raw_text, Loader=_YAML_LOADER)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict YAML root in {resolved}, got {type(data).__name__}")

    header_lines: list[str] = []
    for line in raw_text.splitlines():
        if line.startswith("#") or not line.strip():
            header_lines.append(line)
        else:
            break
    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    raw_notes = data.get("notes") or []
    if not isinstance(raw_notes, list):
        raise ValueError(f"Expected list for 'notes' in {resolved}")

    deduped, raw_count = _dedup_user_notes(raw_notes)
    expired_removed = 0
    kept_entries: list[dict[str, Any]] = []
    for entry in deduped:
        if prune_expired and not entry.get("_pinned") and is_expired(entry.get("_expires_dt"), now_utc):
            expired_removed += 1
            continue
        kept_entries.append(entry)

    clean_notes = [_strip_internal_user_keys(entry) for entry in kept_entries]
    removed = max(0, raw_count - len(clean_notes))

    if not dry_run:
        new_data = dict(data)
        new_data["notes"] = clean_notes
        yaml_str = yaml.dump(new_data, sort_keys=False, allow_unicode=True)
        header_block = "\n".join(header_lines) + "\n\n" if header_lines else ""
        atomic_write_text(resolved, header_block + yaml_str, mode=0o600)

    return {
        "before": raw_count,
        "after": len(clean_notes),
        "removed": removed,
        "expired_removed": expired_removed,
    }


def _compact_system_file(
    resolved: Path,
    dry_run: bool,
    *,
    prune_expired: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    if not resolved.exists():
        return {"before": 0, "after": 0, "removed": 0, "expired_removed": 0, "repaired_footer": False}

    now_utc = _to_utc_now(now)
    lines = resolved.read_text(encoding="utf-8").splitlines()
    raw_rows: list[dict[str, Any]] = []
    header_lines: list[str] = []
    footer_lines: list[str] = []
    seen_first_row = False

    for line_num, line in enumerate(lines, 1):
        parsed = _parse_system_row(line, line_num)
        if parsed is not None:
            seen_first_row = True
            raw_rows.append(parsed)
        elif not seen_first_row:
            header_lines.append(line)
        else:
            footer_lines.append(line)

    deduped = _dedup_system_rows(raw_rows)
    expired_removed = 0
    kept_rows: list[dict[str, Any]] = []
    for row in deduped:
        if prune_expired and not row.get("pinned") and is_expired(row.get("expires_at"), now_utc):
            expired_removed += 1
            continue
        kept_rows.append(row)

    removed = max(0, len(raw_rows) - len(kept_rows))

    while footer_lines and not footer_lines[0].strip():
        footer_lines.pop(0)
    while footer_lines and not footer_lines[-1].strip():
        footer_lines.pop()

    # Check whether any non-empty footer content previously sat before the last row
    last_row_line = raw_rows[-1]["line_num"] if raw_rows else 0
    repaired_footer = any(
        (not _ROW_DATE_RE.match(line.strip()))
        and line.strip()
        and (i + 1) < last_row_line
        for i, line in enumerate(lines)
        if seen_first_row and (i + 1) > (raw_rows[0]["line_num"] if raw_rows else 0)
    )

    if not dry_run and raw_rows:
        out_lines = list(header_lines)
        for r in kept_rows:
            out_lines.append(
                f"| {r['date']} | {r['session']} | {r['learning']} | {r['status']} |"
            )
        if footer_lines:
            out_lines.append("")
            out_lines.extend(footer_lines)
        atomic_write_text(resolved, "\n".join(out_lines) + "\n", mode=0o600)

    return {
        "before": len(raw_rows),
        "after": len(kept_rows),
        "removed": removed,
        "expired_removed": expired_removed,
        "repaired_footer": repaired_footer,
    }


def compact_learnings_stores(
    user_path: Path | None = None,
    system_path: Path | None = None,
    dry_run: bool = False,
    prune_expired: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Deduplicate both local learning stores, optionally prune expired entries, and repair layout."""
    resolved_user = _resolve_store_path("user", user_path)
    resolved_system = _resolve_store_path("system", system_path)

    user_res = _compact_user_file(resolved_user, dry_run=dry_run, prune_expired=prune_expired, now=now)
    system_res = _compact_system_file(resolved_system, dry_run=dry_run, prune_expired=prune_expired, now=now)

    if not dry_run:
        _STORE_CACHE.clear()

    return {
        "dry_run": dry_run,
        "prune_expired": prune_expired,
        "user": user_res,
        "system": system_res,
    }
