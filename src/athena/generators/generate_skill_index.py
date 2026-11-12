#!/usr/bin/env python3
"""
Generate SKILL_INDEX.md to index all compound skills and active protocols.
Tree Mode v2.1 - Unified Skills + Active Protocols Registry (excludes archive/).
"""

import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent
SKILLS_DIR = ROOT_DIR / ".agent/skills"
OUTPUT_FILE = SKILLS_DIR / "SKILL_INDEX.md"
IGNORED_PROTOCOL_DIRS = {"archive", "_archived", "__pycache__"}


def _parse_skill_frontmatter(content: str) -> dict:
    """Parse leading YAML frontmatter metadata from a SKILL.md file."""
    match = re.match(
        r"^\ufeff?\s*---[^\n]*\n(.*?)^---[ \t]*(?:\n|$)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return {}
    try:
        import yaml

        loaded = yaml.safe_load(match.group(1))
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def discover_compound_skills() -> list[dict]:
    """Discover active compound skills under .agent/skills/*/SKILL.md."""
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        return skills

    for item in sorted(SKILLS_DIR.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")) or item.name == "protocols":
            continue
        manifest = item / "SKILL.md"
        if not manifest.is_file():
            continue
        meta = _parse_skill_frontmatter(manifest.read_text(encoding="utf-8", errors="replace"))
        skills.append(
            {
                "name": meta.get("name", item.name),
                "description": str(meta.get("description", "")).strip(),
                "triggers": meta.get("triggers") or [],
                "context_trigger": meta.get("context_trigger"),
                "dependencies": meta.get("dependencies") or [],
                "rel_path": manifest.relative_to(SKILLS_DIR).as_posix(),
            }
        )
    return skills


def build_tree(path):
    tree = {}
    items = sorted(os.listdir(path))
    for item in items:
        if item.startswith(".") or item in IGNORED_PROTOCOL_DIRS:
            continue
        full_path = path / item
        if full_path.is_dir():
            subtree = build_tree(full_path)
            if subtree:
                tree[item] = subtree
        elif item.endswith(".md") and item not in ("SKILL_INDEX.md", "README.md", "INDEX.md"):
            tree[item] = None
    return tree


def format_tree_lines(tree, indent=0):
    lines = []
    for key, value in tree.items():
        prefix = "  " * indent + "├── "
        if value is None:
            lines.append(f"{prefix}{key}")
        else:
            lines.append(f"{prefix}**{key.replace('-', ' ').title()}**")
            lines.extend(format_tree_lines(value, indent + 1))
    return lines


def main():
    if not SKILLS_DIR.exists():
        print(f"Skills dir not found: {SKILLS_DIR}")
        return

    compound_skills = discover_compound_skills()
    lines = [
        "# 🧠 SKILL INDEX (Skills & Active Protocols)",
        "",
        "> **Purpose**: Master registry of active compound skills (with triggers) and active protocols.",
        "> **Auto-generated**: via `generate_skill_index.py` (Tree Mode v2.1)",
        "",
        "---",
        "",
        f"## ⚡ Compound Skills Registry ({len(compound_skills)} active)",
        "",
        "| Skill | Triggers | Description |",
        "| :--- | :--- | :--- |",
    ]

    for skill in compound_skills:
        triggers = skill["triggers"]
        if isinstance(triggers, list) and triggers:
            trig_str = ", ".join(f"`{t}`" for t in triggers[:4])
        elif skill.get("context_trigger"):
            trig_str = f"`{skill['context_trigger']}`"
        else:
            trig_str = "always-on / explicit"
        desc = re.sub(r"\s*\n+\s*", " ", skill["description"]).replace("|", "—")
        if len(desc) > 110:
            desc = desc[:107] + "..."
        lines.append(f"| [{skill['name']}]({skill['rel_path']}) | {trig_str} | {desc} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 🌳 Active Protocol Knowledge Tree",
            "```text",
        ]
    )

    # Build and format tree (excluding archive/)
    protocols_dir = SKILLS_DIR / "protocols"
    if protocols_dir.exists():
        tree = build_tree(protocols_dir)
        lines.extend(format_tree_lines(tree))

    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📂 Detailed Protocol Index")
    lines.append("")

    # Detailed walk logic (excluding archive/)
    for root, dirs, files in os.walk(protocols_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in IGNORED_PROTOCOL_DIRS)
        files = [f for f in sorted(files) if f.endswith(".md") and f not in ("README.md", "INDEX.md")]
        if not files:
            continue

        subdir = Path(root).relative_to(SKILLS_DIR)
        dirname = " > ".join([p.replace("-", " ").title() for p in subdir.parts])
        lines.append(f"### {dirname}")
        lines.append("")

        for f in files:
            path = Path(root) / f
            rel_path = path.relative_to(SKILLS_DIR).as_posix()
            lines.append(f"- [{f}]({rel_path})")
        lines.append("")

    lines.append("")

    # Add Case Studies (from .context)
    case_studies_dir = ROOT_DIR / ".context/memories/case_studies"
    if case_studies_dir.exists():
        lines.append("---")
        lines.append("### 📚 Case Study Library (Context)")
        lines.append("")
        for f in sorted(os.listdir(case_studies_dir)):
            if f.endswith(".md"):
                path = case_studies_dir / f
                rel_path = Path(os.path.relpath(path, SKILLS_DIR)).as_posix()
                lines.append(f"- [{f}]({rel_path})")
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT_FILE} ({len(compound_skills)} compound skills)")


if __name__ == "__main__":
    main()
