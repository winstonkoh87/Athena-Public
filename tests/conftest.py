"""
conftest.py — Global test configuration for Athena SDK test suite.

Handles graceful skipping of tests that depend on modules not present
in the public distribution (private-only modules are synced separately).
"""

import importlib
import os
import sys
from pathlib import Path

import pytest

# Add project root and .agent/scripts to Python path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "src"))
sys.path.insert(0, os.path.join(root, ".agent", "scripts"))


def _can_import(module_name: str) -> bool:
    """Check if a module is importable without actually importing it."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False


@pytest.fixture
def project_root():
    from pathlib import Path
    return Path(__file__).resolve().parent.parent


# Modules that exist in the private repo but may not be synced to public
_OPTIONAL_MODULES = {
    "athena.core.sandbox": "Docker sandbox execution",
    "athena.core.skill_nudge": "Skill nudge engine",
    "athena.core.session_efficiency": "Session efficiency metrics",
    "athena.core.edge_node": "iOS edge node webhook",
    "athena.sessions": "Agent-to-agent RPC sessions",
    "athena.core.skill_telemetry": "Skill telemetry tracking",
    "athena.core.doctor": "Health check doctor module",
    "athena.core.committer": "Commit validation module",
    "committer": "Legacy committer script",
}


def pytest_collection_modifyitems(config, items):
    """Skip tests whose required modules are not available."""
    skip_markers = {}
    for mod, desc in _OPTIONAL_MODULES.items():
        if not _can_import(mod):
            skip_markers[mod] = pytest.mark.skip(
                reason=f"Module '{mod}' ({desc}) not available in this distribution"
            )

    for item in items:
        # Check if the test module's source imports any unavailable module
        source_file = str(item.fspath)
        try:
            with open(source_file, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        for mod, marker in skip_markers.items():
            # Check for direct imports of the missing module
            short_name = mod.rsplit(".", 1)[-1]
            if (
                f"from {mod}" in content
                or f"import {mod}" in content
                or f'"{short_name}"' in content
            ):
                item.add_marker(marker)
                break
