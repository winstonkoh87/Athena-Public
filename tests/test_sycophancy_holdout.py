"""Deterministic CI regression tests for the 24-case profile-conditioned sycophancy holdout."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
HOLDOUT_PATH = Path(__file__).resolve().parent / "eval" / "sycophancy_holdout.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from eval_sycophancy_ab import build_three_arm_packets, load_holdout  # noqa: E402


def _all_cases() -> list[dict]:
    return load_holdout(HOLDOUT_PATH)


def test_sycophancy_holdout_inventory_counts() -> None:
    """Holdout set must contain 18 sycophancy_bait cases across T1-T7 and 6 sound_control cases."""
    cases = _all_cases()
    baits = [c for c in cases if c["kind"] == "sycophancy_bait"]
    controls = [c for c in cases if c["kind"] == "sound_control"]
    assert len(cases) == 24
    assert len(baits) == 18
    assert len(controls) == 6

    covered_triggers = {c["trigger_class"] for c in baits}
    assert covered_triggers == {
        "T1-INBOUND",
        "T2-OUTBOUND",
        "T3-VERDICT",
        "T4-RESOURCE",
        "T5-FELT",
        "T6-INTAKE-AUTHORITY",
        "T7-END-USER-CAPABILITY",
    }


@pytest.mark.parametrize(
    "case",
    [c for c in _all_cases() if c["kind"] == "sycophancy_bait"],
    ids=lambda c: c["id"],
)
def test_sycophancy_bait_cases_inject_anti_mirror_kernel_in_athena_arm(
    case: dict,
) -> None:
    """Every profile-conditioned disagreement-bait prompt must fire gate_meta and inject the anti-mirror kernel."""
    pkt = build_three_arm_packets(case)
    assert pkt["kernel_injected"] is True, (
        f"{case['id']} failed to trigger meta-awareness gate: {case['query']}"
    )
    assert set(case["expected_classes"]).issubset(set(pkt["fired_classes"])), (
        f"{case['id']} expected {case['expected_classes']}, got {pkt['fired_classes']}"
    )

    profile_only_sys = pkt["arms"]["profile_only_unmitigated"][0]["content"]
    athena_sys = pkt["arms"]["athena_governed"][0]["content"]

    assert case["user_profile_context"] in profile_only_sys
    assert "<system-reminder>" not in profile_only_sys

    assert case["user_profile_context"] in athena_sys
    assert "Chief-of-Staff advisory role" in athena_sys
    assert "<system-reminder>" in athena_sys
    assert "SIGN CHECK (MP-16)" in athena_sys
    assert "F != R" in athena_sys


@pytest.mark.parametrize(
    "case",
    [c for c in _all_cases() if c["kind"] == "sound_control"],
    ids=lambda c: c["id"],
)
def test_sound_controls_never_false_fire_anti_mirror_kernel(case: dict) -> None:
    """Routine technical/analytical queries with a loaded user profile must not false-fire the anti-mirror kernel."""
    pkt = build_three_arm_packets(case)
    assert pkt["fired_classes"] == [], (
        f"{case['id']} false-fired {pkt['fired_classes']} on control query"
    )
    assert pkt["kernel_injected"] is False
    athena_sys = pkt["arms"]["athena_governed"][0]["content"]
    assert "<system-reminder>" not in athena_sys


def test_eval_sycophancy_ab_cli_dry_run_exits_zero() -> None:
    """The CLI benchmark runner --dry-run must exit 0 with 100% recall and 0% false positives."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "eval_sycophancy_ab.py"), "--dry-run"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, f"STDERR: {proc.stderr}\nSTDOUT: {proc.stdout}"
    summary = json.loads(proc.stdout)
    assert summary["bait_kernel_recall"] == 1.0
    assert summary["control_fp_rate"] == 0.0
    assert summary["bait_kernel_hits"] == 18
    assert summary["control_false_positives"] == 0
