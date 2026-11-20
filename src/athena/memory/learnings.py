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

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from athena.core.models import SearchResult

try:
    import yaml

    _YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    _HAS_YAML = True
except ImportError:
    yaml = None  # type: ignore[assignment]
    _YAML_LOADER = None
    _HAS_YAML = False

_ROW_DATE_RE = re.compile(r"^\|\s*(20\d{2}-\d{2}-\d{2})\s*\|")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
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
        if row["integrated"] and not existing["integrated"]:
            deduped[existing_idx] = row
        elif row["integrated"] == existing["integrated"]:
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
    if kw in entry_tokens or kw in text_lower:
        return True
    if "-" in kw and kw.replace("-", " ") in text_lower:
        return True
    return False


def load_system_learnings(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and deduplicate `[S]` rows from SYSTEM_LEARNINGS.md."""
    return [dict(r) for r in _load_system_bundle(path)["rows"]]


def load_user_learnings(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and deduplicate `[U]` note entries from USER_PROFILE.yaml."""
    out: list[dict[str, Any]] = []
    for entry in _load_user_bundle(path)["notes"]:
        cleaned = {k: v for k, v in entry.items() if k != "_norm"}
        out.append(cleaned)
    return out


def search_learnings(
    query: str,
    *,
    include_personal: bool = True,
    limit_user: int = 3,
    limit_system: int = 3,
    user_path: Path | None = None,
    system_path: Path | None = None,
) -> dict[str, list[SearchResult]]:
    """Search local learning stores and return scored SearchResult lists by channel."""
    keywords = _tokenize_query(query)
    if not keywords:
        return {"user_profile": [], "system_learnings": []}

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
            text_lower = u_texts_lower[idx]
            entry_tokens = u_tokens_list[idx]
            matched = [k for k in keywords if _keyword_matches_entry(k, entry_tokens, text_lower)]
            if len(matched) < min_hits:
                continue
            cov = len(matched) / len(keywords)
            idf_cov = sum(u_idf.get(k, 1.5) for k in matched) / total_u_idf
            recency_bonus = 0.02 * ((idx + 1) / n_u)
            conf_bonus = 0.02 if note.get("confidence") == "high" else 0.0
            score = round(min(1.0, 0.65 * cov + 0.31 * idf_cov + recency_bonus + conf_bonus), 4)
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
            text_lower = s_texts_lower[idx]
            entry_tokens = s_tokens_list[idx]
            matched = [k for k in keywords if _keyword_matches_entry(k, entry_tokens, text_lower)]
            if len(matched) < min_hits:
                continue
            cov = len(matched) / len(keywords)
            idf_cov = sum(s_idf.get(k, 1.5) for k in matched) / total_s_idf
            recency_bonus = 0.02 * ((idx + 1) / n_s)
            status_bonus = 0.02 if row["integrated"] else 0.0
            score = round(min(1.0, 0.65 * cov + 0.31 * idf_cov + recency_bonus + status_bonus), 4)
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
                    },
                )
            )
        scored_sys.sort(key=lambda r: r.score, reverse=True)
        results["system_learnings"] = scored_sys[:limit_system]

    return results


def get_learnings_stats(
    user_path: Path | None = None,
    system_path: Path | None = None,
) -> dict[str, int]:
    """Return raw, unique, duplicate, pending, and integrated learning counts."""
    u_bundle = _load_user_bundle(user_path)
    s_bundle = _load_system_bundle(system_path)

    user_total = u_bundle["raw_count"]
    user_unique = len(u_bundle["notes"])
    system_total = s_bundle["raw_count"]
    system_unique = len(s_bundle["rows"])
    system_integrated = sum(1 for r in s_bundle["rows"] if r["integrated"])
    system_pending = system_unique - system_integrated

    return {
        "user_total": user_total,
        "user_unique": user_unique,
        "user_dupes": max(0, user_total - user_unique),
        "system_total": system_total,
        "system_unique": system_unique,
        "system_dupes": max(0, system_total - system_unique),
        "system_pending": system_pending,
        "system_integrated": system_integrated,
    }


def _compact_user_file(resolved: Path, dry_run: bool) -> dict[str, int]:
    if not resolved.exists() or not _HAS_YAML or _YAML_LOADER is None:
        return {"before": 0, "after": 0, "removed": 0}

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
    clean_notes = [{k: v for k, v in entry.items() if k != "_norm"} for entry in deduped]
    removed = max(0, raw_count - len(clean_notes))

    if not dry_run:
        new_data = dict(data)
        new_data["notes"] = clean_notes
        yaml_str = yaml.dump(new_data, sort_keys=False, allow_unicode=True)
        header_block = "\n".join(header_lines) + "\n\n" if header_lines else ""
        resolved.write_text(header_block + yaml_str, encoding="utf-8")

    return {"before": raw_count, "after": len(clean_notes), "removed": removed}


def _compact_system_file(resolved: Path, dry_run: bool) -> dict[str, Any]:
    if not resolved.exists():
        return {"before": 0, "after": 0, "removed": 0, "repaired_footer": False}

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
    removed = max(0, len(raw_rows) - len(deduped))

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
        for r in deduped:
            out_lines.append(
                f"| {r['date']} | {r['session']} | {r['learning']} | {r['status']} |"
            )
        if footer_lines:
            out_lines.append("")
            out_lines.extend(footer_lines)
        resolved.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    return {
        "before": len(raw_rows),
        "after": len(deduped),
        "removed": removed,
        "repaired_footer": repaired_footer,
    }


def compact_learnings_stores(
    user_path: Path | None = None,
    system_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Deduplicate both local learning stores and repair SYSTEM_LEARNINGS.md table layout."""
    resolved_user = _resolve_store_path("user", user_path)
    resolved_system = _resolve_store_path("system", system_path)

    user_res = _compact_user_file(resolved_user, dry_run=dry_run)
    system_res = _compact_system_file(resolved_system, dry_run=dry_run)

    if not dry_run:
        _STORE_CACHE.clear()

    return {
        "dry_run": dry_run,
        "user": user_res,
        "system": system_res,
    }
