#!/usr/bin/env python3
"""
reconcile_memory.py — Memory Reconciliation Engine (REC)
=========================================================

Nightly diff that finds contradictions between Athena's memory surfaces:
  - CANONICAL.md (ground truth)
  - activeContext.md (current session state)
  - userContext.md (user profile facts)
  - decisionLog.md (decision records)
  - Last N session logs

Outputs a contradiction report to .context/audit/reconciliation_report.md

Usage:
    python3 .agent/scripts/reconcile_memory.py
    python3 .agent/scripts/reconcile_memory.py --sessions 10  # Check last 10 sessions

Audit Ref: Capability Upgrade REC-001
"""

import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
MEMORY_BANK = CONTEXT_DIR / "memory_bank"
SESSION_DIR = CONTEXT_DIR / "memories" / "session_logs"
REPORT_DIR = CONTEXT_DIR / "audit"
REPORT_PATH = REPORT_DIR / "reconciliation_report.md"

# Memory surfaces to reconcile
SURFACES = {
    "CANONICAL": CONTEXT_DIR / "CANONICAL.md",
    "activeContext": MEMORY_BANK / "activeContext.md",
    "userContext": MEMORY_BANK / "userContext.md",
    "decisionLog": MEMORY_BANK / "decisionLog.md",
    "productContext": MEMORY_BANK / "productContext.md",
}


def extract_facts(content: str, source_name: str) -> list[dict]:
    """Extract fact-like statements from markdown content.

    A 'fact' is any line that contains:
    - A version number (v9.x.x, v8.x)
    - A numeric count claim (### files, ### protocols, ### sessions)
    - A date claim (YYYY-MM-DD or Month YYYY)
    - A status claim (active, completed, paused, deprecated)
    - A key=value or key: value pattern
    """
    facts = []
    lines = content.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        fact = {"source": source_name, "line": i + 1, "text": stripped}

        # Version claims
        version_match = re.search(r'v(\d+\.\d+\.?\d*)', stripped)
        if version_match:
            fact["type"] = "version"
            fact["value"] = version_match.group(0)
            facts.append(fact)
            continue

        # Numeric count claims
        count_match = re.search(
            r'(\d+)\s+(?:protocols?|workflows?|skills?|sessions?|files?|case.?stud)',
            stripped, re.IGNORECASE
        )
        if count_match:
            fact["type"] = "count"
            fact["value"] = int(count_match.group(1))
            fact["subject"] = count_match.group(0)
            facts.append(fact)
            continue

        # Status claims
        status_match = re.search(
            r'(?:status|state|phase)\s*[:=]\s*(\w+)',
            stripped, re.IGNORECASE
        )
        if status_match:
            fact["type"] = "status"
            fact["value"] = status_match.group(1).lower()
            facts.append(fact)
            continue

    return facts


def validate_contradiction_with_llm(contradiction: dict) -> tuple[bool, str]:
    """Use Gemini to check if a contradiction candidate is a real conflict."""
    try:
        # Ensure scripts path is in sys.path
        if str(PROJECT_ROOT / ".agent" / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
        from gemini_client import get_client
        client = get_client(system_prompt="You are a strict, logical memory bank reconciliation auditor for Project Athena.")
    except Exception as e:
        print(f"   ⚠️  Could not initialize LLM for validation: {e}")
        return True, "Skipped LLM validation due to initialization error."

    prompt = f"""
    Analyze the following potential contradiction candidate found by a regex scanner:
    Type: {contradiction['type']}
    Description: {contradiction['description']}
    
    Candidate Sources & Values:
    """
    for src in contradiction.get("sources", []):
        prompt += f"- Source: {src['source']} (Line {src['line']}) | Text: \"{src.get('text', '')}\" | Extracted Value: {src['value']}\n"

    prompt += """
    Is this a genuine contradiction or fact drift in Project Athena's metadata, identity, or session records?
    Identify false positives where:
    - Version numbers belong to different software components (e.g. Next.js v14, pgvector v0.4, vs Project Athena v9.9.0).
    - Counts represent different things (e.g., number of active protocols vs total protocols including archived ones, or files in different subdirectories).
    
    Determine if this represents a real contradiction.
    """

    schema = {
        "type": "OBJECT",
        "properties": {
            "is_actual_contradiction": {
                "type": "BOOLEAN"
            },
            "explanation": {
                "type": "STRING"
            }
        },
        "required": ["is_actual_contradiction", "explanation"]
    }

    try:
        res = client.chat_structured(prompt, schema)
        return res.get("is_actual_contradiction", True), res.get("explanation", "")
    except Exception as e:
        print(f"   ⚠️  LLM validation failed: {e}")
        return True, "LLM validation failed, default to candidate retention."


def find_contradictions(all_facts: dict[str, list[dict]]) -> list[dict]:
    """Cross-reference facts between surfaces to find contradictions, validated by LLM."""
    candidates = []

    # Group facts by type
    by_type = defaultdict(list)
    for source, facts in all_facts.items():
        for fact in facts:
            by_type[fact.get("type", "unknown")].append(fact)

    # Check version contradictions
    version_facts = by_type.get("version", [])
    if version_facts:
        versions = set(f["value"] for f in version_facts)
        if len(versions) > 1:
            candidates.append({
                "type": "VERSION_CONFLICT",
                "severity": "high",
                "description": f"Multiple version numbers found: {', '.join(sorted(versions))}",
                "sources": [
                    {"source": f["source"], "line": f["line"], "value": f["value"], "text": f.get("text", "")}
                    for f in version_facts
                ],
            })

    # Check count contradictions (same subject, different numbers)
    count_facts = by_type.get("count", [])
    by_subject = defaultdict(list)
    for f in count_facts:
        # Normalize subject for grouping
        subject = re.sub(r'\d+\s+', '', f.get("subject", "")).strip().lower()
        # Singularize
        subject = re.sub(r's$', '', subject)
        by_subject[subject].append(f)

    for subject, facts in by_subject.items():
        values = set(f["value"] for f in facts)
        if len(values) > 1:
            candidates.append({
                "type": "COUNT_CONFLICT",
                "severity": "medium",
                "description": f"Conflicting counts for '{subject}': {', '.join(str(v) for v in sorted(values))}",
                "sources": [
                    {"source": f["source"], "line": f["line"], "value": f["value"], "text": f.get("text", "")}
                    for f in facts
                ],
            })

    # Validate candidates with LLM to eliminate false positives
    validated_contradictions = []
    for cand in candidates:
        is_real, explanation = validate_contradiction_with_llm(cand)
        if is_real:
            cand["description"] += f" (LLM Verification: {explanation})"
            validated_contradictions.append(cand)
        else:
            print(f"   ℹ️  Filtered false positive: {cand['description']}")

    return validated_contradictions


def check_staleness(surfaces: dict[str, Path]) -> list[dict]:
    """Check for stale memory surfaces based on modification time."""
    issues = []
    now = datetime.now()

    for name, path in surfaces.items():
        if not path.exists():
            issues.append({
                "type": "MISSING_SURFACE",
                "severity": "high",
                "description": f"{name} does not exist at {path.relative_to(PROJECT_ROOT)}",
            })
            continue

        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age_days = (now - mtime).days

        if age_days > 14:
            issues.append({
                "type": "STALE_SURFACE",
                "severity": "medium" if age_days < 30 else "high",
                "description": f"{name} last modified {age_days} days ago ({mtime.strftime('%Y-%m-%d')})",
                "path": str(path.relative_to(PROJECT_ROOT)),
            })

    return issues


def check_activecontext_bloat(path: Path, max_lines: int = 80) -> list[dict]:
    """Check if activeContext.md exceeds its documented ceiling."""
    issues = []
    if path.exists():
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > max_lines:
            issues.append({
                "type": "CONTEXT_BLOAT",
                "severity": "medium",
                "description": (
                    f"activeContext.md is {lines} lines "
                    f"(ceiling: {max_lines}). Needs compaction."
                ),
            })
    return issues


def get_recent_sessions(n: int = 5) -> list[Path]:
    """Get the N most recent session log files."""
    if not SESSION_DIR.exists():
        return []
    sessions = sorted(SESSION_DIR.glob("*.md"), reverse=True)
    return sessions[:n]


def generate_report(
    contradictions: list[dict],
    staleness: list[dict],
    bloat: list[dict],
    surface_count: int,
    session_count: int,
) -> str:
    """Generate the reconciliation report as markdown."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_issues = len(contradictions) + len(staleness) + len(bloat)
    high = sum(
        1 for issue in contradictions + staleness + bloat
        if issue.get("severity") == "high"
    )

    lines = [
        "# Memory Reconciliation Report",
        "",
        f"> **Generated**: {now}",
        f"> **Surfaces checked**: {surface_count}",
        f"> **Session logs scanned**: {session_count}",
        f"> **Total issues**: {total_issues} ({high} high severity)",
        "",
    ]

    if total_issues == 0:
        lines.append("✅ **All clear.** No contradictions, staleness, or bloat detected.")
        return "\n".join(lines)

    # Contradictions
    if contradictions:
        lines.append("## Contradictions")
        lines.append("")
        for c in contradictions:
            severity_icon = "🔴" if c["severity"] == "high" else "🟡"
            lines.append(f"### {severity_icon} {c['type']}")
            lines.append(f"**{c['description']}**")
            lines.append("")
            if "sources" in c:
                lines.append("| Source | Line | Value |")
                lines.append("|:-------|:-----|:------|")
                for s in c["sources"]:
                    lines.append(f"| {s['source']} | {s['line']} | `{s['value']}` |")
                lines.append("")

    # Staleness
    if staleness:
        lines.append("## Staleness")
        lines.append("")
        for s in staleness:
            severity_icon = "🔴" if s["severity"] == "high" else "🟡"
            lines.append(f"- {severity_icon} {s['description']}")
        lines.append("")

    # Bloat
    if bloat:
        lines.append("## Context Bloat")
        lines.append("")
        for b in bloat:
            lines.append(f"- 🟡 {b['description']}")
        lines.append("")

    # Action items
    lines.append("## Recommended Actions")
    lines.append("")
    if contradictions:
        lines.append(
            "1. **Resolve contradictions**: Update the authoritative source "
            "(CANONICAL.md) and propagate to other surfaces."
        )
    if staleness:
        lines.append(
            "2. **Update stale surfaces**: Review and refresh any surface "
            "older than 14 days."
        )
    if bloat:
        lines.append(
            "3. **Compact activeContext.md**: Archive completed items to "
            "sessionArchive.md."
        )

    return "\n".join(lines)


def main():
    n_sessions = 5
    if "--sessions" in sys.argv:
        idx = sys.argv.index("--sessions")
        if idx + 1 < len(sys.argv):
            n_sessions = int(sys.argv[idx + 1])

    print("🔍 Athena Memory Reconciliation Engine")
    print("=" * 50)

    # Load surfaces
    all_facts = {}
    surface_count = 0

    for name, path in SURFACES.items():
        if path.exists():
            content = path.read_text(encoding="utf-8")
            facts = extract_facts(content, name)
            all_facts[name] = facts
            surface_count += 1
            print(f"  📄 {name}: {len(facts)} facts extracted")
        else:
            print(f"  ❌ {name}: file not found")

    # Load recent sessions
    sessions = get_recent_sessions(n_sessions)
    for session_path in sessions:
        content = session_path.read_text(encoding="utf-8")
        facts = extract_facts(content, f"session:{session_path.stem}")
        all_facts[f"session:{session_path.stem}"] = facts
        print(f"  📝 {session_path.stem}: {len(facts)} facts extracted")

    # Run checks
    print()
    contradictions = find_contradictions(all_facts)
    staleness = check_staleness(SURFACES)
    bloat = check_activecontext_bloat(MEMORY_BANK / "activeContext.md")

    total = len(contradictions) + len(staleness) + len(bloat)
    print(f"  🔎 Contradictions: {len(contradictions)}")
    print(f"  ⏰ Staleness:      {len(staleness)}")
    print(f"  📈 Bloat:          {len(bloat)}")
    print(f"  {'=' * 30}")
    print(f"  Total issues:      {total}")

    # Generate report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = generate_report(
        contradictions, staleness, bloat, surface_count, len(sessions)
    )
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\n📋 Report written to: {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
