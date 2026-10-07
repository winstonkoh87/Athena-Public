"""
athena.core.models
==================

Shared data structures and Pydantic models.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    """
    Standardized search result object.
    Used by: Smart Search, Reranker, Context Window.
    """

    id: str
    content: str = ""
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0  # Raw score from source (cos-sim or keyword match)
    rrf_score: float = 0.0  # Fused Reciprocal Rank score
    signals: dict[str, Any] = field(default_factory=dict)  # Debug info
    path: str | None = None

    def __init__(
        self,
        id: str,
        content: str,
        source: str = "unknown",
        metadata: dict[str, Any] | None = None,
        score: float = 0.0,
        rrf_score: float = 0.0,
        signals: dict[str, Any] | None = None,
        path: str | None = None,
        **extra: Any,
    ):
        self.id = id
        self.content = content
        self.source = source
        self.metadata = dict(metadata) if metadata is not None else {}
        self.score = float(score)
        self.rrf_score = float(rrf_score)
        self.signals = dict(signals) if signals is not None else {}

        resolved_path = path or self.metadata.get("path")
        self.path = str(resolved_path) if resolved_path else None
        if self.path:
            self.metadata["path"] = self.path

        for k, v in extra.items():
            if k not in self.metadata:
                self.metadata[k] = v

    def to_dict(self) -> dict[str, Any]:
        d = {
            "id": self.id,
            "content": (self.content[:100] + "...") if self.content else "",
            "source": self.source,
            "rrf_score": self.rrf_score,
            "signals": self.signals,
        }
        resolved_path = self.path or self.metadata.get("path")
        if resolved_path:
            d["path"] = resolved_path
        return d
