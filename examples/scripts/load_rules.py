#!/usr/bin/env python3
"""
load_rules.py - Load path-specific rules for current context.

Protocol 407: Path-Specific Rules
Stolen from Claude Code.

Usage:
    python3 load_rules.py src/api/routes.py
    # Returns: Contents of global.md + api.md + security.md
"""

import fnmatch
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # Fallback if PyYAML not installed
    yaml = None

RULES_DIR = Path(__file__).parent.parent / "rules"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    if yaml:
        try:
            meta = yaml.safe_load(frontmatter_text)
            return meta or {}, body
        except Exception:
            pass

    # Manual parsing fallback
    meta = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                # Parse simple list
                value = [
                    v.strip().strip('"').strip("'")
                    for v in value[1:-1].split(",")
                    if v.strip()
                ]
            elif value.isdigit():
                value = int(value)
            meta[key] = value

    return meta, body


def matches_path(patterns: list, target_path: str) -> bool:
    """Check if target path matches any pattern."""
    if not patterns:
        return False

    target = Path(target_path)

    for pattern in patterns:
        # Try exact glob match
        if fnmatch.fnmatch(str(target), pattern):
            return True
        # Try matching just the filename
        if fnmatch.fnmatch(target.name, pattern):
            return True
        # Try matching relative path components
        for i in range(len(target.parts)):
            partial = "/".join(target.parts[i:])
            if fnmatch.fnmatch(partial, pattern):
                return True

    return False


def load_rules_for_path(target_path: str) -> str:
    """Load all applicable rules for a given file path."""
    if not RULES_DIR.exists():
        return "# No rules directory found"

    applicable_rules = []

    for rule_file in sorted(RULES_DIR.glob("*.md")):
        content = rule_file.read_text()
        meta, body = parse_frontmatter(content)

        paths = meta.get("paths", [])
        priority = meta.get("priority", 50)

        # Global rules (no paths specified) always load
        if not paths or matches_path(paths, target_path):
            applicable_rules.append(
                {"name": rule_file.stem, "priority": priority, "content": body}
            )

    # Sort by priority (lower = first)
    applicable_rules.sort(key=lambda r: r["priority"])

    # Combine rules
    if not applicable_rules:
        return "# No applicable rules found"

    output = []
    for rule in applicable_rules:
        output.append(f"## Rules: {rule['name']}\n\n{rule['content']}")

    return "\n\n---\n\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: load_rules.py <file_path>", file=sys.stderr)
        print("\nLoads path-specific rules from .agent/rules/", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    rules = load_rules_for_path(target)
    print(rules)
