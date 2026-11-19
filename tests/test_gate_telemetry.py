"""Tests for Gate Telemetry & Fire-Rate Monitoring (TD-069b M2).

Validates:
1. Parsing of .athena/invocations.jsonl telemetry stream.
2. Multi-window aggregations (7d, 14d, 30d).
3. Per-class distribution (T1-INBOUND through T5-FELT).
4. Compliance band evaluation (target: 10%-30%).
5. Integration with AgentGate cross-harness interception.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from athena.core.gate import AgentGate
from athena.intelligence.gate_telemetry import (
    GateTelemetryAnalyzer,
    TelemetrySummary,
    evaluate_substance_decode_adherence,
)


@pytest.fixture
def sample_telemetry(tmp_path: Path) -> Path:
    log_file = tmp_path / "invocations.jsonl"
    now = datetime.now(timezone.utc)

    records = [
        # Prompts (user turns)
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=2)).isoformat()},
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=3)).isoformat()},
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=4)).isoformat()},
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=5)).isoformat()},
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=6)).isoformat()},
        {"type": "prompt", "trigger": "UserPromptSubmit", "ts": (now - timedelta(days=20)).isoformat()},
        # Meta gate fires inside 7-day window
        {
            "type": "hook",
            "name": "meta_awareness_gate",
            "classes": ["T1-INBOUND"],
            "trigger": "UserPromptSubmit",
            "ts": (now - timedelta(days=2)).isoformat(),
        },
        # Outside 7-day window
        {
            "type": "hook",
            "name": "meta_awareness_gate",
            "classes": ["T2-OUTBOUND", "T4-RESOURCE"],
            "trigger": "UserPromptSubmit",
            "ts": (now - timedelta(days=20)).isoformat(),
        },
    ]

    with open(log_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    return log_file


def test_telemetry_analyzer_windowing(sample_telemetry: Path):
    analyzer = GateTelemetryAnalyzer(telemetry_path=sample_telemetry)
    summary_7d: TelemetrySummary = analyzer.analyze(window_days=7)

    assert summary_7d.total_prompts == 5
    assert summary_7d.total_fires == 1
    assert summary_7d.fire_rate_pct == pytest.approx(20.0, 0.1)
    assert summary_7d.compliance_band == "NORMAL (10-30%)"
    assert summary_7d.class_counts.get("T1-INBOUND") == 1
    assert summary_7d.class_counts.get("T2-OUTBOUND", 0) == 0


def test_telemetry_analyzer_30d_window(sample_telemetry: Path):
    analyzer = GateTelemetryAnalyzer(telemetry_path=sample_telemetry)
    summary_30d: TelemetrySummary = analyzer.analyze(window_days=30)

    assert summary_30d.total_prompts == 6
    assert summary_30d.total_fires == 2
    assert summary_30d.fire_rate_pct == pytest.approx(33.3, 0.1)
    assert summary_30d.compliance_band == "SATURATED (>30%)"
    assert summary_30d.class_counts.get("T1-INBOUND") == 1
    assert summary_30d.class_counts.get("T2-OUTBOUND") == 1
    assert summary_30d.class_counts.get("T4-RESOURCE") == 1


def test_telemetry_ascii_report(sample_telemetry: Path):
    analyzer = GateTelemetryAnalyzer(telemetry_path=sample_telemetry)
    report = analyzer.render_ascii_report(window_days=7)

    assert "Meta-Awareness Gate Telemetry" in report
    assert "Fire-Rate: 20.0%" in report
    assert "Band: NORMAL (10-30%)" in report
    assert "T1-INBOUND" in report
    # Ensure zero LaTeX math delimiters
    assert "$" not in report
    assert r"\(" not in report


def test_agent_gate_logging_integration(tmp_path: Path, monkeypatch):
    invocations_path = tmp_path / "invocations.jsonl"
    monkeypatch.setattr(
        "athena.core.gate.get_invocations_path",
        lambda root: invocations_path,
    )

    gate = AgentGate(workspace_root=tmp_path)
    prompt = "why did the client suddenly back out of the contract?"
    reminder = gate.intercept_prompt(prompt)

    assert reminder is not None
    assert "META-AWARENESS GATE" in reminder
    assert invocations_path.exists()

    with open(invocations_path, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]

    assert len(lines) == 1
    assert lines[0]["type"] == "hook"
    assert lines[0]["name"] == "meta_awareness_gate"
    assert "T1-INBOUND" in lines[0]["classes"]


def test_substance_decode_output_contract_pass():
    """Verify that an output containing prior, discriminators, sign check, and payoff action passes."""
    compliant_text = """
    ## Strategic Substance Decode
    - Prior: In corporate contracting arenas, the base rate of counterparty re-negotiation is 70%.
    - Observable Discriminators: The counterparty introduced a non-standard clawback clause on day 30.
    - Sign Check: Running MP-16 sign check against inflating reads (they respect us) vs deflating reads.
    - Payoff-Weighted Action: The asymmetric payoff favors requiring an upfront cash escrow (EV = +2.50).
    """
    res = evaluate_substance_decode_adherence(compliant_text)
    assert res["contract_satisfied"] is True
    assert res["adherence_score"] == 1.0
    assert res["verdict"] == "PASS"
    assert set(res["elements_present"]) == {"prior", "discriminators", "sign_check", "payoff_action"}
    assert len(res["missing_elements"]) == 0


def test_substance_decode_output_contract_partial_and_fail():
    """Verify partial compliance and complete failure cases."""
    # Only prior and discriminators (2/4 = 50% -> PARTIAL, satisfied False)
    partial_text = "The arena base rate is low. Observable discriminators confirm this pattern."
    res_partial = evaluate_substance_decode_adherence(partial_text)
    assert res_partial["contract_satisfied"] is False
    assert res_partial["adherence_score"] == 0.5
    assert res_partial["verdict"] == "PARTIAL"
    assert "sign_check" in res_partial["missing_elements"]
    assert "payoff_action" in res_partial["missing_elements"]

    # Generic text (0/4 -> FAIL)
    empty_text = "Here is what I found regarding the contract."
    res_fail = evaluate_substance_decode_adherence(empty_text)
    assert res_fail["contract_satisfied"] is False
    assert res_fail["adherence_score"] == 0.0
    assert res_fail["verdict"] == "FAIL"
    assert len(res_fail["missing_elements"]) == 4


def test_gate_analyzer_output_contract_report():
    """Verify analyzer ASCII output contract rendering."""
    analyzer = GateTelemetryAnalyzer()
    text = (
        "Base rate prior indicates 80% default. Observable discriminators: 3 missed calls. "
        "Sign check: anti-flattery. Payoff-weighted action: enforce strict collateral."
    )
    report = analyzer.render_contract_report(text)
    assert "Substance-Decode Output Contract Audit" in report
    assert "Verdict:            PASS" in report
    assert "Contract Satisfied: True" in report
    assert "$" not in report
