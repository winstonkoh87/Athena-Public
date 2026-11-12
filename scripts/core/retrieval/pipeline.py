#!/usr/bin/env python3
"""
athena.core.retrieval.pipeline
===============================
Reciprocal Rank Fusion (RRF) retrieval pipeline.
Combines multiple retrieval sources with configurable weights.

Based on: "Reciprocal Rank Fusion outperforms Condorcet and individual
          Rank Learning Methods" (Cormack et al., 2009)
"""

import contextlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Try to import config loader
try:
    from athena.boot.config_loader import ManifestLoader, RetrievalConfig
except ImportError:
    ManifestLoader = None
    RetrievalConfig = None


@dataclass
class RetrievalResult:
    """A single retrieval result with source attribution."""

    content: str
    source: str  # 'vector', 'canonical', 'tags', 'filenames', 'graph_rag'
    score: float
    metadata: dict[str, Any]
    file_path: str | None = None


class RRFPipeline:
    """
    Reciprocal Rank Fusion pipeline for hybrid retrieval.

    RRF Formula: score(d) = Σ (1 / (k + rank(d)))
    where k is a constant (default 60) and rank is position in each list.
    """

    def __init__(self, config: Optional["RetrievalConfig"] = None):
        """Initialize with optional config from manifest."""
        if config is None and ManifestLoader is not None:
            with contextlib.suppress(Exception):
                config = ManifestLoader.get_retrieval_config()

        # Defaults if no config
        self.rrf_k = config.rrf_k if config else 60
        self.per_source_top_k = config.per_source_top_k if config else 40
        self.post_fusion_top_k = config.post_fusion_top_k if config else 60
        self.post_rerank_top_k = config.post_rerank_top_k if config else 10
        self.rerank_enabled = config.rerank_enabled if config else True

        # Source weights (higher = more trusted)
        self.weights = (
            config.weights
            if config
            else {
                "canonical_markdown": 1.8,
                "vector_memory": 2.0,
                "tags_index": 1.2,
                "filenames": 0.8,
                "graph_rag": 1.0,
            }
        )

        # Enabled sources
        self.enabled_sources = (
            config.sources
            if config
            else {
                "canonical_markdown": True,
                "vector_memory": True,
                "tags_index": True,
                "filenames": True,
                "graph_rag": False,
            }
        )

    def rrf_score(self, rank: int, weight: float = 1.0) -> float:
        """
        Calculate RRF score for a document at given rank.

        Args:
            rank: 1-indexed position in the ranked list
            weight: Source-specific weight multiplier

        Returns:
            RRF score contribution
        """
        return weight * (1.0 / (self.rrf_k + rank))

    def fuse(
        self, source_results: dict[str, list[RetrievalResult]]
    ) -> list[RetrievalResult]:
        """
        Fuse results from multiple sources using RRF.

        Args:
            source_results: Dict mapping source name to ranked result list

        Returns:
            Fused and re-ranked results
        """
        # Document ID -> (total_score, best_result)
        doc_scores: dict[str, tuple[float, RetrievalResult]] = {}

        for source_name, results in source_results.items():
            if not self.enabled_sources.get(source_name, False):
                continue

            weight = self.weights.get(source_name, 1.0)

            for rank, result in enumerate(results[: self.per_source_top_k], start=1):
                # Create document ID from content hash or path
                doc_id = result.file_path or hash(result.content)

                rrf_contribution = self.rrf_score(rank, weight)

                if doc_id in doc_scores:
                    current_score, current_result = doc_scores[doc_id]
                    # Accumulate RRF score
                    doc_scores[doc_id] = (
                        current_score + rrf_contribution,
                        current_result,  # Keep first encountered result
                    )
                else:
                    doc_scores[doc_id] = (rrf_contribution, result)

        # Sort by accumulated RRF score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1][0], reverse=True)

        # Extract results up to post_fusion limit
        fused_results = []
        for doc_id, (score, result) in sorted_docs[: self.post_fusion_top_k]:
            # Update the score to be the fused RRF score
            result.score = score
            fused_results.append(result)

        return fused_results

    def rerank(
        self, query: str, results: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        """
        Rerank results using a cross-encoder (placeholder for integration).

        Args:
            query: Original search query
            results: Fused results to rerank

        Returns:
            Reranked results (top_k)
        """
        if not self.rerank_enabled:
            return results[: self.post_rerank_top_k]

        import os

        from google import genai
        from google.genai import types

        has_api = os.getenv("GOOGLE_API_KEY") is not None
        if not has_api:
            return results[: self.post_rerank_top_k]

        try:
            _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

            # Pack top results for reranking
            candidates = []
            for i, r in enumerate(results[: self.post_fusion_top_k]):
                candidates.append({"id": i, "content": r.content[:500]})

            prompt = f"""Rate the relevance of these documents to the query: "{query}"
            Respond with a JSON list of IDs in order of relevance, with a score 0-1.
            Candidates: {json.dumps(candidates)}
            """

            response = _client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            ranks = json.loads(response.text)

            # Reorder based on model feedback
            reranked = []
            seen_ids = set()
            for item in ranks:
                idx = item.get("id")
                if idx is not None and 0 <= idx < len(results) and idx not in seen_ids:
                    res = results[idx]
                    res.score = item.get("score", res.score)
                    reranked.append(res)
                    seen_ids.add(idx)

            # Fill in remaining if needed
            for i, r in enumerate(results):
                if i not in seen_ids:
                    reranked.append(r)

            return reranked[: self.post_rerank_top_k]

        except Exception as e:
            print(f"⚠️ Rerank failed: {e}")
            return results[: self.post_rerank_top_k]

    def retrieve(
        self, query: str, sources: dict[str, list[RetrievalResult]] | None = None
    ) -> list[RetrievalResult]:
        """
        Full retrieval pipeline: gather sources -> fuse -> rerank.

        Args:
            query: Search query
            sources: Pre-fetched source results (or None to fetch fresh)

        Returns:
            Final ranked results
        """
        if sources is None:
            # In production, this would call each retrieval source
            sources = self._gather_sources(query)

        fused = self.fuse(sources)
        final = self.rerank(query, fused)

        return final

    def _gather_sources(self, query: str) -> dict[str, list[RetrievalResult]]:
        """
        Gather results from all enabled sources.
        Override this in subclasses to add real retrieval logic.
        """
        # Placeholder - in production, this would call:
        # - smart_search.py for vector_memory
        # - TAG_INDEX lookup for tags_index
        # - glob search for filenames
        # - KNOWLEDGE_GRAPH.md for graph_rag
        return {
            "canonical_markdown": [],
            "vector_memory": [],
            "tags_index": [],
            "filenames": [],
            "graph_rag": [],
        }


class AthenaRetriever(RRFPipeline):
    """
    Athena-specific retriever with hooks into existing search infrastructure.
    """

    def __init__(self):
        super().__init__()
        _here = Path(__file__).resolve()
        self.project_root = next(
            (
                d
                for d in _here.parents
                if (d / "pyproject.toml").exists() or (d / ".context").exists()
            ),
            _here.parents[3],
        )
        self.tag_shards = [
            self.project_root / ".context" / "TAG_INDEX_A-M.md",
            self.project_root / ".context" / "TAG_INDEX_N-Z.md",
        ]

    def _gather_sources(self, query: str) -> dict[str, list[RetrievalResult]]:
        """Gather from Athena's actual sources."""
        results = {}

        # 1. Vector Memory (via existing search.py)
        results["vector_memory"] = self._search_vector(query)

        # 2. Tag Index
        results["tags_index"] = self._search_tags(query)

        # 3. Filenames
        results["filenames"] = self._search_filenames(query)

        # 4. Canonical Markdown (direct file matches)
        results["canonical_markdown"] = self._search_canonical(query)

        # 5. Graph RAG (NEW: from KNOWLEDGE_GRAPH.md)
        results["graph_rag"] = self._search_graph(query)

        return results

    def _search_vector(self, query: str) -> list[RetrievalResult]:
        """Search vector store (Supabase pgvector)."""
        try:
            from athena.tools.search import search_memory

            raw_results = search_memory(query, limit=self.per_source_top_k)
            return [
                RetrievalResult(
                    content=r.get("content", ""),
                    source="vector_memory",
                    score=r.get("similarity", 0.0),
                    metadata=r.get("metadata", {}),
                    file_path=r.get("file_path"),
                )
                for r in raw_results
            ]
        except Exception:
            return []

    def _search_tags(self, query: str) -> list[RetrievalResult]:
        """Search TAG_INDEX shards for matching tags."""
        results = []
        query_lower = query.lower()

        for shard_path in self.tag_shards:
            if not shard_path.exists():
                continue

            try:
                content = shard_path.read_text()
                for line in content.split("\n"):
                    if "|" in line and query_lower in line.lower():
                        # Extract tag from markdown table row
                        parts = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts) >= 2:
                            tag = parts[0]
                            results.append(
                                RetrievalResult(
                                    content=line,
                                    source="tags_index",
                                    score=1.0 if query_lower in tag.lower() else 0.5,
                                    metadata={"tag": tag, "shard": shard_path.name},
                                    file_path=None,
                                )
                            )
            except Exception:
                pass

        return results[: self.per_source_top_k]

    def _search_filenames(self, query: str) -> list[RetrievalResult]:
        """Search for files matching query in name."""
        results = []
        query_lower = query.lower().replace(" ", "_")

        protocol_dirs = [
            self.project_root / ".agent" / "skills" / "protocols",
            self.project_root / ".agent" / "protocols",
            self.project_root / "examples" / "protocols",
        ]
        search_dirs = [
            *protocol_dirs,
            self.project_root / ".context",
            self.project_root / ".framework",
        ]

        seen: set[Path] = set()
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for path in search_dir.rglob("*.md"):
                rel_parts = path.relative_to(search_dir).parts
                if any(part in {"_archived", "archive"} for part in rel_parts[:-1]):
                    continue
                if path in seen:
                    continue
                seen.add(path)
                if query_lower in path.stem.lower() or query_lower.replace("_", "-") in path.stem.lower():
                    results.append(
                        RetrievalResult(
                            content=f"File: {path.name}",
                            source="filenames",
                            score=1.0 if query_lower == path.stem.lower() else 0.3,
                            metadata={"path": str(path)},
                            file_path=str(path),
                        )
                    )

        return results[: self.per_source_top_k]

    def _search_canonical(self, query: str) -> list[RetrievalResult]:
        """Search canonical markdown files by content."""
        # This is expensive - in production, use pre-indexed content
        return []

    def _search_graph(self, query: str) -> list[RetrievalResult]:
        """Search knowledge graph for related entities and relationships."""
        try:
            from athena.core.retrieval.graphrag import search_graph

            result = search_graph(query)
            if not result.context:
                return []

            return [
                RetrievalResult(
                    content=result.context,
                    source="graph_rag",
                    score=0.8,  # Base score for graph results
                    metadata={
                        "entity_count": len(result.entities),
                        "relationship_count": len(result.relationships),
                    },
                    file_path=str(
                        self.project_root / ".context" / "KNOWLEDGE_GRAPH.md"
                    ),
                )
            ]
        except Exception:
            return []


# Convenience function
def retrieve(query: str, top_k: int = 10) -> list[RetrievalResult]:
    """Quick access to Athena retrieval."""
    retriever = AthenaRetriever()
    results = retriever.retrieve(query)
    return results[:top_k]


if __name__ == "__main__":
    # Test the pipeline
    print("Testing RRF Pipeline...")
    pipeline = RRFPipeline()

    # Create mock results
    mock_sources = {
        "vector_memory": [
            RetrievalResult("Doc A from vector", "vector_memory", 0.9, {}, "a.md"),
            RetrievalResult("Doc B from vector", "vector_memory", 0.8, {}, "b.md"),
        ],
        "canonical_markdown": [
            RetrievalResult(
                "Doc B from canonical", "canonical_markdown", 1.0, {}, "b.md"
            ),
            RetrievalResult(
                "Doc C from canonical", "canonical_markdown", 0.7, {}, "c.md"
            ),
        ],
    }

    fused = pipeline.fuse(mock_sources)
    print(f"Fused {len(fused)} results:")
    for r in fused:
        print(f"  - {r.file_path}: {r.score:.4f}")
