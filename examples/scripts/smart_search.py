#!/usr/bin/env python3
"""
Legacy Shim for Smart Search.
Delegates to `athena.tools.search`.
This file preserves CLI compatibility while logic moves to the SDK.
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path to allow importing athena package
# .agent/scripts/smart_search.py -> .agent/scripts -> .agent -> root -> src
src_path = (Path(__file__).parent.parent.parent / "src").resolve()
sys.path.insert(0, str(src_path))

from athena.core.governance import get_governance
from athena.tools.search import run_search

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Smart Search (Shim -> SDK)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument(
        "--strict", action="store_true", help="Suppress low-confidence results"
    )
    parser.add_argument(
        "--rerank", action="store_true", help="Use Cross-Encoder reranking"
    )
    parser.add_argument("--debug", action="store_true", help="Show debug signals")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--include-personal",
        action="store_true",
        help="Include personal domain in results",
    )
    args = parser.parse_args()

    # Governance: Mark search as performed for this interaction
    try:
        get_governance().mark_search_performed(args.query)
    except Exception as e:
        if args.debug:
            print(f"DEBUG: Governance check failed: {e}", file=sys.stderr)

    try:
        run_search(
            query=args.query,
            limit=args.limit,
            strict=args.strict,
            rerank=args.rerank,
            debug=args.debug,
            json_output=args.json,
            include_personal=args.include_personal,
        )
    except Exception as e:
        print(f"⚠️  Smart Search Partial Fail: {e}", file=sys.stderr)
        # Fallback to fast search or just exit gracefully so workflow doesn't crash
        sys.exit(0)
