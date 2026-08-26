#!/usr/bin/env python3
"""
sync_positioning.py — drift gate for Athena's canonical description.

The failure this fixes
----------------------
On 2026-07-27 the description was reworded three times in ~2 hours. Each reword
meant hand-editing 9 occurrences across 4 repos (private, public, GitHub profile,
website). One of them — `athena.yaml` — was silently missed, because the phrase
wraps a line break there and a substring replace never matched. The edit script
printed a checkmark anyway. It was only caught by diffing the published file.

That is the same generator as TD-063 (colliding identifiers) and the stale
0.908 benchmark: a fact with no single owner drifts, and the drift is found by
accident. This script gives the description one owner
(`.agent/config/positioning.json`) and makes drift loud.

Epistemic status: code-enforced for local surfaces (pre-commit Gate 5),
agent-discretion for remote/sibling surfaces (needs network / a sibling checkout,
so it reports rather than blocks).

Usage
-----
    python3 .agent/scripts/sync_positioning.py              # check local (+sibling if present)
    python3 .agent/scripts/sync_positioning.py --remote     # also check GitHub surfaces
    python3 .agent/scripts/sync_positioning.py --write      # fix mechanical local surfaces
    python3 .agent/scripts/sync_positioning.py --quiet      # exit code only

Exit codes: 0 = in sync, 1 = drift found, 2 = config/IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = PROJECT_ROOT / ".agent" / "config" / "positioning.json"

GREEN, RED, YELLOW, DIM, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m"


def norm(s: str) -> str:
    """Collapse all whitespace so a line-wrapped occurrence still matches.

    This is the whole point: `athena.yaml` wraps "governed AI\\n  agents" across
    a newline. A naive `in` check misses it and reports a false PASS.
    """
    return re.sub(r"\s+", " ", s).strip()


def load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"{RED}✗ missing {CONFIG.relative_to(PROJECT_ROOT)}{RESET}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as e:
        print(f"{RED}✗ {CONFIG.name} is not valid JSON: {e}{RESET}", file=sys.stderr)
        raise SystemExit(2)


def expected_text(cfg: dict, key: str) -> str:
    """Resolve a `must_contain` key against components / variants / top level."""
    if key == "canonical_description":
        return cfg["canonical_description"]
    if key in cfg.get("variants", {}):
        return cfg["variants"][key]
    if key in cfg.get("components", {}):
        return cfg["components"][key]
    raise KeyError(f"unknown must_contain key: {key}")


def check_text(body: str, expect: str) -> bool:
    return norm(expect).lower() in norm(body).lower()


# --------------------------------------------------------------------------- #
# local surfaces
# --------------------------------------------------------------------------- #

def check_local(cfg: dict, write: bool) -> list[tuple[str, str]]:
    """Return a list of (path, reason) drift findings."""
    findings: list[tuple[str, str]] = []
    for surface in cfg["local_surfaces"]:
        path = PROJECT_ROOT / surface["path"]
        if not path.exists():
            findings.append((surface["path"], "file missing"))
            continue
        expect = expected_text(cfg, surface["must_contain"])
        body = path.read_text(encoding="utf-8", errors="replace")
        if check_text(body, expect):
            continue

        fixed = False
        if write:
            fixed = try_fix(path, cfg, surface, expect)
        if not fixed:
            findings.append((surface["path"], f"missing {surface['must_contain']!r}"))
    return findings


def try_fix(path: Path, cfg: dict, surface: dict, expect: str) -> bool:
    """Repair only surfaces with an unambiguous single-line form.

    Prose surfaces (README taglines, wiki copy) are deliberately NOT rewritten:
    a script that mangles prose to satisfy a substring check is worse than a
    checker that tells a human exactly where to look.
    """
    body = path.read_text(encoding="utf-8")

    # pyproject.toml — the whole description value is machine-owned.
    if path.name == "pyproject.toml":
        cat = cfg["components"]["category"]
        val = cfg["variants"]["capability_clause_prose"]
        new_line = (
            f'description = "Athena — a {cat} that helps you make better decisions '
            f'with your own context. {val}."'
        )
        patched, n = re.subn(r"^description = \".*\"$", new_line, body, count=1, flags=re.M)
        if n:
            path.write_text(patched, encoding="utf-8")
            print(f"  {GREEN}fixed{RESET} {path.name} (description line rewritten)")
            return True
    return False


# --------------------------------------------------------------------------- #
# sibling checkouts (website) — present only on the operator's machine
# --------------------------------------------------------------------------- #

def check_siblings(cfg: dict) -> tuple[list[tuple[str, str]], int]:
    findings: list[tuple[str, str]] = []
    skipped = 0
    for surface in cfg.get("sibling_surfaces", []):
        root = Path(surface["root"]).expanduser()
        path = root / surface["path"]
        if not path.exists():
            skipped += 1
            continue
        expect = expected_text(cfg, surface["must_contain"])
        if not check_text(path.read_text(encoding="utf-8", errors="replace"), expect):
            findings.append((f"{root.name}/{surface['path']}", f"missing {surface['must_contain']!r}"))
    return findings, skipped


# --------------------------------------------------------------------------- #
# remote surfaces (GitHub) — read-only, needs `gh`
# --------------------------------------------------------------------------- #

def gh(args: list[str]) -> str | None:
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=25)
        return r.stdout if r.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check_remote(cfg: dict) -> tuple[list[tuple[str, str]], bool]:
    findings: list[tuple[str, str]] = []
    if gh(["--version"]) is None:
        return findings, False

    for surface in cfg["remote_surfaces"]:
        repo, kind = surface["repo"], surface["kind"]
        expect = expected_text(cfg, surface["must_contain"])

        if kind == "about":
            body = gh(["repo", "view", repo, "--json", "description", "-q", ".description"])
            label = f"{repo} (About)"
        else:
            raw = gh(["api", f"repos/{repo}/contents/{surface['file']}", "--jq", ".content"])
            body = None
            if raw:
                import base64
                try:
                    body = base64.b64decode(raw).decode("utf-8", errors="replace")
                except Exception:
                    body = None
            label = f"{repo}/{surface['file']}"

        if body is None:
            findings.append((label, "unreachable (network/auth)"))
        elif not check_text(body, expect):
            findings.append((label, f"missing {surface['must_contain']!r}"))
    return findings, True


# --------------------------------------------------------------------------- #
# retired phrases leaking back into live surfaces
# --------------------------------------------------------------------------- #

PRUNE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".claude", ".athena",
}
MAX_BYTES = 512_000  # a tagline never lives in a half-megabyte file


def check_retired(cfg: dict) -> list[tuple[str, str]]:
    """Historical records legitimately quote retired phrases — those are excluded.

    Walks the tree ONCE for all phrases and prunes excluded directories during
    traversal. The naive version (rglob per phrase, filter after) took >2min on
    this repo, which is useless for a pre-commit gate.
    """
    import os

    findings: list[tuple[str, str]] = []
    exclusions = cfg["retired_phrase_exclusions"]
    phrases = [(e["phrase"], e["phrase"].lower()) for e in cfg["retired_phrases"]]
    exts = {".md", ".toml", ".json", ".yaml", ".yml", ".txt", ".py"}

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        dirnames[:] = [
            d for d in dirnames
            if d not in PRUNE_DIRS
            and not any(x.rstrip("/") == d for x in exclusions)
        ]
        rel_dir = os.path.relpath(dirpath, PROJECT_ROOT)
        if rel_dir != "." and any(x in rel_dir + "/" for x in exclusions):
            dirnames[:] = []
            continue

        for name in filenames:
            if Path(name).suffix.lower() not in exts:
                continue
            rel = os.path.normpath(os.path.join(rel_dir, name)) if rel_dir != "." else name
            if any(x in rel for x in exclusions):
                continue
            full = Path(dirpath) / name
            try:
                if full.stat().st_size > MAX_BYTES:
                    continue
                body = full.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            for original, lowered in phrases:
                if lowered in body:
                    findings.append((rel, f"retired phrase resurfaced: {original!r}"))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Drift gate for Athena's canonical description.")
    ap.add_argument("--write", action="store_true", help="repair mechanical local surfaces")
    ap.add_argument("--remote", action="store_true", help="also check GitHub surfaces (needs gh)")
    ap.add_argument("--quiet", action="store_true", help="exit code only")
    args = ap.parse_args()

    cfg = load_config()
    say = (lambda *a, **k: None) if args.quiet else print

    say(f"\n{DIM}canonical:{RESET} {cfg['canonical_description'][:88]}…\n")

    local = check_local(cfg, args.write)
    siblings, skipped = check_siblings(cfg)
    retired = check_retired(cfg)
    remote, remote_ran = ([], False)
    if args.remote:
        remote, remote_ran = check_remote(cfg)

    n_local = len(cfg["local_surfaces"])
    say(f"  local surfaces    : {n_local - len(local)}/{n_local} in sync")
    n_sib = len(cfg.get("sibling_surfaces", []))
    say(f"  sibling surfaces  : {n_sib - skipped - len(siblings)}/{n_sib - skipped} in sync"
        + (f" {DIM}({skipped} skipped — checkout not present){RESET}" if skipped else ""))
    if args.remote:
        n_rem = len(cfg["remote_surfaces"])
        say(f"  remote surfaces   : {n_rem - len(remote)}/{n_rem} in sync"
            if remote_ran else f"  remote surfaces   : {YELLOW}skipped (gh unavailable){RESET}")
    say(f"  retired phrases   : {len(retired)} leak(s) into live files")

    findings = local + siblings + remote + retired
    if findings:
        say(f"\n{RED}✗ positioning drift ({len(findings)}){RESET}")
        for where, why in findings:
            say(f"    {RED}·{RESET} {where}  {DIM}— {why}{RESET}")
        say(f"\n  {DIM}source of truth: .agent/config/positioning.json{RESET}")
        say(f"  {DIM}mechanical fixes: --write  ·  prose surfaces are intentionally hand-edited{RESET}\n")
        return 1

    say(f"\n{GREEN}✓ positioning in sync across every registered surface{RESET}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
