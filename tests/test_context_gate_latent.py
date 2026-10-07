"""
tests.test_context_gate_latent
==============================
Unit tests for Latent Meta-Pattern expansion inside context_gate.
"""

import json
import unittest
from unittest.mock import patch

from athena.core.permissions import get_permissions
from athena.mcp_server import context_gate


class TestContextGateLatentExpansion(unittest.TestCase):
    def setUp(self):
        perms = get_permissions()
        perms.set_secret_mode(False)

    @patch("athena.tools.search.run_search")
    def test_context_gate_latent_projection_triggers(self, mock_run_search):
        def mock_search_impl(q, *args, **kwargs):
            if "MP-18" in q or "MP-7" in q:
                payload = {"results": [{"id": "CS-596.md", "content": "Diagnostic gap analysis"}]}
            else:
                payload = {"results": [{"id": "car_arbitrage.md", "content": "Used car inspection"}]}
            print(json.dumps(payload))
            return payload

        mock_run_search.side_effect = mock_search_impl

        res = context_gate(
            "How should I structure the used car inspection service with direct-owner warranty?",
            limit=5,
            web=False
        )

        # 1. Latent Meta-Patterns detected
        self.assertIn("latent_meta_patterns", res)
        matched_ids = [mp["id"] for mp in res["latent_meta_patterns"]]
        self.assertIn("MP-18", matched_ids)
        self.assertIn("MP-7", matched_ids)

        # 2. Directive includes cross-domain projection instruction
        self.assertIn("CROSS-DOMAIN PROJECTION", res["directive"])
        self.assertIn("MP-18", res["directive"])

        # 3. Context results contain projected items
        results = res["context"]["results"]
        projected = [r for r in results if "meta_pattern_projection" in r]
        self.assertTrue(len(projected) > 0)
        self.assertEqual(projected[0]["meta_pattern_projection"]["id"], "MP-18")


if __name__ == "__main__":
    unittest.main()
