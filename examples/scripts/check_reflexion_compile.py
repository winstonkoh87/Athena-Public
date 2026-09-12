#!/usr/bin/env python3
"""
check_reflexion_compile.py — P0: Solved-to-Skill Reflexion Router.
Scans session logs for [REFLEXION] entries containing reusable rules,
detects candidate owning skills, and prompts for compilation.
"""

import argparse
import re
import sys
from pathlib import Path

RULE_PATTERN = re.compile(
    r"\b(Rule of [A-Za-z0-9_\- ]+|The \d+-Filter Gate|The \d+-Gate [A-Za-z0-9_\- ]+|\d+-Filter Gate|\d+-Gate Partnership|The [A-Za-z0-9_\- ]+ Rule|[A-Za-z0-9_\- ]+ Law)\b",
    re.IGNORECASE,
)

# Skill heuristic keyword routing
SKILL_MAP = {
    "academic-delivery": ["capstone", "assignment", "brief", "rubric", "presenter", "examiner", "capping"],
    "trading-risk-gate": ["trade", "drawdown", "fill", "pnl", "lot", "stop-loss", "spread"],
    "client-pricing": ["pricing", "quote", "fee", "client", "negotiation", "discount"],
    "spec-driven-dev": ["spec", "vibe-coding", "design doc", "requirements gathering"],
    "social-physics-filter": ["relational", "boundary", "friendship", "callout", "contract"],
}


def find_owning_skill(snippet: str) -> str:
    s = snippet.lower()
    for skill, keywords in SKILL_MAP.items():
        if any(k in s for k in keywords):
            return skill
    return "general"


def scan_file(path: Path) -> list:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    candidates = []
    for match in re.finditer(r"\[REFLEXION\](.*?)(?=\n\n|\n>|\Z)", text, re.DOTALL):
        snippet = match.group(1).strip()
        rules = RULE_PATTERN.findall(snippet)
        if rules:
            skill = find_owning_skill(snippet)
            candidates.append({
                "rules": sorted(set(rules)),
                "snippet": snippet,
                "owning_skill": skill,
                "compile_candidate": True,
            })
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Scan for compile-candidate reflexions.")
    parser.add_argument("file", type=Path, help="Session log or markdown file to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    candidates = scan_file(args.file)
    if not candidates:
        if not args.json:
            print("ℹ️ No reusable rule reflexions detected.")
        sys.exit(0)

    if args.json:
        import json
        print(json.dumps(candidates, indent=2))
    else:
        print(f"⚡ Found {len(candidates)} compile-candidate reflexion(s):")
        for c in candidates:
            print(f"   • Rules: {', '.join(c['rules'])}")
            print(f"     Owning Skill: {c['owning_skill']}")
            print(f"     Prompt: Reflexion references {c['rules'][0]} -> Compile into '{c['owning_skill']}'? (y/n)")


if __name__ == "__main__":
    main()
