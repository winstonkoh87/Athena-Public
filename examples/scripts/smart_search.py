#!/usr/bin/env python3
"""
Smart Search (Shim → SDK) with Process-Level Timeout + Grep Fallback.

Delegates to `athena.tools.search`. If the search engine hangs
(e.g., Supabase cold start), the subprocess is killed after TIMEOUT_SECONDS
and a fast grep-based fallback runs automatically.

GTO Fix: 2026-03-26 — Resolves retrieval hang bottleneck.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# 45s (raised from 30 on 2026-07-23): a *cold* CLI invocation pays one-time costs
# — subprocess spawn, cold imports (supabase/google/onnxruntime), the first Gemini
# embedding, and the first Supabase connect — which can cross 30s and silently drop
# to the grep fallback even though the semantic core is healthy (verified: embedding
# ~2s, RPC ~1s, rerank ~1s once warm). Warm runs finish in a few seconds, so this
# ceiling only ever applies to the first cold call; a genuine hang still falls back,
# just 15s later.
TIMEOUT_SECONDS = 45
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Callers reach us as a bare `python3`, which may be an interpreter with none of
# the retrieval deps. Re-exec into a capable venv before importing anything that
# would quietly degrade. See _venv_bootstrap for why this beats editing callers.
sys.path.insert(0, str(Path(__file__).parent))
from _venv_bootstrap import ensure_deps  # noqa: E402

ensure_deps(PROJECT_ROOT)

# Paths for grep fallback
CANONICAL_PATH = PROJECT_ROOT / ".context" / "CANONICAL.md"
PROTOCOL_SUMMARIES_PATH = PROJECT_ROOT / ".context" / "PROTOCOL_SUMMARIES.md"
SESSION_LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
MEMORY_BANK_DIR = PROJECT_ROOT / ".context" / "memory_bank"


# Stopwords for keyword extraction
STOPWORDS = {"the", "and", "for", "is", "in", "to", "of", "a", "an", "on", "at", "by", "or", "not", "it", "be"}


def _extract_keywords(query: str) -> list[str]:
    """Split a multi-word query into individual searchable keywords."""
    return [w for w in query.split() if len(w) >= 2 and w.lower() not in STOPWORDS]


def run_grep_fallback(query: str, limit: int = 10) -> None:
    """Fast grep-based fallback when the full search engine is unavailable.
    
    Splits multi-word queries into individual keywords and greps for each,
    then merges and deduplicates results.
    """
    print(f"\n⚡ FAST FALLBACK: grep-based search for \"{query}\"", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    keywords = _extract_keywords(query)
    if not keywords:
        print("  (No searchable keywords extracted)", file=sys.stderr)
        return

    results = []
    seen = set()

    def _add_unique(tag: str, line: str):
        key = line.strip()[:80]
        if key not in seen:
            seen.add(key)
            results.append(f"[{tag}] {line.strip()}")

    # Build grep pattern: keyword1|keyword2|keyword3 (extended regex OR)
    grep_pattern = "|".join(keywords)

    # 1. Search CANONICAL.md
    if CANONICAL_PATH.exists():
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "10", grep_pattern, str(CANONICAL_PATH)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    # Score: count how many keywords hit this line
                    line_lower = line.lower()
                    hits = sum(1 for k in keywords if k.lower() in line_lower)
                    if hits >= min(2, len(keywords)):  # Require 2+ keyword overlap
                        _add_unique(f"CANONICAL({hits}/{len(keywords)})", line)
        except Exception:
            pass

    # 2. Search PROTOCOL_SUMMARIES.md
    if PROTOCOL_SUMMARIES_PATH.exists():
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "10", grep_pattern, str(PROTOCOL_SUMMARIES_PATH)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    line_lower = line.lower()
                    hits = sum(1 for k in keywords if k.lower() in line_lower)
                    if hits >= min(2, len(keywords)):
                        _add_unique(f"PROTOCOL({hits}/{len(keywords)})", line)
        except Exception:
            pass

    # 3. Search session log filenames (OR across keywords)
    if SESSION_LOGS_DIR.exists():
        for keyword in keywords[:3]:  # Limit to first 3 keywords for speed
            try:
                proc = subprocess.run(
                    ["find", str(SESSION_LOGS_DIR), "-iname", f"*{keyword.lower()}*",
                     "-type", "f"],
                    capture_output=True, text=True, timeout=3,
                )
                if proc.stdout:
                    for line in proc.stdout.strip().split("\n")[:3]:
                        if line.strip():
                            _add_unique("SESSION", Path(line).name)
            except Exception:
                pass

    # 3.5. Search session log CONTENT (last 200 files by mtime) — P3.3
    if SESSION_LOGS_DIR.exists():
        try:
            # Get most recent 200 session log files by modification time
            session_files = sorted(
                SESSION_LOGS_DIR.rglob("*.md"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )[:200]

            if session_files:
                # Build a file list for grep
                file_list = [str(f) for f in session_files]
                proc = subprocess.run(
                    ["grep", "-i", "-l", "-E", grep_pattern] + file_list,
                    capture_output=True, text=True, timeout=5,
                )
                if proc.stdout:
                    for line in proc.stdout.strip().split("\n")[:5]:
                        if line.strip():
                            matched_file = Path(line)
                            # Now get the matching line content
                            content_proc = subprocess.run(
                                ["grep", "-i", "-E", "-n", "-m", "3", grep_pattern, str(matched_file)],
                                capture_output=True, text=True, timeout=3,
                            )
                            if content_proc.stdout:
                                for content_line in content_proc.stdout.strip().split("\n")[:2]:
                                    _add_unique("SESSION-CONTENT", f"{matched_file.name}:{content_line[:150]}")
        except Exception:
            pass

    # 4. Search memory_bank files
    if MEMORY_BANK_DIR.exists():
        try:
            proc = subprocess.run(
                ["grep", "-rl", "-i", "-E", "-m", "5", grep_pattern, str(MEMORY_BANK_DIR)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    if line.strip():
                        _add_unique("MEMORY_BANK", Path(line).name)
        except Exception:
            pass

    # 5. Search case_studies directory
    case_studies_dir = PROJECT_ROOT / ".context" / "memories" / "case_studies"
    if case_studies_dir.exists():
        for keyword in keywords[:3]:
            try:
                proc = subprocess.run(
                    ["find", str(case_studies_dir), "-iname", f"*{keyword.lower()}*",
                     "-type", "f"],
                    capture_output=True, text=True, timeout=3,
                )
                if proc.stdout:
                    for line in proc.stdout.strip().split("\n")[:3]:
                        if line.strip():
                            _add_unique("CASE_STUDY", Path(line).name)
            except Exception:
                pass

    # Output results
    if results:
        print(f"\n🏆 FALLBACK RESULTS ({len(results[:limit])} matches):")
        for i, result in enumerate(results[:limit], 1):
            print(f"  {i}. {result}")
        print("-" * 60)
    else:
        print("  (No results found via grep fallback)", file=sys.stderr)


def _extract_date_from_filename(filename: str) -> str | None:
    """Extract YYYY-MM-DD from session log filenames.

    Supports both formats:
      - Legacy: 2026-04-15-session-S248.md
      - New:    S248_20260415_desc.md
    Returns the date string or None if unparseable.
    """
    import re

    # Legacy format: starts with YYYY-MM-DD
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1)

    # New format: SNNN_YYYYMMDD_...
    m = re.match(r"^S\d+_(\d{4})(\d{2})(\d{2})_", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    return None


def run_temporal_grep(query: str, as_of: str, limit: int = 10) -> None:
    """Bi-temporal read: grep session content only from files dated <= as_of.

    This is the lightweight 'what did I believe about X on date Y' surface.
    No database, no SQL — just a date filter on session log filenames + content grep.
    Files dated AFTER as_of are excluded, so you only see what existed at that point in time.

    Args:
        query: Search terms.
        as_of: YYYY-MM-DD cutoff date (inclusive).
        limit: Max results to show.
    """
    print(f"\n🧬 TEMPORAL SEARCH (as-of {as_of}): \"{query}\"", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if not SESSION_LOGS_DIR.exists():
        print("  (No session logs directory found)", file=sys.stderr)
        return

    keywords = _extract_keywords(query)
    if not keywords:
        print("  (No searchable keywords extracted)", file=sys.stderr)
        return

    # Collect session files dated on or before as_of
    eligible_files = []
    for f in sorted(SESSION_LOGS_DIR.rglob("*.md")):
        file_date = _extract_date_from_filename(f.name)
        if file_date and file_date <= as_of:
            eligible_files.append((file_date, f))

    if not eligible_files:
        print(f"  (No session logs found on or before {as_of})", file=sys.stderr)
        return

    # Sort by date descending (most recent within window first)
    eligible_files.sort(key=lambda x: x[0], reverse=True)

    grep_pattern = "|".join(keywords)
    results = []
    seen = set()

    for file_date, filepath in eligible_files:
        if len(results) >= limit:
            break
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "3", grep_pattern, str(filepath)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n")[:2]:
                    key = line.strip()[:80]
                    if key not in seen:
                        seen.add(key)
                        results.append(
                            f"[AS-OF {file_date}] {filepath.name}:{line.strip()[:150]}"
                        )
        except Exception:
            pass

    # Also search CANONICAL and decisionLog for the query (these are always in-window)
    for label, path in [("CANONICAL", CANONICAL_PATH),
                        ("DECISION_LOG", MEMORY_BANK_DIR / "decisionLog.md")]:
        if not path.exists() or len(results) >= limit:
            continue
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "5", grep_pattern, str(path)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n")[:3]:
                    line_lower = line.lower()
                    hits = sum(1 for k in keywords if k.lower() in line_lower)
                    if hits >= min(2, len(keywords)):
                        key = line.strip()[:80]
                        if key not in seen:
                            seen.add(key)
                            results.append(f"[{label}] {line.strip()[:150]}")
        except Exception:
            pass

    if results:
        print(f"\n🏆 TEMPORAL RESULTS ({len(results)} matches, window <= {as_of}):")
        for i, result in enumerate(results[:limit], 1):
            print(f"  {i}. {result}")
        print("-" * 60)
    else:
        print(f"  (No temporal matches for \"{query}\" on or before {as_of})", file=sys.stderr)


def run_full_search(query: str, limit: int, strict: bool, rerank: bool,
                    debug: bool, json_output: bool, include_personal: bool) -> None:
    """Run the full SDK search engine in a subprocess with a hard timeout."""
    # Build the command to run the SDK search directly
    src_path = str(PROJECT_ROOT / "src")
    cmd = [
        sys.executable, "-c",
        f"""
import sys
sys.path.insert(0, {src_path!r})
from athena.tools.search import run_search
run_search(
    query={query!r},
    limit={limit},
    strict={strict},
    rerank={rerank},
    debug={debug},
    json_output={json_output},
    include_personal={include_personal},
)
"""
    ]

    # Reranking normally uses the ONNX fast path (~0.4s load) and fits the default
    # budget. Only the torch CrossEncoder FALLBACK (ONNX assets missing) cold-loads
    # ~20-60s; give headroom only in that case.
    onnx_present = (PROJECT_ROOT / ".agent" / "models" / "reranker-onnx" / "tokenizer.json").exists()
    effective_timeout = max(TIMEOUT_SECONDS, 75) if (rerank and not onnx_present) else TIMEOUT_SECONDS

    try:
        proc = subprocess.run(
            cmd,
            timeout=effective_timeout,
            capture_output=False,  # Let stdout/stderr pass through
            env={**os.environ, "PYTHONPATH": src_path},
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Search exited with code {proc.returncode}")
    except subprocess.TimeoutExpired:
        print(
            f"\n⚠️  Full search timed out after {effective_timeout}s (usually a cold "
            "start — imports + first network call; warm runs complete in seconds). "
            "Falling back to grep...",
            file=sys.stderr,
        )
        run_grep_fallback(query, limit)
    except Exception as e:
        print(f"\n⚠️  Full search failed: {e}. Falling back to grep...", file=sys.stderr)
        run_grep_fallback(query, limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Smart Search (with timeout + fallback)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--strict", action="store_true", help="Suppress low-confidence results")
    # Rerank is DEFAULT-ON (2026-07-03): the ONNX fast path loads in ~0.4s, so the
    # old 20s torch cold-load rationale for opt-in no longer applies. --no-rerank
    # remains as the escape hatch; --rerank is kept as a no-op for compatibility.
    parser.add_argument("--rerank", dest="rerank", action="store_true", default=True,
                        help="Use Cross-Encoder reranking (default: on)")
    parser.add_argument("--no-rerank", dest="rerank", action="store_false",
                        help="Disable Cross-Encoder reranking")
    parser.add_argument("--debug", action="store_true", help="Show debug signals")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--include-personal", action="store_true",
        help="Include personal domain in results",
    )
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        metavar="YYYY-MM-DD",
        help="Temporal filter: only return session results dated on or before this date. "
             "Lightweight bi-temporal read — answers 'what did I believe about X on date Y' "
             "by filtering session logs to the as-of window.",
    )
    args = parser.parse_args()

    # Governance: Mark search as performed (best-effort)
    try:
        src_path = str(PROJECT_ROOT / "src")
        sys.path.insert(0, src_path)
        from athena.core.governance import get_governance
        get_governance().mark_search_performed(args.query)
    except Exception:
        pass  # Non-blocking

    run_full_search(
        query=args.query,
        limit=args.limit,
        strict=args.strict,
        rerank=args.rerank,
        debug=args.debug,
        json_output=args.json,
        include_personal=args.include_personal,
    )

    # If --as-of is specified, also run the temporal grep to surface
    # session-dated context from the as-of window
    if args.as_of:
        run_temporal_grep(args.query, args.as_of, args.limit)
