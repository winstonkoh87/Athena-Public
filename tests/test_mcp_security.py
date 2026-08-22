"""
tests.test_mcp_security
=======================
Unit tests verifying MCP resource and tool permission gates and Secret Mode redactions.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from athena.core.permissions import (
    Permission,
    PermissionDenied,
    PermissionEngine,
    SecretModeViolation,
    Sensitivity,
    get_permissions,
)
from athena.mcp_server import current_session_resource, permission_status, set_secret_mode


class TestMCPSecurity(unittest.TestCase):
    def setUp(self):
        self.perms = get_permissions()
        self.original_level = self.perms.caller_level
        self.original_secret = self.perms.secret_mode

    def tearDown(self):
        self.perms.caller_level = self.original_level
        self.perms.secret_mode = self.original_secret

    def test_permission_status_tool_gated(self):
        """Verify permission_status returns full manifest and caller state."""
        status = permission_status()
        self.assertIn("caller_level", status)
        self.assertIn("manifest", status)
        self.assertTrue(len(status["manifest"]) > 0)

    def test_set_secret_mode_tool(self):
        """Verify set_secret_mode requires admin/appropriate permission level."""
        # When caller is READ only
        self.perms.caller_level = Permission.READ
        with self.assertRaises(PermissionDenied):
            set_secret_mode(True)

        # When caller is ADMIN or WRITE
        self.perms.caller_level = Permission.ADMIN
        res = set_secret_mode(True)
        self.assertTrue(res["secret_mode"])
        self.assertTrue(self.perms.secret_mode)

    @patch("athena.sessions.recall_last_session")
    def test_current_session_resource_security(self, mock_recall):
        """Verify athena://session/current resource enforces permissions and blocks internal data in Secret Mode."""
        mock_token = "sk-" + "mocktestsecrettoken1234567890"
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md") as tmp:
            tmp.write(
                "# Session Log\n"
                "**Focus**: System review\n"
                f"TEST_CREDENTIAL={mock_token}\n"
                "SENSITIVE_METRIC: +500\n"
            )
            tmp_path = Path(tmp.name)

        try:
            mock_recall.return_value = tmp_path
            self.perms.caller_level = Permission.WRITE

            # 1. Normal mode: full content accessible
            self.perms.secret_mode = False
            unredacted = current_session_resource()
            self.assertIn(mock_token, unredacted)

            # 2. Secret mode: internal resource is blocked (fail closed)
            self.perms.secret_mode = True
            with self.assertRaises(SecretModeViolation):
                current_session_resource()

            # 3. Direct redaction helper verification
            raw_text = f"TOKEN={mock_token}\nMetrics: +500"
            redacted = self.perms.redact(raw_text)
            self.assertNotIn(mock_token, redacted)
            self.assertIn("[REDACTED]", redacted)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


    def test_meta_awareness_check_in_secret_mode(self):
        """Verify meta_awareness_check tool can execute in Secret Mode without violation."""
        from athena.mcp_server import meta_awareness_check

        self.perms.secret_mode = True
        self.perms.caller_level = Permission.READ
        result = meta_awareness_check("Explain our system architecture")
        self.assertIn("fired", result)


if __name__ == "__main__":
    unittest.main()
