#!/usr/bin/env python3
"""
query_graphrag.py — Dual-Mode GraphRAG Query Interface (v2.0)

Searches both vector embeddings (local) and community summaries (global)
for comprehensive semantic retrieval.

Auto-selects the Python 3.12 venv in .agent/graphrag_env for compatibility.

Usage:
    python3 .agent/scripts/query_graphrag.py "What patterns connect architecture and governance?"
    python3 .agent/scripts/query_graphrag.py "structural trap" --local-only
    python3 .agent/scripts/query_graphrag.py "cross-domain patterns" --deep
    python3 .agent/scripts/query_graphrag.py "query" --json  (Machine readable)

Output:
    Combined results from vector search and community matching.
"""

import json
import os
import pickle
import subprocess
import sys
from pathlib import Path

# === Configuration ===
WORKSPACE = Path(__file__).resolve().parent.parent.parent
GRAPHRAG_DIR = WORKSPACE / ".agent" / "graphrag"
CHROMA_DIR = WORKSPACE / ".agent" / "chroma_db"
VENV_PYTHON = WORKSPACE / ".agent" / "graphrag_env" / "bin" / "python3"
COMMUNITIES_FILE = GRAPHRAG_DIR / "communities.json"
GRAPH_FILE = GRAPHRAG_DIR / "knowledge_graph.gpickle"

TOP_K_VECTORS = 5
TOP_K_COMMUNITIES = 3


# === Auto-Relaunch Logic ===
def ensure_correct_interpreter():
    """Relaunch script with venv python if current interpreter is wrong."""
    if VENV_PYTHON.exists() and str(VENV_PYTHON) != sys.executable:
        # Check if we are already running inside the venv (by path comparison)
        try:
            current_exe = Path(sys.executable).resolve()
            target_exe = VENV_PYTHON.resolve()
            if current_exe != target_exe:
                # Relaunch
                cmd = [str(target_exe)] + sys.argv
                subprocess.run(cmd, check=True)
                sys.exit(0)
        except Exception:
            # If we fail to switch, just warn and try to run (might fail on imports)
            pass


# Call immediately
ensure_correct_interpreter()


def search_vectors(query: str) -> list:
    """Search ChromaDB for similar content."""
    if not CHROMA_DIR.exists():
        return []

    try:
        import chromadb
        from chromadb.utils import embedding_functions

        import logging

        logging.getLogger("chromadb").setLevel(logging.ERROR)

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        collection = client.get_collection(name="codex", embedding_function=embedding_fn)
    except Exception:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=TOP_K_VECTORS,
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    if results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            strict=True,
        ):
            matches.append(
                {
                    "type": "vector",
                    "file": meta.get("file_path", "Unknown"),
                    "similarity": 1 - dist,
                    "preview": doc[:300].replace("\n", " "),
                }
            )

    return matches


def search_communities(query: str) -> list:
    """Search community summaries for thematic matches."""
    if not COMMUNITIES_FILE.exists():
        return []

    try:
        data = json.loads(COMMUNITIES_FILE.read_text())
        communities = data.get("communities", [])
    except json.JSONDecodeError:
        return []

    # Simple keyword matching (could be upgraded to embeddings)
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for comm in communities:
        summary_lower = comm.get("summary", "").lower()
        members_lower = " ".join(comm.get("members", [])).lower()

        # Score based on word overlap
        summary_words = set(summary_lower.split())
        member_words = set(members_lower.split())

        summary_overlap = len(query_words & summary_words)
        member_overlap = len(query_words & member_words)

        score = summary_overlap * 2 + member_overlap

        if score > 0:
            scored.append((score, comm))

    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)

    matches = []
    for score, comm in scored[:TOP_K_COMMUNITIES]:
        matches.append(
            {
                "type": "community",
                "community_id": comm.get("community_id", "???"),
                "size": comm.get("size", 0),
                "summary": comm.get("summary", ""),
                "members": comm.get("members", [])[:10],
                "score": score,
            }
        )

    return matches


def load_graph():
    """Load the knowledge graph (cached for reuse)."""
    if not GRAPH_FILE.exists():
        return None
    try:
        with open(GRAPH_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def expand_entity(G, entity_name: str, max_neighbors: int = 5) -> dict:
    """
    Fan-out from an entity to its neighbors and relationships.
    This is the 'Local Search' pattern from Microsoft GraphRAG.
    """
    if entity_name not in G:
        return {"entity": entity_name, "neighbors": [], "relationships": []}

    neighbors = []
    relationships = []

    # Get direct neighbors with their attributes
    for neighbor in list(G.neighbors(entity_name))[:max_neighbors]:
        neighbor_attrs = G.nodes.get(neighbor, {})
        neighbors.append(
            {
                "name": neighbor,
                "type": neighbor_attrs.get("type", "unknown"),
                "description": neighbor_attrs.get("description", "")[:100],
            }
        )

        # Get edge attributes (relationship info)
        edge_data = G.get_edge_data(entity_name, neighbor, {})
        if edge_data:
            relationships.append(
                {
                    "from": entity_name,
                    "to": neighbor,
                    "weight": edge_data.get("weight", 1),
                    "context": edge_data.get("context", "co-occurrence"),
                }
            )

    return {
        "entity": entity_name,
        "neighbors": neighbors,
        "relationships": relationships,
    }


def search_entities(query: str, expand: bool = False) -> list:
    """Search entity descriptions in the knowledge graph with optional fan-out."""
    G = load_graph()
    if G is None:
        return []

    query_lower = query.lower()
    query_words = set(query_lower.split())

    matches = []
    for node, attrs in G.nodes(data=True):
        node_lower = node.lower()
        desc_lower = attrs.get("description", "").lower()

        # Check for word overlap
        text_words = set(node_lower.split()) | set(desc_lower.split())
        overlap = len(query_words & text_words)

        if overlap > 0 or any(w in node_lower for w in query_words):
            match = {
                "type": "entity",
                "name": node,
                "entity_type": attrs.get("type", "unknown"),
                "description": attrs.get("description", ""),
                "source": attrs.get("source_file", ""),
                "score": overlap + (1 if any(w in node_lower for w in query_words) else 0),
            }

            # Fan-out to neighbors if requested
            if expand:
                expansion = expand_entity(G, node)
                match["neighbors"] = expansion["neighbors"]
                match["relationships"] = expansion["relationships"]

            matches.append(match)

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:5]


def drift_search(query: str) -> dict:
    """
    DRIFT Search logic.
    """
    results = {"query": query, "primer": [], "follow_ups": [], "entities": []}

    # Phase 1: Primer
    community_matches = search_communities(query)
    if not community_matches:
        return results
    results["primer"] = community_matches[:2]

    # Phase 2: Themes
    all_members = []
    for comm in results["primer"]:
        all_members.extend(comm.get("members", [])[:10])

    themes = set()
    for member in all_members:
        if member.startswith("#") and len(member) < 8:
            continue
        if member.replace("#", "").isdigit():
            continue
        themes.add(member)

    # Phase 3: Fan-out
    G = load_graph()
    if G is not None:
        for theme in list(themes)[:5]:
            theme_matches = search_entities(theme, expand=True)
            for match in theme_matches[:2]:
                results["entities"].append(match)
                results["follow_ups"].append(
                    {
                        "theme": theme,
                        "entity": match["name"],
                        "neighbors": match.get("neighbors", []),
                    }
                )

    return results


def synthesize_drift_results(query: str, drift_results: dict) -> str:
    """
    Use Gemini to synthesize DRIFT results.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        return "⚠️ Synthesis unavailable (google-generativeai not found)"

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "your_gemini_api_key_here" in api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ Synthesis unavailable (missing API key)"

    genai.configure(api_key=api_key)

    context_parts = []
    for comm in drift_results.get("primer", []):
        context_parts.append(f"Community {comm['community_id']}: {comm['summary']}")

    seen = set()
    for entity in drift_results.get("entities", []):
        if entity["name"] not in seen:
            parts = [f"Entity: {entity['name']} ({entity.get('entity_type', 'concept')})"]
            if entity.get("description"):
                parts.append(f"  - {entity['description']}")
            context_parts.append("\n".join(parts))
            seen.add(entity["name"])

    context = "\n\n".join(context_parts)

    synthesis_prompt = f"""You are an expert analyst synthesizing knowledge graph search results.
USER QUERY: "{query}"
RETRIEVED CONTEXT:
{context}
TASK: Synthesize these results into 2-3 paragraphs that answer the query and identify patterns.
Keep it concise but insightful."""

    try:
        model = genai.GenerativeModel("gemini-3-flash-preview")
        response = model.generate_content(synthesis_prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Synthesis failed: {e}"


def main():
    args = sys.argv[1:]
    if not args or (args[0].startswith("-") and "--help" not in args):
        print(
            'Usage: python3 query_graphrag.py "Query" [--json] [--local-only] [--global-only] [--deep] [--synthesize]'
        )
        sys.exit(1)

    query = args[0]
    json_mode = "--json" in args
    local_only = "--local-only" in args
    global_only = "--global-only" in args
    expand_mode = "--expand" in args
    deep_mode = "--deep" in args
    synthesize_mode = "--synthesize" in args

    # DRIFT / Deep Mode
    if deep_mode:
        drift_results = drift_search(query)
        synthesis = None
        if synthesize_mode:
            synthesis = synthesize_drift_results(query, drift_results)
            drift_results["synthesis"] = synthesis

        if json_mode:
            print(json.dumps(drift_results, indent=2))
        else:
            print(f'🌊 DRIFT SEARCH: "{query}"')
            print("=" * 60)
            if drift_results["primer"]:
                print("\n─── Phase 1: Primer ───")
                for comm in drift_results["primer"]:
                    print(f"🌐 Community {comm['community_id']}")
                    print(f"   {comm['summary']}")
            if drift_results["entities"]:
                print("\n─── Phase 2: Fan-Out ───")
                for e in drift_results["entities"]:
                    print(f"🏷️  {e['name']}")
            if synthesis:
                print("\n─── Phase 3: Synthesis ───")
                print(synthesis)
        return

    # Standard Search
    all_results = []

    if not global_only:
        # Move imports inside to avoid overhead if only doing global
        all_results.extend(search_vectors(query))
        all_results.extend(search_entities(query, expand=expand_mode))

    if not local_only:
        all_results.extend(search_communities(query))

    if json_mode:
        print(json.dumps(all_results, indent=2))
    else:
        print(f'🔎 GRAPHRAG QUERY: "{query}"')
        print("=" * 60)

        vectors = [r for r in all_results if r["type"] == "vector"]
        entities = [r for r in all_results if r["type"] == "entity"]
        communities = [r for r in all_results if r["type"] == "community"]

        if vectors:
            print(f"\n─── Vector Matches ({len(vectors)}) ───")
            for v in vectors:
                print(f"📁 {v['file']} ({v['similarity']:.1%})")

        if entities:
            print(f"\n─── Entity Matches ({len(entities)}) ───")
            for e in entities:
                print(f"🏷️  {e['name']} ({e['entity_type']})")

        if communities:
            print(f"\n─── Community Matches ({len(communities)}) ───")
            for c in communities:
                print(f"🌐 Community {c['community_id']}")
                print(f"   {c['summary']}")


if __name__ == "__main__":
    main()
