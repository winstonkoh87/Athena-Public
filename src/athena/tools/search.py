"""
athena.tools.search
===================

Hybrid RAG Orchestrator (RRF + Rerank).
Integrates Canonical, Tags, Vectors, and Filesystem.
"""

import argparse
import contextlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from athena.core.cache import get_search_cache
from athena.core.config import (
    CANONICAL_PATH,
    PROJECT_ROOT,
    TAG_INDEX_AM_PATH,
    TAG_INDEX_NZ_PATH,
    TAG_INDEX_PATH,
)
from athena.core.models import SearchResult

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
# GTO Weight Calibration (2026-06-03 Opus Audit):
#   - capability raised 1.8→2.8: skills are authoritative, were drowning under sessions
#   - filename raised 2.0→2.5: exact filename hits should rank high for tool queries
#   - session lowered 3.0→2.5: supplementary context, not primary for tool/skill queries
#   - framework_docs kept 3.0: authoritative system documentation
WEIGHTS = {
    # S527 ranking recalibration: system_doc / framework / framework_docs are
    # ALREADY boot-loaded into context every session (Core_Identity, Output_Standards,
    # CANONICAL, activeContext, etc.). Retrieving them is wasted ranking budget and
    # crowds out the protocols/skills that are NOT already in context. Hard-lowered so
    # retrieval surfaces the non-boot corpus. Protocol/capability lifted to win.
    "case_study": 2.8,
    "session": 2.5,
    "protocol": 3.2,
    "system_doc": 1.2,
    "framework": 1.2,
    "framework_docs": 1.2,

    "user_profile": 2.5,
    "tags": 2.2,
    "canonical": 1.2,
    "filename": 2.5,
    "vector": 1.8,
    "capability": 3.2,
    "playbook": 1.8,
    "workflow": 2.0,
    "entity": 1.8,
    "reference": 1.8,
    "sqlite": 1.5,
    "web_search": 2.8,
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

# GraphRAG paths — REMOVED (GTO fix 2026-06-06: stale since Feb 2025, dead channel)

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
            # Use grep for speed — argument list prevents shell injection.
            # `--` stops flag parsing so a query beginning with `-` (e.g. "-v")
            # is treated as a pattern, not a grep option.
            process = subprocess.run(
                ["grep", "-i", "-m", "10", "--", query, str(path)],
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
    embedding: "list[float] | None" = None,
    exclude_domains: "list[str] | None" = None,
) -> "list[SearchResult]":
    """Collect semantic matches via Supabase using a unified database search."""
    if exclude_domains is None:
        exclude_domains = ["personal"]  # Default: exclude personal domain

    results = []
    try:
        from athena.memory.vectors import get_client, get_embedding

        query_embedding = embedding if embedding else get_embedding(query)

        # Call the unified database search function
        client = get_client()

        # Determine match threshold and limits
        threshold = 0.3
        match_count = limit * 2  # Fetch slightly more to account for filtering

        rpc_result = client.rpc(
            "search_all_vectors",
            {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": match_count,
            }
        ).execute()

        # The RPC returns source_table = document_chunks.table_name, which uses the
        # PLURAL Supabase table names ("sessions", "case_studies", ...). WEIGHTS keys
        # are singular type labels. Without this normalization every vector result
        # fell through to the default weight 1.0 and the per-type RRF calibration
        # (protocol 3.2, boot-doc demotion 1.2, ...) was silently inert.
        TABLE_TO_TYPE = {
            "sessions": "session",
            "protocols": "protocol",
            "case_studies": "case_study",
            "capabilities": "capability",
            "workflows": "workflow",
            "system_docs": "system_doc",
            "frameworks": "framework",
            "playbooks": "playbook",
            "references": "reference",
            "user_profile": "user_profile",
            "memory_bank": "system_doc",
            "insights": "case_study",
            "entities": "entity",
        }

        for item in rpc_result.data or []:
            raw_label = item.get("source_table", "unknown")
            type_label = TABLE_TO_TYPE.get(raw_label, raw_label)
            path = item.get("file_path", "")
            if "?" in path:
                path = path.split("?")[0]

            # Domain filtering: skip items from excluded domains
            item_domain = item.get("metadata", {}).get("domain", "technical") if item.get("metadata") else "technical"
            if item_domain in exclude_domains:
                continue

            chunk_idx = item.get("metadata", {}).get("chunk_index") if item.get("metadata") else None
            chunk_suffix = f" (Chunk {chunk_idx})" if chunk_idx is not None else ""

            # Dynamic Title/ID construction
            item_id = (
                item.get("title")
                or (item.get("metadata", {}).get("name") if item.get("metadata") else None)
                or (item.get("metadata", {}).get("code") if item.get("metadata") else None)
                or (item.get("metadata", {}).get("entity_name") if item.get("metadata") else None)
                or (item.get("metadata", {}).get("filename") if item.get("metadata") else None)
                or f"{type_label}"
            )
            # Chunk metadata often lacks code/name/date (enrichment lives on the
            # parent tables) — fall back to the file path so results never render
            # as "Protocol None: None" / "Session None:".
            path_stem = Path(path).stem if path else ""
            if type_label == "protocol":
                meta_d = item.get("metadata") or {}
                code = meta_d.get("code") or ""
                name = meta_d.get("name") or item.get("title") or path_stem
                item_id = f"Protocol {code}: {name}" if code else f"Protocol: {name}"
            elif type_label == "session":
                meta_d = item.get("metadata") or {}
                date_match = re.search(r"\d{4}-\d{2}-\d{2}", path_stem)
                date = meta_d.get("date") or (date_match.group(0) if date_match else "")
                item_id = f"Session {date}: {item.get('title') or path_stem}"
            elif type_label == "case_study":
                item_id = f"Case Study: {item.get('title') or path_stem}"

            item_id = f"{item_id}{chunk_suffix}"

            # Content extraction
            content = (
                item.get("content")
                or (item.get("metadata", {}).get("summary") if item.get("metadata") else None)
                or (item.get("metadata", {}).get("description") if item.get("metadata") else None)
                or ""
            )

            results.append(
                SearchResult(
                    id=item_id,
                    content=content,
                    source=type_label,
                    score=item.get("similarity", 0.0),
                    metadata={
                        "path": path,
                        "type": type_label,
                        "id": item.get("id"),
                        "code": item.get("metadata", {}).get("code") if item.get("metadata") else None,
                        "tags": (item.get("metadata", {}).get("tags") if item.get("metadata") else None) or [],
                        "chunk_index": chunk_idx,
                    },
                )
            )

    except Exception as e:
        print(f"   ⚠️ Unified vector search failed: {e}", file=sys.stderr)

    return results


# collect_graphrag REMOVED (GTO fix 2026-06-06)
# Rationale: GraphRAG stale since Feb 2025 (16 months). Dead channel carrying
# weight in the search pipeline. User explicitly requested removal.


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
                # Never surface archived/frozen content (S527 pollution guard).
                if "/archive" in line.replace("\\", "/"):
                    continue
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
            # Never surface archived/frozen content (S527 pollution guard).
            if "/archive" in str(md_file).replace("\\", "/"):
                continue
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

        # Also search root files directly in .context (non-recursively)
        context_dir = PROJECT_ROOT / ".context"
        if context_dir.exists():
            for md_file in context_dir.glob("*.md"):
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
                                id=f"ContextDoc: {md_file.name}",
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


def collect_web_search(query: str, limit: int = 5) -> list[SearchResult]:
    """Ground query using live Google/DuckDuckGo Web Search (RRF-fused channel)."""
    import html
    import re
    import urllib.parse
    results = []
    try:
        import requests
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code != 200:
            return []

        # Split by the result div tag to handle nested tags robustly
        blocks = r.text.split('<div class="result results_links results_links_deep web-result')
        for block in blocks[1:limit+1]:
            # Extract title
            title_match = re.search(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
            # Extract snippet
            snippet_match = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)
            # Extract URL
            url_match = re.search(r'class="result__url" href="(.*?)"', block, re.DOTALL)

            if title_match and snippet_match and url_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                # Clean up HTML entities
                title = html.unescape(title)
                snippet = html.unescape(snippet)

                # Extract target URL from DuckDuckGo redirect
                raw_url = url_match.group(1)
                parsed_url = urllib.parse.urlparse(raw_url)
                queries = urllib.parse.parse_qs(parsed_url.query)
                target_url = queries.get("uddg", [raw_url])[0]

                results.append(
                    SearchResult(
                        id=f"Web: {title}",
                        content=snippet,
                        source="web_search",
                        score=1.0 - (len(results) * 0.1),
                        metadata={"path": target_url},
                    )
                )
    except Exception:
        pass
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

            # GTO Temporal Decay Modifier (Recency Weighting):
            # Apply ONLY to time-series sources (session, case_study) with bounded path/id match.
            # Reference sources (protocol, capability, canonical, framework_docs, workflow) remain timeless (1.0x).
            temporal_mod = 1.0
            if source in {"session", "case_study"}:
                doc_path = doc.metadata.get("path", "") if doc.metadata else ""
                target_str = f"{doc_path} {doc.id}"
                if re.search(r"(?:^|[/_\-\s])2026(?:[/_\-.\s]|$)", target_str):
                    temporal_mod = 1.15
                elif re.search(r"(?:^|[/_\-\s])2025(?:[/_\-.\s]|$)", target_str):
                    temporal_mod = 0.90
                elif re.search(r"(?:^|[/_\-\s])2024(?:[/_\-.\s]|$)", target_str):
                    temporal_mod = 0.75

            contrib = weight * score_mod * temporal_mod * (1.0 / (k + rank))
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
    rerank: bool = True,  # default-on for programmatic/agent callers; crash-safe no-op if sentence_transformers unavailable
    debug: bool = False,
    json_output: bool = False,
    include_personal: bool = False,
    web: bool = False,
):
    import time
    t0 = time.time()

    # Define execution scope for strict cache isolation
    search_scope = {
        "limit": limit,
        "strict": strict,
        "rerank": rerank,
        "personal": include_personal,
        "web": web,
    }

    # 0. Check cache first
    cache = get_search_cache()
    cached_results = cache.get(query, scope=search_scope)

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
            import signal

            from athena.memory.vectors import get_embedding

            # Timeout wrapper for get_embedding (Supabase cold start issues)
            def handler(signum, frame):
                raise TimeoutError("Embedding fetch timed out")

            # Set the signal handler and a 15-second alarm (allows exponential backoff retries)
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(15)

            try:
                query_embedding = get_embedding(query)
            finally:
                signal.alarm(0)  # Disable alarm

            semantic_hit = cache.get_semantic(query_embedding, scope=search_scope)

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
                        f"   {DIM}Primary: TAG_INDEX & local channels active.{RESET}\n",
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

            # Live channels (2026-06-19): "tags" and "exocortex" retired — both were
            # dead on disk (TAG_INDEX moved to .context/archive/; exocortex.db absent).
            # Vector is the ONLY semantic channel; the rest are lexical. See TECH_DEBT.md.
            collection_tasks = {
                "canonical": lambda: collect_canonical(query),
                "vector": lambda: collect_vectors(
                    query, embedding=query_embedding, exclude_domains=exclude_domains
                ),
                "sqlite": lambda: collect_sqlite(query),
                "filename": lambda: collect_filenames(query),
                "framework_docs": lambda: collect_framework_docs(query),
            }
            if web:
                collection_tasks["web_search"] = lambda: collect_web_search(query, limit=limit)

            lists = {}
            with ThreadPoolExecutor(max_workers=len(collection_tasks)) as executor:
                # 1. Start all non-vector, non-web tasks in parallel
                future_to_source = {
                    executor.submit(safe_exec, source, func): source
                    for source, func in collection_tasks.items()
                    if source not in ["vector", "web_search"]
                }

                # 2. Wait for non-vector tasks to complete (local processes are very fast)
                done, not_done = wait(
                    future_to_source.keys(), timeout=3, return_when=ALL_COMPLETED
                )

                # Collect non-vector results
                for future in done:
                    source = future_to_source[future]
                    try:
                        lists[source] = future.result()
                    except Exception:
                        lists[source] = []

                # Report timeouts for non-vector tasks
                for future in not_done:
                    source = future_to_source[future]
                    if not json_output:
                        print(f"   ⚠️ {source} timed out (Tier 1 limit)", file=sys.stderr)

                # 3. Adaptive Router: Determine if we can bypass vectors
                word_count = len(query.split())
                is_low_entropy = word_count < 5 and not any(
                    x in query.lower()
                    for x in ["protocol", "session", "case study", "cs-"]
                )

                # Check if we have high-confidence local hits (score >= 0.8)
                has_local_hits = False
                for source in ["canonical", "sqlite", "filename", "framework_docs"]:
                    if any(doc.score >= 0.8 for doc in lists.get(source, [])):
                        has_local_hits = True
                        break

                needs_vector = True
                if is_low_entropy and has_local_hits:
                    needs_vector = False
                    if not json_output:
                        print("   ⚡ Low Entropy Query with Local Hits: Skipping deep vector retrieval")

                if needs_vector or ("web_search" in collection_tasks):
                    futures = {}
                    if needs_vector:
                        futures["vector"] = executor.submit(safe_exec, "vector", collection_tasks["vector"])
                    if "web_search" in collection_tasks:
                        futures["web_search"] = executor.submit(safe_exec, "web_search", collection_tasks["web_search"])

                    for source, fut in futures.items():
                        try:
                            timeout = 10 if GOD_MODE else 12
                            lists[source] = fut.result(timeout=timeout)
                        except Exception as e:
                            if not json_output:
                                print(f"   ⚠️ {source} timed out or failed: {e}", file=sys.stderr)
                            lists[source] = []

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
            # 50-candidate pool (was 25): the reranker can't rescue what fusion
            # buried below the cutoff; 50→top-k is the 2025-consensus shape.
            candidates = fused_results[:50]
            if not json_output:
                print(f"   ⚡ Reranking top {len(candidates)} candidates...")
            from athena.tools.reranker import rerank_results

            fused_results = rerank_results(query, candidates, top_k=limit)

        # Cache the result (Exact + Semantic) with explicit scope isolation
        if fused_results:
            if query_embedding:
                cache.set(
                    query,
                    fused_results,
                    embedding=query_embedding,
                    scope=search_scope,
                )
            else:
                cache.set(query, fused_results, scope=search_scope)

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
    else:
        # JSON output logic
        output = [doc.to_dict() for doc in fused_results[:limit]]
        print(json.dumps({"results": output, "suppressed": suppressed_count}))

    # Retrieval Telemetry — A7 Instrumentation (MCDA Rank #1)
    # Logs every search invocation to enable data-driven pruning.
    with contextlib.suppress(Exception):
        import datetime

        from athena.core.config import PROJECT_ROOT

        telemetry_dir = PROJECT_ROOT / ".agent" / "telemetry"
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        log_path = telemetry_dir / "retrieval_log.jsonl"

        top_results = fused_results[:limit]
        high_count = sum(1 for r in top_results if r.rrf_score >= CONFIDENCE_HIGH)
        med_count = sum(1 for r in top_results if CONFIDENCE_LOW <= r.rrf_score < CONFIDENCE_HIGH)
        low_count = sum(1 for r in top_results if r.rrf_score < CONFIDENCE_LOW)

        # Classify retrieval quality
        if high_count >= 3:
            quality = "hit"
        elif high_count >= 1 or med_count >= 3:
            quality = "partial"
        else:
            quality = "miss"

        # Source distribution — which retrieval channels contributed
        source_counts = defaultdict(int)
        for r in top_results:
            source_counts[r.source] += 1

        # Estimate tokens
        tokens = len(query.split())
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = len(encoding.encode(query))
        except Exception:
            pass

        latency_ms = int((time.time() - t0) * 1000)

        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "query": query,
            "limit": limit,
            "strict": strict,
            "rerank": rerank,
            "total_results": len(fused_results),
            "quality": quality,
            "confidence": {"high": high_count, "med": med_count, "low": low_count},
            "sources": dict(source_counts),
            "top_rrf": round(top_results[0].rrf_score, 5) if top_results else 0,
            "latency_ms": latency_ms,
            "tokens": tokens,
        }

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        # Also log to invocations.jsonl
        invocations_path = PROJECT_ROOT / ".athena" / "invocations.jsonl"
        invocations_path.parent.mkdir(parents=True, exist_ok=True)

        session_id = ""
        with contextlib.suppress(Exception):
            from athena.sessions import get_current_session_log
            log_file = get_current_session_log()
            if log_file:
                session_id = log_file.stem

        inv_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "type": "skill",
            "name": "smart_search",
            "trigger": "search tool call",
            "session_id": session_id,
            "tokens_in": tokens,
            "tokens_out": 0,
            "latency_ms": latency_ms,
            "user_reaction": "",
        }
        with open(invocations_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(inv_entry, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--rerank", dest="rerank", action="store_true", default=True,
                        help="Use Cross-Encoder reranking (default: on)")
    parser.add_argument("--no-rerank", dest="rerank", action="store_false")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--web", action="store_true", help="Enable live web search grounding channel")
    args = parser.parse_args()

    run_search(
        args.query,
        args.limit,
        args.strict,
        args.rerank,
        args.debug,
        args.json,
        web=args.web,
    )
