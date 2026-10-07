#!/usr/bin/env python3
"""
stop_governance_gate.py — Antigravity Stop Lifecycle Governance Gate
===================================================================

Enforces:
1. Law #6 External Verification Mandate (Triple-Lock):
   Substantive turns (STANDARD/ULTRA) MUST invoke at least one external tool
   (context_gate, smart_search, search_web, view_file, grep_search, run_command)
   before emitting a final answer.
2. Epistemic Grounding Gate:
   Universal-negative claims ('never made', 'does not exist') require verified web search.

Antigravity Stop Hook Contract:
  Input (stdin): JSON object with transcriptPath, terminationReason, etc.
  Output (stdout): {"decision": "allow"} or {"decision": "continue", "reason": "..."}
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GATE_DECISIONS_PATH: Path = REPO_ROOT / ".athena" / "gate_decisions.jsonl"
LOOP_GUARD_PATH: Path = REPO_ROOT / ".agent" / "state" / "gate_loop_guard.json"
RETRIEVAL_RECEIPTS_PATH: Path = REPO_ROOT / ".athena" / "retrieval_receipts.jsonl"


def _check_and_increment_loop_guard(key: str) -> bool:
    """Return True if loop count >= 2 (escalate/allow with warning), else increment and return False."""
    try:
        data: dict[str, int] = {}
        if LOOP_GUARD_PATH.exists():
            data = json.loads(LOOP_GUARD_PATH.read_text(encoding="utf-8"))
        count = data.get(key, 0)
        if count >= 2:
            return True
        data[key] = count + 1
        LOOP_GUARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOOP_GUARD_PATH.write_text(json.dumps(data), encoding="utf-8")
        return False
    except Exception:
        return False


def _reset_loop_guard() -> None:
    """Reset loop guard on successful allow."""
    try:
        if LOOP_GUARD_PATH.exists():
            LOOP_GUARD_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def log_gate_decision(
    check: int | str,
    decision: str,
    reason: str,
    transcript_sha1: str,
    extra: dict[str, Any] | None = None,
) -> None:
    """Append decision record to .athena/gate_decisions.jsonl (append-only, T3.3)."""
    try:
        log_file = GATE_DECISIONS_PATH
        log_file.parent.mkdir(parents=True, exist_ok=True)
        record: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "check": check,
            "decision": decision,
            "reason": reason,
            "transcript_sha1": transcript_sha1,
        }
        if extra:
            record.update(extra)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


# Trivial/conversational phrases exempt from the verification mandate
TRIVIAL_PATTERNS = [
    r"^(hi|hello|hey|yo|morning|afternoon|evening)\b",
    r"^(thanks|thank you|ty|cheers|got it|noted|ok|okay|cool|nice|good)\b",
    r"^(yes|no|proceed|continue|agree|approved|lgtm|looks good)\b",
    r"^(bye|goodbye|cya|see you)\b",
]

UNIVERSAL_NEGATIVE_PATTERNS = [
    r"\b(?:has\s+)?never\s+(?:been\s+)?(?:made|manufactured|produced|released|shipped|created|sold|launched)\b",
    r"\b(?:does\s+not|doesn'?t|did\s+not|didn'?t)\s+exist\b",
    r"\bno\s+such\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition|feature|release)\b",
    r"\bis\s+not\s+a\s+real\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition)\b",
    r"\bhas\s+never\s+existed\b",
]

EXTERNAL_TOOL_NAMES = {
    # Exocortex / MCP semantic retrieval
    "context_gate", "smart_search", "agentic_search",
    # Web / URL retrieval
    "search_web", "read_url_content",
}



def is_trivial_query(query: str) -> bool:
    """Check if a user prompt is trivial conversational banter (SNIPER-exempt)."""
    cleaned = query.strip().lower()
    if not cleaned:
        return True

    words = cleaned.split()
    if len(words) <= 4:
        for pat in TRIVIAL_PATTERNS:
            if re.search(pat, cleaned):
                return True

    return False


def clean_prompt_content(raw_content: str) -> str:
    """Strip Antigravity XML tags from raw prompt content."""
    text = raw_content
    text = re.sub(r"<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>", "", text)
    text = re.sub(r"<USER_SETTINGS_CHANGE>[\s\S]*?</USER_SETTINGS_CHANGE>", "", text)
    text = re.sub(r"<SYSTEM_MESSAGE>[\s\S]*?</SYSTEM_MESSAGE>", "", text)
    m = re.search(r"<USER_REQUEST>([\s\S]*?)</USER_REQUEST>", text)
    if m:
        return m.group(1).strip()
    return text.strip()


def extract_unresolved_file_links(text: str, repo_root: Path) -> list[str]:
    """Extract file:// links from text and return those that do not resolve to an existing file."""
    raw_urls = re.findall(r"file://[^\s\)\>\"\']+", text)
    unresolved: list[str] = []
    for raw in raw_urls:
        clean_url = raw.rstrip(".,;:?")
        url_without_frag = clean_url.split("#", 1)[0]
        path_str = url_without_frag[len("file://"):]
        decoded_path = urllib.parse.unquote(path_str)
        if not decoded_path:
            continue

        if decoded_path.startswith("/"):
            p = Path(decoded_path)
            if p.exists():
                continue
            rel_candidate = repo_root / decoded_path.lstrip("/")
            if rel_candidate.exists():
                continue
            if clean_url not in unresolved:
                unresolved.append(clean_url)
        else:
            target_path = repo_root / decoded_path
            if not target_path.exists() and clean_url not in unresolved:
                unresolved.append(clean_url)
    return unresolved


def evaluate_turn_governance(transcript_path: str) -> dict[str, str]:
    """Inspect the latest turn in transcript.jsonl for governance compliance."""
    path = Path(transcript_path).expanduser()
    if not path.exists():
        turn_key = f"missing_path_{transcript_path}"
        if _check_and_increment_loop_guard(turn_key):
            return {"decision": "allow", "warning": "Loop guard tripped: transcript path missing 2+ times"}
        return {"decision": "continue", "reason": "STATE UNKNOWN — transcript file does not exist; could not evaluate governance"}

    try:
        transcript_sha1 = hashlib.sha1(path.read_bytes()).hexdigest()
    except Exception:
        transcript_sha1 = ""

    steps: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        steps.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        turn_key = f"unreadable_path_{transcript_path}"
        if _check_and_increment_loop_guard(turn_key):
            return {"decision": "allow", "warning": "Loop guard tripped: transcript unreadable 2+ times"}
        return {"decision": "continue", "reason": "STATE UNKNOWN — unreadable transcript; could not evaluate governance"}

    if not steps:
        turn_key = f"empty_steps_{transcript_path}"
        if _check_and_increment_loop_guard(turn_key):
            return {"decision": "allow", "warning": "Loop guard tripped: transcript empty 2+ times"}
        return {"decision": "continue", "reason": "STATE UNKNOWN — empty transcript; could not evaluate governance"}

    # Find the index of the most recent USER_INPUT
    last_user_idx = -1
    last_user_content = ""
    for i, step in enumerate(steps):
        if step.get("type") == "USER_INPUT":
            last_user_idx = i
            last_user_content = step.get("content", "")

    if last_user_idx == -1:
        turn_key = f"no_user_{transcript_path}"
        if _check_and_increment_loop_guard(turn_key):
            return {"decision": "allow", "warning": "Loop guard tripped: no USER_INPUT 2+ times"}
        return {"decision": "continue", "reason": "STATE UNKNOWN — no recoverable USER_INPUT in transcript; could not evaluate governance"}

    cleaned_user_prompt = clean_prompt_content(last_user_content)

    # Inspect all steps following the last USER_INPUT
    turn_steps = steps[last_user_idx + 1:]
    tools_called: list[str] = []
    latest_model_output = ""

    for s in turn_steps:
        # Check tool calls
        t_calls = s.get("tool_calls", [])
        if isinstance(t_calls, list):
            for tc in t_calls:
                if isinstance(tc, dict):
                    name = tc.get("name", "")
                    if name == "run_command":
                        args = tc.get("args", {})
                        cmd = args.get("CommandLine", "") if isinstance(args, dict) else ""
                        cmd_clean = cmd.strip().lower()
                        # Only actual retrieval/test execution scripts count as verified command execution
                        retrieval_markers = (
                            "smart_search", "supabase_search", "search.py", "run_search",
                            "fast_search", "exocortex", "index_health", "fts_search", "pytest", "run_tests"
                        )
                        if any(marker in cmd_clean for marker in retrieval_markers):
                            tools_called.append("run_command_verified")
                    elif name:
                        tools_called.append(name)

        # Check content for model output
        if s.get("source") == "MODEL" and s.get("type") == "PLANNER_RESPONSE":
            content = s.get("content", "")
            if content:
                latest_model_output += "\n" + content

    # Evaluate risk tier using lambda_scorer (Phase C1)
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from athena.core.lambda_scorer import compute_lambda
        lambda_info = compute_lambda(cleaned_user_prompt)

        # Protocol 509: If crisis, require that the structured referral was actually emitted
        if lambda_info.get("is_crisis"):
            # Structural referral verification (C-3): Require either the structured referral header
            # or explicit presence of the specialized crisis hotlines (1-767 / 6389 2222).
            # A bare '995' token (e.g. '995 basis points') MUST NOT satisfy this gate.
            has_sos = "1-767" in latest_model_output or "9151 1767" in latest_model_output or "samaritans" in latest_model_output.lower()  # pds:allow
            has_imh = "6389 2222" in latest_model_output or "6389-2222" in latest_model_output
            has_referral_header = "Protocol 509" in latest_model_output or "findahelpline" in latest_model_output.lower()

            if (has_sos and has_imh) or has_referral_header:
                log_gate_decision("protocol_509", "allow", "crisis_referral_emitted", transcript_sha1)
                return {"decision": "allow"}
            reason = (
                "CRISIS REFERRAL REQUIRED (Protocol 509): Severe distress or self-harm signals detected. "
                "You MUST surface the emergency support referral hotlines (SOS 1-767, IMH 6389 2222, 995 Ambulance) "
                "before concluding this turn."
            )
            log_gate_decision("protocol_509", "continue", reason, transcript_sha1)
            return {
                "decision": "continue",
                "reason": reason,
            }

        if lambda_info["tier"] == "SNIPER":
            log_gate_decision("tier", "allow", "sniper_exempt", transcript_sha1)
            return {"decision": "allow"}
    except Exception:
        if is_trivial_query(cleaned_user_prompt):
            log_gate_decision("tier", "allow", "trivial_exempt", transcript_sha1)
            return {"decision": "allow"}

    # Check 1: Did the agent call ANY external verification tool?
    external_called = any(t in EXTERNAL_TOOL_NAMES or t == "run_command_verified" for t in tools_called)

    if not external_called:
        reason = (
            "STOP BLOCKED by Law #6 Triple-Lock Gate: You attempted to complete a "
            "substantive turn without external verification. You MUST execute context_gate(query) "
            "or an external verification tool before concluding this turn."
        )
        log_gate_decision(1, "continue", reason, transcript_sha1)
        return {
            "decision": "continue",
            "reason": reason,
        }

    # WS2.1: Verify retrieval receipt when local retrieval was called
    receipts_file = RETRIEVAL_RECEIPTS_PATH
    if receipts_file.exists() and any(t in ("context_gate", "smart_search") for t in tools_called):
        try:
            latest_receipt = None
            with open(receipts_file, encoding="utf-8") as rf:
                for rline in rf:
                    rline = rline.strip()
                    if rline:
                        try:
                            latest_receipt = json.loads(rline)
                        except Exception:
                            pass
            if latest_receipt and latest_receipt.get("quality") == "degraded":
                web_verified = (
                    "search_web" in tools_called
                    or "read_url_content" in tools_called
                )
                if not web_verified:
                    reason = (
                        "STOP BLOCKED by Degradation Guard: Retrieval returned quality='degraded' "
                        "(semantic vector channel unavailable). You must cross-verify with search_web() "
                        "or external documentation before concluding this turn."
                    )
                    log_gate_decision(1, "continue", reason, transcript_sha1)
                    return {
                        "decision": "continue",
                        "reason": reason,
                    }
        except Exception:
            pass

    # Check 2: Did the agent emit an ungrounded universal negative?
    if latest_model_output:
        has_negative_claim = any(
            re.search(pat, latest_model_output, re.IGNORECASE)
            for pat in UNIVERSAL_NEGATIVE_PATTERNS
        )
        if has_negative_claim:
            web_verified = (
                "search_web" in tools_called
                or "read_url_content" in tools_called
            )
            if not web_verified:
                reason = (
                    "STOP BLOCKED by Epistemic Grounding Gate: You asserted a universal-negative "
                    "claim ('does not exist' / 'never made') without live web verification. "
                    "Verify via search_web() or rephrase with calibrated epistemic uncertainty."
                )
                log_gate_decision(2, "continue", reason, transcript_sha1)
                return {
                    "decision": "continue",
                    "reason": reason,
                }

    # Check 3: Did the agent emit unresolved file:// links?
    if latest_model_output:
        unresolved_links = extract_unresolved_file_links(latest_model_output, REPO_ROOT)
        if unresolved_links:
            reason = (
                f"STOP BLOCKED: Unresolved file links detected: {unresolved_links}. "
                "Ensure all file:// links point to existing files on disk before concluding."
            )
            log_gate_decision(3, "continue", reason, transcript_sha1)
            return {
                "decision": "continue",
                "reason": reason,
            }

    # Check 4: Did the agent emit unreceipted GTO engine claims? (T3.3)
    if latest_model_output:
        try:
            from athena.intelligence.gto_engine import find_unreceipted_engine_claims
            receipts_file = REPO_ROOT / ".athena" / "decision_receipts.jsonl"
            unreceipted = find_unreceipted_engine_claims(latest_model_output, receipts_file)
            if unreceipted:
                reason = (
                    f"STOP BLOCKED by Decision Receipt Gate: Unreceipted GTO engine claims detected: {unreceipted}. "
                    "Run the engine via MCP decision_screen or scripts/gto_exec.sh to obtain a valid GTO-xxxxxxxx receipt, "
                    "or tag the claim with [agent-estimate]."
                )
                log_gate_decision(4, "continue", reason, transcript_sha1)
                return {
                    "decision": "continue",
                    "reason": reason,
                }
        except Exception as exc:
            log_gate_decision(4, "allow", "check_4_exception", transcript_sha1, extra={"error": repr(exc)})

    # Check 5: Citation title mismatch in final answer (T3.2)
    if latest_model_output:
        try:
            scripts_dir = REPO_ROOT / ".agent" / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from verify_canon_citations import check_text_citations
            findings = check_text_citations(latest_model_output)
            mismatches = [f for f in findings if f.get("status") == "MISMATCH"]
            if mismatches:
                mismatch_details = [f"§{m['cited_line']} (expected '{m['name']}')" for m in mismatches]
                reason = (
                    f"STOP BLOCKED by Citation Title Gate: CANONICAL citation title mismatch detected: "
                    f"{', '.join(mismatch_details)}. Line numbers in CANONICAL.md shift on edits; "
                    "verify the cited title matches the actual entry in CANONICAL.md or cite by title."
                )
                log_gate_decision(5, "continue", reason, transcript_sha1)
                return {
                    "decision": "continue",
                    "reason": reason,
                }
        except Exception as exc:
            log_gate_decision(5, "allow", "check_5_exception", transcript_sha1, extra={"error": repr(exc)})

    log_gate_decision("all", "allow", "clean", transcript_sha1)
    return {"decision": "allow"}


def main():
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        if _check_and_increment_loop_guard("empty_stdin"):
            print(json.dumps({"decision": "allow", "warning": "Loop guard tripped: empty stdin repeated 2+ times"}))
            return
        log_gate_decision("indeterminate", "continue", "STATE UNKNOWN — empty stdin; could not evaluate governance", "")
        print(json.dumps({"decision": "continue", "reason": "STATE UNKNOWN — empty stdin; could not evaluate governance"}))
        return

    try:
        payload = json.loads(raw_input)
    except Exception:
        if _check_and_increment_loop_guard("unparseable_stdin"):
            print(json.dumps({"decision": "allow", "warning": "Loop guard tripped: unparseable stdin repeated 2+ times"}))
            return
        log_gate_decision("indeterminate", "continue", "STATE UNKNOWN — unparseable JSON; could not evaluate governance", "")
        print(json.dumps({"decision": "continue", "reason": "STATE UNKNOWN — unparseable JSON; could not evaluate governance"}))
        return

    termination_reason = payload.get("terminationReason", "")
    # Fail-CLOSED: only bypass for involuntary terminations.
    # model_stop = agent chose to stop (must verify), everything else = interrupted.
    NON_VOLUNTARY_TERMINATIONS = {"max_tokens", "error", "timeout", "cancelled", "tool_error"}
    if termination_reason in NON_VOLUNTARY_TERMINATIONS:
        _reset_loop_guard()
        print(json.dumps({"decision": "allow"}))
        return

    transcript_path = payload.get("transcriptPath", "")
    if not transcript_path:
        if _check_and_increment_loop_guard("missing_transcript_path"):
            print(json.dumps({"decision": "allow", "warning": "Loop guard tripped: missing transcriptPath repeated 2+ times"}))
            return
        log_gate_decision("indeterminate", "continue", "STATE UNKNOWN — missing transcriptPath; could not evaluate governance", "")
        print(json.dumps({"decision": "continue", "reason": "STATE UNKNOWN — missing transcriptPath; could not evaluate governance"}))
        return

    result = evaluate_turn_governance(transcript_path)
    if result.get("decision") == "allow":
        _reset_loop_guard()
    print(json.dumps(result))


if __name__ == "__main__":
    main()
