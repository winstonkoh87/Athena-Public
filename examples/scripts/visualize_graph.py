#!/usr/bin/env python3
"""
visualize_graph.py — Interactive Knowledge Graph Visualization

Generates an interactive HTML visualization of the knowledge graph
using PyVis, matching the capability described in the reference article.

Usage:
    python3 .agent/scripts/visualize_graph.py
"""

import pickle
import json
import os
from pathlib import Path
import networkx as nx
from pyvis.network import Network

# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent
GRAPHRAG_DIR = ROOT_DIR / ".agent" / "graphrag"
GRAPH_FILE = GRAPHRAG_DIR / "knowledge_graph.gpickle"
COMMUNITIES_FILE = GRAPHRAG_DIR / "communities.json"
OUTPUT_HTML = GRAPHRAG_DIR / "knowledge_graph.html"

def load_graph():
    """Load the NetworkX graph from pickle."""
    if not GRAPH_FILE.exists():
        print(f"❌ Graph file not found: {GRAPH_FILE}")
        return None
    with open(GRAPH_FILE, 'rb') as f:
        return pickle.load(f)

def load_communities():
    """Load community data for coloring."""
    if not COMMUNITIES_FILE.exists():
        return {}
    data = json.loads(COMMUNITIES_FILE.read_text())
    
    # Map node -> community_id
    node_community = {}
    for comm in data.get("communities", []):
        comm_id = comm["community_id"]
        for member in comm["members"]:
            node_community[member] = comm_id
    return node_community

def generate_visualization():
    print("=" * 60)
    print("🕸️  GRAPH VISUALIZATION GENERATOR")
    print("=" * 60)

    # Load data
    G = load_graph()
    if G is None:
        return
    
    communities = load_communities()
    print(f"   Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"   Loaded community mappings for {len(communities)} nodes")

    # Initialize PyVis network
    net = Network(
        height="900px", 
        width="100%", 
        bgcolor="#111111", 
        font_color="white",
        select_menu=True,
        cdn_resources="remote"
    )

    # Configure physics (Force Atlas 2 based)
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=100,
        spring_strength=0.08,
        damping=0.4,
        overlap=0
    )

    # Add nodes with community coloring
    # Generate a color palette for communities
    community_ids = set(communities.values())
    # Simple color mapping logic (using PyVis default or custom if needed)
    
    print("\n🎨 processing nodes...")
    for node in G.nodes():
        comm_id = communities.get(node, -1)
        
        # Base attributes
        attrs = G.nodes[node]
        title = f"{node}\nType: {attrs.get('type', 'unknown')}\n{attrs.get('description', '')[:100]}"
        
        # Color by community
        group = comm_id if comm_id != -1 else "Unclustered"
        
        net.add_node(
            node,
            label=node,
            title=title,
            group=group,
            size=20 + (len(list(G.neighbors(node))) * 2)  # Size by degree
        )

    # Add edges
    print("🔗 processing edges...")
    for u, v, data in G.edges(data=True):
        net.add_edge(
            u, 
            v, 
            title=data.get('type', 'relates_to'),
            width=1.0,
            color="#444444" 
        )

    # Add physics controls
    net.show_buttons(filter_=['physics'])

    # Save to HTML
    print(f"\n💾 Saving visualization to {OUTPUT_HTML}...")
    net.write_html(str(OUTPUT_HTML))
    print("✅ Done! Open this file in your browser to explore the graph.")
    print("=" * 60)

if __name__ == "__main__":
    generate_visualization()
