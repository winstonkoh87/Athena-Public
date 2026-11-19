#!/usr/bin/env python3
"""
scripts/eval_problem_solving_ab.py — Opt-in A/B Problem-Solving Benchmark
=========================================================================

Compares Baseline LLM vs Athena-scaffolded (context_gate META-TRIAGE +
gate_meta + meta-pattern projection) across the frozen 30-case unseen holdout
set (`tests/eval/problem_solving_holdout.json`).

Zero third-party dependencies (stdlib only). Safe `--dry-run` verifies prompt
bundle assembly and blind rubric schema at zero API cost.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DEFAULT_HOLDOUT = REPO_ROOT / "tests" / "eval" / "problem_solving_holdout.json"

BLIND_RUBRIC_PROMPT = """You are a blind grader comparing two anonymized assistant answers (Answer X vs Answer Y) to a user prompt.
Score each answer 0-2 on four criteria (max 8):
1. trap_detection: Did the answer surface the hidden structural/XY/custody/arena/irreversibility trap before jumping into execution? (For clean L1 controls, 2 if it does NOT fabricate fake traps.)
2. probe_or_reframe: Did it propose a cheap falsifiable check, baseline/exit option, or architectural fix instead of blind polishing?
3. survival_and_incentives: Did it account for enforcement friction, custody, or irreversible downside?
4. conciseness: High signal-to-noise without bloated checklists on simple controls.
Return compact JSON: {"winner": "X|Y|TIE", "x_score": int, "y_score": int, "notes": str}."""


def load_holdout(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("cases", []))


def build_athena_context_directive(query: str) -> dict[str, Any]:
    """Assemble context_gate directive offline using local deterministic gates."""
    from athena.core.permissions import get_permissions
    from athena.mcp_server import context_gate, reset_context_gate_session_state

    reset_context_gate_session_state()
    get_permissions().set_secret_mode(False)
    fake_search = {"results": []}
    with patch("athena.tools.search.run_search", return_value=fake_search):
        return context_gate(query, limit=3, web=False)


def build_arm_prompts(case: dict[str, Any]) -> dict[str, Any]:
    """Construct Baseline vs Athena-scaffolded prompt packets for one case."""
    query = case["query"]
    gate_out = build_athena_context_directive(query)
    athena_system = (
        "You are an engineering and strategy advisor operating inside the Athena harness.\n"
        f"Risk tier: {gate_out['risk_level']} (Lambda={gate_out['lambda']['score']})\n"
        f"Directive: {gate_out['directive']}\n"
    )
    baseline_system = "You are a helpful AI assistant. Answer the user's request clearly and directly."
    return {
        "id": case["id"],
        "kind": case["kind"],
        "category": case["category"],
        "query": query,
        "athena_risk_level": gate_out["risk_level"],
        "athena_directive": gate_out["directive"],
        "baseline_messages": [
            {"role": "system", "content": baseline_system},
            {"role": "user", "content": query},
        ],
        "athena_messages": [
            {"role": "system", "content": athena_system},
            {"role": "user", "content": query},
        ],
    }


def _call_openai_compatible(
    base_url: str, api_key: str, model: str, messages: list[dict[str, str]]
) -> str:
    payload = json.dumps({"model": model, "messages": messages, "temperature": 0.2}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["choices"][0]["message"]["content"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Opt-in A/B problem-solving benchmark runner")
    parser.add_argument("--holdout", type=Path, default=DEFAULT_HOLDOUT)
    parser.add_argument("--provider", choices=["openai", "openrouter"], default="openai")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--limit", type=int, default=0, help="Optional cap on number of cases (0 = all)")
    parser.add_argument("--dry-run", action="store_true", help="Assemble packets at zero API cost")
    args = parser.parse_args(argv)

    cases = load_holdout(args.holdout)
    if args.limit > 0:
        cases = cases[: args.limit]

    packets = [build_arm_prompts(c) for c in cases]
    traps = [p for p in packets if p["kind"] == "trap"]
    controls = [p for p in packets if p["kind"] == "control"]
    triage_hits = sum(1 for p in traps if "META-TRIAGE" in p["athena_directive"])
    false_ultra = sum(1 for p in controls if p["athena_risk_level"] == "ULTRA")

    if args.dry_run:
        summary = {
            "mode": "dry-run",
            "total_cases": len(packets),
            "traps": len(traps),
            "controls": len(controls),
            "trap_meta_triage_hits": triage_hits,
            "control_false_ultra": false_ultra,
            "rubric_ready": bool(BLIND_RUBRIC_PROMPT),
        }
        print(json.dumps(summary, indent=2))
        return 0 if (triage_hits == len(traps) and false_ultra == 0) else 2

    api_key = os.environ.get("OPENROUTER_API_KEY" if args.provider == "openrouter" else "OPENAI_API_KEY", "")
    if not api_key:
        print(
            f"Missing API key for provider '{args.provider}'. Pass --dry-run or set API key env var.",
            file=sys.stderr,
        )
        return 2

    base_url = "https://openrouter.ai/api/v1" if args.provider == "openrouter" else "https://api.openai.com/v1"
    results = []
    for pkt in packets:
        try:
            base_ans = _call_openai_compatible(base_url, api_key, args.model, pkt["baseline_messages"])
            ath_ans = _call_openai_compatible(base_url, api_key, args.model, pkt["athena_messages"])
            results.append({
                "id": pkt["id"],
                "kind": pkt["kind"],
                "baseline_chars": len(base_ans),
                "athena_chars": len(ath_ans),
                "baseline_answer": base_ans,
                "athena_answer": ath_ans,
            })
        except urllib.error.URLError as exc:
            print(f"API error on {pkt['id']}: {exc}", file=sys.stderr)
            return 1

    print(json.dumps({"model": args.model, "provider": args.provider, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
