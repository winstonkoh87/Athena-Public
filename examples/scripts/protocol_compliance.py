#!/usr/bin/env python3
"""
protocol_compliance.py — Track autonomic behavior compliance per session.

Logs protocol violations to PROTOCOL_VIOLATIONS.md and surfaces stats at /end.

Usage:
    python3 protocol_compliance.py log <violation_type> <details>
    python3 protocol_compliance.py report
    python3 protocol_compliance.py reset

Violation Types:
    - semantic_search: §0.7.1 - Failed to run semantic search
    - quicksave: §0.6 - Failed to quicksave after exchange
    - auto_doc: §0.7 - Failed to file insight/pattern
    - lambda: §0.5.1 - Missing Λ indicator
    - tags: Response Enrichment - Missing #tags
    - citation: Law #5 - Orphan statistic

Integrates with quicksave.py for automatic tracking.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
VIOLATIONS_FILE = WORKSPACE / ".context" / "PROTOCOL_VIOLATIONS.md"
VIOLATIONS_JSON = WORKSPACE / ".context" / "protocol_violations.json"

# Violation type metadata
VIOLATION_TYPES = {
    "semantic_search": {
        "protocol": "§0.7.1",
        "description": "Semantic search not run before response",
        "severity": "high"
    },
    "quicksave": {
        "protocol": "§0.6",
        "description": "Quicksave not executed after exchange",
        "severity": "high"
    },
    "auto_doc": {
        "protocol": "§0.7",
        "description": "Insight detected but not filed",
        "severity": "medium"
    },
    "lambda": {
        "protocol": "§0.5.1",
        "description": "Λ latency indicator missing",
        "severity": "low"
    },
    "tags": {
        "protocol": "Response Enrichment",
        "description": "Tags footer missing",
        "severity": "low"
    },
    "citation": {
        "protocol": "Law #5",
        "description": "Orphan statistic without source",
        "severity": "medium"
    }
}


def load_violations() -> dict:
    """Load current violations from JSON."""
    if VIOLATIONS_JSON.exists():
        try:
            return json.loads(VIOLATIONS_JSON.read_text())
        except json.JSONDecodeError:
            return {"violations": [], "session_start": None}
    return {"violations": [], "session_start": None}


def save_violations(data: dict):
    """Save violations to JSON."""
    VIOLATIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    VIOLATIONS_JSON.write_text(json.dumps(data, indent=2))


def log_violation(violation_type: str, details: str = ""):
    """Log a protocol violation."""
    if violation_type not in VIOLATION_TYPES:
        print(f"❌ Unknown violation type: {violation_type}")
        print(f"   Valid types: {', '.join(VIOLATION_TYPES.keys())}")
        return
    
    data = load_violations()
    
    if data["session_start"] is None:
        data["session_start"] = datetime.now().isoformat()
    
    violation = {
        "type": violation_type,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        **VIOLATION_TYPES[violation_type]
    }
    
    data["violations"].append(violation)
    save_violations(data)
    
    print(f"📝 Logged: {violation_type} ({VIOLATION_TYPES[violation_type]['protocol']})")


def generate_report() -> str:
    """Generate compliance report."""
    data = load_violations()
    violations = data.get("violations", [])
    
    if not violations:
        return "✅ No protocol violations this session. Perfect compliance."
    
    # Count by type
    counts = {}
    for v in violations:
        t = v["type"]
        counts[t] = counts.get(t, 0) + 1
    
    # Count by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for v in violations:
        sev = v.get("severity", "low")
        severity_counts[sev] += 1
    
    report = []
    report.append("\n" + "="*60)
    report.append("📊 PROTOCOL COMPLIANCE REPORT")
    report.append("="*60 + "\n")
    
    report.append(f"Session Start: {data.get('session_start', 'Unknown')}")
    report.append(f"Total Violations: {len(violations)}\n")
    
    # By severity
    report.append("By Severity:")
    if severity_counts["high"] > 0:
        report.append(f"  🔴 High: {severity_counts['high']}")
    if severity_counts["medium"] > 0:
        report.append(f"  🟡 Medium: {severity_counts['medium']}")
    if severity_counts["low"] > 0:
        report.append(f"  🟢 Low: {severity_counts['low']}")
    report.append("")
    
    # By type
    report.append("By Type:")
    for vtype, count in sorted(counts.items(), key=lambda x: -x[1]):
        meta = VIOLATION_TYPES.get(vtype, {})
        protocol = meta.get("protocol", "Unknown")
        report.append(f"  {vtype}: {count} ({protocol})")
    report.append("")
    
    # Recent violations (last 5)
    report.append("Recent Violations:")
    for v in violations[-5:]:
        ts = v["timestamp"].split("T")[1][:5]
        report.append(f"  [{ts}] {v['type']}: {v.get('details', '')[:50]}")
    
    report.append("\n" + "="*60)
    
    return "\n".join(report)


def reset_violations():
    """Reset violations for new session."""
    if VIOLATIONS_JSON.exists():
        VIOLATIONS_JSON.unlink()
    print("✅ Violations reset for new session.")


def update_markdown_log():
    """Append session summary to PROTOCOL_VIOLATIONS.md."""
    data = load_violations()
    violations = data.get("violations", [])
    
    if not violations:
        return
    
    # Count by type
    counts = {}
    for v in violations:
        t = v["type"]
        counts[t] = counts.get(t, 0) + 1
    
    # Build summary line
    session_date = datetime.now().strftime("%Y-%m-%d")
    summary_parts = [f"{t}:{c}" for t, c in counts.items()]
    summary = f"| {session_date} | {len(violations)} | {', '.join(summary_parts)} |"
    
    # Append to markdown file
    if not VIOLATIONS_FILE.exists():
        header = """# Protocol Violations Log

> **Purpose**: Track protocol compliance across sessions for calibration.

| Date | Count | Breakdown |
|------|-------|-----------|
"""
        VIOLATIONS_FILE.write_text(header)
    
    with open(VIOLATIONS_FILE, "a") as f:
        f.write(summary + "\n")
    
    print(f"📝 Logged to {VIOLATIONS_FILE.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 protocol_compliance.py <log|report|reset> [args]")
        print("\nCommands:")
        print("  log <type> [details]  - Log a violation")
        print("  report                - Show session report")
        print("  reset                 - Reset for new session")
        print(f"\nViolation types: {', '.join(VIOLATION_TYPES.keys())}")
        return
    
    command = sys.argv[1].lower()
    
    if command == "log":
        if len(sys.argv) < 3:
            print("❌ Missing violation type")
            return
        vtype = sys.argv[2]
        details = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        log_violation(vtype, details)
    
    elif command == "report":
        print(generate_report())
        # Also update the markdown log
        update_markdown_log()
    
    elif command == "reset":
        reset_violations()
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
