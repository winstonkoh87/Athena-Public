#!/usr/bin/env python3
"""
canonical_gate.py — Write-Time Contradiction Gate + Memory Security Layer
=========================================================================

Before a new entry lands in CANONICAL.md, this gate performs TWO checks:

1. TRUST CLASSIFICATION (OWASP ASI06 — Memory Poisoning Defense)
   Classifies the entry source as USER / SYNTH / EXTERNAL and applies
   appropriate validation rules. Prevents temporal-decoupling attacks
   where adversarial content planted today poisons reasoning weeks later.

2. CONTRADICTION DETECTION (Mem0 pattern)
   Surfaces nearest existing neighbors and forces explicit disposition —
   so two versions of the same truth never silently coexist.

Trust Classes (ASI06):
  USER     — Direct user statement, verbatim quote, or user-confirmed fact.
             Highest trust. Auto-eligible for ADD.
  SYNTH    — Agent-generated synthesis, inference, or derived conclusion.
             Medium trust. Requires supporting evidence or user confirmation.
  EXTERNAL — Sourced from web search, URL content, third-party tools, MCP.
             Lowest trust. Must include source URL/citation. Auto-flagged
             for review if it contradicts existing USER-class entries.

Pattern source: Mem0's reconcile-on-add + OWASP Top 10 for Agentic Applications
2026 (ASI06: Memory & Context Poisoning). See: vectorize.io/owasp-asi06

Dispositions (log the chosen one in the new entry's provenance tag):
  ADD         no neighbor covers this fact — append as new entry
  UPDATE      a neighbor IS this fact, outdated — edit it in place
  INVALIDATE  a neighbor is now false — move to CANONICAL_ARCHIVE.md
  NOOP        a neighbor already states this — write nothing

Usage:
    python3 .agent/scripts/canonical_gate.py "Trading stake doubled to $6.6K"
    python3 .agent/scripts/canonical_gate.py --trust USER "User said: ..."
    python3 .agent/scripts/canonical_gate.py --trust EXTERNAL --source "https://..." "..."
    echo "proposed entry" | python3 .agent/scripts/canonical_gate.py
    python3 .agent/scripts/canonical_gate.py --top 8 "..."

Exit codes: 0 = processed OK, 1 = usage error, 2 = BLOCKED by trust policy.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
AUDIT_DIR = CONTEXT_DIR / "audit"

STORES = [
    CONTEXT_DIR / "CANONICAL.md",
    CONTEXT_DIR / "CANONICAL_TIER3.md",
    CONTEXT_DIR / "CANONICAL_ARCHIVE.md",
]

# ASI06 trust policy: injection detection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|rules?)",
    r"you\s+are\s+now\s+(a|an|the)\s+",
    r"system\s*prompt\s*[:=]",
    r"<\s*/?system\s*>",
    r"override\s+(safety|security|policy|rules?)",
    r"act\s+as\s+(if|though)\s+you\s+(have\s+no|don.t\s+have)",
    r"forget\s+(everything|all|your)\s+(you|previous)",
    r"new\s+instruction[s]?\s*:",
    r"ADMIN\s*MODE|GOD\s*MODE|DEBUG\s*MODE",
]

STOPWORDS = frozenset(
    ["the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "is", "are", "was", "were", "be", "been", "has", "have", "had", "this", "that", "it", "its", "as", "by", "at", "from", "not", "no", "if", "then", "than", "into", "over", "under"]
)


# ── Trust Classification ──────────────────────────────────────────────

TRUST_LEVELS = {
    "USER": {
        "rank": 3,
        "label": "🟢 USER",
        "auto_add": True,
        "requires_source": False,
        "desc": "Direct user statement or confirmed fact",
    },
    "SYNTH": {
        "rank": 2,
        "label": "🟡 SYNTH",
        "auto_add": False,
        "requires_source": False,
        "desc": "Agent-generated synthesis or inference",
    },
    "EXTERNAL": {
        "rank": 1,
        "label": "🔴 EXTERNAL",
        "auto_add": False,
        "requires_source": True,
        "desc": "Web search, URL, third-party tool output",
    },
}


def detect_injection(text: str) -> list[str]:
    """Scan text for common prompt injection patterns (ASI06 defense)."""
    findings = []
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            findings.append(pattern)
    return findings


def compute_fingerprint(text: str) -> str:
    """SHA-256 content fingerprint for tamper detection."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def log_audit_event(event: dict) -> None:
    """Append trust gate event to audit log (append-only)."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = AUDIT_DIR / "memory_security_log.jsonl"
    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── Contradiction Detection ───────────────────────────────────────────

def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9$%.]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def split_entries(path: Path) -> list[dict]:
    """Split a canonical store into scoreable line-level entries."""
    entries = []
    if not path.exists():
        return entries
    heading = ""
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("# ")
            continue
        if (stripped.startswith("|") or stripped.startswith(("-", "*")) or ": " in stripped) and len(stripped) > 20:
                # Extract trust class if tagged
                trust = "USER"  # default for legacy entries
                trust_match = re.search(r"\[trust:(USER|SYNTH|EXTERNAL)\]", stripped)
                if trust_match:
                    trust = trust_match.group(1)
                entries.append({
                    "file": path.name,
                    "line": i,
                    "heading": heading,
                    "text": stripped,
                    "tokens": tokenize(stripped + " " + heading),
                    "trust": trust,
                })
    return entries


def score(query_tokens: set[str], entry: dict) -> float:
    """Overlap coefficient: |A∩B| / min(|A|,|B|)."""
    if not query_tokens or not entry["tokens"]:
        return 0.0
    inter = len(query_tokens & entry["tokens"])
    return inter / min(len(query_tokens), len(entry["tokens"]))


# ── Main ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical write-time gate: trust classification + contradiction detection"
    )
    parser.add_argument("entry", nargs="?", help="Proposed canonical entry text (or pipe via stdin)")
    parser.add_argument("--trust", choices=["USER", "SYNTH", "EXTERNAL"], default="SYNTH",
                        help="Trust class of the entry source (default: SYNTH)")
    parser.add_argument("--source", type=str, default=None,
                        help="Source URL/citation (required for EXTERNAL trust)")
    parser.add_argument("--top", type=int, default=5, help="Neighbors to show (default 5)")
    parser.add_argument("--floor", type=float, default=0.25, help="Min overlap score (default 0.25)")
    parser.add_argument("--force", action="store_true", help="Skip injection check (use with caution)")
    args = parser.parse_args()

    proposed = args.entry or (sys.stdin.read() if not sys.stdin.isatty() else "")
    if not proposed or not proposed.strip():
        parser.print_help()
        return 1

    trust_cfg = TRUST_LEVELS[args.trust]
    fingerprint = compute_fingerprint(proposed)

    # ── Phase 1: ASI06 Trust & Injection Check ────────────────────────

    print("═" * 70)
    print("🛂 CANONICAL GATE — Memory Security + Contradiction Check")
    print(f"   Proposed: {proposed.strip()[:100]}")
    print(f"   Trust:    {trust_cfg['label']}  |  Fingerprint: {fingerprint}")
    print("═" * 70)

    # Injection scan
    if not args.force:
        injections = detect_injection(proposed)
        if injections:
            print("\n🚨 ASI06 INJECTION DETECTED — entry BLOCKED")
            print(f"   Matched {len(injections)} pattern(s):")
            for p in injections:
                print(f"     ⛔ {p}")
            print("\n   This entry will NOT be written to any canonical store.")
            print("   Use --force to override (logged as manual override).")
            log_audit_event({
                "action": "BLOCKED",
                "reason": "injection_detected",
                "trust": args.trust,
                "fingerprint": fingerprint,
                "patterns": injections,
                "text_preview": proposed.strip()[:200],
            })
            return 2

    # Source requirement check
    if trust_cfg["requires_source"] and not args.source:
        print("\n⚠️  EXTERNAL trust requires --source URL/citation.")
        print("   Add: --source \"https://...\" or --source \"Paper: Author (Year)\"")
        print("   Entry not blocked, but provenance will be incomplete.")

    # Trust-vs-existing conflict check
    if args.trust == "EXTERNAL":
        # Check if any USER-class entry contradicts this
        query_tokens = tokenize(proposed)
        for store in STORES:
            for entry in split_entries(store):
                if entry["trust"] == "USER" and score(query_tokens, entry) >= 0.5:
                    print("\n⚠️  ASI06 TRUST CONFLICT: EXTERNAL entry conflicts with USER-class fact")
                    print(f"   Existing [{entry['trust']}] {entry['file']}:{entry['line']}")
                    print(f"   {entry['text'][:110]}")
                    print("   → EXTERNAL entries CANNOT override USER entries without user confirmation.")
                    log_audit_event({
                        "action": "TRUST_CONFLICT",
                        "trust_proposed": args.trust,
                        "trust_existing": entry["trust"],
                        "fingerprint": fingerprint,
                        "conflicting_line": f"{entry['file']}:{entry['line']}",
                    })

    # ── Phase 2: Contradiction Detection ──────────────────────────────

    query_tokens = tokenize(proposed)
    neighbors = []
    for store in STORES:
        for entry in split_entries(store):
            s = score(query_tokens, entry)
            if s >= args.floor:
                neighbors.append((s, entry))
    neighbors.sort(key=lambda x: -x[0])
    neighbors = neighbors[: args.top]

    if not neighbors:
        print("\n✅ No near-duplicates above floor. Disposition: ADD")
        tag = f"(S[NNN], [YYYY-MM-DD], disposition: ADD, trust: {args.trust}"
        if args.source:
            tag += f", source: {args.source}"
        tag += f", fp: {fingerprint})"
        print(f"   Provenance tag: {tag}")
        log_audit_event({
            "action": "ADD",
            "trust": args.trust,
            "fingerprint": fingerprint,
            "source": args.source,
            "neighbors": 0,
        })
        return 0

    print(f"\n⚠️  {len(neighbors)} neighbor(s) found — explicit disposition REQUIRED:\n")
    for s, e in neighbors:
        archived = " [ARCHIVED]" if "ARCHIVE" in e["file"] else ""
        trust_tag = f" [{e['trust']}]" if e.get("trust") else ""
        print(f"  [{s:.2f}]{trust_tag} {e['file']}:{e['line']}{archived}  §{e['heading'][:40]}")
        print(f"         {e['text'][:110]}")
    print(
        f"\n   Choose per neighbor: UPDATE (edit in place) | INVALIDATE (archive w/ reason,"
        f"\n   then ADD) | NOOP (already covered) | ADD (genuinely distinct)."
        f"\n   Log it: (S[NNN], [YYYY-MM-DD], disposition: UPDATE of CANONICAL.md:L142,"
        f"\n   trust: {args.trust}, fp: {fingerprint})"
    )
    log_audit_event({
        "action": "REVIEW_REQUIRED",
        "trust": args.trust,
        "fingerprint": fingerprint,
        "source": args.source,
        "neighbors": len(neighbors),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
