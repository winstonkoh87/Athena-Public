"""
Regression tests for MinMax Protocol Remediation & Latency Refactor.

Covers seam contracts and performance invariants across:
1. QueryCache read-hit zero-write & decoupled vector persistence (no float bloat in JSON).
2. search.py parallel execution: local channels must NOT block behind get_embedding().
3. mcp_server.context_gate concurrent Meta-Pattern searches + non-duplicated personalisation.
4. stop_governance_gate.py & hook_epistemic_gate.py O(1) tail reading on large JSONL logs.
5. smart_search.py in-process execution (no nested python -c subprocess).
6. scripts/boot_status.py fast batched execution + turn-1 boot token budget ceiling.
"""

from __future__ import annotations

import builtins
import inspect
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_query_cache_read_hits_do_not_rewrite_disk_and_decouples_vectors(tmp_path):
    """Cache hits must not trigger full-file _save_to_disk(), and vectors stay out of search_cache.json."""
    from athena.core.cache import QueryCache

    cache = QueryCache(cache_dir=tmp_path, ttl_hours=24)
    vec = [0.25] * 64
    scope = {"personal": False, "limit": 3}
    cache.set("minmax test query", [{"id": "doc1", "score": 0.9}], embedding=vec, scope=scope)

    json_text = (tmp_path / "search_cache.json").read_text(encoding="utf-8")
    raw_json = json.loads(json_text)
    for entry in raw_json.values():
        assert not entry.get("embedding"), "search_cache.json must not embed float arrays inline"

    # Reload in a fresh QueryCache instance and assert semantic hit still works + 0 saves on hit
    reloaded = QueryCache(cache_dir=tmp_path, ttl_hours=24)
    with patch.object(reloaded, "_save_to_disk", wraps=reloaded._save_to_disk) as save_spy:
        exact_hit = reloaded.get("minmax test query", scope=scope)
        semantic_hit = reloaded.get_semantic([0.25] * 64, scope=scope, threshold=0.90)
        assert exact_hit is not None
        assert semantic_hit is not None
        assert save_spy.call_count == 0, f"Cache read hits triggered {save_spy.call_count} disk rewrites"


def test_run_search_does_not_block_local_channels_on_embedding(tmp_path):
    """Local channels must launch immediately in parallel rather than waiting for synchronous get_embedding."""
    import athena.tools.search as search_mod
    from athena.core.cache import QueryCache
    from athena.core.models import SearchResult

    local_started_while_embed_blocked = False
    local_started = threading.Event()

    def slow_get_embedding(text, **kwargs):
        nonlocal local_started_while_embed_blocked
        # Block for up to 0.35s waiting for local channels to have started concurrently
        local_started_while_embed_blocked = local_started.wait(timeout=0.35)
        time.sleep(0.02)
        return [0.1] * 8

    def fake_fts(q):
        local_started.set()
        return [SearchResult(id="doc1", content="local fts hit", source="fts_bm25", score=0.9)]

    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=1)
    with (
        patch.object(search_mod, "get_search_cache", return_value=tmp_cache),
        patch.object(search_mod, "collect_canonical", return_value=[]),
        patch.object(search_mod, "collect_fts_bm25", side_effect=fake_fts),
        patch.object(search_mod, "collect_filenames", return_value=[]),
        patch.object(search_mod, "collect_framework_docs", return_value=[]),
        patch.object(search_mod, "collect_vectors", return_value=[]),
        patch("athena.memory.vectors.get_embedding", side_effect=slow_get_embedding),
    ):
        search_mod.run_search(
            "parallel local concurrency check",
            limit=3,
            rerank=False,
            json_output=True,
            print_output=False,
            web=False,
        )

    assert local_started_while_embed_blocked, (
        "Local channels blocked behind get_embedding() instead of launching in parallel"
    )


def test_context_gate_runs_meta_patterns_concurrently_and_deduplicates_personalisation():
    """MP searches in context_gate must run in parallel and avoid duplicate personalisation keys in context."""
    from athena.mcp_server import context_gate

    mps = [
        {"id": "MP-A", "name": "Pattern A", "search_terms": "pattern alpha", "description": "desc a"},
        {"id": "MP-B", "name": "Pattern B", "search_terms": "pattern beta", "description": "desc b"},
    ]

    def fake_run_search(query, **kwargs):
        if query in ("pattern alpha", "pattern beta"):
            time.sleep(0.25)
            return {"results": [{"id": f"doc-{query}", "content": "mp content", "rrf_score": 0.04}]}
        return {
            "results": [{"id": "primary-doc", "content": "primary", "rrf_score": 0.05}],
            "personalisation_context": "<personalisation_context>OPERATOR</personalisation_context>",
            "user_state": {"rate_floor": "S$150/hr"},
        }

    t0 = time.perf_counter()
    with (
        patch("athena.tools.meta_pattern_matcher.detect_latent_meta_patterns", return_value=mps),
        patch("athena.tools.search.run_search", side_effect=fake_run_search),
    ):
        res = context_gate("Should I quote S$300/hr for this client consulting project?", limit=3, web=False)
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.42, f"Meta-Pattern searches ran sequentially ({elapsed:.2f}s >= 0.42s)"
    assert "OPERATOR" in (res.get("personalisation") or "")
    assert "rate_floor" in (res.get("user_state") or {})
    # Context sub-bundle must not carry redundant duplicate personalisation copy
    assert "personalisation_context" not in res["context"]
    assert "user_state" not in res["context"]


def test_stop_and_epistemic_gates_use_bounded_tail_read(tmp_path, monkeypatch):
    """Reading tail of multi-MB JSONL logs must read <= 128 KB from EOF, not scan whole file."""
    import hook_epistemic_gate
    import stop_governance_gate

    # 1. Generate ~4 MB retrieval_receipts.jsonl with degraded receipt at EOF
    receipts_file = tmp_path / "retrieval_receipts.jsonl"
    ok_line = json.dumps({"ts": "2026-01-01T00:00:00Z", "quality": "hit", "pad": "x" * 160}) + "\n"
    degraded_line = json.dumps({"ts": "2026-11-14T00:00:00Z", "quality": "degraded"}) + "\n"
    with open(receipts_file, "w", encoding="utf-8") as f:
        for _ in range(20_000):
            f.write(ok_line)
        f.write(degraded_line)
    assert receipts_file.stat().st_size > 3_500_000

    # Transcript referencing context_gate
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "Analyze our pricing portfolio tradeoffs"}) + "\n"
        + json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "content": "Done.",
            "tool_calls": [{"name": "context_gate", "arguments": {"query": "pricing"}}],
        }) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(stop_governance_gate, "RETRIEVAL_RECEIPTS_PATH", receipts_file)
    monkeypatch.setattr(stop_governance_gate, "GATE_DECISIONS_PATH", tmp_path / "gate_decisions.jsonl")
    monkeypatch.setattr(stop_governance_gate, "LOOP_GUARD_PATH", tmp_path / "loop_guard.json")

    bytes_read_receipts = 0
    real_open = builtins.open

    def tracking_open(file, *args, **kwargs):
        fh = real_open(file, *args, **kwargs)
        if str(file) == str(receipts_file):
            class _Proxy:
                def __init__(self, inner):
                    self._inner = inner
                def __getattr__(self, name):
                    return getattr(self._inner, name)
                def __iter__(self):
                    nonlocal bytes_read_receipts
                    for line in self._inner:
                        bytes_read_receipts += len(line)
                        yield line
                def read(self, n=-1):
                    nonlocal bytes_read_receipts
                    data = self._inner.read(n)
                    bytes_read_receipts += len(data)
                    return data
                def readlines(self, hint=-1):
                    nonlocal bytes_read_receipts
                    lines = self._inner.readlines(hint)
                    bytes_read_receipts += sum(len(x) for x in lines)
                    return lines
                def __enter__(self):
                    self._inner.__enter__()
                    return self
                def __exit__(self, *exc):
                    return self._inner.__exit__(*exc)
            return _Proxy(fh)
        return fh

    with patch("builtins.open", side_effect=tracking_open):
        res = stop_governance_gate.evaluate_turn_governance(str(transcript))

    assert res["decision"] == "continue"
    assert "Degradation Guard" in res["reason"]
    assert bytes_read_receipts <= 131_072, f"Stop gate scanned {bytes_read_receipts} bytes instead of bounded tail"

    # 2. Generate ~4 MB invocations.jsonl with fresh web_search at EOF
    inv_file = tmp_path / "invocations.jsonl"
    old_inv = json.dumps({"timestamp": "2026-01-01T00:00:00+00:00", "type": "skill", "name": "smart_search", "pad": "y" * 160}) + "\n"
    fresh_inv = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "web_search",
        "grounding_status": "ok",
    }) + "\n"
    with open(inv_file, "w", encoding="utf-8") as f:
        for _ in range(20_000):
            f.write(old_inv)
        f.write(fresh_inv)
    assert inv_file.stat().st_size > 3_500_000

    bytes_read_inv = 0

    def tracking_open_inv(file, *args, **kwargs):
        fh = real_open(file, *args, **kwargs)
        if str(file) == str(inv_file):
            class _ProxyInv:
                def __init__(self, inner):
                    self._inner = inner
                def __getattr__(self, name):
                    return getattr(self._inner, name)
                def __iter__(self):
                    nonlocal bytes_read_inv
                    for line in self._inner:
                        bytes_read_inv += len(line)
                        yield line
                def read(self, n=-1):
                    nonlocal bytes_read_inv
                    data = self._inner.read(n)
                    bytes_read_inv += len(data)
                    return data
                def readlines(self, hint=-1):
                    nonlocal bytes_read_inv
                    lines = self._inner.readlines(hint)
                    bytes_read_inv += sum(len(x) for x in lines)
                    return lines
                def __enter__(self):
                    self._inner.__enter__()
                    return self
                def __exit__(self, *exc):
                    return self._inner.__exit__(*exc)
            return _ProxyInv(fh)
        return fh

    with patch("builtins.open", side_effect=tracking_open_inv):
        ok = hook_epistemic_gate.has_recent_grounding(max_age_seconds=180.0, invocations_path=inv_file)

    assert ok is True
    assert bytes_read_inv <= 131_072, f"Epistemic gate scanned {bytes_read_inv} bytes instead of bounded tail"


def test_smart_search_cli_avoids_nested_python_c_subprocess():
    """smart_search.run_full_search must execute in-process without spawning python -c."""
    import smart_search as ss_mod

    src = inspect.getsource(ss_mod.run_full_search)
    assert '"-c"' not in src and "subprocess.run" not in src, (
        "smart_search.run_full_search still spawns a nested python -c subprocess"
    )


def test_boot_status_fast_and_clean(tmp_path):
    """scripts/boot_status.py --json must complete in < 1.5s without RuntimeWarning."""
    script = REPO_ROOT / "scripts" / "boot_status.py"
    assert script.exists(), "scripts/boot_status.py does not exist"
    athena_py = REPO_ROOT / ".agent" / "scripts" / "athena-py"
    runner = str(athena_py) if (athena_py.exists() and os.access(athena_py, os.X_OK)) else sys.executable
    env = {**os.environ, "ATHENA_ROOT": str(tmp_path)}

    t0 = time.perf_counter()
    proc = subprocess.run(
        [runner, str(script), "--json"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    elapsed = time.perf_counter() - t0
    assert proc.returncode == 0, f"boot_status.py failed: {proc.stderr}"
    assert "RuntimeWarning" not in proc.stderr, f"boot_status.py emitted RuntimeWarning: {proc.stderr}"
    assert elapsed < 1.5, f"boot_status.py exceeded fast boot budget: {elapsed:.2f}s"

    data = json.loads(proc.stdout)
    for key in ("accountability", "maintenance_ratio", "frame_ledger", "decisions_due", "index_health", "context_summaries"):
        assert key in data, f"Missing '{key}' in boot_status output"


def test_boot_docs_under_minmax_token_budget():
    """Combined Turn-1 mandatory boot docs (AGENTS.md + _shared.md + start.md) must be <= 16,000 bytes (~4K tokens)."""
    total_bytes = sum(
        (REPO_ROOT / rel).stat().st_size
        for rel in ("AGENTS.md", ".agent/workflows/_shared.md", ".agent/workflows/start.md")
    )
    assert total_bytes <= 16_000, f"Boot docs total {total_bytes} bytes (> 16,000 bytes / ~4K token SLO)"


def test_vector_mode_auto_speculative_local_fast_path(tmp_path):
    """In vector_mode='auto', strong local+ONNX hits short-circuit slow vector retrieval cleanly."""
    import athena.tools.search as search_mod
    from athena.core.cache import QueryCache
    from athena.core.models import SearchResult

    release_vector = threading.Event()
    vector_called = threading.Event()

    def blocked_embedding(text, **kwargs):
        vector_called.set()
        release_vector.wait(timeout=2.0)
        return [0.1] * 8

    local_hits = [
        SearchResult(id="doc-alpha", content="strong local hit alpha", source="fts_bm25", score=0.95),
        SearchResult(id="doc-beta", content="strong local hit beta", source="canonical", score=0.90),
    ]

    def fake_rerank(query, candidates, top_k=10):
        out = list(candidates[:top_k])
        for i, item in enumerate(out):
            item.signals = dict(item.signals or {})
            item.signals["reranker"] = {"score": 3.5 - i}
        return out

    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=1)
    try:
        with (
            patch.object(search_mod, "get_search_cache", return_value=tmp_cache),
            patch.object(search_mod, "collect_canonical", return_value=[local_hits[1]]),
            patch.object(search_mod, "collect_fts_bm25", return_value=[local_hits[0]]),
            patch.object(search_mod, "collect_filenames", return_value=[]),
            patch.object(search_mod, "collect_framework_docs", return_value=[]),
            patch.object(search_mod, "collect_vectors", return_value=[]),
            patch("athena.memory.vectors.get_embedding", side_effect=blocked_embedding),
            patch("athena.tools.reranker.rerank_results", side_effect=fake_rerank),
        ):
            t0 = time.perf_counter()
            res = search_mod.run_search(
                "speculative auto fast path query",
                limit=3,
                rerank=True,
                json_output=True,
                print_output=False,
                web=False,
                vector_mode="auto",
            )
            elapsed = time.perf_counter() - t0
    finally:
        release_vector.set()

    assert elapsed < 0.5, f"Speculative auto fast path waited too long ({elapsed:.2f}s >= 0.5s)"
    assert vector_called.is_set()
    assert res["degraded_recall"] is False
    assert res["rerank_used"] is True
    assert {r["id"] for r in res["results"]} == {"doc-alpha", "doc-beta"}


def test_vector_mode_auto_quality_floor_escalates_to_vector(tmp_path):
    """In vector_mode='auto', weak local ONNX logits must wait for and include remote vector hits."""
    import athena.tools.search as search_mod
    from athena.core.cache import QueryCache
    from athena.core.models import SearchResult

    local_hits = [
        SearchResult(id="weak-fts", content="weak match one", source="fts_bm25", score=0.4),
        SearchResult(id="weak-canon", content="weak match two", source="canonical", score=0.3),
    ]
    vec_hit = SearchResult(id="vec-authoritative", content="authoritative protocol match", source="protocol", score=0.98)

    def slow_embedding(text, **kwargs):
        time.sleep(0.08)
        return [0.2] * 8

    def fake_rerank(query, candidates, top_k=10):
        out = []
        for item in candidates:
            item.signals = dict(item.signals or {})
            item.signals["reranker"] = {"score": 4.2 if item.id == "vec-authoritative" else -1.5}
            out.append(item)
        out.sort(key=lambda r: r.signals["reranker"]["score"], reverse=True)
        return out[:top_k]

    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=1)
    with (
        patch.object(search_mod, "get_search_cache", return_value=tmp_cache),
        patch.object(search_mod, "collect_canonical", return_value=[local_hits[1]]),
        patch.object(search_mod, "collect_fts_bm25", return_value=[local_hits[0]]),
        patch.object(search_mod, "collect_filenames", return_value=[]),
        patch.object(search_mod, "collect_framework_docs", return_value=[]),
        patch.object(search_mod, "collect_vectors", return_value=[vec_hit]),
        patch("athena.memory.vectors.get_embedding", side_effect=slow_embedding),
        patch("athena.tools.reranker.rerank_results", side_effect=fake_rerank),
    ):
        res = search_mod.run_search(
            "weak local quality floor escalation query",
            limit=3,
            rerank=True,
            json_output=True,
            print_output=False,
            web=False,
            vector_mode="auto",
        )

    assert res["degraded_recall"] is False
    ids = [r["id"] for r in res["results"]]
    assert ids[0] == "vec-authoritative", f"Expected escalated vector hit first, got {ids}"


def test_maxmax_workflows_curated_boot_and_athena_py_wiring():
    """MaxMax workflows must avoid bare python3 scripts, wire boot_status.py, enforce <=40K boot, and stay <=24KB."""
    wf_dir = REPO_ROOT / ".agent" / "workflows"
    ultra_files = [wf_dir / name for name in ("ultrastart.md", "ultraend.md", "ultrathink.md")]

    total_bytes = 0
    texts: dict[str, str] = {}
    for path in ultra_files:
        text = path.read_text(encoding="utf-8")
        texts[path.name] = text
        total_bytes += path.stat().st_size
        assert "python3 .agent/scripts/" not in text, (
            f"{path.name} still calls bare 'python3 .agent/scripts/' instead of '.agent/scripts/athena-py'"
        )
        assert ".agent/scripts/athena-py" in text, f"{path.name} missing .agent/scripts/athena-py invocation"

    ustart = texts["ultrastart.md"]
    assert "scripts/boot_status.py" in ustart, "ultrastart.md must wire .agent/scripts/athena-py scripts/boot_status.py"
    assert "40K" in ustart and "20%" in ustart and "200K" in ustart, (
        "ultrastart.md must enforce <=40K (<20% of 200K ECL) curated boot ceiling"
    )
    assert "L1-185" in ustart or "1-185" in ustart, "ultrastart.md must slice CANONICAL.md L1-185 surgically"
    assert "L1009-1067" in ustart or "1009-1067" in ustart, (
        "ultrastart.md must slice PROJECTS.md switchboard tables (L1009-1067) surgically"
    )
    assert "/tmp/ultrathink_context.md" not in texts["ultrathink.md"], (
        "ultrathink.md must stage context in .agent/state/ultrathink_context.md rather than /tmp"
    )
    assert ".agent/state/ultrathink_context.md" in texts["ultrathink.md"]
    assert total_bytes <= 24_000, f"Combined MaxMax workflows total {total_bytes} bytes (> 24,000 byte budget)"


