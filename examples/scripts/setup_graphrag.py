#!/usr/bin/env python3
"""
setup_graphrag.py — Automated GraphRAG Environment Setup

This script sets up a dedicated Python 3.12 virtual environment for GraphRAG,
bypassing the system's Python 3.13 incompatibility.

Usage:
    python3 .agent/scripts/setup_graphrag.py

Requirements:
    - 'uv' (fast python package manager) must be installed.
    - Internet connection to download Python 3.12.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
UV_PATH = Path.home() / ".local" / "bin" / "uv"  # Dynamic home resolution
GRAPH_ENV_DIR = WORKSPACE / ".agent" / "graphrag_env"

def check_uv():
    """Ensure uv is installed."""
    if not UV_PATH.exists():
        print("❌ 'uv' not found at ~/.local/bin/uv")
        print("   Installing uv...")
        subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True, check=True)
    return str(UV_PATH)

def create_venv(uv):
    """Create Python 3.12 environment."""
    if GRAPH_ENV_DIR.exists():
        print(f"✅ Environment exists: {GRAPH_ENV_DIR}")
        # Check python version
        python_exe = GRAPH_ENV_DIR / "bin" / "python3"
        res = subprocess.run([str(python_exe), "--version"], capture_output=True, text=True)
        if "3.12" in res.stdout:
            print("   Python version verified: 3.12")
            return
        else:
            print(f"⚠️  Wrong version ({res.stdout.strip()}). Recreating...")
            shutil.rmtree(GRAPH_ENV_DIR)

    print("🚀 Creating GraphRAG environment (Python 3.12)...")
    cmd = [uv, "venv", str(GRAPH_ENV_DIR), "--python", "3.12"]
    subprocess.run(cmd, check=True)

def install_deps(uv):
    """Install GraphRAG and dependencies."""
    print("📦 Installing graphrag...")
    python_exe = GRAPH_ENV_DIR / "bin" / "python3"
    
    # We use 'uv pip install' targeting the venv python
    cmd = [
        uv, "pip", "install", 
        "--python", str(python_exe),
        "graphrag", 
        "google-generativeai", 
        "chromadb", 
        "chromadb", 
        "networkx",
        "sentence_transformers"
    ]
    subprocess.run(cmd, check=True)

def main():
    print("=== GraphRAG Setup (Compatibility Fix) ===")
    
    try:
        uv = check_uv()
        create_venv(uv)
        install_deps(uv)
        
        print("\n✅ Setup complete!")
        print(f"   Venv: {GRAPH_ENV_DIR}")
        print("   You can now run: python3 .agent/scripts/index_graphrag.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
