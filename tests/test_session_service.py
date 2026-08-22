"""
tests.test_session_service
==========================
Unit tests verifying unified SessionService creation, checkpointing, closing,
edge case handling, and subsystem delegation.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from athena.lifecycle.session_service import SessionService


class TestSessionService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.temp_dir.name) / "session_logs"
        self.service = SessionService(sessions_dir=self.sessions_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_session_and_checkpoint(self):
        """Verify session creation produces valid frontmatter and checkpoints append correctly."""
        session_file = self.service.create_session(
            focus="Release 1 Substrate Hardening",
            tags=["architecture", "security"],
        )
        self.assertTrue(session_file.exists())

        content = session_file.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"))
        self.assertIn("session_id:", content)
        self.assertIn("status: in_progress", content)
        self.assertIn("Release 1 Substrate Hardening", content)

        # Append checkpoint
        self.service.append_checkpoint(
            summary="Completed MCP Security audit",
            bullets=["Gated session resource", "Secured secret mode toggle"],
            log_path=session_file,
        )

        updated = session_file.read_text(encoding="utf-8")
        self.assertIn("Completed MCP Security audit", updated)
        self.assertIn("Gated session resource", updated)

        # Close session
        receipt = self.service.close_session(
            session_path=session_file,
            verdict="🚀 SQUAD",
            learnings={
                "system": ["Unified SessionService eliminates lifecycle drift."],
                "user": ["Prefers deterministic receipts."],
            },
        )

        self.assertEqual(receipt["status"], "SUCCESS")
        self.assertEqual(receipt["action"], "close_session")
        self.assertIn("rcpt_", receipt["receipt_id"])

        closed_content = session_file.read_text(encoding="utf-8")
        self.assertIn("status: closed", closed_content)
        self.assertIn("Unified SessionService eliminates lifecycle drift.", closed_content)

    def test_missing_dir_auto_creation(self):
        """Verify SessionService creates non-existent sessions directory on demand."""
        nested_dir = Path(self.temp_dir.name) / "deep" / "nested" / "sessions"
        service = SessionService(sessions_dir=nested_dir)
        self.assertFalse(nested_dir.exists())

        session_file = service.create_session(focus="Test nested dir")
        self.assertTrue(nested_dir.exists())
        self.assertTrue(session_file.exists())

    def test_append_checkpoint_nonexistent_raises(self):
        """Verify appending to a missing session file raises FileNotFoundError."""
        fake_path = self.sessions_dir / "non_existent_session.md"
        with self.assertRaises(FileNotFoundError):
            self.service.append_checkpoint(summary="Should fail", log_path=fake_path)

    def test_close_session_nonexistent_raises(self):
        """Verify closing a missing session file raises FileNotFoundError."""
        fake_path = self.sessions_dir / "non_existent_session.md"
        with self.assertRaises(FileNotFoundError):
            self.service.close_session(session_path=fake_path)

    def test_forward_lineage_linking(self):
        """Verify creating sequential sessions updates forward lineage link in previous session."""
        session1 = self.service.create_session(focus="Session 1")
        session2 = self.service.create_session(focus="Session 2")

        content1 = session1.read_text(encoding="utf-8")
        self.assertIn(f"next_session: {session2.stem}", content1)

    def test_receipt_uniqueness(self):
        """Verify generated receipts have unique IDs."""
        r1 = self.service.generate_receipt("test_action", "SUCCESS", {})
        r2 = self.service.generate_receipt("test_action", "SUCCESS", {})
        self.assertNotEqual(r1["receipt_id"], r2["receipt_id"])

    def test_shutdown_delegation(self):
        """Verify athena.boot.shutdown.close_session delegates to SessionService."""
        from athena.boot.shutdown import close_session as shutdown_close

        session_file = self.service.create_session(focus="Shutdown test")
        self.assertTrue(shutdown_close(session_file))

        closed_content = session_file.read_text(encoding="utf-8")
        self.assertIn("status: closed", closed_content)

    def test_sessions_module_delegation(self):
        """Verify athena.sessions module functions delegate to SessionService."""
        import athena.sessions as sessions_mod

        with patch("athena.lifecycle.session_service.get_session_service", return_value=self.service):
            session_file = sessions_mod.create_session(focus="Delegation test")
            self.assertTrue(session_file.exists())

            sessions_mod.append_checkpoint("Checkpoint via delegation", log_path=session_file)
            content = session_file.read_text(encoding="utf-8")
            self.assertIn("Checkpoint via delegation", content)

            receipt = sessions_mod.close_session(session_path=session_file)
            self.assertEqual(receipt["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
