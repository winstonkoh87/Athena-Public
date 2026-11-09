"""
athena.duckdb_mcp_server
========================

Lightweight MCP server exposing DuckDB as a local-first OLAP engine.
Provides instant SQL queries over CSV, Parquet, and JSON files on disk
without requiring boilerplate Python scripts.

Transport: stdio (default).

Usage:
    python -m athena.duckdb_mcp_server
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

import duckdb
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server Init
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="duckdb-local",
    version="1.0.0",
    instructions=(
        "DuckDB Local OLAP Engine — instant SQL queries over local CSV, "
        "Parquet, and JSON files. No network calls, no API keys, fully "
        "offline. Use query() for ad-hoc SQL, profile() to auto-inspect "
        "a file's schema and stats, and list_tables() to see what's loaded."
    ),
)

logger = logging.getLogger("athena.duckdb_mcp")

# Persistent in-memory connection (survives across tool calls within a session)
_conn: duckdb.DuckDBPyConnection | None = None

# Safety: max rows returned per query to avoid context window flooding
MAX_ROWS = 500
# Safety: max file size for auto-profile (500 MB)
MAX_PROFILE_BYTES = 500 * 1024 * 1024


def _get_conn() -> duckdb.DuckDBPyConnection:
    """Lazy-init a persistent in-memory DuckDB connection."""
    global _conn
    if _conn is None:
        _conn = duckdb.connect(":memory:")
        # Enable httpfs for remote parquet if needed later
        try:
            _conn.execute("INSTALL httpfs; LOAD httpfs;")
        except Exception:
            pass  # Optional extension, non-fatal
    return _conn


def _resolve_path(file_path: str) -> Path:
    """Resolve and validate a file path. Expand ~ and env vars."""
    p = Path(os.path.expanduser(os.path.expandvars(file_path))).resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return p


TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
SENSITIVE_TARGET_DIRS = {".git", ".ssh", ".gnupg", ".aws", ".env"}


def _validate_table_name(name: str) -> str:
    """Validate table name against alphanumeric/underscore pattern (CWE-89 SQL injection shield)."""
    cleaned = (name or "").strip()
    if not TABLE_NAME_PATTERN.match(cleaned):
        raise ValueError(
            f"Invalid table name: '{name}'. Table names must start with a letter or underscore "
            "and contain only alphanumeric/underscore characters (max 64 chars)."
        )
    return cleaned


def _escape_sql_literal(val: str | Path) -> str:
    """Escape single quotes in SQL string literals to prevent injection/syntax errors."""
    return str(val).replace("'", "''")


def _validate_export_path(path: Path) -> None:
    """Ensure export path does not write to sensitive system or credential directories."""
    resolved = path.resolve()
    for part in resolved.parts:
        if part in SENSITIVE_TARGET_DIRS:
            raise PermissionError(
                f"Security restriction: export target path cannot reside inside sensitive directory '{part}'."
            )


def _format_results(rows: list[tuple], columns: list[str]) -> dict[str, Any]:
    """Format DuckDB results into a clean dict."""
    return {
        "columns": columns,
        "row_count": len(rows),
        "data": [dict(zip(columns, row, strict=False)) for row in rows],
    }


# ---------------------------------------------------------------------------
# TOOL: query
# ---------------------------------------------------------------------------


@mcp.tool(tags={"analytics", "sql", "data"})
def query(
    sql: str,
    max_rows: int = 200,
) -> dict[str, Any]:
    """Execute a SQL query against DuckDB (in-memory or over local files).

    Supports direct file queries like:
        SELECT * FROM read_csv('path/to/file.csv') LIMIT 10
        SELECT * FROM read_parquet('~/data/trades.parquet')
        SELECT * FROM read_json('data.json')

    Also supports queries against tables created with create_table_from_file().

    Args:
        sql: The SQL query to execute. Supports full DuckDB SQL dialect.
        max_rows: Maximum rows to return (default 200, max 500).
    """
    conn = _get_conn()
    effective_max = min(max_rows, MAX_ROWS)

    try:
        result = conn.execute(sql)
        columns = [desc[0] for desc in result.description] if result.description else []
        rows = result.fetchmany(effective_max)
        total_count = len(rows)

        # Check if there are more rows
        has_more = False
        if total_count == effective_max:
            extra = result.fetchone()
            if extra is not None:
                has_more = True

        output = _format_results(rows, columns)
        if has_more:
            output["truncated"] = True
            output["note"] = (
                f"Results truncated to {effective_max} rows. "
                f"Use LIMIT/OFFSET or aggregation to manage large results."
            )
        return output

    except Exception as e:
        return {"error": str(e), "sql": sql}


# ---------------------------------------------------------------------------
# TOOL: profile
# ---------------------------------------------------------------------------


@mcp.tool(tags={"analytics", "data", "schema"})
def profile(
    file_path: str,
    sample_rows: int = 5,
) -> dict[str, Any]:
    """Auto-inspect a local data file: detect schema, row count, and show samples.

    Supports CSV, TSV, Parquet, JSON, and JSON Lines files.

    Args:
        file_path: Path to the data file (supports ~ expansion).
        sample_rows: Number of sample rows to include (default 5).
    """
    conn = _get_conn()

    try:
        p = _resolve_path(file_path)

        # Size guard
        if p.stat().st_size > MAX_PROFILE_BYTES:
            return {
                "error": f"File too large for auto-profile: {p.stat().st_size / 1e6:.1f} MB "
                f"(limit: {MAX_PROFILE_BYTES / 1e6:.0f} MB). Use query() with LIMIT instead."
            }

        escaped_p = _escape_sql_literal(p)
        suffix = p.suffix.lower()
        if suffix in (".csv", ".tsv"):
            read_fn = f"read_csv('{escaped_p}', auto_detect=true)"
        elif suffix in (".parquet", ".pq"):
            read_fn = f"read_parquet('{escaped_p}')"
        elif suffix in (".json", ".jsonl", ".ndjson"):
            read_fn = f"read_json('{escaped_p}', auto_detect=true)"
        else:
            return {"error": f"Unsupported file type: {suffix}. Supported: .csv, .tsv, .parquet, .json, .jsonl"}

        # Schema
        schema_result = conn.execute(f"DESCRIBE SELECT * FROM {read_fn}")
        schema_cols = [desc[0] for desc in schema_result.description]
        schema_rows = schema_result.fetchall()
        schema = [dict(zip(schema_cols, row, strict=False)) for row in schema_rows]

        # Row count
        count_result = conn.execute(f"SELECT COUNT(*) as total FROM {read_fn}")
        count_row = count_result.fetchone()
        total_rows = count_row[0] if count_row else 0

        # Sample
        sample_result = conn.execute(f"SELECT * FROM {read_fn} LIMIT {min(sample_rows, 20)}")
        sample_cols = [desc[0] for desc in sample_result.description]
        sample_data = sample_result.fetchall()
        samples = [dict(zip(sample_cols, row, strict=False)) for row in sample_data]

        # Basic stats for numeric columns
        numeric_cols = [s["column_name"] for s in schema if s.get("column_type", "").upper() in (
            "BIGINT", "INTEGER", "SMALLINT", "TINYINT", "DOUBLE", "FLOAT", "DECIMAL",
            "HUGEINT", "UBIGINT", "UINTEGER", "USMALLINT", "UTINYINT",
        )]

        stats = {}
        if numeric_cols:
            stat_exprs = []
            for col in numeric_cols[:10]:  # Cap at 10 numeric columns
                safe_col = f'"{col}"'
                stat_exprs.append(
                    f"MIN({safe_col}) as \"{col}_min\", "
                    f"MAX({safe_col}) as \"{col}_max\", "
                    f"AVG({safe_col}) as \"{col}_avg\", "
                    f"STDDEV({safe_col}) as \"{col}_std\""
                )

            stats_sql = f"SELECT {', '.join(stat_exprs)} FROM {read_fn}"
            stats_result = conn.execute(stats_sql)
            stats_row = stats_result.fetchone() or ()
            stats_names = [desc[0] for desc in stats_result.description]
            raw_stats = dict(zip(stats_names, stats_row, strict=False))

            for col in numeric_cols[:10]:
                stats[col] = {
                    "min": raw_stats.get(f"{col}_min"),
                    "max": raw_stats.get(f"{col}_max"),
                    "avg": round(raw_stats.get(f"{col}_avg", 0) or 0, 4),
                    "std": round(raw_stats.get(f"{col}_std", 0) or 0, 4),
                }

        return {
            "file": str(p),
            "file_size_mb": round(p.stat().st_size / 1e6, 2),
            "total_rows": total_rows,
            "column_count": len(schema),
            "schema": schema,
            "numeric_stats": stats if stats else None,
            "sample_data": samples,
            "read_function": read_fn,
        }

    except Exception as e:
        return {"error": str(e), "file_path": file_path}


# ---------------------------------------------------------------------------
# TOOL: create_table_from_file
# ---------------------------------------------------------------------------


@mcp.tool(tags={"analytics", "data"})
def create_table_from_file(
    file_path: str,
    table_name: str,
) -> dict[str, Any]:
    """Load a local data file into a named in-memory DuckDB table for repeated querying.

    This avoids re-reading the file on every query() call. The table persists
    for the duration of the MCP session.

    Args:
        file_path: Path to the data file (CSV, Parquet, JSON).
        table_name: Name for the in-memory table.
    """
    conn = _get_conn()

    try:
        valid_table = _validate_table_name(table_name)
        p = _resolve_path(file_path)
        suffix = p.suffix.lower()
        escaped_p = _escape_sql_literal(p)

        if suffix in (".csv", ".tsv"):
            read_fn = f"read_csv('{escaped_p}', auto_detect=true)"
        elif suffix in (".parquet", ".pq"):
            read_fn = f"read_parquet('{escaped_p}')"
        elif suffix in (".json", ".jsonl", ".ndjson"):
            read_fn = f"read_json('{escaped_p}', auto_detect=true)"
        else:
            return {"error": f"Unsupported file type: {suffix}"}

        conn.execute(f"CREATE OR REPLACE TABLE {valid_table} AS SELECT * FROM {read_fn}")

        # Get row count
        count_row = conn.execute(f"SELECT COUNT(*) FROM {valid_table}").fetchone()
        count = count_row[0] if count_row else 0

        # Get schema
        schema_result = conn.execute(f"DESCRIBE {valid_table}")
        schema_cols = [desc[0] for desc in schema_result.description]
        schema_rows = schema_result.fetchall()
        schema = [dict(zip(schema_cols, row, strict=False)) for row in schema_rows]

        return {
            "status": "created",
            "table_name": valid_table,
            "source_file": str(p),
            "row_count": count,
            "column_count": len(schema),
            "schema": schema,
        }

    except Exception as e:
        return {"error": str(e), "file_path": file_path, "table_name": table_name}


# ---------------------------------------------------------------------------
# TOOL: list_tables
# ---------------------------------------------------------------------------


@mcp.tool(tags={"analytics", "data"})
def list_tables() -> dict[str, Any]:
    """List all tables currently loaded in the DuckDB in-memory session."""
    conn = _get_conn()

    try:
        result = conn.execute("SELECT table_name, estimated_size FROM duckdb_tables()")
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        tables = [dict(zip(columns, row, strict=False)) for row in rows]
        return {"tables": tables, "count": len(tables)}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# TOOL: export_result
# ---------------------------------------------------------------------------


@mcp.tool(tags={"analytics", "data", "export"})
def export_result(
    sql: str,
    output_path: str,
    format: str = "csv",
) -> dict[str, Any]:
    """Execute a SQL query and export results to a local file.

    Args:
        sql: The SQL query to execute.
        output_path: Path for the output file (supports ~ expansion).
        format: Output format — 'csv', 'parquet', or 'json' (default: csv).
    """
    conn = _get_conn()

    try:
        out = Path(os.path.expanduser(os.path.expandvars(output_path))).resolve()
        _validate_export_path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        escaped_out = _escape_sql_literal(out)

        fmt = format.lower()
        if fmt == "csv":
            conn.execute(f"COPY ({sql}) TO '{escaped_out}' (HEADER, DELIMITER ',')")
        elif fmt == "parquet":
            conn.execute(f"COPY ({sql}) TO '{escaped_out}' (FORMAT PARQUET)")
        elif fmt == "json":
            conn.execute(f"COPY ({sql}) TO '{escaped_out}' (FORMAT JSON, ARRAY true)")
        else:
            return {"error": f"Unsupported format: {fmt}. Use csv, parquet, or json."}

        file_size = out.stat().st_size

        return {
            "status": "exported",
            "path": str(out),
            "format": fmt,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / 1e6, 2),
        }

    except Exception as e:
        return {"error": str(e), "sql": sql, "output_path": output_path}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    mcp.run(transport="stdio")
