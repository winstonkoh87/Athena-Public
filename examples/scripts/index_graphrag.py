#!/usr/bin/env python3
"""
index_graphrag.py — Full GraphRAG Indexing Orchestrator (v2.0)

Runs the complete GraphRAG indexing pipeline using the isolated
Python 3.12 environment in .agent/graphrag_env (required for compatibility).

Steps:
1. embed_codex.py — Vector embeddings
2. extract_entities.py — Entity extraction
3. build_graph.py — Knowledge graph + communities

Usage:
    python3 .agent/scripts/index_graphrag.py
    python3 .agent/scripts/index_graphrag.py --skip-embed  # Skip vector embedding
"""

import sys
import subprocess
import shutil
from pathlib import Path
import time

# === Configuration ===
WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = WORKSPACE / ".agent" / "scripts"
VENV_PYTHON = WORKSPACE / ".agent" / "graphrag_env" / "bin" / "python3"


def get_interpreter() -> str:
    """Return the correct Python interpreter path."""
    if VENV_PYTHON.exists():
        # Use isolated 3.12 venv if available
        return str(VENV_PYTHON)
    else:
        # Fallback to system python (will validly fail if 3.13)
        print("⚠️  Warning: GraphRAG venv not found. Using system python.")
        return sys.executable


def run_script(script_name: str, args: list = None, retries: int = 3) -> bool:
    """Run a Python script with exponential backoff retry."""
    script_path = SCRIPTS_DIR / script_name
    interpreter = get_interpreter()

    cmd = [interpreter, str(script_path)]
    if args:
        cmd.extend(args)

    for attempt in range(1, retries + 1):
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            if attempt < retries:
                wait_time = 2 ** (attempt - 1)
                print(
                    f"⚠️  {script_name} failed (attempt {attempt}/{retries}). Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                print(f"❌ {script_name} failed permanently after {retries} attempts.")
                return False
        except OSError as e:
            print(f"❌ Execution failed: {e}")
            return False

    return False


def main():
    skip_embed = "--skip-embed" in sys.argv
    use_ollama = "--ollama" in sys.argv
    interpreter = get_interpreter()

    print("=" * 60)
    print(f"🚀 GRAPHRAG FULL INDEXING PIPELINE")
    print(f"🐍 Interpreter: {interpreter}")
    if use_ollama:
        print("🦙 Mode: Ollama (llama3.1:8b - Local)")
    print("=" * 60)

    if str(interpreter) == sys.executable and sys.version_info >= (3, 13):
        print("❌ Error: GraphRAG is incompatible with Python 3.13.")
        print("   Please install the venv: `python3 .agent/scripts/setup_graphrag.py`")
        return

    steps = []

    # Step 1: Vector embeddings
    if not skip_embed:
        print("\n" + "─" * 40)
        print("STEP 1/4: Vector Embeddings")
        print("─" * 40)
        if not run_script("embed_codex.py"):
            print("⚠️  Vector embedding failed, continuing...")
        else:
            steps.append("Vector embeddings")

    # Step 2: Entity extraction
    print("\n" + "─" * 40)
    print("STEP 2/4: Entity Extraction")
    print("─" * 40)

    extract_args = []
    if use_ollama:
        extract_args.append("--ollama")

    if not run_script("extract_entities.py", args=extract_args):
        print("❌ Entity extraction failed, stopping")
        return
    steps.append("Entity extraction")

    # Step 3: Graph building
    print("\n" + "─" * 40)
    print("STEP 3/4: Knowledge Graph + Communities")
    print("─" * 40)
    if not run_script("build_graph.py"):
        print("❌ Graph building failed")
        return
    steps.append("Knowledge graph")

    # Step 4: Supabase sync
    print("\n" + "─" * 40)
    print("STEP 4/4: Supabase Entity Sync")
    print("─" * 40)
    if not run_script("upload_entities_to_supabase.py"):
        print("⚠️  Supabase sync failed (non-blocking), continuing...")
    else:
        steps.append("Supabase sync")

    print("\n" + "=" * 60)
    print("✅ GRAPHRAG INDEXING COMPLETE")
    print("=" * 60)
    print(f"\nCompleted steps: {', '.join(steps)}")
    print("\nQuery your knowledge base:")
    print('  python3 .agent/scripts/query_graphrag.py "your query"')
    print("=" * 60)


if __name__ == "__main__":
    main()
