#!/usr/bin/env python3
"""
code_indexer.py — AST-Based Code Semantic Indexer (Phase 2 + 3)

Extracts:
- Function definitions with docstrings
- Class definitions with methods
- Import relationships (call graph edges)
- PageRank scores for code importance

Usage:
    python3 code_indexer.py [--force]
"""

import ast
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Add src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("⚠️  NetworkX not installed. PageRank disabled. Run: pip install networkx")

from athena.memory.vectors import get_client, get_embedding

# Configuration
TARGET_DIRS = [
    PROJECT_ROOT / "src",
    PROJECT_ROOT / ".agent" / "scripts",
    PROJECT_ROOT / "Athena-Public" / "src",
]

CODE_INDEX_PATH = PROJECT_ROOT / ".context" / "CODE_INDEX.json"


class CodeEntity:
    """Represents a parsed code entity (function, class, module)."""

    def __init__(
        self,
        name: str,
        entity_type: str,
        file_path: Path,
        line_start: int,
        line_end: int,
        docstring: Optional[str] = None,
        signature: Optional[str] = None,
        imports: List[str] = None,
        calls: List[str] = None,
    ):
        self.name = name
        self.entity_type = entity_type
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.docstring = docstring or ""
        self.signature = signature or ""
        self.imports = imports or []
        self.calls = calls or []

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.entity_type,
            "file": str(self.file_path.relative_to(PROJECT_ROOT)),
            "lines": f"{self.line_start}-{self.line_end}",
            "docstring": self.docstring[:500],
            "signature": self.signature,
            "imports": self.imports,
            "calls": self.calls,
        }

    def to_searchable_text(self) -> str:
        """Generate text for embedding."""
        parts = [
            f"{self.entity_type}: {self.name}",
            f"File: {self.file_path.name}",
            f"Signature: {self.signature}" if self.signature else "",
            f"Description: {self.docstring}" if self.docstring else "",
        ]
        return "\n".join(p for p in parts if p)


def parse_python_file(file_path: Path) -> List[CodeEntity]:
    """Parse a Python file and extract code entities."""
    entities = []

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  ⚠️  Parse error in {file_path.name}: {e}")
        return []

    # Extract imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Extract functions and classes
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            entities.append(_parse_function(node, file_path, imports))
        elif isinstance(node, ast.ClassDef):
            entities.append(_parse_class(node, file_path, imports))

    return entities


def _parse_function(
    node: ast.FunctionDef, file_path: Path, imports: List[str]
) -> CodeEntity:
    """Parse a function definition."""
    # Build signature
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)

    returns = ""
    if node.returns:
        returns = f" -> {ast.unparse(node.returns)}"

    signature = f"def {node.name}({', '.join(args)}){returns}"

    # Extract calls within the function
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.append(child.func.attr)

    return CodeEntity(
        name=node.name,
        entity_type="function",
        file_path=file_path,
        line_start=node.lineno,
        line_end=node.end_lineno or node.lineno,
        docstring=ast.get_docstring(node),
        signature=signature,
        imports=imports,
        calls=list(set(calls)),
    )


def _parse_class(node: ast.ClassDef, file_path: Path, imports: List[str]) -> CodeEntity:
    """Parse a class definition."""
    # Build signature with bases
    bases = [ast.unparse(b) for b in node.bases]
    signature = (
        f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
    )

    # Extract method names
    methods = []
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(child.name)

    return CodeEntity(
        name=node.name,
        entity_type="class",
        file_path=file_path,
        line_start=node.lineno,
        line_end=node.end_lineno or node.lineno,
        docstring=ast.get_docstring(node),
        signature=signature,
        imports=imports,
        calls=methods,  # For classes, "calls" = methods
    )


def build_call_graph(entities: List[CodeEntity]) -> Dict[str, List[str]]:
    """Build a call graph from parsed entities."""
    graph = defaultdict(list)

    # Map entity names for lookup
    entity_names = {e.name for e in entities}

    for entity in entities:
        for call in entity.calls:
            if call in entity_names:
                graph[entity.name].append(call)

    return dict(graph)


def compute_pagerank(
    graph: Dict[str, List[str]], all_entities: List[str]
) -> Dict[str, float]:
    """Compute PageRank scores for code entities."""
    if not HAS_NETWORKX:
        return {e: 1.0 for e in all_entities}

    G = nx.DiGraph()
    G.add_nodes_from(all_entities)

    for caller, callees in graph.items():
        for callee in callees:
            G.add_edge(caller, callee)

    try:
        scores = nx.pagerank(G, alpha=0.85)
    except nx.PowerIterationFailedConvergence:
        scores = {n: 1.0 / len(all_entities) for n in all_entities}

    return scores


def sync_to_supabase(entities: List[CodeEntity], pagerank: Dict[str, float]):
    """Sync code entities to Supabase vector database."""
    client = get_client()
    synced = 0

    for entity in entities:
        text = entity.to_searchable_text()
        embedding = get_embedding(text)

        # Calculate importance score
        importance = pagerank.get(entity.name, 0.5)

        data = {
            "content": text,
            "embedding": embedding,
            "file_path": str(entity.file_path.relative_to(PROJECT_ROOT)),
            "title": f"{entity.entity_type}:{entity.name}",
            "code": entity.name,
            "name": entity.name,
        }

        try:
            client.table("protocols").upsert(data, on_conflict="file_path").execute()
            synced += 1
        except Exception as e:
            print(f"  ❌ Sync error for {entity.name}: {e}")

    return synced


def main():
    print("🔍 Athena Code Indexer (AST + PageRank)")
    print("=" * 50)

    all_entities = []

    # Phase 1: Parse all Python files
    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            continue

        py_files = list(target_dir.rglob("*.py"))
        print(f"\n📂 Scanning {target_dir.name}: {len(py_files)} Python files")

        for py_file in py_files:
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue

            entities = parse_python_file(py_file)
            all_entities.extend(entities)

    print(f"\n✅ Parsed {len(all_entities)} code entities")

    # Phase 2: Build call graph
    call_graph = build_call_graph(all_entities)
    print(f"📊 Built call graph with {len(call_graph)} caller nodes")

    # Phase 3: Compute PageRank
    entity_names = [e.name for e in all_entities]
    pagerank = compute_pagerank(call_graph, entity_names)

    # Sort by importance
    top_5 = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n🏆 Top 5 by PageRank:")
    for name, score in top_5:
        print(f"   {name}: {score:.4f}")

    # Save local index
    index_data = {
        "entities": [e.to_dict() for e in all_entities],
        "call_graph": call_graph,
        "pagerank": {k: round(v, 4) for k, v in pagerank.items()},
    }

    CODE_INDEX_PATH.write_text(json.dumps(index_data, indent=2))
    print(f"\n💾 Saved CODE_INDEX.json ({len(all_entities)} entities)")

    # Sync to Supabase
    print("\n☁️  Syncing to Supabase...")
    synced = sync_to_supabase(all_entities, pagerank)
    print(f"✅ Synced {synced} entities to vector DB")


if __name__ == "__main__":
    main()
