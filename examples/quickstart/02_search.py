#!/usr/bin/env python3
"""
Athena Quickstart: Search Demo
==============================

This script demonstrates the hybrid search functionality.
It works in LOCAL_STUB mode by default (no Supabase required).

Usage:
    python examples/quickstart/02_search.py "your query"
    python examples/quickstart/02_search.py "position sizing"
"""

import sys
from pathlib import Path

# Add src to path for development mode
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from athena.core.models import SearchResult

# ============================================
# LOCAL STUB MODE
# ============================================
# When True, uses mock data instead of Supabase
# Set to False if you have configured .env
LOCAL_STUB_MODE = True


def mock_search(query: str) -> list:
    """
    Mock search results for demo purposes.
    Returns fake results to demonstrate the data structure.
    """
    mock_data = [
        SearchResult(
            id="Protocol 46: Trading Methodology",
            content="Max daily loss: 2% of account. Hard stop. No revenge trading after 2 consecutive losses.",
            source="vector",
            score=0.89,
            rrf_score=0.0328,
            metadata={"type": "protocol", "path": "protocols/trading/risk_limits.md"}
        ),
        SearchResult(
            id="Session 2025-03-14: Risk Framework",
            content="Established position sizing rules and psychological safeguards.",
            source="vector",
            score=0.82,
            rrf_score=0.0312,
            metadata={"type": "session"}
        ),
        SearchResult(
            id="Canonical:L45",
            content="| Max Daily Loss | 2% | Hard Stop |",
            source="canonical",
            score=1.0,
            rrf_score=0.0295,
        ),
    ]

    # Filter by query (simple keyword match)
    keywords = query.lower().split()
    filtered = []
    for r in mock_data:
        if any(k in r.content.lower() or k in r.id.lower() for k in keywords):
            filtered.append(r)

    return filtered if filtered else mock_data[:2]


def main():
    # Get query from args or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "position sizing rules"

    print("=" * 60)
    print("🔍 ATHENA SEARCH DEMO")
    print(f"   Query: \"{query}\"")
    print(f"   Mode: {'LOCAL STUB' if LOCAL_STUB_MODE else 'LIVE (Supabase)'}")
    print("=" * 60)

    if LOCAL_STUB_MODE:
        results = mock_search(query)
    else:
        # Live mode - requires .env configuration
        try:
            from athena.tools.search import run_search
            results = run_search(query, limit=5)
        except Exception as e:
            print(f"\n❌ Live search failed: {e}")
            print("   Tip: Set LOCAL_STUB_MODE = True or configure .env")
            return 1

    print(f"\n🏆 TOP {len(results)} RESULTS:\n")

    for i, result in enumerate(results, 1):
        # Confidence badge
        if result.rrf_score >= 0.03:
            badge = "[HIGH]"
        elif result.rrf_score >= 0.02:
            badge = "[MED]"
        else:
            badge = "[LOW]"

        print(f"  {i}. {badge} [RRF:{result.rrf_score:.4f}] {result.id}")
        print(f"     📄 {result.content[:80]}...")
        if result.metadata.get('path'):
            print(f"     📁 {result.metadata['path']}")
        print()

    print("=" * 60)
    print("✅ Search complete")

    if LOCAL_STUB_MODE:
        print("\n💡 To enable live search:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your API keys")
        print("   3. Set LOCAL_STUB_MODE = False in this file")

    return 0


if __name__ == "__main__":
    sys.exit(main())
