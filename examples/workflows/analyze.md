---
description: Structured data analysis pipeline — ingest → profile → query → file insights
created: 2026-04-09
last_updated: 2026-07-22
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: false
---

# /analyze — Execution Script

> **Latency Profile**: VARIABLE (60s first ingest, <1s cached queries)
> **Philosophy**: Ingest once, query forever.

## Prerequisites

```bash
pip install duckdb
```

## Phase 1: Ingest & Profile

// turbo

When the user provides a file path or points to a data directory:

```bash
python3 .agent/scripts/data_engine.py ingest "<file_path>"
```

This auto-detects the format, converts to Parquet (cached), and prints a full profile:
- Schema (columns + types)
- Row count
- Null analysis
- Date range
- Value distributions for categorical columns
- Sample rows

**Output**: Note the Parquet cache path printed — use this for all subsequent queries.

---

## Phase 2: Exploratory Queries

Run SQL against the cached Parquet. The file is registered as table `data`.

```bash
python3 .agent/scripts/data_engine.py query "<parquet_path>" "<sql>"
```

### Standard Exploration Sequence

1. **Volume**: `SELECT COUNT(*) FROM data`
2. **Date range**: `SELECT MIN(date), MAX(date) FROM data`
3. **Time series**: `SELECT strftime(date::TIMESTAMP, '%Y-%m') as month, COUNT(*) FROM data GROUP BY month ORDER BY month`
4. **Categoricals**: `SELECT <column>, COUNT(*) as cnt FROM data GROUP BY <column> ORDER BY cnt DESC LIMIT 20`
5. **Text patterns**: `SELECT date, text FROM data WHERE text ILIKE '%keyword%' LIMIT 10`
6. **Numeric extraction**: `SELECT regexp_extract(text, '\$(\d+)', 1)::INT as val, COUNT(*) FROM data WHERE val IS NOT NULL GROUP BY val ORDER BY cnt DESC`

Iterate until you have enough signal for findings.

---

## Phase 3: Synthesis

After querying, synthesize findings into:

1. **Top N insights** (ranked by surprise value / non-obviousness)
2. **Extracted patterns** (generalisable to other domains)
3. **Actionable recommendations** (what to DO with the data)

---

## Phase 4: File to Exocortex

File the analysis as a case study:

```bash
python3 .agent/scripts/auto_file_insights.py \
    --title "<title>" \
    --domain "<domain>" \
    --tags "<tags>" \
    --context "<context>" \
    --findings "<finding1>||<finding2>||<finding3>" \
    --patterns "<pattern1>||<pattern2>" \
    --relevance "<active project relevance>" \
    --base-dir "/path/to/athena-workspace"
```

Or write the case study manually if the findings are complex enough to warrant full narrative (like CS-552).

---

## Multi-File Analysis

For multiple related files (e.g., two Telegram channel exports):

1. Ingest each file separately (each gets its own Parquet cache)
2. Query with UNION ALL or create combined views:

```sql
SELECT * FROM read_parquet('/path/to/file1.parquet')
UNION ALL
SELECT * FROM read_parquet('/path/to/file2.parquet')
```

Or in `data_engine.py` query mode:

```bash
python3 .agent/scripts/data_engine.py query /path/to/file1.parquet \
    "SELECT * FROM read_parquet('/path/to/file1.parquet') UNION ALL SELECT * FROM read_parquet('/path/to/file2.parquet')"
```

---

## Guardrails

- **Always profile before querying** — understand the schema first
- **Cache is king** — never query raw JSON/CSV after first ingest
- **File insights** — every analysis session should produce at least one case study
- **PII awareness** — large datasets may contain personal data. Flag before any external sharing.

---

## Tagging

#workflow #automation #data-analysis #duckdb
