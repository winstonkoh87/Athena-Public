"""Tests for refactored hook_stop_verify.py and diff-scoped check_latex_leak.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".agent" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_latex_leak import scan_file_diff  # noqa: E402
from hook_stop_verify import (  # noqa: E402
    check_crisis_referral,
    find_missing_cited_paths,
)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )


def _init_temp_repo(repo: Path) -> None:
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@localhost")
    _git(repo, "config", "user.name", "Test User")


def test_crisis_referral_accepts_international_hotlines() -> None:
    crisis_prompt = "I want to end my life tonight."
    for reply in (
        "Please call 988 right now for immediate free support.",
        "Reach out at https://findahelpline.com for confidential crisis support.",
        "Please call SOS at 1-767 immediately.",
    ):
        errs = check_crisis_referral({"prompt": crisis_prompt, "text": reply})
        assert errs == [], f"Unexpected crisis block for reply: {reply}"


def test_crisis_referral_blocks_missing_hotline() -> None:
    errs = check_crisis_referral(
        {
            "prompt": "I am thinking about killing myself.",
            "text": "I am sorry you are going through this.",
        }
    )
    assert len(errs) == 1
    assert "988" in errs[0] and "findahelpline.com" in errs[0]


def test_diff_scoped_latex_ignores_legacy_lines_and_catches_new_leaks(
    tmp_path: Path,
) -> None:
    _init_temp_repo(tmp_path)
    doc = tmp_path / "notes.md"
    legacy_lines = [f"Line {i} safe text." for i in range(1, 10)]
    legacy_lines.append("Legacy complexity is $O(N^2)$ from older notes.")
    doc.write_text("\n".join(legacy_lines) + "\n", encoding="utf-8")
    _git(tmp_path, "add", "notes.md")
    _git(tmp_path, "commit", "-m", "init legacy doc")

    # 1. Clean addition at top must ignore pre-existing line 10 leak
    updated = ["New clean header line."] + legacy_lines
    doc.write_text("\n".join(updated) + "\n", encoding="utf-8")
    assert scan_file_diff(str(doc), repo_root=tmp_path) == []

    # 2. Adding a LaTeX leak on line 2 must flag ONLY line 2
    updated_with_leak = [
        "New clean header line.",
        "Added formula $$E = mc^2$$ here.",
        *legacy_lines,
    ]
    doc.write_text("\n".join(updated_with_leak) + "\n", encoding="utf-8")
    viols = scan_file_diff(str(doc), repo_root=tmp_path)
    assert len(viols) == 1
    assert viols[0][0] == 2

    # 3. Adding LaTeX inside a fenced code block (opened before hunk) must be ignored
    fenced_doc = tmp_path / "fenced.md"
    fenced_doc.write_text("```markdown\nplaceholder\n```\n", encoding="utf-8")
    _git(tmp_path, "add", "fenced.md")
    _git(tmp_path, "commit", "-m", "add fenced doc")
    fenced_doc.write_text("```markdown\nplaceholder\n$O(N)$\n```\n", encoding="utf-8")
    assert scan_file_diff(str(fenced_doc), repo_root=tmp_path) == []

    # 4. Untracked file must be scanned in full
    untracked = tmp_path / "brand_new.md"
    untracked.write_text("New file with $O(N^2)$ leak.\n", encoding="utf-8")
    untracked_viols = scan_file_diff(str(untracked), repo_root=tmp_path)
    assert len(untracked_viols) == 1
    assert untracked_viols[0][0] == 1


def test_find_missing_cited_paths_checks_disk_and_ignores_globs() -> None:
    reply = (
        "Checked `src/athena/mcp_server.py:L10-L20`, `src/athena/*.py`, "
        "and `src/athena/nonexistent_module.py`."
    )
    missing = find_missing_cited_paths(reply, repo_root=REPO_ROOT)
    assert missing == ["src/athena/nonexistent_module.py"]


def test_hook_stop_verify_cli_emits_warning_without_blocking_on_missing_cited_path() -> None:
    payload = json.dumps(
        {"text": "Verified `src/athena/does_not_exist_xyz.py` cleanly."}
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "hook_stop_verify.py")],
        cwd=str(REPO_ROOT),
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["decision"] == "allow"
    assert any("does_not_exist_xyz.py" in w for w in data.get("warnings", []))
