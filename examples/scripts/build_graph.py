#!/usr/bin/env python3
"""
build_graph.py — Knowledge Graph Construction + Community Detection (v2.0)

Builds a NetworkX graph from extracted entities and runs Leiden algorithm
for community detection. Generates community summaries.

Features:
- Resilient Community Detection (Fallbacks for import/runtime errors)
- Enhanced Summarization Prompts
- Safe Graph Serialization

Usage:
    python3 .agent/scripts/build_graph.py

Output:
    - .agent/graphrag/knowledge_graph.gpickle
    - .agent/graphrag/communities.json
"""

import os
import json
import pickle
from pathlib import Path
from collections import defaultdict
import time

import networkx as nx

# Try to import community detection libraries
try:
    import igraph as ig
    import leidenalg

    LEIDEN_AVAILABLE = True
except ImportError:
    LEIDEN_AVAILABLE = False

# Try to import Gemini for summaries
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent
GRAPHRAG_DIR = ROOT_DIR / ".agent" / "graphrag"
ENTITIES_FILE = GRAPHRAG_DIR / "entities.json"
GRAPH_FILE = GRAPHRAG_DIR / "knowledge_graph.gpickle"
COMMUNITIES_FILE = GRAPHRAG_DIR / "communities.json"

# Community summary prompt
SUMMARY_PROMPT = """You are an expert analyst summarizing a thematic domain from a knowledge graph.

Context:
The following entities form a calculated community (cluster) within the user's workspace.
They are tightly connected.

Entities in this cluster:
{entities}

Source Files:
{files}

Task:
Write a high-yield executive summary (2-3 sentences) that explains:
1. **The Core Theme**: What connects these concepts?
2. **The Insight**: What is the "bigger picture" or pattern here?

Rules:
- Be specific. Mention key protocol numbers or entity names.
- Avoid generic fluff like "This cluster represents...". Go straight to the point.
- Output ONLY the summary text.
"""


def load_entities() -> dict:
    """Load extracted entities from JSON."""
    if not ENTITIES_FILE.exists():
        print("❌ entities.json not found. Run extract_entities.py first.")
        return None
    try:
        return json.loads(ENTITIES_FILE.read_text())
    except json.JSONDecodeError:
        print("❌ entities.json is corrupted.")
        return None


def build_graph(data: dict) -> nx.Graph:
    """Build NetworkX graph from entities and relationships."""
    G = nx.Graph()

    # Add nodes
    for entity in data.get("entities", []):
        G.add_node(
            entity["name"],
            type=entity.get("type", "unknown"),
            description=entity.get("description", ""),
            source_file=entity.get("source_file", ""),
        )

    # Add edges from explicit relationships
    for rel in data.get("relationships", []):
        if G.has_node(rel["source"]) and G.has_node(rel["target"]):
            G.add_edge(
                rel["source"],
                rel["target"],
                type=rel.get("type", "relates_to"),
                source_file=rel.get("source_file", ""),
            )

    # Add implicit edges: entities from same file are connected
    # (Optional: Weights could be lower for implicit connections)
    file_entities = defaultdict(list)
    for entity in data.get("entities", []):
        if entity.get("source_file"):
            file_entities[entity["source_file"]].append(entity["name"])

    for file_path, entities in file_entities.items():
        # Only connect up to a reasonable number to avoid clique explosion on huge files
        # Smart chunking upstream mitigates this, but safety first.
        safe_entities = entities[:20]
        for i, e1 in enumerate(safe_entities):
            for e2 in safe_entities[i + 1 :]:
                if not G.has_edge(e1, e2):
                    G.add_edge(e1, e2, type="co_occurs", source_file=file_path)

    return G


def run_leiden(G: nx.Graph) -> dict:
    """Run Leiden community detection algorithm with fallback."""
    if not LEIDEN_AVAILABLE:
        print(
            "⚠️  Leiden libraries not installed (igraph/leidenalg). Using Connected Components."
        )
        return _fallback_communities(G)

    try:
        # Convert to igraph (efficiently)
        node_list = list(G.nodes())
        if not node_list:
            return {}

        ig_graph = ig.Graph(len(node_list))
        node_to_idx = {node: i for i, node in enumerate(node_list)}

        edges = []
        for u, v in G.edges():
            if u in node_to_idx and v in node_to_idx:
                edges.append((node_to_idx[u], node_to_idx[v]))

        ig_graph.add_edges(edges)

        # Run Leiden
        partition = leidenalg.find_partition(
            ig_graph, leidenalg.ModularityVertexPartition
        )

        communities = {}
        for idx, cluster in enumerate(partition.membership):
            communities[node_list[idx]] = cluster

        return communities

    except Exception as e:
        print(f"⚠️  Leiden detection failed: {e}. Falling back to Connected Components.")
        return _fallback_communities(G)


def _fallback_communities(G: nx.Graph) -> dict:
    """Use simple connected components as communities."""
    communities = {}
    for i, component in enumerate(nx.connected_components(G)):
        for node in component:
            communities[node] = i
    return communities


def generate_community_summaries(G: nx.Graph, communities: dict) -> list:
    """Generate summaries for each community."""
    # Group nodes by community
    community_nodes = defaultdict(list)
    for node, comm_id in communities.items():
        community_nodes[comm_id].append(node)

    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "your_gemini_api_key_here" in api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    use_gemini = GEMINI_AVAILABLE and api_key

    if use_gemini:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3-flash-preview")

    summaries = []

    # Sort communities by size to prioritize largest for processing
    sorted_communities = sorted(
        community_nodes.items(), key=lambda x: len(x[1]), reverse=True
    )

    print(f"   Processing {len(sorted_communities)} communities...")

    for comm_id, nodes in sorted_communities:
        # Skip tiny communities (noise)
        if len(nodes) < 3:
            continue

        # Get entity info for prompt
        entity_info = []
        files = set()

        # Top nodes by degree centrality within subgraph would be better, but list order is decent proxy
        for node in nodes[:15]:
            if G.has_node(node):
                attrs = G.nodes[node]
                desc = attrs.get("description", "Concept")
                entity_info.append(f"- {node} ({attrs.get('type', 'concept')}): {desc}")
                if attrs.get("source_file"):
                    files.add(attrs["source_file"])

        # Generate summary
        summary = ""
        if use_gemini:
            try:
                response = model.generate_content(
                    SUMMARY_PROMPT.format(
                        entities="\n".join(entity_info),
                        files=", ".join(list(files)[:5]),
                    )
                )
                summary = response.text.strip()
                # Rate limit protection
                time.sleep(0.5)
            except Exception as e:
                print(f"      ⚠️ Summary failed for Comm {comm_id}: {e}")
                summary = f"Cluster including: {', '.join(nodes[:5])}"
        else:
            summary = f"Cluster of {len(nodes)} nodes: {', '.join(nodes[:5])}"

        summaries.append(
            {
                "community_id": comm_id,
                "size": len(nodes),
                "members": nodes,
                "summary": summary,
                "source_files": list(files),
            }
        )

    return summaries


def main():
    print("=" * 60)
    print("🕸️  KNOWLEDGE GRAPH BUILDER (v2.0)")
    print("=" * 60)

    # Load entities
    print("\n📂 Loading entities...")
    data = load_entities()
    if data is None:
        return

    print(
        f"   Loaded {len(data.get('entities', []))} entities, {len(data.get('relationships', []))} relationships"
    )

    # Build graph
    print("\n🔨 Building graph...")
    G = build_graph(data)
    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")

    if G.number_of_nodes() == 0:
        print("❌ Graph is empty. Exiting.")
        return

    # Run community detection
    print("\n🔍 Running Community Detection...")
    communities = run_leiden(G)
    num_communities = len(set(communities.values()))
    print(f"   Identified {num_communities} communities")

    # Generate summaries
    print("\n📝 Generating summaries (Gemini 2.0)...")
    summaries = generate_community_summaries(G, communities)

    # Save graph
    GRAPHRAG_DIR.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_FILE, "wb") as f:
        pickle.dump(G, f)
    print(f"\n💾 Saved graph to {GRAPH_FILE}")

    # Save communities
    output = {
        "communities": summaries,
        "stats": {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "num_communities": num_communities,
        },
    }
    COMMUNITIES_FILE.write_text(json.dumps(output, indent=2))
    print(f"💾 Saved communities to {COMMUNITIES_FILE}")

    # Preview top communities
    print("\n" + "=" * 60)
    print("📊 TOP INSIGHTS:")
    for comm in summaries[:3]:
        print(f"\n   Community {comm['community_id']} ({comm['size']} nodes):")
        print(f"   {comm['summary']}")

    print("\n" + "=" * 60)
    print(f"✅ GRAPH BUILD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
