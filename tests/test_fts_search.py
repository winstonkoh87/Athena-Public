"""
Tests for the Offline Local FTS5/BM25 Search Engine.
"""

import pytest

from athena.tools.fts_search import ExocortexFTS


@pytest.fixture
def temp_project(tmp_path, monkeypatch):
    # Mock PROJECT_ROOT and other dirs
    import athena.core.config as config
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(config, "CONTEXT_DIR", tmp_path / ".context")
    monkeypatch.setattr(config, "AGENT_DIR", tmp_path / ".agent")

    # Create directories
    (tmp_path / ".context").mkdir()
    (tmp_path / ".agent" / "skills").mkdir(parents=True)
    (tmp_path / ".agent" / "workflows").mkdir(parents=True)
    (tmp_path / ".athena").mkdir()

    return tmp_path

def create_md(project_path, rel_path, content):
    p = project_path / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return p

def test_build_index(temp_project):
    create_md(temp_project, ".context/doc1.md", "# First Doc\nHello world")

    db_path = temp_project / ".athena" / "exocortex_fts.db"
    fts = ExocortexFTS(db_path=db_path)

    # Also patch _get_md_files to use our mock paths
    def mock_get_md_files(self):
        return [temp_project / ".context/doc1.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)

    res = fts.build()
    assert res['file_count'] == 1
    assert res['total_size'] > 0
    assert "elapsed_time" in res

def test_bm25_search(temp_project):
    create_md(temp_project, ".context/doc1.md", "# Test Doc\nThis is a bm25 ranking test.")
    create_md(temp_project, ".context/doc2.md", "# Another Doc\nThis has no matching words.")

    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)

    def mock_get_md_files(self):
        return [temp_project / ".context/doc1.md", temp_project / ".context/doc2.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)

    fts.build()
    results = fts.search("ranking")
    assert len(results) == 1
    assert "bm25" in results[0]['title'].lower() or "test doc" in results[0]['title'].lower()

def test_exact_search(temp_project):
    create_md(temp_project, ".context/doc1.md", "# Exact\nFind this exact phrase.")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/doc1.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search_exact("exact phrase")
    assert len(res) == 1

    res2 = fts.search_exact("phrase exact")
    assert len(res2) == 0

def test_prefix_search(temp_project):
    create_md(temp_project, ".context/doc1.md", "# Prefix\nAutocompletion is cool.")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/doc1.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search_prefix("Autocomp")
    assert len(res) == 1
    assert res[0]['title'] == "Prefix"

def test_empty_query(temp_project):
    fts = ExocortexFTS(db_path=temp_project / ".athena/test.db")
    assert fts.search("") == []
    assert fts.search_exact("   ") == []
    assert fts.search_prefix("") == []

def test_no_headings(temp_project):
    create_md(temp_project, ".context/nohead.md", "Just some regular text without headings.")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/nohead.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search("regular")
    assert len(res) == 1
    assert res[0]['title'] == "nohead.md" # defaults to filename

def test_unicode_content(temp_project):
    create_md(temp_project, ".context/uni.md", "# 🌟 Unicode\nHello 🌍 world.")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/uni.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search("world")
    assert len(res) == 1
    assert "Unicode" in res[0]['title']

def test_persistence_reopen(temp_project):
    create_md(temp_project, ".context/persist.md", "# Persist\nData should persist.")
    db_path = temp_project / ".athena" / "test.db"

    fts1 = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/persist.md"]
    fts1._get_md_files = mock_get_md_files.__get__(fts1, ExocortexFTS)
    fts1.build()

    # Reopen
    fts2 = ExocortexFTS(db_path=db_path)
    res = fts2.search("persist")
    assert len(res) == 1

def test_stats_computation(temp_project):
    create_md(temp_project, ".context/s1.md", "# S1\ntext")
    create_md(temp_project, ".context/s2.md", "# S2\ntext")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / ".context/s1.md", temp_project / ".context/s2.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    stats = fts.stats()
    assert stats['file_count'] == 2
    assert stats['total_size'] > 0
    assert stats['indexed_at'] > 0

def test_reindex_clears_old_data(temp_project):
    p1 = create_md(temp_project, ".context/r1.md", "# R1\nold data")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)

    def mock_get_md_files1(self):
        return [p1]
    fts._get_md_files = mock_get_md_files1.__get__(fts, ExocortexFTS)
    fts.build()

    assert len(fts.search("old")) == 1

    # Change file and reindex
    p2 = create_md(temp_project, ".context/r2.md", "# R2\nnew data")
    def mock_get_md_files2(self):
        return [p2]
    fts._get_md_files = mock_get_md_files2.__get__(fts, ExocortexFTS)
    fts.build()

    assert len(fts.search("old")) == 0
    assert len(fts.search("new")) == 1

def test_extract_title():
    fts = ExocortexFTS()
    content = "Some text\n# Actual Title \nMore text"
    assert fts._extract_title(content, "default") == "Actual Title"

def test_stats_no_index(temp_project):
    db_path = temp_project / ".athena" / "nonexistent.db"
    fts = ExocortexFTS(db_path=db_path)
    stats = fts.stats()
    assert stats['file_count'] == 0

def test_search_no_index(temp_project):
    db_path = temp_project / ".athena" / "nonexistent.db"
    fts = ExocortexFTS(db_path=db_path)
    res = fts.search("query")
    assert res == []

def test_search_bad_syntax(temp_project):
    create_md(temp_project, ".context/doc.md", "hello")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self): return [temp_project / ".context/doc.md"]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search('hello "')
    assert isinstance(res, list)

def test_limit(temp_project):
    create_md(temp_project, ".context/doc1.md", "# L1\nword")
    create_md(temp_project, ".context/doc2.md", "# L2\nword")
    create_md(temp_project, ".context/doc3.md", "# L3\nword")
    db_path = temp_project / ".athena" / "test.db"
    fts = ExocortexFTS(db_path=db_path)
    def mock_get_md_files(self):
        return [temp_project / f".context/doc{i}.md" for i in range(1,4)]
    fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
    fts.build()

    res = fts.search("word", limit=2)
    assert len(res) == 2


class TestCollectFtsBm25:
    """Integration tests for the collect_fts_bm25 pipeline wrapper."""

    def test_collect_fts_bm25_returns_list(self, temp_project):
        """collect_fts_bm25 always returns a list (possibly empty)."""
        from athena.tools.search import collect_fts_bm25

        result = collect_fts_bm25("nonexistent query xyz")
        assert isinstance(result, list)

    def test_collect_fts_bm25_returns_search_results(self, temp_project):
        """collect_fts_bm25 returns SearchResult objects with correct source."""
        from athena.core.models import SearchResult
        from athena.tools.fts_search import ExocortexFTS

        # Create a doc and build an FTS index
        create_md(temp_project, ".context/pipeline.md", "# Pipeline\nHybrid retrieval pipeline test.")
        db_path = temp_project / ".athena" / "exocortex_fts.db"
        fts = ExocortexFTS(db_path=db_path)

        def mock_get_md_files(self):
            return [temp_project / ".context/pipeline.md"]
        fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)
        fts.build()

        from athena.tools.search import collect_fts_bm25
        results = collect_fts_bm25("pipeline")
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, SearchResult)
            assert r.source == "fts_bm25"
            assert r.rrf_score == 0.0

    def test_collect_fts_bm25_graceful_on_missing_db(self, temp_project, monkeypatch):
        """collect_fts_bm25 returns [] when no FTS DB exists and build is mocked to fail."""
        import athena.core.config as config
        # Point to a non-existent path that can't be built
        monkeypatch.setattr(config, "PROJECT_ROOT", temp_project / "nonexistent_root")

        from athena.tools.search import collect_fts_bm25
        result = collect_fts_bm25("anything")
        assert result == []

    def test_build_and_search_roundtrip(self, temp_project):
        """ExocortexFTS can build an index and immediately search it."""
        create_md(temp_project, ".context/roundtrip.md", "# Roundtrip\nVerify build then search works end to end.")
        db_path = temp_project / ".athena" / "roundtrip.db"
        fts = ExocortexFTS(db_path=db_path)

        def mock_get_md_files(self):
            return [temp_project / ".context/roundtrip.md"]
        fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)

        build_result = fts.build()
        assert build_result["file_count"] == 1

        search_results = fts.search("roundtrip")
        assert len(search_results) >= 1
        assert search_results[0]["title"] == "Roundtrip"

    def test_compile_fts_query_syntax_safety(self):
        """compile_fts_query properly preserves hyphenated terms and strips syntax crash triggers."""
        from athena.tools.fts_search import compile_fts_query

        assert compile_fts_query("CS-101") == '"CS-101"'
        assert compile_fts_query("what did I decide about Project42?") == "what did I decide about Project42"
        assert compile_fts_query("Project42: what was decided?") == "Project42 what was decided"
        assert '"AND"' in compile_fts_query("AND OR NOT")
        assert compile_fts_query('stray * and ? test') == "stray and test"

    def test_search_hyphen_and_punctuation_recall(self, temp_project):
        """search() handles hyphenated codes and question marks without syntax errors or dropping recall."""
        create_md(temp_project, ".context/cs101.md", "# Case Study CS-101\nDistributed consensus protocol and replication mechanics.")
        create_md(temp_project, ".context/doc123.md", "# Module DOC-123 Specification\nHere is what I did decide about DOC-123 architecture.")
        db_path = temp_project / ".athena" / "resilient.db"
        fts = ExocortexFTS(db_path=db_path)

        def mock_get_md_files(self):
            return [temp_project / ".context/cs101.md", temp_project / ".context/doc123.md"]
        fts._get_md_files = mock_get_md_files.__get__(fts, ExocortexFTS)

        fts.build()
        hits_hyphen = fts.search("CS-101 distributed consensus")
        assert len(hits_hyphen) == 1
        assert "cs101.md" in hits_hyphen[0]["file_path"].lower()

        hits_question = fts.search("what did I decide about DOC-123?")
        assert len(hits_question) == 1
        assert "doc123.md" in hits_question[0]["file_path"].lower()


