#!/usr/bin/env python3
"""Create the project venv and install the locked retrieval runtime.

Why this exists
---------------
`pyproject.toml` declared twelve dependencies and nothing ever installed them.
The Homebrew interpreter that every workflow reaches via a bare `python3` had
neither the Supabase client nor python-dotenv, so `.env` never loaded, the
vector channel raised on every call, and `search.py` swallowed it per-channel
and returned a smaller candidate pool. Six eval runs recorded a "retrieval
regression" that was really an uninstalled dependency (TD-064).

Declaring dependencies is not installing them. This script closes that gap and
verifies the result rather than assuming it.

Usage
-----
    python3 .agent/scripts/bootstrap_env.py            # create + install + verify
    python3 .agent/scripts/bootstrap_env.py --check    # verify only, exit 1 if broken
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python3"
LOCKFILE = PROJECT_ROOT / ".agent" / "config" / "requirements.lock"

sys.path.insert(0, str(Path(__file__).parent))
from _venv_bootstrap import REQUIRED, _candidate_venvs, _missing  # noqa: E402


def _resolve_venv() -> Path | None:
    """First existing candidate venv. In a worktree this is the main checkout's."""
    for cand in _candidate_venvs(PROJECT_ROOT):
        if cand.exists():
            return cand
    return None


def _run(cmd: list[str], desc: str) -> bool:
    print(f"   → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ✗ {desc} failed:\n{result.stderr[-1500:]}", file=sys.stderr)
        return False
    return True


def check() -> int:
    """Verify the venv can actually import what retrieval needs."""
    venv = _resolve_venv()
    if venv is None:
        print(
            f"✗ No venv found for {PROJECT_ROOT}. Run without --check to create one.",
            file=sys.stderr,
        )
        return 1

    missing = _missing(str(venv))
    if missing:
        # Not "not installed" — unusable. A shadowed namespace package imports
        # fine and lacks the symbol we call, which is why this probes usability.
        print(f"✗ Unusable in {venv}: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"✓ All {len(REQUIRED)} retrieval deps usable in {venv}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Verify only; do not create or install."
    )
    args = parser.parse_args()

    if args.check:
        return check()

    if not VENV_PYTHON.exists():
        # --system-site-packages: some deps (e.g. the supabase client on this
        # host) are only present system-wide, and inheriting them avoids
        # reinstalling a working copy.
        if not _run(
            [sys.executable, "-m", "venv", "--system-site-packages", str(VENV_DIR)],
            f"creating venv at {VENV_DIR}",
        ):
            return 1

    if not LOCKFILE.exists():
        print(f"✗ Lockfile missing: {LOCKFILE}", file=sys.stderr)
        return 1

    if not _run(
        [str(VENV_PYTHON), "-m", "pip", "install", "-q", "-r", str(LOCKFILE)],
        f"installing from {LOCKFILE.name}",
    ):
        return 1

    # Verify rather than declare success. The whole failure class this script
    # exists to prevent was a green report over an unverified property.
    return check()


if __name__ == "__main__":
    sys.exit(main())
