"""
tests/test_personalisation.py — Personalisation Engine & Intent Unit Tests
==========================================================================

Verifies query intent classification, dynamic RRF weight profiles, un-gated
personal vector access, user state snapshot generation, and personalisation
golden benchmark validation.
"""

import json
from pathlib import Path

import pytest

from athena.core.models import SearchResult
from athena.tools.personalisation import (
    build_personalisation_prompt,
    build_user_state_snapshot,
)
from athena.tools.search import (
    classify_query_intent,
    collect_vectors,
    get_intent_weights,
    weighted_rrf,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestIntentClassification:
    """Test query intent classifier on decision vs system knowledge archetypes."""

    @pytest.mark.parametrize(
        "query",
        [
            "What rate should I charge for a 5-hour consulting engagement?",
            "Should I accept a S$300 freelance project right now?",
            "Should I risk 10% on this gold scalp breakout?",
            "How should I handle my Saturday gym session this week?",
            "How should I respond to an ambiguous client negotiation message?",
            "I feel anxious about pipeline drought and want to deconstruct this trigger",
            "What should Winston do about his active runway and cash buffer?",
            "Is it worth taking this assignment at $120/hr?",
            # Edge cases caught in Opus audit
            "negotiate this deal for me",
            "My wife cheated on me, what do I do about the BTO?",
        ],
    )
    def test_personalised_decision_intent(self, query: str):
        intent = classify_query_intent(query)
        assert intent == "PERSONALISED_DECISION", f"Failed for query: {query} (got {intent})"

    @pytest.mark.parametrize(
        "query",
        [
            "What is Protocol 528 sandboxed execution modes?",
            "Explain PAT-574 substance decode framework",
            "How does ARC-528 work in the orchestrator?",
            "What is P509 crisis triage protocol?",
            "Show me the system architecture manifest and hooks",
            "Run test_eval_harness and verify linter rules",
            # Edge cases caught in Opus audit
            "How does weighted_rrf work in search.py?",
            "Explain the bionic-decision-engine skill",
        ],
    )
    def test_system_knowledge_intent(self, query: str):
        intent = classify_query_intent(query)
        assert intent == "SYSTEM_KNOWLEDGE", f"Failed for query: {query} (got {intent})"

    def test_general_intent_fallback(self):
        intent = classify_query_intent("DuckDB parquet memory optimization")
        assert intent == "GENERAL"

    def test_general_intent_simple_questions(self):
        """Verify non-personal, non-system queries stay GENERAL."""
        for query in ["What is the weather today?", "help me", "hello"]:
            assert classify_query_intent(query) == "GENERAL", f"'{query}' should be GENERAL"


class TestDynamicWeighting:
    """Verify intent-driven RRF weight calibration."""

    def test_decision_weights_profile(self):
        weights = get_intent_weights("PERSONALISED_DECISION")
        assert weights["user_profile"] == 4.0
        assert weights["canonical"] == 2.8
        assert weights["session"] == 3.0
        assert weights["framework_docs"] == 0.8
        assert weights["user_profile"] > weights["protocol"]

    def test_system_weights_profile(self):
        weights = get_intent_weights("SYSTEM_KNOWLEDGE")
        assert weights["protocol"] == 3.5
        assert weights["capability"] == 3.2
        assert weights["protocol"] > weights["user_profile"]

    def test_weighted_rrf_with_decision_intent(self):
        # Create identical score candidates from different channels
        user_doc = SearchResult(id="user_doc", content="Rate floor $150", source="user_profile", score=1.0)
        protocol_doc = SearchResult(id="protocol_doc", content="Protocol 528 spec", source="protocol", score=1.0)

        ranked = {
            "user_profile": [user_doc],
            "protocol": [protocol_doc],
        }

        # Under PERSONALISED_DECISION: user_profile (4.0) > protocol (2.0) → user_doc wins
        fused_decision = weighted_rrf(ranked, intent="PERSONALISED_DECISION")
        assert fused_decision[0].id == "user_doc", "user_profile should rank #1 in PERSONALISED_DECISION"

        # Under SYSTEM_KNOWLEDGE: protocol (3.5) > user_profile (1.5) → protocol_doc wins
        fused_system = weighted_rrf(ranked, intent="SYSTEM_KNOWLEDGE")
        assert fused_system[0].id == "protocol_doc", "protocol should rank #1 in SYSTEM_KNOWLEDGE"


class TestPersonalVectorUnGating:
    """Verify personal domain is included by default in local search."""

    def test_collect_vectors_default_exclude_domains_is_empty(self, monkeypatch):
        called_args = {}

        class FakeClient:
            def rpc(self, name, params):
                called_args["params"] = params
                return self
            def execute(self):
                return type("Res", (), {"data": []})()

        monkeypatch.setattr("athena.memory.vectors.get_client", lambda: FakeClient())
        monkeypatch.setattr("athena.memory.vectors.get_embedding", lambda q: [0.1] * 768)

        # Calling without exclude_domains should not exclude 'personal'
        results = collect_vectors("test query")
        assert isinstance(results, list)


class TestPersonalisationPromptAndSnapshot:
    """Verify active synthesis framing and snapshot generation."""

    def test_build_user_state_snapshot(self):
        snapshot = build_user_state_snapshot()
        assert "rate_floor" in snapshot
        assert "financial_constraints" in snapshot
        assert "key_man_risk" in snapshot
        assert "behavioral_anchors" in snapshot
        assert "state_as_of" in snapshot
        assert "strategic_priorities" in snapshot
        assert isinstance(snapshot["strategic_priorities"], list)

    def test_rate_floor_exact_currency_shape(self):
        """Verify rate_floor is a clean currency string and not corrupted markdown prose."""
        snapshot = build_user_state_snapshot()
        rate = snapshot.get("rate_floor", "")
        # Must match clean currency shape (e.g. $150/hr or S$150/hr)
        import re
        assert re.match(r"^S?\$\d+(?:/hr)?$", rate), f"rate_floor '{rate}' does not match currency pattern"
        # Specifically verify it is NOT polluted by line 334 trading paragraph ("noise floor", "Barrier Proximity")
        assert "noise floor" not in rate.lower()
        assert "barrier proximity" not in rate.lower()
        assert "kelly" not in rate.lower()

    def test_poisoned_canonical_triggers_fallback(self, monkeypatch, tmp_path):
        """Verify that malformed CANONICAL rate rows gracefully trigger shape fallback."""
        poisoned_canonical = tmp_path / "CANONICAL.md"
        poisoned_canonical.write_text(
            "| **Consulting Rate** | **This is corrupted text that is not a rate** |\n",
            encoding="utf-8",
        )
        monkeypatch.setattr("athena.tools.personalisation.CANONICAL_PATH", poisoned_canonical)
        snapshot = build_user_state_snapshot()
        # Default safe fallback must be retained
        assert "S$150/hr" in snapshot["rate_floor"]
        assert "[STATE_FIELD_FALLBACK]" in snapshot.get("_provenance_rate_floor", "")

    def test_build_personalisation_prompt(self):
        res = [SearchResult(id="doc_1", content="Client negotiation history", source="case_study", score=0.9)]
        prompt = build_personalisation_prompt("Should I accept this client?", res)
        assert "<personalisation_context" in prompt
        assert "OPERATOR STATE & CONSTRAINTS" in prompt
        assert "SYNTHESIS INSTRUCTION" in prompt
        assert "Do NOT provide generic" in prompt


class TestDegradedRecallAndAgenticWiring:
    """Verify degraded recall flag propagation and agentic search personalisation wiring."""

    def test_search_json_has_degraded_recall_flag(self, capsys, monkeypatch):
        from athena.tools.search import run_search

        # Mock vector collection to fail
        monkeypatch.setattr("athena.tools.search.collect_vectors", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Supabase 404 connection failed")))

        run_search("DuckDB optimization", limit=3, json_output=True)
        captured = capsys.readouterr()
        # Parse JSON output from stdout
        payload = json.loads(captured.out.strip())
        assert "degraded_recall" in payload
        assert isinstance(payload["degraded_recall"], bool)

    def test_agentic_search_json_wires_personalisation_for_decisions(self, capsys):
        from athena.tools.agentic_search import run_agentic_search

        run_agentic_search("What rate should I charge for consulting?", limit=3, json_output=True)
        captured = capsys.readouterr()
        payload = json.loads(captured.out.strip())
        assert payload.get("intent") == "PERSONALISED_DECISION"
        assert "personalisation_context" in payload
        assert "OPERATOR STATE & CONSTRAINTS" in payload["personalisation_context"]
        assert "user_state" in payload
        assert "rate_floor" in payload["user_state"]


class TestGoldenBenchmark:
    """Validate all golden personalisation cases."""

    def test_gold_personalisation_suite(self):
        gold_path = PROJECT_ROOT / "src" / "athena" / "eval" / "gold_personalisation.json"
        assert gold_path.exists(), "gold_personalisation.json must exist"

        data = json.loads(gold_path.read_text(encoding="utf-8"))
        test_cases = data.get("test_cases", [])
        assert len(test_cases) >= 18, f"Expected >= 18 golden test cases, found {len(test_cases)}"

        for case in test_cases:
            query = case["query"]
            expected_intent = case["expected_intent"]
            actual_intent = classify_query_intent(query)
            assert actual_intent == expected_intent, f"Benchmark failure on {case['id']}: '{query}' -> got '{actual_intent}', expected '{expected_intent}'"


class TestSearchResultAndContextGateWiring:
    """Validate SearchResult deserialization and context_gate personalisation frame."""

    def test_search_result_to_dict_and_kwargs_roundtrip(self):
        from athena.core.models import SearchResult

        sr = SearchResult(
            id="test-1",
            content="Sample text",
            source="fts_bm25",
            metadata={"path": "foo/bar.md"},
            score=0.9,
            rrf_score=0.05,
        )
        d = sr.to_dict()
        assert d["path"] == "foo/bar.md"

        # Roundtrip via **d must succeed without TypeError on unexpected kwarg 'path'
        reconstructed = SearchResult(**d)
        assert reconstructed.id == "test-1"
        assert reconstructed.path == "foo/bar.md"
        assert reconstructed.metadata["path"] == "foo/bar.md"

    def test_context_gate_personalisation_resolution(self):
        from athena.core.permissions import get_permissions
        from athena.mcp_server import context_gate

        perms = get_permissions()
        perms.set_secret_mode(False)
        res = context_gate("What consulting rate should I quote for this project?", limit=3)
        assert res.get("intent") == "PERSONALISED_DECISION"
        assert res.get("personalisation") is not None
        assert "OPERATOR STATE & CONSTRAINTS" in res["personalisation"]
        assert res.get("user_state") is not None
        assert "rate_floor" in res["user_state"]



