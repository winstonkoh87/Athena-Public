#!/usr/bin/env python3
"""
semantic_audit.py — Track semantic search compliance per session.

Usage:
    # Log a search call (called by smart_search.py)
    python3 semantic_audit.py --log-search "query terms"
    
    # Log a response checkpoint (called by quicksave.py)
    python3 semantic_audit.py --log-response "summary"
    
    # Get compliance report (called by shutdown.py)
    python3 semantic_audit.py --compliance
    
    # Reset audit log (called by boot.py)
    python3 semantic_audit.py --reset

Protocol: §0.7.1 Semantic Search (MANDATORY)
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
AUDIT_LOG = WORKSPACE / ".context" / ".semantic_audit_log.json"


def _load_log() -> dict:
    """Load audit log from disk."""
    if not AUDIT_LOG.exists():
        return {"searches": [], "responses": [], "session_start": None}
    try:
        return json.loads(AUDIT_LOG.read_text())
    except (json.JSONDecodeError, Exception):
        return {"searches": [], "responses": [], "session_start": None}


def _save_log(data: dict):
    """Save audit log to disk."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG.write_text(json.dumps(data, indent=2))


def log_search(query: str):
    """Log a semantic search call."""
    data = _load_log()
    data["searches"].append({
        "timestamp": datetime.now().isoformat(),
        "query": query[:200]  # Truncate for storage
    })
    _save_log(data)


def log_response(summary: str) -> bool:
    """
    Log a response checkpoint.
    Returns True if a search was logged since last response (compliant).
    Returns False if no search was logged (violation).
    """
    data = _load_log()
    
    # Check if any search exists since last response
    last_response_time = None
    if data["responses"]:
        last_response_time = data["responses"][-1]["timestamp"]
    
    # Count searches after last response
    recent_searches = 0
    for s in data["searches"]:
        if last_response_time is None or s["timestamp"] > last_response_time:
            recent_searches += 1
    
    is_compliant = recent_searches > 0
    
    data["responses"].append({
        "timestamp": datetime.now().isoformat(),
        "summary": summary[:200],
        "had_search": is_compliant
    })
    _save_log(data)
    
    return is_compliant


def get_compliance_rate() -> tuple[int, int, float]:
    """
    Calculate compliance rate for the session.
    Returns: (compliant_responses, total_responses, rate_percent)
    """
    data = _load_log()
    
    total = len(data["responses"])
    if total == 0:
        return (0, 0, 100.0)
    
    compliant = sum(1 for r in data["responses"] if r.get("had_search", False))
    rate = (compliant / total) * 100
    
    return (compliant, total, rate)


def reset_audit():
    """Reset audit log for new session."""
    data = {
        "searches": [],
        "responses": [],
        "session_start": datetime.now().isoformat()
    }
    _save_log(data)
    print("✅ Semantic audit log reset")


def print_compliance_report():
    """Print session compliance report."""
    compliant, total, rate = get_compliance_rate()
    
    if total == 0:
        print("📊 Semantic Compliance: No responses logged this session")
        return
    
    emoji = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
    print(f"{emoji} Semantic Compliance: {compliant}/{total} responses ({rate:.0f}%)")
    
    # List violations
    data = _load_log()
    violations = [r for r in data["responses"] if not r.get("had_search", False)]
    if violations:
        print(f"   Violations: {len(violations)}")
        for v in violations[-3:]:  # Show last 3
            print(f"   - {v['timestamp'][:16]}: {v['summary'][:50]}...")


def main():
    if len(sys.argv) < 2:
        print("Usage: semantic_audit.py --log-search|--log-response|--compliance|--reset")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "--log-search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "unknown"
        log_search(query)
    
    elif cmd == "--log-response":
        summary = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "unknown"
        is_compliant = log_response(summary)
        if not is_compliant:
            print("⚠️ COMPLIANCE VIOLATION: No semantic search before this response (§0.7.1)")
    
    elif cmd == "--compliance":
        print_compliance_report()
    
    elif cmd == "--reset":
        reset_audit()
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
