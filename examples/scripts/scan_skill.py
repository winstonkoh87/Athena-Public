#!/usr/bin/env python3
"""
scan_skill.py — Automated Skill/Protocol Safety Scanner

Stolen from: anthropics/knowledge-work-plugins `.github/policy/prompt.md` + `schema.json`
Adapted for: Athena workspace local skill vetting

Usage:
    python3 .agent/scripts/scan_skill.py <path-to-skill-or-protocol>
    python3 .agent/scripts/scan_skill.py --all          # Scan all skills
    python3 .agent/scripts/scan_skill.py --recent 7     # Scan skills modified in last 7 days
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]  # .agent/scripts/ → root
SKILLS_DIR = WORKSPACE_ROOT / ".agent" / "skills"
PROTOCOLS_DIR = WORKSPACE_ROOT / ".agent" / "skills" / "protocols"

# Patterns that indicate potential safety concerns
COERCIVE_PATTERNS = [
    r"ignore\s+(all\s+)?other\s+instructions",
    r"ignore\s+previous\s+(instructions|context|rules)",
    r"always\s+run\s+(me|this)\s+first",
    r"override\s+(all|any)\s+(safety|security|rules)",
    r"disregard\s+(all|any|previous)",
    r"you\s+must\s+obey",
    r"do\s+not\s+question",
    r"bypass\s+(safety|security|filters)",
    r"pretend\s+you\s+are",
    r"act\s+as\s+if\s+you\s+have\s+no\s+(rules|constraints)",
]

NETWORK_CALL_PATTERNS = [
    r"\bfetch\b\(",
    r"\baxios\b",
    r"\bhttp\.request\b",
    r"\bhttps\.request\b",
    r"\brequests\.(get|post|put|delete|patch)\b",
    r"\burllib\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bsocket\b",
    r"\bXMLHttpRequest\b",
    r"\bnode-fetch\b",
    r"\bhttpx\b",
    r"\baiohttp\b",
]

DATA_EXFIL_PATTERNS = [
    r"(send|post|upload|transmit|exfiltrate)\s+.*(data|file|secret|key|token|password)",
    r"base64\.(encode|b64encode)",
    r"os\.environ\[",
    r"subprocess\.(call|run|Popen)",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
]

UNDISCLOSED_BEHAVIOR_PATTERNS = [
    r"silently",
    r"without\s+(the\s+)?user('s)?\s+(knowledge|awareness|consent)",
    r"hidden",
    r"covert",
    r"background\s+(task|process|thread)",
]


# ── Scanner ────────────────────────────────────────────────────────────

class SkillScanResult:
    def __init__(self, path: str):
        self.path = path
        self.passes = True
        self.violations = []
        self.warnings = []
        self.may_make_external_network_calls = False
        self.has_coercive_instructions = False
        self.has_undisclosed_behavior = False
        self.has_data_exfil_risk = False
        self.description_present = False
        self.context_trigger_present = False

    def add_violation(self, msg: str):
        self.violations.append(msg)
        self.passes = False

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "passes": self.passes,
            "violations": self.violations,
            "warnings": self.warnings,
            "may_make_external_network_calls": self.may_make_external_network_calls,
            "has_coercive_instructions": self.has_coercive_instructions,
            "has_undisclosed_behavior": self.has_undisclosed_behavior,
            "has_data_exfil_risk": self.has_data_exfil_risk,
            "description_present": self.description_present,
            "context_trigger_present": self.context_trigger_present,
        }

    def summary(self) -> str:
        status = "✅ PASS" if self.passes else "❌ FAIL"
        lines = [f"{status}  {self.path}"]
        for v in self.violations:
            lines.append(f"  🚫 {v}")
        for w in self.warnings:
            lines.append(f"  ⚠️  {w}")
        return "\n".join(lines)


def scan_file(filepath: Path) -> SkillScanResult:
    """Scan a single SKILL.md or protocol file."""
    result = SkillScanResult(str(filepath.relative_to(WORKSPACE_ROOT)))

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        result.add_violation(f"Cannot read file: {e}")
        return result

    content_lower = content.lower()

    # ── Part 1: Frontmatter checks ──

    # Check for description
    if re.search(r'^description:', content, re.MULTILINE):
        result.description_present = True
    else:
        result.add_warning("Missing 'description' in frontmatter")

    # Check for context_trigger
    if re.search(r'^context_trigger:', content, re.MULTILINE):
        result.context_trigger_present = True

    # ── Part 2: Coercive instructions ──

    for pattern in COERCIVE_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            result.has_coercive_instructions = True
            result.add_violation(f"Coercive instruction detected: pattern '{pattern}' matched")

    # ── Part 3: Network call indicators ──

    for pattern in NETWORK_CALL_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            result.may_make_external_network_calls = True
            result.add_warning(f"Potential network call: pattern '{pattern}' matched")

    # ── Part 4: Data exfiltration risk ──

    for pattern in DATA_EXFIL_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            result.has_data_exfil_risk = True
            result.add_violation(f"Data exfiltration risk: pattern '{pattern}' matched")

    # ── Part 5: Undisclosed behavior ──

    for pattern in UNDISCLOSED_BEHAVIOR_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            result.has_undisclosed_behavior = True
            result.add_warning(f"Potential undisclosed behavior: pattern '{pattern}' matched")

    # ── Part 6: Size sanity check ──

    line_count = content.count("\n")
    if line_count > 500:
        result.add_warning(f"Large file ({line_count} lines) — review for unnecessary complexity")

    # ── Part 7: Embedded code block checks ──

    code_blocks = re.findall(r'```(?:python|javascript|bash|sh|js|py)\n(.*?)```', content, re.DOTALL)
    for block in code_blocks:
        for pattern in DATA_EXFIL_PATTERNS:
            if re.search(pattern, block.lower()):
                result.has_data_exfil_risk = True
                result.add_violation(f"Data exfiltration risk in code block: '{pattern}'")

    return result


def find_skill_files(root: Path, recent_days: int = None) -> list[Path]:
    """Find all SKILL.md and protocol .md files."""
    files = []

    # Skills
    if (root / ".agent" / "skills").exists():
        for f in (root / ".agent" / "skills").rglob("SKILL.md"):
            files.append(f)

    # Protocols
    if (root / ".agent" / "skills" / "protocols").exists():
        for f in (root / ".agent" / "skills" / "protocols").rglob("*.md"):
            files.append(f)

    # Filter by modification time if requested
    if recent_days is not None:
        cutoff = datetime.now() - timedelta(days=recent_days)
        files = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime) > cutoff]

    return sorted(files)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Skill/Protocol Safety Scanner")
    parser.add_argument("path", nargs="?", help="Path to a specific file to scan")
    parser.add_argument("--all", action="store_true", help="Scan all skills and protocols")
    parser.add_argument("--recent", type=int, metavar="DAYS", help="Scan files modified in last N days")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.path:
        filepath = Path(args.path).resolve()
        if not filepath.exists():
            print(f"❌ File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        files = [filepath]
    elif args.all:
        files = find_skill_files(WORKSPACE_ROOT)
    elif args.recent:
        files = find_skill_files(WORKSPACE_ROOT, recent_days=args.recent)
    else:
        parser.print_help()
        sys.exit(1)

    results = []
    pass_count = 0
    fail_count = 0

    for f in files:
        result = scan_file(f)
        results.append(result)
        if result.passes:
            pass_count += 1
        else:
            fail_count += 1

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Skill Safety Scanner — {len(results)} files scanned")
        print(f"  ✅ {pass_count} passed  |  ❌ {fail_count} failed")
        print(f"{'='*60}\n")

        for r in results:
            print(r.summary())
            print()

    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
