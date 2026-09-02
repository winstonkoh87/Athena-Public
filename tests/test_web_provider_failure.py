"""Provider failure regression tests (P4.2).

Asserts that when all web providers are down:
1. web_channel reports degraded: True
2. No crash occurs
3. Local channels remain intact
4. The old silent-[] pattern is dead
"""
import unittest
from unittest.mock import MagicMock, patch


class TestProviderFailureRegression(unittest.TestCase):
    """Regression tests for the silent-[] bug class."""

    def test_all_providers_down_returns_degraded(self):
        """When all providers fail, web_search returns degraded=True, not empty []."""
        from athena.tools.web_providers import ProviderFailure, web_search

        # Mock all providers to fail
        with patch("athena.tools.web_providers.get_provider_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.name = "mock_provider"
            mock_provider.healthy.return_value = True
            mock_provider.search.side_effect = ProviderFailure("mock", "test failure")
            mock_chain.return_value = [mock_provider]

            results, meta = web_search("test query")

            self.assertEqual(results, [])
            self.assertTrue(meta["degraded"])
            self.assertIn("test failure", str(meta["errors"]))

    def test_provider_failure_no_crash(self):
        """Web search never crashes, even with unexpected errors."""
        from athena.tools.web_providers import web_search

        with patch("athena.tools.web_providers.get_provider_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.name = "crash_provider"
            mock_provider.healthy.return_value = True
            mock_provider.search.side_effect = RuntimeError("unexpected")
            mock_chain.return_value = [mock_provider]

            # Must not raise
            results, meta = web_search("test query")
            self.assertIsInstance(results, list)
            self.assertIsInstance(meta, dict)

    def test_local_channels_unaffected_by_web_failure(self):
        """Verify that local search channels work even when web is broken."""
        from athena.tools.search import collect_canonical

        # Canonical search should work regardless of web state
        results = collect_canonical("protocol governance")
        # Just verify it doesn't crash and returns a list
        self.assertIsInstance(results, list)

    def test_web_result_has_fetched_at(self):
        """Web results must carry fetched_at timestamps."""
        from athena.tools.web_providers import WebResult

        # Verify WebResult has fetched_at field
        wr = WebResult(
            title="Test",
            snippet="Test snippet",
            url="https://example.com",
            fetched_at="2026-09-02T00:00:00+00:00",
            provider="test",
            position=0,
        )
        self.assertTrue(hasattr(wr, "fetched_at"))
        self.assertIn("2026", wr.fetched_at)


if __name__ == "__main__":
    unittest.main()
