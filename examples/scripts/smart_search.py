#!/usr/bin/env python3
"""
Legacy Shim for Smart Search.
Delegates to `athena.tools.search`.
This file preserves CLI compatibility while logic moves to the SDK.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to sys.path to allow importing athena package
# .agent/scripts/smart_search.py -> .agent/scripts -> .agent -> root -> src
src_path = (Path(__file__).parent.parent.parent / "src").resolve()
sys.path.insert(0, str(src_path))
print(f"DEBUG: Added {src_path} to sys.path", file=sys.stderr)
print(f"DEBUG: sys.path: {sys.path}", file=sys.stderr)

from athena.tools.search import run_search
from athena.core.governance import get_governance

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
    get_governance().mark_search_performed(args.query)

    run_search(
        query=args.query,
        limit=args.limit,
        strict=args.strict,
        rerank=args.rerank,
        debug=args.debug,
        json_output=args.json,
        include_personal=args.include_personal,
    )
