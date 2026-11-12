#!/usr/bin/env python3
"""
athena.core.retrieval.graphrag
===============================
GraphRAG bridge for the RRF pipeline.

Parses the KNOWLEDGE_GRAPH.md file and provides entity/relationship
lookup for knowledge-graph-augmented retrieval.

This fixes the "placeholder retrieval" blind spot where graph_rag
was enabled in config but returned empty results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Entity:
    """A knowledge graph entity."""

    name: str
    type: str  # 'PROTOCOL', 'CONCEPT', 'FILE', 'PERSON', etc.
    description: str = ""


@dataclass
class Relationship:
    """A relationship between entities."""

    source: str
    target: str
    relation: str  # 'USES', 'DEPENDS_ON', 'CREATED_BY', etc.


@dataclass
class GraphSearchResult:
    """Result from a graph search."""

    entities: list[Entity]
    relationships: list[Relationship]
    context: str  # Aggregated context for retrieval


class KnowledgeGraphParser:
    """
    Parser for KNOWLEDGE_GRAPH.md.

    The graph is stored in a simple markdown format:

    ## Entities
    - [PROTOCOL] 418-promise-gate: Handoff protocol
    - [CONCEPT] RRF: Reciprocal Rank Fusion

    ## Relationships
    - 418-promise-gate USES promise-file
    - boot.py DEPENDS_ON config_loader
    """

    def __init__(self, graph_path: Path | None = None):
        if graph_path is None:
            # Default location
            _here = Path(__file__).resolve()
            project_root = next(
                (
                    d
                    for d in _here.parents
                    if (d / "pyproject.toml").exists() or (d / ".context").exists()
                ),
                _here.parents[3],
            )
            graph_path = project_root / ".context" / "KNOWLEDGE_GRAPH.md"

        self.graph_path = graph_path
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []
        self._loaded = False

    def load(self) -> bool:
        """Load and parse the knowledge graph."""
        if self._loaded:
            return True

        if not self.graph_path.exists():
            return False

        try:
            content = self.graph_path.read_text()
            self._parse_entities(content)
            self._parse_relationships(content)
            self._loaded = True
            return True
        except Exception:
            return False

    def _parse_entities(self, content: str):
        """Parse entity definitions."""
        # Pattern: - [TYPE] name: description
        pattern = r"-\s*\[(\w+)\]\s*([^:]+):\s*(.+)"

        for match in re.finditer(pattern, content):
            entity_type = match.group(1).strip()
            name = match.group(2).strip()
            description = match.group(3).strip()

            self.entities[name.lower()] = Entity(
                name=name, type=entity_type, description=description
            )

    def _parse_relationships(self, content: str):
        """Parse relationship definitions."""
        # Pattern: - source RELATION target
        pattern = r"-\s*(\S+)\s+(USES|DEPENDS_ON|CREATED_BY|RELATED_TO|IMPLEMENTS|EXTENDS)\s+(\S+)"

        for match in re.finditer(pattern, content, re.IGNORECASE):
            source = match.group(1).strip()
            relation = match.group(2).strip().upper()
            target = match.group(3).strip()

            self.relationships.append(
                Relationship(source=source, target=target, relation=relation)
            )

    def search(self, query: str, max_hops: int = 2) -> GraphSearchResult:
        """
        Search the graph for entities matching query and their neighbors.

        Args:
            query: Search query
            max_hops: How many relationship hops to traverse

        Returns:
            GraphSearchResult with matching entities and context
        """
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        query_terms = query_lower.split()

        # Find matching entities
        matched_entities = []
        for name, entity in self.entities.items():
            score = 0
            for term in query_terms:
                if term in name:
                    score += 2
                if term in entity.description.lower():
                    score += 1
                if term in entity.type.lower():
                    score += 0.5

            if score > 0:
                matched_entities.append((entity, score))

        # Sort by score
        matched_entities.sort(key=lambda x: x[1], reverse=True)
        entities = [e for e, _ in matched_entities[:10]]

        # Find related relationships
        entity_names = {e.name.lower() for e in entities}
        related_rels = []

        for _ in range(max_hops):
            new_names = set()
            for rel in self.relationships:
                src = rel.source.lower()
                tgt = rel.target.lower()
                if src in entity_names or tgt in entity_names:
                    related_rels.append(rel)
                    new_names.add(src)
                    new_names.add(tgt)
            entity_names.update(new_names)

        # Build context string
        context_parts = []
        for entity in entities:
            context_parts.append(f"[{entity.type}] {entity.name}: {entity.description}")

        for rel in related_rels[:20]:
            context_parts.append(f"{rel.source} --{rel.relation}--> {rel.target}")

        return GraphSearchResult(
            entities=entities,
            relationships=related_rels[:20],
            context="\n".join(context_parts),
        )


# Singleton instance
_parser_instance: KnowledgeGraphParser | None = None


def get_parser() -> KnowledgeGraphParser:
    """Get or create the singleton parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = KnowledgeGraphParser()
    return _parser_instance


def search_graph(query: str) -> GraphSearchResult:
    """Convenience function for graph search."""
    parser = get_parser()
    return parser.search(query)


if __name__ == "__main__":
    print("Testing Knowledge Graph Parser...\n")

    parser = KnowledgeGraphParser()
    loaded = parser.load()

    if loaded:
        print(
            f"Loaded {len(parser.entities)} entities, {len(parser.relationships)} relationships\n"
        )

        result = parser.search("protocol boot")
        print("Search 'protocol boot':")
        print(f"  Entities: {len(result.entities)}")
        print(f"  Relationships: {len(result.relationships)}")
        print(f"  Context preview: {result.context[:200]}...")
    else:
        print("KNOWLEDGE_GRAPH.md not found - creating sample...")

        sample = """# Athena Knowledge Graph

## Entities

- [PROTOCOL] 418-promise-gate: Handoff protocol for async operations
- [PROTOCOL] 419-handoff-loop: Continuous execution loop
- [CONCEPT] RRF: Reciprocal Rank Fusion for hybrid retrieval
- [FILE] boot.py: Main boot script
- [FILE] config_loader.py: Manifest configuration parser

## Relationships

- boot.py USES config_loader.py
- boot.py IMPLEMENTS 419-handoff-loop
- RRF RELATED_TO retrieval
"""
        print(sample)
