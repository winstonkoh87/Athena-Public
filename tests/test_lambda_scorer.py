"""
tests.test_lambda_scorer
========================
Unit tests for the Deterministic Lambda Scorer (Phase C1.1).
Verifies:
1. Low-stakes & trivial queries score SNIPER (<10).
2. Medium-complexity queries score STANDARD (10-30).
3. High-stakes financial, legal, ruin, and strategic queries score ULTRA (>30).
4. S777 ruin query correctly triggers ULTRA.
5. Deterministic feature trace output and sub-5ms latency.
"""

import time
import unittest

from athena.core.governance import RiskLevel
from athena.core.lambda_scorer import assess_intel_posture, compute_lambda


class TestLambdaScorer(unittest.TestCase):
    def test_sniper_trivial_greetings(self):
        greetings = ["hi", "hello", "thanks!", "ok", "proceed", "lgtm"]
        for g in greetings:
            res = compute_lambda(g)
            self.assertEqual(res["tier"], "SNIPER")
            self.assertLess(res["score"], 10)
            self.assertEqual(res["risk_level"], RiskLevel.SNIPER)

    def test_sniper_short_system_fact(self):
        res = compute_lambda("what is protocol 501", intent="SYSTEM_KNOWLEDGE")
        self.assertEqual(res["tier"], "SNIPER")
        self.assertLess(res["score"], 10)

    def test_standard_general_queries(self):
        res = compute_lambda("how do I format this markdown table in python")
        self.assertEqual(res["tier"], "STANDARD")
        self.assertTrue(10 <= res["score"] <= 30)

    def test_ultra_s777_ruin_query(self):
        query = "audit my FX trading drawdown with -S,300 guillotine firewall and short-gamma exposure"
        res = compute_lambda(query, web_required=True)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)
        feature_names = [f["name"] for f in res["features"]]
        self.assertIn("ruin_risk", feature_names)

    def test_ultra_financial_and_contract_signing(self):
        query = "should I sign this client contract for S$1,500 with liability indemnity clause?"
        res = compute_lambda(query)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)
        feature_names = [f["name"] for f in res["features"]]
        self.assertIn("currency_amount", feature_names)
        self.assertIn("irreversible_action", feature_names)

    def test_ultra_social_high_stakes(self):
        query = "invite coursemate to elder brother wedding banquet with S$300 ang-bao"
        res = compute_lambda(query)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)

    def test_crisis_detection_referral_gate(self):
        crisis_queries = [
            "I want to end it all",
            "feeling suicidal today",
            "complete broken can't take it anymore",
            "no point in living",
        ]
        for q in crisis_queries:
            res = compute_lambda(q)
            self.assertTrue(res.get("is_crisis"), f"Expected is_crisis=True for '{q}'")
            referral = res.get("crisis_referral")
            self.assertIsNotNone(referral, f"Expected crisis_referral for '{q}'")
            self.assertIn("1-767", referral)
            self.assertIn("6389 2222", referral)
            self.assertIn("995", referral)
            self.assertIn("Athena is an AI assistant, not a clinician", referral)

    def test_crisis_inflections_and_indirect_signs(self):
        missed = [
            "thinking about unaliving myself tonight",
            "giving away my stuff and writing letters to people",
            "won't be around much longer",
        ]
        for q in missed:
            res = compute_lambda(q)
            self.assertTrue(res.get("is_crisis"), f"Expected is_crisis=True for '{q}'")

    def test_crisis_decoys_not_flagged(self):
        decoys = [
            "this joke is killing me, i'm dead lol",
            "my trading account got killed today",
            "neutral control statement about finance",
        ]
        for q in decoys:
            res = compute_lambda(q)
            self.assertFalse(res.get("is_crisis"), f"Expected is_crisis=False for decoy '{q}'")


    def test_audit_classifier_misses(self):
        # 1. Past-tense job exit
        res1 = compute_lambda("handed in my notice")
        self.assertGreaterEqual(res1["score"], 30)
        feat_names1 = [f["name"] for f in res1["features"]]
        self.assertIn("job_exit_paraphrase", feat_names1)

        # 2. All-in ruin risk
        res2 = compute_lambda("sell everything and go all in")
        self.assertGreaterEqual(res2["score"], 30)
        feat_names2 = [f["name"] for f in res2["features"]]
        self.assertIn("all_in_ruin_risk", feat_names2)

        # 3. Career exit
        res3 = compute_lambda("leaving my job to trade full time")
        self.assertGreaterEqual(res3["score"], 30)
        feat_names3 = [f["name"] for f in res3["features"]]
        self.assertIn("career_exit", feat_names3)

        # 4. Bare large number
        res4 = compute_lambda("200000")
        feat_names4 = [f["name"] for f in res4["features"]]
        self.assertIn("large_bare_number", feat_names4)

    def test_latency_performance(self):
        query = "audit my FX trading drawdown with -S,300 guillotine firewall and short-gamma exposure"
        start = time.perf_counter()
        for _ in range(200):
            compute_lambda(query, web_required=True)
        elapsed_ms = (time.perf_counter() - start) * 1000 / 200
        self.assertLess(elapsed_ms, 5.0)

    def test_micro_currency_amount_threshold_calibration(self):
        q1 = "Athena, buy the $1.15 one am I correct?"
        res1 = compute_lambda(q1)
        feat1 = {f["name"]: f["weight"] for f in res1["features"]}
        self.assertEqual(res1["score"], 14)
        self.assertEqual(feat1.get("micro_currency_amount"), 4)
        self.assertNotIn("currency_amount", feat1)
        posture1 = assess_intel_posture(q1, lambda_res=res1)
        self.assertEqual(posture1["posture"], "RECON_AND_FRAME")
        self.assertNotIn("high_stakes", posture1["reasons"])

        q2 = "Place Order Est. S$2.29 (¥11.72)"
        res2 = compute_lambda(q2)
        feat2 = {f["name"]: f["weight"] for f in res2["features"]}
        self.assertEqual(res2["score"], 14)
        self.assertEqual(feat2.get("micro_currency_amount"), 4)
        self.assertNotIn("currency_amount", feat2)

        q3 = "Should I pay S$50 for this tool?"
        res3 = compute_lambda(q3)
        feat3 = {f["name"]: f["weight"] for f in res3["features"]}
        self.assertEqual(feat3.get("currency_amount"), 20)
        self.assertGreaterEqual(res3["score"], 30)

        q4 = "Contract for S$1,500"
        res4 = compute_lambda(q4)
        feat4 = {f["name"]: f["weight"] for f in res4["features"]}
        self.assertEqual(feat4.get("currency_amount"), 20)
        self.assertGreaterEqual(res4["score"], 30)


if __name__ == "__main__":
    unittest.main()

