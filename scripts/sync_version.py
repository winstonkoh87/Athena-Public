#!/usr/bin/env python3
"""
Single source of truth version synchronizer.

Two modes:
  (default)  rewrite every declared surface to match pyproject.toml
  --check    report drift and exit 1 without writing anything (for CI)

--check exists because running the writer in CI is not a check: it rewrote the
files inside the runner, discarded them with the workspace, and exited 0
whatever the state of the commit. Version drift could never fail the build.

The narrower failure that replaced it: --check covered three files
(pyproject.toml, src/athena/__init__.py, docs/ARCHITECTURE.md), printed "All
version references consistent", and exited 0 — while the same tree carried
9.9.6 in CAPS.json, 9.9.7 across four docs and eight wiki pages, and 9.9.8 in
AGENTS.md and README.md. A guard scoped to the files that already agree is a
guard that cannot fail, wearing a green check.

So this script does two things, and the second is the one that matters:

  1. DECLARED SURFACES — every place the repo states its own version, checked
     against the SSOT.
  2. DISCOVERY — a sweep of every tracked text file for version-shaped strings.
     Anything not covered by a declared surface or an explicit exemption fails
     the check. A new version claim cannot appear silently; it must be declared
     as a surface or exempted with a stated reason.

Adding a version stamp somewhere new now costs one line in SURFACES. That is
the point: the cost of a silent surface is a wrong number shipped to users.
"""

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"

# ── Declared surfaces ────────────────────────────────────────────────────────
# (relative path, regex with exactly one capture group around the version,
#  human label). Multiple surfaces may share a path.
SURFACES: list[tuple[str, str, str]] = [
    ("src/athena/__init__.py", r'__version__\s*=\s*"([^"]+)"', "SDK package version"),
    # Both copies carry a version heading and both drifted independently.
    ("docs/ARCHITECTURE.md", r"(?:\*\*Version\*\*|Version):\s*v([0-9][0-9A-Za-z.\-]*)", "architecture heading"),
    ("ARCHITECTURE.md", r"(?:\*\*Version\*\*|Version):\s*v([0-9][0-9A-Za-z.\-]*)", "architecture heading (root copy)"),
    ("docs/ENGINEERING_DEPTH.md", r"\*\*Version\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "engineering-depth heading"),
    ("docs/KNOWLEDGE_GRAPH.md", r"\*\*Version\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "knowledge-graph heading"),
    ("docs/DEMO.md", r"ATHENA BOOT SEQUENCE v([0-9][0-9A-Za-z.\-]*)", "demo boot banner"),
    ("docs/REQUIREMENTS.md", r"\*\*Version\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "requirements heading"),
    ("docs/SPEC_SHEET.md", r"\*\*Version\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "spec-sheet heading"),
    ("AGENTS.md", r"\*\*System\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "agent-context system version"),
    ("CLAUDE.md", r"\*\*System\*\*:\s*v([0-9][0-9A-Za-z.\-]*)", "agent-context system version"),
    (".agent/config/CAPS.json", r'"system":\s*"v?([0-9][0-9A-Za-z.\-]*)"', "CAPS system version"),
    ("src/athena/tools/citation_verifier.py", r'Athena-Academic-Verifier/([0-9][0-9A-Za-z.\-]*)\s', "Crossref User-Agent version"),
]

# ── Exemptions ───────────────────────────────────────────────────────────────
# Version strings that legitimately are NOT the current version. Every entry
# needs a reason: an exemption without a stated reason is just a narrower guard
# wearing different clothes.
EXEMPTIONS: list[tuple[str, str, str]] = [
    # Release history — every past version by definition.
    ("docs/CHANGELOG.md", r".", "release history"),
    ("CHANGELOG.md", r".", "release history"),
    ("community/CHANGELOG.md", r".", "community release history"),
    ("README.md", r"^\s*-\s*\*\*v[0-9]", "README release-history entries"),
    ("README.md", r"\[v[0-9][0-9A-Za-z.\-]*\s+notes\]", "links to past release notes"),
    ("docs/TECH_DEBT.md", r".", "debt ledger discusses versions, never declares one"),
    ("docs/marketing/*", r".", "dated marketing artifacts, pinned to their release"),

    # "Landed in version X" markers — pinned to that version on purpose.
    ("*", r"\(v[0-9][0-9A-Za-z.\-]*\+?\)", "introduced-in markers, pinned by design"),
    ("*", r"v[0-9][0-9A-Za-z.\-]*\+", "'version X and later' markers"),
    ("*", r"v[0-9][0-9A-Za-z.\-]*\s*(?:→|->)\s*v?[0-9]", "version-transition prose"),

    # Per-document stamps rather than the system version.
    ("Athena-Public.wiki/*", r".", "vendored wiki pages carry per-page stamps"),
    (".context/CHANGELOG.md", r".", "context-local release history, same class as root CHANGELOG"),
    (".context/PROJECTS.md", r".",
     "project switchboard references version-stamped milestones — historical by construction"),
    (".context/META_LEARNING.md", r".",
     "longitudinal behavioral tracking references the version era each pattern was observed"),
    (".context/TECH_DEBT.md", r".",
     "debt ledger discusses versions where debt was introduced — historical context"),
    (".context/KNOWLEDGE_GRAPH.md", r".",
     "knowledge graph contains version-stamped entity references"),
    (".context/*", r"Last Updated", "per-document last-updated stamps"),

    # Append-only records — historical by construction, same class as CHANGELOG.
    # These grow on every session/eval run, so without these two the ratchet
    # breaks the build as a matter of routine rather than on real drift.
    (".context/memories/session_logs/*", r".",
     "session records quote whatever version was current that day; historical by definition"),
    (".agent/eval/results/*", r".",
     "generated eval run artifacts — the version-shaped strings are retrieved document "
     "filenames (e.g. reddit_post_v9.1.0.md) surfacing in search results, never declarations"),
    (".context/audit/*", r".",
     "generated by reconcile_memory.py — quotes past session decisions verbatim, so it "
     "inherits whatever version those decisions named; same class as session_logs"),
    (".agent/EVOLUTION.md", r".",
     "autonomic evolution log — append-only historical record of RSI upgrades, same class as CHANGELOG"),


    # Context data directories — memory bank, raw data, research, cache, archives.
    # These are append-only operational data that quote whatever version was current
    # at time of writing; they are the same class as session_logs (historical by
    # construction, never a version declaration).
    (".context/memory_bank/*", r".",
     "decision logs, active context, and user context quote past versions verbatim"),
    (".context/raw_data/*", r".",
     "ingested data blobs containing version references from past sessions"),
    (".context/archive/*", r".",
     "archived memory bank and legacy data — frozen historical snapshots"),
    (".context/cache/*", r".",
     "cached search results and intermediate data referencing past versions"),
    (".context/research/*", r".",
     "research notes and compilations quoting version-stamped sources"),
    (".context/memories/*", r".",
     "case studies, insights, strategic notes — historical by construction"),
    (".context/specs/*", r".",
     "specification documents pinned to their creation-time version"),
    (".context/self_optimization/*", r".",
     "daily self-RSI logs referencing the version they ran under"),
    (".context/CANONICAL.md", r".",
     "materialized view contains financial figures, subscription costs, and "
     "metrics with dollar signs and version-shaped numbers — never a version declaration"),

    # Wiki pages carry per-page version stamps, pinned to their publication date.
    ("docs/wiki/*", r".",
     "vendored wiki pages carry per-page stamps, same class as Athena-Public.wiki"),

    # Archived and deploy scripts carry their own release versions (v1.0.0, v0.0.1).
    (".agent/scripts/deploy_v1.sh", r".",
     "deploy script for v1.0.0 release — version pinned to that release"),
    (".agent/scripts/archive/*", r".",
     "archived scripts carrying their own pinned versions (install_mu v0.0.1, deploy_v1, etc.)"),

    # Agent config and state files — version references are historical or structural.
    (".agent/config/CAPS.json", r"cap_policy",
     "cap_policy prose mentions the version caps were lifted — historical marker"),
    (".agent/config/accountability_status.template.json", r".",
     "template with example entries quoting past session versions"),
    (".agent/state/*", r".",
     "state files carry decision history referencing past versions"),

    # Script internals — version strings in code that reference other software or
    # fallback defaults, not the project's own version.
    (".agent/scripts/reconcile_memory.py", r".",
     "prompt text listing example version patterns from other software"),
    (".agent/scripts/skill_watcher.py", r".",
     "provenance comment crediting Claude Code v2.1.0"),
    (".agent/scripts/sync_agents_md.py", r".",
     "fallback version default in code — always overwritten by CAPS.json at runtime"),

    # Archived protocols carry provenance and version references from their era.
    (".agent/skills/protocols/archive/*", r".",
     "superseded protocols referencing the version they were created under"),
    (".agent/skills/protocols/meta/*", r".",
     "meta-protocols quoting version examples in diagnostic prose"),
    (".agent/skills/web-launch-gate/SKILL.md", r".",
     "skill references the v9.8.0 security sprint as historical context"),

    # Not this project's version at all.
    (".agent/CONNECTORS.md", r".",
     "connector table references third-party dependency versions (e.g. DuckDB), not Athena's"),
    (".archive/*", r".", "archived subprojects and npm package-lock.json dependency versions"),
    (".agent/config/gate_config.json", r'"version":', "gate config schema version"),
    ("examples/*", r".", "sample and scaffold code carrying its own versions"),
    ("src/athena/cli/init.py", r".", "scaffolding templates written into new projects"),
    (".github/ISSUE_TEMPLATE/*", r"e\.g\.", "placeholder examples in issue forms"),
    ("tests/*", r".", "test fixtures and expected-value literals"),
    ("scripts/generate_demo_gif.py", r"Claude Code", "third-party CLI banner in demo gif generator"),

    # Red-team review documents — analytical prose quoting historical version numbers.
    ("REDTEAM_REVIEW_*.md", r".", "adversarial audit referencing past versions in analytical prose"),
    ("docs/audits/*", r".", "adversarial and workspace audits referencing historical or evaluated versions"),

    # Prose that talks *about* version numbers.
    ("scripts/bump_version.sh", r"e\.g\.", "comment describing the version format"),
    ("scripts/sync_version.py", r".", "this file's docstring describes the drift it fixes"),
    ("*", r"git tag v?[0-9]", "example git tag commands in docs and workflow comments"),
    ("docs/DISCIPLINE.md", r"says v", "illustration of the drift failure mode"),
    ("docs/SPEC_SHEET.md", r"^\s*version:", "example config block"),
]

# ── Discovery debt ratchet ───────────────────────────────────────────────────
# The discovery sweep finds version claims outside every declared surface. In a
# corpus this size most are historical prose that will never be current, and
# declaring or exempting all of them in one pass would mean writing exemptions
# so broad they stop catching anything — the failure this script exists to fix.
#
# So the count is ratcheted instead: the check fails when it goes UP. This is a
# debt figure, not a target. It must only ever move down.
UNDECLARED_BASELINE = 0

TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".yaml", ".yml", ".txt", ".cfg", ".sh"}


def read_ssot_version() -> str | None:
    """Return the version declared in pyproject.toml, or None if unreadable."""
    if not PYPROJECT.exists():
        print(f"ERROR: {PYPROJECT.name} not found.", file=sys.stderr)
        return None

    match = re.search(r'version\s*=\s*"([^"]+)"', PYPROJECT.read_text(encoding="utf-8"))
    if not match:
        print(f"ERROR: version not found in {PYPROJECT.name}.", file=sys.stderr)
        return None

    return match.group(1)


def _swap_capture(match: re.Match, version: str) -> str:
    """Rebuild a match with capture group 1 replaced — works for any surface."""
    whole, base = match.group(0), match.start(0)
    return whole[: match.start(1) - base] + version + whole[match.end(1) - base :]


def _tracked_text_files() -> list[Path]:
    # --others --exclude-standard includes files that are new and not yet
    # committed. Without it a brand-new file is invisible locally and the
    # check only fails in CI, one commit too late.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return [
        ROOT / f
        for f in result.stdout.strip().splitlines()
        if f and Path(f).suffix.lower() in TEXT_SUFFIXES
    ]


def _is_exempt(rel: str, line: str) -> str | None:
    """Reason this version string is exempt, or None."""
    for glob, line_pattern, reason in EXEMPTIONS:
        if fnmatch.fnmatch(rel, glob) and re.search(line_pattern, line):
            return reason
    return None


def check_surfaces(version: str, write: bool) -> tuple[list[str], list[str]]:
    """Verify (or update) every declared surface. Returns (in_sync, drifted)."""
    in_sync, drifted = [], []

    for rel, pattern, label in SURFACES:
        path = ROOT / rel
        if not path.exists():
            print(f"  skipped (not present): {rel} — {label}")
            continue

        content = path.read_text(encoding="utf-8")
        matches = list(re.finditer(pattern, content, re.M))
        if not matches:
            drifted.append(f"{rel} ({label}): declared surface matched nothing")
            print(f"  MISSING: {rel} — {label} pattern matched nothing")
            continue

        found = {m.group(1) for m in matches}
        if found == {version}:
            in_sync.append(f"{rel} ({label})")
            print(f"  in sync: {rel} — {label}")
            continue

        drifted.append(f"{rel} ({label}): {', '.join(sorted(found))}")
        if write:
            path.write_text(
                re.sub(pattern, lambda m: _swap_capture(m, version), content, flags=re.M),
                encoding="utf-8",
            )
            print(f"  updated: {rel} — {label} -> v{version}")
        else:
            print(f"  DRIFT: {rel} — {label} declares {', '.join(sorted(found))}")

    return in_sync, drifted


def discover_undeclared(version: str) -> list[str]:
    """Find version-shaped strings not covered by a surface or an exemption."""
    major_minor = ".".join(version.split(".")[:2])
    # `v` prefixed anything, or a bare version sharing this release's major.minor.
    version_shape = re.compile(
        rf"\bv\d+\.\d+\.\d+[A-Za-z0-9.\-]*|\b{re.escape(major_minor)}\.\d+[A-Za-z0-9.\-]*"
    )
    surface_patterns: dict[str, list[re.Pattern]] = {}
    for rel, pattern, _ in SURFACES:
        surface_patterns.setdefault(rel, []).append(re.compile(pattern, re.M))

    undeclared = []
    for path in _tracked_text_files():
        rel = str(path.relative_to(ROOT))
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            if not version_shape.search(line):
                continue
            if any(p.search(line) for p in surface_patterns.get(rel, [])):
                continue
            if rel == "pyproject.toml" and re.search(r'^version\s*=', line):
                continue
            if _is_exempt(rel, line):
                continue
            undeclared.append(f"{rel}:{line_num}: {line.strip()[:100]}")

    return undeclared


def sync(check: bool) -> int:
    version = read_ssot_version()
    if version is None:
        return 1

    print(f"SSOT version from pyproject.toml: {version}\n")
    print(f"Declared surfaces ({len(SURFACES)}):")
    in_sync, drifted = check_surfaces(version, write=not check)

    print("\nDiscovery sweep across tracked text files:")
    undeclared = discover_undeclared(version)
    regression = len(undeclared) - UNDECLARED_BASELINE
    if undeclared:
        shown = undeclared[:15]
        print(
            f"  {len(undeclared)} undeclared version claim(s) "
            f"(baseline {UNDECLARED_BASELINE}, {regression:+d})"
        )
        for entry in shown:
            print(f"    ? {entry}")
        if len(undeclared) > len(shown):
            print(f"    ... and {len(undeclared) - len(shown)} more (not truncated silently)")
        if regression <= 0 and UNDECLARED_BASELINE:
            print(
                f"  ratchet holding. Lower UNDECLARED_BASELINE to {len(undeclared)} "
                "when you commit this."
            )
    else:
        print("  no undeclared version claims")

    if check and (drifted or regression > 0):
        print("", file=sys.stderr)
        if drifted:
            print(
                f"Version drift in {len(drifted)} declared surface(s):",
                file=sys.stderr,
            )
            for entry in drifted:
                print(f"  {entry}", file=sys.stderr)
            print(
                "Run `python scripts/sync_version.py` and commit the result.",
                file=sys.stderr,
            )
        if regression > 0:
            print(
                f"\n{regression} NEW version claim(s) live outside any declared "
                f"surface ({len(undeclared)} total vs baseline {UNDECLARED_BASELINE}). "
                "Add each to SURFACES so it is kept in sync, or to EXEMPTIONS "
                "with a reason.",
                file=sys.stderr,
            )
        return 1

    if check:
        tail = (
            "no undeclared claims found"
            if not undeclared
            else f"{len(undeclared)} undeclared claim(s) carried as debt (baseline {UNDECLARED_BASELINE})"
        )
        print(f"\nConsistent at v{version}: {len(in_sync)} declared surface(s) checked, {tail}.")
    else:
        print(f"\nVersion sync complete at v{version}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit 1 without writing (CI mode)",
    )
    sys.exit(sync(check=parser.parse_args().check))
