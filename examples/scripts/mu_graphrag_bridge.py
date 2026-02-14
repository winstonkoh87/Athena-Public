#!/usr/bin/env python3
"""
mu_graphrag_bridge.py — Bridge mu codebase intelligence to GraphRAG

Exports mu's code structure as entities/relationships for the knowledge graph.

Usage:
    python3 .agent/scripts/mu_graphrag_bridge.py
    python3 .agent/scripts/mu_graphrag_bridge.py --refresh  # Re-bootstrap first

Output:
    Updates .agent/graphrag/entities.json with code structure entities
"""

import json
import subprocess
import sys
from pathlib import Path

# === Configuration ===
ROOT_DIR = Path(__file__).parent.parent.parent
GRAPHRAG_DIR = ROOT_DIR / ".agent" / "graphrag"
ENTITIES_FILE = GRAPHRAG_DIR / "entities.json"
MU_BINARY = Path.home() / ".local" / "bin" / "mu"


def run_mu_command(args: list[str]) -> str:
    """Run a mu command and return output."""
    cmd = [str(MU_BINARY)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT_DIR))
        return result.stdout
    except Exception as e:
        print(f"⚠️  mu command failed: {e}")
        return ""


def extract_code_entities() -> dict:
    """Extract code structure as GraphRAG entities."""
    entities = []
    relationships = []
    
    # Get compressed overview
    compress_output = run_mu_command(["compress", "."])
    
    if not compress_output:
        print("❌ No mu output - is mu installed?")
        return {"entities": [], "relationships": []}
    
    # Parse mu output for modules/files
    for line in compress_output.split("\n"):
        line = line.strip()
        
        # Module headers (## or ###)
        if line.startswith("##") or line.startswith("###"):
            name = line.lstrip("#").strip().rstrip("/")
            if name:
                entities.append({
                    "name": f"[CODE] {name}",
                    "type": "code_module",
                    "description": f"Code module from codebase",
                    "source_file": "_mu_bridge"
                })
        
        # Files (! prefix)
        elif line.startswith("!"):
            file_path = line[1:].strip()
            if file_path:
                entities.append({
                    "name": f"[FILE] {Path(file_path).name}",
                    "type": "code_file", 
                    "description": f"Source file: {file_path}",
                    "source_file": "_mu_bridge"
                })
    
    # Try to get function list if available
    query_output = run_mu_command(["query", "functions"])
    if query_output and "function" in query_output.lower():
        for line in query_output.split("\n"):
            if "::" in line or "fn " in line:
                entities.append({
                    "name": f"[FN] {line.strip()[:50]}",
                    "type": "code_function",
                    "description": "Function from codebase",
                    "source_file": "_mu_bridge"
                })
    
    return {"entities": entities, "relationships": relationships}


def merge_with_existing(new_data: dict) -> dict:
    """Merge new entities with existing GraphRAG entities."""
    if ENTITIES_FILE.exists():
        try:
            existing = json.loads(ENTITIES_FILE.read_text())
        except:
            existing = {"entities": [], "relationships": []}
    else:
        existing = {"entities": [], "relationships": []}
    
    # Remove old mu-bridge entities
    existing["entities"] = [
        e for e in existing.get("entities", [])
        if e.get("source_file") != "_mu_bridge"
    ]
    existing["relationships"] = [
        r for r in existing.get("relationships", [])
        if r.get("source_file") != "_mu_bridge"
    ]
    
    # Add new
    existing["entities"].extend(new_data["entities"])
    existing["relationships"].extend(new_data["relationships"])
    
    # Update stats
    existing["stats"] = existing.get("stats", {})
    existing["stats"]["code_entities"] = len(new_data["entities"])
    
    return existing


def main():
    print("=" * 60)
    print("🔌 MU → GRAPHRAG BRIDGE")
    print("=" * 60)
    
    # Check mu is installed
    if not MU_BINARY.exists():
        print(f"❌ mu not found at {MU_BINARY}")
        print("   Run: .agent/scripts/install_mu.sh")
        sys.exit(1)
    
    # Refresh bootstrap if requested
    if "--refresh" in sys.argv:
        print("\n🔄 Refreshing mu index...")
        subprocess.run([str(MU_BINARY), "bootstrap", "."], cwd=str(ROOT_DIR))
    
    # Extract entities
    print("\n📊 Extracting code structure...")
    code_entities = extract_code_entities()
    print(f"   Found {len(code_entities['entities'])} code entities")
    
    # Merge with existing
    print("\n🔗 Merging with GraphRAG entities...")
    GRAPHRAG_DIR.mkdir(parents=True, exist_ok=True)
    merged = merge_with_existing(code_entities)
    
    # Save
    ENTITIES_FILE.write_text(json.dumps(merged, indent=2))
    print(f"   Saved to {ENTITIES_FILE}")
    
    print("\n" + "=" * 60)
    print("✅ MU BRIDGE COMPLETE")
    print(f"   Code entities added: {len(code_entities['entities'])}")
    print(f"   Total entities: {len(merged['entities'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
