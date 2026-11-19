"""Tests for hook_meta_awareness_gate.py v3 — structural trigger classes T1-T5.

Covers: per-class positives across >=6 domains, the 12 golden historical cases
(known-answer reads from the corpus), negative controls (routine ops must not
fire), and the T4-only negative-guard suppression rule.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "hook_meta_awareness_gate.py"

spec = importlib.util.spec_from_file_location("meta_gate", HOOK_PATH)
meta_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(meta_gate)


def fired(prompt: str):
    return meta_gate.classify(prompt)


# ---------------------------------------------------------------- T1 INBOUND
@pytest.mark.parametrize("prompt", [
    "why would the landlord suddenly offer a discount on renewal?",
    "HR scheduled a meeting with no agenda — what does this mean?",
    "what's the real reason he took this route?",
    "she hasn't replied for three days",
    "he left me on read again",
    "am I missing something in this contract clause?",
])
def test_t1_inbound_fires(prompt):
    assert "T1-INBOUND" in fired(prompt)


# --------------------------------------------------------------- T2 OUTBOUND
@pytest.mark.parametrize("prompt", [
    "should I post this take on EDMW?",
    "thinking of inviting my coursemate to the wedding",
    "before I send this quote to the client, sanity check it",
    "I invited him to the wedding and he got very angry",  # retro decode
    "should I sign the tenancy agreement today?",
    "how will this come across if I share it in the group chat?",
])
def test_t2_outbound_fires(prompt):
    assert "T2-OUTBOUND" in fired(prompt)


# ---------------------------------------------------------------- T3 VERDICT
@pytest.mark.parametrize("prompt", [
    "is this okay that he texted my client directly?",
    "that comment she made — wasn't it inappropriate?",
    "how could he say that in front of everyone",
    "am i being pryce about this?",
])
def test_t3_verdict_fires(prompt):
    assert "T3-VERDICT" in fired(prompt)


# --------------------------------------------------------------- T4 RESOURCE
@pytest.mark.parametrize("prompt", [
    "should I buy the Cornell air fryer at the promo price?",
    "is the ETB worth it at $130?",
    "should I subscribe to TradingView premium?",
    "should I book the Genting trip for the poker series?",
    "is this a fair price for the FlexSim job?",
])
def test_t4_resource_fires(prompt):
    assert "T4-RESOURCE" in fired(prompt)


# ------------------------------------------------------------------- T5 FELT
@pytest.mark.parametrize("prompt", [
    "I feel like the market has to bounce here",
    "it seems like they respect me now",
    "obviously she wants me there",
    "my gut says this dip is the bottom",
    "felt like we really connected at the gym",
])
def test_t5_felt_fires(prompt):
    assert len(fired(prompt)) > 0  # T5 or co-fired class


# ---------------------------------------------------- T6 INTAKE-AUTHORITY
@pytest.mark.parametrize("prompt", [
    "taking on a new capstone project for Coventry uni",
    "the examiner is a veteran logistics director",
    "what business idea should for this capstone project?",
    "quoting a new assignment for an engineering professor",
])
def test_t6_intake_fires(prompt):
    assert "T6-INTAKE-AUTHORITY" in fired(prompt)


# ------------------------------------------------- T7 END-USER-CAPABILITY
@pytest.mark.parametrize("prompt", [
    "the student will present this capstone live next week",
    "she doesn't know what CAGR means and has no finance background",
    "client is anxious about the presentation and defense",
    "please make the speaker notes not so cheem and explain simply",
    "this deliverable is for a non-technical client",
])
def test_t7_capability_fires(prompt):
    assert "T7-END-USER-CAPABILITY" in fired(prompt)


# ------------------------------------------------- Golden historical cases
#
# Known-answer reads: each case carries the exact set of classes it must
# produce, not merely "something fired".
#
# The previous form asserted `len(fired(prompt)) > 0`, which made the suite
# unable to detect a change in *which* class fires. 755486a rewrote every one
# of these prompts to sanitize names — one case changed scenario entirely, from
# a tournament final round to a last week at a job — and the suite stayed green
# because it never checked a classification. A calibration suite that cannot
# detect recalibration is decoration.
#
# These are golden files: when the gate legitimately changes a classification,
# update the expected set here in the same commit, deliberately.
GOLDEN = {
    "relational-inbound":  ("felt like we really connected — why hasn't he texted back?",
                            {"T1-INBOUND", "T5-FELT"}),
    "wedding-invite":      ("I invited a coursemate to the wedding and he got very angry, he thought he was a table filler",
                            {"T2-OUTBOUND"}),
    "employment-pip":      ("HR put me on a PIP but says it's for my growth — what does it mean?",
                            {"T1-INBOUND"}),
    "shorted-invoice":     ("the client's payment came in $20 short, am I missing something or just a mistake?",
                            {"T1-INBOUND"}),
    "public-callout":      ("should I call out this coach publicly? what he did looks inappropriate",
                            {"T2-OUTBOUND"}),
    "travel-commit":       ("should I book the casino trip for the poker series?",
                            {"T4-RESOURCE"}),
    "trading-hot-streak":  ("the strategy is printing — I feel like this edge is real, should I scale up?",
                            {"T4-RESOURCE", "T5-FELT"}),
    "collectible-fomo":    ("are these boxes worth it at $80? feels like they'll only go up",
                            {"T4-RESOURCE"}),
    "consumer-promo":      ("should I buy the air fryer at the promo price?",
                            {"T4-RESOURCE"}),
    "tail-risk-denial":    ("everyone says the volcano tour is perfectly safe, obviously nothing will happen",
                            {"T5-FELT"}),
    "harsh-feedback":      ("the reviewer was harsh with me again — is that okay or is it just cruel?",
                            {"T3-VERDICT"}),
    "confession-timing":   ("it's my last week here — should I tell her how I actually feel?",
                            {"T2-OUTBOUND"}),
    # v3.1 golden cases — covering bare-narration, open-verb, Singlish, felt-evidence
    "bare-narration-retrench":  ("received the retrenchment letter today, they say it is not performance",
                                 {"T1-INBOUND"}),
    "bare-narration-boss":      ("boss says need to talk later about my role",
                                 {"T1-INBOUND"}),
    "bare-narration-landlord":  ("landlord says he needs to renovate the unit next month",
                                 {"T1-INBOUND"}),
    "bare-narration-distant":   ("she is being distant lately",
                                 {"T1-INBOUND"}),
    "counterparty-short":       ("payment came in 50 short of the quoted amount",
                                 {"T1-INBOUND"}),
    "open-verb-raise":          ("thinking about asking for a raise during the review",
                                 {"T2-OUTBOUND"}),
    "open-verb-propose":        ("I am going to propose to her at the dinner",
                                 {"T2-OUTBOUND"}),
    "singlish-jiak-zua":        ("should i just jiak zua and take the transfer to the SG office",
                                 {"T2-OUTBOUND"}),
    "singlish-reply":           ("later i reply him or wait better",
                                 {"T2-OUTBOUND"}),
    "felt-off":                 ("this deal feels off somehow",
                                 {"T5-FELT"}),
    "counterparty-pushback":    ("the client is pushing back hard on the quote",
                                 {"T1-INBOUND"}),
    # v3.2 golden cases — intake authority over-fitting and end-user capability mismatch
    "intake-authority-cv":      ("new capstone project intake: the examiner is a veteran SCM director",
                                 {"T6-INTAKE-AUTHORITY"}),
    "end-user-anxiety":         ("the student has to present live and she doesn't know what CAGR means",
                                 {"T7-END-USER-CAPABILITY"}),
}


@pytest.mark.parametrize("case,prompt,expected", [(k, p, e) for k, (p, e) in GOLDEN.items()])
def test_golden_cases_classify(case, prompt, expected):
    actual = set(fired(prompt))
    assert actual == expected, (
        f"golden case '{case}' now classifies as {sorted(actual) or '[]'}, "
        f"expected {sorted(expected)}. If the gate changed on purpose, update "
        f"GOLDEN in this commit."
    )


def test_golden_coverage_spans_all_classes():
    """The golden set must exercise every trigger class, or it is not calibration."""
    covered = set().union(*(expected for _, expected in GOLDEN.values()))
    assert covered == {"T1-INBOUND", "T2-OUTBOUND", "T3-VERDICT", "T4-RESOURCE", "T5-FELT", "T6-INTAKE-AUTHORITY", "T7-END-USER-CAPABILITY"}, (
        f"golden set only exercises {sorted(covered)}"
    )


# --------------------------------------------------------- Negative controls
@pytest.mark.parametrize("prompt", [
    "reconcile the June statement against Myfxbook",
    "rebuild the Excel tracker and sync balances to v3.25.0",
    "compile the case study index",
    "fix the failing pytest in test_boot.py",
    "update the changelog for v9.9.7",
    "list the files in .agent/skills",
    # v3.1: routine-ops uses of institutional nouns (must not false-fire)
    "update the HR policy doc for Q3",
    "compile the retrenchment stats for the report",
    "search for HR retrenchment policy templates",
    "rename the performance review template",
    "refactor the landlord contract module",
])
def test_negatives_do_not_fire(prompt):
    assert fired(prompt) == []


def test_negative_guard_suppresses_t4_only():
    # Routine-ops context + a T4-only match -> suppressed by design.
    prompt = "reconcile the statement, then tell me if the surplus is worth topping up"
    assert fired(prompt) == []


# ------------------------------------------------------------ Hook contract
def test_hook_never_blocks_and_injects():
    """End-to-end: run as the harness does; malformed input exits 0 silently."""
    env = {**os.environ, "ATHENA_TELEMETRY_DISABLE": "1"}
    ok = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps({"prompt": "should I post this on EDMW?"}),
        capture_output=True, text=True, env=env,
    )
    assert ok.returncode == 0
    assert "META-AWARENESS GATE" in ok.stdout
    assert "T2-OUTBOUND" in ok.stdout

    bad = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input="not json", capture_output=True, text=True, env=env,
    )
    assert bad.returncode == 0
    assert bad.stdout == ""


def test_telemetry_disable_env_prevents_invocation_log_writes(tmp_path: Path):
    """ATHENA_TELEMETRY_DISABLE=1 prevents pytest/subprocess fires from polluting invocations.jsonl."""
    athena_dir = tmp_path / ".athena"
    athena_dir.mkdir()
    inv_file = athena_dir / "invocations.jsonl"
    env = {**os.environ, "ATHENA_TELEMETRY_DISABLE": "1"}
    res = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps({"prompt": "should I post this publicly?"}),
        cwd=str(tmp_path),
        capture_output=True, text=True, env=env,
    )
    assert res.returncode == 0
    assert "META-AWARENESS GATE" in res.stdout
    assert not inv_file.exists(), "ATHENA_TELEMETRY_DISABLE=1 must skip writing invocations.jsonl"


def test_t1_sla_warranty_cap_and_t4_build_vs_buy_fire():
    """General structural act-grammar catches SLA caps (T1) and multi-month build bets (T4)."""
    assert "T4-RESOURCE" in fired("Should I spend 6 months building a custom ERP for our 12-person logistics company?")
    assert "T1-INBOUND" in fired("Review this vendor SLA: 99.9% uptime with service credits capped at 10% of monthly fees.")


def test_reminder_is_question_framed_and_bounded():
    text = meta_gate.REMINDER_TEMPLATE
    assert text.count("?") >= 6          # ask-don't-tell framing
    assert len(text.splitlines()) <= 18  # injection-fatigue bound


def test_mcp_meta_awareness_check_parity():
    """Verify FastMCP tool returns correct injection payload."""
    from athena.mcp_server import meta_awareness_check

    # FastMCP 2.x wraps @mcp.tool functions in a FunctionTool object whose
    # underlying callable is exposed as `.fn`. Fall back to the object itself so
    # the test survives a FastMCP API change in either direction.
    check = getattr(meta_awareness_check, "fn", meta_awareness_check)

    res = check("should I post this on EDMW?")
    assert "T2-OUTBOUND" in res["fired"]
    assert res["injection"] is not None
    assert "META-AWARENESS GATE" in res["injection"]

    res_clean = check("fix the failing pytest in test_boot.py")
    assert res_clean["fired"] == []
    assert res_clean["injection"] is None


def test_governance_skip_auditor():
    """Verify check_governance_skip.py runs without error and integrates GateTelemetryAnalyzer."""
    script_path = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "check_governance_skip.py"
    ok = subprocess.run(
        [sys.executable, str(script_path), "--days", "7"],
        capture_output=True, text=True,
    )
    assert ok.returncode == 0
    assert "Governance Telemetry Audit" in ok.stdout
    assert "Compliance Band:" in ok.stdout or "Status:            NO_DATA" in ok.stdout


def test_hook_script_ssot_parity_and_execution():
    """Verify hook_meta_awareness_gate.py has 100% SSOT parity with athena.core.gate_meta (TD-069b)."""
    import importlib.util
    import json

    hook_path = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "hook_meta_awareness_gate.py"
    spec = importlib.util.spec_from_file_location("hook_meta_awareness_gate", hook_path)
    hook_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_mod)

    # 1. Structural SSOT identity
    assert hook_mod.CLASSES is meta_gate.CLASSES
    assert hook_mod.NEGATIVE is meta_gate.NEGATIVE
    assert hook_mod.REMINDER_TEMPLATE is meta_gate.REMINDER_TEMPLATE
    assert hook_mod.classify is meta_gate.classify

    # 2. Subprocess execution verification across all trigger classes + negative guards
    test_cases = [
        ("I was let go from my job today", ["T1-INBOUND"]),
        ("Manager scheduled a 1:1 with no agenda out of the blue", ["T1-INBOUND"]),
        ("should I post this on LinkedIn?", ["T2-OUTBOUND"]),
        ("is this acceptable or creepy?", ["T3-VERDICT"]),
        ("should I buy the ThinkPad T14 Gen 3?", ["T4-RESOURCE"]),
        ("it feels like the market has to bounce here", ["T5-FELT"]),
        ("starting a new capstone with an examiner who wants machine vision", ["T6-INTAKE-AUTHORITY"]),
        ("the client is anxious about presenting and has no background", ["T7-END-USER-CAPABILITY"]),
        ("patut tandatangan kontrak atau tidak", ["T8-MULTILINGUAL"]),
        ("老板让我辞职", ["T8-MULTILINGUAL"]),
        # Negative routine-ops suppression
        ("reconcile the portfolio balance sheet with pytest", []),
    ]

    env = {**os.environ, "ATHENA_TELEMETRY_DISABLE": "1"}
    for prompt, expected_classes in test_cases:
        res = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps({"prompt": prompt}),
            capture_output=True,
            text=True,
            env=env,
        )
        assert res.returncode == 0
        if expected_classes:
            assert "<system-reminder>" in res.stdout
            assert "META-AWARENESS GATE" in res.stdout
            for exp in expected_classes:
                assert exp in res.stdout
        else:
            assert res.stdout == ""


