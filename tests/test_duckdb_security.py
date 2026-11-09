"""
tests.test_duckdb_security
==========================
Regression tests for DuckDB MCP security: SQL injection prevention,
table name validation, SQL escaping, and export directory confinement.
"""

from pathlib import Path

import pytest

from athena.duckdb_mcp_server import (
    _escape_sql_literal,
    _validate_export_path,
    _validate_table_name,
    create_table_from_file,
)


class TestDuckDBSecurity:
    def test_validate_table_name_valid(self):
        assert _validate_table_name("valid_table_123") == "valid_table_123"
        assert _validate_table_name("_trades") == "_trades"
        assert _validate_table_name("DATA") == "DATA"

    def test_validate_table_name_invalid_injection(self):
        invalids = [
            "table; DROP TABLE users; --",
            "table name with spaces",
            "table' OR '1'='1",
            "123starts_with_number",
            "table-hyphen",
            "table\"quote",
            "",
            "a" * 65,  # too long
        ]
        for bad in invalids:
            with pytest.raises(ValueError):
                _validate_table_name(bad)

    def test_escape_sql_literal(self):
        assert _escape_sql_literal("normal_path.csv") == "normal_path.csv"
        assert _escape_sql_literal("user's_file.csv") == "user''s_file.csv"
        assert _escape_sql_literal("a'b'c") == "a''b''c"

    def test_validate_export_path_sensitive_dirs(self):
        with pytest.raises(PermissionError):
            _validate_export_path(Path("/Users/example/.ssh/id_rsa.csv"))

        with pytest.raises(PermissionError):
            _validate_export_path(Path("/Users/example/project/.git/compromised.parquet"))

        with pytest.raises(PermissionError):
            _validate_export_path(Path("/Users/example/.aws/credentials.json"))

        # Safe path
        _validate_export_path(Path("/tmp/safe_export.csv"))

    def test_create_table_from_file_blocks_injection(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,val\n1,foo\n2,bar\n")

        # Unwrapped function or tool call
        fn = getattr(create_table_from_file, "fn", create_table_from_file)
        res = fn(str(csv_file), "bad; DROP TABLE dummy; --")
        assert "error" in res
        assert "Invalid table name" in res["error"]
