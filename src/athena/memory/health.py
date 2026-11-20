"""
athena.memory.health
====================

Zero-token memory health evaluator and deterministic CI fixture suite.

Measures:
1. Startup footprint against byte/line caps (userContext.md, activeContext.md surgical slice, CANONICAL.md)
2. Cross-layer 4-gram shingle overlap across durable memory layers
3. TTL hygiene (expired entries, imminent <=72h expiries, date-bound rules missing expires_at)
4. Borges's Map Trap ratio (curated summary/index bytes vs raw corpus bytes)
5. Session taint status and 4 synthetic scoping/TTL/quarantine fixtures
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from athena.core import config
from athena.core.taint import get_taint_status
from athena.memory.budgets import assemble_scoped_context
from athena.memory.learnings import get_learnings_stats

USER_CONTEXT_MAX_BYTES = 12_288
ACTIVE_SURGICAL_MAX_BYTES = 8_192
CANONICAL_T1_MAX_BYTES = 65_536
OVERLAP_WARN_PCT = 25.0
BORGES_WARN_RATIO = 0.35

_WORD_RE = re.compile(r"[a-z0-9]+")


def compute_shingle_overlap(texts: dict[str, str], n: int = 4) -> dict[str, Any]:
    """Compute pairwise and overall duplicated n-gram shingle share across memory layers."""
    if n < 1:
        raise ValueError("Shingle size n must be >= 1")

    shingles_by_layer: dict[str, set[tuple[str, ...]]] = {}
    for name, text in texts.items():
        words = _WORD_RE.findall((text or "").lower())
        if len(words) < n:
            continue
        layer_set = {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}
        if layer_set:
            shingles_by_layer[name] = layer_set

    if len(shingles_by_layer) < 2:
        return {
            "shingle_n": n,
            "layers_evaluated": sorted(shingles_by_layer.keys()),
            "overall_overlap_pct": 0.0,
            "pairs": [],
        }

    names = sorted(shingles_by_layer.keys())
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(names):
        set_a = shingles_by_layer[a]
        for b in names[i + 1 :]:
            set_b = shingles_by_layer[b]
            denom = min(len(set_a), len(set_b))
            shared = len(set_a & set_b)
            pct = round((shared / denom) * 100.0, 2) if denom > 0 else 0.0
            pairs.append(
                {
                    "layer_a": a,
                    "layer_b": b,
                    "shared_shingles": shared,
                    "overlap_pct": pct,
                }
            )

    pairs.sort(key=lambda p: p["overlap_pct"], reverse=True)
    total_shingles = sum(len(s) for s in shingles_by_layer.values())
    unique_shingles = len(set().union(*shingles_by_layer.values()))
    dup_shingles = max(0, total_shingles - unique_shingles)
    overall_pct = round((dup_shingles / total_shingles) * 100.0, 2) if total_shingles > 0 else 0.0

    return {
        "shingle_n": n,
        "layers_evaluated": names,
        "overall_overlap_pct": overall_pct,
        "pairs": pairs,
    }


def _extract_active_surgical_slice(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    header_end = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "---":
            header_end = idx
            break
    header_slice = "\n".join(lines[: min(header_end, 40)])

    last_cp_idx = text.rfind("[[ S")
    if last_cp_idx == -1:
        tail_slice = "\n".join(lines[-40:]) if len(lines) > 40 else ""
        return (header_slice + "\n" + tail_slice).strip()

    section_idx = text.rfind("\n## Session ", 0, last_cp_idx)
    start_idx = section_idx + 1 if section_idx != -1 else last_cp_idx
    latest_slice = text[start_idx:]
    if start_idx <= len(header_slice):
        return text
    return (header_slice + "\n" + latest_slice).strip()


def _safe_read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _safe_bytes(path: Path) -> int:
    if not path.is_file():
        return 0
    return path.stat().st_size


def evaluate_memory_health(
    project_root: Path | None = None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Evaluate zero-token memory health metrics across startup footprint, overlap, TTL, and Borges ratio."""
    root = Path(project_root) if project_root is not None else config.PROJECT_ROOT

    user_ctx_path = root / ".context" / "memory_bank" / "userContext.md"
    active_ctx_path = root / ".context" / "memory_bank" / "activeContext.md"
    canonical_path = root / ".context" / "CANONICAL.md"
    user_profile_path = root / ".athena" / "memory" / "USER_PROFILE.yaml"
    system_learnings_path = root / ".athena" / "memory" / "SYSTEM_LEARNINGS.md"

    user_ctx_text = _safe_read(user_ctx_path)
    active_ctx_text = _safe_read(active_ctx_path)
    canonical_text = _safe_read(canonical_path)
    user_profile_text = _safe_read(user_profile_path)
    system_learnings_text = _safe_read(system_learnings_path)

    active_surgical_text = _extract_active_surgical_slice(active_ctx_text)

    user_ctx_bytes = len(user_ctx_text.encode("utf-8"))
    active_full_bytes = len(active_ctx_text.encode("utf-8"))
    active_surgical_bytes = len(active_surgical_text.encode("utf-8"))
    canonical_bytes = len(canonical_text.encode("utf-8"))

    startup_footprint = {
        "user_context_bytes": user_ctx_bytes,
        "user_context_lines": len(user_ctx_text.splitlines()),
        "user_context_max_bytes": USER_CONTEXT_MAX_BYTES,
        "active_context_bytes": active_full_bytes,
        "active_surgical_bytes": active_surgical_bytes,
        "active_surgical_max_bytes": ACTIVE_SURGICAL_MAX_BYTES,
        "canonical_bytes": canonical_bytes,
        "canonical_max_bytes": CANONICAL_T1_MAX_BYTES,
        "total_surgical_bytes": user_ctx_bytes + active_surgical_bytes,
    }

    overlap = compute_shingle_overlap(
        {
            "userContext.md": user_ctx_text,
            "activeContext.md": active_ctx_text,
            "CANONICAL.md": canonical_text,
            "USER_PROFILE.yaml": user_profile_text,
            "SYSTEM_LEARNINGS.md": system_learnings_text,
        },
        n=4,
    )

    ttl_hygiene = get_learnings_stats(
        user_path=user_profile_path,
        system_path=system_learnings_path,
        now=now,
    )

    curated_paths = (
        canonical_path,
        root / ".context" / "PROTOCOL_SUMMARIES.md",
        root / ".context" / "CASE_STUDY_INDEX.md",
        active_ctx_path,
    )
    curated_bytes = sum(_safe_bytes(p) for p in curated_paths)

    raw_bytes = 0
    for raw_dir, pattern in (
        (root / ".context" / "memories" / "session_logs", "*.md"),
        (root / ".context" / "memories" / "case_studies", "*.md"),
        (root / ".agent" / "skills" / "protocols", "**/*.md"),
    ):
        if raw_dir.is_dir():
            for md_file in raw_dir.glob(pattern):
                if md_file.is_file():
                    raw_bytes += md_file.stat().st_size

    borges_ratio = round(curated_bytes / raw_bytes, 4) if raw_bytes > 0 else None
    borges_map = {
        "curated_bytes": curated_bytes,
        "raw_corpus_bytes": raw_bytes,
        "ratio": borges_ratio,
        "warn_threshold": BORGES_WARN_RATIO,
    }

    taint_status = get_taint_status(project_root=root)

    warnings: list[str] = []
    if user_ctx_bytes > USER_CONTEXT_MAX_BYTES:
        warnings.append(
            f"userContext.md exceeds startup budget ({user_ctx_bytes} > {USER_CONTEXT_MAX_BYTES} B)"
        )
    if active_surgical_bytes > ACTIVE_SURGICAL_MAX_BYTES:
        warnings.append(
            f"activeContext.md surgical slice exceeds budget ({active_surgical_bytes} > {ACTIVE_SURGICAL_MAX_BYTES} B)"
        )
    if canonical_bytes > CANONICAL_T1_MAX_BYTES:
        warnings.append(
            f"CANONICAL.md Tier-1 exceeds budget ({canonical_bytes} > {CANONICAL_T1_MAX_BYTES} B)"
        )
    if overlap["overall_overlap_pct"] > OVERLAP_WARN_PCT:
        warnings.append(
            f"Cross-layer shingle overlap {overlap['overall_overlap_pct']}% > {OVERLAP_WARN_PCT}%"
        )
    expired_total = ttl_hygiene["user_expired"] + ttl_hygiene["system_expired"]
    if expired_total > 0:
        warnings.append(f"{expired_total} expired non-pinned learnings pending pruning")
    if ttl_hygiene["date_bound_missing_ttl"] > 0:
        warnings.append(
            f"{ttl_hygiene['date_bound_missing_ttl']} date-bound learnings lack explicit expires_at TTL"
        )
    if borges_ratio is not None and borges_ratio > BORGES_WARN_RATIO:
        warnings.append(
            f"Borges Map Trap ratio {borges_ratio:.2f} > {BORGES_WARN_RATIO:.2f} (curated/raw)"
        )
    if taint_status["tainted"]:
        warnings.append("Session is currently under monotonic taint quarantine")

    return {
        "status": "warn" if warnings else "ok",
        "warnings": warnings,
        "startup_footprint": startup_footprint,
        "cross_layer_overlap": overlap,
        "ttl_hygiene": ttl_hygiene,
        "borges_map": borges_map,
        "taint": taint_status,
    }


def run_memory_fixtures() -> dict[str, Any]:
    """Run 4 deterministic synthetic CI fixtures proving scope, TTL, budget, and taint invariants."""
    fixed_now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    fixtures: list[dict[str, Any]] = []

    # Fixture 1: Scope isolation + 0% personal leakage for scoped_worker
    f1_facts: list[dict[str, Any]] = [
        {"text": "Dentist appointment tomorrow 9am", "scope": "personal", "personal": True, "topic": "errands"},
        {"text": "Always run pytest before pushing", "scope": "global", "pinned": True, "topic": "testing"},
        {"text": "Build repo-alpha with make test", "scope": "repo:alpha", "topic": "build"},
        {"text": "Deploy repo-beta via docker", "scope": "repo:beta", "topic": "build"},
    ]
    res1 = assemble_scoped_context(
        "scoped_worker",
        facts=f1_facts,
        scope="repo:alpha",
        personal_summary="Private operator schedule and preferences",
        active_context="Personal weekend errands",
        repo_playbook="Run pytest -q before commit.",
        now=fixed_now,
    )
    texts1 = [f["text"] for f in res1["selected_facts"]]
    pass1 = (
        not res1["personal_included"]
        and "personal_summary" not in res1["sections"]
        and "active_context" not in res1["sections"]
        and "Build repo-alpha with make test" in texts1
        and "Always run pytest before pushing" in texts1
        and all("Dentist" not in t and "repo-beta" not in t for t in texts1)
        and res1["total_bytes"] <= res1["max_bytes"]
    )
    fixtures.append({"name": "scope_isolation_zero_personal_leakage", "passed": pass1})

    # Fixture 2: Zero-token TTL expiry + Negative Guardrail Paradox pinned immunity
    f2_facts: list[dict[str, Any]] = [
        {
            "text": "Temporary sprint cutoff expired yesterday",
            "scope": "global",
            "expires_at": (fixed_now - timedelta(hours=12)).isoformat(),
            "topic": "ops",
        },
        {
            "text": "Never send external messages without showing exact draft [pinned]",
            "scope": "global",
            "pinned": True,
            "expires_at": (fixed_now - timedelta(days=30)).isoformat(),
            "topic": "guardrails",
        },
        {
            "text": "Submit compliance form within 24h",
            "scope": "global",
            "expires_at": (fixed_now + timedelta(hours=24)).isoformat(),
            "topic": "ops",
        },
    ]
    res2 = assemble_scoped_context("front_desk", facts=f2_facts, now=fixed_now)
    texts2 = [f["text"] for f in res2["selected_facts"]]
    pass2 = (
        res2["dropped_expired"] == 1
        and len(texts2) == 2
        and texts2[0].startswith("Never send external messages")
        and any("Submit compliance form" in t for t in texts2)
        and all("Temporary sprint cutoff" not in t for t in texts2)
    )
    fixtures.append({"name": "zero_token_ttl_and_negative_guardrail_paradox", "passed": pass2})

    # Fixture 3: Front Desk per-topic cap prevents one noisy topic starving others
    noisy_errands: list[dict[str, Any]] = [
        {"text": f"Errand reminder number {i}", "scope": "personal", "topic": "errands"}
        for i in range(10)
    ]
    core_arch: list[dict[str, Any]] = [
        {"text": "Use atomic writes with 0600 mode", "scope": "global", "pinned": True, "topic": "architecture"},
        {"text": "Keep Law 1 ruin gates fail-closed", "scope": "global", "pinned": True, "topic": "safety"},
    ]
    res3 = assemble_scoped_context("front_desk", facts=noisy_errands + core_arch, now=fixed_now)
    errand_selected = [f for f in res3["selected_facts"] if f["topic"] == "errands"]
    arch_selected = [f for f in res3["selected_facts"] if f["topic"] == "architecture"]
    safety_selected = [f for f in res3["selected_facts"] if f["topic"] == "safety"]
    pass3 = (
        len(errand_selected) == 3
        and res3["dropped_topic_cap"] == 7
        and len(arch_selected) == 1
        and len(safety_selected) == 1
    )
    fixtures.append({"name": "front_desk_topic_cap_no_starvation", "passed": pass3})

    # Fixture 4: Monotonic taint forces zero-byte quarantine
    res4 = assemble_scoped_context(
        "front_desk",
        facts=f1_facts,
        personal_summary="Sensitive notes",
        active_context="Sensitive active state",
        repo_playbook="Build steps",
        tainted=True,
        now=fixed_now,
    )
    pass4 = (
        res4["tainted"] is True
        and res4["total_bytes"] == 0
        and res4["selected_facts"] == []
        and res4["sections"] == {}
        and res4["personal_included"] is False
    )
    fixtures.append({"name": "monotonic_taint_zero_byte_quarantine", "passed": pass4})

    passed = sum(1 for f in fixtures if f["passed"])
    return {
        "passed": passed,
        "total": len(fixtures),
        "all_passed": passed == len(fixtures),
        "fixtures": fixtures,
    }
