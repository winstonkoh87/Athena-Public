#!/usr/bin/env python3
"""
Generate a SFW (Safe For Work) knowledge graph visualization.
Filters out sensitive entity names before generating the HTML.
"""

import json
from pathlib import Path

# Sensitive keywords to filter out
NSFW_KEYWORDS = [
    'virgin', 'seduction', 'threesome', 'escort', 'sexual', 'sex',
    'bdsm', 'erotic', 'fetish', 'porn', 'nude', 'naked',
    'shadow-hotel', 'locker-room', 'dating-app', 'hookup',
    'abuse', 'trauma', 'cptsd', 'rape', 'predator',
    'yap-weng-wah', 'mermaid-girl',
    # Personal identifiers
    'winston', 'jun-kai', 'jj',
]

# SFW categories to keep
SFW_CATEGORIES = [
    'business', 'engineering', 'architecture', 'workflow', 'automation',
    'decision', 'research', 'protocol', 'framework', 'system',
    'knowledge', 'graph', 'index', 'memory', 'session',
    'trading', 'arbitrage', 'pricing', 'market', 'funnel',
    'communication', 'negotiation', 'strategy', 'pattern',
    'isomorphism', 'detection', 'analysis', 'synthesis',
]

# Dynamic workspace resolution
WORKSPACE = Path(__file__).resolve().parent.parent.parent
ENTITIES_FILE = WORKSPACE / ".agent/graphrag/entities.json"
OUTPUT_FILE = WORKSPACE / ".agent/graphrag/knowledge_graph_sfw.html"

def is_sfw(name: str) -> bool:
    """Check if entity name is safe for work."""
    name_lower = name.lower()

    # Reject if contains NSFW keyword
    return all(kw not in name_lower for kw in NSFW_KEYWORDS)

def generate_sfw_graph():
    """Generate a filtered SFW graph visualization."""

    # Load entities
    data = json.loads(ENTITIES_FILE.read_text())

    # Filter entities
    sfw_entities = [e for e in data['entities'] if is_sfw(e['name'])]
    sfw_names = {e['name'] for e in sfw_entities}

    # Filter relationships (both ends must be SFW)
    sfw_rels = [r for r in data['relationships']
                if r['source'] in sfw_names and r['target'] in sfw_names]

    print(f"Original: {len(data['entities'])} entities, {len(data['relationships'])} relationships")
    print(f"Filtered: {len(sfw_entities)} entities, {len(sfw_rels)} relationships")

    # Generate simple HTML with vis.js
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Athena Knowledge Graph (Public View)</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { margin: 0; padding: 0; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
        #graph { width: 100vw; height: 100vh; }
        #info { position: fixed; top: 20px; left: 20px; color: #eee; background: rgba(0,0,0,0.7);
                padding: 15px; border-radius: 8px; max-width: 300px; }
        h2 { margin: 0 0 10px 0; color: #4ecdc4; }
        p { margin: 5px 0; font-size: 14px; }
        .stat { color: #ff6b6b; font-weight: bold; }
    </style>
</head>
<body>
    <div id="info">
        <h2>🧠 Athena Knowledge Graph</h2>
        <p>Entities: <span class="stat">ENTITY_COUNT</span></p>
        <p>Relationships: <span class="stat">REL_COUNT</span></p>
        <p style="margin-top: 10px; font-size: 12px; color: #888;">
            Drag to pan, scroll to zoom.<br>
            Click nodes to highlight connections.
        </p>
    </div>
    <div id="graph"></div>
    <script>
        const nodes = new vis.DataSet(NODES_DATA);
        const edges = new vis.DataSet(EDGES_DATA);

        const container = document.getElementById('graph');
        const data = { nodes: nodes, edges: edges };
        const options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: { size: 12, color: '#ffffff' },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                color: { color: '#4a4a6a', highlight: '#4ecdc4' },
                smooth: { type: 'continuous' }
            },
            physics: {
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08
                },
                maxVelocity: 50,
                solver: 'forceAtlas2Based',
                timestep: 0.35,
                stabilization: { iterations: 150 }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };

        const network = new vis.Network(container, data, options);
    </script>
</body>
</html>"""

    # Build nodes (limit to top 200 for performance)
    # Sort by connection count
    entity_connections = {}
    for r in sfw_rels:
        entity_connections[r['source']] = entity_connections.get(r['source'], 0) + 1
        entity_connections[r['target']] = entity_connections.get(r['target'], 0) + 1

    top_entities = sorted(sfw_entities,
                          key=lambda e: entity_connections.get(e['name'], 0),
                          reverse=True)[:200]
    top_names = {e['name'] for e in top_entities}

    # Color by type
    type_colors = {
        'concept': '#4ecdc4',
        'file': '#ff6b6b',
        'protocol': '#ffe66d',
        'framework': '#95e1d3',
        'default': '#a8a8a8'
    }

    nodes_data = []
    for e in top_entities:
        etype = e.get('type', 'default').lower()
        color = type_colors.get(etype, type_colors['default'])
        size = 10 + min(entity_connections.get(e['name'], 0) * 2, 30)
        nodes_data.append({
            'id': e['name'],
            'label': e['name'][:20],
            'title': e.get('description', e['name'])[:100],
            'color': color,
            'size': size
        })

    # Build edges (only between top entities)
    edges_data = []
    for r in sfw_rels:
        if r['source'] in top_names and r['target'] in top_names:
            edges_data.append({
                'from': r['source'],
                'to': r['target']
            })

    # Inject data
    html = html.replace('ENTITY_COUNT', str(len(top_entities)))
    html = html.replace('REL_COUNT', str(len(edges_data)))
    html = html.replace('NODES_DATA', json.dumps(nodes_data))
    html = html.replace('EDGES_DATA', json.dumps(edges_data))

    OUTPUT_FILE.write_text(html)
    print(f"\n✅ Generated: {OUTPUT_FILE}")
    print(f"   Nodes: {len(nodes_data)}, Edges: {len(edges_data)}")

if __name__ == "__main__":
    generate_sfw_graph()
