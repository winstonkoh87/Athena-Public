#!/usr/bin/env python3
"""
test_doctor.py — Smoke tests for athena doctor CLI
====================================================

Validates that the doctor module loads, runs checks, and produces
structured results without crashing.
"""

import os
import sys
from pathlib import Path

# Add project root to path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "Athena-Public", "src"))


class TestDoctorModule:
    """Test the doctor diagnostic engine."""

    def test_import(self):
        """Verify the doctor module can be imported."""
        from athena.cli.doctor import ALL_CHECKS, run_doctor

        assert run_doctor is not None
        assert len(ALL_CHECKS) == 16

    def test_check_result_str(self):
        """Verify CheckResult renders correctly."""
        from athena.cli.doctor import PASS, CheckResult

        r = CheckResult("Test", PASS, "All good")
        assert "Test" in str(r)
        assert "All good" in str(r)

    def test_check_result_to_dict(self):
        """Verify CheckResult serializes to dict."""
        from athena.cli.doctor import PASS, CheckResult

        r = CheckResult("Test", PASS, "All good", "details here")
        d = r.to_dict()
        assert d["name"] == "Test"
        assert d["status"] == "pass"
        assert d["message"] == "All good"
        assert d["details"] == "details here"

    def test_run_doctor_returns_int(self, project_root):
        """Verify run_doctor returns an integer exit code."""
        from athena.cli.doctor import run_doctor

        result = run_doctor(root=Path(project_root), quiet=True)
        assert isinstance(result, int)
        assert result in (0, 1)

    def test_individual_checks_return_list(self, project_root):
        """Verify each check function returns a list of CheckResult."""
        from athena.cli.doctor import ALL_CHECKS, CheckResult

        root = Path(project_root)
        for name, check_fn in ALL_CHECKS:
            results = check_fn(root, fix=False)
            assert isinstance(results, list), f"Check {name} did not return a list"
            for r in results:
                assert isinstance(r, CheckResult), (
                    f"Check {name} returned non-CheckResult"
                )
                assert r.status in ("pass", "warn", "fail", "skip"), (
                    f"Check {name} invalid status: {r.status}"
                )


class TestDoctorJson:
    """Test JSON output mode."""

    def test_json_output(self, project_root, capsys):
        """Verify --json produces valid JSON."""
        import json

        from athena.cli.doctor import run_doctor

        run_doctor(root=Path(project_root), output_json=True)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "summary" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)


class TestCommitterValidation:
    """Test committer.py validation logic (without actual git operations)."""

    def test_import(self):
        """Verify committer module can be imported."""
        sys.path.insert(0, os.path.join(root, ".agent", "scripts"))
        from committer import validate_files

        assert validate_files is not None

    def test_blocks_dot(self):
        """Verify '.' is blocked."""
        sys.path.insert(0, os.path.join(root, ".agent", "scripts"))
        from committer import validate_files

        errors = validate_files(["."])
        assert len(errors) > 0
        assert any("not allowed" in e for e in errors)

    def test_blocks_node_modules(self):
        """Verify node_modules paths are blocked."""
        sys.path.insert(0, os.path.join(root, ".agent", "scripts"))
        from committer import validate_files

        errors = validate_files(["node_modules/foo.js"])
        assert len(errors) > 0

    def test_allows_normal_files(self):
        """Verify normal file paths are allowed."""
        sys.path.insert(0, os.path.join(root, ".agent", "scripts"))
        from committer import validate_files

        errors = validate_files(["src/athena/cli/doctor.py", "README.md"])
        assert len(errors) == 0
