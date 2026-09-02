import os
import unittest
from unittest.mock import MagicMock, patch

from athena.tools.web_providers import (
    DuckDuckGoProvider,
    ProviderFailure,
    WebResult,
    get_provider_chain,
    get_web_health,
    web_search,
)


class TestWebProviders(unittest.TestCase):
    def test_duckduckgo_failure_raises(self):
        """1. Test ProviderFailure is raised when DuckDuckGo fails"""
        provider = DuckDuckGoProvider()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection refused")
            with patch("time.sleep"):  # skip the 1s delay
                with self.assertRaises(ProviderFailure) as ctx:
                    provider.search("test")

                self.assertEqual(ctx.exception.provider, "duckduckgo")
                self.assertIn("Connection refused", ctx.exception.reason)

    def test_provider_chain_fallover(self):
        """2. Test provider chain fallover"""
        mock_results = [WebResult("Title", "Snippet", "http://example.com", "2023-01-01", "brave", 0)]

        with patch("athena.tools.web_providers.get_provider_chain") as mock_chain:
            serper = MagicMock()
            serper.name = "serper"
            serper.healthy.return_value = True
            serper.search.side_effect = ProviderFailure("serper", "API Error")

            brave = MagicMock()
            brave.name = "brave"
            brave.healthy.return_value = True
            brave.search.return_value = mock_results

            mock_chain.return_value = [serper, brave]

            results, metadata = web_search("test")

            self.assertEqual(results, mock_results)
            self.assertEqual(metadata["provider"], "brave")
            self.assertTrue(metadata["degraded"])
            self.assertEqual(len(metadata["errors"]), 1)
            self.assertIn("API Error", metadata["errors"][0])

            serper.search.assert_called_once_with("test", 5)
            brave.search.assert_called_once_with("test", 5)

    def test_all_providers_down(self):
        """3. Test all-providers-down returns degraded: True without crash"""
        with patch("athena.tools.web_providers.get_provider_chain") as mock_chain:
            ddg = MagicMock()
            ddg.name = "duckduckgo"
            ddg.healthy.return_value = True
            ddg.search.side_effect = ProviderFailure("duckduckgo", "Timeout")

            mock_chain.return_value = [ddg]

            results, metadata = web_search("test")

            self.assertEqual(results, [])
            self.assertEqual(metadata["provider"], "none")
            self.assertTrue(metadata["degraded"])
            self.assertEqual(len(metadata["errors"]), 1)
            self.assertIn("Timeout", metadata["errors"][0])

    def test_web_search_returns_webresult(self):
        """4. Test web_search returns WebResult objects with fetched_at timestamps"""
        mock_results = [WebResult("Title", "Snippet", "http://example.com", "2023-01-01", "duckduckgo", 0)]
        with patch("athena.tools.web_providers.get_provider_chain") as mock_chain:
            ddg = MagicMock()
            ddg.name = "duckduckgo"
            ddg.healthy.return_value = True
            ddg.search.return_value = mock_results
            mock_chain.return_value = [ddg]

            results, metadata = web_search("test")

            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], WebResult)
            self.assertTrue(bool(results[0].fetched_at))
            self.assertTrue(bool(metadata["fetched_at"]))

    def test_get_provider_chain_reads_env(self):
        """5. Test get_provider_chain reads WEB_PROVIDERS env var"""
        with patch.dict(os.environ, {"WEB_PROVIDERS": "duckduckgo,brave"}):
            chain = get_provider_chain()
            self.assertEqual(len(chain), 2)
            self.assertEqual(chain[0].name, "duckduckgo")
            self.assertEqual(chain[1].name, "brave")

    def test_get_web_health(self):
        """6. Test get_web_health returns proper structure"""
        with patch.dict(os.environ, {"SERPER_API_KEY": "123", "BRAVE_API_KEY": ""}):
            health = get_web_health()

            self.assertIn("providers", health)
            self.assertIn("active_provider", health)
            self.assertIn("degraded", health)

            self.assertEqual(health["active_provider"], "serper")

            providers = health["providers"]
            self.assertEqual(len(providers), 3)

            serper = next(p for p in providers if p["name"] == "serper")
            self.assertTrue(serper["healthy"])

            brave = next(p for p in providers if p["name"] == "brave")
            self.assertFalse(brave["healthy"])

    def test_duckduckgo_retry_logic(self):
        """7. Test DuckDuckGo retry logic (first attempt fails, retry succeeds)"""
        provider = DuckDuckGoProvider()

        mock_html = b'''
        <a class="result__url" href="http://example.com">Example</a>
        <a class="result__snippet" href="#">Snippet text</a>
        '''

        with patch("urllib.request.urlopen") as mock_urlopen:
            # First call raises Exception, second returns valid response
            mock_response = MagicMock()
            mock_response.read.return_value = mock_html
            mock_response.__enter__.return_value = mock_response

            mock_urlopen.side_effect = [Exception("Network Glitch"), mock_response]

            with patch("time.sleep") as mock_sleep:
                results = provider.search("test")

                self.assertEqual(len(results), 1)
                self.assertEqual(results[0].title, "Example")
                mock_sleep.assert_called_once_with(1)
                self.assertEqual(mock_urlopen.call_count, 2)

if __name__ == "__main__":
    unittest.main()
