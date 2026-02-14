import os
from pathlib import Path

WORKFLOW_DIR = Path(".agent/workflows")
INDEX_FILE = Path(".agent/WORKFLOW_INDEX.md")


def generate_index():
    workflows = []
    for f in WORKFLOW_DIR.glob("*.md"):
        if f.name == "WORKFLOW_INDEX.md":
            continue

        # Simple extraction of description if available
        desc = "No description"
        content = f.read_text(errors="ignore")
        for line in content.splitlines():
            if line.startswith("description:") or line.startswith("---description:"):
                desc = line.split(":", 1)[1].strip()
                break

        latency = "Medium"  # Default
        workflows.append(f"| `/{f.stem}` | {desc} | {latency} |")

    workflows.sort()

    header = """---
created: 2025-12-19
last_updated: 2026-02-11
---

# Workflow Index

> **Purpose**: Auto-generated reference for all available workflows.
> **Last Updated**: 2026-02-11

---

## All Workflows

| Command | Description | Latency |
| :--- | :--- | :--- |
"""

    footer = """
---

## Tagging

# index #workflow #automation
"""

    with open(INDEX_FILE, "w") as f:
        f.write(header + "\n".join(workflows) + footer)
    print(f"Generated index with {len(workflows)} workflows.")


if __name__ == "__main__":
    generate_index()
