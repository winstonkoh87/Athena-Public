"""Re-exec into the project venv when the current interpreter lacks the deps.

Why this exists
---------------
255 call sites across `.agent/` and `.claude/` invoke a bare `python3` — the
workflows (`start.md`, `end.md`), the hooks, the docs, and the scripts
themselves. That resolves through PATH to whatever interpreter is first, which
on this machine is a Homebrew build with none of `pyproject.toml`'s twelve
dependencies installed. The result was not a crash: `search.py` catches its own
import failures per channel, so retrieval silently ran on a fraction of its
corpus and the eval harness recorded six sub-baseline runs nobody could explain
(TD-064).

Editing all 255 call sites is neither feasible nor durable — the next one
written will be a bare `python3` too, and a pinned path breaks the day someone
clones to a different machine. So the entry point self-heals instead: if the
deps are missing *here* and a venv has them, re-exec into that venv.

This is a repair, not a substitute for installing dependencies. If no capable
interpreter exists, we continue on the current one and let the caller's own
degradation reporting surface it — never silently.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Sentinel: set before re-exec so a venv that is *itself* missing deps cannot
# ping-pong forever. One hop is the entire budget.
_REEXEC_FLAG = "ATHENA_VENV_REEXEC"

# The imports that decide whether retrieval runs whole or in fragments.
# dotenv  -> .env never loads -> SUPABASE_*/GOOGLE_API_KEY absent -> vector channel dead
# supabase-> unified vector RPC unavailable
# onnxruntime/tokenizers -> reranker no-ops, results keep RRF order
REQUIRED = ("dotenv", "supabase", "onnxruntime", "tokenizers")

# A module can be importable and still be the wrong thing. The repo contains a
# `supabase/` directory (CLI config: migrations, config.toml) which Python treats
# as a namespace package whenever the project root lands on sys.path — so
# `find_spec("supabase")` succeeds, `import supabase` succeeds, and only
# `create_client` is missing. Probing for presence rather than usability is the
# same indicator-vs-property mistake that produced TD-064, so probe the symbol.
_REQUIRED_ATTR = {"supabase": "create_client"}

_PROBE_SRC = """
import sys
missing = []
for mod, attr in {pairs!r}:
    try:
        m = __import__(mod)
        if attr and not hasattr(m, attr):
            missing.append(mod)
    except Exception:
        missing.append(mod)
print(','.join(missing))
"""


def _probe_pairs() -> list:
    return [(m, _REQUIRED_ATTR.get(m)) for m in REQUIRED]


def _missing(interpreter: str | None = None) -> list[str]:
    """Which of REQUIRED are unusable by `interpreter` (default: us)?

    "Unusable" means the import fails *or* the module lacks the symbol we
    actually call — a shadowed namespace package imports fine and is useless.
    """
    if interpreter is None or interpreter == sys.executable:
        missing = []
        for mod, attr in _probe_pairs():
            try:
                m = __import__(mod)
                if attr and not hasattr(m, attr):
                    missing.append(mod)
            except Exception:
                missing.append(mod)
        return missing

    probe = _PROBE_SRC.format(pairs=_probe_pairs())
    try:
        out = subprocess.run(
            [interpreter, "-c", probe], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return list(REQUIRED)
    if out.returncode != 0:
        return list(REQUIRED)
    return [m for m in out.stdout.strip().split(",") if m]


def _candidate_venvs(project_root: Path) -> list[Path]:
    """Venv interpreters worth probing, most specific first."""
    cands = [project_root / ".venv" / "bin" / "python3"]
    # During parallel work `project_root` is a git worktree and `.venv` lives in
    # the main checkout, so resolve that too.
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_root),
        )
        if common.returncode == 0 and common.stdout.strip():
            cands.append(Path(common.stdout.strip()).parent / ".venv" / "bin" / "python3")
    except (OSError, subprocess.SubprocessError):
        pass
    return cands


def ensure_deps(
    project_root: Path, *, quiet: bool = False, extra: tuple[str, ...] = ()
) -> list[str]:
    """Re-exec into a capable venv if this interpreter is missing deps.

    `extra` names modules this particular caller needs beyond REQUIRED — e.g.
    shutdown.py needs `yaml`, which retrieval does not (TD-062).

    Returns the still-missing modules. An empty list means we are good — either
    we already were, or we are now running inside the venv we re-exec'd into
    (in which case this call does not return at all).
    """
    global REQUIRED
    if extra:
        REQUIRED = tuple(dict.fromkeys((*REQUIRED, *extra)))

    if os.environ.get(_REEXEC_FLAG):
        # We are the re-exec'd child. Report honestly; do not hop again.
        return _missing()

    missing = _missing()
    if not missing:
        return []

    for cand in _candidate_venvs(project_root):
        if not cand.exists():
            continue
        if _missing(str(cand)):
            continue
        # Rebuild argv from a resolved script path. sys.argv[0] is whatever the
        # caller typed — relative, or not a file at all when we were loaded via
        # `-c` or importlib. Re-execing on a bad argv[0] produces a confusing
        # "can't open file" from the *new* interpreter, so verify first and
        # decline to hop if we cannot name our own entry point.
        script = sys.argv[0] if sys.argv else ""
        if not script or not Path(script).is_file():
            if not quiet:
                print(
                    f"   ⚠️  missing {', '.join(missing)}; cannot re-exec "
                    f"(entry point {script!r} is not a file). Run this as a "
                    f"script, or invoke {cand} directly.",
                    file=sys.stderr,
                )
            return missing

        env = dict(os.environ, **{_REEXEC_FLAG: "1"})
        if not quiet:
            print(
                f"   ↻ re-exec into {cand} (this interpreter lacks: "
                f"{', '.join(missing)})",
                file=sys.stderr,
            )
        try:
            os.execve(str(cand), [str(cand), str(Path(script).resolve()), *sys.argv[1:]], env)
        except OSError:
            continue  # try the next candidate rather than dying here

    if not quiet:
        print(
            f"   ⚠️  DEGRADED — missing {', '.join(missing)} on {sys.executable} and no "
            f"venv has them.\n"
            f"      Retrieval will run on a reduced channel set. "
            f"Fix: python3 -m venv .venv && .venv/bin/python -m pip install -e .",
            file=sys.stderr,
        )
    return missing
