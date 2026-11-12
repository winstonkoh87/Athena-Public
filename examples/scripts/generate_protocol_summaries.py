#!/usr/bin/env python3
"""
Auto-generate PROTOCOL_SUMMARIES.md from protocol frontmatter.
Replaces the manually-maintained version that drifts within 14 days.

Walks populated protocol directories (.agent/skills/protocols,
examples/protocols, .framework/*/protocols), extracts:
  - Protocol number / ID (numeric, PREFIX-NUM, or flat framework formats)
  - Description (from frontmatter or first substantive paragraph)
  - Category (from directory name, or 'framework' for flat framework protocols)

Output: .context/PROTOCOL_SUMMARIES.md
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from athena.core.config import (
        IGNORED_PROTOCOL_DIRNAMES,
        IGNORED_PROTOCOL_FILENAMES,
        get_protocol_dirs as _config_get_protocol_dirs,
        iter_protocol_files as _config_iter_protocol_files,
    )
except ImportError:
    IGNORED_PROTOCOL_FILENAMES = frozenset({"README.md", "INDEX.md"})
    IGNORED_PROTOCOL_DIRNAMES = frozenset({"_archived", "archive"})
    _config_get_protocol_dirs = None
    _config_iter_protocol_files = None

PROTOCOLS_DIR = REPO_ROOT / ".agent" / "skills" / "protocols"
OUTPUT_FILE = REPO_ROOT / ".context" / "PROTOCOL_SUMMARIES.md"

_LEADING_FM_RE = re.compile(
    r"^\ufeff?\s*---([^\n]*)\n((?:(?![ \t]*---[ \t]*(?:\n|$))[^\n]*\n)*)---[ \t]*(?:\n|$)"
)
_PROTOCOL_NUM_RE = re.compile(r"^(?:[A-Za-z]+-(?:[A-Za-z]+-)?)?(\d+)(?=[-_.]|$)")


def _is_active_file(path: Path, base_dir: Path) -> bool:
    if not path.is_file() or path.suffix != ".md":
        return False
    if path.name in IGNORED_PROTOCOL_FILENAMES or path.name.startswith("."):
        return False
    try:
        parts = path.relative_to(base_dir).parts
    except ValueError:
        return False
    return not any(
        part in IGNORED_PROTOCOL_DIRNAMES or part.startswith(".")
        for part in parts[:-1]
    )


def discover_protocol_dirs(repo_root: Path | None = None) -> list[Path]:
    """Return populated protocol directories in priority order."""
    root = Path(repo_root).resolve() if repo_root else REPO_ROOT
    if _config_get_protocol_dirs is not None:
        return _config_get_protocol_dirs(root)

    candidates = [
        root / ".agent" / "skills" / "protocols",
        root / "examples" / "protocols",
    ]
    fw_dir = root / ".framework"
    if fw_dir.is_dir():
        for child in sorted(fw_dir.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                candidates.append(child / "protocols")

    dirs: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if not candidate.is_dir():
            continue
        if not any(_is_active_file(p, candidate) for p in candidate.rglob("*.md")):
            continue
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            dirs.append(candidate)
    return dirs


def _iter_active_files(repo_root: Path) -> list[tuple[Path, Path]]:
    """Return (proto_dir, filepath) pairs for active protocols."""
    pairs: list[tuple[Path, Path]] = []
    seen: set[Path] = set()
    if _config_iter_protocol_files is not None:
        dirs = discover_protocol_dirs(repo_root)
        for md_file in _config_iter_protocol_files(repo_root):
            resolved = md_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            parent_dir = next((d for d in dirs if md_file.is_relative_to(d)), md_file.parent)
            pairs.append((parent_dir, md_file))
        return pairs

    for proto_dir in discover_protocol_dirs(repo_root):
        for md_file in sorted(proto_dir.rglob("*.md")):
            if not _is_active_file(md_file, proto_dir):
                continue
            resolved = md_file.resolve()
            if resolved not in seen:
                seen.add(resolved)
                pairs.append((proto_dir, md_file))
    return pairs


def _strip_leading_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Strip sequential leading YAML-ish blocks (including ---key: malformed headers)."""
    fm: dict[str, str] = {}
    body = content

    while True:
        match = _LEADING_FM_RE.match(body)
        if not match:
            break
        first_line_extra, block = match.groups()
        raw_lines = []
        if first_line_extra.strip():
            raw_lines.append(first_line_extra.strip())
        raw_lines.extend(block.splitlines())
        for line in raw_lines:
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip().lower()
                val = val.strip().strip("\"'")
                if key and val:
                    fm.setdefault(key, val)
        body = body[match.end() :]

    return fm, body


def extract_frontmatter(filepath: Path) -> dict[str, str]:
    """Extract leading YAML-ish frontmatter, heading, and body summary cleanly."""
    content = filepath.read_text(errors="ignore")
    fm, body = _strip_leading_frontmatter(content)

    # Strip fenced code blocks before searching for headings or body paragraphs
    body_no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)

    heading_match = re.search(r"^#\s+(.+)$", body_no_code, re.MULTILINE)
    if heading_match:
        fm.setdefault("heading", heading_match.group(1).strip())

    for para in re.split(r"\n\s*\n", body_no_code.strip()):
        para = para.strip()
        if not para:
            continue
        if re.match(r"^#{1,6}\s", para):
            continue
        if re.match(r"^[-_*]{3,}\s*$", para):
            continue
        if re.match(r"^\|", para):
            continue
        if re.match(r"^<!--.*-->$", para, re.DOTALL):
            continue
        if re.match(r"^#", para) and len(para) < 80:
            continue
        clean = re.sub(r"^>\s*", "", para, flags=re.MULTILINE).strip()
        clean_flat = re.sub(r"\s*\n+\s*", " ", clean).strip()
        clean_unbold = clean_flat.replace("**", "").strip()
        if re.match(
            r"^(?:(?:⚠️|ℹ️)\s*)?(Source|Domain|Priority|Tags|Protocol|Definition|Status|Version|Updated|Created|Last[ _]Updated|Category|Type|Reference|Dependencies|ID[ _-]note|Redirect)\s*:",
            clean_unbold,
            re.IGNORECASE,
        ):
            continue
        if len(clean_flat) >= 20:
            first_sentence = re.split(r"(?<!\b\d)(?<=[.!?])\s+", clean_flat, maxsplit=1)[0]
            summary_text = first_sentence if len(first_sentence) >= 25 else clean_flat
            fm.setdefault("body_summary", summary_text[:150])
            break

    return fm


def extract_protocol_name(filename: str, frontmatter: dict) -> str:
    """Derive a human-readable protocol name from frontmatter heading or filename."""
    if "heading" in frontmatter:
        return frontmatter["heading"]

    stem = Path(filename).stem
    stem = re.sub(r"^(?:[A-Za-z]+-(?:[A-Za-z]+-)?)?\d+[-_]", "", stem)
    stem = re.sub(r"^[A-Za-z]+[-_]", "", stem)
    return re.sub(r"[-_]+", " ", stem).strip().title()


def extract_protocol_number(filename: str) -> str:
    """Extract numeric ID from standard, prefixed, or flat framework protocol filenames."""
    match = _PROTOCOL_NUM_RE.match(Path(filename).stem)
    return match.group(1) if match else ""


def _infer_category(filepath: Path, proto_dir: Path) -> str:
    """Determine category folder name, using 'framework' for flat .framework files."""
    try:
        rel_parts = filepath.relative_to(proto_dir).parts
    except ValueError:
        return "general"
    if len(rel_parts) > 1:
        return rel_parts[0]
    if proto_dir.parent.parent.name == ".framework":
        return "framework"
    return "general"


def _sanitize_cell_text(text: str) -> str:
    """Clean markdown text so table rows stay single-line and link-safe."""
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    cleaned = re.sub(r"```[a-zA-Z0-9_-]*\s*", "", cleaned)
    cleaned = cleaned.replace("```", "").replace("**", "")
    cleaned = re.sub(r"\s*\n+\s*", " ", cleaned)
    cleaned = cleaned.replace("|", "—")
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _clean_protocol_title(raw_name: str) -> str:
    """Strip redundant 'Protocol 123:' or 'DEC-123:' prefixes from display title."""
    return re.sub(
        r"^(?:Protocol(?:\s+(?:[A-Za-z]+-)*\d+)?|[A-Za-z]+-\d+)\s*[:\-—]\s*",
        "",
        raw_name,
        flags=re.IGNORECASE,
    ).strip()


def build_summary(filepath: Path, category: str, repo_root: Path | None = None) -> dict:
    """Build a summary record for one protocol file."""
    root = Path(repo_root).resolve() if repo_root else REPO_ROOT
    fm = extract_frontmatter(filepath)
    filename = filepath.name
    number = extract_protocol_number(filename)
    name = extract_protocol_name(filename, fm)

    description = fm.get("description", "") or fm.get("body_summary", "")

    return {
        "number": number,
        "name": name,
        "description": description,
        "category": category,
        "filename": filename,
        "path": filepath.resolve().relative_to(root).as_posix(),
    }


def generate_summaries(
    repo_root: Path | None = None,
    output_file: Path | None = None,
    force: bool = False,
) -> tuple[int, Path]:
    """Discover active protocols, generate summary index, and return (count, output_path)."""
    root = Path(repo_root).resolve() if repo_root else REPO_ROOT
    target = Path(output_file) if output_file else (root / ".context" / "PROTOCOL_SUMMARIES.md")
    if not target.is_absolute():
        target = root / target

    active_files = _iter_active_files(root)
    categories: dict[str, list[dict]] = defaultdict(list)
    seen_protocols: set[tuple[str, str]] = set()
    total = 0

    for proto_dir, md_file in active_files:
        category = _infer_category(md_file, proto_dir)
        summary = build_summary(md_file, category, repo_root=root)
        name_clean = _clean_protocol_title(summary["name"])
        if summary["number"]:
            dedup_key = (summary["number"].lstrip("0") or "0", name_clean.lower())
            if dedup_key in seen_protocols:
                continue
            seen_protocols.add(dedup_key)
        categories[category].append(summary)
        total += 1

    if total == 0 and not force:
        if target.exists():
            print(f"⚠️ No active protocols found; preserved existing {target}")
        else:
            print(f"⚠️ No active protocols found under {root}; skipped writing {target}")
        return 0, target

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "---",
        "created: 2026-03-16",
        f"last_updated: {now}",
        "description: Quick-lookup summaries for all protocols, grouped by category",
        "auto_generated: true",
        "generator: generate_protocol_summaries.py",
        "---",
        "",
        "# Protocol Summaries",
        "",
        "> **Purpose**: One-line summaries for rapid protocol discovery. Referenced by `AGENTS.md` for agent retrieval.",
        f"> **Inventory**: {total} protocols across {len(categories)} categories.",
        f"> **Generated**: {now} by `generate_protocol_summaries.py`",
        "",
        "---",
        "",
    ]

    sorted_cats = sorted(categories.items(), key=lambda x: (-len(x[1]), x[0]))
    output_dir = target.resolve().parent

    for category, protocols in sorted_cats:
        cat_title = category.replace("-", " ").title()
        lines.append(f"## {cat_title} ({len(protocols)})")
        lines.append("")
        lines.append("| Protocol | Summary |")
        lines.append("|----------|---------|")

        for p in protocols:
            num = p["number"]
            name_clean = _clean_protocol_title(p["name"])
            name_clean = _sanitize_cell_text(name_clean) or Path(p["filename"]).stem

            desc = _sanitize_cell_text(p["description"])
            if not desc:
                desc = "(No description — needs frontmatter backfill)"
            if desc.lower() == name_clean.lower():
                desc = "(Title-echo detected — needs frontmatter backfill)"
            if len(desc) > 100:
                desc = desc[:97] + "..."

            label_text = f"{num} {name_clean}" if num else name_clean
            abs_proto = root / p["path"]
            rel_link = Path(os.path.relpath(abs_proto, output_dir)).as_posix()
            lines.append(f"| [{label_text}]({rel_link}) | {desc} |")

        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "> **System Note**: For deep lookup, use `smart_search.py` or inspect the protocol libraries directly. "
        "This file is a quick-reference index only."
    )
    lines.append("")
    lines.append("#protocols #index #summaries #retrieval")
    lines.append("")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {target} — {total} protocols across {len(categories)} categories")
    return total, target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate PROTOCOL_SUMMARIES.md from active protocols.")
    parser.add_argument("--repo-root", type=Path, default=None, help="Override repository root path")
    parser.add_argument("--output", type=Path, default=None, help="Override output markdown file path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write output even if 0 active protocols are discovered",
    )
    args = parser.parse_args(argv)
    generate_summaries(repo_root=args.repo_root, output_file=args.output, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
