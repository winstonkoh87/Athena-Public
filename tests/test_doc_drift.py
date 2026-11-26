"""Tests for scripts/check_doc_drift.py."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_doc_drift import (  # noqa: E402
    check_agents_hooks,
    check_agents_index,
    check_athena_yaml,
    check_hook_paths,
    check_markdown_links,
    check_tracked_docs,
    parse_tracks_frontmatter,
)


def test_parse_tracks_frontmatter_inline_and_block() -> None:
    inline = "---\ntracks: [src/a.py, src/b.py]\n---\n# Title\n"
    assert parse_tracks_frontmatter(inline) == ["src/a.py", "src/b.py"]

    block = "---\ntitle: Doc\ntracks:\n  - src/a.py\n  - scripts/b.py  # comment\n---\n# Title\n"
    assert parse_tracks_frontmatter(block) == ["src/a.py", "scripts/b.py"]


def test_broken_markdown_link_detected(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("See [Missing](docs/MISSING.md) and [External](https://example.com).\n", encoding="utf-8")
    findings = check_markdown_links(readme, tmp_path)
    assert len(findings) == 1
    assert findings[0]["code"] == "BROKEN_LINK"
    assert findings[0]["target"] == "docs/MISSING.md"


def test_agents_index_flags_retired_and_allows_negative_mention(tmp_path: Path) -> None:
    (tmp_path / "src" / "athena").mkdir(parents=True)
    (tmp_path / "src" / "athena" / "real.py").write_text("", encoding="utf-8")

    agents_bad = tmp_path / "AGENTS.md"
    agents_bad.write_text(
        "- State: `.context/TAG_INDEX.md`, `.context/project_state.md`, `src/athena/ghost.py`\n",
        encoding="utf-8",
    )
    findings = check_agents_index(agents_bad, tmp_path)
    codes = {f["code"] for f in findings}
    assert "RETIRED_INDEX_REF" in codes
    assert "MISSING_INDEX_PATH" in codes

    agents_good = tmp_path / "AGENTS.md"
    agents_good.write_text(
        "- Never rely on retired `TAG_INDEX.md` or deprecated `project_state.md`.\n"
        "- Active: `src/athena/real.py`\n",
        encoding="utf-8",
    )
    assert check_agents_index(agents_good, tmp_path) == []


def test_tracked_docs_detect_drift_and_missing_targets(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    src_dir = tmp_path / "src"
    docs_dir.mkdir()
    src_dir.mkdir()

    src_file = src_dir / "engine.py"
    src_file.write_text("def run(): pass\n", encoding="utf-8")
    doc_file = docs_dir / "ENGINE.md"
    doc_file.write_text(
        "---\ntracks:\n  - src/engine.py\n---\n# Engine\n",
        encoding="utf-8",
    )

    now = time.time()
    os.utime(doc_file, (now - 3600, now - 3600))
    os.utime(src_file, (now, now))

    findings = check_tracked_docs(tmp_path)
    assert len(findings) == 1
    assert findings[0]["code"] == "DRIFTED"
    assert findings[0]["severity"] == "warning"

    missing_doc = docs_dir / "BROKEN_TRACK.md"
    missing_doc.write_text("---\ntracks: [src/missing.py]\n---\n# Broken\n", encoding="utf-8")
    all_findings = check_tracked_docs(tmp_path)
    assert any(f["code"] == "MISSING_TRACKED_TARGET" for f in all_findings)


def test_hook_paths_and_athena_yaml_checks(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    settings = claude_dir / "settings.json"
    settings.write_text(
        '{"hooks": {"Stop": [{"hooks": [{"command": "python3 .agent/scripts/missing.py"}]}]}}',
        encoding="utf-8",
    )
    hook_findings = check_hook_paths(settings, tmp_path)
    assert len(hook_findings) == 1
    assert hook_findings[0]["code"] == "MISSING_HOOK_SCRIPT"

    yaml_file = tmp_path / "athena.yaml"
    yaml_file.write_text("hooks:\n  # See hooks/hooks.yaml\nruntime:\n  boot_tokens: 10000\n", encoding="utf-8")
    yaml_findings = check_athena_yaml(yaml_file, tmp_path)
    yaml_codes = {f["code"] for f in yaml_findings}
    assert yaml_codes == {"STALE_BOOT_BUDGET", "DEAD_COMMENT_REF"}


def test_agents_hooks_check_catches_missing_and_allows_valid(tmp_path: Path) -> None:
    agents_dir = tmp_path / ".agents"
    scripts_dir = tmp_path / ".agent" / "scripts"
    agents_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "ok.py").write_text("", encoding="utf-8")

    hooks_json = agents_dir / "hooks.json"
    hooks_json.write_text(
        '{"gate": {"PreToolUse": [{"matcher": "run_command", "hooks": [{"command": ".agent/scripts/ok.py"}, {"command": ".agent/scripts/ghost.py"}]}], "Stop": [{"command": ".agent/scripts/ok.py"}]}}',
        encoding="utf-8",
    )
    findings = check_agents_hooks(hooks_json, tmp_path)
    assert len(findings) == 1
    assert findings[0]["code"] == "MISSING_HOOK_SCRIPT"
    assert findings[0]["target"] == ".agent/scripts/ghost.py"

    (scripts_dir / "ghost.py").write_text("", encoding="utf-8")
    assert check_agents_hooks(hooks_json, tmp_path) == []


def test_live_repo_doc_drift_check_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "check_doc_drift.py"), "--root", str(REPO_ROOT), "--check"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, f"check_doc_drift failed:\n{proc.stdout}\n{proc.stderr}"
