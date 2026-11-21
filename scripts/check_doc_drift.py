#!/usr/bin/env python3
"""
scripts/check_doc_drift.py — Source-Bound Documentation & Instruction Drift Gate
================================================================================

Detects actual structural and temporal drift between documentation/instructions
and the repository codebase (answering the "curated notes drift from code" and
"contradictory instructions" failure modes):
  1. Broken relative Markdown links in root docs (AGENTS.md, README.md)
  2. Retired index files (TAG_INDEX.md, project_state.md) or missing indexed
     concrete paths in AGENTS.md
  3. Missing hook scripts referenced in .claude/settings.json
  4. Stale boot_tokens / dead hooks/hooks.yaml references in athena.yaml
  5. Source-vs-summary temporal drift via `tracks:` YAML frontmatter on docs/skills

Usage:
    python3 scripts/check_doc_drift.py
    python3 scripts/check_doc_drift.py --check
    python3 scripts/check_doc_drift.py --check --fail-on-drift --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

RETIRED_INDEX_FILENAMES = ("TAG_INDEX.md", "project_state.md")
_NEGATION_MARKERS = ("retired", "never rely", "deprecated", "removed", "do not use", "replaced")
_RUNTIME_MEMORY_FILES = {"activeContext.md", "userContext.md", "productContext.md"}
_INDEXED_PATH_PREFIXES = (
    "src/",
    "scripts/",
    ".agent/",
    "examples/",
    "docs/",
    "tests/",
    ".context/",
)
_CONCRETE_EXTS = (".py", ".md", ".json", ".yaml", ".yml", ".sh")
_SKIP_DIR_NAMES = {"archive", "archive_skills", "session_logs", "node_modules", ".git", ".venv"}

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")
_HOOK_SCRIPT_RE = re.compile(r"(\.agent/scripts/[A-Za-z0-9_./-]+\.py)")


def parse_tracks_frontmatter(text: str) -> list[str]:
    """Extract `tracks:` entries from YAML frontmatter (inline or block list)."""
    if not text.startswith("---"):
        return []

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    fm_lines: list[str] = []
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        fm_lines.append(line)

    if not closed:
        return []

    tracks: list[str] = []
    in_tracks_block = False
    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if in_tracks_block:
            if line[:1].isspace() or stripped.startswith("- "):
                if stripped.startswith("- "):
                    item = stripped[2:].split("#", 1)[0].strip().strip("'\"")
                    if item:
                        tracks.append(item)
                continue
            in_tracks_block = False

        if re.match(r"^tracks\s*:", stripped):
            rest = stripped.split(":", 1)[1].split("#", 1)[0].strip()
            if rest.startswith("[") and rest.endswith("]"):
                inner = rest[1:-1]
                for part in inner.split(","):
                    item = part.strip().strip("'\"")
                    if item:
                        tracks.append(item)
            elif rest:
                item = rest.strip("'\"")
                if item:
                    tracks.append(item)
            else:
                in_tracks_block = True

    return tracks


def check_markdown_links(doc_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Verify relative Markdown link targets exist on disk."""
    if not doc_path.exists():
        return []

    findings: list[dict[str, Any]] = []
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    in_fence = False

    for line_num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        clean_line = _BACKTICK_RE.sub("", line)
        for m in _MD_LINK_RE.finditer(clean_line):
            raw_target = m.group(2).strip()
            if not raw_target or raw_target.startswith(
                ("http://", "https://", "mailto:", "file://", "#")
            ):
                continue
            target_no_title = raw_target.split()[0]
            target_rel = target_no_title.split("#", 1)[0]
            if not target_rel:
                continue

            resolved = (doc_path.parent / target_rel).resolve()
            if not resolved.exists():
                findings.append(
                    {
                        "severity": "error",
                        "code": "BROKEN_LINK",
                        "file": str(doc_path.relative_to(repo_root)),
                        "line": line_num,
                        "target": raw_target,
                        "message": f"Broken relative link '{raw_target}' in {doc_path.name}:{line_num}",
                    }
                )
    return findings


def check_agents_index(agents_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Audit AGENTS.md for retired index files and non-existent indexed repo paths."""
    if not agents_path.exists():
        return []

    findings: list[dict[str, Any]] = []
    text = agents_path.read_text(encoding="utf-8", errors="ignore")
    in_fence = False
    rel_agents = str(agents_path.relative_to(repo_root))

    for line_num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        lower_line = line.lower()
        is_negative_note = any(marker in lower_line for marker in _NEGATION_MARKERS)

        if not is_negative_note:
            for retired_name in RETIRED_INDEX_FILENAMES:
                if retired_name in line:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "RETIRED_INDEX_REF",
                            "file": rel_agents,
                            "line": line_num,
                            "target": retired_name,
                            "message": f"Retired index '{retired_name}' listed as active in {rel_agents}:{line_num}",
                        }
                    )

        for m in _BACKTICK_RE.finditer(line):
            token = m.group(1).strip()
            if not token or any(ch.isspace() for ch in token):
                continue
            if not token.startswith(_INDEXED_PATH_PREFIXES):
                continue
            if any(ch in token for ch in "*?<>[]{}") or "..." in token:
                continue
            if not token.endswith(_CONCRETE_EXTS):
                continue
            if Path(token).name in _RUNTIME_MEMORY_FILES:
                continue
            if not (repo_root / token).exists():
                findings.append(
                    {
                        "severity": "error",
                        "code": "MISSING_INDEX_PATH",
                        "file": rel_agents,
                        "line": line_num,
                        "target": token,
                        "message": f"Indexed path '{token}' missing on disk ({rel_agents}:{line_num})",
                    }
                )

    return findings


def check_hook_paths(settings_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Verify every .agent/scripts/*.py referenced in .claude/settings.json exists."""
    if not settings_path.exists():
        return []

    findings: list[dict[str, Any]] = []
    rel_settings = str(settings_path.relative_to(repo_root))
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            {
                "severity": "error",
                "code": "INVALID_SETTINGS_JSON",
                "file": rel_settings,
                "line": 1,
                "target": rel_settings,
                "message": f"Failed to parse {rel_settings}: {exc}",
            }
        ]

    commands: list[str] = []
    hooks = data.get("hooks", {})
    if isinstance(hooks, dict):
        for groups in hooks.values():
            if not isinstance(groups, list):
                continue
            for group in groups:
                if not isinstance(group, dict):
                    continue
                for hook in group.get("hooks", []):
                    if isinstance(hook, dict) and hook.get("command"):
                        commands.append(str(hook["command"]))

    status_line = data.get("statusLine", {})
    if isinstance(status_line, dict) and status_line.get("command"):
        commands.append(str(status_line["command"]))

    seen: set[str] = set()
    for cmd in commands:
        for m in _HOOK_SCRIPT_RE.finditer(cmd):
            script_rel = m.group(1)
            if script_rel in seen:
                continue
            seen.add(script_rel)
            if not (repo_root / script_rel).exists():
                findings.append(
                    {
                        "severity": "error",
                        "code": "MISSING_HOOK_SCRIPT",
                        "file": rel_settings,
                        "line": 1,
                        "target": script_rel,
                        "message": f"Hook script '{script_rel}' referenced in {rel_settings} does not exist",
                    }
                )

    return findings


def check_athena_yaml(yaml_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Verify athena.yaml has no stale boot_tokens budget or dead hooks/hooks.yaml ref."""
    if not yaml_path.exists():
        return []

    findings: list[dict[str, Any]] = []
    rel_yaml = str(yaml_path.relative_to(repo_root))
    text = yaml_path.read_text(encoding="utf-8", errors="ignore")

    m_boot = re.search(r"^\s*boot_tokens:\s*(\d+)", text, re.MULTILINE)
    if m_boot:
        budget = int(m_boot.group(1))
        if budget > 5000:
            line_num = text[: m_boot.start()].count("\n") + 1
            findings.append(
                {
                    "severity": "error",
                    "code": "STALE_BOOT_BUDGET",
                    "file": rel_yaml,
                    "line": line_num,
                    "target": str(budget),
                    "message": f"boot_tokens={budget} in {rel_yaml}:{line_num} exceeds 5000 (MinMax v2.2 target ~3600)",
                }
            )

    if "hooks/hooks.yaml" in text:
        has_hooks_yaml = (
            (repo_root / ".agent" / "hooks" / "hooks.yaml").exists()
            or (repo_root / "hooks" / "hooks.yaml").exists()
        )
        if not has_hooks_yaml:
            idx = text.index("hooks/hooks.yaml")
            line_num = text[:idx].count("\n") + 1
            findings.append(
                {
                    "severity": "error",
                    "code": "DEAD_COMMENT_REF",
                    "file": rel_yaml,
                    "line": line_num,
                    "target": "hooks/hooks.yaml",
                    "message": f"Dead reference to 'hooks/hooks.yaml' in {rel_yaml}:{line_num}",
                }
            )

    return findings


def _is_git_repo(repo_root: Path) -> bool:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=2,
        )
        return res.returncode == 0 and res.stdout.strip() == "true"
    except Exception:
        return False


def _get_effective_timestamp(
    file_path: Path, repo_root: Path, use_git: bool
) -> float:
    """Return latest git commit timestamp for clean tracked files, else file mtime."""
    if use_git:
        try:
            rel = file_path.resolve().relative_to(repo_root.resolve()).as_posix()
            dirty = subprocess.run(
                ["git", "status", "--porcelain", "--", rel],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=2,
            )
            if dirty.returncode == 0 and not dirty.stdout.strip():
                log = subprocess.run(
                    ["git", "log", "-1", "--format=%ct", "--", rel],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if log.returncode == 0 and log.stdout.strip():
                    return float(int(log.stdout.strip()))
        except Exception:
            pass
    return os.path.getmtime(file_path)


def check_tracked_docs(
    repo_root: Path, scan_dirs: list[Path] | None = None
) -> list[dict[str, Any]]:
    """Verify docs/skills with `tracks:` frontmatter have not drifted behind source files."""
    roots = scan_dirs or [
        repo_root / "docs",
        repo_root / ".agent" / "skills",
        repo_root / "examples" / "skills",
    ]
    use_git = _is_git_repo(repo_root)
    findings: list[dict[str, Any]] = []

    for base in roots:
        if not base.exists() or not base.is_dir():
            continue
        for current_root, dirnames, filenames in os.walk(base):
            dirnames[:] = [
                d
                for d in sorted(dirnames)
                if d not in _SKIP_DIR_NAMES and not d.startswith(".")
            ]
            for fn in sorted(filenames):
                if not fn.endswith(".md"):
                    continue
                doc_path = Path(current_root) / fn
                text = doc_path.read_text(encoding="utf-8", errors="ignore")
                tracks = parse_tracks_frontmatter(text)
                if not tracks:
                    continue

                rel_doc = str(doc_path.relative_to(repo_root))
                doc_ts: float | None = None

                for target_rel in tracks:
                    target_path = (repo_root / target_rel).resolve()
                    if not target_path.exists():
                        findings.append(
                            {
                                "severity": "error",
                                "code": "MISSING_TRACKED_TARGET",
                                "file": rel_doc,
                                "line": 1,
                                "target": target_rel,
                                "message": f"{rel_doc} tracks missing path '{target_rel}'",
                            }
                        )
                        continue

                    if doc_ts is None:
                        doc_ts = _get_effective_timestamp(doc_path, repo_root, use_git)
                    target_ts = _get_effective_timestamp(target_path, repo_root, use_git)
                    if target_ts - doc_ts > 60.0:
                        delta_days = round((target_ts - doc_ts) / 86400.0, 2)
                        findings.append(
                            {
                                "severity": "warning",
                                "code": "DRIFTED",
                                "file": rel_doc,
                                "line": 1,
                                "target": target_rel,
                                "delta_days": delta_days,
                                "hint": "Re-read source file before trusting summary",
                                "message": (
                                    f"{rel_doc} may be drifted from '{target_rel}' "
                                    f"({delta_days}d newer) — Re-read source file before trusting summary"
                                ),
                            }
                        )

    return findings


def run_audit(repo_root: Path) -> dict[str, Any]:
    """Run all instruction, link, config, and source-bound doc drift checks."""
    root = repo_root.resolve()
    findings: list[dict[str, Any]] = []

    agents_path = root / "AGENTS.md"
    readme_path = root / "README.md"
    settings_path = root / ".claude" / "settings.json"
    yaml_path = root / "athena.yaml"

    findings.extend(check_agents_index(agents_path, root))
    findings.extend(check_markdown_links(agents_path, root))
    findings.extend(check_markdown_links(readme_path, root))
    findings.extend(check_hook_paths(settings_path, root))
    findings.extend(check_athena_yaml(yaml_path, root))
    findings.extend(check_tracked_docs(root))

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    drifted = [f for f in findings if f["code"] == "DRIFTED"]

    return {
        "repo_root": str(root),
        "findings": findings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "drifted_count": len(drifted),
        "ok": len(errors) == 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit instruction consistency, link integrity, and source-bound doc drift."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root to audit (defaults to script parent's parent).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any error findings are detected.",
    )
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Also exit 1 when DRIFTED warnings are detected.",
    )
    args = parser.parse_args(argv)

    result = run_audit(args.root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Doc Drift Audit ({result['repo_root']}): "
            f"{result['error_count']} error(s), {result['warning_count']} warning(s) "
            f"({result['drifted_count']} drifted)"
        )
        for item in result["findings"]:
            tag = "ERROR" if item["severity"] == "error" else "WARN"
            print(f"  [{tag}:{item['code']}] {item['message']}")

    if args.fail_on_drift and result["drifted_count"] > 0:
        return 1
    if args.check and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
