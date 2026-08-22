"""
tests.test_cache_scope
======================
Unit tests verifying query cache privacy and scope isolation.
"""

import tempfile
import unittest
from pathlib import Path

from athena.core.cache import QueryCache


class TestCacheScopeIsolation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache = QueryCache(cache_dir=Path(self.temp_dir.name), ttl_hours=1)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_exact_match_scope_isolation(self):
        """Verify queries under different scopes do not collide."""
        query = "quarterly trade PnL"
        personal_scope = {"personal": True, "limit": 5, "web": False}
        public_scope = {"personal": False, "limit": 5, "web": False}

        personal_data = [{"id": "Private:Account", "score": 1.0}]
        public_data = [{"id": "Public:Summary", "score": 0.8}]

        # Set under personal scope
        self.cache.set(query, personal_data, scope=personal_scope)

        # Retrieve under personal scope -> Hit
        self.assertEqual(self.cache.get(query, scope=personal_scope), personal_data)

        # Retrieve under public scope -> Miss (No leakage)
        self.assertIsNone(self.cache.get(query, scope=public_scope))

        # Set under public scope
        self.cache.set(query, public_data, scope=public_scope)

        # Retrieve under both -> isolated hits
        self.assertEqual(self.cache.get(query, scope=personal_scope), personal_data)
        self.assertEqual(self.cache.get(query, scope=public_scope), public_data)

    def test_semantic_scope_isolation(self):
        """Verify semantic similarity cache matches only within identical scopes."""
        vec_a = [1.0, 0.0, 0.0]
        vec_similar = [0.99, 0.05, 0.0]  # Very high cosine similarity

        personal_scope = {"personal": True}
        public_scope = {"personal": False}

        data = [{"id": "SecretDoc"}]

        # Store with vector and personal scope
        self.cache.set("query a", data, embedding=vec_a, scope=personal_scope)

        # Semantic query with similar vector in public scope -> Miss
        self.assertIsNone(
            self.cache.get_semantic(vec_similar, scope=public_scope, threshold=0.90)
        )

        # Semantic query with similar vector in personal scope -> Hit
        self.assertEqual(
            self.cache.get_semantic(vec_similar, scope=personal_scope, threshold=0.90),
            data,
        )

    def test_scope_none_vs_empty_dict_equivalence(self):
        """Verify None and empty dictionary scopes are normalized identically."""
        query = "normalized scope test"
        data = [{"id": "Item1"}]

        # Set with None scope
        self.cache.set(query, data, scope=None)

        # Retrieve with {} scope -> Hit (equivalent to None)
        self.assertEqual(self.cache.get(query, scope={}), data)

        # Retrieve with None scope -> Hit
        self.assertEqual(self.cache.get(query, scope=None), data)

    def test_search_result_dataclass_disk_persistence(self):
        """Verify SearchResult dataclass objects survive disk serialization and reloading."""
        from athena.core.models import SearchResult

        query = "decision protocol"
        results = [
            SearchResult(
                id="PR-01: Risk",
                content="Never risk ruin.",
                source="protocol",
                score=0.95,
                rrf_score=0.082,
                signals={"protocol": {"rank": 1, "contrib": 0.082}},
                metadata={"path": "protocols/risk.md"},
            )
        ]
        scope = {"limit": 5, "personal": False}

        # Store dataclass in cache
        self.cache.set(query, results, scope=scope)

        # Create a new cache instance pointing to the same directory (simulates process restart)
        reloaded_cache = QueryCache(cache_dir=Path(self.temp_dir.name), ttl_hours=1)
        reloaded_val = reloaded_cache.get(query, scope=scope)

        self.assertIsNotNone(reloaded_val)
        self.assertEqual(len(reloaded_val), 1)
        self.assertIsInstance(reloaded_val[0], SearchResult)
        self.assertEqual(reloaded_val[0].id, "PR-01: Risk")
        self.assertEqual(reloaded_val[0].content, "Never risk ruin.")
    def test_cache_invalidation(self):
        """Verify cache.invalidate() clears all entries."""
        self.cache.set("query", [{"id": "1"}], scope={"personal": False})
        self.assertIsNotNone(self.cache.get("query", scope={"personal": False}))

        self.cache.invalidate()
        self.assertIsNone(self.cache.get("query", scope={"personal": False}))


if __name__ == "__main__":
    unittest.main()
