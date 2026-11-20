"""
athena.memory.budgets
=====================

Role-scoped startup context assembly with hard UTF-8 byte caps, deterministic
Negative-Guardrail-Paradox immunity (pinned invariants + scope match + imminent
expiry sort first with zero hit-counters), topic starvation caps, and taint
quarantine enforcement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from athena.memory.learnings import (
    _INLINE_PINNED_RE,
    _to_utc_now,
    is_expired,
    is_imminent,
    parse_expires_at,
)

ROLE_BUDGETS: dict[str, dict[str, Any]] = {
    "front_desk": {
        "max_bytes": 12_288,
        "include_personal": True,
        "include_active_context": True,
        "include_repo_playbook": False,
        "max_playbook_bytes": 0,
        "max_facts_per_topic": 3,
    },
    "scoped_worker": {
        "max_bytes": 4_915,
        "include_personal": False,
        "include_active_context": False,
        "include_repo_playbook": True,
        "max_playbook_bytes": 1_228,
        "max_facts_per_topic": 5,
    },
    "red_team_auditor": {
        "max_bytes": 4_915,
        "include_personal": False,
        "include_active_context": False,
        "include_repo_playbook": False,
        "max_playbook_bytes": 0,
        "max_facts_per_topic": 3,
    },
    "tainted": {
        "max_bytes": 0,
        "include_personal": False,
        "include_active_context": False,
        "include_repo_playbook": False,
        "max_playbook_bytes": 0,
        "max_facts_per_topic": 0,
    },
}


def _utf8_bytes(text: str) -> int:
    return len(text.encode("utf-8"))


def _truncate_utf8(text: str, max_bytes: int) -> str:
    if max_bytes <= 0 or not text:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore").rstrip()


def assemble_scoped_context(
    role: str,
    *,
    facts: list[dict[str, Any]] | None = None,
    scope: str | None = None,
    personal_summary: str = "",
    active_context: str = "",
    repo_playbook: str = "",
    tainted: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Assemble role-scoped context within deterministic byte and topic budgets."""
    if role not in ROLE_BUDGETS:
        raise ValueError(f"Unknown context role: {role!r}. Expected one of {sorted(ROLE_BUDGETS)}")

    if tainted or role == "tainted":
        return {
            "role": "tainted",
            "tainted": True,
            "total_bytes": 0,
            "max_bytes": 0,
            "sections": {},
            "selected_facts": [],
            "dropped_expired": 0,
            "dropped_scope": 0,
            "dropped_topic_cap": 0,
            "dropped_budget": 0,
            "personal_included": False,
        }

    cfg = ROLE_BUDGETS[role]
    max_bytes = int(cfg["max_bytes"])
    now_utc = _to_utc_now(now)

    dropped_expired = 0
    dropped_scope = 0
    dropped_topic_cap = 0
    dropped_budget = 0

    candidates: list[dict[str, Any]] = []
    for idx, raw in enumerate(facts or []):
        text = str(raw.get("text") or raw.get("learned") or raw.get("content") or "").strip()
        if not text:
            continue

        pinned = bool(raw.get("pinned")) or bool(_INLINE_PINNED_RE.search(text))
        expires_dt = parse_expires_at(raw.get("expires_at"), text)
        if not pinned and is_expired(expires_dt, now_utc):
            dropped_expired += 1
            continue

        f_scope = raw.get("scope")
        is_personal = (f_scope == "personal") or bool(raw.get("personal"))
        if not cfg["include_personal"] and is_personal:
            dropped_scope += 1
            continue

        if role == "scoped_worker" and scope is not None:
            if f_scope != scope and not (f_scope in ("global", None) and pinned):
                dropped_scope += 1
                continue
        elif role == "red_team_auditor" and scope is not None and f_scope not in (None, "global", scope):
            dropped_scope += 1
            continue

        exact_scope = bool(scope is not None and f_scope == scope)
        imminent = bool(not pinned and is_imminent(expires_dt, now_utc))
        topic = str(raw.get("topic") or "general").strip() or "general"
        candidates.append(
            {
                **raw,
                "text": text,
                "scope": f_scope,
                "topic": topic,
                "pinned": pinned,
                "personal": is_personal,
                "imminent": imminent,
                "exact_scope": exact_scope,
                "idx": idx,
            }
        )

    # Deterministic priority (no usage hit-counters — avoids Negative Guardrail Paradox)
    candidates.sort(
        key=lambda c: (not c["pinned"], not c["exact_scope"], not c["imminent"], c["idx"])
    )

    topic_cap = int(cfg["max_facts_per_topic"])
    topic_counts: dict[str, int] = {}
    eligible_facts: list[dict[str, Any]] = []
    for cand in candidates:
        t = cand["topic"]
        if topic_counts.get(t, 0) >= topic_cap:
            dropped_topic_cap += 1
            continue
        topic_counts[t] = topic_counts.get(t, 0) + 1
        eligible_facts.append(cand)

    sections: dict[str, str] = {}
    used_bytes = 0

    if cfg["include_repo_playbook"] and repo_playbook.strip():
        pb_budget = min(int(cfg["max_playbook_bytes"]), max_bytes - used_bytes)
        pb_slice = _truncate_utf8(repo_playbook.strip(), pb_budget)
        if pb_slice:
            sections["repo_playbook"] = pb_slice
            used_bytes += _utf8_bytes(pb_slice)

    if cfg["include_personal"] and personal_summary.strip():
        ps_slice = _truncate_utf8(personal_summary.strip(), max_bytes - used_bytes)
        if ps_slice:
            sections["personal_summary"] = ps_slice
            used_bytes += _utf8_bytes(ps_slice)

    if cfg["include_active_context"] and active_context.strip():
        ac_slice = _truncate_utf8(active_context.strip(), max_bytes - used_bytes)
        if ac_slice:
            sections["active_context"] = ac_slice
            used_bytes += _utf8_bytes(ac_slice)

    selected_facts: list[dict[str, Any]] = []
    for cand in eligible_facts:
        line_bytes = _utf8_bytes(cand["text"]) + 1  # account for newline separator
        if used_bytes + line_bytes > max_bytes:
            dropped_budget += 1
            continue
        used_bytes += line_bytes
        selected_facts.append(
            {
                "text": cand["text"],
                "scope": cand["scope"],
                "topic": cand["topic"],
                "pinned": cand["pinned"],
                "personal": cand["personal"],
                "imminent": cand["imminent"],
            }
        )

    if selected_facts:
        sections["facts"] = "\n".join(f["text"] for f in selected_facts)

    personal_included = bool(sections.get("personal_summary")) or any(
        f["personal"] for f in selected_facts
    )

    return {
        "role": role,
        "tainted": False,
        "total_bytes": used_bytes,
        "max_bytes": max_bytes,
        "sections": sections,
        "selected_facts": selected_facts,
        "dropped_expired": dropped_expired,
        "dropped_scope": dropped_scope,
        "dropped_topic_cap": dropped_topic_cap,
        "dropped_budget": dropped_budget,
        "personal_included": personal_included,
    }
