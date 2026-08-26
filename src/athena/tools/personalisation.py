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
        "rate_floor": "Configured Minimum Rate Floor (per CANONICAL.md)",
        "financial_constraints": "Capital preservation & active float discipline, 0 unhedged risk",
        "key_man_risk": "Standard — Single operator dependency",
        "strategic_priorities": [],
        "behavioral_anchors": [
            "Meta-Awareness & Perspective Taking",
            "Law of Ruin & Ergodic Capital Sizing (Law #1)",
            "Output-over-Scaffolding Execution Gate",
        ],
    }

    # Extract metrics from CANONICAL if available
    if CANONICAL_PATH.exists():
        try:
            content = CANONICAL_PATH.read_text(encoding="utf-8")
            for line in content.splitlines():
                line_str = line.strip()
                if "rate" in line_str.lower() and ("$" in line_str or "s$" in line_str.lower()):
                    if "floor" in line_str.lower() or "hourly" in line_str.lower() or "minimum" in line_str.lower():
                        snapshot["rate_floor"] = line_str.lstrip("- *#|").strip()
                elif "runway" in line_str.lower() or "cash buffer" in line_str.lower():
                    snapshot["financial_constraints"] = line_str.lstrip("- *#|").strip()
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
                snapshot["active_focus"] = focus_match.group(1).strip()
        except Exception:
            pass

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
        f"- Rate Floor & Pricing: {user_state.get('rate_floor', 'Configured Rate Floor')}",
        f"- Financial & Capital Risk: {user_state.get('financial_constraints', 'Active float discipline')}",
        f"- Key-Man Risk: {user_state.get('key_man_risk', 'Standard')}",
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
