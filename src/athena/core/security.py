"""
athena.core.security — Runtime security hardening.
==================================================

Mitigates CVE-2025-69872 (CVSS 7.3, published 2026-02-11): the ``diskcache``
library (through 5.6.3) deserializes cache entries with ``pickle`` by default.
An attacker who can WRITE to a cache directory can plant a malicious pickle that
executes arbitrary code when the cache is next read. In Athena, ``diskcache``
is only ever a *transitive* dependency (via fastmcp / flashrank) — the package's
own query cache (``athena.core.cache``) is JSON and unaffected.

Threat model (local-first, single-user): an attacker who can write to your
cache directory already has local code execution, so the practical risk is low.
This module applies the advisory's *own* recommended remediation as
defense-in-depth for the shared-volume / container / multi-user case:

    1. Restrict cache/state directory permissions to 0700 (owner-only) so other
       local users cannot plant a malicious pickle.
    2. If ``dspy`` happens to be loaded in-process, swap its ``FanoutCache`` to
       the pickle-free SafeJSONDisk backend (diskcache-community). Best-effort only;
       this module NEVER imports ``dspy`` itself (it is not an Athena dependency).

Everything here is best-effort and must never raise into the boot sequence.

Epistemic status: code-enforced. ``apply_diskcache_hardening()`` runs at boot
(see ``athena.boot.orchestrator``) and the directory chmod is verifiable.
"""

from __future__ import annotations

import logging
import stat
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Owner-only: rwx------ (0o700)
_SECURE_DIR_MODE = stat.S_IRWXU


def _harden_dir(path: Path) -> bool:
    """chmod a directory to 0700 if it exists. Returns True if it was hardened."""
    try:
        if path.is_dir():
            path.chmod(_SECURE_DIR_MODE)
            return True
    except OSError as e:
        logger.debug("Could not harden %s: %s", path, e)
    return False


def harden_cache_directories() -> list[str]:
    """
    Restrict permissions on the cache/state directories Athena controls to
    0700, mitigating CVE-2025-69872 (diskcache pickle RCE) on shared
    filesystems. Returns the list of directories that were hardened.
    """
    hardened: list[str] = []
    try:
        from athena.core.config import AGENT_DIR, PROJECT_ROOT
    except Exception:
        return hardened

    # Deterministic, in-scope set only — no recursive project walk on boot.
    candidates = [
        AGENT_DIR / "state",
        PROJECT_ROOT / ".athena",
        PROJECT_ROOT / ".context" / "cache",
    ]

    for path in candidates:
        if _harden_dir(path):
            hardened.append(str(path))
    return hardened


def _patch_dspy_if_loaded() -> bool:
    """
    If ``dspy`` is ALREADY imported in this process, swap its FanoutCache to the
    pickle-free SafeJSONDisk backend (diskcache-community). Never imports ``dspy``
    itself (not an Athena dependency). Returns True if a patch was applied.
    """
    dspy = sys.modules.get("dspy")
    if dspy is None:
        return False
    try:
        from diskcache_community import FanoutCache, SafeJSONDisk

        cache = getattr(dspy, "cache", None)
        if cache is None:
            return False
        disk_cache = getattr(cache, "disk_cache", None)
        if disk_cache is None or not hasattr(disk_cache, "directory"):
            return False
        if not getattr(cache, "enable_disk_cache", False):
            return False

        directory = disk_cache.directory
        size_limit = disk_cache.size_limit
        disk_cache.close()
        cache.disk_cache = FanoutCache(
            directory=directory,
            size_limit=size_limit,
            disk=SafeJSONDisk.with_options(on_error="miss"),  # pickle-free serialization
        )
        logger.info("Security: dspy disk cache swapped to SafeJSONDisk (pickle-free).")
        return True
    except Exception as e:  # best-effort; never break boot
        logger.debug("dspy cache patch skipped: %s", e)
        return False


def apply_diskcache_hardening() -> dict:
    """
    Boot entry point. Applies CVE-2025-69872 mitigations and returns a summary.
    Never raises.
    """
    try:
        hardened = harden_cache_directories()
    except Exception as e:  # pragma: no cover - defensive
        logger.debug("Cache-dir hardening failed: %s", e)
        hardened = []

    dspy_patched = _patch_dspy_if_loaded()
    return {"dirs_hardened": hardened, "dspy_patched": dspy_patched}


# Backwards-compatible alias — older callers imported this name.
def patch_dspy_cache_security() -> dict:
    """Deprecated name, retained for import compatibility. See
    :func:`apply_diskcache_hardening`."""
    return apply_diskcache_hardening()
