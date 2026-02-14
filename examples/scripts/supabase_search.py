#!/usr/bin/env python3
"""
Supabase Semantic Search for Project Athena
Search sessions and case studies by meaning using pgvector.
"""

import os
import json
import subprocess
import time
from lib.shared_utils import setup_paths, get_supabase_client, get_embedding

setup_paths()

from athena.core.governance import get_governance

# Client initialization
from supabase import Client

supabase = get_supabase_client()

from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GRAPHRAG_SCRIPT = PROJECT_ROOT / ".agent" / "scripts" / "query_graphrag.py"


def search_sessions(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search sessions by semantic similarity."""
    result = supabase.rpc(
        "search_sessions",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_case_studies(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search case studies by semantic similarity."""
    result = supabase.rpc(
        "search_case_studies",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_protocols(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search protocols by semantic similarity."""
    result = supabase.rpc(
        "search_protocols",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_capabilities(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search capabilities by semantic similarity."""
    result = supabase.rpc(
        "search_capabilities",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_playbooks(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search playbooks by semantic similarity."""
    result = supabase.rpc(
        "search_playbooks",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_references(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search references by semantic similarity."""
    result = supabase.rpc(
        "search_references",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_frameworks(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search frameworks by semantic similarity."""
    result = supabase.rpc(
        "search_frameworks",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_workflows(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search workflows by semantic similarity."""
    result = supabase.rpc(
        "search_workflows",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_entities(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 10,
    threshold: float = 0.3,
):
    """Search entities (Telegram export) by semantic similarity."""
    result = supabase.rpc(
        "search_entities",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_user_profile(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search user profile docs by semantic similarity."""
    result = supabase.rpc(
        "search_user_profile",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_system_docs(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search system docs by semantic similarity."""
    result = supabase.rpc(
        "search_system_docs",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def search_insights(
    supabase: Client,
    query_embedding: list[float],
    limit: int = 5,
    threshold: float = 0.3,
):
    """Search insights (analysis) by semantic similarity."""
    result = supabase.rpc(
        "search_insights",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


def collect_graphrag(query: str) -> list:
    """Collect GraphRAG results via subprocess invocation."""
    if not GRAPHRAG_SCRIPT.exists():
        return []

    try:
        # Run query_graphrag.py with --json flag
        # We also pass --expand to get more context
        cmd = ["python3", str(GRAPHRAG_SCRIPT), query, "--json", "--expand"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't throw error, handle returncode manually
        )

        if result.returncode != 0:
            # print(f"  ⚠️ GraphRAG Error: {result.stderr}")
            return []

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # print(f"  ⚠️ GraphRAG returned invalid JSON")
            return []

    except Exception as e:
        print(f"  ⚠️ GraphRAG invocation failed: {e}")
        return []


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Semantic search across Athena memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of results (default: 5)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Similarity threshold 0-1 (default: 0.3)",
    )
    parser.add_argument(
        "--sessions-only", action="store_true", help="Only search sessions"
    )
    parser.add_argument(
        "--cases-only", action="store_true", help="Only search case studies"
    )
    parser.add_argument(
        "--protocols-only", action="store_true", help="Only search protocols"
    )
    parser.add_argument(
        "--capabilities-only", action="store_true", help="Only search capabilities"
    )
    parser.add_argument(
        "--playbooks-only", action="store_true", help="Only search playbooks"
    )
    parser.add_argument(
        "--references-only", action="store_true", help="Only search references"
    )
    parser.add_argument(
        "--frameworks-only", action="store_true", help="Only search frameworks"
    )
    parser.add_argument(
        "--workflows-only", action="store_true", help="Only search workflows"
    )
    parser.add_argument(
        "--entities-only", action="store_true", help="Only search entities (JJ data)"
    )
    parser.add_argument(
        "--profile-only", action="store_true", help="Only search user profile"
    )
    parser.add_argument(
        "--system-only", action="store_true", help="Only search system docs"
    )
    parser.add_argument(
        "--insights-only", action="store_true", help="Only search insights (analysis)"
    )
    args = parser.parse_args()

    # Connect (Managed via lib.shared_utils)
    # supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f'\n🔍 Searching for: "{args.query}"')
    print("=" * 60)

    # Generate query embedding
    query_embedding = get_embedding(args.query)

    # Determine what to search based on flags
    has_specific = any(
        [
            args.sessions_only,
            args.cases_only,
            args.protocols_only,
            args.capabilities_only,
            args.playbooks_only,
            args.references_only,
            args.frameworks_only,
            args.workflows_only,
            args.entities_only,
            args.profile_only,
            args.system_only,
            args.insights_only,
        ]
    )
    search_all = not has_specific

    # ---------------------------------------------------------
    # PRIORITY 0: CANONICAL MEMORY (Protocol 215)
    # ---------------------------------------------------------
    if search_all or args.system_only:
        print("\n🏆 CANONICAL MEMORY (Protocol 215):")

        # Determine script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        canonical_path = os.path.join(repo_root, ".context", "CANONICAL.md")

        if os.path.exists(canonical_path):
            # Simple keyword extraction (same as TAG_INDEX logic)
            keywords = [
                w
                for w in args.query.split()
                if len(w) >= 2
                and w.lower()
                not in [
                    "the",
                    "and",
                    "for",
                    "was",
                    "with",
                    "what",
                    "how",
                    "when",
                    "who",
                    "does",
                    "is",
                ]
            ]

            if not keywords:
                keywords = args.query.split()

            matches = []
            try:
                with open(canonical_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # Case-insensitive check for ANY keyword
                        if any(k.lower() in line.lower() for k in keywords):
                            if (
                                "|" in line and "http" not in line
                            ):  # Optimize for table rows
                                matches.append((line_num, line.strip()))
                            elif "##" in line:  # Headers are good context
                                matches.append((line_num, line.strip()))

                if matches:
                    print(
                        f"  Found {len(matches)} matches in CANONICAL.md (The Truth):"
                    )
                    for i, (ln, content) in enumerate(matches[:5], 1):  # Limit to top 5
                        print(f"  {i}. Line {ln}: {content}")
                else:
                    print(f"  No direct matches in CANONICAL.md.")
            except Exception as e:
                print(f"  ⚠️ Error reading CANONICAL.md: {e}")
        else:
            print("  ⚠️ CANONICAL.md not found.")

    # Search sessions
    if search_all or args.sessions_only:
        print("\n📚 SESSIONS:")
        sessions = search_sessions(
            supabase, query_embedding, args.limit, args.threshold
        )
        if sessions:
            for i, s in enumerate(sessions, 1):
                similarity = s.get("similarity", 0)
                title = s.get("title", "Untitled")
                date = s.get("date", "Unknown")
                file_path = s.get("file_path", "")
                if "?chunk=" in file_path:
                    file_path = file_path.split("?chunk=")[0]
                print(f"  {i}. [{similarity:.2%}] {date} - {title}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching sessions found.")

    # Search case studies
    if search_all or args.cases_only:
        print("\n📖 CASE STUDIES:")
        cases = search_case_studies(
            supabase, query_embedding, args.limit, args.threshold
        )
        if cases:
            for i, c in enumerate(cases, 1):
                similarity = c.get("similarity", 0)
                code = c.get("code", "Unknown")
                title = c.get("title", "Untitled")
                file_path = c.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] {code} - {title}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching case studies found.")

    # Search protocols
    if search_all or args.protocols_only:
        print("\n📋 PROTOCOLS:")
        protocols = search_protocols(
            supabase, query_embedding, args.limit, args.threshold
        )
        if protocols:
            for i, p in enumerate(protocols, 1):
                similarity = p.get("similarity", 0)
                code = p.get("code", "Unknown")
                name = p.get("name", "")
                file_path = p.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] Protocol {code}: {name}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching protocols found.")

    # Search capabilities
    if search_all or args.capabilities_only:
        print("\n🔧 CAPABILITIES:")
        capabilities = search_capabilities(
            supabase, query_embedding, args.limit, args.threshold
        )
        if capabilities:
            for i, c in enumerate(capabilities, 1):
                similarity = c.get("similarity", 0)
                name = c.get("name", "Unknown")
                title = c.get("title", "")
                file_path = c.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] {name}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching capabilities found.")

    # Search playbooks
    if search_all or args.playbooks_only:
        print("\n📕 PLAYBOOKS:")
        playbooks = search_playbooks(
            supabase, query_embedding, args.limit, args.threshold
        )
        if playbooks:
            for i, p in enumerate(playbooks, 1):
                similarity = p.get("similarity", 0)
                name = p.get("name", "Unknown")
                title = p.get("title", "")
                file_path = p.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] {name}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching playbooks found.")

    # Search references
    if search_all or args.references_only:
        print("\n📚 REFERENCES:")
        references = search_references(
            supabase, query_embedding, args.limit, args.threshold
        )
        if references:
            for i, r in enumerate(references, 1):
                similarity = r.get("similarity", 0)
                name = r.get("name", "Unknown")
                title = r.get("title", "")
                file_path = r.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] {name}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching references found.")

    # Search frameworks
    if search_all or args.frameworks_only:
        print("\n🏗️ FRAMEWORKS:")
        frameworks = search_frameworks(
            supabase, query_embedding, args.limit, args.threshold
        )
        if frameworks:
            for i, f in enumerate(frameworks, 1):
                similarity = f.get("similarity", 0)
                name = f.get("name", "Unknown")
                title = f.get("title", "")
                file_path = f.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] {name}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching frameworks found.")

    # Search workflows
    if search_all or args.workflows_only:
        print("\n⚙️ WORKFLOWS:")
        workflows = search_workflows(
            supabase, query_embedding, args.limit, args.threshold
        )
        if workflows:
            for i, w in enumerate(workflows, 1):
                similarity = w.get("similarity", 0)
                name = w.get("name", "Unknown")
                description = w.get("description", "")
                file_path = w.get("file_path", "")
                print(f"  {i}. [{similarity:.2%}] /{name} - {description}")
                print(f"     📁 {file_path}")
        else:
            print("  No matching workflows found.")

    # Search entities (JJ behavioral data)
    if search_all or args.entities_only:
        print("\n💬 ENTITIES (JJ Data):")
        entities = search_entities(
            supabase, query_embedding, args.limit, args.threshold
        )
        if entities:
            for i, e in enumerate(entities, 1):
                similarity = e.get("similarity", 0)
                entity_name = e.get("entity_name", "Unknown")
                content = (
                    e.get("content", "")[:200] + "..."
                    if len(e.get("content", "")) > 200
                    else e.get("content", "")
                )
                print(f"  {i}. [{similarity:.2%}] {entity_name}")
                print(f"     💬 {content}")
        else:
            print("  No matching entities found.")

    # Search user profile
    if search_all or args.profile_only:
        print("\n👤 USER PROFILE:")
        profile = search_user_profile(
            supabase, query_embedding, args.limit, args.threshold
        )
        if profile:
            for i, p in enumerate(profile, 1):
                similarity = p.get("similarity", 0)
                filename = p.get("filename", "Unknown")
                title = p.get("title", "")
                category = p.get("category", "")
                print(f"  {i}. [{similarity:.2%}] {filename} ({category})")
                if title:
                    print(f"     📝 {title}")
        else:
            print("  No matching profile docs found.")

    # Search system docs
    if search_all or args.system_only:
        print("\n📄 SYSTEM DOCS:")
        system = search_system_docs(
            supabase, query_embedding, args.limit, args.threshold
        )
        if system:
            for i, s in enumerate(system, 1):
                similarity = s.get("similarity", 0)
                filename = s.get("filename", "Unknown")
                doc_type = s.get("doc_type", "")
                print(f"  {i}. [{similarity:.2%}] {filename} [{doc_type}]")
        else:
            print("  No matching system docs found.")

    # Search insights
    if search_all or args.insights_only:
        print("\n💡 INSIGHTS:")
        insights = search_insights(
            supabase, query_embedding, args.limit, args.threshold
        )
        if insights:
            for i, item in enumerate(insights, 1):
                similarity = item.get("similarity", 0)
                filename = item.get("filename", "Unknown")
                title = item.get("title", "")
                print(f"  {i}. [{similarity:.2%}] {filename}")
                if title:
                    print(f"     📝 {title}")
        else:
            print("  No matching insights found.")

    # ---------------------------------------------------------
    # PRIORITY 2: GraphRAG (Knowledge Graph)
    # ---------------------------------------------------------
    if search_all:
        print("\n🕸️ GRAPHRAG (Entities & Communities):")

        graphrag_results = collect_graphrag(args.query)

        if graphrag_results:
            # Filter and display by type
            communities = [r for r in graphrag_results if r.get("type") == "community"]
            entities = [r for r in graphrag_results if r.get("type") == "entity"]

            if communities:
                print(f"  [Communities]")
                for i, comm in enumerate(communities[:3], 1):
                    print(
                        f"  {i}. Community {comm.get('community_id', '?')} ({comm.get('size', 0)} members)"
                    )
                    print(f"     📄 {comm.get('summary', '')[:150]}...")

            if entities:
                print(f"  [Entities]")
                for i, ent in enumerate(entities[:5], 1):
                    preview = ent.get("description", "")[:100]
                    print(
                        f"  {i}. {ent.get('name', 'Unknown')} ({ent.get('entity_type', 'Entity')})"
                    )
                    print(f"     📄 {preview}")
                    if ent.get("neighbors"):
                        neighbor_names = [n["name"] for n in ent["neighbors"][:2]]
                        print(f"     🔗 {', '.join(neighbor_names)}")

        else:
            print("  No GraphRAG matches found.")

    # ---------------------------------------------------------
    # COMPULSORY TAG SEARCH (Dual-Path Protocol)
    # ---------------------------------------------------------
    if search_all:
        print("\n🏷️ TAG INDEX (Keyword Match):")
        try:
            # Locate TAG_INDEX.md
            # Try .context/TAG_INDEX.md relative to repo root
            # Script is in .agent/scripts, so root is ../../

            # Determine script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repo_root = os.path.dirname(os.path.dirname(script_dir))

            tag_index_path = os.path.join(repo_root, ".context", "TAG_INDEX.md")
            if not os.path.exists(tag_index_path):
                tag_index_path = os.path.join(
                    repo_root, "Athena-Public", "TAG_INDEX.md"
                )

            if os.path.exists(tag_index_path):
                # Simple keyword extraction (split by space)
                # Filter out short words to avoid noise (keep length >= 2 to catch acronyms like 'AI', 'SAF')
                keywords = [
                    w
                    for w in args.query.split()
                    if len(w) >= 2
                    and w.lower() not in ["the", "and", "for", "was", "with"]
                ]

                if not keywords:
                    # If query only has short words, use them all
                    keywords = args.query.split()

                matches = []
                with open(tag_index_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # Case-insensitive check for ANY keyword
                        if any(k.lower() in line.lower() for k in keywords):
                            if (
                                "|" in line and "http" not in line
                            ):  # Simple heuristic to identify table rows
                                matches.append((line_num, line.strip()))

                if matches:
                    # Limit to top 10 matches to avoid spamming
                    print(
                        f"  Found {len(matches)} matches in TAG_INDEX.md for keywords: {keywords}"
                    )
                    for i, (ln, content) in enumerate(matches[:10], 1):
                        print(f"  {i}. Line {ln}: {content[:150]}...")
                    if len(matches) > 10:
                        print(f"  ...and {len(matches) - 10} more.")
                else:
                    print(f"  No tag matches found for keywords: {keywords}")
            else:
                print("  ⚠️ TAG_INDEX.md not found.")
        except Exception as e:
            print(f"  ⚠️ SQL/Grep Error: {e}")

    # Register for Triple-Lock compliance
    get_governance().mark_search_performed(args.query)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
