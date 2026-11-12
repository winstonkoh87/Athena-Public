from pathlib import Path

WORKFLOW_DIR = Path(".agent/workflows")
PUBLIC_WORKFLOW_DIR = Path("examples/workflows")
INDEX_FILE = Path(".agent/WORKFLOW_INDEX.md")


def _resolve_workflow_dir() -> Path:
    for candidate in (WORKFLOW_DIR, PUBLIC_WORKFLOW_DIR):
        if candidate.exists() and any(candidate.glob("*.md")):
            return candidate
    return WORKFLOW_DIR


def generate_index():
    workflow_dir = _resolve_workflow_dir()
    workflows = []
    for f in workflow_dir.glob("*.md"):
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

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        f.write(header + "\n".join(workflows) + footer)
    print(f"Generated index with {len(workflows)} workflows.")


if __name__ == "__main__":
    generate_index()
