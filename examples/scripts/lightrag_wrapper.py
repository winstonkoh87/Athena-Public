#!/usr/bin/env python3
"""
LightRAG Wrapper for Project Athena (Sovereign Memory)
Purpose:
  - Index markdown files from .agent/skills/ and .context/memories/ into a local Graph RAG.
  - Query the graph for multi-hop reasoning.
  - Usage:
      python3 lightrag_wrapper.py --index --dir .agent/skills/protocols/
      python3 lightrag_wrapper.py --query "How does Protocol 10 relate to Protocol 50?" --mode hybrid
"""

import os
import argparse
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc, always_get_an_event_loop

# --- Configuration ---
WORKING_DIR = ".context/memory_bank/lightrag_store"
DEFAULT_LLM_MODEL = "llama3.1:8b"  # Optimizing for speed/quality balance on local
DEFAULT_EMBED_MODEL = (
    "llama3.1:8b"  # Fallback to LLM for embedding if nomic is unavailable
)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def setup_rag(working_dir=WORKING_DIR):
    """Initializes LightRAG with Ollama backend."""
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=ollama_model_complete,
        llm_model_name=DEFAULT_LLM_MODEL,
        llm_model_max_async=4,
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(texts, embed_model=DEFAULT_EMBED_MODEL),
        ),
    )
    return rag


def index_directory(rag, directory_path):
    """Recursively indexes all .md files in a directory."""
    if not os.path.exists(directory_path):
        logging.error(f"Directory not found: {directory_path}")
        return

    files_indexed = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if not content.strip():
                            continue

                        # Use relative path as ID/Source reference
                        rel_path = os.path.relpath(file_path, start=os.getcwd())
                        logging.info(f"Indexing: {rel_path}")

                        # LightRAG insert
                        rag.insert(content)
                        files_indexed += 1
                except Exception as e:
                    logging.error(f"Failed to index {file_path}: {e}")

    logging.info(f"Indexing complete. Processed {files_indexed} files.")


def query_graph(rag, query_text, mode="hybrid"):
    """Queries the graph using specified mode (local, global, hybrid)."""
    logging.info(f"Querying ({mode}): {query_text}")

    result = rag.query(query_text, param=QueryParam(mode=mode))
    return result


def main():
    parser = argparse.ArgumentParser(description="Athena LightRAG Interface")
    parser.add_argument(
        "--index", action="store_true", help="Index files from specified directory"
    )
    parser.add_argument(
        "--dir", type=str, help="Directory to index (required if --index is set)"
    )
    parser.add_argument("--query", type=str, help="Query text")
    parser.add_argument(
        "--mode",
        type=str,
        default="hybrid",
        choices=["local", "global", "hybrid", "naive"],
        help="Query mode",
    )
    parser.add_argument("--test", action="store_true", help="Run a quick smoke test")
    parser.add_argument(
        "--insert", type=str, help="Insert text directly into the graph"
    )

    args = parser.parse_args()

    rag = setup_rag()
    loop = always_get_an_event_loop()
    loop.run_until_complete(rag.initialize_storages())

    if args.test:
        print("Running smoke test...")
        rag.insert("Project Athena is a Sovereign AI system designed by [AUTHOR].")
        res = rag.query("Who designed Project Athena?", param=QueryParam(mode="local"))
        print(f"Test Result: {res}")
        return

    if args.index:
        if not args.dir:
            print("Error: --dir is required when --index is True")
            return
        index_directory(rag, args.dir)

    if args.insert:
        print(f"Inserting text: {args.insert[:50]}...")
        rag.insert(args.insert)
        print("Text inserted successfully.")

    if args.query:
        answer = query_graph(rag, args.query, mode=args.mode)
        print("\n=== LightRAG Answer ===")
        print(answer)
        print("=======================\n")


if __name__ == "__main__":
    main()
