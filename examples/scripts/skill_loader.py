#!/usr/bin/env python3
"""
Dynamic Skill Loader (Protocol 411)

Discovers and loads skills based on triggers and dependencies.

Usage:
    python3 skill_loader.py index       # Generate skill index
    python3 skill_loader.py list        # List available skills
    python3 skill_loader.py match <msg> # Find skills matching a message
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_PATHS = [
    PROJECT_ROOT / ".agent" / "skills",
    Path.home() / ".athena" / "skills",
]


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    try:
        _, fm, body = content.split("---", 2)
        meta = yaml.safe_load(fm)
        return meta or {}, body
    except (ValueError, yaml.YAMLError):
        return {}, content


def discover_skills() -> Dict[str, dict]:
    """Discover all available skills with metadata."""
    skills = {}

    for base in SKILL_PATHS:
        if not base.exists():
            continue

        for skill_dir in base.iterdir():
            if not skill_dir.is_dir():
                continue

            manifest = skill_dir / "SKILL.md"
            if not manifest.exists():
                continue

            content = manifest.read_text()
            meta, body = parse_frontmatter(content)

            name = meta.get("name", skill_dir.name)
            skills[name] = {
                **meta,
                "name": name,
                "path": str(manifest),
                "dir": str(skill_dir),
                "description": meta.get("description", ""),
                "triggers": meta.get("triggers", []),
                "dependencies": meta.get("dependencies", []),
            }

    return skills


def list_skills():
    """List all available skills."""
    skills = discover_skills()

    if not skills:
        print("📭 No skills found")
        return

    print(f"📦 Available Skills ({len(skills)}):")
    print("-" * 50)

    for name, skill in sorted(skills.items()):
        print(f"\n  {name}")
        if skill.get("description"):
            print(f"    {skill['description']}")
        if skill.get("triggers"):
            triggers = ", ".join(skill["triggers"][:3])
            print(f"    Triggers: {triggers}")


def match_triggers(message: str, triggers: List[str]) -> bool:
    """Check if message matches any triggers."""
    message_lower = message.lower()

    for trigger in triggers:
        # Slash command
        if trigger.startswith("/"):
            if message.strip().startswith(trigger):
                return True

        # Keyword match
        elif "+" in trigger or "|" in trigger:
            # Parse boolean expression: "buy" + "sell" + ("BTC" | "ETH")
            # Simplified: check if all required keywords present
            keywords = re.findall(r'"([^"]+)"', trigger)
            if all(kw.lower() in message_lower for kw in keywords):
                return True

        # Simple substring
        elif trigger.lower() in message_lower:
            return True

    return False


def find_matching_skills(message: str) -> List[str]:
    """Find skills whose triggers match the message."""
    skills = discover_skills()
    matched = []

    for name, skill in skills.items():
        triggers = skill.get("triggers", [])
        if triggers and match_triggers(message, triggers):
            matched.append(name)

    return matched


def generate_index():
    """Generate a skill index markdown file."""
    skills = discover_skills()

    lines = [
        "# Skill Index",
        "",
        f"*Auto-generated on {__import__('datetime').datetime.now().isoformat()}*",
        "",
        f"Total skills: {len(skills)}",
        "",
        "---",
        "",
    ]

    for name, skill in sorted(skills.items()):
        lines.append(f"## {name}")
        lines.append("")
        if skill.get("description"):
            lines.append(f"> {skill['description']}")
            lines.append("")
        lines.append(f"- **Path**: `{skill['path']}`")
        if skill.get("triggers"):
            lines.append(f"- **Triggers**: `{', '.join(skill['triggers'])}`")
        if skill.get("dependencies"):
            lines.append(f"- **Dependencies**: `{', '.join(skill['dependencies'])}`")
        lines.append("")

    index_path = PROJECT_ROOT / ".agent" / "skills" / "SKILL_INDEX.md"
    index_path.write_text("\n".join(lines))
    print(f"✅ Generated skill index: {index_path}")


def load_skill(name: str) -> Optional[str]:
    """Load a skill's content."""
    skills = discover_skills()

    if name not in skills:
        print(f"❌ Skill '{name}' not found")
        return None

    skill = skills[name]
    content = Path(skill["path"]).read_text()

    # Also load dependencies
    deps = []
    for dep in skill.get("dependencies", []):
        dep_path = PROJECT_ROOT / dep
        if dep_path.exists():
            deps.append(dep_path.read_text())

    return content + "\n\n" + "\n\n".join(deps)


def main():
    if len(sys.argv) < 2:
        print("Dynamic Skill Loader (Protocol 411)")
        print("")
        print("Usage:")
        print("  skill_loader.py index         # Generate skill index")
        print("  skill_loader.py list          # List available skills")
        print("  skill_loader.py match <msg>   # Find skills matching message")
        print("  skill_loader.py load <name>   # Load a skill's content")
        sys.exit(1)

    command = sys.argv[1]

    if command == "index":
        generate_index()

    elif command == "list":
        list_skills()

    elif command == "match":
        if len(sys.argv) < 3:
            print("❌ Usage: skill_loader.py match <message>")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        matched = find_matching_skills(message)

        if matched:
            print(f"🎯 Matched skills: {', '.join(matched)}")
        else:
            print("📭 No matching skills found")

    elif command == "load":
        if len(sys.argv) < 3:
            print("❌ Usage: skill_loader.py load <skill_name>")
            sys.exit(1)
        content = load_skill(sys.argv[2])
        if content:
            print(content)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
