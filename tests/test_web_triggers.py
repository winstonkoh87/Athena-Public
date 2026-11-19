import unittest
from unittest.mock import patch

from athena.tools.web_triggers import (
    is_in_game_optimization_trap,
    is_underspecified_optimization,
    needs_web,
)


class TestWebTriggers(unittest.TestCase):

    def test_needs_web_true_cases(self):
        self.assertEqual(needs_web("current S$/USD rate", "GENERAL"), (True, 'market'))
        self.assertEqual(needs_web("what is the latest SSB cap", "GENERAL"), (True, 'policy'))
        self.assertEqual(needs_web("gold price today", "GENERAL"), (True, 'market'))
        self.assertEqual(needs_web("latest python release", "GENERAL"), (True, 'time_word'))
        self.assertEqual(needs_web("who won the election", "GENERAL"), (True, 'market'))
        self.assertEqual(needs_web("current CPF contribution rates", "GENERAL"), (True, 'policy'))
        self.assertEqual(needs_web("2026 budget changes", "GENERAL"), (True, 'policy'))
        self.assertEqual(needs_web("bitcoin price right now", "GENERAL"), (True, 'market'))
        self.assertEqual(needs_web("latest MAS ruling", "GENERAL"), (True, 'policy'))
        self.assertEqual(needs_web("what is the fed rate", "GENERAL"), (True, 'market'))
        self.assertEqual(needs_web("should I refinance — what's the current SSB cap", "PERSONALISED_DECISION"), (True, 'policy'))
        self.assertEqual(needs_web("upcoming CPI release", "GENERAL"), (True, 'market'))

    def test_needs_web_false_cases(self):
        self.assertEqual(needs_web("what is Protocol 133", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("explain the triple-lock", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("what is my rate floor", "PERSONALISED_DECISION"), (False, 'none'))
        self.assertEqual(needs_web("should I take the deal", "PERSONALISED_DECISION"), (False, 'none'))
        self.assertEqual(needs_web("what did we decide about the assignment", "GENERAL"), (False, 'none'))
        self.assertEqual(needs_web("explain Law #6", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("how does the governance engine work", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("show me session S834", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("what protocols are in cluster 3", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("latest protocol changes", "GENERAL"), (False, 'internal_entity'))
        self.assertEqual(needs_web("my wife said...", "PERSONALISED_DECISION"), (False, 'none'))
        self.assertEqual(needs_web("what is the canonical weight for vectors", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))
        self.assertEqual(needs_web("internal project status check", "SYSTEM_KNOWLEDGE"), (False, 'internal_system'))


class TestUnderspecifiedOptimization(unittest.TestCase):
    """Tests for the underspecified optimization frame detector (DEC-180 / Nudge Test).

    The detector must fire on open optimization questions where no objective
    function is specified, and must NOT fire when the user has pinned the
    utility function (risk tolerance, Kelly, Sharpe, etc.) or when the
    question is a routine lookup.
    """

    # --- TRUE CASES: should detect underspecified optimization ---

    def test_specimen_question_verbatim(self):
        """The exact roulette specimen question that started the audit."""
        self.assertTrue(is_underspecified_optimization(
            "How would you structure your bets to maximise payoff in this game?"
        ))

    def test_maximize_profit(self):
        self.assertTrue(is_underspecified_optimization(
            "How do I maximize profit on this portfolio?"
        ))

    def test_optimise_returns(self):
        """British spelling."""
        self.assertTrue(is_underspecified_optimization(
            "What's the best way to optimise returns here?"
        ))

    def test_structure_portfolio(self):
        self.assertTrue(is_underspecified_optimization(
            "How would you structure your portfolio allocation?"
        ))

    def test_optimal_strategy_to_bet(self):
        self.assertTrue(is_underspecified_optimization(
            "What's the optimal strategy to bet on these outcomes?"
        ))

    def test_best_way_to_allocate(self):
        self.assertTrue(is_underspecified_optimization(
            "What's the best way to allocate capital across these trades?"
        ))

    def test_how_would_you_approach(self):
        self.assertTrue(is_underspecified_optimization(
            "How would you approach this betting problem?"
        ))

    def test_maximize_expected_value(self):
        self.assertTrue(is_underspecified_optimization(
            "How do I maximize expected value in this game?"
        ))

    # --- FALSE CASES: should NOT fire ---

    def test_specified_risk_tolerance(self):
        """Param guard: risk tolerance specified = objective function pinned."""
        self.assertFalse(is_underspecified_optimization(
            "How would you structure your bets to maximise payoff given my risk tolerance is low?"
        ))

    def test_specified_kelly(self):
        """Param guard: Kelly criterion specified."""
        self.assertFalse(is_underspecified_optimization(
            "What's the optimal strategy to bet using Kelly criterion sizing?"
        ))

    def test_specified_sharpe(self):
        """Param guard: Sharpe ratio target specified."""
        self.assertFalse(is_underspecified_optimization(
            "How do I maximize profit while targeting a Sharpe of 2?"
        ))

    def test_specified_utility_function(self):
        """Param guard: utility function explicitly named."""
        self.assertFalse(is_underspecified_optimization(
            "How would you structure your bets assuming a log utility function?"
        ))

    def test_specified_variance_budget(self):
        """Param guard: variance budget specified."""
        self.assertFalse(is_underspecified_optimization(
            "Best way to allocate with a variance budget of 5%?"
        ))

    def test_routine_lookup(self):
        """Routine query — no optimization language."""
        self.assertFalse(is_underspecified_optimization(
            "What is Protocol 133?"
        ))

    def test_personal_decision_no_opt(self):
        """Personal question without optimization framing."""
        self.assertFalse(is_underspecified_optimization(
            "Should I take the deal or walk away?"
        ))

    def test_simple_roi_question(self):
        """Specified surface question — asking for a number, not a strategy."""
        self.assertFalse(is_underspecified_optimization(
            "What's the ROI if I bet $500 on each dozen for 100 rounds?"
        ))


class TestInGameOptimizationTrap(unittest.TestCase):
    """Tests for L0/L1 in-game business optimization & arena-selection detector."""

    def test_in_game_cost_and_wage_optimization_fires(self):
        self.assertTrue(is_in_game_optimization_trap(
            "How do I optimize food costs and reduce worker wages for my kopitiam stall?"
        ))
        self.assertTrue(is_in_game_optimization_trap(
            "How can I survive running a hawker stall with rising rent?"
        ))
        self.assertTrue(is_in_game_optimization_trap(
            "Should we apply the red curve blue curve protocol to find the right game?"
        ))

    def test_code_optimization_and_routine_lookup_do_not_fire(self):
        self.assertFalse(is_in_game_optimization_trap(
            "How do I optimize SQL query latency and reduce memory footprint in Python?"
        ))
        self.assertFalse(is_in_game_optimization_trap("What is Protocol 131?"))

    def test_mcp_context_gate_and_classify_turn_emit_arena_reframe(self):
        from athena.mcp_server import classify_turn, context_gate

        q = "How do I optimize food costs and reduce worker wages for my kopitiam stall?"
        ct = classify_turn(q)
        self.assertTrue(ct["in_game_opt_trap"])

        fake_search = {
            "results": [{"id": "doc1", "content": "test", "rrf_score": 0.05}],
            "user_state": {"rate_floor": "S$150/hr"},
        }
        with (
            patch("athena.tools.meta_pattern_matcher.detect_latent_meta_patterns", return_value=[]),
            patch("athena.tools.search.run_search", return_value=fake_search),
        ):
            cg = context_gate(q, limit=3, web=False)
        self.assertTrue(cg["in_game_opt_trap"])
        self.assertIn("ARENA REFRAME DIRECTIVE", cg["directive"])

        # Non-trap strategic query with meta_frame_required=True emits META-FRAME POSTURE
        q2 = "Compare private equity vs dividend stocks for long-term wealth strategy."
        with (
            patch("athena.tools.meta_pattern_matcher.detect_latent_meta_patterns", return_value=[]),
            patch("athena.tools.search.run_search", return_value=fake_search),
        ):
            cg2 = context_gate(q2, limit=3, web=False)
        self.assertFalse(cg2["in_game_opt_trap"])
        self.assertTrue(cg2["intel_posture"]["meta_frame_required"])
        self.assertIn("META-FRAME POSTURE", cg2["directive"])

    def test_tech_and_saas_business_traps_not_blindly_excluded(self):
        """Technical keywords paired with churn/CAC/pricing traps must not bypass arena triage."""
        self.assertTrue(is_in_game_optimization_trap(
            "My SaaS CAC just doubled after iOS tracking changes; how do I tweak my Meta ads copy?"
        ))
        self.assertTrue(is_in_game_optimization_trap(
            "Write a Python script to scrape competitor prices and match the lowest one automatically."
        ))
        self.assertTrue(is_in_game_optimization_trap(
            "How can I speed up our React dashboard render time? Users are churning."
        ))
        # Pure technical optimization without business/churn/pricing trap stays False
        self.assertFalse(is_in_game_optimization_trap(
            "How do I speed up a Python loop over 100k integers using list comprehension?"
        ))


if __name__ == '__main__':
    unittest.main()

