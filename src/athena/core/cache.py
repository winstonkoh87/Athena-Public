"""
athena.core.cache — Semantic Query Cache
=========================================

A production-grade LRU cache with semantic similarity matching.

Features:
    - Exact Match: Hash-based O(1) lookup for identical queries
    - Semantic Match: Cosine similarity search for semantically similar queries
    - TTL Expiration: Entries expire after configurable time period
    - Disk Persistence: Cache survives process restarts

Usage:
    from athena.core.cache import get_search_cache

    cache = get_search_cache()

    # Exact match
    result = cache.get("what is caching?")

    # Semantic match (requires query embedding)
    result = cache.get_semantic(query_embedding, threshold=0.90)

    # Store with embedding for semantic retrieval
    cache.set("what is caching?", results, embedding=query_embedding)
"""

import contextlib
import hashlib
import json
import math
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from athena.core.config import AGENT_DIR


@dataclass
class CacheEntry:
    """A cached query result with optional embedding and scope for semantic matching."""

    value: Any
    timestamp: float
    hits: int = 0
    embedding: list[float] | None = field(default=None)
    scope: dict[str, Any] | None = field(default=None)


def _normalize_scope(scope: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize scope: empty dict or None -> None; otherwise sorted key-value dict."""
    if not scope:
        return None
    return {k: scope[k] for k in sorted(scope.keys())}


def _serialize_value(val: Any) -> Any:
    """Serialize values including SearchResult dataclasses into JSON-compatible objects."""
    if isinstance(val, list):
        return [_serialize_value(item) for item in val]
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    if hasattr(val, "__dataclass_fields__"):
        import dataclasses

        d = dataclasses.asdict(val)
        d["__dataclass_type__"] = val.__class__.__name__
        return d
    return val


def _deserialize_value(val: Any) -> Any:
    """Deserialize values back into SearchResult objects if tagged."""
    if isinstance(val, list):
        return [_deserialize_value(item) for item in val]
    if isinstance(val, dict):
        if val.get("__dataclass_type__") == "SearchResult":
            from athena.core.models import SearchResult

            data = {k: v for k, v in val.items() if k != "__dataclass_type__"}
            return SearchResult(**data)
        return {k: _deserialize_value(v) for k, v in val.items()}
    return val


class QueryCache:
    """TTL-based LRU cache with semantic similarity matching, serialization, and scope isolation."""

    def __init__(
        self,
        cache_dir: Path,
        ttl_hours: float = 24,
        max_size: int = 100,
    ):
        self.ttl_seconds = ttl_hours * 3600
        self.max_size = max_size
        self._cache_file = cache_dir / "search_cache.json"
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._load_from_disk()

    def _hash_key(self, query: str, scope: dict[str, Any] | None = None) -> str:
        """Create deterministic hash for query and scope (case-insensitive)."""
        normalized = query.lower().strip()
        norm_scope = _normalize_scope(scope)
        scope_str = ""
        if norm_scope:
            # Sort keys for deterministic representation
            scope_items = sorted((k, str(v)) for k, v in norm_scope.items())
            scope_str = "|" + "|".join(f"{k}={v}" for k, v in scope_items)
        combined = f"{normalized}{scope_str}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _load_from_disk(self):
        """Load cache from disk on initialization."""
        if not self._cache_file.exists():
            return
        try:
            data = json.loads(self._cache_file.read_text())
            now = time.time()
            for key, entry_data in data.items():
                if now - entry_data["timestamp"] < self.ttl_seconds:
                    if "embedding" not in entry_data:
                        entry_data["embedding"] = None
                    if "scope" not in entry_data:
                        entry_data["scope"] = None
                    else:
                        entry_data["scope"] = _normalize_scope(entry_data["scope"])
                    entry_data["value"] = _deserialize_value(entry_data["value"])
                    self._cache[key] = CacheEntry(**entry_data)
        except Exception:
            pass

    def _save_to_disk(self):
        """Persist cache to disk (atomic write via temp + rename)."""
        import os
        import tempfile

        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                k: {
                    "value": _serialize_value(e.value),
                    "timestamp": e.timestamp,
                    "hits": e.hits,
                    "embedding": e.embedding,
                    "scope": _normalize_scope(e.scope),
                }
                for k, e in self._cache.items()
            }
            # Write to temp file first, then atomic rename
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self._cache_file.parent), suffix=".tmp"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                os.replace(tmp_path, str(self._cache_file))
            except BaseException:
                # Clean up temp file on any failure
                with contextlib.suppress(OSError):
                    os.unlink(tmp_path)
                raise
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Exact Matching
    # -------------------------------------------------------------------------

    def get(self, query: str, scope: dict[str, Any] | None = None) -> Any | None:
        """Get cached result if exists, not expired, and scope matches (exact match)."""
        key = self._hash_key(query, scope)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        now = time.time()

        if now - entry.timestamp > self.ttl_seconds:
            del self._cache[key]
            self._save_to_disk()
            return None

        entry.hits += 1
        self._cache.move_to_end(key)  # LRU update
        self._save_to_disk()
        return entry.value

    # -------------------------------------------------------------------------
    # Semantic Matching
    # -------------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Calculate cosine similarity between two embedding vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=True))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_semantic(
        self,
        target_embedding: list[float],
        scope: dict[str, Any] | None = None,
        threshold: float = 0.90,
    ) -> Any | None:
        """
        Get cached result if a semantically similar query exists with identical scope.

        Args:
            target_embedding: Vector embedding of the query
            scope: Security and retrieval scope dictionary (e.g. personal, web)
            threshold: Minimum cosine similarity (0.90 = very similar)

        Returns:
            Cached result if similar query found in identical scope, else None
        """
        best_sim = -1.0
        best_entry = None
        best_key = None

        norm_scope = _normalize_scope(scope)
        for key, entry in self._cache.items():
            # Scope matching: Do not match across differing sensitivity/domain scopes
            if norm_scope != _normalize_scope(entry.scope):
                continue

            if entry.embedding:
                sim = self._cosine_similarity(target_embedding, entry.embedding)
                if sim > best_sim:
                    best_sim = sim
                    best_entry = entry
                    best_key = key

        if best_sim >= threshold and best_entry and best_key:
            best_entry.hits += 1
            self._cache.move_to_end(best_key)
            self._save_to_disk()
            return best_entry.value

        return None

    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------

    def set(
        self,
        query: str,
        value: Any,
        embedding: list[float] | None = None,
        scope: dict[str, Any] | None = None,
    ) -> None:
        """Cache a result with optional embedding and scope for retrieval."""
        norm_scope = _normalize_scope(scope)
        key = self._hash_key(query, norm_scope)

        # Evict oldest if at capacity (LRU)
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            hits=0,
            embedding=embedding,
            scope=norm_scope,
        )
        self._save_to_disk()

    def invalidate(self) -> None:
        """Invalidate all cached results (call when underlying data changes)."""
        self._cache.clear()
        self._save_to_disk()

    def stats(self) -> dict:
        """Get cache statistics for monitoring."""
        total_hits = sum(e.hits for e in self._cache.values())
        semantic_entries = sum(1 for e in self._cache.values() if e.embedding)
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "semantic_entries": semantic_entries,
            "ttl_hours": self.ttl_seconds / 3600,
        }


# Singleton Instance
_search_cache: QueryCache | None = None


def get_search_cache() -> QueryCache:
    """Singleton accessor for the search cache."""
    global _search_cache
    if _search_cache is None:
        _search_cache = QueryCache(cache_dir=AGENT_DIR / "state")
    return _search_cache


def invalidate_search_cache() -> None:
    """Invalidate search cache across the workspace."""
    cache = get_search_cache()
    cache.invalidate()
