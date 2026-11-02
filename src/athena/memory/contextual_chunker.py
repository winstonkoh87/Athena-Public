"""
athena.memory.contextual_chunker
================================

Hierarchical AST Breadcrumb & Contextual Chunk Header Injection.

Resolves TD-052 ("Widen the semantic surface: revisit chunking") by parsing
Markdown heading hierarchy and prepending structured breadcrumb headers to
every chunk before embedding.  This ensures that chunks past index 0 retain
document provenance (title, parent headings) in vector space, eliminating the
"context amnesia" that causes retrieval misses on nested concepts.

Design constraints:
  - Zero external dependencies (pure stdlib regex).
  - Zero LLM API calls (deterministic heading parse, not generative summary).
  - Drop-in replacement for the naive chunk_text() in sync.py.
  - Graceful fallback: if the document has no headings, behaviour is identical
    to the old character-window chunker, just with the filename prepended.

Ticket: [T-20260919-01]
Retires: naive chunk_text() as the primary chunking path in sync.py.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Heading hierarchy tracker
# ---------------------------------------------------------------------------

# Matches Markdown ATX headings: # H1, ## H2, ### H3, etc.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_CLAIM_KIND_RE = re.compile(r"^claim_kind:\s*['\"]?([a-zA-Z0-9_\-]+)['\"]?", re.MULTILINE | re.IGNORECASE)
_STATUS_RE = re.compile(r"^status:\s*['\"]?([a-zA-Z0-9_\-]+)['\"]?", re.MULTILINE | re.IGNORECASE)


def extract_frontmatter_provenance(text: str) -> dict[str, str]:
    """Extract epistemic claim_kind and status provenance from Markdown frontmatter (TD-084)."""
    if not text.startswith("---"):
        return {}
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm_text = m.group(1)
    prov: dict[str, str] = {}
    kind_m = _CLAIM_KIND_RE.search(fm_text)
    if kind_m:
        prov["claim_kind"] = kind_m.group(1).lower().strip()
    status_m = _STATUS_RE.search(fm_text)
    if status_m:
        prov["status"] = status_m.group(1).lower().strip()
    return prov


def _build_breadcrumb(
    heading_stack: dict[int, str],
    filename: str,
    provenance: dict[str, str] | None = None,
) -> str:
    """Render the current heading stack and epistemic provenance as a breadcrumb string.

    Example output:
        [Doc: CS-453.md | Kind: design_proposal | Status: active | # The 6 Pillars > ## Generosity Asymmetry]
    """
    labels = [f"Doc: {filename}"]
    if provenance:
        if provenance.get("claim_kind"):
            labels.append(f"Kind: {provenance['claim_kind']}")
        if provenance.get("status"):
            labels.append(f"Status: {provenance['status']}")

    parts = []
    for level in sorted(heading_stack):
        text = heading_stack[level]
        parts.append(f"{'#' * level} {text}")

    if parts:
        labels.append(" > ".join(parts))

    return f"[{' | '.join(labels)}]\n\n"


# ---------------------------------------------------------------------------
# Structure-aware chunking
# ---------------------------------------------------------------------------

def _find_paragraph_break(text: str, target: int, window: int = 400) -> int:
    """Find the nearest paragraph break (double newline) near `target`.

    Searches within [target - window, target + window//2].  Falls back to a
    single newline, then to the exact target position.
    """
    search_start = max(0, target - window)
    search_end = min(len(text), target + window // 2)
    region = text[search_start:search_end]

    # Prefer double newline (paragraph break)
    best = region.rfind("\n\n", 0, target - search_start + window // 2)
    if best != -1:
        return search_start + best + 2  # +2 to skip past the "\n\n"

    # Fall back to single newline
    best = region.rfind("\n", 0, target - search_start + window // 2)
    if best != -1:
        return search_start + best + 1

    return target


def chunk_markdown_contextual(
    text: str,
    filename: str,
    chunk_size: int = 4000,
    overlap: int = 400,
) -> list[str]:
    """Split Markdown text into breadcrumb-enriched, overlapping chunks.

    Each chunk is prepended with a contextual header derived from the active
    heading hierarchy at that position in the document.  Chunk boundaries
    prefer paragraph breaks over arbitrary character positions.

    Parameters
    ----------
    text : str
        Full document content (may include YAML frontmatter).
    filename : str
        Basename of the source file (e.g. "CS-652-keith-leo.md").
    chunk_size : int
        Target chunk size in characters (breadcrumb header is excluded from
        the budget so downstream embedding sees full content).
    overlap : int
        Character overlap between consecutive chunks.

    Returns
    -------
    list[str]
        List of breadcrumb-prefixed chunk strings.
    """
    if not text or not text.strip():
        return []

    provenance = extract_frontmatter_provenance(text)

    # --- Step 1: Index all headings and their positions ----------------------
    headings: list[tuple[int, int, str]] = []  # (position, level, text)
    for m in _HEADING_RE.finditer(text):
        level = len(m.group(1))
        heading_text = m.group(2).strip()
        headings.append((m.start(), level, heading_text))

    # --- Step 2: Chunk with paragraph-aware boundaries -----------------------
    chunks: list[str] = []
    pos = 0
    text_len = len(text)

    while pos < text_len:
        # Determine raw end for this chunk
        raw_end = pos + chunk_size

        if raw_end >= text_len:
            # Last chunk — take everything remaining
            chunk_body = text[pos:]
        else:
            # Find a clean paragraph break near the target
            break_at = _find_paragraph_break(text, raw_end)
            # Don't let the break search push us backward past our start
            if break_at <= pos:
                break_at = raw_end
            chunk_body = text[pos:break_at]

        # --- Step 3: Compute the heading stack active at `pos` ---------------
        heading_stack: dict[int, str] = {}
        for h_pos, h_level, h_text in headings:
            if h_pos >= pos:
                break
            # When a heading at level N appears, it clears all sub-headings
            heading_stack[h_level] = h_text
            for deeper in list(heading_stack):
                if deeper > h_level:
                    del heading_stack[deeper]

        # Also pick up headings that START inside this chunk (for chunk 0
        # where the H1 title is at the very top)
        if not heading_stack:
            for h_pos, h_level, h_text in headings:
                if pos <= h_pos < pos + len(chunk_body):
                    heading_stack[h_level] = h_text
                    # Just grab the first heading to establish context
                    break

        breadcrumb = _build_breadcrumb(heading_stack, filename, provenance)
        chunks.append(breadcrumb + chunk_body)

        # Advance position (subtract overlap for continuity)
        chunk_end = pos + len(chunk_body)
        next_pos = chunk_end - overlap
        if next_pos <= pos:
            # Safety: always advance at least 1 char to avoid infinite loop
            next_pos = chunk_end
        pos = next_pos

    return chunks


# ---------------------------------------------------------------------------
# Convenience wrapper for sync.py integration
# ---------------------------------------------------------------------------

def contextual_chunk_text(
    text: str,
    filename: str = "unknown.md",
    chunk_size: int = 4000,
    overlap: int = 400,
) -> list[str]:
    """Drop-in replacement for sync.chunk_text with breadcrumb enrichment.

    This is the function sync.py should call instead of the old chunk_text().
    Signature is kept close to the original for minimal integration friction.
    """
    return chunk_markdown_contextual(text, filename, chunk_size, overlap)
