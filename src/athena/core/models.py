"""
athena.core.models
==================

Shared data structures and Pydantic models.
"""

import re
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

        # Epistemic provenance extraction (TD-084)
        if "claim_kind" in self.metadata:
            self.claim_kind = self.metadata["claim_kind"]
        elif self.content and self.content.startswith("[Doc:"):
            m_kind = re.search(r"\|\s*Kind:\s*([a-zA-Z0-9_\-]+)", self.content[:200], re.IGNORECASE)
            self.claim_kind = m_kind.group(1).lower().strip() if m_kind else None
            if self.claim_kind:
                self.metadata["claim_kind"] = self.claim_kind
        else:
            self.claim_kind = None

        if "status" in self.metadata:
            self.status = self.metadata["status"]
        elif self.content and self.content.startswith("[Doc:"):
            m_status = re.search(r"\|\s*Status:\s*([a-zA-Z0-9_\-]+)", self.content[:200], re.IGNORECASE)
            self.status = m_status.group(1).lower().strip() if m_status else None
            if self.status:
                self.metadata["status"] = self.status
        else:
            self.status = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "id": self.id,
            "content": (self.content[:100] + "...") if self.content else "",
            "source": self.source,
            "rrf_score": self.rrf_score,
            "signals": self.signals,
        }
        if self.metadata.get("claim_kind"):
            d["claim_kind"] = self.metadata["claim_kind"]
        if self.metadata.get("status"):
            d["status"] = self.metadata["status"]
        resolved_path = self.path or self.metadata.get("path")
        if resolved_path:
            d["path"] = resolved_path
        return d
