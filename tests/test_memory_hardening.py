"""
tests/test_memory_hardening.py — TDD suite for memory TTL, taint quarantine,
deterministic /dream verifier, atomic forget, role-scoped budgets, and health eval.

All tests are 100% isolated under tmp_path / monkeypatch and contain zero private
fixtures so they pass cleanly in both Project Athena and Athena-Public CI.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _write_sample_stores(
    root: Path,
    *,
    user_notes: list[dict],
    system_rows: list[str],
    canonical_lines: list[str] | None = None,
) -> tuple[Path, Path]:
    import yaml

    mem_dir = root / ".athena" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    ctx_dir = root / ".context"
    (ctx_dir / "memory_bank").mkdir(parents=True, exist_ok=True)
    (ctx_dir / "memories" / "session_logs").mkdir(parents=True, exist_ok=True)

    user_file = mem_dir / "USER_PROFILE.yaml"
    header = "# User Profile (Machine-Readable Preferences)\n# Test Fixture\n\n"
    user_file.write_text(
        header + yaml.dump({"notes": user_notes}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    system_file = mem_dir / "SYSTEM_LEARNINGS.md"
    sys_body = [
        "# System Learnings Log",
        "",
        "| Date | Session | Learning | Integrated |",
        "|------|---------|----------|------------|",
        *system_rows,
        "",
        "## Tagging",
        "",
        "# system #learnings",
        "",
    ]
    system_file.write_text("\n".join(sys_body), encoding="utf-8")

    canon_file = ctx_dir / "CANONICAL.md"
    canon_file.write_text("\n".join(canonical_lines or ["# Canonical"]), encoding="utf-8")
    return user_file, system_file


# ---------------------------------------------------------------------------
# 1. Zero-Token TTL, Negative Guardrail Paradox Immunity & Atomic Writes
# ---------------------------------------------------------------------------


def test_ttl_parsing_and_zero_token_search_exclusion(tmp_path):
    from athena.memory.learnings import parse_expires_at, search_learnings

    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    past = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    future = (now + timedelta(days=5)).strftime("%Y-%m-%d")

    assert parse_expires_at("2026-11-20") == datetime(2026, 11, 20, 23, 59, 59, tzinfo=timezone.utc)
    assert parse_expires_at(None, f"Sprint freeze reminder [expires_at:{past}]") is not None

    user_file, sys_file = _write_sample_stores(
        tmp_path,
        user_notes=[
            {
                "learned": "Expired dentist appointment logistics for alpha workspace",
                "session": "2026-11-10-session-S1",
                "confidence": "medium",
                "expires_at": past,
            },
            {
                "learned": "Active quarterly planning logistics for alpha workspace",
                "session": "2026-11-20-session-S2",
                "confidence": "medium",
                "expires_at": future,
            },
        ],
        system_rows=[
            f"| 2026-11-10 | 2026-11-10-session-S1 | Temporary alpha deploy window closed [expires_at:{past}] | ⏳ Pending |",
            f"| 2026-11-20 | 2026-11-20-session-S2 | Active alpha deploy checklist item [expires_at:{future}] | ⏳ Pending |",
        ],
    )

    default_hits = search_learnings(
        "alpha workspace appointment deploy",
        user_path=user_file,
        system_path=sys_file,
        now=now,
    )
    user_contents = [r.content for r in default_hits["user_profile"]]
    sys_contents = [r.content for r in default_hits["system_learnings"]]
    assert any("Active quarterly planning" in c for c in user_contents)
    assert all("Expired dentist" not in c for c in user_contents)
    assert any("Active alpha deploy checklist" in c for c in sys_contents)
    assert all("Temporary alpha deploy window closed" not in c for c in sys_contents)

    with_expired = search_learnings(
        "alpha workspace dentist deploy",
        user_path=user_file,
        system_path=sys_file,
        now=now,
        include_expired=True,
    )
    assert any("Expired dentist" in r.content for r in with_expired["user_profile"])
    assert any("Temporary alpha deploy window closed" in r.content for r in with_expired["system_learnings"])


def test_negative_guardrail_paradox_pinned_immunity(tmp_path):
    from athena.memory.learnings import search_learnings

    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    past = (now - timedelta(days=30)).isoformat()

    user_file, sys_file = _write_sample_stores(
        tmp_path,
        user_notes=[
            {
                "learned": "Never push unverified credentials to public branch",
                "session": "2026-09-01-session-S1",
                "confidence": "medium",
                "pinned": True,
                "expires_at": past,
            },
            {
                "learned": "Never push unverified credentials on Fridays",
                "session": "2026-11-20-session-S9",
                "confidence": "medium",
            },
        ],
        system_rows=[
            f"| 2026-09-01 | 2026-09-01-session-S1 | Never bypass ruin gate checks [pinned] [expires_at:{past}] | ⏳ Pending |",
        ],
    )

    hits = search_learnings(
        "never push unverified credentials bypass ruin gate",
        user_path=user_file,
        system_path=sys_file,
        now=now,
    )
    assert hits["user_profile"], "Pinned guardrail must survive even with past expires_at"
    assert hits["user_profile"][0].metadata["pinned"] is True
    assert "public branch" in hits["user_profile"][0].content
    assert hits["system_learnings"], "Inline [pinned] system guardrail must remain active"
    assert hits["system_learnings"][0].metadata["pinned"] is True


def test_imminent_expiry_boost_and_stats(tmp_path):
    from athena.memory.learnings import get_learnings_stats, search_learnings

    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    imminent = (now + timedelta(hours=24)).isoformat()
    distant = (now + timedelta(days=30)).isoformat()
    past = (now - timedelta(days=1)).isoformat()

    user_file, sys_file = _write_sample_stores(
        tmp_path,
        user_notes=[
            {
                "learned": "Submit quarterly tax briefing checkpoint",
                "session": "2026-11-20-session-S10",
                "confidence": "medium",
                "expires_at": imminent,
            },
            {
                "learned": "Submit quarterly tax briefing archival check",
                "session": "2026-11-21-session-S11",
                "confidence": "medium",
                "expires_at": distant,
            },
        ],
        system_rows=[
            f"| 2026-11-10 | 2026-11-10-session-S1 | Expired release freeze notice [expires_at:{past}] | ⏳ Pending |",
            "| 2026-11-20 | 2026-11-20-session-S11 | Complete CI migration deadline by 2026-12-01 | ⏳ Pending |",
        ],
    )

    hits = search_learnings("quarterly tax briefing", user_path=user_file, system_path=sys_file, now=now)
    assert "checkpoint" in hits["user_profile"][0].content

    stats = get_learnings_stats(user_path=user_file, system_path=sys_file, now=now)
    assert stats["user_expired"] == 0
    assert stats["system_expired"] == 1
    assert stats["imminent_expiring"] == 1
    assert stats["date_bound_missing_ttl"] >= 1


def test_compact_prune_expired_and_0600_mode(tmp_path):
    from athena.memory.learnings import compact_learnings_stores

    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    past = (now - timedelta(days=2)).isoformat()
    future = (now + timedelta(days=10)).isoformat()

    user_file, sys_file = _write_sample_stores(
        tmp_path,
        user_notes=[
            {"learned": "Old temporary note", "session": "s1", "confidence": "low", "expires_at": past},
            {"learned": "Pinned old guardrail", "session": "s1", "confidence": "high", "pinned": True, "expires_at": past},
            {"learned": "Future active note", "session": "s2", "confidence": "medium", "expires_at": future},
        ],
        system_rows=[
            f"| 2026-11-01 | s1 | Old expired row [expires_at:{past}] | ⏳ Pending |",
            f"| 2026-11-01 | s1 | Pinned guardrail row [pinned] [expires_at:{past}] | ⏳ Pending |",
            f"| 2026-11-20 | s2 | Active valid row [expires_at:{future}] | ⏳ Pending |",
        ],
    )

    res = compact_learnings_stores(
        user_path=user_file,
        system_path=sys_file,
        dry_run=False,
        prune_expired=True,
        now=now,
    )
    assert res["user"]["expired_removed"] == 1
    assert res["user"]["after"] == 2
    assert res["system"]["expired_removed"] == 1
    assert res["system"]["after"] == 2

    sys_text = sys_file.read_text(encoding="utf-8")
    assert "Pinned guardrail row" in sys_text
    assert "Old expired row" not in sys_text
    assert sys_text.index("Active valid row") < sys_text.index("## Tagging")

    if os.name == "posix":
        assert stat.S_IMODE(user_file.stat().st_mode) == 0o600
        assert stat.S_IMODE(sys_file.stat().st_mode) == 0o600


# ---------------------------------------------------------------------------
# 2. Monotonic Inbound Taint Quarantine
# ---------------------------------------------------------------------------


def test_taint_is_monotonic_and_requires_human_confirm(tmp_path):
    from athena.core.taint import (
        TaintBlockedError,
        assert_untainted,
        clear_taint,
        get_taint_status,
        is_tainted,
        mark_tainted,
    )

    assert not is_tainted(project_root=tmp_path, session_id="s-test")
    entry = mark_tainted("external_email", "untrusted_attachment", session_id="s-test", project_root=tmp_path)
    assert entry["tainted"] is True
    assert is_tainted(project_root=tmp_path, session_id="s-test")

    status = get_taint_status(project_root=tmp_path, session_id="s-test")
    assert status["tainted"] is True
    assert status["sources"][0]["source"] == "external_email"

    with pytest.raises(TaintBlockedError):
        assert_untainted("quicksave", session_id="s-test", project_root=tmp_path)

    with pytest.raises(ValueError, match="human_confirm=True"):
        clear_taint(session_id="s-test", project_root=tmp_path)

    assert is_tainted(project_root=tmp_path, session_id="s-test")
    assert clear_taint(human_confirm=True, session_id="s-test", project_root=tmp_path) is True
    assert not is_tainted(project_root=tmp_path, session_id="s-test")


def test_taint_blocks_session_append_checkpoint(tmp_path):
    from athena.core.taint import TaintBlockedError, clear_taint, mark_tainted
    from athena.lifecycle.session_service import SessionService

    logs_dir = tmp_path / ".context" / "memories" / "session_logs"
    svc = SessionService(sessions_dir=logs_dir)
    session_file = svc.create_session(focus="Taint isolation test")

    mark_tainted("external_web_drop", "prompt_injection_risk", project_root=tmp_path)
    with pytest.raises(TaintBlockedError):
        svc.append_checkpoint("Should be quarantined", log_path=session_file)

    assert "Should be quarantined" not in session_file.read_text(encoding="utf-8")

    clear_taint(human_confirm=True, project_root=tmp_path)
    svc.append_checkpoint("Safe post-clear checkpoint", log_path=session_file)
    assert "Safe post-clear checkpoint" in session_file.read_text(encoding="utf-8")


def test_taint_blocks_mcp_quicksave_and_quarantines_context_gate(tmp_path, monkeypatch):
    from athena.core.permissions import Permission, get_permissions
    from athena.core.taint import is_protected_memory_path, mark_tainted
    from athena.mcp_server import context_gate, quicksave

    taint_file = tmp_path / "taint_state.json"
    monkeypatch.setenv("ATHENA_TAINT_STATE_PATH", str(taint_file))
    mark_tainted("untrusted_email", "external_drop")

    perms = get_permissions()
    orig_level = perms.caller_level
    perms.caller_level = Permission.WRITE
    try:
        qs_res = quicksave("Attempted tainted checkpoint")
        assert qs_res["status"] == "blocked"
        assert qs_res["taint_blocked"] is True

        seen_include_personal: list[bool] = []

        def fake_run_search(query, **kwargs):
            seen_include_personal.append(bool(kwargs.get("include_personal", True)))
            return {"results": [{"id": "doc-1", "content": "Neutral system doc", "rrf_score": 0.05}]}

        with patch("athena.tools.search.run_search", side_effect=fake_run_search):
            cg_res = context_gate("Should I send this external client proposal?", limit=2, web=False)

        assert seen_include_personal and seen_include_personal[0] is False
        assert cg_res["tainted"] is True
        assert cg_res["personalisation"] is None
        assert cg_res["user_state"] is None
        assert "TAINT QUARANTINE ACTIVE" in cg_res["directive"]
    finally:
        perms.caller_level = orig_level

    assert is_protected_memory_path(".context/CANONICAL.md") is True
    assert is_protected_memory_path(".athena/memory/USER_PROFILE.yaml") is True
    assert is_protected_memory_path(".context/memories/session_logs/2026-11-21-session-S1.md") is True
    assert is_protected_memory_path("src/athena/core/taint.py") is False


def test_block_tainted_memory_hook_fail_closed(tmp_path, monkeypatch):
    from athena.core.taint import mark_tainted

    hook_script = REPO_ROOT / ".agent" / "scripts" / "security" / "block_tainted_memory.py"
    assert hook_script.is_file()

    taint_file = tmp_path / "taint_state.json"
    monkeypatch.setenv("ATHENA_TAINT_STATE_PATH", str(taint_file))
    monkeypatch.delenv("ATHENA_TAINTED", raising=False)
    env = {
        **os.environ,
        "ATHENA_ROOT": str(tmp_path),
        "ATHENA_TAINT_STATE_PATH": str(taint_file),
    }

    # (a) Malformed JSON stdin must fail closed (exit 2)
    bad = subprocess.run(
        [sys.executable, str(hook_script)],
        input="{not-valid-json",
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )
    assert bad.returncode == 2
    assert "BLOCKED (fail-closed)" in bad.stderr

    # (b) Untainted write to CANONICAL.md passes (exit 0)
    canon_payload = json.dumps({"tool_input": {"file_path": str(tmp_path / ".context" / "CANONICAL.md")}})
    clean = subprocess.run(
        [sys.executable, str(hook_script)],
        input=canon_payload,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )
    assert clean.returncode == 0

    # (c) Tainted write to CANONICAL.md fails closed (exit 2)
    mark_tainted("external_attachment", "untrusted_drop", project_root=tmp_path)
    blocked = subprocess.run(
        [sys.executable, str(hook_script)],
        input=canon_payload,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )
    assert blocked.returncode == 2
    assert "taint quarantine" in blocked.stderr

    # (d) Tainted write to ordinary source file exits 0
    src_payload = json.dumps({"tool_input": {"file_path": str(tmp_path / "src" / "foo.py")}})
    allowed_src = subprocess.run(
        [sys.executable, str(hook_script)],
        input=src_payload,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )
    assert allowed_src.returncode == 0


# ---------------------------------------------------------------------------
# 3. Deterministic /dream Transcript Verifier
# ---------------------------------------------------------------------------


def test_dream_verifier_catches_pokemon_red_contradiction(tmp_path):
    from athena.memory.dream_verifier import verify_pending_learnings

    _write_sample_stores(
        tmp_path,
        user_notes=[],
        system_rows=[
            "| 2026-11-20 | 2026-11-20-session-S100 | Fixed build pipeline and tests passing | ⏳ Pending |",
        ],
    )
    log_file = tmp_path / ".context" / "memories" / "session_logs" / "2026-11-20-session-S100.md"
    log_file.write_text(
        "# Session S100\nRun pytest...\nFAILED test_core.py\nTraceback: AssertionError\n",
        encoding="utf-8",
    )

    report = verify_pending_learnings(project_root=tmp_path)
    assert report["counts"]["UNVERIFIED_CLAIM"] == 1
    item = report["by_verdict"]["UNVERIFIED_CLAIM"][0]
    assert item["evidence_lines"]
    assert "2026-11-20-session-S100.md#L" in item["evidence_lines"][0]


def test_dream_verifier_allows_recovered_session(tmp_path):
    from athena.memory.dream_verifier import verify_pending_learnings

    _write_sample_stores(
        tmp_path,
        user_notes=[],
        system_rows=[
            "| 2026-11-20 | 2026-11-20-session-S101 | Fixed build pipeline and verified green | ⏳ Pending |",
        ],
    )
    log_file = tmp_path / ".context" / "memories" / "session_logs" / "2026-11-20-session-S101.md"
    log_file.write_text(
        "# Session S101\nFAILED first attempt\nPatched parser\nall passed in 0.8s\n",
        encoding="utf-8",
    )

    report = verify_pending_learnings(project_root=tmp_path)
    assert report["counts"]["READY_TO_GRADUATE"] == 1
    assert report["counts"]["UNVERIFIED_CLAIM"] == 0


def test_dream_verifier_detects_already_codified_and_expired(tmp_path):
    from athena.memory.dream_verifier import verify_pending_learnings

    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    past = (now - timedelta(days=1)).isoformat()

    _write_sample_stores(
        tmp_path,
        user_notes=[],
        system_rows=[
            f"| 2026-11-01 | s1 | Old expired sprint checklist item [expires_at:{past}] | ⏳ Pending |",
            "| 2026-11-15 | s2 | Always use atomic writes with advisory locks and 0600 permissions | ⏳ Pending |",
            "| 2026-11-19 | s-missing | Unlogged brand-new heuristic pending review | ⏳ Pending |",
        ],
        canonical_lines=[
            "# Canonical Laws",
            "- Always use atomic writes with advisory locks and 0600 permissions for learning stores.",
        ],
    )

    report = verify_pending_learnings(project_root=tmp_path, now=now)
    assert report["counts"]["PRUNE_EXPIRED"] == 1
    assert report["counts"]["ALREADY_CODIFIED"] == 1
    assert report["counts"]["NEEDS_REVIEW"] == 1
    assert report["by_verdict"]["ALREADY_CODIFIED"][0]["canonical_line"] == "CANONICAL.md#L2"


# ---------------------------------------------------------------------------
# 4. Atomic Cross-Layer `forget`
# ---------------------------------------------------------------------------


def test_forget_dry_run_vs_apply_and_short_phrase_guard(tmp_path):
    import yaml

    from athena.memory.forget import forget_phrase

    with pytest.raises(ValueError, match="at least 4 characters"):
        forget_phrase("abc", project_root=tmp_path)

    user_file, sys_file = _write_sample_stores(
        tmp_path,
        user_notes=[
            {"learned": "Operator dislikes brittle canary phrase delta-99", "session": "s1", "confidence": "medium"},
            {"learned": "Operator keeps atomic memory writes clean", "session": "s2", "confidence": "high"},
        ],
        system_rows=[
            "| 2026-11-20 | s1 | Remove brittle canary phrase delta-99 from prompts | ⏳ Pending |",
            "| 2026-11-20 | s2 | Keep FTS index synchronized cleanly | ⏳ Pending |",
        ],
    )
    src_file = tmp_path / "src" / "example.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text('CONST = "canary phrase delta-99"\n', encoding="utf-8")

    before_user = user_file.read_text(encoding="utf-8")
    before_sys = sys_file.read_text(encoding="utf-8")

    dry = forget_phrase("canary phrase delta-99", project_root=tmp_path, dry_run=True)
    assert dry["dry_run"] is True
    assert dry["entries_removed"] == 2
    assert user_file.read_text(encoding="utf-8") == before_user
    assert sys_file.read_text(encoding="utf-8") == before_sys

    applied = forget_phrase("canary phrase delta-99", project_root=tmp_path, dry_run=False)
    assert applied["dry_run"] is False
    assert applied["entries_removed"] == 2
    assert applied["cache_invalidated"] is True

    user_data = yaml.safe_load(user_file.read_text(encoding="utf-8"))
    assert len(user_data["notes"]) == 1
    assert "atomic memory writes" in user_data["notes"][0]["learned"]

    sys_text = sys_file.read_text(encoding="utf-8")
    assert "canary phrase delta-99" not in sys_text
    assert "## Tagging" in sys_text
    assert "Keep FTS index synchronized cleanly" in sys_text
    # Never touches source code files
    assert "canary phrase delta-99" in src_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 5. Role-Scoped Budgets, Memory Health Eval & CLI Smoke
# ---------------------------------------------------------------------------


def test_run_memory_fixtures_all_pass():
    from athena.memory.health import run_memory_fixtures

    fx = run_memory_fixtures()
    assert fx["total"] == 4
    assert fx["passed"] == 4
    assert fx["all_passed"] is True


def test_evaluate_memory_health_overlap_and_borges_map(tmp_path):
    from athena.memory.health import evaluate_memory_health

    shared_prose = " ".join(["deterministic invariant verification rule alpha beta"] * 20)
    _write_sample_stores(
        tmp_path,
        user_notes=[],
        system_rows=[],
        canonical_lines=[shared_prose],
    )
    (tmp_path / ".context" / "memory_bank" / "userContext.md").write_text(shared_prose, encoding="utf-8")
    (tmp_path / ".context" / "memory_bank" / "activeContext.md").write_text(shared_prose, encoding="utf-8")
    raw_log = tmp_path / ".context" / "memories" / "session_logs" / "2026-11-21-session-S1.md"
    raw_log.write_text("short raw log", encoding="utf-8")

    health = evaluate_memory_health(project_root=tmp_path)
    assert health["status"] == "warn"
    assert health["cross_layer_overlap"]["overall_overlap_pct"] > 25.0
    assert health["borges_map"]["ratio"] is not None
    assert health["borges_map"]["ratio"] > 0.35
    assert any("overlap" in w.lower() for w in health["warnings"])
    assert any("borges" in w.lower() for w in health["warnings"])


def test_cli_memory_subcommands_smoke(tmp_path):
    _write_sample_stores(tmp_path, user_notes=[], system_rows=[])
    env = {
        **os.environ,
        "PYTHONPATH": str(SRC_ROOT),
        "ATHENA_TAINT_STATE_PATH": str(tmp_path / "taint_state.json"),
    }

    eval_proc = subprocess.run(
        [sys.executable, "-m", "athena", "--root", str(tmp_path), "memory", "eval", "--fixtures", "--json"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert eval_proc.returncode == 0, eval_proc.stderr
    eval_data = json.loads(eval_proc.stdout)
    assert eval_data["fixtures"]["all_passed"] is True

    taint_proc = subprocess.run(
        [sys.executable, "-m", "athena", "--root", str(tmp_path), "memory", "taint", "status", "--json"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert taint_proc.returncode == 0, taint_proc.stderr
    assert json.loads(taint_proc.stdout)["tainted"] is False

    verify_proc = subprocess.run(
        [sys.executable, "-m", "athena", "--root", str(tmp_path), "memory", "verify", "--json"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert verify_proc.returncode == 0, verify_proc.stderr
    assert "counts" in json.loads(verify_proc.stdout)

    script_proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "memory_eval.py"),
            "--root",
            str(tmp_path),
            "--fixtures",
            "--verify",
            "--json",
        ],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert script_proc.returncode == 0, script_proc.stderr
    script_data = json.loads(script_proc.stdout)
    assert script_data["fixtures"]["all_passed"] is True
    assert "verify" in script_data
