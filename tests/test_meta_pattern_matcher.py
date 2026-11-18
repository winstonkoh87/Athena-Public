"""
tests.test_meta_pattern_matcher
===============================
Unit tests for the Latent Meta-Pattern Matcher (GTO Architecture Upgrade).
Verifies:
1. Pattern detection across core business, trading, platform, and diagnostic queries.
2. Graceful empty/none handling.
3. Sub-5ms execution speed.
"""

import time
import unittest

from athena.tools.meta_pattern_matcher import (
    detect_latent_meta_patterns,
)


class TestMetaPatternMatcher(unittest.TestCase):
    def test_empty_and_benign_queries(self):
        self.assertEqual(detect_latent_meta_patterns(""), [])
        self.assertEqual(detect_latent_meta_patterns("hello"), [])
        self.assertEqual(detect_latent_meta_patterns("what time is it"), [])

    def test_diagnostic_gap_and_structural_protection(self):
        query = "How should I set up the used car inspection service with direct-owner warranty?"
        matches = detect_latent_meta_patterns(query)
        matched_ids = [m["id"] for m in matches]
        self.assertIn("MP-18", matched_ids)
        self.assertIn("MP-7", matched_ids)

    def test_short_gamma_variance(self):
        query = "I am on a hot streak with high win rate, should I size up or run monte carlo?"
        matches = detect_latent_meta_patterns(query)
        matched_ids = [m["id"] for m in matches]
        self.assertIn("MP-16", matched_ids)

    def test_sharecropping_platform(self):
        query = "Carousell is raising their middleman commission and platform take-rate again."
        matches = detect_latent_meta_patterns(query)
        matched_ids = [m["id"] for m in matches]
        self.assertIn("MP-1", matched_ids)

    def test_observable_liquidity(self):
        query = "Where is the observable liquidity and high-frequency cash in this market?"
        matches = detect_latent_meta_patterns(query)
        matched_ids = [m["id"] for m in matches]
        self.assertIn("MP-19", matched_ids)

    def test_compounding_and_leverage_inversion(self):
        compounding_matches = detect_latent_meta_patterns(
            "This sweat equity model is trading time for money in a linear carnot trap."
        )
        self.assertIn("MP-6", [m["id"] for m in compounding_matches])

        curve_matches = detect_latent_meta_patterns(
            "Stop committing the boxer fallacy on the red curve vs blue curve table selection."
        )
        self.assertIn("MP-9", [m["id"] for m in curve_matches])

        kopitiam_matches = detect_latent_meta_patterns(
            "My kopitiam hawker stall tenancy is bleeding cash at renewal."
        )
        self.assertIn("MP-1", [m["id"] for m in kopitiam_matches])

    def test_execution_latency(self):
        start = time.perf_counter()
        for _ in range(100):
            detect_latent_meta_patterns("used car inspection warranty middleman platform take-rate drawdown")
        elapsed_ms = (time.perf_counter() - start) * 1000 / 100
        # Average execution must be well under 5ms
        self.assertLess(elapsed_ms, 5.0)


if __name__ == "__main__":
    unittest.main()
