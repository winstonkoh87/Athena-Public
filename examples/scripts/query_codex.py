#!/usr/bin/env python3
"""
query_codex.py — Semantic Search Interface for Zero-Point Codex

Queries the ChromaDB vector store for semantically similar content.

Usage:
    python3 .agent/scripts/query_codex.py "What do I know about adaptive latency?"
    python3 .agent/scripts/query_codex.py "protocol enforcement patterns"

Output:
    Top 5 matching chunks with file paths and relevance scores.
"""

import sys
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent
CHROMA_DIR = ROOT_DIR / ".agent" / "chroma_db"
COLLECTION_NAME = "codex"
TOP_K = 5


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 query_codex.py "Your query here"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    print("=" * 60)
    print(f'🔎 SEMANTIC SEARCH: "{query}"')
    print("=" * 60)

    # Check if DB exists
    if not CHROMA_DIR.exists():
        print("\n❌ ChromaDB not found. Run embed_codex.py first.")
        sys.exit(1)

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Use same embedding function as indexing
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Get collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    except ValueError:
        print("\n❌ Collection not found. Run embed_codex.py first.")
        sys.exit(1)

    # Query
    results = collection.query(
        query_texts=[query], n_results=TOP_K, include=["documents", "metadatas", "distances"]
    )

    # Display results
    print(f"\n📄 TOP {TOP_K} RESULTS:\n")

    for i, (doc, metadata, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        # Convert distance to similarity (cosine)
        similarity = 1 - distance
        file_path = metadata.get("file_path", "Unknown")
        chunk_idx = metadata.get("chunk_index", 0)
        total_chunks = metadata.get("total_chunks", 1)

        print(f"─── Result {i + 1} ───")
        print(f"📁 File: {file_path}")
        print(f"📊 Similarity: {similarity:.2%}")
        print(f"📦 Chunk: {chunk_idx + 1}/{total_chunks}")
        print(f"📝 Preview:")
        # Show first 300 chars of the chunk
        preview = doc[:300].replace("\n", " ")
        if len(doc) > 300:
            preview += "..."
        print(f"   {preview}")
        print()

    print("=" * 60)


if __name__ == "__main__":
    main()
