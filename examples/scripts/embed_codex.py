#!/usr/bin/env python3
"""
embed_codex.py — GraphRAG Indexing Script for Zero-Point Codex

Scans all .md files in .context/, .agent/skills/, and .framework/,
chunks them, embeds them using sentence-transformers, and stores
them in a local ChromaDB instance.

Usage:
    python3 .agent/scripts/embed_codex.py

Output:
    Creates/updates .agent/chroma_db/ with vector embeddings.
"""

import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent  # /Users/.../AI LLM
CHROMA_DIR = ROOT_DIR / ".agent" / "chroma_db"
COLLECTION_NAME = "codex"

# Directories to index
SCAN_DIRS = [
    ROOT_DIR / ".context",
    ROOT_DIR / ".agent" / "skills",
    ROOT_DIR / ".framework",
]

# Chunking config
# Chunking config
MAX_CHUNK_SIZE = 1000  # characters (approx 250 tokens, fits within 256 limit)
CHUNK_OVERLAP = 200


def get_all_md_files(directories: list[Path]) -> list[Path]:
    """Recursively find all .md files in the given directories."""
    files = []
    for directory in directories:
        if directory.exists():
            files.extend(directory.rglob("*.md"))
    return files


def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def main():
    print("=" * 60)
    print("🧠 CODEX EMBEDDING PIPELINE")
    print("=" * 60)
    
    # Initialize ChromaDB with persistent storage
    print(f"\n📁 Initializing ChromaDB at: {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Use sentence-transformers for embeddings (local, no API key)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Delete existing collection if it exists (fresh index)
    existing_collections = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️  Deleted existing collection (fresh index)")
    
    # Create collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Find all markdown files
    print("\n🔍 Scanning directories...")
    md_files = get_all_md_files(SCAN_DIRS)
    print(f"   Found {len(md_files)} markdown files")
    
    # Process each file
    total_chunks = 0
    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            chunks = chunk_text(content)
            
            # Generate IDs and metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path.stem}_{i}"
                metadata = {
                    "file_path": str(file_path.relative_to(ROOT_DIR)),
                    "file_name": file_path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                
                collection.add(
                    ids=[chunk_id],
                    documents=[chunk],
                    metadatas=[metadata]
                )
            
            total_chunks += len(chunks)
            print(f"   ✓ {file_path.name} ({len(chunks)} chunks)")
            
        except Exception as e:
            print(f"   ✗ {file_path.name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ INDEXING COMPLETE")
    print(f"   Files indexed: {len(md_files)}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Database: {CHROMA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
