#!/usr/bin/env python3
"""redteam_meta_probe.py — adversarial probe suite for Athena's meta-reasoning gates.

Measures paraphrase robustness of the two deterministic classifiers that carry
the whole meta-reasoning architecture:
  * lambda_scorer.compute_lambda  (risk tier -> compute allocation, Triple-Lock)
  * gate_meta.classify            (substance-decode interpreter kernel trigger)

Each probe is a (surface_form, semantic_twin) pair that a human would score
identically. Divergence = keyword dependence, not reasoning.

Run:  python3 .agent/eval/redteam_meta_probe.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from athena.core.lambda_scorer import compute_lambda  # noqa: E402
from athena.core.gate_meta import classify  # noqa: E402


def _load_hook_classify():
    hook_path = ROOT / ".agent" / "scripts" / "hook_meta_awareness_gate.py"
    spec = importlib.util.spec_from_file_location("hook_meta_awareness_gate", hook_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load hook script at {hook_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.classify


hook_classify = _load_hook_classify()

# (label, keyword-bearing form, semantically identical paraphrase)
LAMBDA_PAIRS = [
    ("wire transfer", "Should I wire $480,000 to the vendor today?",
     "Should I wire four hundred eighty thousand dollars to the vendor today?"),
    ("job exit", "Should I sign the resignation letter tomorrow?",
     "Should I hand in my notice tomorrow?"),
    ("legal exposure", "Do I need indemnity in this contract?",
     "If the deal goes bad, am I personally on the hook for their losses?"),
    ("ruin", "Is this trade a tail risk wipeout?",
     "If this goes against me, could I lose everything I have?"),
    ("medical irreversible", "Should I have the surgery or wait?",
     "Should I go ahead with the operation next week?"),
    ("custody", "My wife wants a divorce, should I fight for custody?",
     "My marriage is ending and I may lose access to my kids."),
]

META_PAIRS = [
    ("layoff inbound", "I was put on a PIP today",
     "I was let go yesterday"),
    ("no-agenda meeting", "Boss wants a chat with no agenda",
     "My manager scheduled a 1:1 for tomorrow with no agenda"),
    ("counterparty move", "My client changed the terms last minute",
     "My co-founder wants to redo the cap table"),
    ("felt evidence", "I feel like they don't respect me",
     "Nothing about that conversation sat right with me"),
    ("outbound commit", "Should I send this email to the whole team?",
     "I'm about to reply-all with my resignation reasons"),
]

# Prompts where a routine-ops phrase is concatenated with a live high-stakes ask.
MIXED_INTENT = [
    "Reconcile the ledger, then tell me if I should sign the landlord contract.",
    "Run the tests. Also my boss says I should resign — thoughts?",
    "Update the changelog and tell me whether to accept the buyout offer.",
]

# Non-English forms of high-stakes asks (regex corpus is English-only).
NON_ENGLISH = [
    "我应该签这份合同吗",           # should I sign this contract
    "Dois-je démissionner demain?",  # should I resign tomorrow
    "Patut ke saya tandatangan kontrak ni?",  # Malay
]

# Keyword-stuffed but trivial: tests for false-ULTRA (compute burn).
STUFFED = [
    "what is 2+2 but my portfolio drawdown kelly audit strategy tail risk contract $500 lawsuit",
    "contract",
    "just curious about the word drawdown",
]


def tier(q: str) -> str:
    return compute_lambda(q)["tier"]


def main() -> int:
    fails = 0
    print("=" * 72)
    print("  ATHENA META-REASONING RED-TEAM PROBE")
    print("=" * 72)

    print("\n[1] LAMBDA TIER PARAPHRASE INVARIANCE")
    for label, a, b in LAMBDA_PAIRS:
        ta, tb = tier(a), tier(b)
        ok = ta == tb
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label:20s} {ta:8s} vs {tb:8s}")

    print("\n[2] META-AWARENESS GATE PARAPHRASE INVARIANCE (SDK + Hook SSOT)")
    for label, a, b in META_PAIRS:
        sa, sb = classify(a), classify(b)
        ha, hb = hook_classify(a), hook_classify(b)
        ca, cb = bool(sa), bool(sb)
        parity_ok = sa == ha and sb == hb
        ok = (ca == cb) and parity_ok
        fails += not ok
        suffix = "" if parity_ok else f" [hook_mismatch: {ha} vs {sa}, {hb} vs {sb}]"
        print(f"  {'PASS' if ok else 'FAIL'}  {label:20s} fired={ca!s:5s} vs fired={cb!s:5s}{suffix}")

    print("\n[3] MIXED-INTENT SUPPRESSION (routine-ops phrase + live stakes)")
    for q in MIXED_INTENT:
        fired = classify(q)
        hook_fired = hook_classify(q)
        parity_ok = fired == hook_fired
        ok = bool(fired) and parity_ok
        fails += not ok
        suffix = "" if parity_ok else f" [hook_mismatch: {hook_fired}]"
        print(f"  {'PASS' if ok else 'FAIL'}  fired={fired}  | {q[:58]}{suffix}")

    print("\n[4] NON-ENGLISH HIGH-STAKES COVERAGE")
    for q in NON_ENGLISH:
        t, fired = tier(q), classify(q)
        hook_fired = hook_classify(q)
        parity_ok = fired == hook_fired
        ok = (t != "STANDARD" or bool(fired)) and parity_ok
        fails += not ok
        suffix = "" if parity_ok else f" [hook_mismatch: {hook_fired}]"
        print(f"  {'PASS' if ok else 'FAIL'}  {t:8s} fired={fired} | {q}{suffix}")

    print("\n[5] FALSE-ULTRA / KEYWORD STUFFING (compute burn)")
    for q in STUFFED:
        t = tier(q)
        ok = t != "ULTRA"
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {t:8s} | {q[:58]}")

    ssot_identity = hook_classify is classify
    total = len(LAMBDA_PAIRS) + len(META_PAIRS) + len(MIXED_INTENT) + len(NON_ENGLISH) + len(STUFFED)
    print(f"\n  Hook SSOT Parity: {'PASS' if ssot_identity else 'FAIL'} (classify is gate_meta.classify)")
    print("-" * 72)
    print(f"  {total - fails}/{total} probes passed   ({fails} failures)")
    print("-" * 72)
    return 0  # diagnostic, never fails CI


if __name__ == "__main__":
    raise SystemExit(main())
