#!/usr/bin/env python3
"""
harvest_check.py — Pre-close session audit for §0.7 Auto-Documentation enforcement.

Scans current session log for:
1. Placeholder content (unharvested insights)
2. Insight patterns that may not have been filed to case_studies/protocols

Usage: python3 .agent/scripts/harvest_check.py

Runs as part of /end workflow.
"""

import os
import re
import subprocess
import glob
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
SESSION_LOGS_DIR = WORKSPACE / ".context" / "memories" / "session_logs"

# Patterns that indicate unharvested/placeholder content
PLACEHOLDER_PATTERNS = [
    "**Insight**: ...",
    "**Decision**: ...",
    "**Pattern**: ...",
    "*   **Insight**: ...",
    "*   **Decision**: ...",
    "- **Insight**: ...",
    "- **Decision**: ...",
    "- **Pattern**: ...",
    "TODO:",
    "PLACEHOLDER",
]

# Insight detection patterns (suggests documentable content)
INSIGHT_PATTERNS = [
    r"validates?\s+(the\s+)?case\s+study",
    r"confirms?\s+(the\s+)?pattern",
    r"new\s+(pattern|insight|evidence|data)",
    r"key\s+insight",
    r"this\s+proves",
    r"real[\s-]?data",
    r"live\s+data",
    r"testimony",
    r"validates?\s+section",
    r"structural\s+pattern",
    r"isomorphic\s+to",
    r"case\s+study\s+validation",
    r"protocol\s+violation",
    r"discovered\s+that",
    r"realized\s+that",
    r"platform\s+feudalism",
    r"turkey\s+problem",
    r"law\s+#\d",
]

# Filing indicators (suggests already documented)
FILING_PATTERNS = [
    r"updated.*\.md",
    r"committed",
    r"filed\s+to",
    r"appended\s+to",
    r"created.*protocol",
    r"added\s+to\s+case",
    r"documented\s+in",
    r"wrote\s+to",
    r"git\s+commit",
    r"case_grab_driver",
    r"\[x\]",  # Checked checkbox
]


def get_latest_session() -> Path | None:
    """Get the most recent session log file."""
    if not SESSION_LOGS_DIR.exists():
        return None
    
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md$")
    
    logs = []
    for f in SESSION_LOGS_DIR.glob("*-session-*.md"):
        match = pattern.match(f.name)
        if match:
            date_str, session_num = match.groups()
            logs.append((date_str, int(session_num), f))
    
    if not logs:
        return None
    
    logs.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return logs[0][2]


def get_recent_commits(hours: int = 12) -> list[str]:
    """Get git commit messages from the last N hours."""
    try:
        since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--all"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=10
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def check_for_placeholders(content: str) -> list[dict]:
    """Check if session log has placeholder content."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in line:
                issues.append({
                    "type": "placeholder",
                    "line": i,
                    "content": line.strip()[:80]
                })
                break
    return issues


def scan_for_insights(content: str) -> list[dict]:
    """Scan content for insight patterns that may need documentation."""
    insights = []
    lines = content.split("\n")
    
    for i, line in enumerate(lines, 1):
        line_lower = line.lower()
        for pattern in INSIGHT_PATTERNS:
            if re.search(pattern, line_lower):
                insights.append({
                    "type": "insight",
                    "line": i,
                    "content": line.strip()[:80]
                })
                break  # One match per line
    
    return insights


def check_if_filed(insight: dict, content: str) -> bool:
    """Check if an insight appears to have corresponding documentation action."""
    lines = content.split("\n")
    insight_line = insight["line"]
    
    # Look at following 20 lines for filing indicators
    following = "\n".join(lines[insight_line:insight_line + 20]).lower()
    
    for pattern in FILING_PATTERNS:
        if re.search(pattern, following):
            return True
    
    return False


def main():
    print("\n" + "="*60)
    print("🌾 HARVEST CHECK — §0.7 Auto-Documentation Enforcement")
    print("="*60 + "\n")
    
    # 1. Get current session log
    log_path = get_latest_session()
    if not log_path:
        print("❌ No session log found.")
        return 1
    
    print(f"📋 Scanning: {log_path.name}")
    content = log_path.read_text(encoding="utf-8")
    
    exit_code = 0
    
    # 2. Check for placeholders
    placeholders = check_for_placeholders(content)
    if placeholders:
        print(f"\n⚠️  PLACEHOLDER CONTENT ({len(placeholders)} items):")
        for item in placeholders[:5]:
            print(f"   L{item['line']}: {item['content']}")
        if len(placeholders) > 5:
            print(f"   ... and {len(placeholders) - 5} more")
        print("   📝 Fill in placeholders before closing session.\n")
        exit_code = 1
    
    # 3. Scan for unfiled insights
    insights = scan_for_insights(content)
    
    if insights:
        unfiled = []
        filed = []
        
        for insight in insights:
            if check_if_filed(insight, content):
                filed.append(insight)
            else:
                unfiled.append(insight)
        
        if filed:
            print(f"✅ Filed Insights ({len(filed)}):")
            for item in filed[:3]:
                print(f"   L{item['line']}: {item['content']}...")
            if len(filed) > 3:
                print(f"   ... and {len(filed) - 3} more")
            print()
        
        if unfiled:
            print(f"⚠️  POTENTIALLY UNFILED INSIGHTS ({len(unfiled)}):")
            for item in unfiled[:10]:
                print(f"   L{item['line']}: {item['content']}...")
            if len(unfiled) > 10:
                print(f"   ... and {len(unfiled) - 10} more")
            print("\n   📝 Review above — file to case_studies/ or protocols/ if valid.")
            print("   📝 If already filed, you can safely proceed.\n")
            # Don't fail on this — it's a warning, not a blocker
    else:
        print("✅ No insight patterns detected in session.\n")
    
    if not placeholders:
        print("✅ No placeholders found.\n")
    
    # 4. Show recent commits for cross-reference
    commits = get_recent_commits(hours=12)
    if commits and commits[0]:  # Check not empty
        print(f"📦 Recent Commits ({len(commits)}):")
        for commit in commits[:5]:
            if commit:
                print(f"   {commit}")
        if len(commits) > 5:
            print(f"   ... and {len(commits) - 5} more")
        print()
    
    # 5. Final verdict
    print("="*60)
    if exit_code == 0:
        print("✅ Harvest check PASSED. Session ready to close.")
    else:
        print("⚠️  Harvest check found issues. Review before closing.")
    print("="*60 + "\n")
    
    return exit_code


if __name__ == "__main__":
    exit(main())
