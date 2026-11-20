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


@pytest.mark.parametrize(
    "ide",
    ["antigravity", "claude", "cursor", "gemini", "kilocode", "roocode"],
)
def test_init_scaffolds_problem_solving_and_decision_workflow(ide: str, tmp_path: Path) -> None:
    """Every text-rule IDE scaffold wires context_gate, lite frame_open, decision_screen, and calibration_status."""
    target = tmp_path / f"workflow-{ide}"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--ide", ide],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    rules_text = (target / EXPECTED_FILES[ide]).read_text(encoding="utf-8")
    for tool_name in ("context_gate", "frame_open", "decision_screen", "calibration_status"):
        assert tool_name in rules_text, f"{ide} rules missing '{tool_name}'"


def test_init_full_excludes_retired_project_state(tmp_path: Path) -> None:
    """Default full init must not create retired .context/project_state.md."""
    target = tmp_path / "full-no-retired"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert not (target / ".context" / "project_state.md").exists()


def test_init_profile_minimal_claude_creates_3_files_and_symlink(tmp_path: Path) -> None:
    """Minimal profile scaffolds 3 Markdown memory files + AGENTS.md + CLAUDE.md without .framework/."""
    target = tmp_path / "minimal-claude"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--profile", "minimal", "--ide", "claude"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert (target / ".context" / "memory_bank" / "activeContext.md").is_file()
    assert (target / ".context" / "memory_bank" / "userContext.md").is_file()
    assert (target / ".context" / "memory_bank" / "decisions.md").is_file()
    assert (target / "AGENTS.md").is_file()
    assert (target / "CLAUDE.md").exists()
    assert not (target / ".framework").exists()


def test_init_profile_hooks_only_preserves_existing_settings(tmp_path: Path) -> None:
    """Hooks-only profile drops PreToolUse guards without .framework/.context and preserves existing settings."""
    target = tmp_path / "hooks-only"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--profile", "hooks-only"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    settings_file = target / ".claude" / "settings.json"
    assert settings_file.is_file()
    import json

    settings_data = json.loads(settings_file.read_text(encoding="utf-8"))
    for group in settings_data["hooks"]["PreToolUse"]:
        assert group["hooks"][0]["onFailure"] == "block"

    assert (target / ".agent" / "scripts" / "security" / "block_secrets.py").is_file()
    assert (target / ".agent" / "scripts" / "security" / "block_ruin.py").is_file()
    assert not (target / ".framework").exists()
    assert not (target / ".context").exists()

    # Generated standalone hooks must fail closed on malformed stdin
    for rel in (
        ".agent/scripts/security/block_secrets.py",
        ".agent/scripts/security/block_ruin.py",
    ):
        malformed = subprocess.run(
            [sys.executable, str(target / rel)],
            input="{bad json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert malformed.returncode == 2, f"{rel} did not fail closed on malformed stdin"

    # Existing .claude/settings.json must never be overwritten
    custom = '{"custom": true}\n'
    settings_file.write_text(custom, encoding="utf-8")
    rerun = subprocess.run(
        [sys.executable, "-m", "athena", "init", str(target), "--profile", "hooks-only"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert rerun.returncode == 0
    assert (target / ".claude" / "settings.json").read_text(encoding="utf-8") == custom
