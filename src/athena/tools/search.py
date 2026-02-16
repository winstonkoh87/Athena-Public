"""
athena.tools.search
===================

Hybrid RAG Orchestrator (RRF + Rerank).
Integrates Canonical, Tags, Vectors, and Filesystem.
"""

import argparse
import contextlib
import json
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from athena.core.config import (
    PROJECT_ROOT,
    TAG_INDEX_PATH,
    TAG_INDEX_AM_PATH,
    TAG_INDEX_NZ_PATH,
    CANONICAL_PATH,
)
from athena.core.models import SearchResult
from athena.core.cache import get_search_cache
# Lazy imports to speed up CLI startup
# from athena.memory.vectors import ... (Moved inside functions)
# from athena.tools.reranker import ... (Moved inside functions)

# ANSI Colors
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# God Mode: Aggressive latency optimization
GOD_MODE = True

# Config
# NOTE: Vector subtypes (case_study, session, protocol, etc.) each get their own
# weight so RRF applies them correctly.
WEIGHTS = {
    "case_study": 3.0,
    "session": 3.0,
    "protocol": 2.8,
    "graphrag": 2.5,
    "user_profile": 2.5,
    "framework_docs": 2.5,
    "framework": 2.3,
    "tags": 2.2,
    "canonical": 2.0,
    "filename": 2.0,
    "vector": 1.8,
    "capability": 1.8,
    "playbook": 1.8,
    "workflow": 1.8,
    "entity": 1.8,
    "reference": 1.8,
    "system_doc": 1.8,
    "sqlite": 1.5,
    "exocortex": 1.5,
}
RRF_K = 60
CONFIDENCE_HIGH = 0.03
CONFIDENCE_MED = 0.02
CONFIDENCE_LOW = 0.01

# Filter config: Items that should be de-prioritized or hidden
SKIP_PATHS = [
    "node_modules/",
    ".git/",
    "athena-public/docs/libraries/",
    "README.md",
]

# GraphRAG paths
GRAPHRAG_DIR = PROJECT_ROOT / ".agent" / "graphrag"
COMMUNITIES_FILE = GRAPHRAG_DIR / "communities.json"
GRAPH_FILE = GRAPHRAG_DIR / "knowledge_graph.gpickle"
CHROMA_DIR = PROJECT_ROOT / ".agent" / "chroma_db"

# --- Collection Functions ---


def collect_canonical(query: str) -> list[SearchResult]:
    """Collect matches from CANONICAL.md — requires 2+ keyword hits per line."""
    results = []
    if not CANONICAL_PATH.exists():
        return []

    stopwords = {
        "the",
        "and",
        "for",
        "is",
        "in",
        "to",
        "of",
        "a",
        "an",
        "on",
        "at",
        "by",
        "or",
        "not",
    }
    keywords = [w for w in query.split() if len(w) >= 2 and w.lower() not in stopwords]
    if not keywords:
        return []

    try:
        text = CANONICAL_PATH.read_text(encoding="utf-8")
        for line_num, line in enumerate(text.splitlines(), 1):
            line_lower = line.lower()
            # Require 2+ keyword matches to reduce noise
            hits = sum(1 for k in keywords if k.lower() in line_lower)
            if hits < min(2, len(keywords)):
                continue

            # Score based on keyword density
            density = hits / len(keywords)

            if "|" in line and "http" not in line:
                results.append(
                    SearchResult(
                        id=f"Canonical:L{line_num}",
                        content=line.strip(),
                        source="canonical",
                        score=density,  # Was 1.0 flat — now reflects match quality
                    )
                )
            elif "##" in line:
                results.append(
                    SearchResult(
                        id=f"Canonical:Header:L{line_num}",
                        content=line.strip(),
                        source="canonical",
                        score=density * 0.9,
                    )
                )
    except Exception:
        pass
    # Sort by score and limit to 3 (was 5 — reducing Canonical dominance)
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:3]


def collect_tags(query: str) -> list[SearchResult]:
    """Collect exact tag matches from sharded indexes."""
    results = []
    index_paths = [TAG_INDEX_AM_PATH, TAG_INDEX_NZ_PATH]

    # Fallback to legacy if shards don't exist
    if not any(p.exists() for p in index_paths) and TAG_INDEX_PATH.exists():
        index_paths = [TAG_INDEX_PATH]

    for path in index_paths:
        if not path.exists():
            continue

        try:
            # Use grep for speed — argument list prevents shell injection
            process = subprocess.run(
                ["grep", "-i", "-m", "10", query, str(path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if process.stdout:
                lines = process.stdout.strip().split("\n")
                for i, line in enumerate(lines):
                    results.append(
                        SearchResult(
                            id=f"Tag:{line.split('|')[0].strip() if '|' in line else query}",
                            content=line.strip(),
                            source="tags",
                            score=1.0 - (i * 0.05),
                        )
                    )
        except Exception:
            pass
    return results


def collect_vectors(
    query: str,
    limit: int = 20,
    embedding: list[float] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[SearchResult]:
    """Collect semantic matches via Supabase"""
    if exclude_domains is None:
        exclude_domains = ["personal"]  # Default: exclude personal domain

    results = []
    try:
        from athena.memory.vectors import (
            get_embedding,
            get_client,
            search_sessions,
            search_case_studies,
            search_protocols,
            search_capabilities,
            search_playbooks,
            search_references,
            search_frameworks,
            search_workflows,
            search_entities,
            search_user_profile,
            search_system_docs,
        )

        query_embedding = embedding if embedding else get_embedding(query)

        # God Mode Limits
        high_limit = 10
        mid_limit = 5 if not GOD_MODE else 3
        low_limit = 5 if not GOD_MODE else 3

        # Parallel search using ThreadPoolExecutor
        search_tasks = [
            ("protocol", search_protocols, high_limit, 0.3),
            ("case_study", search_case_studies, high_limit, 0.3),
            ("session", search_sessions, mid_limit, 0.35),
            ("capability", search_capabilities, low_limit, 0.3),
            ("playbook", search_playbooks, low_limit, 0.3),
            ("workflow", search_workflows, low_limit, 0.3),
            ("entity", search_entities, low_limit, 0.3),
            ("reference", search_references, low_limit, 0.3),
            ("framework", search_frameworks, low_limit, 0.3),
            ("user_profile", search_user_profile, low_limit, 0.3),
            ("system_doc", search_system_docs, low_limit, 0.3),
        ]

        def run_task(task):
            type_label, func, limit, threshold = task
            try:
                # Ensure thread-local client is retrieved within the worker thread
                worker_client = get_client()
                return type_label, func(
                    worker_client, query_embedding, limit=limit, threshold=threshold
                )
            except Exception as e:
                print(f"   ⚠️ Search failed for {type_label}: {e}", file=sys.stderr)
                return type_label, []

        with ThreadPoolExecutor(max_workers=len(search_tasks)) as executor:
            task_results = list(executor.map(run_task, search_tasks))

        for type_label, raw_results in task_results:
            for item in raw_results or []:
                path = item.get("file_path", "")
                if "?" in path:
                    path = path.split("?")[0]

                # Domain filtering: skip items from excluded domains
                item_domain = item.get("domain", "technical")
                if item_domain in exclude_domains:
                    continue

                # Dynamic Title/ID construction
                item_id = (
                    item.get("title")
                    or item.get("name")
                    or item.get("code")
                    or item.get("entity_name")
                    or item.get("filename")
                    or f"{type_label}"
                )
                if type_label == "protocol":
                    item_id = f"Protocol {item.get('code')}: {item.get('name')}"
                elif type_label == "session":
                    item_id = f"Session {item.get('date')}: {item.get('title')}"
                elif type_label == "case_study":
                    item_id = f"Case Study: {item.get('title')}"

                # Path filtering (SKIP_PATHS)
                if any(sp in path for sp in SKIP_PATHS):
                    continue

                results.append(
                    SearchResult(
                        id=item_id,
                        content=item.get("content", "")[:200],
                        source=type_label,  # Use actual type for correct RRF weighting
                        score=item.get("similarity", 0),
                        metadata={
                            "type": type_label,
                            "path": path,
                            "domain": item_domain,
                        },
                    )
                )

    except Exception as e:
        print(f"Vector search warning: {e}", file=sys.stderr)

    return results


def collect_graphrag(query: str, limit: int = 5) -> list[SearchResult]:
    """Collect entity and community matches via query_graphrag.py subprocess."""
    results = []

    # Path to query script
    script_path = PROJECT_ROOT / ".agent" / "scripts" / "query_graphrag.py"
    if not script_path.exists():
        return []

    try:
        # Run query_graphrag.py with --json flag
        # Optimization: Use --global-only to skip slow model loading
        cmd = ["python3", str(script_path), query, "--json", "--global-only"]

        # Add strict timeout
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=5
        )

        if result.returncode != 0:
            return []

        data = json.loads(result.stdout)

        for item in data:
            # Skip vectors (handled by collect_vectors via Supabase/Chroma)
            if item.get("type") == "vector":
                continue

            # Handle Communities
            if item.get("type") == "community":
                comm_id = item.get("community_id", "?")
                size = item.get("size", 0)
                summary = item.get("summary", "")
                members = item.get("members", [])

                content = f"Community {comm_id} ({size} members): {summary[:200]}..."
                if members:
                    content += f"\nMembers: {', '.join(str(m) for m in members[:5])}..."

                results.append(
                    SearchResult(
                        id=f"Graph:Community:{comm_id}",
                        content=content,
                        source="graphrag",
                        score=item.get("score", 0) / 10.0,  # Normalize rough score
                        metadata={"type": "community", "id": comm_id},
                    )
                )

            # Handle Entities
            elif item.get("type") == "entity":
                name = item.get("name", "Unknown")
                desc = item.get("description", "")
                neighbors = item.get("neighbors", [])

                content = f"Entity: {name} ({item.get('entity_type', 'Entity')})\n{desc[:200]}"
                if neighbors:
                    neighbor_names = [n["name"] for n in neighbors[:3]]
                    content += f"\nConnected to: {', '.join(neighbor_names)}"

                results.append(
                    SearchResult(
                        id=f"Graph:Entity:{name}",
                        content=content,
                        source="graphrag",
                        score=min(item.get("score", 0), 1.0),
                        metadata={"type": "entity", "name": name},
                    )
                )

    except Exception as e:
        print(f"GraphRAG search warning: {e}", file=sys.stderr)

    return results[:limit]


def collect_filenames(query: str) -> list[SearchResult]:
    """Collect filename matches in Project Root — splits query into keyword tokens."""
    results = []
    stopwords = {"the", "and", "for", "is", "in", "to", "of", "a", "an"}
    keywords = [w for w in query.split() if len(w) >= 2 and w.lower() not in stopwords]
    if not keywords:
        return []

    seen_paths = set()
    try:
        # Optimization: Single find command with OR logic for all keywords
        # find . -path X -prune -o -type f \( -iname *k1* -o -iname *k2* \) -print
        cmd = [
            "find",
            ".",
            "-path",
            "./node_modules",
            "-prune",
            "-o",
            "-path",
            "./.git",
            "-prune",
            "-o",
            "-path",
            "./Athena-Public",
            "-prune",
            "-o",
            "-path",
            "./.context/knowledge",  # Skip large binary/db dumps if present
            "-prune",
            "-o",
            "-type",
            "f",
            "(",
        ]

        # Add keywords with OR logic
        for i, keyword in enumerate(keywords):
            if i > 0:
                cmd.append("-o")
            cmd.extend(["-iname", f"*{keyword}*"])

        cmd.extend([")", "-print"])

        process = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=3,  # Slightly increased for the heavier single query
        )

        if process.stdout:
            lines = process.stdout.strip().split("\n")[
                :20
            ]  # Take a few more candidates, filter later
            for line in lines:
                if line.strip() and line not in seen_paths:
                    seen_paths.add(line)
                    full_path = PROJECT_ROOT / line
                    # Score by how many query keywords appear in the filename
                    fname_lower = full_path.name.lower()
                    keyword_hits = sum(1 for k in keywords if k.lower() in fname_lower)
                    results.append(
                        SearchResult(
                            id=f"File: {full_path.name}",
                            content=f"Path: {line}",
                            source="filename",
                            score=keyword_hits / len(keywords),
                            metadata={"path": str(full_path)},
                        )
                    )
    except Exception:
        pass

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:10]


def collect_framework_docs(query: str) -> list[SearchResult]:
    """Search .framework/ directory content for matches — surfaces identity/system docs."""
    results = []
    framework_dir = PROJECT_ROOT / ".framework"
    if not framework_dir.exists():
        return []

    stopwords = {"the", "and", "for", "is", "in", "to", "of", "a", "an", "or", "not"}
    keywords = [w for w in query.split() if len(w) >= 2 and w.lower() not in stopwords]
    if not keywords:
        return []

    try:
        # Use grep -rl to find files containing any keyword, then score by density
        for md_file in framework_dir.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")[:5000]  # First 5k chars
                text_lower = text.lower()
                hits = sum(1 for k in keywords if k.lower() in text_lower)
                if hits >= min(2, len(keywords)):
                    # Find the best matching line for the snippet
                    best_line = ""
                    best_score = 0
                    for line in text.splitlines():
                        line_lower = line.lower()
                        line_hits = sum(1 for k in keywords if k.lower() in line_lower)
                        if line_hits > best_score:
                            best_score = line_hits
                            best_line = line.strip()

                    density = hits / len(keywords)
                    rel_path = md_file.relative_to(PROJECT_ROOT)
                    results.append(
                        SearchResult(
                            id=f"Framework: {md_file.name}",
                            content=best_line[:200] if best_line else text[:200],
                            source="framework_docs",
                            score=min(density, 1.0),
                            metadata={"path": str(rel_path)},
                        )
                    )
            except Exception:
                pass

        # Also search memory_bank files
        memory_bank_dir = PROJECT_ROOT / ".context" / "memory_bank"
        if memory_bank_dir.exists():
            for md_file in memory_bank_dir.rglob("*.md"):
                try:
                    text = md_file.read_text(encoding="utf-8")[:3000]
                    text_lower = text.lower()
                    hits = sum(1 for k in keywords if k.lower() in text_lower)
                    if hits >= min(2, len(keywords)):
                        best_line = ""
                        best_score = 0
                        for line in text.splitlines():
                            line_lower = line.lower()
                            line_hits = sum(
                                1 for k in keywords if k.lower() in line_lower
                            )
                            if line_hits > best_score:
                                best_score = line_hits
                                best_line = line.strip()

                        density = hits / len(keywords)
                        results.append(
                            SearchResult(
                                id=f"MemoryBank: {md_file.name}",
                                content=best_line[:200] if best_line else text[:200],
                                source="framework_docs",
                                score=min(density, 1.0),
                                metadata={
                                    "path": str(md_file.relative_to(PROJECT_ROOT))
                                },
                            )
                        )
                except Exception:
                    pass

    except Exception:
        pass

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:5]


def collect_sqlite(query: str, limit: int = 10) -> list[SearchResult]:
    """Sovereign Fallback: Search the local SQLite index (athena.db)."""
    import sqlite3
    from athena.core.config import INPUTS_DIR

    db_path = INPUTS_DIR / "athena.db"
    if not db_path.exists():
        return []

    results = []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Keyword search on tags and filenames
        query_sanitized = f"%{query}%"

        # 1. Search Files by Path/Name
        cursor.execute(
            "SELECT path FROM files WHERE path LIKE ? LIMIT ?", (query_sanitized, limit)
        )
        for row in cursor.fetchall():
            filepath = Path(row["path"])
            results.append(
                SearchResult(
                    id=f"Local:File:{filepath.name}",
                    content=f"Local match: {filepath.name}",
                    source="sqlite",
                    score=0.8,
                    metadata={"path": str(filepath)},
                )
            )

        # 2. Search by Tags
        cursor.execute(
            """
            SELECT f.path, t.name 
            FROM files f
            JOIN file_tags ft ON f.path = ft.file_path
            JOIN tags t ON ft.tag_id = t.id
            WHERE t.name LIKE ?
            LIMIT ?
        """,
            (query_sanitized, limit),
        )

        for row in cursor.fetchall():
            filepath = Path(row["path"])
            results.append(
                SearchResult(
                    id=f"Local:Tag:{row['name']}:{filepath.name}",
                    content=f"Tag match: #{row['name']}",
                    source="sqlite",
                    score=0.9,
                    metadata={"path": str(filepath)},
                )
            )

        conn.close()
    except Exception as e:
        print(f"   ⚠️ SQLite fallback failed: {e}", file=sys.stderr)

    return results


def collect_exocortex(query: str, limit: int = 5) -> list[SearchResult]:
    """Search the Exocortex (Wikipedia Abstracts) via SQLite FTS5."""
    import sqlite3

    # Hardcoded path to standard location
    db_path = PROJECT_ROOT / ".context" / "knowledge" / "exocortex.db"

    if not db_path.exists():
        return []

    results = []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Sanitize term for FTS5
        # Tokenize and wrap in quotes to prevent column syntax interpretation (e.g. 1:1)
        # "trend" "continuation" "1:1"
        tokens = [f'"{token.replace('"', '""')}"' for token in query.split()]
        clean_query = " ".join(tokens)

        # FTS query syntax
        sql = "SELECT title, abstract, url FROM abstracts WHERE title MATCH ? OR abstract MATCH ? ORDER BY rank LIMIT ?"

        cursor.execute(sql, (clean_query, clean_query, limit))

        for row in cursor.fetchall():
            results.append(
                SearchResult(
                    id=f"Exocortex:{row['title']}",
                    content=f"{row['abstract'][:300]}...",
                    source="exocortex",
                    score=1.0,  # FTS rank is internal, we normalize flat here
                    metadata={"url": row["url"]},
                )
            )

        conn.close()
    except Exception as e:
        print(f"   ⚠️ Exocortex search failed: {e}", file=sys.stderr)

    return results


# --- Fusion Logic ---


def weighted_rrf(
    ranked_lists: dict[str, list[SearchResult]], k: int = 60
) -> list[SearchResult]:
    fused_scores = defaultdict(float)
    doc_map = {}
    doc_signals = defaultdict(dict)

    for source, docs in ranked_lists.items():
        weight = WEIGHTS.get(source, 1.0)
        for rank, doc in enumerate(docs, start=1):
            score_mod = 0.5 + doc.score  # Dynamic: range 0.5 to 1.5
            contrib = weight * score_mod * (1.0 / (k + rank))
            fused_scores[doc.id] += contrib

            if doc.id not in doc_map:
                doc_map[doc.id] = doc

            doc_signals[doc.id][source] = {"rank": rank, "contrib": round(contrib, 5)}

    final_list = []
    for doc_id, score in fused_scores.items():
        doc = doc_map[doc_id]
        doc.rrf_score = score
        doc.signals = doc_signals[doc_id]
        final_list.append(doc)

    return sorted(final_list, key=lambda x: x.rrf_score, reverse=True)


# --- Main Entry Point ---


def run_search(
    query: str,
    limit: int = 10,
    strict: bool = False,
    rerank: bool = False,
    debug: bool = False,
    json_output: bool = False,
    include_personal: bool = False,
):
    # 0. Check cache first
    cache = get_search_cache()
    cache_key = f"{query}|{limit}|{strict}|{rerank}"
    cached_results = cache.get(cache_key)

    if cached_results is not None:
        if not json_output:
            print(f'\n⚡ CACHE HIT: "{query}"')
            print("=" * 60)
        fused_results = cached_results
    else:
        # 0.5. Check Semantic Cache (if miss on exact)
        query_embedding = None
        if not json_output:
            print("   ⚡ Checking semantic cache...")

        try:
            # We need the embedding for semantic check
            # This corresponds to "Step 2: Fetch embedding" in the plan
            from athena.memory.vectors import get_embedding
            import signal

            # Timeout wrapper for get_embedding (Supabase cold start issues)
            def handler(signum, frame):
                raise TimeoutError("Embedding fetch timed out")

            # Set the signal handler and a 3-second alarm
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(3)

            try:
                query_embedding = get_embedding(query)
            finally:
                signal.alarm(0)  # Disable alarm

            semantic_hit = cache.get_semantic(query_embedding)

            if semantic_hit:
                if not json_output:
                    print(f'🔥 SEMANTIC CACHE HIT: "{query}"')
                    print("=" * 60)
                fused_results = semantic_hit
                # Proceed to display (skip collection)
                pass
            else:
                raise ValueError("Semantic Miss")
        except Exception as e:
            # Embedding failed or semantic miss - continue with hybrid search
            # Make embedding optional for non-vector search methods
            if "404" in str(e) or "GOOGLE_API_KEY" in str(e) or "timed out" in str(e):
                if not json_output:
                    print(
                        f"\n   {YELLOW}⚠️  FALLBACK: Vector search unavailable ({e}){RESET}",
                        file=sys.stderr,
                    )
                    print(
                        f"   {DIM}Primary: TAG_INDEX & GraphRAG active.{RESET}\n",
                        file=sys.stderr,
                    )
                query_embedding = None  # Proceed without vectors

            # Fallback to full search
            if not json_output:
                print(
                    f'\n🔍 SMART SEARCH (Parallel Hybrid RRF{" + Rerank" if rerank else ""}): "{query}"'
                )
                print("=" * 60)

            # 1. Collect (Parallel execution)
            # Wrapper for robust execution

            # 1. Collect (Parallel execution)
            exclude_domains = [] if include_personal else ["personal"]

            # Helper to create safe lambdas
            def safe_exec(name, func):
                try:
                    return func()
                except Exception as e:
                    print(f"   ⚠️ {name} task failed: {e}", file=sys.stderr)
                    return []

            collection_tasks = {
                "canonical": lambda: collect_canonical(query),
                "tags": lambda: collect_tags(query),
                "graphrag": lambda: collect_graphrag(query),
                "vector": lambda: collect_vectors(
                    query, embedding=query_embedding, exclude_domains=exclude_domains
                ),
                "sqlite": lambda: collect_sqlite(query),
                "filename": lambda: collect_filenames(query),
                "framework_docs": lambda: collect_framework_docs(query),
                "exocortex": lambda: collect_exocortex(query),
            }

            lists = {}
            with ThreadPoolExecutor(max_workers=len(collection_tasks)) as executor:
                future_to_source = {
                    executor.submit(safe_exec, source, func): source
                    for source, func in collection_tasks.items()
                    if source != "vector"  # Defer vector launch
                }

                # Adaptive Latency: Entropy Check
                # If query is short (< 5 words) and generic, skip vectors
                word_count = len(query.split())
                is_low_entropy = word_count < 5 and not any(
                    x in query.lower()
                    for x in ["protocol", "session", "case study", "cs-"]
                )

                if is_low_entropy and not include_personal:
                    if not json_output:
                        print(
                            f"   ⚡ Low Entropy Query: Skipping deep retrieval (Vectors bypassed)"
                        )
                else:
                    # Launch vector search
                    future_to_source[
                        executor.submit(safe_exec, "vector", collection_tasks["vector"])
                    ] = "vector"

                # God Mode Timeout
                timeout = 8 if not GOD_MODE else 5

                # Wait for ALL to finish (or timeout)
                done, not_done = wait(
                    future_to_source.keys(), timeout=timeout, return_when=ALL_COMPLETED
                )

                # Collect finished results
                for future in done:
                    source = future_to_source[future]
                    try:
                        lists[source] = future.result()
                    except Exception:
                        lists[source] = []

                # Report timeouts
                for future in not_done:
                    source = future_to_source[future]
                    if not json_output:
                        print(
                            f"   ⚠️ {source} timed out (Tier 2 limit)", file=sys.stderr
                        )
                    # We simply don't add it to lists, effectively skipping it
                    # Ensure we cancel if possible (though Python threads can't be killed)
                    future.cancel()

            # 2. Fuse
            # Split vector results by their type-specific source for correct
            # per-type RRF weighting (e.g., case_study=3.0, session=3.0, protocol=2.8)
            vector_items = lists.pop("vector", [])
            for item in vector_items:
                type_key = item.source  # e.g., "case_study", "session", "protocol"
                if type_key not in lists:
                    lists[type_key] = []
                lists[type_key].append(item)

            fused_results = weighted_rrf(lists)

        # 3. Rerank
        if rerank and fused_results:
            candidates = fused_results[:25]
            if not json_output:
                print(f"   ⚡ Reranking top {len(candidates)} candidates...")
            from athena.tools.reranker import rerank_results

            fused_results = rerank_results(query, candidates, top_k=limit)

        # Cache the result (Exact + Semantic)
        if fused_results and query_embedding:
            cache.set(query, fused_results, embedding=query_embedding)

        # Store in cache for next time
        cache.set(cache_key, fused_results)

    # 4. Filter
    if strict:
        high_conf = [r for r in fused_results if r.rrf_score >= CONFIDENCE_MED]
        low_conf = [r for r in fused_results if r.rrf_score < CONFIDENCE_MED]
        suppressed_count = len(low_conf)
        fused_results = high_conf
        if not json_output and suppressed_count > 0:
            print(
                f"\n   🛡️ STRICT MODE: {suppressed_count} low-confidence result(s) suppressed"
            )
    else:
        suppressed_count = 0

    if not json_output and fused_results:
        print("\n<athena_grounding>")

    # 5. Present
    if not fused_results:
        if json_output:
            print(
                json.dumps(
                    {
                        "results": [],
                        "suppressed": suppressed_count,
                        "message": "No high-confidence results",
                    }
                )
            )
        else:
            print(
                "  (No high-confidence results found)"
                if strict
                else "  (No results found)"
            )
        return

    if not json_output:
        print(f"\n🏆 TOP {limit} RESULTS:")
        for i, doc in enumerate(fused_results[:limit], 1):
            if doc.rrf_score >= CONFIDENCE_HIGH:
                conf_badge = "[HIGH]"
            elif doc.rrf_score >= CONFIDENCE_MED:
                conf_badge = "[MED]"
            else:
                conf_badge = "[LOW]"

            score_display = (
                f"Rerank:{doc.signals.get('reranker', {}).get('score', 0):.2f}"
                if rerank
                else f"RRF:{doc.rrf_score:.4f}"
            )
            print(f"\n  {i}. {conf_badge} [{score_display}] {doc.id}")

            if debug:
                print(f"     Signals: {json.dumps(doc.signals)}")

            if doc.metadata.get("path"):
                print(f"     📁 {doc.metadata['path']}")
            else:
                print(f"     📄 {doc.content[:100]}...")

        print("-" * 60)
        print("</athena_grounding>\n")

        # Log (Optional compliance hook)
        with contextlib.suppress(Exception):
            # Assuming logging logic will be migrated later or importable
            pass
    else:
        # JSON output logic
        output = [doc.to_dict() for doc in fused_results[:limit]]
        print(json.dumps({"results": output, "suppressed": suppressed_count}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    run_search(args.query, args.limit, args.strict, args.rerank, args.debug, args.json)
