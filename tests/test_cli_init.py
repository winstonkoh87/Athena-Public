"""Tests for athena init CLI — every IDE choice must work.

Red Run proof: before this test existed, `athena init --ide claude` crashed
with `invalid choice: 'claude'` because the CLI parser didn't list it.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# All IDE choices that __main__.py advertises
ALL_IDE_CHOICES = [
    "antigravity",
    "claude",
    "cursor",
    "vscode",
    "gemini",
    "kilocode",
    "roocode",
    "zoocode",
]

# Expected output files per IDE
EXPECTED_FILES = {
    "antigravity": "AGENTS.md",
    "claude": "CLAUDE.md",
    "cursor": ".cursor/rules.md",
    "vscode": ".vscode/settings.json",
    "gemini": ".gemini/AGENTS.md",
    "kilocode": ".kilocode/rules/athena.md",
    "roocode": ".roo/rules/athena.md",
    "zoocode": ".roo/rules/athena.md",  # alias for roocode
}


@pytest.mark.parametrize("ide", ALL_IDE_CHOICES)
def test_init_ide_choice_accepted(ide: str, tmp_path: Path) -> None:
    """Every --ide value listed in the CLI must be accepted without error."""
    target = tmp_path / f"test-{ide}"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--ide", ide],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"athena init --ide {ide} failed (exit {result.returncode}):\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


@pytest.mark.parametrize("ide", ALL_IDE_CHOICES)
def test_init_ide_creates_expected_file(ide: str, tmp_path: Path) -> None:
    """Every --ide value must create the expected config file."""
    target = tmp_path / f"test-{ide}"
    target.mkdir()
    subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--ide", ide],
        capture_output=True,
        text=True,
        timeout=30,
    )
    expected = target / EXPECTED_FILES[ide]
    assert expected.exists(), (
        f"athena init --ide {ide} did not create {EXPECTED_FILES[ide]}"
    )


def test_init_no_author_in_output(tmp_path: Path) -> None:
    """The init output must not contain [AUTHOR] redaction artifacts."""
    target = tmp_path / "test-author"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "[AUTHOR]" not in result.stdout, (
        f"[AUTHOR] redaction artifact leaked into init output:\n{result.stdout}"
    )
    assert "[AUTHOR]" not in result.stderr, (
        f"[AUTHOR] redaction artifact leaked into init stderr:\n{result.stderr}"
    )


def test_init_docs_url_is_valid(tmp_path: Path) -> None:
    """The docs URL printed by init must point to a real GitHub repo."""
    target = tmp_path / "test-url"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "github.com/winstonkoh87/Athena-Public" in result.stdout, (
        f"Expected public repo URL in init output, got:\n{result.stdout}"
    )


def test_init_creates_workspace_structure(tmp_path: Path) -> None:
    """Basic init must create the core directory structure."""
    target = tmp_path / "test-structure"
    target.mkdir()
    subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Core directories that init_workspace always creates
    for d in [".framework", ".context", ".agent"]:
        assert (target / d).is_dir(), f"init did not create {d}/"


def test_choices_match_handlers() -> None:
    """The argparse choices in __main__.py must match _create_ide_config handlers.

    Prevents the exact regression that caused the original bug: adding an IDE
    to docs/README but forgetting to add it to the parser choices or handler.
    """
    import inspect

    from athena.cli.init import _create_ide_config

    source = inspect.getsource(_create_ide_config)
    for ide in ALL_IDE_CHOICES:
        assert f'"{ide}"' in source or f"'{ide}'" in source, (
            f"IDE '{ide}' is in CLI choices but has no handler in _create_ide_config"
        )
