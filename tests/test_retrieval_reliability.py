"""
Tests for SafeCrossEncoder and chunk verification (src/athena/tools/reranker.py & memory/sync.py).

These previously asserted `isinstance(res, bool)` for integrity and `len(res) == 1`
for the fallback path — both pass whether the code works or is catastrophically
broken. This is the retrieval path that shipped a silent regression the project's
own monitoring missed, so its tests should be able to detect one.
"""

import pytest

from athena.core.models import SearchResult
from athena.memory import sync as sync_module
from athena.memory.sync import verify_chunk_integrity
from athena.tools import reranker as reranker_module
from athena.tools.reranker import SafeCrossEncoder

# ── chunk integrity ──────────────────────────────────────────────────────────

class _FakeTable:
    def __init__(self, count):
        self._count = count

    def select(self, *_args, **_kwargs):
        return self

    def execute(self):
        return type("Res", (), {"count": self._count})()


class _FakeClient:
    def __init__(self, count):
        self._count = count

    def table(self, _name):
        return _FakeTable(self._count)


@pytest.fixture
def context_dir(tmp_path, monkeypatch):
    """A .context tree holding 10 indexable files."""
    root = tmp_path / "repo"
    ctx = root / ".context"
    ctx.mkdir(parents=True)
    for i in range(10):
        (ctx / f"doc_{i}.md").write_text("content", encoding="utf-8")
    monkeypatch.setattr(sync_module, "PROJECT_ROOT", root)
    return root


def test_integrity_fails_when_chunks_are_under_populated(context_dir, monkeypatch):
    """The whole point of the function: 10 local files, 1 chunk indexed -> False."""
    monkeypatch.setattr(sync_module, "get_client", lambda: _FakeClient(1))
    assert verify_chunk_integrity(expected_min_ratio=0.5) is False


def test_integrity_passes_when_chunks_are_populated(context_dir, monkeypatch):
    monkeypatch.setattr(sync_module, "get_client", lambda: _FakeClient(40))
    assert verify_chunk_integrity(expected_min_ratio=0.5) is True


def test_integrity_boundary_is_inclusive(context_dir, monkeypatch):
    """10 files x 0.5 = 5. Exactly 5 chunks is not under-population; 4 is."""
    monkeypatch.setattr(sync_module, "get_client", lambda: _FakeClient(5))
    assert verify_chunk_integrity(expected_min_ratio=0.5) is True
    monkeypatch.setattr(sync_module, "get_client", lambda: _FakeClient(4))
    assert verify_chunk_integrity(expected_min_ratio=0.5) is False


def test_integrity_ratio_is_honoured(context_dir, monkeypatch):
    """A stricter ratio must reject a chunk count a looser one accepts."""
    monkeypatch.setattr(sync_module, "get_client", lambda: _FakeClient(6))
    assert verify_chunk_integrity(expected_min_ratio=0.5) is True
    assert verify_chunk_integrity(expected_min_ratio=0.9) is False


def test_integrity_fails_open_when_db_is_unreachable(context_dir, monkeypatch):
    """Deliberate: an offline DB must not block local runs.

    Asserted rather than left implicit — a caller reading True as "verified"
    is wrong whenever the vector DB is unconfigured.
    """
    def _boom():
        raise RuntimeError("no vector DB configured")

    monkeypatch.setattr(sync_module, "get_client", _boom)
    assert verify_chunk_integrity(expected_min_ratio=0.5) is True


def test_integrity_passes_when_there_is_nothing_to_index(tmp_path, monkeypatch):
    monkeypatch.setattr(sync_module, "PROJECT_ROOT", tmp_path / "empty")
    assert verify_chunk_integrity(expected_min_ratio=0.5) is True


# ── reranker fallback ────────────────────────────────────────────────────────

def _docs(n):
    return [SearchResult(id=str(i), content=f"doc {i}", source=f"{i}.md") for i in range(n)]


def test_safe_cross_encoder_empty():
    encoder = SafeCrossEncoder()
    res, fallback = encoder.rerank("test query", [], top_k=5)
    assert res == []
    assert fallback is False


def test_fallback_flag_false_on_the_fast_path(monkeypatch):
    """ONNX scored the pairs — no degradation, so the caller must see False."""
    monkeypatch.setattr(reranker_module, "_predict_onnx", lambda pairs: [0.1] * len(pairs))
    res, fallback = SafeCrossEncoder().rerank("q", _docs(3), top_k=3)
    assert fallback is False
    assert len(res) == 3


def test_fallback_flag_true_when_no_model_is_available(monkeypatch):
    """ONNX unavailable and no CrossEncoder: degraded, and the caller must know."""
    monkeypatch.setattr(reranker_module, "_predict_onnx", lambda pairs: None)
    monkeypatch.setattr(reranker_module, "get_model", lambda: None)
    docs = _docs(4)
    res, fallback = SafeCrossEncoder().rerank("q", docs, top_k=2)
    assert fallback is True, "silent degradation is the regression class that shipped before"
    assert res == docs[:2], "degraded path must return the candidate slice unreordered"


def test_fallback_flag_true_when_scoring_raises(monkeypatch):
    def _boom(_pairs):
        raise RuntimeError("model exploded")

    monkeypatch.setattr(reranker_module, "_predict_onnx", _boom)
    res, fallback = SafeCrossEncoder().rerank("q", _docs(3), top_k=2)
    assert fallback is True
    assert len(res) == 2


def test_rerank_actually_reorders_by_score(monkeypatch):
    """The contract, not just the shape: highest score must come first."""
    scores = {"doc 0": 0.10, "doc 1": 0.90, "doc 2": 0.50}
    monkeypatch.setattr(
        reranker_module, "_predict_onnx", lambda pairs: [scores[c] for _q, c in pairs]
    )
    res, fallback = SafeCrossEncoder().rerank("q", _docs(3), top_k=3)
    assert fallback is False
    assert [d.content for d in res] == ["doc 1", "doc 2", "doc 0"]
    assert res[0].signals["reranker"]["score"] == 0.90


def test_rerank_respects_top_k(monkeypatch):
    monkeypatch.setattr(reranker_module, "_predict_onnx", lambda pairs: list(range(len(pairs))))
    res, _ = SafeCrossEncoder().rerank("q", _docs(6), top_k=2)
    assert len(res) == 2


# ── temporal decay in weighted_rrf ──────────────────────────────────────────

def test_temporal_decay_boosts_recent_sessions():
    """Sessions from 2026 must outrank equivalent 2024 sessions in weighted_rrf."""
    from athena.tools.search import weighted_rrf

    doc_2024 = SearchResult(
        id="Session:2024-05-10-session-S100.md",
        content="2024 trading discussion",
        source="session",
        score=0.8,
        metadata={"path": ".context/memories/session_logs/2024-05-10-session-S100.md"},
    )
    doc_2026 = SearchResult(
        id="Session:2026-08-20-session-S780.md",
        content="2026 trading discussion",
        source="session",
        score=0.8,
        metadata={"path": ".context/memories/session_logs/2026-08-20-session-S780.md"},
    )

    ranked_lists = {
        "session": [doc_2024, doc_2026],  # 2024 passed first in rank order
    }

    fused = weighted_rrf(ranked_lists, k=60)
    assert len(fused) == 2
    # 2026 has temporal_mod=1.15 vs 2024's 0.75, which overcomes rank 2 vs rank 1
    assert fused[0].id == "Session:2026-08-20-session-S780.md"
    assert fused[1].id == "Session:2024-05-10-session-S100.md"


def test_temporal_decay_preserves_timeless_protocols():
    """Protocols with year mentions in name or path must NOT be decayed."""
    from athena.tools.search import weighted_rrf

    protocol_with_year = SearchResult(
        id="Protocol:2024-governance-audit.md",
        content="Governance rules",
        source="protocol",
        score=0.9,
        metadata={"path": ".agent/skills/protocols/archive/2024-governance-audit.md"},
    )
    protocol_standard = SearchResult(
        id="Protocol:001-law-of-ruin.md",
        content="Law of ruin rules",
        source="protocol",
        score=0.9,
        metadata={"path": ".agent/skills/protocols/safety/SAF-001-law-of-ruin.md"},
    )

    ranked_lists = {
        "protocol": [protocol_with_year, protocol_standard],
    }

    fused = weighted_rrf(ranked_lists, k=60)
    # Neither protocol has temporal decay applied; rank order 1 then 2 is preserved purely by rank position
    assert fused[0].id == "Protocol:2024-governance-audit.md"
    assert fused[1].id == "Protocol:001-law-of-ruin.md"

