"""Tests for refactored hook_stop_verify.py and diff-scoped check_latex_leak.py."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

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
    assert "988" in errs[0]
    urls = re.findall(r"https?://[^\s)]+", errs[0])
    assert any(urlparse(url).hostname == "findahelpline.com" for url in urls)


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


def test_claude_settings_pretooluse_security_hooks_fail_closed() -> None:
    settings_path = REPO_ROOT / ".claude" / "settings.json"
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    pre_tool_use = data["hooks"]["PreToolUse"]
    by_matcher = {group["matcher"]: group["hooks"] for group in pre_tool_use}
    assert by_matcher["Read|Edit|Write"][0]["onFailure"] == "block"
    assert by_matcher["Bash"][0]["onFailure"] == "block"


def test_block_secrets_fail_closed_behavior() -> None:
    script = SCRIPTS_DIR / "security" / "block_secrets.py"
    blocked = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_input": {"file_path": ".env"}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert blocked.returncode == 2

    malformed = subprocess.run(
        [sys.executable, str(script)],
        input="{bad json",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert malformed.returncode == 2
    assert "fail-closed" in malformed.stderr

    allowed = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_input": {"file_path": "README.md"}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert allowed.returncode == 0


def test_block_ruin_fail_closed_behavior() -> None:
    script = SCRIPTS_DIR / "security" / "block_ruin.py"
    blocked = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_input": {"command": "rm -rf .context"}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert blocked.returncode == 2

    malformed = subprocess.run(
        [sys.executable, str(script)],
        input="{bad json",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert malformed.returncode == 2
    assert "fail-closed" in malformed.stderr

    allowed = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_input": {"command": "ls -la"}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert allowed.returncode == 0


def test_hook_stop_verify_has_no_url_substring_checks() -> None:
    """Guard against CodeQL py/incomplete-url-substring-sanitization (CWE-20)."""
    common_tlds = r"com|org|edu|gov|uk|net|io"
    url_regex = re.compile(
        rf"(?i)^([a-z]*:?//)?\.?([a-z0-9-]+\.)+({common_tlds})(:[0-9]+)?/?$"
    )
    http_url_regex = re.compile(r"(?i)^https?://([a-z0-9-]+\.)+([a-z]+)(:[0-9]+)?/?$")

    def looks_like_url(s: str) -> bool:
        return bool(url_regex.match(s) or http_url_regex.match(s))

    class SubstringSanitizationVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.violations: list[tuple[int, str]] = []

        def visit_Compare(self, node: ast.Compare) -> None:
            left: ast.expr = node.left
            for op, comparator in zip(node.ops, node.comparators, strict=False):
                if isinstance(op, (ast.In, ast.NotIn)):
                    for operand in (left, comparator):
                        if (
                            isinstance(operand, ast.Constant)
                            and isinstance(operand.value, str)
                            and looks_like_url(operand.value)
                        ):
                            self.violations.append((node.lineno, operand.value))
                left = comparator
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in ("startswith", "endswith")
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and looks_like_url(node.args[0].value)
            ):
                self.violations.append((node.lineno, node.args[0].value))
            self.generic_visit(node)

    for target_path in (Path(__file__), SCRIPTS_DIR / "hook_stop_verify.py"):
        tree = ast.parse(target_path.read_text(encoding="utf-8"))
        visitor = SubstringSanitizationVisitor()
        visitor.visit(tree)
        assert visitor.violations == [], (
            f"CodeQL incomplete-url-substring-sanitization pattern detected in {target_path}: "
            f"{visitor.violations}"
        )


def test_block_secrets_expanded_patterns_fail_closed_and_dual_harness(tmp_path: Path, monkeypatch) -> None:
    script = SCRIPTS_DIR / "security" / "block_secrets.py"
    athena_dir = tmp_path / ".athena" / "runtime"
    athena_dir.mkdir(parents=True)
    taint_file = athena_dir / "taint_state.json"
    env = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "HOME": str(tmp_path),
        "ATHENA_ROOT": str(tmp_path),
        "ATHENA_TAINT_STATE_PATH": str(taint_file),
    }

    # Empty non-TTY stdin fails closed (exit 2)
    empty = subprocess.run(
        [sys.executable, str(script)],
        input="",
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert empty.returncode == 2
    assert "fail-closed" in empty.stderr

    # Expanded credential patterns blocked; .env.example allowed
    for blocked_path in (".env.production", "config/credentials.json", "certs/PROD.PEM"):
        res = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": blocked_path}}),
            capture_output=True,
            text=True,
            env=env,
            timeout=10,
        )
        assert res.returncode == 2, f"Expected exit 2 for {blocked_path}"

    example_res = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": ".env.example"}}),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert example_res.returncode == 0

    # Antigravity PreToolUse read_file on .env returns JSON decision=deny (exit 0)
    ag_res = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(
            {
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "read_file", "args": {"Path": ".env"}},
            }
        ),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert ag_res.returncode == 0
    assert json.loads(ag_res.stdout)["decision"] == "deny"

    # Merged taint quarantine blocks Edit (Claude) & write_file (Antigravity), allows Read
    taint_file.write_text(
        json.dumps({"sessions": {"active": {"tainted": True}}}),
        encoding="utf-8",
    )
    canonical_path = str(tmp_path / ".context" / "CANONICAL.md")

    read_tainted = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": canonical_path}}),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert read_tainted.returncode == 0

    edit_tainted = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": canonical_path}}),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert edit_tainted.returncode == 2
    assert "taint quarantine" in edit_tainted.stderr

    ag_write_tainted = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(
            {
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "write_file", "args": {"TargetFile": canonical_path}},
            }
        ),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert ag_write_tainted.returncode == 0
    ag_data = json.loads(ag_write_tainted.stdout)
    assert ag_data["decision"] == "deny"
    assert "taint quarantine" in ag_data["reason"]


def test_block_ruin_empty_stdin_and_antigravity_contract() -> None:
    script = SCRIPTS_DIR / "security" / "block_ruin.py"
    empty = subprocess.run(
        [sys.executable, str(script)],
        input="   ",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert empty.returncode == 2
    assert "fail-closed" in empty.stderr

    ag_block = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(
            {
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf .context"}},
            }
        ),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert ag_block.returncode == 0
    assert json.loads(ag_block.stdout)["decision"] == "deny"


def test_hook_stop_verify_widened_paths_scoping_loop_guard_and_waiver(tmp_path: Path) -> None:
    script = SCRIPTS_DIR / "hook_stop_verify.py"

    # 1. Widened path regex catches missing .context/docs/skills paths and ignores fenced blocks
    reply = (
        "Checked `.context/nonexistent_doc_xyz.md`, `.agent/skills/missing_skill_xyz.md`, "
        "`docs/NONEXISTENT_XYZ.md`, and real `AGENTS.md`.\n"
        "```markdown\n"
        "`docs/IGNORED_IN_CODEBLOCK.md`\n"
        "```\n"
    )
    missing = find_missing_cited_paths(reply, repo_root=REPO_ROOT)
    assert missing == [
        ".context/nonexistent_doc_xyz.md",
        ".agent/skills/missing_skill_xyz.md",
        "docs/NONEXISTENT_XYZ.md",
    ]

    # 2. Missing cited path surfaces systemMessage alongside warnings
    msg_proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        input=json.dumps({"text": "Read `.context/ghost_xyz.md`."}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert msg_proc.returncode == 0
    msg_data = json.loads(msg_proc.stdout)
    assert "systemMessage" in msg_data
    assert "ghost_xyz.md" in msg_data["systemMessage"]

    # 3. stop_hook_active prevents infinite loop on non-crisis unreceipted errors
    reentry_proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        input=json.dumps(
            {
                "text": "Law #1 PASS confirmed by engine.",
                "stop_hook_active": True,
            }
        ),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert reentry_proc.returncode == 0
    reentry_data = json.loads(reentry_proc.stdout)
    assert reentry_data["decision"] == "allow"
    assert any("Loop guard allowed" in w for w in reentry_data.get("warnings", []))

    # 4. Audited waiver allows non-safety error but NEVER waives Protocol 509 crisis
    waived_env = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "HOME": str(tmp_path),
        "ATHENA_HOOK_WAIVER": "build server down; verified manually",
    }
    waived_proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        input=json.dumps({"text": "Law #1 PASS confirmed by engine."}),
        capture_output=True,
        text=True,
        env=waived_env,
        timeout=10,
    )
    assert waived_proc.returncode == 0
    assert json.loads(waived_proc.stdout)["decision"] == "allow"

    crisis_waived = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        input=json.dumps({"prompt": "I want to kill myself", "text": "Sorry to hear that."}),
        capture_output=True,
        text=True,
        env=waived_env,
        timeout=10,
    )
    assert crisis_waived.returncode == 2

    # 5. Turn-scoped Q&A transcript with no write tools ignores unrelated dirty files
    qa_transcript = tmp_path / "qa_transcript.jsonl"
    qa_transcript.write_text(
        json.dumps({"type": "USER_INPUT", "content": "Explain hooks"}) + "\n"
        + json.dumps({"source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Hooks run scripts."}) + "\n",
        encoding="utf-8",
    )
    qa_proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        input=json.dumps({"transcriptPath": str(qa_transcript)}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert qa_proc.returncode == 0
    assert json.loads(qa_proc.stdout)["decision"] == "allow"


def test_hook_post_edit_lint_single_file_feedback(tmp_path: Path) -> None:
    script = SCRIPTS_DIR / "hook_post_edit_lint.py"

    # 1. Broken Python syntax returns exit 0 with additionalContext
    bad_py = tmp_path / "broken.py"
    bad_py.write_text("def broken(:\n    pass\n", encoding="utf-8")
    py_proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(bad_py)}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert py_proc.returncode == 0
    py_out = json.loads(py_proc.stdout)
    assert py_out["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "syntax error" in py_out["hookSpecificOutput"]["additionalContext"].lower()

    # 2. Untracked markdown file with LaTeX leak returns additionalContext
    bad_md = tmp_path / "leak.md"
    bad_md.write_text("Complexity is $O(N^2)$.\n", encoding="utf-8")
    md_proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(bad_md)}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert md_proc.returncode == 0
    md_out = json.loads(md_proc.stdout)
    assert "LaTeX leak" in md_out["hookSpecificOutput"]["additionalContext"]

    # 3. Clean file produces no violation output
    good_py = tmp_path / "clean.py"
    good_py.write_text("def ok() -> int:\n    return 1\n", encoding="utf-8")
    clean_proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(good_py)}}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert clean_proc.returncode == 0
    assert clean_proc.stdout.strip() == ""
