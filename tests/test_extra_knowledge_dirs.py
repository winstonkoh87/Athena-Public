"""Tests for external Markdown vault directories (memory.extra_dirs / ATHENA_EXTRA_DIRS)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import athena.core.config as config  # noqa: E402
from athena.tools.fts_search import ExocortexFTS  # noqa: E402


def test_get_extra_knowledge_dirs_resolves_env_and_yaml(
    tmp_path: Path, monkeypatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    vault_env = tmp_path / "logseq_pages"
    vault_env.mkdir()
    vault_yaml = tmp_path / "obsidian_notes"
    vault_yaml.mkdir()

    (workspace / "athena.yaml").write_text(
        f"memory:\n  extra_dirs:\n    - {vault_yaml}\n    - /nonexistent/vault/xyz\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ATHENA_EXTRA_DIRS", str(vault_env))

    resolved = config.get_extra_knowledge_dirs(workspace)
    assert vault_env.resolve() in resolved
    assert vault_yaml.resolve() in resolved
    assert len(resolved) == 2


def test_fts_indexes_and_searches_external_vault(
    tmp_path: Path, monkeypatch
) -> None:
    workspace = tmp_path / "workspace"
    (workspace / ".context").mkdir(parents=True)
    (workspace / ".agent").mkdir(parents=True)
    (workspace / ".athena").mkdir(parents=True)

    ext_vault = tmp_path / "external_logseq"
    ext_vault.mkdir()
    note = ext_vault / "architecture_notes.md"
    note.write_text(
        "# External Vault Note\nUnique vault token: XENON_ORBITAL_CALIBRATION_991.\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("ATHENA_EXTRA_DIRS", str(ext_vault))
    monkeypatch.setattr(config, "PROJECT_ROOT", workspace)
    monkeypatch.setattr(config, "CONTEXT_DIR", workspace / ".context")
    monkeypatch.setattr(config, "AGENT_DIR", workspace / ".agent")

    fts = ExocortexFTS(db_path=tmp_path / "test_fts.db")
    stats = fts.build()
    assert stats["file_count"] >= 1

    hits = fts.search("XENON_ORBITAL_CALIBRATION_991", limit=5)
    assert len(hits) == 1
    assert "architecture_notes.md" in hits[0]["file_path"]
