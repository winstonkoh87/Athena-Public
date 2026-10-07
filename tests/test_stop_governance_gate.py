"""
tests.test_stop_governance_gate
===============================
Unit tests for the Antigravity Stop Lifecycle Governance Gate.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "scripts"))

import stop_governance_gate
from stop_governance_gate import (
    clean_prompt_content,
    evaluate_turn_governance,
    is_trivial_query,
)


class TestStopGovernanceGate(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="athena_gate_tests_"))
        self._orig_gate_decisions_path = getattr(stop_governance_gate, "GATE_DECISIONS_PATH", None)
        self._orig_loop_guard_path = getattr(stop_governance_gate, "LOOP_GUARD_PATH", None)
        self._orig_receipts_path = getattr(stop_governance_gate, "RETRIEVAL_RECEIPTS_PATH", None)
        stop_governance_gate.GATE_DECISIONS_PATH = self.tmp_dir / "gate_decisions.jsonl"
        stop_governance_gate.LOOP_GUARD_PATH = self.tmp_dir / "gate_loop_guard.json"
        stop_governance_gate.RETRIEVAL_RECEIPTS_PATH = self.tmp_dir / "retrieval_receipts.jsonl"

    def tearDown(self):
        if self._orig_gate_decisions_path:
            stop_governance_gate.GATE_DECISIONS_PATH = self._orig_gate_decisions_path
        if self._orig_loop_guard_path:
            stop_governance_gate.LOOP_GUARD_PATH = self._orig_loop_guard_path
        if self._orig_receipts_path:
            stop_governance_gate.RETRIEVAL_RECEIPTS_PATH = self._orig_receipts_path
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_is_trivial_query(self):
        self.assertTrue(is_trivial_query("hi"))
        self.assertTrue(is_trivial_query("thanks"))
        self.assertTrue(is_trivial_query("thank you"))
        self.assertTrue(is_trivial_query("got it"))
        self.assertTrue(is_trivial_query("proceed"))
        self.assertTrue(is_trivial_query("approved"))
        self.assertFalse(is_trivial_query("How should I structure the used car concierge service?"))
        self.assertFalse(is_trivial_query("Analyze our short-gamma variance in FX trading."))

    def test_clean_prompt_content(self):
        raw = """<USER_REQUEST>
What is our current portfolio variance?
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-14T00:53:17+08:00.
</ADDITIONAL_METADATA>"""
        self.assertEqual(clean_prompt_content(raw), "What is our current portfolio variance?")

    def test_trivial_turn_allows_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "thanks"}) + "\n")
            tf.write(json.dumps({"step_index": 1, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "You are welcome!"}) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "allow")

    def test_ungrounded_substantive_turn_blocks_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>Evaluate our short-gamma risk in FX trading.</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Short-gamma risk is very high.",
                "tool_calls": []
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("Triple-Lock Gate", res["reason"])

    def test_grounded_substantive_turn_allows_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>Evaluate our short-gamma risk in FX trading.</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "context_gate", "args": {"query": "FX short-gamma"}}]
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 2,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Based on S736, our risk is bounded by the -S,300 guillotine firewall."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "allow")

    def test_ungrounded_universal_negative_blocks_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>Did Garmin release a Forerunner 570?</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "smart_search", "args": {"query": "Garmin Forerunner 570"}}]
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 2,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Garmin has never made a Forerunner 570 watch."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("Epistemic Grounding Gate", res["reason"])

    def test_crisis_turn_without_referral_blocks_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>I want to die</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "I am here to help you."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("CRISIS REFERRAL REQUIRED", res["reason"])

    def test_crisis_turn_with_referral_hotlines_allows_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>I want to die</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Please reach out to SOS at 1-767 and IMH at 6389 2222 immediately."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "allow")

    def test_crisis_turn_with_referral_header_protocol_509_allows_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>I want to die</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "🚨 Protocol 509: Life-safety support resources are available."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "allow")

    def test_crisis_turn_with_referral_header_findahelpline_allows_stop(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>I want to die</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "International support is available via https://findahelpline.com."
            }) + "\n")
            temp_path = tf.name

        res = evaluate_turn_governance(temp_path)
        self.assertEqual(res["decision"], "allow")

    def test_codeql_url_substring_sanitization_ast_clean(self):
        """CodeQL py/incomplete-url-substring-sanitization AST guard.
        Ensures no StringLiteral that looks like a domain/URL is checked using
        'in', 'startswith', or 'endswith', which triggers CodeQL alert #47 (CWE-20).
        """
        import ast
        import re

        common_tlds = r"com|org|edu|gov|uk|net|io"
        url_regex = re.compile(rf"(?i)^([a-z]*:?//)?\.?([a-z0-9-]+\.)+({common_tlds})(:[0-9]+)?/?$")
        http_url_regex = re.compile(r"(?i)^https?://([a-z0-9-]+\.)+([a-z]+)(:[0-9]+)?/?$")

        def looks_like_url(s: str) -> bool:
            return bool(url_regex.match(s) or http_url_regex.match(s))

        class SubstringSanitizationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.violations = []

            def visit_Compare(self, node):
                for op, comparator in zip(node.ops, node.comparators, strict=False):
                    if isinstance(op, ast.In):
                        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str) and looks_like_url(node.left.value):
                            self.violations.append((node.lineno, node.left.value))
                        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str) and looks_like_url(comparator.value):
                            self.violations.append((node.lineno, comparator.value))
                self.generic_visit(node)

            def visit_Call(self, node):
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("startswith", "endswith")
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                    and looks_like_url(node.args[0].value)
                ):
                    self.violations.append((node.lineno, node.args[0].value))
                self.generic_visit(node)

        script_path = REPO_ROOT / "examples" / "scripts" / "stop_governance_gate.py"
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
        visitor = SubstringSanitizationVisitor()
        visitor.visit(tree)
        self.assertEqual(
            visitor.violations,
            [],
            f"CodeQL incomplete-url-substring-sanitization pattern detected in {script_path}: {visitor.violations}",
        )


if __name__ == "__main__":
    unittest.main()
