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
from datetime import datetime, timezone

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

    # Execute search directly without stdout hijacking (WS3.1 / M-1 fix)
    results = run_search(
        query=query,
        limit=limit,
        strict=strict,
        rerank=rerank,
        json_output=True,
        web=web,
        print_output=False,
    )
    if not isinstance(results, dict):
        results = {"results": [], "error": "Search returned invalid payload"}

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

    result = _agentic_search(query=query, limit=limit, validate=validate, web=web or False)

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
    from athena.tools.web_providers import get_web_health
    web_health = get_web_health()

    return {
        "vector_api": vector,
        "database": db,
        "web_search": web_health,
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


# ---------------------------------------------------------------------------
# TOOL: search_web
# ---------------------------------------------------------------------------


@mcp.tool(
    tags={"read", "search", "web"},
)
def search_web(
    query: str,
    limit: int = 5,
) -> dict:
    """Execute live web search via Athena's resilient multi-provider failover chain
    (Serper -> Brave -> DuckDuckGo). Returns structured results and explicit
    tri-state grounding_status (ok, degraded, tool_error).

    Use this whenever you need fresh, external facts or when IDE-native web search
    is unavailable or fails.

    Args:
        query: Search query string.
        limit: Maximum results to return (default 5).

    Returns:
        dict with 'results', 'metadata' (provider, errors, fetched_at),
        'grounding_status' ('ok' | 'degraded' | 'tool_error'), and 'directive'.
    """
    import json

    from athena.core.config import PROJECT_ROOT
    from athena.core.governance import get_governance
    from athena.tools.web_providers import web_search as provider_web_search

    perms = get_permissions()
    perms.gate("search_web")

    results_raw, meta = provider_web_search(query, limit=limit)
    status = meta.get("grounding_status", "ok" if results_raw else "tool_error")

    gov = get_governance()
    if status != "tool_error":
        gov.mark_web_search_performed(query)

    # Log to invocations.jsonl
    invocations_path = PROJECT_ROOT / ".athena" / "invocations.jsonl"
    try:
        invocations_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "web_search",
            "query": query[:200],
            "grounding_status": status,
            "provider": meta.get("provider", "none"),
            "result_count": len(results_raw),
        }
        with open(invocations_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    directive = None
    if status == "tool_error":
        directive = (
            "CIRCUIT BREAKER (P514): All web search providers failed (tool_error). "
            "Do NOT assert facts or universal-negative claims ('does not exist', 'never made') "
            "from internal model weights alone. Either cite the search failure and state "
            "epistemic uncertainty, use alternate tools (e.g. read_url_content), or ask the user."
        )
    elif status == "degraded":
        directive = (
            f"Note: Web search ran on fallback provider '{meta.get('provider')}'. "
            "Verify critical facts if answer hinges on high-stakes details."
        )

    results_data = [
        {
            "title": r.title,
            "snippet": r.snippet,
            "url": r.url,
            "fetched_at": r.fetched_at,
            "provider": r.provider,
            "position": r.position,
        }
        for r in results_raw
    ]

    return {
        "results": results_data,
        "metadata": meta,
        "grounding_status": status,
        "directive": directive,
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

    # Classify risk level via deterministic lambda_scorer (Phase C1)
    from athena.core.lambda_scorer import compute_lambda
    lambda_res = compute_lambda(
        query,
        intent=intent,
        web_required=web_required,
        underspec_opt=underspec_opt,
    )
    risk_level = lambda_res["risk_level"]
    is_crisis = lambda_res.get("is_crisis", False)
    crisis_referral = lambda_res.get("crisis_referral")

    if is_crisis:
        # Protocol 509 hard stop: bypass web search, do not escalate cognitive loops
        web_required = False
        web_reason = "crisis_gate_hard_stop"
    elif risk_level == RiskLevel.ULTRA:
        web_required = True
        if web_reason == "none":
            web_reason = "ultra_tier"

    # Set the governance risk level (this is what makes SNIPER/ULTRA reachable)
    gov.set_risk_level(risk_level)

    return {
        "risk_level": risk_level.name,
        "lambda_score": lambda_res["score"],
        "lambda_features": lambda_res["features"],
        "is_crisis": is_crisis,
        "crisis_referral": crisis_referral,
        "web_required": web_required,
        "web_reason": web_reason,
        "underspec_opt": underspec_opt,
        "intent": intent,
        "query_words": len(query.strip().split()),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool(
    tags={"governance", "reasoning", "cluster15"},
)
def frame_open(frame_json: str, session: str = "", lock: bool = False) -> dict:
    """Pre-register a problem frame BEFORE solving (RSN-504 Gate 5b).

    Frames are validated against the machine-checkable R1-R10 contract and the
    value-of-information stop rule. A frame that cannot be falsified, has no
    rival hypothesis, no numeric exit criteria, no kill criteria, no baseline
    counterfactual, or no justification for spending framing time is REJECTED
    and never recorded.

    Args:
        frame_json: JSON object of the frame. Required keys: literal_request,
            candidate_reframe, hypotheses (>=2, priors summing to 1.0, each with
            a falsifier), discriminating_test, success_criteria (metric +
            threshold with a number + by-date), review_date, kill_criteria,
            baseline_counterfactual, framing_budget_min, p_flip, delta_payoff,
            info_cost, cost_of_delay_per_day.
        session: session id for provenance.
        lock: mark the frame locked once registered.

    Returns:
        dict with frame_id, contract verdict (blockers/warnings), the VOI
        verdict, and the ledger path.
    """
    from athena.intelligence.frame_ledger import (
        DEFAULT_LEDGER,
        FrameLedger,
        build_frame,
        compute_evi,
    )

    perms = get_permissions()
    perms.gate("frame_open")

    payload = json.loads(frame_json)
    frame = build_frame(payload, session=session)
    ledger = FrameLedger(DEFAULT_LEDGER)
    result = ledger.open(frame, lock=lock)
    voi = compute_evi(
        frame.p_flip,
        frame.delta_payoff,
        frame.info_cost,
        frame.framing_budget_min,
        frame.cost_of_delay_per_day,
    )
    return {
        "frame_id": frame.id,
        "ok": result.ok,
        "blockers": [v.to_dict() for v in result.blockers],
        "warnings": [v.to_dict() for v in result.warnings],
        "voi_verdict": voi.verdict,
        "voi_net_evi": voi.net_evi,
        "ledger": str(DEFAULT_LEDGER),
        "contract_report": result.to_ascii(),
    }


@mcp.tool(
    tags={"governance", "reasoning", "cluster15"},
)
def frame_validate(frame_json: str = "", frame_id: str = "") -> dict:
    """Run the R1-R10 frame contract + VOI stop rule on a frame.

    Call this on the CANDIDATE REFRAME before spending solution effort, and on
    any locked frame before a REVIEW date. Rejecting a bad frame early is the
    cheapest gate in the system; there is no probe that costs less.

    Args:
        frame_json: inline frame JSON (omit if using frame_id).
        frame_id: id of a frame already in the ledger.

    Returns:
        dict with the contract verdict, per-rule violations, and VOI verdict.
    """
    from athena.intelligence.frame_ledger import (
        DEFAULT_LEDGER,
        FrameLedger,
        build_frame,
        compute_evi,
        validate_frame,
    )

    perms = get_permissions()
    perms.gate("frame_validate")

    if frame_id:
        frame = FrameLedger(DEFAULT_LEDGER).get(frame_id)
        if frame is None:
            return {"ok": False, "error": f"unknown frame {frame_id}"}
    elif frame_json:
        frame = build_frame(json.loads(frame_json))
    else:
        return {"ok": False, "error": "provide frame_json or frame_id"}

    result = validate_frame(frame)
    voi = compute_evi(
        frame.p_flip,
        frame.delta_payoff,
        frame.info_cost,
        frame.framing_budget_min,
        frame.cost_of_delay_per_day,
    )
    return {
        "frame_id": frame.id,
        "ok": result.ok,
        "blockers": [v.to_dict() for v in result.blockers],
        "warnings": [v.to_dict() for v in result.warnings],
        "voi_verdict": voi.verdict,
        "contract_report": result.to_ascii(),
        "voi_report": voi.to_ascii(),
    }


@mcp.tool(
    tags={"governance", "reasoning", "cluster15"},
)
def frame_resolve(
    frame_id: str,
    supported: str = "",
    killed: str = "",
    regret: float | None = None,
    note: str = "",
    action: str = "",
) -> dict:
    """Score a locked frame against reality at its REVIEW date.

    Resolution is appended to the ledger as a NEW event; the pre-registered
    frame is never edited (that is the point of pre-registration). Produces the
    per-frame Brier score, whether the top hypothesis survived, and the
    realised regime.

    Args:
        frame_id: id of the frame being resolved.
        supported: comma-separated hypothesis ids that survived.
        killed: comma-separated hypothesis ids that were falsified.
        regret: optional self-reported regret, 0-10, recorded as an outcome
            signal (not as evidence for the diagnosis).
        note: one-line evidence note.
        action: what was actually done.

    Returns:
        dict with the resolution record.
    """
    from athena.intelligence.frame_ledger import DEFAULT_LEDGER, FrameLedger

    perms = get_permissions()
    perms.gate("frame_resolve")

    ledger = FrameLedger(DEFAULT_LEDGER)
    resolution = ledger.resolve(
        frame_id,
        supported=[s for s in supported.split(",") if s],
        killed=[k for k in killed.split(",") if k],
        regret=regret,
        note=note,
        decided_action=action,
    )
    return {"frame_id": frame_id, "resolution": resolution}


@mcp.tool(
    tags={"read", "governance", "reasoning", "cluster15"},
)
def frame_status() -> dict:
    """Report frame quality + protocol adoption (the measurement surface).

    Returns the numbers this layer previously never produced: frames opened /
    resolved, pending rot, mean frame Brier vs the 0.25 coin-flip baseline,
    skill, mode distribution, the thesis kill-switch status, and the adoption
    scan (do the Cluster #15 artifacts appear anywhere in the corpus?).

    Returns:
        dict with scoring and adoption metrics.
    """
    from athena.intelligence.frame_ledger import (
        DEFAULT_LEDGER,
        FrameLedger,
        scan_adoption,
        score_frames,
    )

    perms = get_permissions()
    perms.gate("frame_status")

    frames = FrameLedger(DEFAULT_LEDGER).frames()
    return {
        "scoring": score_frames(frames),
        "adoption": scan_adoption("."),
    }


@mcp.tool(
    tags={"governance", "decision", "gto"},
)
def decision_screen(
    action: str,
    payload_json: str,
    real: bool = False,
    review_date: str = "",
    prediction: str = "",
) -> dict:
    """Execute a strategic decision evaluation via the GTO numerical engine.

    Computes decision metrics (EEV, Kelly sizing, Ruin probability, MCDA ranking,
    Decision Monte Carlo, or Scenario-Matrix Robustness) and appends a verified
    decision receipt to .athena/decision_receipts.jsonl.

    Args:
        action: Calculation action to execute ('eev', 'kelly', 'ruin', 'monte-carlo',
            'mcda', 'decision-mc', 'robustness', 'barbell', 'devaluation', 'borrow-audit').
        payload_json: JSON string containing action parameters.
        real: True if this evaluation backs a consequential real-world decision.
        review_date: Calibration review date (YYYY-MM-DD) for real decisions.
        prediction: Anticipated outcome / hypothesis for calibration tracking.

    Returns:
        dict containing receipt_id, action, verdict, top, ascii_table, and result data.
    """
    from dataclasses import asdict

    from athena.intelligence.gto_engine import (
        _serialize_for_json,
        execute_decision_action,
    )

    perms = get_permissions()
    perms.gate("decision_screen")

    payload = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
    res, receipt = execute_decision_action(
        action=action,
        payload=payload,
        real=real,
        review_date=review_date or None,
        prediction=prediction or None,
    )

    result_dict = _serialize_for_json(asdict(res)) if hasattr(res, "__dataclass_fields__") else {"result": res}
    receipt_id = receipt["receipt_id"] if receipt else "N/A"
    ascii_table = res.to_ascii_table() if hasattr(res, "to_ascii_table") else str(res)
    if receipt:
        ascii_table += f"\nreceipt: {receipt_id}"

    return {
        "receipt_id": receipt_id,
        "action": action,
        "verdict": receipt["verdict"] if receipt else getattr(res, "verdict", "N/A"),
        "top": receipt["top"] if receipt else getattr(res, "top_candidate", "N/A"),
        "ascii_table": ascii_table,
        "result": result_dict,
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

    from athena.core.governance import RiskLevel, get_governance

    # 0. Protocol 509 Early Screen: If query indicates crisis, surface referral IMMEDIATELY
    # Life-safety overrides demo/redaction mode; no internal data or secrets are returned.
    from athena.core.lambda_scorer import compute_lambda
    from athena.tools.search import classify_query_intent, run_search
    early_lambda = compute_lambda(query)
    if early_lambda.get("is_crisis"):
        return {
            "status": "CRISIS_REFERRAL_GATE",
            "protocol": "SAF-509",
            "directive": (
                "HARD STOP (Protocol 509): Active crisis signals detected. "
                "Athena is an AI assistant, not a clinician. Surface professional crisis "
                "resources immediately. Do not execute problem framing, web search, or deep analysis."
            ),
            "referral": early_lambda.get("crisis_referral"),
            "missing": [],
            "ready": True,
            "lambda_score": early_lambda["score"],
            "risk_level": early_lambda["tier"],
        }

    perms = get_permissions()
    perms.gate("context_gate")

    # 1. Classify intent and set risk level
    intent = classify_query_intent(query)
    gov = get_governance()

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

    lambda_res = compute_lambda(
        query,
        intent=intent,
        web_required=web_required,
        underspec_opt=underspec_opt,
    )

    risk_level = lambda_res["risk_level"]
    if risk_level == RiskLevel.ULTRA:
        web_required = True
        if web_reason == "none":
            web_reason = "ultra_tier"

    gov.set_risk_level(risk_level)

    # 2. Determine effective web setting
    effective_web = web if web is not None else web_required

    # 3. Run search (captures JSON output)
    gov.mark_search_performed(query)  # Mark semantic leg

    # Latent Meta-Pattern projection (GTO Upgrade: cross-domain expansion)
    latent_patterns = []
    try:
        from athena.tools.meta_pattern_matcher import detect_latent_meta_patterns
        latent_patterns = detect_latent_meta_patterns(query, max_patterns=2)
    except ImportError:
        pass

    # Execute search directly without stdout hijacking (WS3.1 / M-1 fix)
    search_results = run_search(
        query,
        limit=limit,
        json_output=True,
        include_personal=True,
        web=effective_web,
        intent=intent,
        print_output=False,
    )
    if not isinstance(search_results, dict):
        search_results = {"results": [], "error": "Failed to obtain search output"}

    # Secondary multi-hop retrieval for matched Meta-Patterns
    if latent_patterns:
        existing_ids = {
            r.get("id") for r in search_results.get("results", []) if isinstance(r, dict)
        }
        for mp in latent_patterns:
            try:
                mp_results = run_search(
                    mp["search_terms"],
                    limit=2,
                    json_output=True,
                    include_personal=False,
                    web=False,
                    intent="SYSTEM_KNOWLEDGE",
                    print_output=False,
                )
            except Exception:
                mp_results = {}
            if isinstance(mp_results, dict):
                for item in mp_results.get("results", []):
                    if isinstance(item, dict) and item.get("id") not in existing_ids:
                        item["meta_pattern_projection"] = {
                            "id": mp["id"],
                            "name": mp["name"],
                            "rationale": mp["description"],
                        }
                        search_results.setdefault("results", []).append(item)
                        existing_ids.add(item.get("id"))

    # 4. Build personalisation frame (when relevant)
    personalisation = None
    user_state = None
    if intent == "PERSONALISED_DECISION":
        try:
            from athena.core.models import SearchResult as _SR
            from athena.tools.personalisation import (
                build_personalisation_prompt,
                build_user_state_snapshot,
            )
            raw_results = search_results.get("results", [])
            sr_objects = [
                _SR(**r) if isinstance(r, dict) else r
                for r in raw_results
            ]
            personalisation = build_personalisation_prompt(query, sr_objects)
            user_state = build_user_state_snapshot()
        except Exception as e:
            import sys
            print(f"   ⚠️ Personalisation frame construction failed: {e}", file=sys.stderr)

    # 5. Check for strong local hit (threshold must be reachable under RRF normalization)
    local_first = False
    results_list = search_results.get("results", [])
    if isinstance(results_list, list) and results_list:
        top_result = results_list[0] if results_list else {}
        top_score = top_result.get("rrf_score", 0) if isinstance(top_result, dict) else 0
        # CONFIDENCE_HIGH (0.03) from search.py — the actual high-confidence
        # threshold aligned to RRF_K=60 normalization. Prior value 0.8 was
        # unreachable (max theoretical RRF ≈ 0.61) — dead branch since inception.
        if top_score >= 0.03:
            local_first = True

    # 6. Determine missing requirements and degradation status
    missing = []
    has_parse_error = bool(search_results.get("error"))
    is_degraded = bool(
        search_results.get("degraded_recall")
        or search_results.get("quality") == "degraded"
        or has_parse_error
    )
    if has_parse_error:
        missing.append("retrieval_parse")
        local_first = False
    elif is_degraded:
        missing.append("semantic")
        local_first = False

    if risk_level == RiskLevel.ULTRA and not effective_web and web_required:
        missing.append("web")

    # 7. Build directive
    directive_parts = []
    if has_parse_error:
        directive_parts.append(
            f"ERROR [RETRIEVAL PARSE FAILURE]: {search_results.get('error')}. "
            "Context bundle is incomplete; do not rely on local search results."
        )
    elif is_degraded:
        directive_parts.append(
            "WARNING [DEGRADED RETRIEVAL]: Semantic vector search channel failed. "
            "Results are lexical-only. Do not treat absence of memory as proof of non-existence."
        )
    elif local_first:
        directive_parts.append(
            "Strong local hit found. Prefer local knowledge; web supplements."
        )

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

    # v3.1: Meta-awareness bridge — cross-harness parity with Claude Code hook.
    # When gate_meta.classify() fires, inject a META directive so any MCP client
    # (Antigravity, Gemini, Codex) gets the substance-decode kernel without
    # requiring a Claude Code UserPromptSubmit hook. Never blocks, never errors.
    try:
        from athena.core.gate_meta import classify as meta_classify
        meta_classes = meta_classify(query)
        if meta_classes:
            directive_parts.append(
                f"META: Structural trigger {meta_classes} fired — run the "
                "substance-decode interpreter kernel (arena → prior → discriminators "
                "→ sign check → receiver-frame → F≠R → payoff) before answering. "
                "Load substance-decode skill for depth."
            )
    except Exception:
        pass  # stdlib-only gate; never block context_gate on import failure

    # 8. Web metadata and tri-state grounding_status
    web_count = len([
        r for r in (results_list if isinstance(results_list, list) else [])
        if isinstance(r, dict) and r.get("source") == "web_search"
    ])

    if not effective_web:
        grounding_status = "unrequested"
    elif web_count > 0:
        grounding_status = "ok"
    else:
        grounding_status = "tool_error"

    # Circuit breaker on web tool_error
    if effective_web and web_count == 0:
        directive_parts.append(
            "CIRCUIT BREAKER (P514): Web search returned 0 results or degraded (tool_error). "
            "Do NOT treat search failure as evidence of non-existence. Never emit universal-negative "
            "claims ('never made', 'does not exist') without verified external search."
        )

    # Epistemic Gate directive: negative-claim protection
    directive_parts.append(
        "EPISTEMIC GATE: Never assert that a product, entity, or event does NOT exist or was NEVER made "
        "based solely on absence from pre-training weights. Absence of memory is not proof of non-existence. "
        "Cite verified live search or state epistemic uncertainty."
    )

    # Latent Meta-Pattern directive (GTO Upgrade)
    if latent_patterns:
        mp_summary = ", ".join(f"{mp['id']} ({mp['name']})" for mp in latent_patterns)
        directive_parts.append(
            f"CROSS-DOMAIN PROJECTION: Query projected onto latent Meta-Patterns: {mp_summary}. "
            "Synthesize structural invariants across these domains."
        )

    if not directive_parts:
        directive_parts.append("Context bundle assembled. Proceed with answer.")

    directive = " ".join(directive_parts)

    web_meta = {
        "fired": effective_web,
        "required": web_required,
        "reason": web_reason,
        "count": web_count,
        "grounding_status": grounding_status,
    }

    # Add provider info if available
    for r in (results_list if isinstance(results_list, list) else []):
        if isinstance(r, dict) and r.get("source") == "web_search":
            meta = r.get("metadata", {})
            if isinstance(meta, dict) and "provider" in meta:
                web_meta["provider"] = meta["provider"]
                break

    # Build evidence checklist (Phase C1.2)
    evidence_checklist = []
    f_names = [f["name"] for f in lambda_res.get("features", [])]
    if "currency_amount" in f_names or "financial_concept" in f_names:
        evidence_checklist.append("Verify numerical quantities and capital boundaries against CANONICAL or account statements.")
    if "irreversible_action" in f_names or "legal_liability" in f_names:
        evidence_checklist.append("Audit contract indemnity, liability exposure, and counterparty recoil boundaries.")
    if "ruin_risk" in f_names:
        evidence_checklist.append("Verify survival floor, stop-loss limits, and worst-case tail-risk firewalls.")
    if latent_patterns:
        evidence_checklist.append(f"Synthesize structural invariants across latent Meta-Patterns ({', '.join(mp['id'] for mp in latent_patterns)}).")
    if not evidence_checklist:
        evidence_checklist.append("Ground substantive claims in retrieved Exocortex session logs or live web results.")

    # Calculate preliminary retrieval sufficiency ratio (C-2 / H-5 fix)
    if is_degraded:
        sufficiency = 0.4
    elif missing:
        sufficiency = 0.6
    else:
        sufficiency = 1.0 if (local_first or (len(results_list) >= 3 and not is_degraded) or web_count > 0) else 0.75

    return {
        "context": search_results,
        "lambda": {
            "score": lambda_res["score"],
            "tier": lambda_res["tier"],
            "features": lambda_res["features"],
        },
        "evidence_checklist": evidence_checklist,
        "sufficiency": sufficiency,
        "latent_meta_patterns": latent_patterns,
        "personalisation": personalisation,
        "user_state": user_state,
        "web": web_meta,
        "grounding_status": grounding_status,
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
