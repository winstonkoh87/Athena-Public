#!/usr/bin/env python3
"""
Protocol Generator
Describe a rough idea → get a full workflow.md with phases and turbo annotations.
"""
import argparse
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client

load_dotenv()

WORKFLOWS_DIR = Path(".agent/workflows")
PROTOCOLS_DIR = Path(".agent/skills/protocols")

_IGNORED_FILENAMES = {"README.md", "INDEX.md"}
_IGNORED_DIRNAMES = {"archive", "_archived"}
_PROTOCOL_ID_RE = re.compile(
    r"^(?:[A-Za-z]+-(?:[A-Za-z]+-)?)?(\d+)(?=[-_.]|$)"
)


def _discover_protocol_dirs() -> list[Path]:
    """Return populated or candidate protocol directories in CWD."""
    candidates = [PROTOCOLS_DIR, Path("examples/protocols")]
    fw_dir = Path(".framework")
    if fw_dir.exists():
        candidates.extend(sorted(fw_dir.glob("*/protocols")))
    return [d for d in candidates if d.exists() and d.is_dir()]


def _iter_protocol_files() -> list[tuple[Path, Path]]:
    """Yield (base_dir, protocol_file) across discovered protocol directories."""
    results: list[tuple[Path, Path]] = []
    for base_dir in _discover_protocol_dirs():
        for f in sorted(base_dir.rglob("*.md")):
            rel_parts = f.relative_to(base_dir).parts
            if f.name in _IGNORED_FILENAMES or any(
                part in _IGNORED_DIRNAMES for part in rel_parts[:-1]
            ):
                continue
            results.append((base_dir, f))
    return results


def _extract_protocol_id(stem: str) -> int | None:
    """Extract numeric protocol ID from numeric, prefixed, or flat names."""
    match = _PROTOCOL_ID_RE.match(stem)
    return int(match.group(1)) if match else None


def get_existing_protocol_ids() -> set:
    """Scan all protocol directories for existing IDs."""
    ids: set[int] = set()
    for _base_dir, f in _iter_protocol_files():
        pid = _extract_protocol_id(f.stem)
        if pid is not None:
            ids.add(pid)
    return ids


def check_for_collisions():
    """Check for duplicate protocol IDs across directories."""
    id_locations: dict[int, list[str]] = {}
    for _base_dir, f in _iter_protocol_files():
        pid = _extract_protocol_id(f.stem)
        if pid is not None:
            id_locations.setdefault(pid, []).append(str(f))

    return {k: v for k, v in id_locations.items() if len(v) > 1}

SYSTEM_PROMPT = """You are a workflow architect for the Athena AI system. Given a rough description, generate a complete workflow file.

Follow this exact format:
```markdown
---
description: [Short one-line description]
---

# /[workflow-name] — [Title]

> **Latency Profile**: [QUICK/STANDARD/DEEP]
> **Philosophy**: "[Core principle]"
> **Use Case**: [When to use this]

---

## Phase 1: [Phase Name]

> **Rule**: [Key constraint or principle]

// turbo

```bash
[command if applicable]
```

[Description of what this phase does]

---

## Phase 2: [Next Phase]
...

---

## Quick Reference

| Command | Effect | Time |
|---------|--------|------|
| `/workflow-name` | [What it does] | [Estimate] |

---

## Tagging

#workflow #automation #[relevant-tags]
```

Rules:
1. Use `// turbo` annotation before bash blocks that are safe to auto-run
2. Include clear phase gates where decisions happen
3. Be specific about commands and file paths
4. Keep it actionable and concise"""

def generate_protocol(description: str, name: str | None = None) -> str:
    """Generate a protocol from description."""
    client = get_client()

    name_hint = f"Workflow name should be: {name}" if name else "Suggest an appropriate workflow name."

    prompt = f"""{SYSTEM_PROMPT}

USER REQUEST:
{description}

{name_hint}

Generate the complete workflow file:"""

    response = client.generate(prompt)

    # Clean up if wrapped in code blocks
    if response.startswith("```markdown"):
        response = response[11:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]

    return response.strip()

def main():
    parser = argparse.ArgumentParser(description="Generate a workflow file from description")
    parser.add_argument("description", nargs="*", help="Workflow description")
    parser.add_argument("--name", help="Workflow name (e.g., 'deploy')")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        print("🔧 Protocol Generator (Ctrl+C to exit)\n")
        description = input("Describe the workflow: ").strip()
        name = input("Workflow name (or press Enter to auto-generate): ").strip() or None
    elif args.description:
        description = " ".join(args.description)
        name = args.name
    else:
        parser.print_help()
        sys.exit(1)

    print("🤖 Generating protocol...")
    protocol = generate_protocol(description, name)

    if args.output:
        output_path = Path(args.output)
    elif name:
        output_path = WORKFLOWS_DIR / f"{name}.md"
    else:
        # Extract name from generated content
        output_path = None

    if output_path:
        output_path.write_text(protocol, encoding="utf-8")
        print(f"✅ Saved to {output_path}")
    else:
        print("\n" + protocol)

if __name__ == "__main__":
    main()
