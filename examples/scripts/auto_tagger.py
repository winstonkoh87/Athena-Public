#!/usr/bin/env python3
"""
Auto-Tagger
Scans files and auto-generates #tags based on content using Gemini.
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client

load_dotenv()

SYSTEM_PROMPT = """You are a file tagger for the Athena knowledge management system. Given file content, generate appropriate hashtags.

Rules:
1. Generate 3-8 tags max
2. Use lowercase, no spaces (use hyphens if needed)
3. Include: type tags (#casestudy, #protocol, #reference), topic tags (#psychology, #trading, #ai), and any specific tags
4. Format: One line of space-separated tags like: #tag1 #tag2 #tag3
5. Output ONLY the tags, nothing else"""

def generate_tags(content: str, filename: str) -> str:
    """Generate tags for file content."""
    client = get_client()
    
    prompt = f"""{SYSTEM_PROMPT}

Filename: {filename}

Content (first 2000 chars):
{content[:2000]}

Tags:"""
    
    response = client.generate(prompt)
    
    # Clean up response - ensure it's just tags
    tags = response.strip()
    # Filter to only hashtag words
    words = tags.split()
    tags = " ".join(w for w in words if w.startswith("#"))
    
    return tags

def update_file_tags(file_path: Path, tags: str, dry_run: bool = False) -> bool:
    """Add or update tags in a file's Tagging section."""
    content = file_path.read_text(encoding="utf-8")
    
    # Check if file already has a Tagging section
    if "## Tagging" in content or "**Tags**:" in content:
        print(f"  ⚠️ Already has tags, skipping: {file_path.name}")
        return False
    
    # Add tags at the end
    new_content = content.rstrip() + f"\n\n---\n**Tags**: {tags}\n"
    
    if dry_run:
        print(f"  Would add: {tags}")
        return True
    
    file_path.write_text(new_content, encoding="utf-8")
    return True

def main():
    parser = argparse.ArgumentParser(description="Auto-generate tags for files")
    parser.add_argument("files", nargs="*", help="Files to tag")
    parser.add_argument("--dir", help="Directory to scan for .md files")
    parser.add_argument("--dry-run", action="store_true", help="Show tags without modifying files")
    args = parser.parse_args()

    files_to_process = []
    
    if args.files:
        files_to_process.extend(Path(f) for f in args.files)
    
    if args.dir:
        files_to_process.extend(Path(args.dir).rglob("*.md"))
    
    if not files_to_process:
        parser.print_help()
        sys.exit(1)

    print(f"🏷️ Auto-Tagger ({'DRY RUN' if args.dry_run else 'LIVE'})")
    print(f"   Processing {len(files_to_process)} files\n")
    
    client = get_client()
    tagged = 0
    
    for file_path in files_to_process:
        if not file_path.exists():
            continue
        
        print(f"📄 {file_path.name}")
        content = file_path.read_text(encoding="utf-8")
        
        tags = generate_tags(content, file_path.name)
        print(f"   → {tags}")
        
        if update_file_tags(file_path, tags, args.dry_run):
            tagged += 1
    
    print(f"\n✅ Tagged {tagged} files")

if __name__ == "__main__":
    main()
