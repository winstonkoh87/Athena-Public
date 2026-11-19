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
