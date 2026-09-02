import unittest

from athena.tools.web_triggers import (
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


if __name__ == '__main__':
    unittest.main()

