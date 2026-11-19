#!/usr/bin/env python3
"""
hook_meta_awareness_gate.py — v3: Code-enforced domain-general interpreter gate.

Claude Code UserPromptSubmit hook. Fires on every user prompt. v2 matched
domain keywords (relational/social only); v3 classifies by ACT STRUCTURE so the
same gate covers trading, consumer, institutional, commercial, broadcast, and
relational reads without per-domain regex whack-a-mole.

Trigger classes (structural, domain-agnostic):
    T1 INBOUND-NARRATIVE   received story/act with stakes ("why did they…")
    T2 OUTBOUND-COMMIT     audience-facing act about to be (or just) emitted
    T3 THIRD-PARTY-VERDICT forming/broadcasting judgment of someone else's act
    T4 RESOURCE-COMMIT     novel money/time/reputation deployment (~S$100+)
    T5 FELT-EVIDENCE       feeling offered as evidence ("feels like the market…")

Why this exists (S545/S583/S601): `auto-invoke: true` frontmatter enforced
nothing (S534 anti-self-mythologizing). v2 closed that gap for relational cases
only; each new case class needed a new regex group (S583 added JUDGMENT). v3 is
the generalization: new domains extend the ARENA LIBRARY (substance-decode
Module 3, content), never this file (mechanism).

Epistemic status: code-enforced (harness runs it every prompt). KNOWN LIMITS:
      - Text-only: cannot fire on an act the user never narrates.
      - Claude Code only: hook-less environments revert to agent-discretion
        UNLESS the agent calls context_gate (MCP), which now carries the
        meta directive when gate_meta.classify() fires (v3.1 cross-harness
        bridge — see mcp_server.py::context_gate).
      - Regex tier is high-recall/low-precision by design. On a regex miss,
        NO kernel enters context — the fallback is the context_gate MCP
        bridge (v3.1) and AGENTS.md Substance Decode Lens (agent-discretion
        prose). Biased to over-fire (CS-125: false positive = one cheap
        reminder; false negative = a Hummer driven off the lot).
      - NEGATIVE guard: routine-ops prompts (reconciliation, test runs, doc
        chores) suppress a T4-only or T1-only fire to keep fire-rate in
        the 10-30% band.

Contract: NEVER blocks (always exit 0), <50ms, stdlib only. Anything printed to
    stdout is injected into model context by the UserPromptSubmit hook.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# SSOT: Delegate classification engine directly to athena.core.gate_meta (TD-069b)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SDK_PATH = PROJECT_ROOT / "src"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.gate_meta import (
    CLASSES,
    NEGATIVE,
    REMINDER_TEMPLATE,
    classify,
)

__all__ = ["CLASSES", "NEGATIVE", "REMINDER_TEMPLATE", "classify", "log_fire"]



def log_fire(fired: list) -> None:
    """Fire-rate telemetry — reuses .athena/invocations.jsonl. Never raises."""
    if os.environ.get("ATHENA_TELEMETRY_DISABLE") == "1":
        return
    try:
        path = os.path.join(os.getcwd(), ".athena", "invocations.jsonl")
        if not os.path.isdir(os.path.dirname(path)):
            return
        record = {
            "type": "hook",
            "name": "meta_awareness_gate",
            "classes": fired,
            "trigger": "UserPromptSubmit",
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    prompt = (payload.get("prompt") or "").strip()
    if prompt:
        fired = classify(prompt)
        if fired:
            sys.stdout.write(REMINDER_TEMPLATE.format(classes=", ".join(fired)) + "\n")
            log_fire(fired)
    sys.exit(0)


if __name__ == "__main__":
    main()
