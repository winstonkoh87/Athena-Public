#!/usr/bin/env python3
"""Regression tests for protocol discovery, summary indexing, and status/health tools."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _build_hybrid_workspace(root: Path) -> Path:
    """Create a repo fixture with an empty .agent/skills/protocols plus populated example/framework trees."""
    (root / ".athena_root").write_text("", encoding="utf-8")
    (root / ".context").mkdir(parents=True, exist_ok=True)
    # Simulate `athena init` creating an empty .agent/skills/protocols dir (and README/archived noise only)
    (root / ".agent" / "skills" / "protocols").mkdir(parents=True, exist_ok=True)
    _write(root / "examples" / "protocols" / "README.md", "# Protocols Index\n")
    _write(root / "examples" / "protocols" / "INDEX.md", "# Index\n")
    _write(
        root / "examples" / "protocols" / "architecture" / "_archived" / "ARC-999-retired.md",
        "# Protocol 999: Retired Protocol\n\nThis archived file must be ignored by discovery.\n",
    )
    _write(
        root / "examples" / "protocols" / "architecture" / "archive" / "ARC-998-archived.md",
        "# Protocol 998: Private Archive Protocol\n\nThis archive directory must also be ignored.\n",
    )
    _write(
        root / "examples" / "protocols" / "architecture" / "ARC-530-conditional-skill.md",
        """---
created: 2026-07-01
description: Load conditional skill definitions on explicit trigger match | pipe safe
---

# Protocol 530: Conditional Skill Activation

Only inject skill files when explicit conditions match.
""",
    )
    _write(
        root / "examples" / "protocols" / "workflow" / "WFL-62-double-fm.md",
        """---
created: 2025-12-16
last_updated: 2026-07-22
---

---tags: #workflow #co-thinking
created: 2025-12-16
---

# Protocol 62: Co-Thinking Interface

Structured collaborative drafting workflow between operator and model.

---

Body divider above must stay intact while double frontmatter must never leak.
""",
    )
    _write(
        root / "examples" / "protocols" / "engineering" / "075-cognitive-engine.md",
        """# Protocol 075: Cognitive Engine

Multi-perspective reasoning harness for high-stakes engineering tasks.
""",
    )
    _write(
        root / "examples" / "protocols" / "singapore" / "SGP-sg-001-randian.md",
        """# Protocol SG-001: Pragmatic Policy Model

Pragmatic public policy calibration framework.
""",
    )
    _write(
        root / "examples" / "protocols" / "communication" / "COM-adaptive-response.md",
        """---
created: 2026-05-01
---

---created: 2026-05-01
---

# Protocol: Adaptive Response Standard

Calibrate response depth dynamically to operator complexity.
""",
    )
    _write(
        root / ".framework" / "v8.2-stable" / "protocols" / "409_Parallel_Worktree.md",
        """# Protocol 409: Parallel Worktree Orchestration

Run isolated parallel worker agents in separate git worktrees safely.
""",
    )
    return root


@pytest.fixture
def hybrid_root(tmp_path: Path):
    import athena.core.config as cfg

    _build_hybrid_workspace(tmp_path)
    original_cwd = Path.cwd()
    yield tmp_path
    cfg.set_project_root(None)
    import os

    os.chdir(original_cwd)


class TestConfigDiscovery:
    """Validate athena.core.config protocol directory and file discovery."""

    def test_ignores_empty_agent_dir_and_finds_examples_and_framework(
        self, hybrid_root: Path
    ):
        import athena.core.config as cfg

        dirs = cfg.get_protocol_dirs(hybrid_root)
        assert dirs == [
            hybrid_root / "examples" / "protocols",
            hybrid_root / ".framework" / "v8.2-stable" / "protocols",
        ]
        assert cfg.get_protocols_dir(hybrid_root) == hybrid_root / "examples" / "protocols"

        active_files = cfg.iter_protocol_files(hybrid_root)
        names = {p.name for p in active_files}
        assert names == {
            "ARC-530-conditional-skill.md",
            "WFL-62-double-fm.md",
            "075-cognitive-engine.md",
            "SGP-sg-001-randian.md",
            "COM-adaptive-response.md",
            "409_Parallel_Worktree.md",
        }
        assert "README.md" not in names
        assert "INDEX.md" not in names
        assert "ARC-999-retired.md" not in names
        assert "ARC-998-archived.md" not in names

    def test_set_project_root_updates_core_dirs_and_active_memory_paths(
        self, hybrid_root: Path
    ):
        import athena.core.config as cfg

        cfg.set_project_root(hybrid_root)
        assert cfg.CORE_DIRS["protocols"] == hybrid_root / "examples" / "protocols"

        memory_paths = cfg.get_active_memory_paths()
        assert hybrid_root / "examples" / "protocols" in memory_paths
        assert hybrid_root / ".framework" / "v8.2-stable" / "protocols" in memory_paths
        assert hybrid_root / ".agent" / "skills" / "protocols" not in memory_paths

    def test_prefers_populated_agent_dir_over_examples(self, hybrid_root: Path):
        import athena.core.config as cfg

        live_proto = _write(
            hybrid_root / ".agent" / "skills" / "protocols" / "core" / "001-live.md",
            "# Protocol 001: Live Override\n\nActive local protocol.\n",
        )
        dirs = cfg.get_protocol_dirs(hybrid_root)
        assert dirs[0] == hybrid_root / ".agent" / "skills" / "protocols"
        assert cfg.get_protocols_dir(hybrid_root) == (
            hybrid_root / ".agent" / "skills" / "protocols"
        )
        assert live_proto in cfg.iter_protocol_files(hybrid_root)


class TestSummaryGenerationAndIndexing:
    """Validate generate_protocol_summaries.py and scripts/core/index_workspace.py."""

    def test_generates_summaries_with_relative_links_and_clean_frontmatter(
        self, hybrid_root: Path
    ):
        gen = _load_module(
            "generate_protocol_summaries",
            REPO_ROOT / "examples" / "scripts" / "generate_protocol_summaries.py",
        )
        out_file = hybrid_root / ".context" / "PROTOCOL_SUMMARIES.md"
        count, written = gen.generate_summaries(repo_root=hybrid_root, output_file=out_file)
        assert count == 6
        assert written == out_file

        content = out_file.read_text(encoding="utf-8")
        assert "**Inventory**: 6 protocols across 6 categories." in content
        assert "---tags:" not in content
        assert "---created:" not in content
        assert "## Framework (1)" in content
        assert "[530 Conditional Skill Activation](../examples/protocols/architecture/ARC-530-conditional-skill.md)" in content
        assert "pipe safe" in content
        assert "| pipe safe" not in content
        assert "[409 Parallel Worktree Orchestration](../.framework/v8.2-stable/protocols/409_Parallel_Worktree.md)" in content
        assert "[001 Pragmatic Policy Model](../examples/protocols/singapore/SGP-sg-001-randian.md)" in content
        assert "[Adaptive Response Standard](../examples/protocols/communication/COM-adaptive-response.md)" in content

        # Verify every generated link resolves relative to .context/
        import re

        links = re.findall(r"\]\(([^)]+\.md)\)", content)
        assert len(links) == 6
        for rel in links:
            assert rel.startswith("../")
            assert (out_file.parent / rel).resolve().is_file()

    def test_preserves_existing_summaries_when_empty_unless_forced(self, tmp_path: Path):
        gen = _load_module(
            "generate_protocol_summaries",
            REPO_ROOT / "examples" / "scripts" / "generate_protocol_summaries.py",
        )
        (tmp_path / ".agent" / "skills" / "protocols").mkdir(parents=True)
        out_file = _write(tmp_path / ".context" / "PROTOCOL_SUMMARIES.md", "# Existing Index\nKeep me!\n")

        count, _ = gen.generate_summaries(repo_root=tmp_path, output_file=out_file, force=False)
        assert count == 0
        assert "Keep me!" in out_file.read_text(encoding="utf-8")

        count_forced, _ = gen.generate_summaries(repo_root=tmp_path, output_file=out_file, force=True)
        assert count_forced == 0
        assert "0 protocols across 0 categories" in out_file.read_text(encoding="utf-8")

    def test_index_workspace_delegates_and_preserves_on_empty(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        idx = _load_module(
            "index_workspace",
            REPO_ROOT / "scripts" / "core" / "index_workspace.py",
        )
        out_file = hybrid_root / ".context" / "PROTOCOL_SUMMARIES.md"
        monkeypatch.setattr(idx, "PROJECT_ROOT", hybrid_root)
        monkeypatch.setattr(idx, "CONTEXT_DIR", hybrid_root / ".context")
        monkeypatch.setattr(idx, "PROTOCOL_SUMMARIES_FILE", out_file)

        idx.generate_protocol_summaries()
        text = out_file.read_text(encoding="utf-8")
        assert "6 protocols across 6 categories" in text
        assert "../examples/protocols/architecture/ARC-530-conditional-skill.md" in text

        # Empty root must NOT overwrite existing PROTOCOL_SUMMARIES.md
        empty_root = hybrid_root / "empty_sub"
        (empty_root / ".agent" / "skills" / "protocols").mkdir(parents=True)
        preserved = _write(empty_root / ".context" / "PROTOCOL_SUMMARIES.md", "# Sentinel\n")
        monkeypatch.setattr(idx, "PROJECT_ROOT", empty_root)
        monkeypatch.setattr(idx, "PROTOCOL_SUMMARIES_FILE", preserved)
        idx.generate_protocol_summaries()
        assert preserved.read_text(encoding="utf-8") == "# Sentinel\n"


class TestAuditorsStatusDoctorHeatmap:
    """Validate audit_staleness, athena_doctor, athena_status, and protocol_heatmap."""

    def test_audit_staleness_resolves_prefixed_and_framework_protocols(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        import athena.auditors.audit_staleness as staleness

        monkeypatch.setattr(staleness, "PROJECT_ROOT", hybrid_root)

        assert (
            staleness.resolve_protocol_ref("530")
            == hybrid_root / "examples" / "protocols" / "architecture" / "ARC-530-conditional-skill.md"
        )
        assert (
            staleness.resolve_protocol_ref("409")
            == hybrid_root / ".framework" / "v8.2-stable" / "protocols" / "409_Parallel_Worktree.md"
        )
        assert (
            staleness.resolve_protocol_ref("75")
            == hybrid_root / "examples" / "protocols" / "engineering" / "075-cognitive-engine.md"
        )
        # Must not collide across numbers (16 must not match 416 or 999)
        assert staleness.resolve_protocol_ref("16") is None
        assert staleness.resolve_protocol_ref("999") is None

    def test_athena_doctor_ignores_empty_agent_dir_and_counts_all_active(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        doctor = _load_module(
            "athena_doctor",
            REPO_ROOT / "examples" / "scripts" / "athena_doctor.py",
        )
        monkeypatch.setattr(doctor, "PROJECT_ROOT", hybrid_root)
        report = doctor.Report()
        doctor.check_protocols(report)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.severity == "pass"
        assert "6 protocols across 6 categories" in finding.message

        # Completely empty workspace should fail check_protocols rather than pass 0
        empty_ws = hybrid_root / "empty_ws"
        (empty_ws / ".agent" / "skills" / "protocols").mkdir(parents=True)
        monkeypatch.setattr(doctor, "PROJECT_ROOT", empty_ws)
        empty_report = doctor.Report()
        doctor.check_protocols(empty_report)
        assert empty_report.findings[0].severity == "fail"

    def test_status_scripts_root_and_protocol_count(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        status_root = _load_module(
            "scripts_athena_status",
            REPO_ROOT / "scripts" / "athena_status.py",
        )
        status_ex = _load_module(
            "examples_athena_status",
            REPO_ROOT / "examples" / "scripts" / "athena_status.py",
        )
        assert status_root.PROJECT_ROOT == REPO_ROOT
        assert status_ex.PROJECT_ROOT == REPO_ROOT
        assert status_root.count_protocols(hybrid_root) == 6
        assert status_ex.count_protocols(hybrid_root) == 6

        monkeypatch.setattr(status_root, "PROJECT_ROOT", hybrid_root)
        assert status_root.count_protocols() == 6

    def test_protocol_heatmap_collects_prefixed_numeric_and_framework_ids(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        heatmap = _load_module(
            "protocol_heatmap",
            REPO_ROOT / "examples" / "scripts" / "protocol_heatmap.py",
        )
        monkeypatch.setattr(heatmap, "ROOT", hybrid_root)
        known = heatmap.get_known_protocols()
        assert {"P530", "P062", "P075", "P001", "P409"}.issubset(known)
        assert "P999" not in known
        assert "P998" not in known


class TestLiveRepoParity:
    """Smoke-check real Athena-Public repository layout."""

    def test_live_repo_discovery_and_summary_links(self):
        import athena.core.config as cfg

        cfg.set_project_root(REPO_ROOT)
        try:
            dirs = cfg.get_protocol_dirs(REPO_ROOT)
            assert REPO_ROOT / "examples" / "protocols" in dirs
            assert REPO_ROOT / ".framework" / "v8.2-stable" / "protocols" in dirs

            active_files = cfg.iter_protocol_files(REPO_ROOT)
            assert len(active_files) >= 140
            assert all("_archived" not in p.parts for p in active_files)
            assert all(p.name not in {"README.md", "INDEX.md"} for p in active_files)
        finally:
            cfg.set_project_root(None)


class TestPhase2RepoWideFixes:
    """Regression tests for Phase 2 repo-wide path, depth, and parser fixes."""

    def test_sync_extracts_prefixed_and_framework_protocol_codes(self):
        import athena.memory.sync as mem_sync

        ex_sync = _load_module(
            "examples_engine_sync",
            REPO_ROOT / "examples" / "engine" / "sync.py",
        )
        cases = {
            "ARC-530-conditional-skill.md": "530",
            "SGP-sg-001-randian.md": "001",
            "075-cognitive-engine.md": "075",
            "409_Parallel_Worktree.md": "409",
            "COM-adaptive-response.md": "000",
        }
        for mod in (mem_sync, ex_sync):
            for fname, expected in cases.items():
                data: dict = {}
                mod._enrich_data_by_table(data, Path(fname), "protocols", {})
                assert data["code"] == expected

    def test_auditors_and_generators_use_repo_root_and_examples_paths(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        import athena.auditors.audit_observations as obs
        import athena.auditors.audit_runner as runner
        import athena.cli.doctor as cli_doc
        import athena.generators.generate_protocol as gen_proto

        assert "examples/protocols/" in obs.CATEGORIES["protocols"]
        assert ".framework/" in obs.CATEGORIES["protocols"]
        assert "examples/workflows/" in obs.CATEGORIES["workflows"]
        assert runner.PROJECT_ROOT == REPO_ROOT

        monkeypatch.chdir(hybrid_root)
        ids = gen_proto.get_existing_protocol_ids()
        assert {530, 62, 75, 1, 409}.issubset(ids)
        assert 999 not in ids
        assert 998 not in ids
        assert gen_proto.check_for_collisions() == {}

        # cli.doctor orphan detection falls back to scripts/orphan_detector.py
        fake_root = hybrid_root / "fake_root"
        script_path = _write(
            fake_root / "scripts" / "orphan_detector.py",
            "print('0 orphans found')\n",
        )
        assert script_path.exists()
        results = cli_doc.check_06_orphan_detection(fake_root)
        assert len(results) == 1
        assert results[0].status == cli_doc.PASS

    def test_script_project_root_depths_and_retrieval_pipeline(
        self, hybrid_root: Path
    ):
        # Verify scripts relocated from .agent/ resolve to REPO_ROOT
        script_specs = [
            ("scripts_reflection", REPO_ROOT / "scripts" / "core" / "reflection.py"),
            ("scripts_auditor", REPO_ROOT / "scripts" / "core" / "auditor.py"),
            ("scripts_bootstrap_env", REPO_ROOT / "scripts" / "bootstrap_env.py"),
            ("scripts_context_monitor", REPO_ROOT / "scripts" / "context_monitor.py"),
            ("examples_athenad", REPO_ROOT / "examples" / "scripts" / "athenad.py"),
        ]
        for mod_name, path in script_specs:
            mod = _load_module(mod_name, path)
            assert mod.PROJECT_ROOT == REPO_ROOT, f"{path} resolved {mod.PROJECT_ROOT}"

        graphrag = _load_module(
            "scripts_graphrag",
            REPO_ROOT / "scripts" / "core" / "retrieval" / "graphrag.py",
        )
        g = graphrag.KnowledgeGraphParser()
        assert g.graph_path == REPO_ROOT / ".context" / "KNOWLEDGE_GRAPH.md"

        pipeline_mod = _load_module(
            "scripts_pipeline",
            REPO_ROOT / "scripts" / "core" / "retrieval" / "pipeline.py",
        )
        pipe = pipeline_mod.AthenaRetriever()
        assert pipe.project_root == REPO_ROOT

        pipe.project_root = hybrid_root
        hits = pipe._search_filenames("conditional")
        hit_paths = {Path(h.file_path).name for h in hits if h.file_path}
        assert "ARC-530-conditional-skill.md" in hit_paths
        retired_hits = pipe._search_filenames("retired")
        assert retired_hits == []

    def test_athena_doctor_workflows_fallback_and_template_placeholder_links(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        doctor = _load_module(
            "athena_doctor_phase2",
            REPO_ROOT / "examples" / "scripts" / "athena_doctor.py",
        )
        _write(
            hybrid_root / "examples" / "workflows" / "start.md",
            "---\ndescription: Boot sequence\n---\n\n# /start\n",
        )
        _write(
            hybrid_root / "README.md",
            "# Test\n\nSee [placeholder]({URL}) and [valid](docs/OK.md).\n",
        )
        _write(hybrid_root / "docs" / "OK.md", "# OK\n")
        _write(
            hybrid_root / "docs" / "SCHEDULED_TASKS.md",
            "| Name | Citation |\n|---|---|\n| {Name} | [{Citation}]({URL}) |\n",
        )

        monkeypatch.setattr(doctor, "PROJECT_ROOT", hybrid_root)
        wf_report = doctor.Report()
        doctor.check_workflows(wf_report)
        assert wf_report.findings[0].severity == "pass"
        assert "1 workflows defined" in wf_report.findings[0].message

        link_report = doctor.Report()
        doctor.check_dead_links(link_report)
        assert link_report.findings[0].severity == "pass"

    def test_example_scripts_and_engine_config_discovery(
        self, hybrid_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        compress = _load_module(
            "examples_compress_protocols",
            REPO_ROOT / "examples" / "scripts" / "compress_protocols.py",
        )
        assert compress.parse_protocol_code("ARC-530-conditional-skill.md") == "530"
        assert compress.parse_protocol_code("SGP-sg-001-randian.md") == "001"
        assert compress.parse_protocol_code("409_Parallel_Worktree.md") == "409"
        assert compress.parse_protocol_code("075-cognitive-engine.md") == "075"

        meta_ext = _load_module(
            "examples_metadata_extractor",
            REPO_ROOT / "examples" / "scripts" / "metadata_extractor.py",
        )
        assert meta_ext.PROJECT_ROOT == REPO_ROOT
        monkeypatch.setattr(meta_ext, "PROJECT_ROOT", hybrid_root)
        arc_meta = meta_ext.extract_metadata(
            hybrid_root / "examples" / "protocols" / "architecture" / "ARC-530-conditional-skill.md"
        )
        assert arc_meta is not None and arc_meta["id"] == "530"
        fw_meta = meta_ext.extract_metadata(
            hybrid_root / ".framework" / "v8.2-stable" / "protocols" / "409_Parallel_Worktree.md"
        )
        assert fw_meta is not None and fw_meta["id"] == "409"

        scaffold = _load_module(
            "examples_protocol_scaffold",
            REPO_ROOT / "examples" / "scripts" / "protocol_scaffold.py",
        )
        monkeypatch.setattr(scaffold, "PROJECT_ROOT", str(hybrid_root))
        monkeypatch.setattr(
            scaffold,
            "PROTOCOLS_DIR",
            str(hybrid_root / ".agent" / "skills" / "protocols"),
        )
        assert scaffold.get_next_protocol_number() == 531

        scan_skill = _load_module(
            "examples_scan_skill",
            REPO_ROOT / "examples" / "scripts" / "scan_skill.py",
        )
        scanned = {p.name for p in scan_skill.find_skill_files(hybrid_root)}
        assert "ARC-530-conditional-skill.md" in scanned
        assert "409_Parallel_Worktree.md" in scanned
        assert "ARC-999-retired.md" not in scanned
        assert "README.md" not in scanned

        repair = _load_module(
            "examples_repair_links",
            REPO_ROOT / "examples" / "scripts" / "repair_links.py",
        )
        monkeypatch.setattr(repair, "WORKSPACE", hybrid_root)
        monkeypatch.setattr(
            repair,
            "PROTOCOLS_DIR",
            hybrid_root / ".agent" / "skills" / "protocols",
        )
        monkeypatch.setattr(
            repair,
            "PUBLIC_PROTOCOLS_DIR",
            hybrid_root / "examples" / "protocols",
        )
        pmap = repair.build_protocol_map()
        assert "ARC-530-conditional-skill.md" in pmap
        assert "409_Parallel_Worktree.md" in pmap
        assert "ARC-999-retired.md" not in pmap

        regen_wf = _load_module(
            "examples_regenerate_workflow_index",
            REPO_ROOT / "examples" / "scripts" / "regenerate_workflow_index.py",
        )
        _write(
            hybrid_root / "examples" / "workflows" / "boot.md",
            "---\ndescription: Boot test\n---\n",
        )
        monkeypatch.chdir(hybrid_root)
        regen_wf.generate_index()
        wf_idx = (hybrid_root / ".agent" / "WORKFLOW_INDEX.md").read_text(encoding="utf-8")
        assert "`/boot`" in wf_idx

        ex_cfg = _load_module(
            "examples_engine_config",
            REPO_ROOT / "examples" / "engine" / "config.py",
        )
        assert ex_cfg.get_protocols_dir(hybrid_root) == hybrid_root / "examples" / "protocols"
        assert (
            hybrid_root / ".framework" / "v8.2-stable" / "protocols"
            in ex_cfg.get_protocol_dirs(hybrid_root)
        )

    def test_pre_commit_hook_syntax_valid(self):
        import subprocess

        res = subprocess.run(
            ["bash", "-n", str(REPO_ROOT / "scripts" / "hooks" / "pre-commit")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert res.returncode == 0, res.stderr

