"""
Tests for StructuredRuinCheck (src/athena/core/ruin_structured.py).
"""

from pathlib import Path

from athena.core.ruin_structured import StructuredRuinCheck


def test_safe_commands():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("git status")
    assert allowed is True
    assert len(flags) == 0

def test_destructive_context_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -rf .context")
    assert allowed is False
    assert "targets_context_memory" in flags

def test_destructive_agent_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -r -f .agent/config")
    assert allowed is False
    assert "targets_agent_config" in flags

def test_root_directory_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -rf /")
    assert allowed is False
    assert "targets_root_directory" in flags

def test_find_delete_bypass_blocked():
    """Verify that find -delete targeting .context is blocked (Audit Bypass 1)."""
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("find .context -delete")
    assert allowed is False
    assert "find_destructive_call_on_protected_path" in flags

def test_find_exec_rm_blocked():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("find .context -type f -exec rm -f {} +")
    assert allowed is False
    assert "find_destructive_call_on_protected_path" in flags

def test_mv_context_bypass_blocked():
    """Verify that moving .context away is blocked (Audit Bypass 2)."""
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("mv .context /tmp/x")
    assert allowed is False
    assert "moving_protected_memory_path" in flags

def test_mv_agent_bypass_blocked():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("mv .agent /tmp/stolen_agent")
    assert allowed is False
    assert "moving_protected_memory_path" in flags

def test_git_destructive_commands_blocked():
    checker = StructuredRuinCheck(Path("."))
    assert checker.check_command("git reset --hard HEAD~1")[0] is False
    assert checker.check_command("git push origin main --force")[0] is False
    assert checker.check_command("git clean -fd")[0] is False
    assert checker.check_command("git checkout -- .")[0] is False

def test_redirection_truncation_blocked():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("echo '' > .context/CANONICAL.md")
    assert allowed is False
    assert "truncating_redirection_on_protected_path" in flags

def test_python_c_destructive_blocked():
    checker = StructuredRuinCheck(Path("."))
    cmd = 'python3 -c "import shutil; shutil.rmtree(\'.context\')"'
    allowed, flags = checker.check_command(cmd)
    assert allowed is False
    assert "python_destructive_call" in flags

def test_safe_read_commands_allowed():
    checker = StructuredRuinCheck(Path("."))
    assert checker.check_command("cat .context/CANONICAL.md")[0] is True
    assert checker.check_command("ls -la .context/memories")[0] is True
    assert checker.check_command("python3 -m pytest tests/")[0] is True
    assert checker.check_command("git log -n 5")[0] is True

def test_read_only_multi_path_commands_allowed():
    """Verify that harmless read-only commands targeting multiple protected paths are NOT blocked."""
    checker = StructuredRuinCheck(Path("."))
    assert checker.check_command("grep -rn 'def ' .agent/scripts/a.py .agent/scripts/b.py")[0] is True
    assert checker.check_command("wc -l .agent/scripts/a.py .agent/scripts/b.py")[0] is True
    assert checker.check_command("sed -n '1,10p' .agent/scripts/a.py .agent/scripts/b.py")[0] is True
    assert checker.check_command("cat .context/CANONICAL.md .agent/config/CAPS.json")[0] is True


def test_secret_file_shell_reads_blocked_and_examples_allowed():
    checker = StructuredRuinCheck(Path("."))
    for bad_cmd in (
        "cat .env",
        "head -n 5 .env.production",
        "grep SECRET .env.local",
        "cat ~/.ssh/id_rsa",
        "echo ok && cat .env",
        "python3 -c \"print(open('.env').read())\"",
    ):
        allowed, flags = checker.check_command(bad_cmd)
        assert allowed is False, f"Expected block for: {bad_cmd}"
        assert "secret_file_shell_access" in flags

    for safe_cmd in (
        "cat .env.example",
        "cat .context/CANONICAL.md",
        "grep '.env' src/athena/cli/init.py",
        "python3 -c \"print(open('.env.example').read())\"",
    ):
        allowed, _ = checker.check_command(safe_cmd)
        assert allowed is True, f"Expected allow for: {safe_cmd}"

