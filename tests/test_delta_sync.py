"""
test_delta_sync.py — Verification suite for P0 Delta Sync.
"""

import sys
from pathlib import Path

import pytest

# Add src to sys.path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path / "src"))

from athena.memory.delta_manifest import DeltaManifest


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temp workspace for testing."""
    manifest_path = tmp_path / "manifest.json"
    file_a = tmp_path / "file_a.md"
    file_a.write_text("Content A", encoding="utf-8")
    return {"manifest_path": manifest_path, "file_a": file_a}


def test_hash_calculation(temp_workspace):
    """Falsification: Does hashing work and normalize?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])

    # Baseline
    h1 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 is not None

    # Whitespace change -> Same hash
    temp_workspace["file_a"].write_text("Content A\n", encoding="utf-8")
    h2 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 == h2

    # Content change -> New hash
    temp_workspace["file_a"].write_text("Content B", encoding="utf-8")
    h3 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 != h3


def test_should_sync_logic(temp_workspace):
    """Falsification: Does should_sync return correct booleans?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])
    f = temp_workspace["file_a"]

    # 1. New file -> Sync
    assert dm.should_sync(f) is True

    # 2. Update manifest (Simulate sync)
    dm.update_entry(f)
    dm.save()

    # 3. No change -> Skip
    # Reload manifest to check persistence
    dm2 = DeltaManifest(temp_workspace["manifest_path"])
    assert dm2.should_sync(f) is False

    # 4. Content Change -> Sync
    f.write_text("New Content", encoding="utf-8")
    assert dm2.should_sync(f) is True


def test_stale_detection(temp_workspace):
    """Falsification: Do we detect deleted files?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])
    f = temp_workspace["file_a"]

    # Register file
    dm.update_entry(f)

    # File exists -> Not stale
    assert dm.get_stale_files([f]) == []

    # File not passed in scan -> Stale
    assert len(dm.get_stale_files([])) == 1
    assert str(f) in dm.get_stale_files([])


def test_sync_file_to_supabase_does_not_duplicate_full_content_in_parent_table(tmp_path, monkeypatch):
    """sync_file_to_supabase stores chunk content in document_chunks and keeps parent content empty."""
    from athena.memory import sync as sync_mod

    sample = tmp_path / "2026-11-14-session-99.md"
    sample.write_text("# Session 99\n\nUnique Body Text for halfvec compaction test.\n", encoding="utf-8")

    upserts: list[tuple[str, dict, str | None]] = []

    class _QueryStub:
        def __init__(self, table_name: str):
            self.table_name = table_name

        def delete(self):
            return self

        def eq(self, _col: str, _val: str):
            return self

        def upsert(self, payload: dict, on_conflict: str | None = None):
            upserts.append((self.table_name, dict(payload), on_conflict))
            return self

        def execute(self):
            return type("Resp", (), {"data": []})()

    class _ClientStub:
        def table(self, table_name: str):
            return _QueryStub(table_name)

    monkeypatch.setattr(sync_mod, "get_client", lambda: _ClientStub())
    monkeypatch.setattr(sync_mod, "get_embedding", lambda _text, **_kw: [0.1] * 8)

    ok = sync_mod.sync_file_to_supabase(sample, "sessions")
    assert ok is True

    chunk_upserts = [u for u in upserts if u[0] == "document_chunks"]
    parent_upserts = [u for u in upserts if u[0] == "sessions"]
    assert len(chunk_upserts) >= 1
    assert "Unique Body Text" in chunk_upserts[0][1]["content"]
    assert chunk_upserts[0][1]["embedding"] == [0.1] * 8

    assert len(parent_upserts) == 1
    assert parent_upserts[0][1]["content"] == ""
    assert "embedding" not in parent_upserts[0][1]
    assert parent_upserts[0][1]["session_number"] == 99
