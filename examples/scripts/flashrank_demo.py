#!/usr/bin/env python3
"""
athena.core.optimization.flashrank_demo
=======================================
FlashRank "Green Zone" Re-ranking Demo

Demonstrates ultra-fast CPU re-ranking of Hybrid RAG results using quantized Cross-Encoders.
Includes "Freshness Bias" logic to prefer recent Web results over older Local results when scores are close.

Dependencies:
    pip install flashrank

Usage:
    python3 flashrank_demo.py
"""

import sys
import time
from typing import List, Dict

# Mock the FlashRank import to allow the script to run without the package installed
# In production, remove this mock and use: from flashrank import Ranker, RerankRequest
try:
    from flashrank import Ranker, RerankRequest
except ImportError:
    print("⚠️  FlashRank not installed. Using MockRanker for demonstration.")

    class RerankRequest:
        def __init__(self, query, passages):
            self.query = query
            self.passages = passages

    class Ranker:
        def __init__(self, model_name, cache_dir):
            self.model_name = model_name

        def rerank(self, request):
            # Mock scoring logic based on text match
            results = []
            q_terms = request.query.lower().split()

            for p in request.passages:
                score = 0.5
                text = p["text"].lower()
                for term in q_terms:
                    if term in text:
                        score += 0.2

                # Mock: Boost 'Prime Minister' if in query
                if (
                    "prime minister" in request.query.lower()
                    and "prime minister" in text
                ):
                    score += 0.3

                # Mock: Boost 'Current' / '2024'
                if "2024" in text or "2025" in text:
                    score += 0.1

                p["score"] = min(0.99, score)
                results.append(p)

            # Sort desc
            return sorted(results, key=lambda x: x["score"], reverse=True)


# --- CORE LOGIC ---


def hybrid_pipeline_with_flashrank(
    query: str, local_results: List[Dict], web_results: List[Dict]
):
    """
    Refines a mix of Local and Web results using FlashRank + Freshness Bias.
    """

    # 1. Initialize Ranker
    # Use 'ms-marco-TinyBERT-L-2-v2' for max speed, or 'ms-marco-MiniLM-L-12-v2' for accuracy
    ranker = Ranker(
        model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./opt/flashrank_cache"
    )

    # 2. Standardization
    passages = []

    # Process Local Results
    for idx, doc in enumerate(local_results):
        passages.append(
            {
                "id": f"local_{idx}",
                "text": doc.get("content"),
                "meta": {"source": "local_wikipedia", "original_data": doc},
            }
        )

    # Process Web Results
    for idx, doc in enumerate(web_results):
        passages.append(
            {
                "id": f"web_{idx}",
                "text": doc.get("content"),
                "meta": {
                    "source": "web_search",
                    "url": doc.get("url"),
                    "original_data": doc,
                },
            }
        )

    print(f"⚡ [FlashRank] Reranking {len(passages)} documents for query: '{query}'...")
    start_time = time.time()

    # 3. Execution
    rerankrequest = RerankRequest(query=query, passages=passages)
    ranked_results = ranker.rerank(rerankrequest)

    latency = (time.time() - start_time) * 1000
    print(f"   => Done in {latency:.2f}ms")

    # 4. Freshness Bias (Post-Processing)
    # Strategy: If a Web result is within 5% of a Local result, bump it up.

    # Simple re-sort with bias
    final_results = []
    for r in ranked_results:
        # Clone to avoid mutating original
        item = r.copy()

        # Apply Bias
        if item["meta"]["source"] == "web_search":
            # Heuristic: Boost Web by 5% to prefer freshness
            item["score"] = item["score"] * 1.05
            item["meta"]["boosted"] = True

        final_results.append(item)

    # Re-sort after boost
    final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)

    # Cutoff Top 5
    return final_results[:5]


# --- DEMO ---

if __name__ == "__main__":
    query = "Current Prime Minister of Singapore"

    # Mock Data
    local_hits = [
        {
            "content": "Lee Hsien Loong is the Prime Minister of Singapore (2023 snapshot)."
        },
        {"content": "Singapore's political system is a parliamentary republic."},
        {"content": "History of Singapore: Founded by Raffles in 1819."},
    ]
    web_hits = [
        {
            "content": "Lawrence Wong to take over as PM on May 15, 2024.",
            "url": "straitstimes.com",
        },
        {
            "content": "Best places to eat in Singapore 2026.",
            "url": "foodblog.com",
        },  # Noise
        {
            "content": "Singapore GDP grows by 2% in Q1 2025.",
            "url": "businesstimes.com.sg",
        },
    ]

    ranked_docs = hybrid_pipeline_with_flashrank(query, local_hits, web_hits)

    print(f"\n🏆 Final Top 5 Context:")
    for i, doc in enumerate(ranked_docs):
        boost_tag = " [BOOSTED]" if doc["meta"].get("boosted") else ""
        print(
            f"   {i + 1}. [{doc['score']:.4f}]{boost_tag} {doc['meta']['source'].upper()}: {doc['text']}"
        )
