---
tracks:
  - src/athena/mcp_server.py
  - src/athena/duckdb_mcp_server.py
---

# MCP Tool Server

> **Model Context Protocol integration for Project Athena.**

The MCP Server exposes Athena's core capabilities as standardized [MCP tools](https://modelcontextprotocol.io/), consumable by any MCP-compatible client (Antigravity, Claude Desktop, Cursor, etc.).

---

## Quick Start

### stdio (IDE Integration)

```bash
python -m athena.mcp_server
```

### SSE (Remote / Multi-Client)

```bash
python -m athena.mcp_server --sse --port 8765
```

### IDE Configuration

For **Claude Code**, copy [.mcp.json.example](../.mcp.json.example) to `.mcp.json` at the repo root to expose both `athena.mcp_server` (20 governance/memory/decision tools) and `athena.duckdb_mcp_server` (5 analytical SQL tools).

For other IDEs, add to your IDE's MCP settings (e.g., `.agent/mcp_config.json`):

```json
{
  "mcpServers": {
    "athena": {
      "command": "python3",
      "args": ["-m", "athena.mcp_server"],
      "cwd": "/path/to/your/athena/workspace"
    },
    "duckdb-local": {
      "command": "python3",
      "args": ["-m", "athena.duckdb_mcp_server"],
      "cwd": "/path/to/your/athena/workspace"
    }
  }
}
```

---

## Tools (20)

| Tool | Permission | Sensitivity | Description |
|------|-----------|-------------|-------------|
| `smart_search` | read | internal | Hybrid RAG search (BM25 FTS5 + vectors + canonical/graph + ONNX rerank) |
| `agentic_search` | read | internal | Multi-step query decomposition with parallel search |
| `context_gate` | read | internal | Pre-answer context assembly, Meta-Triage, and grounding gate |
| `quicksave` | write | internal | Save timestamped checkpoint to session log |
| `health_check` | read | public | Audit Vector API + Database subsystems |
| `recall_session` | read | internal | Retrieve recent session log content |
| `governance_status` | read | internal | Check Triple-Lock compliance state |
| `list_memory_paths` | read | public | List active memory directories |
| `set_secret_mode` | admin | public | Toggle demo/external mode (blocks internal tools) |
| `meta_awareness_check` | read | public | Classify prompt for meta-awareness / interpreter kernel injection |
| `permission_status` | read | public | Show permission state and caller level |
| `classify_turn` | read | public | Classify query complexity (`Lambda`) and risk tier |
| `search_web` | read | public | Live web search via multi-provider failover chain |
| `report_external_web_search` | read | public | Report external web search compliance |
| `frame_open` | write | internal | Pre-register a problem frame (Lite/Strict, R1-R14 gates) |
| `frame_validate` | read | internal | Validate a frame against contract gates + VOI stop rule |
| `frame_resolve` | write | internal | Score a locked frame against observed outcomes |
| `frame_status` | read | internal | Report frame quality and protocol adoption |
| `calibration_status` | read | internal | Report Brier score, log-loss, and overdue predictions |
| `decision_screen` | read | internal | Evaluate options via GTO engine (EEV / 1/3 Kelly / Ruin / MCDA) with SHA-256 receipts |

> **Analytical SQL (`athena.duckdb_mcp_server`, 5 tools)**: `query`, `profile`, `create_table_from_file`, `list_tables`, and `export_result` run local DuckDB queries over CSV/JSON/Parquet without loading raw datasets into context.

## Resources (2)

| URI | Description |
|-----|-------------|
| `athena://session/current` | Full content of active session log |
| `athena://memory/canonical` | Canonical Memory (CANONICAL.md) |

---

## Permissioning Layer

All tools are gated by the **Permissioning Engine** (`athena.core.permissions`).

### Capability Tokens

4 escalating permission levels:

| Level | Access |
|-------|--------|
| `read` | Query/read data |
| `write` | Modify session logs, checkpoints |
| `admin` | Modify config, clear caches |
| `dangerous` | Delete data, run shell commands (future) |

Default caller level: `write` (can access `read` + `write` tools).

### Sensitivity Labels

3 data classification tiers:

| Label | Description | Examples |
|-------|-------------|----------|
| `public` | Safe for demos, external sharing | Health check, memory paths |
| `internal` | Normal operational data | Session logs, search results |
| `secret` | Credentials, finances, PII | API keys, trading data |

### Secret Mode

Toggle with `set_secret_mode(True)`. When active:

- ✅ `health_check` and `list_memory_paths` remain accessible (PUBLIC)
- 🔒 All INTERNAL/SECRET tools are blocked
- 📝 Content from remaining data sources is auto-redacted (API keys → `[REDACTED]`)

Use case: sharing screen during a demo, external pair-programming, or showing Athena to a client.

### Content Auto-Classification

The engine auto-labels content based on pattern matching:

- **SECRET patterns**: `api_key`, `password`, `SUPABASE_KEY`, `trading`, `.env`, etc.
- **INTERNAL patterns**: `session_log`, `canonical`, `memory_bank`, etc.
- Everything else → `PUBLIC`

### Audit Trail

Every permission check is logged with timestamp, action, target, and outcome. Audit log is bounded at 1,000 entries (auto-truncated to 500).

---

## Dependencies

```bash
# From inside the cloned repo — this installs the `mcp` extra declared in
# pyproject.toml (fastmcp>=2.0.0).
pip install -e ".[mcp]"

# Or just the dependency, if you are not installing the package:
pip install "fastmcp>=2.0.0"
```

> ⚠️ Do **not** `pip install athena-cli` — that is an unrelated third-party
> package (a Presto-like CLI for AWS Athena), not this project. This page
> previously recommended it, contradicting the warning in the README.

---

## Architecture

```
┌─────────────────────────────────────┐
│         MCP Client (IDE)            │
│   (Antigravity / Claude Desktop)    │
└──────────────┬──────────────────────┘
               │ stdio / SSE
┌──────────────▼──────────────────────┐
│         MCP Server (FastMCP)        │
│                                     │
│  ┌───────────┐  ┌────────────────┐  │
│  │ Permission │  │   Tool Router  │  │
│  │   Gate     │──│                │  │
│  └───────────┘  │ smart_search   │  │
│                 │ quicksave      │  │
│                 │ health_check   │  │
│                 │ recall_session │  │
│                 │ governance     │  │
│                 │ memory_paths   │  │
│                 │ secret_mode    │  │
│                 │ perm_status    │  │
│                 └───────┬────────┘  │
└─────────────────────────┼───────────┘
                          │
┌─────────────────────────▼───────────┐
│          Athena SDK (core)          │
│  search │ sessions │ governance     │
│  health │ config   │ permissions    │
└─────────────────────────────────────┘
```
