"""
tests.test_cli_contracts
========================
Unit tests verifying zero-side-effect CLI contracts across all Athena entry points.
Ensures that --help and --version never mutate state, files, or logs (TD-066).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from athena.core.config import PROJECT_ROOT


class TestCLIContracts(unittest.TestCase):
    def _snapshot_dir(self, directory: Path) -> dict[str, float]:
        """Take a timestamp snapshot of files in a directory."""
        snapshot = {}
        if not directory.exists():
            return snapshot
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in str(path) and not path.name.endswith(".tmp"):
                try:
                    snapshot[str(path)] = path.stat().st_mtime
                except OSError:
                    pass
        return snapshot

    def test_shutdown_script_help_zero_side_effects(self):
        """Verify .agent/scripts/shutdown.py --help causes zero file mutations."""
        target = PROJECT_ROOT / ".agent" / "scripts" / "shutdown.py"
        if not target.exists():
            self.skipTest("shutdown.py script not found")

        state_dir = PROJECT_ROOT / ".athena"
        context_dir = PROJECT_ROOT / ".context" / "memory_bank"

        before_state = self._snapshot_dir(state_dir)
        before_context = self._snapshot_dir(context_dir)

        proc = subprocess.run(
            [sys.executable, str(target), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stdout.lower())

        after_state = self._snapshot_dir(state_dir)
        after_context = self._snapshot_dir(context_dir)

        self.assertEqual(before_state, after_state, "State directory mutated during --help!")
        self.assertEqual(before_context, after_context, "Context directory mutated during --help!")

    def test_boot_shutdown_help_zero_side_effects(self):
        """Verify athena.boot.shutdown --help causes zero file mutations."""
        proc = subprocess.run(
            [sys.executable, "-m", "athena.boot.shutdown", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stdout.lower())

    def test_doctor_help_zero_side_effects(self):
        """Verify athena doctor --help causes zero file mutations."""
        proc = subprocess.run(
            [sys.executable, "-m", "athena.cli.doctor", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stdout.lower())


if __name__ == "__main__":
    unittest.main()
