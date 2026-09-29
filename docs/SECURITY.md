# Security Model

## Data Residency Options

| Mode | Where Data Lives | Best For |
|------|------------------|----------|
| **Cloud** | Supabase (your project) | Cross-device access, collaboration |
| **Local** | Your machine only | Sensitive data, air-gapped environments |
| **Hybrid** | Local files + cloud embeddings | Best of both (embeddings only leave machine) |

> **Sensitive data?** Keep it local. The `athena` SDK supports local vector stores (ChromaDB, LanceDB) for users who don't want data leaving their machine. See [LOCAL_MODE.md](LOCAL_MODE.md).

## What Leaves Your Machine (Cloud Mode)

| Component | Sends Raw Text? | Sends Embeddings? | Destination |
|-----------|-----------------|-------------------|-------------|
| **Embedding API** | Yes (text chunks) | — | Google Cloud |
| **LLM API** | Yes (prompts) | — | Anthropic (Claude) |
| **Supabase** | No | Yes (vectors only) | Your Supabase project |

## Key Security Practices

- **Supabase Keys**: Use `SUPABASE_ANON_KEY` for client-side operations. Never expose `SUPABASE_SERVICE_ROLE_KEY` in code or logs.
- **Row-Level Security**: Enable RLS on Supabase tables.
- **Agentic Safety**: If using an agentic IDE with filesystem access, restrict the agent's working directory. Never grant access to `~/.ssh`, `.env` files, or git credentials.

---

## Permissioning Layer (v8.4.0+)

All MCP tools are gated by the **Permission Engine** (`athena.core.permissions`).

### Capability Tokens

| Level | Access | Example Tools |
|-------|--------|---------------|
| `read` | Query data, read config | `smart_search`, `recall_session` |
| `write` | Modify session logs | `quicksave` |
| `admin` | Modify config, toggle modes | `set_secret_mode` |
| `dangerous` | Delete data (future, unused) | — |

### Sensitivity Labels

| Label | Description | Access in Secret Mode? |
|-------|-------------|------------------------|
| `public` | Safe for demos | ✅ Allowed |
| `internal` | Normal operational data | 🔒 Blocked |
| `secret` | Credentials, PII | 🔒 Blocked + Redacted |

### Secret Mode

Toggle via `set_secret_mode(True)`. Designed for:

- Screen sharing during demos
- External pair-programming
- Client presentations

When active, only PUBLIC tools are accessible and sensitive content is auto-redacted.

### Audit Trail

Every permission check is logged with timestamp, action, target, and outcome. State persists to `.agent/state/permissions.json`.

👉 **[Full MCP + Permissions Documentation](MCP_SERVER.md)**
