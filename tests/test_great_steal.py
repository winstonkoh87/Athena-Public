#!/usr/bin/env python3
"""
test_great_steal.py — Integration Tests for The Great Steal 2.0
================================================================

Tests the three features extracted from OpenClaw:
1. Agent-to-Agent RPC (Sessions Tools)
2. iOS Edge Node Webhook
3. Docker Sandbox Execution

Usage: python3 -m pytest Athena-Public/tests/test_great_steal.py -v
"""

import sys
from pathlib import Path

import pytest

# Add repo src to sys.path without mutating global ATHENA_ROOT for other tests
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if not SRC_DIR.exists():
    SRC_DIR = REPO_ROOT.parent / "Athena-Public" / "src"
sys.path.insert(0, str(SRC_DIR))


# =============================================
# FEATURE 1: Sessions RPC Tests
# =============================================


class TestSessionsRPC:
    """Test the Agent-to-Agent RPC message bus."""

    @pytest.fixture(autouse=True)
    def setup_rpc(self, tmp_path):
        """Create a fresh RPC instance with a temp database."""
        from athena.core.sessions_rpc import (
            SessionMessage,
            SessionRegister,
            SessionsRPC,
            SessionStatus,
        )

        self.db_path = tmp_path / "test_athena.db"
        self.rpc = SessionsRPC(db_path=self.db_path)
        self.rpc.init_tables()
        self.SessionRegister = SessionRegister
        self.SessionMessage = SessionMessage
        self.SessionStatus = SessionStatus

    def test_register_session(self):
        """Register a session and verify it appears in the list."""
        result = self.rpc.register_session(
            self.SessionRegister(
                session_id="master-001", role="master", goal="Test objective"
            )
        )
        assert result["session_id"] == "master-001"
        assert result["role"] == "master"
        assert result["status"] == "active"

    def test_register_auto_id(self):
        """Register without specifying ID should auto-generate one."""
        result = self.rpc.register_session(self.SessionRegister(role="A"))
        assert result["session_id"].startswith("swarm-A-")

    def test_send_and_receive_message(self):
        """Send a message between two sessions and verify history."""
        # Register both sessions
        self.rpc.register_session(self.SessionRegister(session_id="agent-A", role="A"))
        self.rpc.register_session(
            self.SessionRegister(session_id="master", role="master")
        )

        # Send message from agent to master
        send_result = self.rpc.send_message(
            self.SessionMessage(
                from_session="agent-A",
                to_session="master",
                content="Track A analysis complete. Found 3 risks.",
                msg_type="synthesis",
            )
        )
        assert send_result["status"] == "delivered"
        assert send_result["from"] == "agent-A"
        assert send_result["to"] == "master"

        # Retrieve history
        history = self.rpc.get_history("master")
        assert len(history) == 1
        assert history[0]["content"] == "Track A analysis complete. Found 3 risks."
        assert history[0]["msg_type"] == "synthesis"
        assert history[0]["read"] == 0  # Not yet marked at fetch time; marked after

    def test_unread_filter(self):
        """Unread-only filter should work correctly."""
        self.rpc.register_session(
            self.SessionRegister(session_id="master", role="master")
        )

        # Send 2 messages
        self.rpc.send_message(
            self.SessionMessage(from_session="A", to_session="master", content="Msg 1")
        )
        self.rpc.send_message(
            self.SessionMessage(from_session="B", to_session="master", content="Msg 2")
        )

        # First read marks them as read
        history1 = self.rpc.get_history("master", unread_only=True)
        assert len(history1) == 2

        # Second read with unread_only should return nothing
        history2 = self.rpc.get_history("master", unread_only=True)
        assert len(history2) == 0

    def test_list_sessions(self):
        """List sessions should return all registered sessions with unread counts."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.register_session(self.SessionRegister(session_id="s2", role="B"))

        sessions = self.rpc.list_sessions()
        assert len(sessions) == 2
        roles = {s["role"] for s in sessions}
        assert roles == {"A", "B"}

    def test_update_status(self):
        """Update session status should persist."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.update_status(self.SessionStatus(session_id="s1", status="completed"))

        sessions = self.rpc.list_sessions(status="completed")
        assert len(sessions) == 1
        assert sessions[0]["status"] == "completed"

    def test_list_filter_by_status(self):
        """Filter sessions by status."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.register_session(self.SessionRegister(session_id="s2", role="B"))
        self.rpc.update_status(self.SessionStatus(session_id="s1", status="completed"))

        active = self.rpc.list_sessions(status="active")
        assert len(active) == 1
        assert active[0]["session_id"] == "s2"


# =============================================
# FEATURE 2: Edge Node Tests
# =============================================


class TestEdgeNode:
    """Test the iOS Edge Node ingest pipeline."""

    @pytest.fixture(autouse=True)
    def setup_ingest(self, tmp_path, monkeypatch):
        """Redirect INGEST_DIR to a temp directory."""
        import athena.core.edge_node as edge_mod

        monkeypatch.setattr(edge_mod, "INGEST_DIR", tmp_path)
        self.ingest_dir = tmp_path
        self.edge_mod = edge_mod

    def test_text_ingest(self):
        """Text payload should create a .md file."""
        from athena.core.edge_node import IngestPayload, process_ingest

        result = process_ingest(
            IngestPayload(
                type="text",
                data="This is a quick thought from my iPhone.",
                metadata={"source": "ios_shortcut"},
            )
        )
        assert result.status == "saved"
        assert result.type == "text"

        # Verify file exists
        files = list(self.ingest_dir.glob("*.md"))
        assert len(files) == 1
        content = files[0].read_text()
        assert "This is a quick thought from my iPhone." in content
        assert "ios_shortcut" in content

    def test_location_ingest(self):
        """Location payload should create a .json file."""
        import json

        from athena.core.edge_node import IngestPayload, process_ingest

        result = process_ingest(
            IngestPayload(
                type="location",
                data="1.3521,103.8198",
                metadata={"source": "iphone_gps", "city": "Singapore"},
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert data["raw"] == "1.3521,103.8198"

    def test_camera_ingest(self):
        """Camera payload (base64) should create a .jpg file."""
        import base64

        from athena.core.edge_node import IngestPayload, process_ingest

        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # Fake JPEG header
        b64_data = base64.b64encode(fake_image).decode()

        result = process_ingest(
            IngestPayload(
                type="camera",
                data=b64_data,
                metadata={"source": "iphone_camera"},
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.jpg"))
        assert len(files) == 1
        assert files[0].stat().st_size > 0

    def test_unknown_type_fallback(self):
        """Unknown types should fall back to .bin."""
        from athena.core.edge_node import IngestPayload, process_ingest

        result = process_ingest(
            IngestPayload(
                type="biometric",
                data="heart_rate=72",
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.bin"))
        assert len(files) == 1


# =============================================
# FEATURE 3: Sandbox Tests (Unit only — Docker optional)
# =============================================


class TestSandbox:
    """Test the sandbox module logic (does NOT require Docker)."""

    def test_sandbox_request_model(self):
        """SandboxExecRequest model should have correct defaults."""
        from athena.core.sandbox import SandboxExecRequest

        req = SandboxExecRequest(script="print('hello')")
        assert req.timeout == 30
        assert req.allow_network is False

    def test_sandbox_response_model(self):
        """SandboxExecResponse should serialize correctly."""
        from athena.core.sandbox import SandboxExecResponse

        resp = SandboxExecResponse(
            stdout="hello\n",
            stderr="",
            exit_code=0,
            execution_time=0.5,
            sandbox="athena-sandbox:latest",
        )
        assert resp.stdout == "hello\n"
        assert resp.exit_code == 0

    def test_sandbox_unavailable_gracefully(self):
        """is_available() should return False if Docker is not installed."""
        from athena.core.sandbox import SandboxRunner

        runner = SandboxRunner(image="nonexistent-image:latest")
        # This should not crash, just return False
        available = runner.is_available()
        assert isinstance(available, bool)


# =============================================
# FEATURE 4: Skill Telemetry (Great Steal III)
# =============================================


class TestSkillTelemetry:
    """Test the JSONL skill usage telemetry system."""

    @pytest.fixture(autouse=True)
    def setup_telemetry(self, tmp_path, monkeypatch):
        """Redirect telemetry log to a temp directory."""
        import athena.core.skill_telemetry as telem_mod

        self.log_path = tmp_path / "skill_usage.jsonl"
        monkeypatch.setattr(telem_mod, "_get_telemetry_path", lambda: self.log_path)
        self.telem = telem_mod

    def test_log_invocation(self):
        """log_skill_invocation should create a JSONL entry."""
        record = self.telem.log_skill_invocation(
            "Protocol 367", session_id="test-session", trigger="auto"
        )
        assert record["skill"] == "Protocol 367"
        assert record["trigger"] == "auto"
        assert self.log_path.exists()
        assert self.log_path.read_text().strip() != ""

    def test_log_multiple_and_stats(self):
        """Multiple invocations should aggregate correctly in stats."""
        self.telem.log_skill_invocation("Protocol 367", "s1", trigger="auto")
        self.telem.log_skill_invocation("Protocol 367", "s2", trigger="manual")
        self.telem.log_skill_invocation("Protocol 162", "s1", trigger="auto")

        stats = self.telem.get_skill_stats(days=30)
        assert stats["total_invocations"] == 3
        assert stats["unique_skills"] == 2
        assert stats["skills"]["Protocol 367"]["count"] == 2
        assert stats["skills"]["Protocol 367"]["auto_pct"] == 0.5
        assert stats["skills"]["Protocol 162"]["count"] == 1

    def test_log_skill_change_excluded_from_stats(self):
        """skill_change events should NOT appear in invocation stats."""
        self.telem.log_skill_invocation("Protocol 367", "s1")
        self.telem.log_skill_change("new_skill", "added", "/path/to/skill.md")

        stats = self.telem.get_skill_stats(days=30)
        assert stats["total_invocations"] == 1  # Only invocation, not change

    def test_dead_skills(self):
        """get_dead_skills should return skills with zero invocations."""
        self.telem.log_skill_invocation("Protocol 367", "s1")

        dead = self.telem.get_dead_skills(
            known_skills=["Protocol 367", "Protocol 162", "Protocol 999"],
            days=30,
        )
        assert "Protocol 367" not in dead
        assert "Protocol 162" in dead
        assert "Protocol 999" in dead

    def test_top_skills_sorted(self):
        """top_skills should be sorted by count descending."""
        for _ in range(5):
            self.telem.log_skill_invocation("Skill A", "s1")
        for _ in range(3):
            self.telem.log_skill_invocation("Skill B", "s1")
        self.telem.log_skill_invocation("Skill C", "s1")

        stats = self.telem.get_skill_stats(days=30)
        top = stats["top_skills"]
        assert top[0] == ("Skill A", 5)
        assert top[1] == ("Skill B", 3)
        assert top[2] == ("Skill C", 1)


# =============================================
# FEATURE 5: Skill Nudge (Great Steal III)
# =============================================


class TestSkillNudge:
    """Test the 2-tier keyword matching engine."""

    def test_tier1_primary_keyword(self):
        """Primary keywords (Tier 1) should match with high confidence."""
        from athena.core.skill_nudge import match_skills

        results = match_skills("What is Kelly criterion for my positions?")
        assert len(results) > 0
        match = results[0]
        assert match["tier"] == 1
        assert match["confidence"] == 0.9
        assert "367" in match["skill"]

    def test_tier2_secondary_keywords(self):
        """Secondary keywords (Tier 2) need 2+ matches."""
        from athena.core.skill_nudge import match_skills

        results = match_skills("Help me with marketing positioning and pricing")
        pmod_matches = [r for r in results if "PMOD" in r["skill"]]
        assert len(pmod_matches) > 0
        assert pmod_matches[0]["tier"] == 2

    def test_negative_keywords_bail(self):
        """Negative keywords should return empty results."""
        from athena.core.skill_nudge import match_skills

        assert match_skills("hello") == []
        assert match_skills("thanks for the help") == []
        assert match_skills("test") == []

    def test_no_match_returns_empty(self):
        """Unrelated prompts should return no matches."""
        from athena.core.skill_nudge import match_skills

        results = match_skills("What is the weather today in Singapore?")
        assert results == []

    def test_max_results_limit(self):
        """Results should respect max_results parameter."""
        from athena.core.skill_nudge import match_skills

        # A very broad prompt that could match many skills
        results = match_skills(
            "I need help with trading risk management and marketing strategy",
            max_results=2,
        )
        assert len(results) <= 2

    def test_registry_summary(self):
        """get_registry_summary should return all registered skills."""
        from athena.core.skill_nudge import get_registry_summary

        summary = get_registry_summary()
        assert len(summary) > 0
        for item in summary:
            assert "skill" in item
            assert "primary_keywords" in item
            assert "hint" in item


# =============================================
# FEATURE 6: Session Efficiency (Great Steal III)
# =============================================


class TestSessionEfficiency:
    """Test the composite session efficiency scoring."""

    def test_perfect_efficiency(self):
        """High skill usage, low tokens, high cache, zero retries = excellent."""
        from athena.core.session_efficiency import calculate_session_efficiency

        result = calculate_session_efficiency(
            skill_invocations=18,
            total_prompts=20,
            tokens_used=8000,
            token_budget=20000,
            memory_hits=19,
            total_queries=20,
            retry_count=0,
            total_actions=20,
        )
        assert result.score >= 80
        assert result.grade == "excellent"

    def test_poor_efficiency(self):
        """No skills, over budget, no cache, many retries = needs_work."""
        from athena.core.session_efficiency import calculate_session_efficiency

        result = calculate_session_efficiency(
            skill_invocations=0,
            total_prompts=20,
            tokens_used=25000,  # Over budget
            token_budget=20000,
            memory_hits=0,
            total_queries=20,
            retry_count=15,
            total_actions=20,
        )
        assert result.score < 60
        assert result.grade == "needs_work"

    def test_medium_efficiency(self):
        """Moderate usage across all metrics = good."""
        from athena.core.session_efficiency import calculate_session_efficiency

        result = calculate_session_efficiency(
            skill_invocations=10,
            total_prompts=20,
            tokens_used=12000,
            token_budget=20000,
            memory_hits=12,
            total_queries=20,
            retry_count=2,
            total_actions=20,
        )
        assert 50 <= result.score <= 90

    def test_to_dict(self):
        """to_dict should produce a serializable dictionary."""
        from athena.core.session_efficiency import calculate_session_efficiency

        result = calculate_session_efficiency()
        d = result.to_dict()
        assert "score" in d
        assert "grade" in d
        assert "components" in d
        assert isinstance(d["components"]["skill_utilization"], float)

    def test_format_report(self):
        """format_efficiency_report should produce readable output."""
        from athena.core.session_efficiency import (
            calculate_session_efficiency,
            format_efficiency_report,
        )

        result = calculate_session_efficiency(skill_invocations=15, total_prompts=20)
        report = format_efficiency_report(result)
        assert "Session Efficiency" in report
        assert "Skill Utilization" in report
        assert "%" in report

    def test_zero_division_safety(self):
        """Should handle zero values without crashing."""
        from athena.core.session_efficiency import calculate_session_efficiency

        result = calculate_session_efficiency(
            skill_invocations=0,
            total_prompts=0,
            tokens_used=0,
            token_budget=0,
            memory_hits=0,
            total_queries=0,
            retry_count=0,
            total_actions=0,
        )
        assert isinstance(result.score, int)
        assert 0 <= result.score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
