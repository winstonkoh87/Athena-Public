#!/usr/bin/env python3
"""
Legacy Shim for Agentic Search.
Delegates to `athena.tools.agentic_search`.
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path
src_path = (Path(__file__).parent.parent.parent / "Athena-Public" / "src").resolve()
if src_path.exists():
    sys.path.insert(0, str(src_path))

from athena.tools.agentic_search import run_agentic_search

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Agentic Search (RAG v2)")
    parser.add_argument("query", help="Complex search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument(
        "--no-validate", action="store_true", help="Skip cosine validation"
    )
    parser.add_argument("--debug", action="store_true", help="Show debug signals")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    run_agentic_search(
        query=args.query,
        limit=args.limit,
        validate=not args.no_validate,
        debug=args.debug,
        json_output=args.json,
    )
