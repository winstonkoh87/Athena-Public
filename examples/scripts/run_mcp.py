#!/usr/bin/env python3
"""
run_mcp.py — MCP Server Launch Script
======================================
Ensures PYTHONPATH includes the SDK before starting the server.

Usage:
    python3 .agent/scripts/run_mcp.py           # stdio transport (IDE)
    python3 .agent/scripts/run_mcp.py --sse     # SSE transport (remote)
"""

import os
import sys
from pathlib import Path

# Resolve project root and ensure SDK is on path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SDK_PATH))

# Load .env for API keys
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

if __name__ == "__main__":
    from athena.mcp_server import mcp

    # Pass through CLI args
    import argparse

    parser = argparse.ArgumentParser(description="Athena MCP Server Launcher")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--port", type=int, default=8765, help="SSE port")
    args = parser.parse_args()

    print(
        f"⚡ Athena MCP Server starting ({('SSE:' + str(args.port)) if args.sse else 'stdio'})..."
    )

    if args.sse:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")
