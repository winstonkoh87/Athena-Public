"""Tests for athena.intelligence.calibration and MCP calibration_status."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))


def test_calibration_unconfigured_missing_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from athena.intelligence.calibration import get_calibration_status

    missing = tmp_path / "missing_CALIBRATION_LEDGER.md"
    monkeypatch.setenv("ATHENA_CAL_LEDGER_PATH", str(missing))
    res = get_calibration_status()
    assert res["status"] == "unconfigured"
    assert res["resolved"] == 0
    assert res["brier"] is None
    assert res["overdue_ids"] == []


def test_calibration_scores_brier_overdue_and_domains(tmp_path: Path) -> None:
    from athena.intelligence.calibration import (
        format_calibration_report,
        get_calibration_status,
    )

    ledger = tmp_path / "CALIBRATION_LEDGER.md"
    ledger.write_text(
        """# Calibration Ledger

### CAL-001
- **Claim**: Feature A launches on schedule
- **Probability**: 0.80
- **Deadline**: 2026-01-10
- **Domain**: technical
- **Source**: session 2026-01-01
- **Outcome**: true
- **Resolved**: 2026-01-11

### CAL-002
- **Claim**: Trade B clears target
- **Probability**: 0.80
- **Deadline**: 2026-01-15
- **Domain**: trading
- **Source**: session 2026-01-02
- **Outcome**: false
- **Resolved**: 2026-01-16

### CAL-003
- **Claim**: Overdue unresolved prediction
- **Probability**: 0.60
- **Deadline**: 2026-02-01
- **Domain**: career
- **Source**: session 2026-01-20
- **Outcome**: pending
- **Resolved**: -

### CAL-004
- **Claim**: Future pending prediction
- **Probability**: 0.70
- **Deadline**: 2099-12-31
- **Domain**: technical
- **Source**: session 2026-02-01
- **Outcome**: pending
- **Resolved**: -
""",
        encoding="utf-8",
    )

    res = get_calibration_status(ledger_path=ledger, as_of="2026-11-19")
    assert res["status"] == "ok"
    assert res["total"] == 4
    assert res["resolved"] == 2
    assert res["pending"] == 2
    # ((0.8-1)^2 + (0.8-0)^2) / 2 = (0.04 + 0.64) / 2 = 0.34
    assert res["brier"] == pytest.approx(0.34, abs=1e-4)
    assert res["overdue_ids"] == ["CAL-003"]
    assert res["upcoming_ids"] == ["CAL-004"]
    assert res["by_domain"]["technical"]["brier"] == pytest.approx(0.04, abs=1e-4)
    assert res["by_domain"]["trading"]["brier"] == pytest.approx(0.64, abs=1e-4)

    report = format_calibration_report(res)
    assert "ATHENA CALIBRATION REPORT" in report
    assert "CAL-003" in report
    assert "$" not in report


def test_mcp_calibration_status_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from athena.core.permissions import TOOL_REGISTRY, get_permissions
    from athena.mcp_server import calibration_status

    assert "calibration_status" in TOOL_REGISTRY
    perms = get_permissions()
    perms.set_secret_mode(False)

    missing = tmp_path / "none.md"
    monkeypatch.setenv("ATHENA_CAL_LEDGER_PATH", str(missing))

    fn = getattr(calibration_status, "fn", calibration_status)
    out = fn()
    assert isinstance(out, dict)
    assert out["status"] == "unconfigured"
    assert "brier" in out


def test_fit_linear_shrinkage_overconfident_data() -> None:
    from athena.intelligence.calibration import fit_linear_shrinkage

    preds = [
        {"probability": 0.90, "outcome": "true" if i < 7 else "false"}
        for i in range(10)
    ]
    # (0.9 - 0.5) = 0.4; mean(actual - 0.5) = 0.7 - 0.5 = 0.2 -> optimal k = 0.2 / 0.4 = 0.5
    fit = fit_linear_shrinkage(preds)
    assert fit["k"] == pytest.approx(0.5, abs=1e-4)
    assert fit["shrunk_brier"] < fit["raw_brier"]
    assert fit["n"] == 10
    assert fit["sample_reliable"] is False


def test_fit_linear_shrinkage_well_calibrated_and_reliable_n() -> None:
    from athena.intelligence.calibration import MIN_RELIABLE_N, fit_linear_shrinkage

    assert MIN_RELIABLE_N == 30
    # 30 predictions at 0.80 with exactly 24 hits (80% hit rate) -> k == 1.0
    preds = [
        {"probability": 0.80, "outcome": "true" if i < 24 else "false"}
        for i in range(30)
    ]
    fit = fit_linear_shrinkage(preds)
    assert fit["k"] == pytest.approx(1.0, abs=1e-4)
    assert fit["n"] == 30
    assert fit["sample_reliable"] is True


def test_fit_linear_shrinkage_constant_half_edge_case() -> None:
    from athena.intelligence.calibration import fit_linear_shrinkage

    preds = [{"probability": 0.50, "outcome": "true"}, {"probability": 0.50, "outcome": "false"}]
    fit = fit_linear_shrinkage(preds)
    assert fit["k"] == 1.0
    assert fit["n"] == 2
    assert fit["sample_reliable"] is False


def test_format_calibration_report_shows_shrinkage_and_low_n_caveat(tmp_path: Path) -> None:
    from athena.intelligence.calibration import (
        format_calibration_report,
        get_calibration_status,
    )

    ledger = tmp_path / "CALIBRATION_LEDGER.md"
    ledger.write_text(
        """# Calibration Ledger

### CAL-001
- **Claim**: Overconfident claim A
- **Probability**: 0.90
- **Deadline**: 2026-01-10
- **Domain**: technical
- **Outcome**: true
- **Resolved**: 2026-01-11

### CAL-002
- **Claim**: Overconfident claim B
- **Probability**: 0.90
- **Deadline**: 2026-01-15
- **Domain**: technical
- **Outcome**: false
- **Resolved**: 2026-01-16
""",
        encoding="utf-8",
    )
    res = get_calibration_status(ledger_path=ledger, as_of="2026-11-28")
    assert res["sample_reliable"] is False
    assert res["shrinkage"]["k"] == pytest.approx(0.0, abs=1e-4)

    report = format_calibration_report(res)
    assert "$" not in report
    assert "Shrinkage k" in report
    assert "n=2 < 30" in report


def test_frame_open_emits_non_breaking_overconfidence_advisory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json

    from athena.core.permissions import get_permissions
    from athena.intelligence import frame_ledger
    from athena.mcp_server import frame_open

    ledger = tmp_path / "CALIBRATION_LEDGER.md"
    ledger.write_text(
        """# Calibration Ledger

### CAL-001
- **Claim**: Overconfident claim A
- **Probability**: 0.90
- **Deadline**: 2026-01-10
- **Domain**: technical
- **Outcome**: true
- **Resolved**: 2026-01-11

### CAL-002
- **Claim**: Overconfident claim B
- **Probability**: 0.90
- **Deadline**: 2026-01-15
- **Domain**: technical
- **Outcome**: false
- **Resolved**: 2026-01-16
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("ATHENA_CAL_LEDGER_PATH", str(ledger))
    monkeypatch.setattr(frame_ledger, "DEFAULT_LEDGER", tmp_path / "frames.jsonl")

    perms = get_permissions()
    perms.set_secret_mode(False)

    fn = getattr(frame_open, "fn", frame_open)
    payload = json.dumps({
        "literal_request": "Ship calibration advisory test",
        "candidate_reframe": "Attach non-blocking overconfidence warning at high priors",
        "discriminating_test": "Verify frame_open returns ok=True with DEC-140 advisory",
        "review_date": "2026-12-31",
        "reframe_prior": 0.85,
        "reversibility": 4,
    })
    out = fn(payload, session="test-cal", lite=True)
    assert out["ok"] is True
    assert "overconfidence_advisory" in out
    adv = out["overconfidence_advisory"]
    assert adv["max_prior"] == pytest.approx(0.85, abs=1e-4)
    assert "DEC-140" in adv["message"]
