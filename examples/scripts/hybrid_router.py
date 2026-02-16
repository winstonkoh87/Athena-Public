#!/usr/bin/env python3
"""
athena.core.orchestration.hybrid_router
=======================================
Hybrid RAG Router (Protocol 051) - v3.0 (HITL Bridge)

Routes queries between Local Knowledge (Static Exocortex) and Web Search (Manual Bridge)
using an interactive Human-in-the-Loop workflow.

Usage:
    python3 hybrid_router.py "Who is the US President?"
"""

import sys
import concurrent.futures
from typing import List, Dict, Literal
from dataclasses import dataclass
import os

# Import Kinetic Engine
try:
    from kinetic_engine import ExocortexClient
except ImportError:
    # Fallback if running outside of strict module path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from kinetic_engine import ExocortexClient


# --- 1. DATA SOURCES ---


def retrieve_local(query: str) -> List[Dict]:
    """
    Searches the Exocortex (SQLite FTS5) via Kinetic Engine.
    Returns logic-compatible dicts.
    """
    print(f"   [LOCAL] Searching Exocortex for: '{query}'")
    client = ExocortexClient()
    results = client.search(query, limit=5)

    formatted_results = []
    for r in results:
        formatted_results.append(
            {
                "content": r["abstract"] if r["abstract"] else r["title"],
                "source": f"exocortex:{r['url']}"
                if r.get("url")
                else "exocortex:internal",
                "score": 1.0,
            }
        )

    return formatted_results


def search_web_interactive(query: str) -> List[Dict]:
    """
    Prompts the USER to perform the search in Gemini/Browser and paste results.
    """
    print("\n" + "=" * 60)
    print(f"🛑 HITL ACTION REQUIRED: WEB SEARCH BRIDGE")
    print(f"Please ask your Gemini/ChatGPT window:")
    print(f"   'Search the web for \"{query}\" and summarize.'")
    print("-" * 60)
    print("Paste the result below (Press Enter then Ctrl+D to finish):")
    print("=" * 60)

    try:
        # Read multi-line input
        lines = sys.stdin.readlines()
        content = "".join(lines).strip()
    except KeyboardInterrupt:
        return [
            {"content": "User Aborted Web Search", "source": "user_abort", "score": 0.0}
        ]

    if not content:
        return [
            {"content": "User provided no input.", "source": "user_empty", "score": 0.0}
        ]

    return [{"content": content, "source": "manual_web_bridge", "score": 1.0}]


def classify_interactive(query: str) -> Literal["local_only", "web_only", "hybrid"]:
    """
    Heuristic first, then HITL fallback if ambiguous?
    Actually, to be fast, let's use a strong heuristic and allow override args.
    """
    q = query.lower()

    # strong web signals
    if any(
        x in q
        for x in [
            "latest",
            "news",
            "price",
            "current",
            "today",
            "2025",
            "2026",
            "president",
            "stock",
            "crypto",
        ]
    ):
        return "web_only"

    # strong local signals
    if any(
        x in q
        for x in [
            "history",
            "define",
            "what is",
            "concept",
            "principle",
            "protocol",
            "athena",
        ]
    ):
        return "local_only"

    # Default to Hybrid for maximum context
    return "hybrid"


# --- 2. CORE LOGIC ---


@dataclass
class RouteDecision:
    classification: Literal["local_only", "web_only", "hybrid"]
    local_query: str
    web_query: str
    reasoning: str


def route_query_logic(query: str) -> RouteDecision:
    """
    Decides how to route the query.
    """
    classification = classify_interactive(query)

    reasoning = f"Heuristic Classified as {classification.upper()}"

    return RouteDecision(
        classification=classification,
        local_query=query,
        web_query=query,
        reasoning=reasoning,
    )


# --- 3. ORCHESTRATION ---


def execute_hybrid_search(user_query: str):
    print(f"\n🚀 Processing: '{user_query}'")

    # Step 1: Route
    decision = route_query_logic(user_query)
    print(f"👉 Decision: {decision.classification.upper()} ({decision.reasoning})")

    local_results = []
    web_results = []

    # Step 2: Execution
    # We can't really parallelize effectively with blocking stdin, so we go sequential for HITL.

    if decision.classification in ["local_only", "hybrid"]:
        try:
            local_results = retrieve_local(decision.local_query)
        except Exception as e:
            print(f"   ❌ LOCAL failed: {e}")

    if decision.classification in ["web_only", "hybrid"]:
        # This is blocking interaction
        web_results = search_web_interactive(decision.web_query)

    # Step 3: Context Partitioning

    # Format the Prompt Structure
    print("\n🏁 Final Partitioned Prompt Structure:")
    print("-" * 40)
    print("SYSTEM: You have two distinct data streams.\n")

    print(f"--- STREAM A: FOUNDATIONAL KNOWLEDGE (Static Exocortex) ---")
    if local_results:
        for i, res in enumerate(local_results[:3]):
            content_preview = (
                (res["content"][:200] + "...")
                if len(res["content"]) > 200
                else res["content"]
            )
            print(f"[{i + 1}] {content_preview}")
    else:
        print("(No Local Data Found)")

    print(f"\n--- STREAM B: LIVE INTELLIGENCE (Manual Web Bridge) ---")
    if web_results:
        for i, res in enumerate(web_results[:1]):
            print(f"[User Paste] {res['content']}")
    else:
        print("(No Web Data Provided)")

    print("-" * 40)
    print("INSTRUCTION: Stream B trumps Stream A for current status.")

    return {"local": local_results, "web": web_results}


# --- 4. MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        execute_hybrid_search(query)
    else:
        print("Usage: python3 hybrid_router.py 'Your query here'")
