#!/usr/bin/env python3
"""
hook_epistemic_gate.py — Epistemic Grounding Output Gate
======================================================

Protects against the Negative-Knowledge Fallacy:
Asserting that an entity, product, feature, or event does NOT exist or was NEVER made
based solely on absence from internal model weights.

Fires on agent turn completion (Stop event) in Claude Code and as a standalone verification gate.

Rules:
1. Detects universal-negative claim patterns:
   - "never (been) made / manufactured / produced / released / shipped / created / sold"
   - "(does not / did not) exist"
   - "no such (model / product / device / version / ...)"
   - "is not a real (model / product / device / version / ...)"
   - "has never existed"
2. When a universal-negative pattern is detected:
   - Verifies whether external grounding was performed (via telemetry in .athena/invocations.jsonl
     or tool calls in transcript / options).
   - If NO live verification occurred: BLOCKS output (exit code 2), instructing the agent
     to verify via live search or downgrade the claim to epistemic uncertainty.
   - If verified: ALLOWS output (exit code 0).
3. If no universal-negative claim is detected:
   - ALLOWS output (exit code 0).

Contract:
  - Exit 0: Allow completion
  - Exit 2: Block completion with actionable remediation message on stderr
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

UNIVERSAL_NEGATIVE_PATTERNS = [
    (
        r"\b(?:has\s+)?never\s+(?:been\s+)?(?:made|manufactured|produced|released|shipped|created|sold|launched)\b",
        "Universal claim of non-manufacture ('never made / released')",
    ),
    (
        r"\b(?:does\s+not|doesn'?t|did\s+not|didn'?t)\s+exist\b",
        "Universal claim of non-existence ('does not exist')",
    ),
    (
        r"\bno\s+such\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition|feature|release)\b",
        "Categorical denial of existence ('no such model/product')",
    ),
    (
        r"\bis\s+not\s+a\s+real\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition)\b",
        "Categorical assertion of fictionality ('is not a real model/product')",
    ),
    (
        r"\bnever\s+existed\b",
        "Universal claim of past non-existence ('never existed')",
    ),
]

# Benign idioms that contain negative words but are NOT empirical claims about external entities
BENIGN_EXCEPTIONS = [
    r"\bthere is no need to\b",
    r"\bthere is no doubt\b",
    r"\bthere is no problem\b",
    r"\bthere is no question\b",
    r"\bthere is no reason to\b",
    r"\bdoes not exist yet in your codebase\b",
    r"\bfile does not exist\b",
    r"\bdirectory does not exist\b",
    r"\bpath does not exist\b",
]


def detect_negative_claims(text: str) -> list[tuple[str, str]]:
    """Scan text for universal-negative claims.
    Returns list of (matched_substring, description).
    """
    if not text:
        return []

    # First check if text matches benign exceptions exclusively
    cleaned_lines = []
    for line in text.splitlines():
        if any(re.search(exc, line, re.IGNORECASE) for exc in BENIGN_EXCEPTIONS):
            continue
        cleaned_lines.append(line)
    scan_text = "\n".join(cleaned_lines)

    matches = []
    for pattern, desc in UNIVERSAL_NEGATIVE_PATTERNS:
        found = re.search(pattern, scan_text, re.IGNORECASE)
        if found:
            matches.append((found.group(0), desc))

    return matches


def has_recent_grounding(max_age_seconds: float = 180.0, invocations_path: Path | None = None) -> bool:
    """Check .athena/invocations.jsonl for recent successful web or smart search."""
    path = invocations_path or (REPO_ROOT / ".athena" / "invocations.jsonl")
    if not path.exists():
        return False

    now_utc = datetime.now(timezone.utc).timestamp()
    now_local = datetime.now().timestamp()
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines[-30:]):  # Scan last 30 entries
                try:
                    data = json.loads(line)
                    t_str = data.get("timestamp", "")
                    if not t_str:
                        continue
                    if t_str.endswith("Z"):
                        t_str = t_str[:-1] + "+00:00"
                    t = datetime.fromisoformat(t_str)
                    if t.tzinfo is None:
                        age = now_local - t.timestamp()
                    else:
                        age = now_utc - t.timestamp()

                    if 0 <= age <= max_age_seconds:
                        inv_type = data.get("type", "")
                        status = data.get("grounding_status", "")
                        if inv_type in ("web_search", "web_search_external") and status != "tool_error":
                            return True
                        if inv_type in ("tool", "skill") and data.get("name") in ("smart_search", "search_web"):
                            return True
                except Exception:
                    continue
    except Exception:
        return False

    return False


def verify_text(
    text: str,
    force_grounded: bool = False,
    invocations_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Verify text against epistemic grounding rules.
    Returns (is_allowed, error_messages).
    """
    matches = detect_negative_claims(text)
    if not matches:
        return True, []

    if force_grounded or has_recent_grounding(invocations_path=invocations_path):
        return True, []

    errors = []
    for match_text, desc in matches:
        errors.append(
            f"Universal-negative claim detected: '{match_text}' ({desc}). "
            "Absence from model training memory is NOT proof of non-existence. "
            "You MUST perform a live search (search_web / read_url_content) before claiming "
            "an entity/product never existed or was never made, or explicitly downgrade "
            "to epistemic uncertainty ('I could not find records of...')."
        )
    return False, errors


def main():
    parser = argparse.ArgumentParser(description="Epistemic Grounding Output Gate")
    parser.add_argument("--text", type=str, help="Text content to verify directly")
    parser.add_argument("--file", type=str, help="File path to verify")
    parser.add_argument("--force-grounded", action="store_true", help="Override grounding check for testing")
    parser.add_argument("--invocations-file", type=str, help="Custom invocations file path for testing")
    args, remaining = parser.parse_known_args()

    text_to_check = ""
    if args.text:
        text_to_check = args.text
    elif args.file:
        p = Path(args.file)
        if p.exists():
            text_to_check = p.read_text(encoding="utf-8", errors="ignore")
    else:
        # Check stdin for Claude Code Stop payload
        try:
            stdin_data = sys.stdin.read()
            if stdin_data:
                try:
                    payload = json.loads(stdin_data)
                    if isinstance(payload, dict):
                        transcript_path = payload.get("transcript_path")
                        if transcript_path and os.path.exists(transcript_path):
                            with open(transcript_path, encoding="utf-8") as tf:
                                for line in reversed(tf.readlines()[-20:]):
                                    try:
                                        rec = json.loads(line)
                                        msg = rec.get("message", {})
                                        if msg.get("role") == "assistant":
                                            content = msg.get("content", "")
                                            if isinstance(content, str):
                                                text_to_check = content
                                                break
                                            elif isinstance(content, list):
                                                text_to_check = " ".join(
                                                    c.get("text", "") for c in content if isinstance(c, dict)
                                                )
                                                break
                                    except Exception:
                                        continue
                        else:
                            text_to_check = payload.get("text", "")
                except json.JSONDecodeError:
                    text_to_check = stdin_data
        except Exception:
            pass

    if not text_to_check:
        sys.exit(0)

    inv_path = Path(args.invocations_file) if args.invocations_file else None
    is_allowed, errors = verify_text(
        text_to_check,
        force_grounded=args.force_grounded,
        invocations_path=inv_path,
    )
    if is_allowed:
        sys.exit(0)

    reason = (
        "Output Verifier Blocked Completion (Epistemic Grounding Gate):\n"
        + "\n".join(f"  - {err}" for err in errors)
        + "\nPlease verify via search_web / read_url_content or rephrase with calibrated epistemic uncertainty."
    )
    print(reason, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
