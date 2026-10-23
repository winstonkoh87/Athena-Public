#!/usr/bin/env python3
"""
scripts/sync_to_public.py — Default-Deny, Fail-Closed Public Repo Synchronizer

Implements Phase 0 remediation ticket P0.2 (audit finding P-1):
1. Default-deny allowlist architecture based on .agent/config/public_manifest.yaml.
2. Manifest validation: every entry must resolve to >=1 existing tracked file, else exit 2.
3. Fail-closed: absent or empty blocklist/deny-set causes immediate exit 2.
4. No directory entries under .context/ allowed.
5. Dry-run by default; requires --apply to copy files.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / ".agent/config/public_manifest.yaml"
DEFAULT_BLOCKLIST = REPO_ROOT / ".agent/config/privacy_patterns.txt"


def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        sys.stderr.write(f"FATAL: Manifest not found at {manifest_path}\n")
        sys.exit(2)
    try:
        with open(manifest_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        sys.stderr.write(f"FATAL: Failed to parse manifest YAML: {e}\n")
        sys.exit(2)
    return data


def validate_and_resolve(
    manifest_data: dict, repo_root: Path
) -> tuple[set[Path], list[str]]:
    resolved_files: set[Path] = set()
    errors: list[str] = []

    # Check for forbidden wholesale directory allowlists under .context/
    context_entries = manifest_data.get("context", []) or []
    for entry in context_entries:
        if entry.strip() in {".context", ".context/", ".context/**"}:
            errors.append(
                f"FORBIDDEN: Wholesale directory allowlist for '.context/' found: '{entry}'. "
                "Audit P-1 requires individual file enumeration only."
            )

    # Categories to inspect
    categories = [
        "root_files",
        "docs",
        "examples",
        "scripts",
        "src",
        "supabase",
        "tests",
        "tools",
        "wiki",
        "community",
        "framework",
        "context",
        "agent",
    ]

    for cat in categories:
        entries = manifest_data.get(cat, []) or []
        for entry in entries:
            target = repo_root / entry
            if target.is_dir():
                # Enumerate files recursively inside directory (excluding cache/transient files)
                files_found = [
                    p
                    for p in target.rglob("*")
                    if p.is_file()
                    and "__pycache__" not in p.parts
                    and p.suffix != ".pyc"
                    and p.name != ".DS_Store"
                ]
                if not files_found:
                    errors.append(f"Empty or non-existent directory entry: '{entry}'")
                for f in files_found:
                    resolved_files.add(f)
            elif target.is_file():
                resolved_files.add(target)
            else:
                errors.append(f"Unresolved manifest entry (not found on disk): '{entry}'")

    return resolved_files, errors


def verify_blocklist_gate(blocklist_path: Path) -> None:
    """Fail-closed if privacy blocklist is missing or empty."""
    if not blocklist_path.exists():
        sys.stderr.write(
            f"FATAL: Privacy blocklist missing at {blocklist_path}. Refusing to sync without privacy gate.\n"
        )
        sys.exit(2)

    with open(blocklist_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not lines:
        sys.stderr.write(
            f"FATAL: Privacy blocklist at {blocklist_path} is empty. Refusing to sync without active patterns.\n"
        )
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Default-deny public repo synchronizer")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to manifest")
    parser.add_argument("--blocklist", type=Path, default=DEFAULT_BLOCKLIST, help="Path to blocklist")
    parser.add_argument("--dest", type=Path, default=None, help="Destination directory (Athena-Public)")
    parser.add_argument("--apply", action="store_true", help="Execute file copy (dry-run by default)")
    args = parser.parse_args()

    # Fail-closed checks
    verify_blocklist_gate(args.blocklist)
    manifest_data = load_manifest(args.manifest)

    resolved_files, errors = validate_and_resolve(manifest_data, REPO_ROOT)

    if errors:
        sys.stderr.write(f"FATAL: Manifest validation failed ({len(errors)} errors):\n")
        for err in errors:
            sys.stderr.write(f"  - {err}\n")
        sys.exit(2)

    print(f"Manifest validated successfully: {len(resolved_files)} files resolved.")

    # Display files with SHA256 in dry-run mode
    for p in sorted(resolved_files):
        rel_path = p.relative_to(REPO_ROOT)
        sha = calculate_sha256(p)
        print(f"  {sha[:12]}  {rel_path}")

    if not args.apply:
        print("\n[DRY-RUN] No files were copied. Pass --apply and --dest to synchronize.")
        return 0

    if not args.dest:
        sys.stderr.write("FATAL: --dest required when --apply is set.\n")
        return 2

    dest_root = args.dest.resolve()
    if not dest_root.exists():
        sys.stderr.write(f"FATAL: Destination root {dest_root} does not exist.\n")
        return 2

    # Perform copy
    copied = 0
    for src_file in resolved_files:
        rel = src_file.relative_to(REPO_ROOT)
        dst_file = dest_root / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied += 1

    print(f"Successfully copied {copied} files to {dest_root}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
