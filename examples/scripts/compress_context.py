#!/usr/bin/env python3
"""
Athena Context Compressor
Uses Gemini API with automatic model fallback to generate compressed summaries.
"""
import os
import sys
import hashlib
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import pathspec

# Import our fallback client
sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client, GeminiClient

load_dotenv()

# --- Constants ---
CACHE_DIR = Path(".context/cache/compression")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_METADATA_FILE = CACHE_DIR / "metadata_index.json"

DEFAULT_IGNORE_LIST = [
    ".git", "venv", ".summary_files", "__pycache__",
    ".vscode", ".idea", "node_modules", "build", "dist",
    "*.pyc", "*.pyo", "*.egg-info", ".DS_Store", ".env",
    ".context", ".agent", ".framework"
]

SYSTEM_PROMPT = """You are a code documenter. Your purpose is to provide useful summaries for inclusion as reference for future prompts. Provide a concise summary of the given code and any notes that will be useful for other ChatBots to understand how it works. Include specific documentation about each function, class, and relevant parameters."""

# --- Utilities ---

def get_file_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_cache_index():
    if CACHE_METADATA_FILE.exists():
        try:
            with open(CACHE_METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache_index(index_data):
    with open(CACHE_METADATA_FILE, 'w') as f:
        json.dump(index_data, f, indent=2)

def get_cached_summary(file_path: str, content_hash: str, index_data: dict):
    if file_path in index_data:
        entry = index_data[file_path]
        if entry.get("hash") == content_hash:
            summary_file = CACHE_DIR / entry.get("summary_file")
            if summary_file.exists():
                return summary_file.read_text(encoding="utf-8")
    return None

def cache_summary(file_path: str, content_hash: str, summary: str, index_data: dict):
    summary_filename = f"{hashlib.md5(file_path.encode()).hexdigest()}_{content_hash[:8]}.md"
    summary_path = CACHE_DIR / summary_filename
    summary_path.write_text(summary, encoding="utf-8")
    
    index_data[file_path] = {
        "hash": content_hash,
        "summary_file": summary_filename,
        "timestamp": os.path.getmtime(summary_path)
    }
    save_cache_index(index_data)

def is_text_file(file_path: Path) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        if b'\x00' in chunk: return False
        return True
    except:
        return False

def get_gitignore_spec(root_dir: Path):
    gitignore_path = root_dir / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            return pathspec.PathSpec.from_lines('gitwildmatch', f)
    return None

def compress_content(client: GeminiClient, file_path: str, content: str, mock: bool = False) -> str:
    """Calls Gemini to summarize content with automatic fallback."""
    if mock:
        return f"Summary of {file_path} (Mocked)\n- Content length: {len(content)}\n- MD5: {get_file_hash(content)}"

    prompt = f"{SYSTEM_PROMPT}\n\nFile: {file_path}\n\n{content}"
    return client.generate(prompt)

# --- Main Logic ---

def process_file(file_path: Path, client: GeminiClient, index_data: dict, args):
    try:
        relative_path = file_path.relative_to(Path.cwd())
    except:
        relative_path = file_path

    if args.verbose:
        print(f"Processing: {relative_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading {relative_path}: {e}"

    current_hash = get_file_hash(content)
    
    # Check cache
    cached = get_cached_summary(str(relative_path), current_hash, index_data)
    if cached and not args.force:
        if args.verbose: print(f"  -> Cache Hit")
        return f"## File: {relative_path} [Cached]\n\n{cached}\n\n---\n"
    
    # Compress with fallback
    if args.verbose: print(f"  -> Compressing ({'Mock' if args.mock else 'Gemini API'})...")
    try:
        summary = compress_content(client, str(relative_path), content, args.mock)
        if args.verbose and client:
            print(f"     Used model: {client.last_successful_model}")
    except Exception as e:
        summary = f"Error: {e}"
    
    cache_summary(str(relative_path), current_hash, summary, index_data)
    
    return f"## File: {relative_path} [AI Compressed]\n\n{summary}\n\n---\n"

def main():
    parser = argparse.ArgumentParser(description="Athena Context Compressor (Gemini with Fallback)")
    parser.add_argument("--files", nargs="+", help="Specific files to compress")
    parser.add_argument("--dir", help="Directory to walk recursively")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--force", action="store_true", help="Force regenerate summaries (ignore cache)")
    parser.add_argument("--verbose", action="store_true", help="Show progress")
    parser.add_argument("--mock", action="store_true", help="Mock API calls for testing")
    args = parser.parse_args()

    # Init Gemini with fallback
    client = None
    if not args.mock:
        try:
            client = get_client()
            if args.verbose:
                print(f"🔗 Gemini client ready. Fallback chain: {' → '.join(client.models.keys())}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    index_data = load_cache_index()
    files_to_process = []
    
    # Collect files
    if args.files:
        for f in args.files:
            p = Path(f).resolve()
            if p.exists() and p.is_file():
                files_to_process.append(p)
    
    if args.dir:
        root = Path(args.dir).resolve()
        spec = get_gitignore_spec(root)
        
        for root_dir, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_LIST]
            
            for f in files:
                file_path = Path(root_dir) / f
                
                try:
                    rel_path = file_path.relative_to(root)
                    if spec and spec.match_file(str(rel_path)):
                        continue
                    if any(str(rel_path).endswith(ext.replace("*", "")) for ext in DEFAULT_IGNORE_LIST if ext.startswith("*")):
                        continue
                    if not is_text_file(file_path):
                        continue
                        
                    files_to_process.append(file_path)
                except Exception as e:
                    if args.verbose: print(f"Skipping {f}: {e}")

    # Process
    final_markdown = f"# Compressed Context Summary\nGenerated by Athena Context Compressor (Gemini with Fallback)\n\n"
    
    for f in files_to_process:
        chunk = process_file(f, client, index_data, args)
        final_markdown += chunk
        
    # Output
    if args.output:
        Path(args.output).write_text(final_markdown, encoding="utf-8")
        print(f"Summary written to {args.output}")
    else:
        print(final_markdown)

if __name__ == "__main__":
    main()
