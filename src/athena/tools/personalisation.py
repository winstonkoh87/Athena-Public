"""
athena.tools.personalisation
============================

Active Personalisation & Context Synthesis Layer.
Converts raw retrieval results into an explicit synthesis framing that instructs
downstream LLM reasoning to ground decisions in user-specific constraints,
rate floors, financial runway, risk models, and behavioral history.
"""

from __future__ import annotations

import re
from typing import Any

from athena.core.config import CANONICAL_PATH, PROJECT_ROOT
from athena.core.models import SearchResult


def build_user_state_snapshot() -> dict[str, Any]:
    """
    Extract core Tier 1 user metrics and active constraints from CANONICAL.md
    and active memory files into a compact structured dictionary.
    """
    snapshot: dict[str, Any] = {
        "rate_floor": "$100/hr (Calibrated minimum floor)",
        "financial_constraints": "Cash buffer & active float discipline, 0 unhedged risk",
        "key_man_risk": "CRITICAL — Single operator dependency",
        "strategic_priorities": [],
        "behavioral_anchors": [
            "Pryce Test / Meta-Awareness (PAT-574)",
            "Law of Ruin & Half-Kelly sizing (Law #1)",
            "Anti-Procrastination by tool building (TD-045 / DIAG-001)",
        ],
    }

    # Extract metrics from CANONICAL if available — structured table parser
    # GTO FIX (2026-08-27): Old parser used loose substring matching
    # ("rate" + "$" + "floor") which matched false positives (e.g. trading
    # paragraphs containing "noise floor" and "Win Rate"). New parser targets
    # the exact markdown table row format and validates the currency shape.
    if CANONICAL_PATH.exists():
        try:
            content = CANONICAL_PATH.read_text(encoding="utf-8")

            # 1. Rate floor: target the exact table row format
            rate_match = re.search(
                r"\|\s*\*\*Consulting Rate\*\*\s*\|\s*\*\*([^|]+?)\*\*\s*\|",
                content,
            )
            if rate_match:
                raw_rate = rate_match.group(1).strip()
                # Shape validation: must look like a currency amount (e.g. $150/hr, S$150)
                if re.match(r"^S?\$\d+(?:/hr)?$", raw_rate):
                    snapshot["rate_floor"] = raw_rate
                    snapshot["_provenance_rate_floor"] = "CANONICAL.md::Consulting Rate row"
                else:
                    # Shape mismatch — keep default, flag it
                    snapshot["_provenance_rate_floor"] = (
                        f"[STATE_FIELD_FALLBACK] raw='{raw_rate}' failed shape check"
                    )

            # 2. Financial constraints: target Runway or Key-Man rows
            for line in content.splitlines():
                line_str = line.strip()
                if line_str.startswith("|") and (
                    "runway" in line_str.lower() or "cash buffer" in line_str.lower()
                ):
                    # Extract value cell from table row
                    cells = [c.strip() for c in line_str.split("|") if c.strip()]
                    if len(cells) >= 2:
                        snapshot["financial_constraints"] = cells[1].strip("* ")
                        snapshot["_provenance_financial"] = "CANONICAL.md::table row"
                        break
        except Exception:
            pass


    # Extract active tasks from activeContext if available
    active_ctx_path = PROJECT_ROOT / ".context" / "memory_bank" / "activeContext.md"
    if active_ctx_path.exists():
        try:
            ctx_text = active_ctx_path.read_text(encoding="utf-8")
            pending_match = re.search(r"@pending:\s*([^!\]\n]+)", ctx_text)
            if pending_match:
                snapshot["active_pending"] = pending_match.group(1).strip()
            focus_match = re.search(r"@focus:\s*([^!\]\n]+)", ctx_text)
            if focus_match:
                focus_value = focus_match.group(1).strip()
                snapshot["active_focus"] = focus_value
                # FIX-10: Populate strategic_priorities from @focus (was declared-but-never-filled)
                snapshot["strategic_priorities"] = [
                    p.strip() for p in focus_value.split(",") if p.strip()
                ]
        except Exception:
            pass

    # FIX-10: Freshness stamp — lets downstream consumers know how stale the frame is
    import datetime

    snapshot["state_as_of"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return snapshot


def build_personalisation_prompt(
    query: str,
    results: list[SearchResult],
    user_state: dict[str, Any] | None = None,
    intent: str = "PERSONALISED_DECISION",
) -> str:
    """
    Wraps retrieved search context in an explicit, active synthesis frame.

    Transforms passive chunk dumping into active decision constraints.
    """
    if user_state is None:
        user_state = build_user_state_snapshot()

    lines = [
        f'<personalisation_context intent="{intent}">',
        "=== OPERATOR STATE & CONSTRAINTS ===",
        f"- Rate Floor & Pricing: {user_state.get('rate_floor', '$100/hr minimum')}",
        f"- Financial & Capital Risk: {user_state.get('financial_constraints', 'Active float discipline')}",
        f"- Key-Man Risk: {user_state.get('key_man_risk', 'CRITICAL')}",
    ]

    if "active_focus" in user_state:
        lines.append(f"- Active Focus: {user_state['active_focus']}")
    if "active_pending" in user_state:
        lines.append(f"- Active Pending Queue: {user_state['active_pending']}")

    anchors = user_state.get("behavioral_anchors", [])
    if anchors:
        lines.append(f"- Core Behavioral Anchors: {'; '.join(anchors)}")

    lines.append("\n=== RELEVANT RETRIEVED CONTEXT ===")
    for i, res in enumerate(results, 1):
        source_label = res.source.upper() if res.source else "UNKNOWN"
        lines.append(f"{i}. [{source_label}] {res.id}")
        if res.metadata and res.metadata.get("path"):
            lines.append(f"   Path: {res.metadata['path']}")
        content_preview = res.content.strip() if res.content else ""
        if len(content_preview) > 300:
            content_preview = content_preview[:300] + "..."
        lines.append(f"   Content: {content_preview}")

    lines.extend([
        "\n=== SYNTHESIS INSTRUCTION ===",
        "Ground your advice strictly in the operator's verified constraints, rate floors, and decision history.",
        "Do NOT provide generic or one-size-fits-all advice. Explicitly evaluate the query against the operator's asymmetric payoffs, capital limits, and behavioral patterns above.",
        "</personalisation_context>",
    ])

    return "\n".join(lines)
