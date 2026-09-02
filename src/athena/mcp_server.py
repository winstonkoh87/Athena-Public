"""
athena.mcp_server
=================

MCP Tool Server for Project Athena.
Exposes core capabilities (search, quicksave, health, session) as
standardized MCP tools, consumable by any MCP-compatible client.

Transport: stdio (default), SSE (optional via --sse flag).

Usage:
    # stdio (for IDE integration like Antigravity / Claude Desktop)
    python -m athena.mcp_server

    # SSE (for remote / multi-client access)
    python -m athena.mcp_server --sse --port 8765
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env if present
current = Path(__file__).resolve()
project_root = None
for parent in current.parents:
    if (parent / "pyproject.toml").exists():
        project_root = parent
        break

if project_root:
    load_dotenv(project_root / ".env")
else:
    load_dotenv()

import json
import logging
import sys
from datetime import datetime

from fastmcp import FastMCP

from athena.core.permissions import (
    get_permissions,
)

# ---------------------------------------------------------------------------
# Server Init
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="athena",
    version="1.1.0",
    instructions=(
        "Project Athena MCP Server — a sovereign personal intelligence "
        "infrastructure. Use these tools to search memory, save checkpoints, "
        "check system health, and manage sessions.\n\n"
        "All tools are gated by the Permissioning Layer. Use permission_status "
        "to see what's accessible. Use set_secret_mode to toggle demo mode."
    ),
)

logger = logging.getLogger("athena.mcp")

# ---------------------------------------------------------------------------
# TOOL: smart_search
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "memory", "search"},
)
def smart_search(
    query: str,
    limit: int = 10,
    strict: bool = False,
    rerank: bool = True,  # default-on; Cross-Encoder rerank is crash-safe (no-op if sentence_transformers unavailable)
    web: bool | None = None,
) -> dict:
    """
    Search Athena's knowledge base using hybrid RAG (Canonical + Vectors +
    Filenames + Framework Docs + SQLite) with RRF fusion and ONNX reranker.

    Args:
        query: The search query string.
        limit: Maximum number of results to return (default 10).
        strict: If True, filter out low-confidence results.
        rerank: If True, apply Cross-Encoder reranking to top candidates.
        web: If True, enable live web search grounding. Default auto —
             live web grounding fires automatically for freshness-sensitive
             queries when set to None/False; pass True to force web.

    Returns:
        dict with 'results' (list of matches) and 'meta' (query info).
    """
    from athena.core.governance import get_governance
    from athena.tools.search import run_search

    # Permission gate
    perms = get_permissions()
    perms.gate("smart_search")

    # Governance: Mark search as performed
    get_governance().mark_search_performed(query)

    # Capture results via json_output mode
    import io

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        run_search(
            query=query,
            limit=limit,
            strict=strict,
            rerank=rerank,
            json_output=True,
            web=web,
        )
        output = buffer.getvalue()
    finally:
        sys.stdout = old_stdout

    # Parse the JSON output
    try:
        results = json.loads(output)
    except json.JSONDecodeError:
        results = {"raw_output": output}

    return {
        "results": results if isinstance(results, list) else results,
        "meta": {
            "query": query,
            "limit": limit,
            "strict": strict,
            "rerank": rerank,
            "web": web,
            "timestamp": datetime.now().isoformat(),
        },
    }


# ---------------------------------------------------------------------------
# TOOL: agentic_search (RAG v2)
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "memory", "search", "admin"},
)
def agentic_search(
    query: str,
    limit: int = 10,
    validate: bool = True,
    web: bool | None = None,
) -> dict:
    """
    Agentic RAG v2 — Multi-step query decomposition with parallel search
    and cosine validation. Use this for complex, multi-part queries.

    Pipeline: Decompose → Parallel Retrieve → Validate → Synthesize

    Args:
        query: Complex search query (e.g. "trading risk protocols and case studies").
        limit: Maximum number of results to return (default 10).
        validate: If True, validate results via cosine similarity against original query.
        web: If True, enable live web search grounding.

    Returns:
        dict with 'results', 'sub_queries', 'decomposed', and 'meta'.
    """
    from athena.tools.agentic_search import agentic_search as _agentic_search

    # Permission gate
    perms = get_permissions()
    perms.gate("agentic_search")

    result = _agentic_search(query=query, limit=limit, validate=validate, web=web)

    return {
        "results": [r.to_dict() for r in result["results"]],
        "sub_queries": result["sub_queries"],
        "decomposed": result["decomposed"],
        "meta": {
            **result["meta"],
            "web": web,
            "timestamp": datetime.now().isoformat(),
        },
    }


# ---------------------------------------------------------------------------
# TOOL: quicksave
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"write", "session", "checkpoint"},
)
def quicksave(
    summary: str,
    bullets: list[str] | None = None,
) -> dict:
    """
    Save a checkpoint to the current session log. Appends a timestamped
    block with a summary and optional bullet points.

    Args:
        summary: Brief description of what was accomplished/decided.
        bullets: Optional list of specific items to record.

    Returns:
        dict with 'status', 'log_file', and 'timestamp'.
    """
    from athena.core.governance import get_governance
    from athena.sessions import append_checkpoint

    # Permission gate
    perms = get_permissions()
    perms.gate("quicksave")

    # Governance: Check Triple-Lock compliance (canonical rule)
    gov = get_governance()
    lock_result = gov.evaluate_triple_lock()
    violation = None
    if not lock_result["compliant"]:
        violation = f"TRIPLE-LOCK VIOLATION: Missing: {', '.join(lock_result['missing'])}"

    gov.verify_exchange_integrity()  # Reset state

    try:
        log_path = append_checkpoint(summary, bullets)
        return {
            "status": "ok",
            "log_file": str(log_path),
            "timestamp": datetime.now().isoformat(),
            "governance": violation or "COMPLIANT",
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "error": str(e),
            "hint": "No active session. Run boot first.",
        }


# ---------------------------------------------------------------------------
# TOOL: health_check
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "system", "health"},
)
def health_check() -> dict:
    """
    Run a health audit of Athena's core services (Vector API, Database).

    Returns:
        dict with check results for each subsystem.
    """
    from athena.core.health import HealthCheck

    # Permission gate
    get_permissions().gate("health_check")

    vector = HealthCheck.check_vector_api()
    db = HealthCheck.check_database()

    return {
        "vector_api": vector,
        "database": db,
        "overall": "PASS" if (vector["status"] == "PASS" and db["status"] == "PASS") else "FAIL",
        "timestamp": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# TOOL: recall_session
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "session", "memory"},
)
def recall_session(lines: int = 50) -> dict:
    """
    Retrieve the most recent session log content.

    Args:
        lines: Number of lines from the end of the log to return (default 50).

    Returns:
        dict with session file path and recent content.
    """
    from athena.sessions import recall_last_session

    # Permission gate
    perms = get_permissions()
    perms.gate("recall_session")

    log_path = recall_last_session()

    if not log_path or not log_path.exists():
        return {
            "status": "error",
            "error": "No active session log found.",
        }

    content = log_path.read_text(encoding="utf-8")
    content_lines = content.splitlines()

    # Return the last N lines
    tail = content_lines[-lines:] if len(content_lines) > lines else content_lines
    tail_text = "\n".join(tail)

    # Redact if in secret mode
    if perms.secret_mode:
        tail_text = perms.redact(tail_text)

    return {
        "status": "ok",
        "session_file": str(log_path),
        "session_id": log_path.stem,
        "total_lines": len(content_lines),
        "content": tail_text,
    }


# ---------------------------------------------------------------------------
# TOOL: governance_status
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "system", "governance"},
)
def governance_status() -> dict:
    """
    Check the current Triple-Lock governance state. Shows whether semantic
    search and web search have been performed in the current exchange.

    Returns:
        dict with governance state and integrity score.
    """
    from athena.core.governance import get_governance

    # Permission gate
    get_permissions().gate("governance_status")

    gov = get_governance()
    state = gov._state.copy()

    return {
        "semantic_search_performed": state.get("semantic_search_performed", False),
        "web_search_performed": state.get("web_search_performed", False),
        "integrity_score": gov.get_integrity_score(),
        "compliant": state.get("semantic_search_performed", False)
        and state.get("web_search_performed", False),
        "timestamp": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# TOOL: list_memory_paths
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "system", "config"},
)
def list_memory_paths() -> dict:
    """
    List all active memory directories that Athena searches over.
    Useful for understanding what knowledge domains are indexed.

    Returns:
        dict with core and extended memory paths.
    """
    from athena.core.config import (
        CORE_DIRS,
        EXTENDED_DIRS,
        get_active_memory_paths,
    )

    # Permission gate
    get_permissions().gate("list_memory_paths")

    core = {k: str(v) for k, v in CORE_DIRS.items()}
    extended = [{"path": str(p), "maps_to": t} for p, t in EXTENDED_DIRS]
    active = [str(p) for p in get_active_memory_paths()]

    return {
        "core_directories": core,
        "extended_directories": extended,
        "active_count": len(active),
    }


# ---------------------------------------------------------------------------
# RESOURCE: session_log (current)
# ---------------------------------------------------------------------------


@mcp.resource(
    uri="athena://session/current",
    name="Current Session Log",
    description="The full content of the active session log file.",
)
def current_session_resource() -> str:
    """Return the full current session log as a resource."""
    from athena.sessions import recall_last_session

    perms = get_permissions()
    perms.gate("recall_session")

    log_path = recall_last_session()
    if not log_path or not log_path.exists():
        return "No active session."

    content = log_path.read_text(encoding="utf-8")
    if perms.secret_mode:
        content = perms.redact(content)
    return content


# ---------------------------------------------------------------------------
# RESOURCE: canonical memory
# ---------------------------------------------------------------------------


@mcp.resource(
    uri="athena://memory/canonical",
    name="Canonical Memory",
    description="The Canonical Memory (CANONICAL.md) — Athena's constitution.",
)
def canonical_memory_resource() -> str:
    """Return the Canonical Memory content."""
    from athena.core.config import CANONICAL_PATH

    perms = get_permissions()
    perms.gate("smart_search")

    if not CANONICAL_PATH.exists():
        return "CANONICAL.md not found."

    content = CANONICAL_PATH.read_text(encoding="utf-8")

    # Redact in secret mode
    if perms.secret_mode:
        content = perms.redact(content)

    return content


# ---------------------------------------------------------------------------
# TOOL: set_secret_mode
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"admin", "security", "mode"},
)
def set_secret_mode(enabled: bool) -> dict:
    """
    Toggle Secret Mode (demo/external mode). When active, only PUBLIC
    tools are accessible and sensitive content is redacted.

    Args:
        enabled: True to activate secret mode, False to deactivate.

    Returns:
        dict with mode state and list of blocked tools.
    """
    perms = get_permissions()
    perms.gate("set_secret_mode")
    return perms.set_secret_mode(enabled)


# ---------------------------------------------------------------------------
# TOOL: meta_awareness_check
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "system", "governance"},
)
def meta_awareness_check(prompt: str) -> dict:
    """
    Code-enforced meta-awareness classification. Call on user prompt.

    Args:
        prompt: User prompt string to evaluate.

    Returns:
        dict with fired classes and optional system-reminder injection.
    """
    from athena.core.gate_meta import REMINDER_TEMPLATE, classify

    # Carried over from the duplicate definition this replaced: that one gated
    # on permissions, this one did not, and it silently won because it was
    # defined later in the file. Dropping the gate would have been a governance
    # regression nobody asked for.
    get_permissions().gate("meta_awareness_check")

    fired = classify(prompt)
    if not fired:
        return {"fired": [], "injection": None}

    return {
        "fired": fired,
        "injection": REMINDER_TEMPLATE.format(classes=", ".join(fired)),
        "telemetry_path": ".athena/invocations.jsonl",
    }


# ---------------------------------------------------------------------------
# TOOL: permission_status
# ---------------------------------------------------------------------------



@mcp.tool(
    tags={"read", "system", "security"},
)
def permission_status() -> dict:
    """
    Show the current permission state: caller level, secret mode,
    accessible/blocked tools, and tool manifest.

    Returns:
        dict with full permission state and tool manifest.
    """
    perms = get_permissions()
    perms.gate("permission_status")
    status = perms.get_status()
    status["manifest"] = perms.get_tool_manifest()
    return status


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

@mcp.tool(
    tags={"governance", "compliance"},
)
def report_external_web_search(
    query: str,
) -> dict:
    """Report that external web research was performed (e.g., via IDE's native
    search_web tool). This marks the web leg of the Triple-Lock as satisfied
    so that quicksave governance reports COMPLIANT.

    Use this when the client IDE performed web search using its own tools
    rather than Athena's built-in web channel.

    Args:
        query: The query that was searched on the web.

    Returns:
        dict with confirmation and timestamp.
    """
    import json

    from athena.core.config import PROJECT_ROOT
    from athena.core.governance import get_governance

    perms = get_permissions()
    perms.gate("report_external_web_search")

    gov = get_governance()
    gov.mark_web_search_performed(query)

    # Log to invocations.jsonl
    invocations_path = PROJECT_ROOT / ".athena" / "invocations.jsonl"
    try:
        invocations_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "web_search_external",
            "query": query[:200],  # Truncate for privacy
        }
        with open(invocations_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Best effort logging

    return {
        "status": "ok",
        "message": "Web research marked for Triple-Lock compliance.",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool(
    tags={"governance", "classification"},
)
def classify_turn(
    query: str,
) -> dict:
    """Classify a user query's risk level and determine if web search is needed.

    This is a deterministic classifier (no LLM). Call at the start of each turn
    to set the appropriate risk level for governance. This makes SNIPER/ULTRA
    modes reachable — without this call, everything defaults to STANDARD.

    Args:
        query: The user's query text.

    Returns:
        dict with risk_level, web_required, intent, and reason.
    """
    from athena.core.governance import RiskLevel, get_governance
    from athena.tools.search import classify_query_intent

    perms = get_permissions()
    perms.gate("classify_turn")

    intent = classify_query_intent(query)
    gov = get_governance()

    # Determine web requirement and frame detection
    web_required = False
    web_reason = "none"
    underspec_opt = False
    try:
        from athena.tools.web_triggers import is_underspecified_optimization, needs_web
        web_required, web_reason = needs_web(query, intent)
        underspec_opt = is_underspecified_optimization(query)
    except ImportError:
        # web_triggers not yet available — fall back to intent-based rule
        web_required = intent == "GENERAL"  # Conservative default
        web_reason = "fallback_intent"

    # Classify risk level
    query_lower = query.lower().strip()
    word_count = len(query_lower.split())

    # SNIPER: Short, simple, low-stakes queries
    # underspec_opt questions are NEVER sniper — they need the frame directive
    sniper_signals = (
        word_count <= 5
        and intent == "SYSTEM_KNOWLEDGE"
        and not web_required
        and not underspec_opt
    )

    # ULTRA: Complex, multi-part, high-stakes queries
    ultra_signals = (
        word_count > 20
        or any(marker in query_lower for marker in [
            "analyze", "analyse", "deep dive", "comprehensive",
            "compare", "evaluate", "strategy", "trade",
            "should i", "what are the implications",
            "risk", "ruin", "circuit breaker",
        ])
        or (intent == "PERSONALISED_DECISION" and web_required)
    )

    if sniper_signals:
        risk_level = RiskLevel.SNIPER
    elif ultra_signals:
        risk_level = RiskLevel.ULTRA
        web_required = True  # ULTRA always requires web
        if web_reason == "none":
            web_reason = "ultra_tier"
    else:
        risk_level = RiskLevel.STANDARD

    # Set the governance risk level (this is what makes SNIPER/ULTRA reachable)
    gov.set_risk_level(risk_level)

    return {
        "risk_level": risk_level.name,
        "web_required": web_required,
        "web_reason": web_reason,
        "underspec_opt": underspec_opt,
        "intent": intent,
        "query_words": word_count,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool(
    tags={"read", "memory", "governance", "context"},
)
def context_gate(
    query: str,
    limit: int = 10,
    web: bool | None = None,
) -> dict:
    """Pre-answer context assembly gate. Call this BEFORE answering any
    STANDARD/ULTRA query. Returns the complete retrieval bundle including
    local results, web grounding (when needed), personalisation frame,
    user state, and a machine-authored directive for the answering model.

    This is the single tool that satisfies Law #6 (Risk-Proportional
    Triple-Lock) in one call. It runs smart_search with auto-web,
    builds the personalisation frame when relevant, and returns
    governance compliance state.

    Args:
        query: The user's query text.
        limit: Maximum number of context results (default 10).
        web: Force web search on/off. None = auto (recommended).

    Returns:
        dict with context bundle, web metadata, governance state,
        missing requirements, and a directive for the answering model.
    """
    import io
    import json as _json

    from athena.core.governance import RiskLevel, get_governance
    from athena.tools.search import classify_query_intent, run_search

    perms = get_permissions()
    perms.gate("context_gate")

    # 1. Classify intent and set risk level
    intent = classify_query_intent(query)
    gov = get_governance()

    # Determine risk level
    # Determine risk level and frame detection
    web_required = False
    web_reason = "none"
    underspec_opt = False
    try:
        from athena.tools.web_triggers import is_underspecified_optimization, needs_web
        web_required, web_reason = needs_web(query, intent)
        underspec_opt = is_underspecified_optimization(query)
    except ImportError:
        pass

    query_lower = query.lower().strip()
    word_count = len(query_lower.split())

    sniper_signals = (
        word_count <= 5
        and intent == "SYSTEM_KNOWLEDGE"
        and not web_required
        and not underspec_opt
    )
    ultra_signals = (
        word_count > 20
        or any(m in query_lower for m in [
            "analyze", "analyse", "deep dive", "comprehensive",
            "compare", "evaluate", "strategy", "trade",
            "should i", "what are the implications",
            "risk", "ruin", "circuit breaker",
        ])
        or (intent == "PERSONALISED_DECISION" and web_required)
    )

    if sniper_signals:
        risk_level = RiskLevel.SNIPER
    elif ultra_signals:
        risk_level = RiskLevel.ULTRA
        web_required = True
        if web_reason == "none":
            web_reason = "ultra_tier"
    else:
        risk_level = RiskLevel.STANDARD

    gov.set_risk_level(risk_level)

    # 2. Determine effective web setting
    effective_web = web if web is not None else web_required

    # 3. Run search (captures JSON output)
    gov.mark_search_performed(query)  # Mark semantic leg

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        run_search(
            query,
            limit=limit,
            json_output=True,
            include_personal=True,
            web=effective_web,
            intent=intent,
        )
    finally:
        sys.stdout = old_stdout

    raw_output = buffer.getvalue().strip()

    # Parse search results
    search_results = {}
    try:
        search_results = _json.loads(raw_output)
    except (ValueError, _json.JSONDecodeError):
        search_results = {"results": [], "error": "Failed to parse search output"}

    # 4. Build personalisation frame (when relevant)
    personalisation = None
    user_state = None
    if intent == "PERSONALISED_DECISION":
        try:
            from athena.tools.personalisation import (
                build_personalisation_prompt,
                build_user_state_snapshot,
            )
            personalisation = build_personalisation_prompt(query)
            user_state = build_user_state_snapshot()
        except Exception:
            pass

    # 5. Check for strong local hit
    local_first = False
    results_list = search_results.get("results", [])
    if isinstance(results_list, list) and results_list:
        top_result = results_list[0] if results_list else {}
        top_score = top_result.get("rrf_score", 0) if isinstance(top_result, dict) else 0
        if top_score >= 0.8:
            local_first = True

    # 6. Determine missing requirements
    missing = []
    if risk_level == RiskLevel.ULTRA and not effective_web and web_required:
        missing.append("web")

    # 7. Build directive
    directive_parts = []
    if effective_web and any(
        isinstance(r, dict) and r.get("source") == "web_search"
        for r in (results_list if isinstance(results_list, list) else [])
    ):
        web_results = [
            r for r in results_list
            if isinstance(r, dict) and r.get("source") == "web_search"
        ]
        if web_results:
            fetched_at = ""
            for wr in web_results:
                meta = wr.get("metadata", {})
                if isinstance(meta, dict):
                    fetched_at = meta.get("fetched_at", "")
                    if fetched_at:
                        break
            if fetched_at:
                directive_parts.append(
                    f"Web results fetched at {fetched_at}. Cite fetched_at in answer; "
                    "re-verify if the answer pivots on a time-sensitive fact."
                )

    if local_first:
        directive_parts.append(
            "Strong local hit found. Prefer local knowledge; web supplements."
        )

    if missing:
        directive_parts.append(
            f"Missing requirements: {', '.join(missing)}. Satisfy before answering."
        )

    # Frame directive: underspecified optimization (DEC-180 / Nudge Test)
    if underspec_opt:
        directive_parts.append(
            "FRAME DIRECTIVE: Underspecified optimization detected (objective function "
            "undefined). Do NOT solve for a single scalar answer. First decouple "
            "Expected Value invariance from Utility Profiles (Sharpe/Arbitrage vs "
            "Recreational Comfort vs Tournament Skewness), present the level "
            "hierarchy, and hand the choice back to the user (DEC-180)."
        )

    if not directive_parts:
        directive_parts.append("Context bundle assembled. Proceed with answer.")

    directive = " ".join(directive_parts)

    # 8. Web metadata
    web_meta = {
        "fired": effective_web,
        "required": web_required,
        "reason": web_reason,
        "count": len([
            r for r in (results_list if isinstance(results_list, list) else [])
            if isinstance(r, dict) and r.get("source") == "web_search"
        ]),
    }

    # Add provider info if available
    for r in (results_list if isinstance(results_list, list) else []):
        if isinstance(r, dict) and r.get("source") == "web_search":
            meta = r.get("metadata", {})
            if isinstance(meta, dict) and "provider" in meta:
                web_meta["provider"] = meta["provider"]
                break

    return {
        "context": search_results,
        "personalisation": personalisation,
        "user_state": user_state,
        "web": web_meta,
        "local_first": local_first,
        "missing": missing,
        "underspec_opt": underspec_opt,
        "directive": directive,
        "risk_level": risk_level.name,
        "intent": intent,
        "timestamp": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Athena MCP Server")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--port", type=int, default=8765, help="SSE port")
    args = parser.parse_args()

    if args.sse:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")
