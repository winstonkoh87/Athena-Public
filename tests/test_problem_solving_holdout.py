"""Deterministic CI regression test for the 30-case unseen problem-solving holdout set."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from athena.core.permissions import get_permissions
from athena.mcp_server import context_gate, reset_context_gate_session_state

HOLDOUT_PATH = Path(__file__).resolve().parent / "eval" / "problem_solving_holdout.json"


def _load_cases() -> list[dict]:
    data = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
    return list(data["cases"])


@pytest.mark.parametrize(
    "case",
    [c for c in _load_cases() if c["kind"] == "trap"],
    ids=lambda c: c["id"],
)
def test_holdout_traps_trigger_meta_triage_and_avoid_sniper_demotion(case: dict) -> None:
    """Every unseen cross-domain trap must receive META-TRIAGE and stay >= STANDARD."""
    reset_context_gate_session_state()
    get_permissions().set_secret_mode(False)
    fake_search = {"results": [{"id": "doc1", "content": "context", "rrf_score": 0.05}]}

    with (
        patch("athena.tools.meta_pattern_matcher.detect_latent_meta_patterns", return_value=[]),
        patch("athena.tools.search.run_search", return_value=fake_search),
    ):
        res = context_gate(case["query"], limit=3, web=False)

    assert res["risk_level"] in ("STANDARD", "ULTRA"), (
        f"{case['id']} was demoted to {res['risk_level']}"
    )
    assert "META-TRIAGE" in res["directive"], (
        f"{case['id']} missed META-TRIAGE directive: {res['directive']}"
    )


@pytest.mark.parametrize(
    "case",
    [c for c in _load_cases() if c["kind"] == "control"],
    ids=lambda c: c["id"],
)
def test_holdout_clean_l1_controls_never_false_escalate_to_ultra(case: dict) -> None:
    """Clean reversible L1/system queries must not burn ULTRA compute."""
    reset_context_gate_session_state()
    get_permissions().set_secret_mode(False)
    fake_search = {"results": [{"id": "doc1", "content": "context", "rrf_score": 0.05}]}

    with (
        patch("athena.tools.meta_pattern_matcher.detect_latent_meta_patterns", return_value=[]),
        patch("athena.tools.search.run_search", return_value=fake_search),
    ):
        res = context_gate(case["query"], limit=3, web=False)

    assert res["risk_level"] != "ULTRA", (
        f"{case['id']} false-escalated to ULTRA: {res['lambda']}"
    )
    if res["intent"] == "SYSTEM_KNOWLEDGE":
        assert "META-TRIAGE" not in res["directive"]
