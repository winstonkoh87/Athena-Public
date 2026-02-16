#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict

# --- Configuration ---
# Dynamic workspace resolution
WORKSPACE_ROOT = str(Path(__file__).resolve().parent.parent.parent)
SCAN_DIRS = [
    ".agent/skills",
    ".context/memories",
    ".framework/v7.0",
    ".context/references"
]
EXCLUDE_DIRS = [
    ".git",
    "node_modules",
    ".DS_Store",
    "__pycache__"
]
# Regex to capture standard markdown links: [text](path)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def get_all_md_files(root_path: str, subdirs: List[str]) -> List[Path]:
    md_files = []
    for subdir in subdirs:
        search_path = Path(root_path) / subdir
        if not search_path.exists():
            print(f"⚠️  Warning: Directory not found: {search_path}")
            continue
        
        for root, _, files in os.walk(search_path):
            if any(exclude in root for exclude in EXCLUDE_DIRS):
                continue
            for file in files:
                if file.endswith(".md"):
                    md_files.append(Path(root) / file)
    return md_files

def resolve_path(source_file: Path, link_target: str) -> Path:
    """
    Resolves a link target to an absolute path.
    Handles 'file://...', absolute paths, and relative paths.
    """
    # Remove fragments (#...)
    link_target = link_target.split('#')[0]
    
    if link_target.startswith('file://'):
        return Path(link_target.replace('file://', ''))
    elif link_target.startswith('/'):
        return Path(link_target)
    else:
        # Relative path
        return (source_file.parent / link_target).resolve()

def build_graph(files: List[Path]) -> Tuple[Dict[Path, Set[Path]], Dict[Path, Set[Path]]]:
    """
    Returns:
        adjacency_list: Source -> Set of Targets (Outgoing)
        reverse_adjacency_list: Target -> Set of Sources (Incoming)
    """
    adj_list = defaultdict(set)
    rev_adj_list = defaultdict(set)
    
    # Initialize all files in graph to ensure orphans are tracked
    for f in files:
        adj_list[f] = set()
        rev_adj_list[f] = set()

    for file_path in files:
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        matches = LINK_PATTERN.findall(content)
        for _, link_target in matches:
            # Skip external links
            if link_target.startswith(('http', 'https', 'mailto')):
                continue
            
            resolved_target = resolve_path(file_path, link_target)
            
            # Check if target exists in our tracked files list (or at least exists on disk)
            # We filter for 'is this target inside our graph universe?'
            if resolved_target in adj_list: # This checks exact path match
                 adj_list[file_path].add(resolved_target)
                 rev_adj_list[resolved_target].add(file_path)
            # Try to handle potential path mismatches (symlinks, case sensitivity? usually not an issue on mac for logic but good to be strict)
            
    return adj_list, rev_adj_list

def analyze_graph(adj: Dict[Path, Set[Path]], rev_adj: Dict[Path, Set[Path]]):
    total_nodes = len(adj)
    orphans = [] # 0 in, 0 out
    sources = [] # 0 in, >0 out 
    sinks = []   # >0 in, 0 out
    
    for node in adj:
        out_degree = len(adj[node])
        in_degree = len(rev_adj[node])
        
        if out_degree == 0 and in_degree == 0:
            orphans.append(node)
        elif in_degree == 0:
            sources.append(node)
        elif out_degree == 0:
            sinks.append(node)
            
    print(f"\n📊 === KNOWLEDGE GRAPH AUDIT ===")
    print(f"Total Nodes: {total_nodes}")
    print(f"Disconnected Orphans (Priority Fix): {len(orphans)}")
    print(f"Sources (Roots/New Files): {len(sources)}")
    print(f"Sinks (Dead Ends): {len(sinks)}")
    
    print(f"\n🚫 === ORPHAN FILES (No Links In or Out) ===")
    for o in sorted(orphans):
        # Print relative to workspace root for readability
        try:
            rel_path = o.relative_to(WORKSPACE_ROOT)
            print(f"  - {rel_path}")
        except:
            print(f"  - {o}")

    print(f"\n🔗 === DENSITY STATS ===")
    total_edges = sum(len(targets) for targets in adj.values())
    avg_degree = total_edges / total_nodes if total_nodes > 0 else 0
    print(f"Total Connections: {total_edges}")
    print(f"Avg Connections per Node: {avg_degree:.2f}")

if __name__ == "__main__":
    print("🔍 Scanning workspace for knowledge graph connectivity...")
    files = get_all_md_files(WORKSPACE_ROOT, SCAN_DIRS)
    print(f"Found {len(files)} markdown files in target directories.")
    
    adj, rev = build_graph(files)
    analyze_graph(adj, rev)
