#!/usr/bin/env python3
"""
Athena Data Engine — DuckDB-powered analytical backend for large data dumps.

Usage:
    python3 data_engine.py ingest <file_path>           # Ingest JSON/CSV → profile + convert to Parquet
    python3 data_engine.py query <parquet_path> <sql>    # Run SQL against Parquet file
    python3 data_engine.py profile <file_path>           # Profile a dataset (schema, stats, sample)
    python3 data_engine.py convert <file_path>           # Convert JSON/CSV to Parquet only

Architecture:
    - DuckDB as embedded OLAP engine (zero-server, in-process)
    - Parquet as columnar storage (5-10x compression, 100x query speed)
    - First-ingest converts raw files to Parquet alongside originals
    - Subsequent queries hit Parquet directly (millisecond latency)

Dependencies:
    pip install duckdb
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import duckdb

try:
    import pandas as pd
except ImportError:
    pd = None


# ─── Constants ────────────────────────────────────────────────────────────────

PARQUET_DIR = ".athena_cache/parquet"  # Relative to the data file's directory
MAX_SAMPLE_ROWS = 10
MAX_PROFILE_UNIQUE = 20


# ─── Core Engine ──────────────────────────────────────────────────────────────

class DataEngine:
    """DuckDB-powered analytical engine for Athena."""

    def __init__(self):
        self.con = duckdb.connect(":memory:")
        # Enable JSON extension
        self.con.execute("INSTALL json; LOAD json;")

    def close(self):
        self.con.close()

    # ─── Ingestion ────────────────────────────────────────────────────────

    def detect_format(self, file_path: str) -> str:
        """Detect file format from extension."""
        ext = Path(file_path).suffix.lower()
        if ext in (".json", ".jsonl"):
            return "json"
        elif ext in (".csv", ".tsv"):
            return "csv"
        elif ext in (".parquet", ".pq"):
            return "parquet"
        else:
            raise ValueError(f"Unsupported format: {ext}")

    def get_parquet_path(self, file_path: str) -> str:
        """Get the Parquet cache path for a given file."""
        fp = Path(file_path).resolve()
        cache_dir = fp.parent / PARQUET_DIR
        return str(cache_dir / f"{fp.stem}.parquet")

    def has_parquet_cache(self, file_path: str) -> bool:
        """Check if a Parquet cache exists and is newer than the source."""
        pq_path = self.get_parquet_path(file_path)
        if not os.path.exists(pq_path):
            return False
        src_mtime = os.path.getmtime(file_path)
        pq_mtime = os.path.getmtime(pq_path)
        return pq_mtime >= src_mtime

    def ingest_json_telegram(self, file_path: str) -> str:
        """
        Ingest a Telegram JSON export.
        Telegram exports have a top-level object with 'messages' array.
        We extract the messages array and flatten text fields.
        Returns the Parquet output path.
        """
        print(f"📥 Ingesting Telegram JSON: {file_path}")
        t0 = time.time()

        # Read the JSON structure first to detect Telegram format
        with open(file_path) as f:
            # Read just enough to detect structure
            chunk = f.read(500)
            f.seek(0)

        pq_path = self.get_parquet_path(file_path)
        os.makedirs(os.path.dirname(pq_path), exist_ok=True)

        if '"messages"' in chunk:
            # Telegram export — extract messages array
            print("  Detected Telegram channel export format")

            # Load JSON and extract messages (DuckDB can handle this)
            # But for 800MB files, use Python streaming approach
            print("  Loading JSON (this may take a minute for large files)...")
            with open(file_path) as f:
                data = json.load(f)

            channel_name = data.get('name', 'unknown')
            channel_type = data.get('type', 'unknown')
            messages = data.get('messages', [])

            print(f"  Channel: {channel_name}")
            print(f"  Messages: {len(messages):,}")

            # Flatten messages: extract text as string
            rows = []
            for m in messages:
                text = m.get('text', '')
                if isinstance(text, list):
                    parts = []
                    for p in text:
                        if isinstance(p, str):
                            parts.append(p)
                        elif isinstance(p, dict):
                            parts.append(p.get('text', ''))
                    text = ' '.join(parts)

                rows.append({
                    'id': m.get('id'),
                    'type': m.get('type', ''),
                    'date': m.get('date', ''),
                    'from_name': m.get('from', m.get('actor', '')),
                    'from_id': m.get('from_id', m.get('actor_id', '')),
                    'author': m.get('author', ''),
                    'forwarded_from': m.get('forwarded_from', ''),
                    'text': text,
                    'channel_name': channel_name,
                    'channel_type': channel_type,
                })

            # Convert to DuckDB and export as Parquet
            print(f"  Converting {len(rows):,} rows to Parquet...")

            if pd is not None:
                df = pd.DataFrame(rows)
                self.con.execute("CREATE TABLE messages AS SELECT * FROM df")
            else:
                # Fallback: write to temp JSON, let DuckDB read it
                import tempfile
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(rows, tmp)
                tmp.close()
                self.con.execute(f"CREATE TABLE messages AS SELECT * FROM read_json_auto('{tmp.name}')")
                os.unlink(tmp.name)

            self.con.execute(f"COPY messages TO '{pq_path}' (FORMAT PARQUET, COMPRESSION ZSTD)")
            self.con.execute("DROP TABLE messages")

            del data, messages, rows  # Free memory

        else:
            # Generic JSON — try DuckDB native read
            print("  Detected generic JSON format")
            self.con.execute(f"""
                COPY (SELECT * FROM read_json_auto('{file_path}'))
                TO '{pq_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)

        elapsed = time.time() - t0
        src_size = os.path.getsize(file_path)
        pq_size = os.path.getsize(pq_path)
        ratio = src_size / pq_size if pq_size > 0 else 0

        print(f"\n✅ Parquet written: {pq_path}")
        print(f"   Source: {src_size / 1024 / 1024:.1f} MB")
        print(f"   Parquet: {pq_size / 1024 / 1024:.1f} MB")
        print(f"   Compression: {ratio:.1f}x")
        print(f"   Time: {elapsed:.1f}s")

        return pq_path

    def ingest_csv(self, file_path: str) -> str:
        """Ingest a CSV file → Parquet."""
        print(f"📥 Ingesting CSV: {file_path}")
        t0 = time.time()

        pq_path = self.get_parquet_path(file_path)
        os.makedirs(os.path.dirname(pq_path), exist_ok=True)

        self.con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{file_path}'))
            TO '{pq_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        elapsed = time.time() - t0
        src_size = os.path.getsize(file_path)
        pq_size = os.path.getsize(pq_path)
        ratio = src_size / pq_size if pq_size > 0 else 0

        print(f"\n✅ Parquet written: {pq_path}")
        print(f"   Source: {src_size / 1024 / 1024:.1f} MB")
        print(f"   Parquet: {pq_size / 1024 / 1024:.1f} MB")
        print(f"   Compression: {ratio:.1f}x")
        print(f"   Time: {elapsed:.1f}s")

        return pq_path

    def ingest(self, file_path: str) -> str:
        """
        Auto-detect format and ingest to Parquet.
        Returns the Parquet path.
        """
        file_path = str(Path(file_path).resolve())

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check cache
        if self.has_parquet_cache(file_path):
            pq_path = self.get_parquet_path(file_path)
            print(f"⚡ Parquet cache hit: {pq_path}")
            return pq_path

        fmt = self.detect_format(file_path)

        if fmt == "json":
            return self.ingest_json_telegram(file_path)
        elif fmt == "csv":
            return self.ingest_csv(file_path)
        elif fmt == "parquet":
            print(f"  Already Parquet: {file_path}")
            return file_path
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    # ─── Querying ─────────────────────────────────────────────────────────

    def query(self, parquet_path: str, sql: str) -> list:
        """
        Run a SQL query against a Parquet file.
        The Parquet file is registered as table 'data'.
        Returns results as list of dicts.
        """
        parquet_path = str(Path(parquet_path).resolve())

        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        self.con.execute(f"CREATE OR REPLACE VIEW data AS SELECT * FROM read_parquet('{parquet_path}')")

        t0 = time.time()
        result = self.con.execute(sql).fetchdf()
        elapsed = time.time() - t0

        print(f"⚡ Query completed in {elapsed * 1000:.0f}ms ({len(result):,} rows)")
        return result

    def query_print(self, parquet_path: str, sql: str):
        """Run a SQL query and print results as a formatted table."""
        df = self.query(parquet_path, sql)
        print(df.to_string(index=False))
        return df

    # ─── Profiling ────────────────────────────────────────────────────────

    def profile(self, file_path: str) -> dict:
        """
        Profile a dataset: schema, row count, null counts, value distribution.
        Auto-ingests to Parquet if needed.
        """
        pq_path = self.ingest(file_path)

        print(f"\n📊 Profiling: {pq_path}")
        print("=" * 60)

        # Schema
        schema = self.con.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq_path}')").fetchall()
        print(f"\n📋 Schema ({len(schema)} columns):")
        for col_name, col_type, *_ in schema:
            print(f"   {col_name:30s} {col_type}")

        # Row count
        row_count = self.con.execute(f"SELECT COUNT(*) FROM read_parquet('{pq_path}')").fetchone()[0]
        print(f"\n📏 Rows: {row_count:,}")

        # Null counts
        print("\n🔍 Null Analysis:")
        self.con.execute(f"CREATE OR REPLACE VIEW data AS SELECT * FROM read_parquet('{pq_path}')")
        for col_name, col_type, *_ in schema:
            null_count = self.con.execute(f'SELECT COUNT(*) FROM data WHERE "{col_name}" IS NULL').fetchone()[0]
            null_pct = (null_count / row_count * 100) if row_count > 0 else 0
            if null_count > 0:
                print(f"   {col_name:30s} {null_count:>10,} nulls ({null_pct:.1f}%)")

        # Sample rows
        print(f"\n📝 Sample ({MAX_SAMPLE_ROWS} rows):")
        sample = self.con.execute(f"SELECT * FROM data LIMIT {MAX_SAMPLE_ROWS}").fetchdf()
        print(sample.to_string(index=False))

        # Date range (if date column exists)
        date_cols = [c for c, t, *_ in schema if 'date' in c.lower()]
        if date_cols:
            print("\n📅 Date Range:")
            for dc in date_cols:
                try:
                    min_date = self.con.execute(f'SELECT MIN("{dc}") FROM data WHERE "{dc}" IS NOT NULL AND "{dc}" != \'\'').fetchone()[0]
                    max_date = self.con.execute(f'SELECT MAX("{dc}") FROM data WHERE "{dc}" IS NOT NULL AND "{dc}" != \'\'').fetchone()[0]
                    print(f"   {dc}: {min_date} → {max_date}")
                except Exception:
                    pass

        # Value distribution for low-cardinality columns
        print(f"\n📊 Value Distributions (top {MAX_PROFILE_UNIQUE}):")
        for col_name, col_type, *_ in schema:
            if col_type in ('VARCHAR', 'BOOLEAN') and col_name not in ('text', 'from_id', 'actor_id'):
                try:
                    dist = self.con.execute(f"""
                        SELECT "{col_name}", COUNT(*) as cnt
                        FROM data
                        WHERE "{col_name}" IS NOT NULL AND "{col_name}" != ''
                        GROUP BY "{col_name}"
                        ORDER BY cnt DESC
                        LIMIT {MAX_PROFILE_UNIQUE}
                    """).fetchall()
                    unique_count = self.con.execute(f'SELECT COUNT(DISTINCT "{col_name}") FROM data').fetchone()[0]
                    if unique_count <= MAX_PROFILE_UNIQUE * 2:
                        print(f"\n   {col_name} ({unique_count} unique values):")
                        for val, cnt in dist:
                            pct = cnt / row_count * 100
                            print(f"      {str(val):40s} {cnt:>10,} ({pct:.1f}%)")
                except Exception:
                    pass

        return {
            'parquet_path': pq_path,
            'schema': schema,
            'row_count': row_count,
        }


# ─── CLI Interface ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Athena Data Engine — DuckDB-powered analytical backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Ingest a Telegram JSON export
    python3 data_engine.py ingest /path/to/result.json

    # Profile a dataset
    python3 data_engine.py profile /path/to/result.json

    # Run SQL against cached Parquet
    python3 data_engine.py query /path/to/.athena_cache/parquet/result.parquet \\
        "SELECT date, text FROM data WHERE text LIKE '%math%' LIMIT 10"

    # Convert only (no profiling)
    python3 data_engine.py convert /path/to/result.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest file → profile + Parquet")
    ingest_parser.add_argument("file_path", help="Path to JSON/CSV file")

    # Profile
    profile_parser = subparsers.add_parser("profile", help="Profile a dataset")
    profile_parser.add_argument("file_path", help="Path to JSON/CSV/Parquet file")

    # Query
    query_parser = subparsers.add_parser("query", help="Run SQL against Parquet")
    query_parser.add_argument("parquet_path", help="Path to Parquet file")
    query_parser.add_argument("sql", help="SQL query (table is 'data')")

    # Convert
    convert_parser = subparsers.add_parser("convert", help="Convert to Parquet only")
    convert_parser.add_argument("file_path", help="Path to JSON/CSV file")

    args = parser.parse_args()
    engine = DataEngine()

    try:
        if args.command == "ingest":
            pq_path = engine.ingest(args.file_path)
            engine.profile(args.file_path)

        elif args.command == "profile":
            engine.profile(args.file_path)

        elif args.command == "query":
            engine.query_print(args.parquet_path, args.sql)

        elif args.command == "convert":
            engine.ingest(args.file_path)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        engine.close()


if __name__ == "__main__":
    main()
