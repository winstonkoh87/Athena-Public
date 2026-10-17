"""
tests.test_frame_ledger
=======================

Tests for the frame-contract enforcement layer (Cluster #15).

Two suites in one file:

1. CONTRACT TESTS - each rule R1-R10 must reject its target defect and must
   NOT reject a well-formed frame (specificity, not just sensitivity).
2. SEEDED-DEFECT AUDIT - the auditor's own calibration. A validator that
   never fires and a validator that always fires are equally worthless, so
   both error rates are measured here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# src-layout: make `athena` importable when the package is not installed.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.intelligence.frame_ledger import (  # noqa: E402
    ADOPTION_MARKERS,
    FrameLedger,
    FrameRecord,
    Hypothesis,
    ValidationError,
    build_frame,
    calibration_report,
    compute_evi,
    deterministic_frame_id,
    scan_adoption,
    score_frames,
    validate_frame,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def valid_payload(**overrides) -> dict:
    """A frame that SHOULD pass. Every defect test mutates exactly one field."""
    payload = {
        "literal_request": "Give me a productivity schedule to stop procrastinating on client work",
        "candidate_reframe": (
            "Procrastination is a risk-mitigation move by a protective part: shipping exposes "
            "work to appraisal, so delay protects against a failure/defectiveness judgement."
        ),
        "tier": "ULTRA",
        "mode": 3,
        "session": "S-SEED-01",
        "evidence_for": "Three separate abandonments occurred within 48h of a deliverable going external.",
        "evidence_against": "Two finished deliverables shipped without hesitation; the pattern may be "
        "domain-specific (client work) rather than global.",
        "hypotheses": [
            {
                "id": "H1",
                "statement": "Protective part: delay avoids external appraisal of the work.",
                "prior": 0.45,
                "falsifier": "When appraisal is removed (anonymous draft review), completion time drops to baseline.",
                "test": "Send an unlabeled draft to two reviewers and measure time-to-completion.",
            },
            {
                "id": "H2",
                "statement": "Skill gap: the task is genuinely under-specified and unclear next step.",
                "prior": 0.35,
                "falsifier": "A written 3-step scope reduces time-to-start within 7 days.",
                "test": "Write the 3-step scope, then measure start latency for 5 working days.",
            },
            {
                "id": "H3",
                "statement": "Capacity: workload/energy is the binding constraint, not fear.",
                "prior": 0.20,
                "falsifier": "On weeks with <25 billable hours the same avoidance persists.",
                "test": "Log billable hours vs start latency for 14 days.",
            },
        ],
        "discriminating_test": (
            "Run both probes in parallel for 5 days: anonymous draft (H1) vs written scope (H2). "
            "Whichever moves start latency most is the surviving frame."
        ),
        "hard_constraints": ["24h clock", "client contract deadlines"],
        "soft_constraints": ["belief that work must be finished before it is shown"],
        "soft_masquerading": "The 'no draft until it is polished' rule is a policy, not physics.",
        "success_criteria": [
            {"metric": "start latency", "threshold": "median <= 24h", "by": "2026-10-07"},
            {"metric": "external shipments", "threshold": ">= 2 per week", "by": "within 21 days"},
        ],
        "review_date": "2026-10-07",
        "kill_criteria": [
            "If neither probe moves start latency by >20% within 14 days, the diagnosis is falsified.",
            "If shipments still 0 by 2026-10-21, abandon this frame and re-frame from scratch.",
        ],
        "anti_goals": ["optimize for feeling productive", "add tooling instead of shipping"],
        "framing_budget_min": 55,
        "p_flip": 0.60,
        "delta_payoff": 4000.0,
        "info_cost": 300.0,
        "cost_of_delay_per_day": 900.0,
        "baseline_counterfactual": (
            "Generic LLM: recommend a Pomodoro/2-minute-rule schedule. Predicted outcome: no "
            "change in external shipments within 30 days."
        ),
        "origin": "user",
        "surviving_branches": [
            {"id": "B1", "name": "Anonymous draft probe (H1)", "contingency": False},
            {
                "id": "B2",
                "name": "3-step scope probe (H2)",
                "contingency": True,
                "revive_trigger": "Anonymous draft fails to reduce start latency within 5 days",
            },
        ],
        "loop_budget": {
            "max_rounds": 3,
            "max_hours": 6,
            "success_signal": "Median start latency <= 24h across 2 external shipments",
        },
        "reversibility": 4,
    }
    payload.update(overrides)
    return payload


def frame_from(**overrides) -> FrameRecord:
    return build_frame(valid_payload(**overrides))


def codes(frame: FrameRecord) -> set[str]:
    return {v.code for v in validate_frame(frame).violations}


# ---------------------------------------------------------------------------
# Contract rules
# ---------------------------------------------------------------------------


def test_valid_frame_passes_all_rules():
    result = validate_frame(frame_from())
    assert result.ok, result.to_ascii()
    assert result.blockers == []


def test_r1_single_hypothesis_is_a_belief_not_a_diagnosis():
    frame = frame_from(hypotheses=[valid_payload()["hypotheses"][0] | {"prior": 1.0}])
    assert "R1" in codes(frame)


def test_r1b_unnormalised_priors_rejected():
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[0]["prior"] = 0.9  # sums to 1.45
    assert "R1b" in codes(frame_from(hypotheses=hyps))


def test_r1c_decorative_zero_prior_rival_rejected():
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[2]["prior"] = 0.0
    hyps[0]["prior"] = 0.65
    assert "R1c" in codes(frame_from(hypotheses=hyps))


def test_r2_missing_falsifier_rejected():
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[0]["falsifier"] = ""
    assert "R2" in codes(frame_from(hypotheses=hyps))


@pytest.mark.parametrize(
    "sealed",
    [
        "The part is protecting the wound, so he will resist the schedule.",
        "Any pushback is evidence of denial.",
        "Of course he would say that - it proves the point.",
        "The subconscious mind keeps him stuck.",
        "If he really wanted the client work he would have started.",
        "If he pushes back on the schedule, that is the protective part resisting, which confirms the diagnosis.",
    ],
)
def test_r2b_self_sealing_falsifiers_rejected(sealed):
    """The anti-pseudoscience guard: a 'falsifier' that can never die."""
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[0]["falsifier"] = sealed
    frame = frame_from(hypotheses=hyps)
    assert "R2b" in codes(frame)


def test_r2b_legitimate_falsifier_containing_resist_still_passes():
    """Specificity of the anti-pseudoscience guard: external resistance is not sealing."""
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[1]["falsifier"] = "The client resists the price by more than 30%, which kills the scope hypothesis."
    assert "R2b" not in codes(frame_from(hypotheses=hyps))


def test_r2c_missing_test_is_warning_not_blocker():
    hyps = [dict(h) for h in valid_payload()["hypotheses"]]
    hyps[1]["test"] = ""
    result = validate_frame(frame_from(hypotheses=hyps))
    assert "R2c" in {v.code for v in result.warnings}
    assert result.ok  # a warning must not stop execution


def test_r3_no_success_criteria_rejected():
    assert "R3" in codes(frame_from(success_criteria=[]))


@pytest.mark.parametrize(
    "criteria",
    [
        [{"metric": "feels better", "threshold": "noticeably", "by": "soon"}],
        [{"metric": "shipments", "threshold": "more than before", "by": "2026-10-07"}],
        [{"metric": "shipments", "threshold": ">= 2 per week", "by": "eventually"}],
    ],
)
def test_r3b_vibes_criteria_rejected(criteria):
    assert "R3b" in codes(frame_from(success_criteria=criteria))


def test_r3c_missing_review_date_rejected():
    assert "R3c" in codes(frame_from(review_date=""))


def test_r4_missing_kill_criteria_rejected():
    assert "R4" in codes(frame_from(kill_criteria=[]))


def test_r4b_reused_metric_warns():
    frame = frame_from(
        kill_criteria=["start latency"],
        success_criteria=[
            {"metric": "start latency", "threshold": "median <= 24h", "by": "2026-10-07"}
        ],
    )
    assert "R4b" in {v.code for v in validate_frame(frame).warnings}


def test_r5_framing_budget_above_tier_cap_rejected():
    assert "R5" in codes(frame_from(tier="STANDARD", framing_budget_min=55))


def test_r6_voi_stop_rule_blocks_unjustified_framing():
    """55 minutes of deliberation for a cheap, irrelevant answer must be refused."""
    assert "R6" in codes(frame_from(p_flip=0.02, delta_payoff=100.0, info_cost=50.0))


def test_r6_voi_blocks_when_probe_outearns_deliberation():
    # Net EVI is positive, but the framing's own delay cost exceeds it -> PROBE.
    assert "R6" in codes(
        frame_from(p_flip=0.30, delta_payoff=1000.0, info_cost=10.0, framing_budget_min=55,
                   cost_of_delay_per_day=10000.0)
    )


def test_r7b_challenge_mode_requires_evidence_against():
    assert "R7b" in codes(frame_from(evidence_against=""))


def test_r7c_experiment_mode_requires_discriminating_test():
    assert "R7c" in codes(frame_from(mode=4, discriminating_test=""))


def test_r8_missing_baseline_counterfactual_rejected():
    assert "R8" in codes(frame_from(baseline_counterfactual=""))


def test_r9_unexamined_soft_constraints_warn():
    frame = frame_from(soft_constraints=[], soft_masquerading="")
    assert "R9" in {v.code for v in validate_frame(frame).warnings}


def test_r10_missing_frame_level_discriminating_test_rejected():
    assert "R10" in codes(frame_from(discriminating_test=""))


# ---------------------------------------------------------------------------
# EVI / value of information
# ---------------------------------------------------------------------------


def test_evi_frame_verdict_when_deliberation_pays():
    r = compute_evi(p_flip=0.6, delta_payoff=4000.0, info_cost=300.0, framing_minutes=55,
                    cost_of_delay_per_day=900.0)
    assert r.verdict == "FRAME"
    assert r.gross_evi == pytest.approx(2400.0)
    assert r.net_evi == pytest.approx(2100.0)
    assert r.framing_evi < r.net_evi  # delay is priced, not ignored


def test_evi_probe_verdict_when_cheap_test_outearns_thinking():
    r = compute_evi(p_flip=0.5, delta_payoff=100.0, info_cost=10.0, framing_minutes=240,
                    cost_of_delay_per_day=10000.0)
    assert r.verdict == "PROBE"


def test_evi_execute_verdict_when_information_is_worthless():
    r = compute_evi(p_flip=0.05, delta_payoff=100.0, info_cost=50.0)
    assert r.verdict == "EXECUTE"
    assert r.net_evi < 0


def test_evi_rejects_invalid_inputs():
    with pytest.raises(ValidationError):
        compute_evi(p_flip=1.4, delta_payoff=1.0, info_cost=0.0)
    with pytest.raises(ValidationError):
        compute_evi(p_flip=0.5, delta_payoff=-1.0, info_cost=0.0)


# ---------------------------------------------------------------------------
# Ledger behaviour
# ---------------------------------------------------------------------------


def test_frame_id_is_deterministic():
    a = deterministic_frame_id("same request", "S1", "2026-09-23T00:00:00+00:00")
    b = deterministic_frame_id("SAME REQUEST ", "S1", "2026-09-23T00:00:00+00:00")
    c = deterministic_frame_id("same request", "S2", "2026-09-23T00:00:00+00:00")
    assert a == b
    assert a != c


def test_ledger_rejects_invalid_frame(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    result = ledger.open(frame_from(kill_criteria=[]))
    assert not result.ok
    assert ledger.frames() == []  # nothing recorded
    assert not (tmp_path / "frames.jsonl").exists()


def test_ledger_roundtrip_and_append_only(tmp_path: Path):
    path = tmp_path / "frames.jsonl"
    ledger = FrameLedger(path)
    frame = frame_from()
    assert ledger.open(frame, lock=True).ok
    with pytest.raises(ValidationError):
        ledger.open(frame)  # append-only: no silent overwrite
    reloaded = FrameLedger(path).get(frame.id)
    assert reloaded is not None
    assert reloaded.top_hypothesis.id == "H1"
    assert reloaded.status == "locked"


def test_resolve_scores_brier_and_hit(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    frame = frame_from()
    ledger.open(frame, lock=True)
    res = ledger.resolve(frame.id, supported=["H1"], killed=["H2", "H3"], regret=2.0, note="probe worked")
    # ((0.45-1)^2 + (0.35-0)^2 + (0.20-0)^2) / 3
    assert res["brier"] == pytest.approx((0.3025 + 0.1225 + 0.04) / 3, abs=1e-4)
    assert res["frame_hit"] is True
    stored = FrameLedger(tmp_path / "frames.jsonl").get(frame.id)
    assert stored.status == "resolved"


def test_resolve_rejects_unknown_hypothesis_ids(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    frame = frame_from()
    ledger.open(frame)
    with pytest.raises(ValidationError):
        ledger.resolve(frame.id, supported=["H9"])


def test_resolve_requires_an_outcome(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    frame = frame_from()
    ledger.open(frame)
    with pytest.raises(ValidationError):
        ledger.resolve(frame.id, supported=[])


def test_pivot_is_recorded_as_its_own_event(tmp_path: Path):
    path = tmp_path / "frames.jsonl"
    ledger = FrameLedger(path)
    frame = frame_from()
    ledger.open(frame)
    ledger.pivot(frame.id, "H2 probe moved start latency 4x more than H1 probe")
    kinds = [e["kind"] for e in FrameLedger(path).events()]
    assert kinds == ["frame", "pivot"]


# ---------------------------------------------------------------------------
# Scoring / kill switch
# ---------------------------------------------------------------------------


def test_kill_switch_reports_insufficient_data_below_threshold(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    frame = frame_from()
    ledger.open(frame)
    ledger.resolve(frame.id, supported=["H2"], killed=["H1", "H3"])
    stats = score_frames(ledger.frames())
    assert "INSUFFICIENT DATA" in stats["kill_switch_status"]
    assert stats["frames_resolved"] == 1
    assert stats["frame_hit_rate"] == 0.0
    assert stats["mean_brier"] == pytest.approx((0.2025 + 0.4225 + 0.04) / 3, abs=1e-4)


def test_kill_switch_fires_when_frames_underperform_coin_flip(tmp_path: Path):
    """50 resolved frames that score worse than a coin flip must trip the thesis kill switch."""
    path = tmp_path / "frames.jsonl"
    lines = []
    for i in range(50):
        hyp = [
            Hypothesis(id="H1", statement="a", prior=0.9, falsifier="x observed", test="probe a"),
            Hypothesis(id="H2", statement="b", prior=0.1, falsifier="y observed", test="probe b"),
        ]
        rec = frame_from(hypotheses=[h.to_dict() for h in hyp])
        rec.id = f"FR-SEED{i:03d}"
        rec.literal_request = f"seedful request {i}"
        lines.append(json.dumps({"kind": "frame", "ts": "2026-01-01T00:00:00+00:00", "frame": rec.to_dict()}))
        lines.append(
            json.dumps(
                {
                    "kind": "resolution",
                    "ts": "2026-02-01T00:00:00+00:00",
                    "id": rec.id,
                    "resolution": {"brier": 0.82, "frame_hit": False, "supported": ["H2"], "regret": 8},
                }
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    stats = score_frames(FrameLedger(path).frames())
    assert stats["frames_resolved"] == 50
    assert stats["skill_vs_coinflip"] < 0
    assert "KILL SWITCH FIRED" in stats["kill_switch_status"]


def test_pending_rot_counts_unresolved_frames(tmp_path: Path):
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    a, b = frame_from(), frame_from()
    b.id = "FR-SECOND"
    b.literal_request = "second distinct request"
    ledger.open(a)
    ledger.open(b)
    ledger.resolve(a.id, supported=["H1"], killed=["H2", "H3"])
    stats = score_frames(ledger.frames())
    assert stats["frames_opened"] == 2
    assert stats["pending_rot"] == 1


# ---------------------------------------------------------------------------
# Adoption scan (operationalises the audit's F-01 finding)
# ---------------------------------------------------------------------------


def test_adoption_scan_counts_markers_and_cold_markers(tmp_path: Path):
    corpus = tmp_path / ".context" / "memories" / "session_logs"
    corpus.mkdir(parents=True)
    (corpus / "2026-09-01-session-001.md").write_text(
        "We produced a Literal Request and a Candidate Reframe, then locked it.", encoding="utf-8"
    )
    (corpus / "2026-09-02-session-002.md").write_text("no artifacts here", encoding="utf-8")
    scan = scan_adoption(tmp_path)
    assert scan["session_files"] == 2
    assert scan["files_with_any_marker"] == 1
    assert scan["marker_hits"]["Candidate Reframe"] == 1
    assert "Kill Criteria" in scan["cold_markers"]
    assert scan["markers_per_100_sessions"] == 100.0


def test_adoption_scan_on_this_repo_is_deterministic():
    first = scan_adoption(Path("."))
    second = scan_adoption(Path("."))
    assert first == second
    assert set(first["marker_hits"]) == set(ADOPTION_MARKERS)


# ---------------------------------------------------------------------------
# Seeded-defect calibration of the validator itself
# ---------------------------------------------------------------------------


SEEDED_DEFECTS = [
    ("R1", {"hypotheses": [valid_payload()["hypotheses"][0] | {"prior": 1.0}]}),
    ("R2", {"hypotheses": [{**valid_payload()["hypotheses"][0], "falsifier": ""}] +
                       valid_payload()["hypotheses"][1:]}),
    ("R3", {"success_criteria": []}),
    ("R4", {"kill_criteria": []}),
    ("R5", {"tier": "SNIPER", "framing_budget_min": 55}),
    ("R7b", {"evidence_against": ""}),
    ("R8", {"baseline_counterfactual": ""}),
    ("R10", {"discriminating_test": ""}),
    ("R11", {"loop_budget": None}),
    ("R12", {"surviving_branches": [{"id": "B1", "contingency_trigger": "only one"}]}),
    ("R13", {"reversibility": 1, "ruin_receipt": ""}),
]


def test_seeded_defect_sensitivity_is_100_percent():
    """Sensitivity: every seeded defect must be caught by its own rule."""
    caught = 0
    for expected_code, overrides in SEEDED_DEFECTS:
        found = codes(frame_from(**overrides))
        caught += int(expected_code in found)
    assert caught == len(SEEDED_DEFECTS), f"{caught}/{len(SEEDED_DEFECTS)} seeded defects caught"


def test_validator_false_positive_rate_is_zero_on_clean_frames():
    """Specificity: a clean frame must never be blocked, or the gate is unusable."""
    for i in range(10):
        frame = frame_from(literal_request=f"clean request variant {i}")
        result = validate_frame(frame)
        assert result.ok, f"false positive on variant {i}: {result.to_ascii()}"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def test_report_written_atomically(tmp_path: Path):
    ledger_path = tmp_path / "frames.jsonl"
    out = tmp_path / "FRAME_CALIBRATION.md"
    ledger = FrameLedger(ledger_path)
    frame = frame_from()
    ledger.open(frame)
    text = calibration_report(ledger, adoption_root=tmp_path)
    out.write_text(text, encoding="utf-8")
    assert "Frame Quality" in text
    assert frame.id in text
    assert not out.with_suffix(".md.tmp").exists()

# ---------------------------------------------------------------------------
# Wiring + regression guards (the pipeline must not decay back into prose)
# ---------------------------------------------------------------------------

CLUSTER15_PROTOCOLS = [
    "src/athena/mcp_server.py",
    "src/athena/core/permissions.py",
]


def test_mcp_tools_are_wired_with_permissions():
    """The enforcement surface must exist in code, not only in a protocol."""
    import ast

    from athena.core.permissions import TOOL_REGISTRY

    source = (PROJECT_ROOT / "src" / "athena" / "mcp_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    decorated = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and any("mcp.tool" in ast.unparse(d) for d in node.decorator_list)
    }
    expected = {"frame_open", "frame_validate", "frame_resolve", "frame_status"}
    assert expected <= decorated, f"missing MCP tools: {sorted(expected - decorated)}"
    assert expected <= set(TOOL_REGISTRY), f"missing permission entries: {sorted(expected - set(TOOL_REGISTRY))}"


_SEED_FRAME = PROJECT_ROOT / "docs" / "audits" / "frames" / "cluster15-redteam-2026-09-23.json"


@pytest.mark.skipif(
    not _SEED_FRAME.exists(),
    reason="audit seed frame not present in public repo",
)
def test_seed_frame_for_this_audit_passes_the_contract():
    """The audit's own pre-registered frame must stay compliant."""
    frame = build_frame(json.loads(_SEED_FRAME.read_text(encoding="utf-8")))
    result = validate_frame(frame)
    assert result.ok, result.to_ascii()


@pytest.mark.parametrize(
    "protocol",
    [
        ".agent/skills/protocols/reasoning/RSN-504-problem-framing.md",
        ".agent/skills/protocols/reasoning/RSN-505-graph-of-thought.md",
        ".agent/skills/protocols/reasoning/RSN-506-gto-execution-plan.md",
    ],
)
def test_cluster15_protocol_links_resolve(protocol):
    """Regression guard: the pipeline shipped with two dead cross-references."""
    import re

    path = PROJECT_ROOT / protocol
    if not path.exists():
        pytest.skip(f"{protocol} not present in this repo layout")
    text = path.read_text(encoding="utf-8")
    dead = []
    for link in re.findall(r"\]\(([^)#]+)\)", text):
        if link.startswith(("http", "mailto")):
            continue
        if not (path.parent / link).resolve().exists():
            dead.append(link)
    assert dead == [], f"{protocol} has dead links: {dead}"


# ---------------------------------------------------------------------------
# Phase 3 (2026-10-17 Plan T3.1-T3.3): Commitment gate, Luck gate, user origin
# ---------------------------------------------------------------------------


def test_r11_missing_loop_budget_rejected():
    """T3.1: A frame with no loop_budget is BLOCKED by R11, and passes once added."""
    blocked = frame_from(loop_budget={})
    assert "R11" in codes(blocked)
    passed = frame_from(
        loop_budget={"max_rounds": 3, "success_signal": "Rubric score >= 75/100"}
    )
    assert "R11" not in codes(passed)


def test_r12_requires_two_surviving_branches_with_contingency():
    """T3.1: R12 blocks single-branch lock ('kill all other options') and passes with contingency."""
    single = frame_from(
        surviving_branches=[{"id": "B1", "name": "Primary", "contingency": False}]
    )
    assert "R12" in codes(single)
    no_trigger = frame_from(
        surviving_branches=[
            {"id": "B1", "name": "Primary", "contingency": False},
            {"id": "B2", "name": "Backup", "contingency": True, "revive_trigger": ""},
        ]
    )
    assert "R12" in codes(no_trigger)
    valid = frame_from(
        surviving_branches=[
            {"id": "B1", "name": "Primary", "contingency": False},
            {
                "id": "B2",
                "name": "Backup",
                "contingency": True,
                "revive_trigger": "Primary fails regulatory bailment check within 7 days",
            },
        ]
    )
    assert "R12" not in codes(valid)


def test_r13_irreversible_requires_verified_ruin_receipt_or_agent_estimate(
    tmp_path: Path, monkeypatch
):
    """T3.1: Reversibility <= 2 requires a real receipt ID in decision_receipts.jsonl or [agent-estimate]."""
    receipts_file = tmp_path / "decision_receipts.jsonl"
    receipts_file.write_text(
        json.dumps({"receipt_id": "GTO-real9999", "action": "mcda", "verdict": "PASS"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ATHENA_RECEIPTS_PATH", str(receipts_file))

    fake = frame_from(reversibility=2, ruin_receipt="GTO-madeup00")
    assert "R13" in codes(fake)

    real = frame_from(reversibility=2, ruin_receipt="GTO-real9999")
    assert "R13" not in codes(real)

    est = frame_from(
        reversibility=2,
        ruin_receipt="[agent-estimate] p_ruin=0.02 based on capped S$1,500 deposit",
    )
    assert "R13" not in codes(est)


def test_t32_luck_classification_requires_outcome_within_registered_band(tmp_path: Path):
    """T3.2: LUCK classification is accepted only if observed_value is inside outcome_band."""
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    frame = frame_from(outcome_band={"min": -200.0, "max": 500.0})
    assert ledger.open(frame, lock=True).ok

    # Outside band -> rejected
    with pytest.raises(ValidationError, match="LUCK|band"):
        ledger.resolve(
            frame.id,
            supported=["H2"],
            killed=["H1", "H3"],
            classification="LUCK",
            observed_value=-450.0,
        )

    # Inside band -> accepted
    res = ledger.resolve(
        frame.id,
        supported=["H2"],
        killed=["H1", "H3"],
        classification="LUCK",
        observed_value=-120.0,
    )
    assert res["classification"] == "LUCK"
    assert res["observed_value"] == -120.0


def test_t33_calibrate_counts_only_user_origin_frames(tmp_path: Path):
    """T3.3: Audit frames count as 0 user frames toward the adoption kill criterion."""
    ledger = FrameLedger(tmp_path / "frames.jsonl")
    audit1 = frame_from(id="FRM-20260923-001", origin="audit", session="cluster15-redteam-2026-09-23")
    audit2 = frame_from(id="FRM-20260929-001", origin="audit", session="audit-2026-09-29")
    assert ledger.open(audit1).ok
    assert ledger.open(audit2).ok
    stats = score_frames(ledger.frames())
    assert stats["frames_opened"] == 2
    assert stats["user_frames_opened"] == 0
    assert stats["audit_frames_opened"] == 2

    private_ledger = PROJECT_ROOT / ".context" / "ledger" / "frames.jsonl"
    if private_ledger.exists():
        existing = FrameLedger(private_ledger).frames()
        pstats = score_frames(existing)
        assert pstats["frames_opened"] == 2
        assert pstats["user_frames_opened"] == 0
        assert pstats["audit_frames_opened"] == 2
