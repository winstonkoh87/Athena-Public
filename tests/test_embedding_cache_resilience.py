"""Tests that PersistentEmbeddingCache gracefully handles SQLite corruption, disk errors, or malformed state."""

import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

from athena.memory.vectors import PersistentEmbeddingCache


def test_embedding_cache_handles_corrupt_database_on_get():
    """When the SQLite cache database is malformed or corrupted, get() must return None (cache miss) instead of crashing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "corrupt.db"

        cache = PersistentEmbeddingCache.__new__(PersistentEmbeddingCache)
        cache.legacy_json = Path(tmpdir) / "dummy.json"
        cache.db_path = db_path
        cache.lock = MagicMock()
        cache.lock.__enter__.return_value = None
        cache.lock.__exit__.return_value = None
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.DatabaseError("database disk image is malformed")
        cache._conn = mock_conn

        # In pre-fix state, cache.get() will raise sqlite3.DatabaseError
        # In post-fix state, it must return None gracefully
        result = cache.get("test_hash")
        assert result is None


def test_embedding_cache_handles_corrupt_database_on_set():
    """When SQLite fails on set(), it must not crash the caller."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "corrupt.db"
        cache = PersistentEmbeddingCache.__new__(PersistentEmbeddingCache)
        cache.legacy_json = Path(tmpdir) / "dummy.json"
        cache.db_path = db_path
        cache.lock = MagicMock()
        cache.lock.__enter__.return_value = None
        cache.lock.__exit__.return_value = None
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.DatabaseError("database disk image is malformed")
        cache._conn = mock_conn

        # In pre-fix state, cache.set() will raise sqlite3.DatabaseError
        # In post-fix state, it must catch and not raise
        cache.set("test_hash", [0.1, 0.2, 0.3])


def test_cache_key_includes_model_task_and_dims():
    """F-03 regression test: Cache key must namespace model, task_type, and dims."""
    from athena.memory.vectors import _hash_text

    h_query = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_QUERY", dims=3072)
    h_doc = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_DOCUMENT", dims=3072)
    h_diff_model = _hash_text("alpha", model="gemini-embedding-002", task_type="RETRIEVAL_QUERY", dims=3072)
    h_diff_dims = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_QUERY", dims=1536)

    assert h_query != h_doc, "RETRIEVAL_QUERY and RETRIEVAL_DOCUMENT must produce distinct cache hashes!"
    assert h_query != h_diff_model, "Different models must produce distinct cache hashes!"
    assert h_query != h_diff_dims, "Different dimensions must produce distinct cache hashes!"
    assert len(h_query) == 64, "Expected SHA-256 (64 hex characters) hash"


def test_embedding_cache_self_heals_malformed_db_on_disk(tmp_path, monkeypatch):
    """Malformed on-disk SQLite DB must be quarantined and recreated immediately without stalling."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    db_path = state_dir / "embedding_cache.db"
    db_path.write_bytes(b"not a valid sqlite database" * 100)
    monkeypatch.setattr("athena.core.config.AGENT_DIR", tmp_path)

    t0 = time.perf_counter()
    cache = PersistentEmbeddingCache()
    assert cache.get("k1") is None
    cache.set("k1", [0.1, 0.2])
    got = cache.get("k1")
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.5, f"Malformed DB self-heal took {elapsed:.3f}s (>= 0.5s)"
    assert got == [0.1, 0.2]
    corrupt_backups = list(state_dir.glob("embedding_cache.db.corrupt*"))
    assert corrupt_backups, "Expected malformed DB to be quarantined as *.corrupt*"


def test_get_embedding_respects_timeout_and_zero_floor_delay(monkeypatch):
    """Interactive get_embedding calls can pass short timeout and floor_delay=0.0 without sleeping."""
    from athena.memory import vectors

    monkeypatch.setenv("GOOGLE_API_KEY", "dummy-test-key")
    fake_cache = MagicMock()
    fake_cache.get.return_value = None
    monkeypatch.setattr(vectors, "get_embedding_cache", lambda: fake_cache)

    captured_kwargs = {}
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"embedding": {"values": [0.5] * 8}}

    def fake_post(url, **kwargs):
        captured_kwargs.update(kwargs)
        return mock_resp

    sleep_calls = []
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: True)
    monkeypatch.setattr(vectors.time, "sleep", lambda s: sleep_calls.append(s))

    emb = vectors.get_embedding("fast", max_retries=1, timeout=4.0, floor_delay=0.0)
    assert emb == [0.5] * 8
    assert captured_kwargs.get("timeout") == 4.0
    assert sleep_calls == []

