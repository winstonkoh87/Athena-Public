#!/usr/bin/env python3
"""
metadata_extractor.py — Mass Protocol Injector
==============================================
Scans all .md files in .agent/skills/protocols/, extracts metadata,
and populates protocols.json.

Heuristic:
1. ID & Name: From filename (e.g., `121-amoral-realism.md`)
2. Tags: From directory (e.g., `.../business/` -> `business`) and internal `#tags`.
3. Use Cases: "Contextual Guessing" based on keywords.
"""

import os
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
PROTOCOLS_DIR = PROJECT_ROOT / ".agent" / "skills" / "protocols"
CASE_STUDIES_DIR = PROJECT_ROOT / ".context" / "memories" / "case_studies"
REGISTRY_PATH = PROJECT_ROOT / ".agent" / "protocols.json"

# Heuristic Maps
KEYWORD_MAP = {
    "negotiation": "Negotiating with a client or partner",
    "pricing": "Setting prices or evaluating costs",
    "code": "Writing or refactoring code",
    "debug": "Fixing a bug or error",
    "design": "Creating UI/UX or visual assets",
    "strategy": "Planning high-level business moves",
    "psychology": "Analyzing human behavior or bias",
    "content": "Writing articles or copy",
    "automation": "Building workflows or scripts",
    "marketing": "Launching campaigns or ads",
    "risk": "Evaluating downside or ruin",
    "learning": "Acquiring new skills or knowledge"
}

def extract_metadata(filepath):
    """Parses a single MD file for signal."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(2000) # Read first 2k chars
            
        # Extract ID and Name from filename
        filename = filepath.name
        match = re.match(r'(\d+)-(.+)\.md', filename)
        if not match:
            return None
        
        pid = match.group(1)
        name_slug = match.group(2).replace("-", " ").title()
        
        # Extract Real Name from H1
        h1_match = re.search(r'^# Protocol \d+: (.+)$', content, re.MULTILINE)
        if h1_match:
            real_name = h1_match.group(1).split('(')[0].strip()
        else:
            real_name = name_slug
            
        # Extract Context Tags (Directory)
        context_tags = []
        parent_dir = filepath.parent.name
        if parent_dir != "protocols":
            context_tags.append(parent_dir)
            
        # Extract Internal Tags
        tag_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if tag_match:
            raw_tags = tag_match.group(1).split()
            context_tags.extend([t.replace("#", "").lower() for t in raw_tags])
            
        # Derive Use Cases
        use_cases = []
        full_text_lower = content.lower()
        for key, guess in KEYWORD_MAP.items():
            if key in filename or key in full_text_lower:
                use_cases.append(guess)
        
        if not use_cases:
            use_cases.append(f"Applying {parent_dir} principles")
            
        return {
            "id": pid,
            "name": real_name,
            "path": str(filepath.relative_to(PROJECT_ROOT)),
            "status": "passive", # Default
            "context_tags": list(set(context_tags)),
            "applied_use_cases": list(set(use_cases))
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def extract_case_study_metadata(filepath):
    """Parses a Case Study MD file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(2000)
            
        filename = filepath.name
        
        # ID is filename base
        pid = filename.replace(".md", "")
        
        # Name: Try to find H1 or Title
        h1_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if h1_match:
            real_name = h1_match.group(1).strip()
        else:
            real_name = pid.replace("_", " ").title()
            
        # Tags & Use Cases via Keyword Map
        use_cases = []
        full_text_lower = content.lower()
        for key, guess in KEYWORD_MAP.items():
            if key in filename or key in full_text_lower:
                use_cases.append(guess)
        
        if not use_cases:
            use_cases.append("Reference for parallel scenarios")
            
        return {
            "id": pid,
            "type": "case_study",
            "name": real_name,
            "path": str(filepath.relative_to(PROJECT_ROOT)),
            "status": "active", 
            "context_tags": ["case_study", "reference"],
            "applied_use_cases": list(set(use_cases))
        }
    except Exception as e:
        print(f"Error parsing case study {filepath}: {e}")
        return None

def main():
    if not PROTOCOLS_DIR.exists():
        print("Protocols dir not found.")
        return

    # Load existing to preserve manual edits
    existing = {}
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            existing = json.load(f).get("protocols", {})

    new_protocols = existing.copy()
    count = 0
    
    for root, dirs, files in os.walk(PROTOCOLS_DIR):
        for file in files:
            if file.endswith(".md"):
                path = Path(root) / file
                meta = extract_metadata(path)
                if meta:
                    pid = meta["id"]
                    # Only update if strict improvement or missing
                    if pid not in new_protocols:
                        new_protocols[pid] = meta
                        count += 1
                    else:
                        # Merge tags (don't overwrite manual use cases if they exist)
                        curr = new_protocols[pid]
                        curr["context_tags"] = list(set(curr.get("context_tags", []) + meta["context_tags"]))
                        if not curr.get("applied_use_cases"):
                            curr["applied_use_cases"] = meta["applied_use_cases"]

    # Scan Case Studies
    if CASE_STUDIES_DIR.exists():
        for root, dirs, files in os.walk(CASE_STUDIES_DIR):
            for file in files:
                if file.endswith(".md"):
                    path = Path(root) / file
                    meta = extract_case_study_metadata(path)
                    if meta:
                        pid = meta["id"]
                        if pid not in new_protocols:
                            new_protocols[pid] = meta
                            count += 1
    
    # Save
    final_data = {
        "meta": {"generated_at": "2025-12-28", "purpose": "Mass Context Map"},
        "protocols": new_protocols
    }
    
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(final_data, f, indent=4)
        
    print(f"✅ Injected {count} new protocols. Total: {len(new_protocols)}")

if __name__ == "__main__":
    main()
