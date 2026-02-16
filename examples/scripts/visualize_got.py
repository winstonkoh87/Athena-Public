#!/usr/bin/env python3
"""
visualize_got.py - GoT Visualization Generator
=============================================
Generates ASCII (default) or Mermaid (optional) visualizations for
Graph of Thoughts reasoning structures.

Usage:
    python3 visualize_got.py "Problem Statement" --steps "Step 1, Step 2" --branches "Path A, Path B"
    python3 visualize_got.py "Problem" --json '{...}'
    python3 visualize_got.py ... --mermaid

Dependencies: None (Standard Library only)
"""

import sys
import argparse
import json
from typing import List, Dict, Any


def generate_ascii_tree(root: str, branches: List[Dict[str, Any]]) -> str:
    """Generates a directory-tree style ASCII visualization."""
    lines = [f"ROOT: {root}"]

    for i, branch in enumerate(branches):
        is_last_branch = i == len(branches) - 1
        prefix = "└── " if is_last_branch else "├── "
        child_prefix = "    " if is_last_branch else "│   "

        name = branch.get("name", f"Track {i + 1}")
        lines.append(f"{prefix}{name}")

        steps = branch.get("steps", [])
        for j, step in enumerate(steps):
            is_last_step = j == len(steps) - 1
            step_prefix = "└── " if is_last_step else "├── "
            lines.append(f"{child_prefix}{step_prefix}{step}")

    return "\n".join(lines)


def generate_mermaid(root: str, branches: List[Dict[str, Any]]) -> str:
    """Generates Mermaid.js flowchart syntax."""
    lines = ["graph TD"]
    lines.append(f"    R[{root}]")

    for i, branch in enumerate(branches):
        name = branch.get("name", f"Track {i + 1}")
        branch_id = f"B{i}"
        lines.append(f"    R --> {branch_id}[{name}]")

        previous_node = branch_id
        steps = branch.get("steps", [])
        for j, step in enumerate(steps):
            step_id = f"B{i}S{j}"
            # Escape quotes
            safe_step = step.replace('"', "'")
            lines.append(f'    {previous_node} --> {step_id}["{safe_step}"]')
            previous_node = step_id

    return "```mermaid\n" + "\n".join(lines) + "\n```"


def main():
    parser = argparse.ArgumentParser(description="GoT Visualization Tool")
    parser.add_argument(
        "problem",
        nargs="?",
        default="Reasoning Root",
        help="The root problem or question",
    )
    parser.add_argument("--json", help="Pass full structure as JSON string")
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Output Mermaid.js syntax instead of ASCII",
    )

    # Quick CLI usage
    parser.add_argument("--branches", help="Comma-separated branch names")
    parser.add_argument(
        "--steps",
        help="Comma-separated steps (applied to all branches for simple test)",
    )

    args = parser.parse_args()

    # Parse Structure
    structure = {"root": args.problem, "branches": []}

    if args.json:
        try:
            data = json.loads(args.json)
            structure["root"] = data.get("root", structure["root"])
            structure["branches"] = data.get("branches", [])
        except json.JSONDecodeError:
            print("Error: Invalid JSON provided", file=sys.stderr)
            sys.exit(1)
    elif args.branches:
        branch_names = [b.strip() for b in args.branches.split(",")]
        steps = (
            [s.strip() for s in args.steps.split(",")]
            if args.steps
            else ["Step 1", "Step 2"]
        )

        for name in branch_names:
            structure["branches"].append({"name": name, "steps": steps})

    # Generate Output
    if args.mermaid:
        print(generate_mermaid(structure["root"], structure["branches"]))
    else:
        print("```text")
        print(generate_ascii_tree(structure["root"], structure["branches"]))
        print("```")


if __name__ == "__main__":
    main()
