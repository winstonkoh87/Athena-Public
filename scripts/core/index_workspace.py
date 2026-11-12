#!/usr/bin/env python3
"""
index_workspace.py — Unified Indexing Engine
============================================
Generates and maintains the map of the workspace.
1. TAG_INDEX.md: Maps #tags to files.
2. PROTOCOL_SUMMARIES.md: Compressed index of all protocols.

Usage: python3 .agent/scripts/index_workspace.py
"""

import argparse
import importlib.util
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Setup Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_DIR = PROJECT_ROOT / ".context"
PROTOCOLS_DIR = PROJECT_ROOT / ".agent" / "skills" / "protocols"
TAG_INDEX_FILE = CONTEXT_DIR / "TAG_INDEX.md"
PROTOCOL_SUMMARIES_FILE = CONTEXT_DIR / "PROTOCOL_SUMMARIES.md"


def generate_tag_index():
    """Scans the workspace for #tags and builds an index."""
    tag_map = {}

    # Files and directories to ignore
    ignore_patterns = {
        ".git",
        ".agent",
        "node_modules",
        "dist",
        "build",
        ".venv",
        ".context/cache",
        ".athena",
        "user_backup",
        "Athena-Public.wiki",
        "__pycache__",
        ".pytest_cache",
        ".shared",
        ". Clawdhub",
    }

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune ignored directories from recursion
        dirs[:] = [
            d
            for d in dirs
            if not any(p in str(Path(root) / d) for p in ignore_patterns)
        ]

        for file in files:
            if file.endswith((".md", ".py", ".js", ".ts", ".astro")):
                path = Path(root) / file
                try:
                    # Skip if any ignore pattern is in the absolute path
                    if any(p in str(path) for p in ignore_patterns):
                        continue

                    content = path.read_text(encoding="utf-8", errors="ignore")
                    # Match tags that start with # but are not hex codes (3 or 6 chars)
                    # Filter: Must start with letter, at least 3 chars.
                    candidates = re.findall(r"(?<!\w)#([a-zA-Z][\w-]{2,})", content)
                    for tag in candidates:
                        # Further filter out common noise
                        if tag.lower() in {"py", "md", "js", "ts", "astro", "tmp"}:
                            continue

                        if tag not in tag_map:
                            tag_map[tag] = []
                        rel_path = path.relative_to(PROJECT_ROOT)
                        if str(rel_path) not in tag_map[tag]:
                            tag_map[tag].append(str(rel_path))
                except Exception:
                    continue

    # Write TAG_INDEX.md
    output = [
        "# Tag Index\n",
        f"> **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "---\n",
    ]
    for tag in sorted(tag_map.keys()):
        output.append(f"## #{tag}")
        for path in sorted(tag_map[tag]):
            output.append(f"- [{os.path.basename(path)}]({path})")
        output.append("")

    TAG_INDEX_FILE.write_text("\n".join(output))
    print(f"✅ Generated {TAG_INDEX_FILE}")


def _load_summary_generator():
    """Load generate_protocol_summaries helper module from the repo if available."""
    for base in (PROJECT_ROOT, Path(__file__).resolve().parents[2]):
        candidate = base / "examples" / "scripts" / "generate_protocol_summaries.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("generate_protocol_summaries", candidate)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    return None


def _iter_fallback_protocol_files(root: Path) -> list[Path]:
    """Fallback active-protocol collector when generate_protocol_summaries.py is absent."""
    src_dir = root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    try:
        from athena.core.config import iter_protocol_files

        return iter_protocol_files(root)
    except ImportError:
        pass

    ignored_dirs = {"_archived", "archive"}
    ignored_files = {"README.md", "INDEX.md"}
    candidates = [
        root / ".agent" / "skills" / "protocols",
        root / "examples" / "protocols",
    ]
    fw_dir = root / ".framework"
    if fw_dir.is_dir():
        for child in sorted(fw_dir.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                candidates.append(child / "protocols")

    files: list[Path] = []
    seen: set[Path] = set()
    for base in candidates:
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            if md.name in ignored_files or md.name.startswith("."):
                continue
            rel_parts = md.relative_to(base).parts
            if any(p in ignored_dirs or p.startswith(".") for p in rel_parts[:-1]):
                continue
            resolved = md.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(md)
    return files


def generate_protocol_summaries(force: bool = False):
    """Delegate summary indexing to generate_protocol_summaries.py with safe fallback."""
    generator = _load_summary_generator()
    if generator is not None and hasattr(generator, "generate_summaries"):
        generator.generate_summaries(
            repo_root=PROJECT_ROOT,
            output_file=PROTOCOL_SUMMARIES_FILE,
            force=force,
        )
        return

    protocols = []
    num_re = re.compile(r"^(?:[A-Za-z]+-(?:[A-Za-z]+-)?)?(\d+)(?=[-_.]|$)")
    target_dir = Path(PROTOCOL_SUMMARIES_FILE).resolve().parent

    for path in _iter_fallback_protocol_files(PROJECT_ROOT):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            heading_match = re.search(
                r"^#\s+(?:Protocol(?:\s+(?:[A-Za-z]+-)*\d+)?\s*[:.]?\s*)?(.*)",
                content,
                re.MULTILINE,
            )
            title = heading_match.group(1).strip() if heading_match and heading_match.group(1).strip() else path.stem
            num_match = num_re.match(path.stem)
            code = num_match.group(1) if num_match else "—"

            trigger_match = re.search(r"\*\*When\*\*:\s*(.*)", content)
            trigger = trigger_match.group(1).strip() if trigger_match else "---"
            rel_link = Path(os.path.relpath(path, target_dir)).as_posix()

            protocols.append(
                {
                    "code": code,
                    "title": title,
                    "trigger": trigger,
                    "summary": "---",
                    "path": rel_link,
                }
            )
        except Exception:
            continue

    if not protocols and not force:
        if PROTOCOL_SUMMARIES_FILE.exists():
            print(f"⚠️ No active protocols found; preserved existing {PROTOCOL_SUMMARIES_FILE}")
        else:
            print(f"⚠️ No active protocols found under {PROJECT_ROOT}; skipped writing {PROTOCOL_SUMMARIES_FILE}")
        return

    protocols.sort(key=lambda x: x["code"])
    output = [
        "# Protocol Summaries (Compressed)\n",
        f"> **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"> **Total**: {len(protocols)} protocols\n",
        "---\n",
        "| Code | Title | Trigger | Summary |",
        "|------|-------|---------|---------|",
    ]

    for p in protocols:
        row = f"| {p['code']} | [{p['title']}]({p['path']}) | {p['trigger']} | {p['summary']} |"
        output.append(row)

    PROTOCOL_SUMMARIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROTOCOL_SUMMARIES_FILE.write_text("\n".join(output), encoding="utf-8")
    print(f"✅ Generated {PROTOCOL_SUMMARIES_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build TAG_INDEX.md and PROTOCOL_SUMMARIES.md")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write PROTOCOL_SUMMARIES.md even if 0 active protocols are discovered",
    )
    args = parser.parse_args()
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    generate_tag_index()
    generate_protocol_summaries(force=args.force)
