#!/usr/bin/env python3
"""
Generate SKILL_INDEX.md to index all protocols and prevent orphans.
Tree Mode v2.0 - Implements Hierarchical Skill Tree.
"""

import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT_DIR / ".agent/skills"
OUTPUT_FILE = SKILLS_DIR / "SKILL_INDEX.md"

# ANSI Colors for script output (will be stripped for file)
BOLD = "\033[1m"
RESET = "\033[0m"


def build_tree(path):
    tree = {}
    items = sorted(os.listdir(path))
    for item in items:
        if item.startswith(".") or item == "__pycache__":
            continue
        full_path = path / item
        if full_path.is_dir():
            tree[item] = build_tree(full_path)
        elif item.endswith(".md") and item != "SKILL_INDEX.md":
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

    lines = [
        "# 🧠 SKILL INDEX (Protocol Registry)",
        "",
        "> **Purpose**: Master registry of all installed protocols.",
        "> **Auto-generated**: via `generate_skill_index.py` (Tree Mode v2.0)",
        "",
        "---",
        "",
        "## 🌳 Knowledge Tree Overview",
        "```text",
    ]

    # Build and format tree
    protocols_dir = SKILLS_DIR / "protocols"
    if protocols_dir.exists():
        tree = build_tree(protocols_dir)
        lines.extend(format_tree_lines(tree))

    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📂 Detailed Index")
    lines.append("")

    # Detailed walk logic
    for root, dirs, files in os.walk(protocols_dir):
        files = [f for f in sorted(files) if f.endswith(".md")]
        if not files:
            continue

        subdir = Path(root).relative_to(SKILLS_DIR)
        level = len(subdir.parts)

        dirname = " > ".join([p.replace("-", " ").title() for p in subdir.parts])
        lines.append(f"### {dirname}")
        lines.append("")

        for f in files:
            path = Path(root) / f
            rel_path = path.relative_to(SKILLS_DIR)
            lines.append(f"- [{f}]({rel_path})")
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
                rel_path = os.path.relpath(path, SKILLS_DIR)
                lines.append(f"- [{f}]({rel_path})")
        lines.append("")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
