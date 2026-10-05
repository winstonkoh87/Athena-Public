"""
tests.test_benchmark_kv_cache
==============================
Unit tests for benchmark_kv_cache.py verifying synthetic context generation,
table formatting, and CLI zero-mutation contracts.
"""

import subprocess
import sys
import unittest
from pathlib import Path

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from benchmark_kv_cache import (
    format_markdown_table,
    generate_synthetic_code_context,
)


class TestBenchmarkKVCache(unittest.TestCase):
    def test_cli_help(self):
        """Verify benchmark_kv_cache.py --help exits 0 without error."""
        script_path = PROJECT_ROOT / "scripts" / "benchmark_kv_cache.py"
        res = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Benchmark TTFT, throughput, and VRAM scaling", res.stdout)

    def test_synthetic_context_length(self):
        """Verify context generator produces approximate target token length."""
        ctx_2k = generate_synthetic_code_context(2048)
        self.assertTrue(len(ctx_2k) > 5000)
        self.assertIn("verify_data_contract", ctx_2k)

        ctx_8k = generate_synthetic_code_context(8192)
        self.assertTrue(len(ctx_8k) > len(ctx_2k))

    def test_format_markdown_table(self):
        """Verify markdown table formatting with valid trials."""
        results = [
            {
                "tokens": 2048,
                "status": "ok",
                "ttft_ms": 350.0,
                "total_ms": 500.0,
                "tokens_generated": 5,
                "tps": 33.3,
                "vram_mb": 400,
            },
            {
                "tokens": 32768,
                "status": "ok",
                "ttft_ms": 14000.0,
                "total_ms": 14200.0,
                "tokens_generated": 5,
                "tps": 25.0,
                "vram_mb": 8500,
            },
        ]
        table = format_markdown_table(
            results, "qwen2.5-coder:14b", "http://localhost:11434/v1"
        )
        self.assertIn("| 2K | 2,048 | 350.0 ms | 40.0x | 33.3 | 400 MB |", table)
        self.assertIn(
            "| 32K | 32,768 | 14,000.0 ms | Baseline | 25.0 | 8,500 MB |", table
        )


if __name__ == "__main__":
    unittest.main()
