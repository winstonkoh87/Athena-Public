# Local Mode

> **Purpose**: Run Athena entirely on your machine without sending data to the cloud.

---

## When to Use Local Mode

- Sensitive data that shouldn't leave your machine
- Air-gapped environments
- Development/testing without API costs

---

## Setup

### 1. Install Local Dependencies

```bash
pip install -e ".[local]"  # Includes ChromaDB
```

### 2. Configure `.env`

```bash
# Disable cloud sync
ATHENA_MODE=local

# Optional: specify local vector store path
ATHENA_LOCAL_DB_PATH=~/.athena/vectorstore
```

### 3. Initialize Local Store

```bash
python -c "from athena.memory import LocalStore; LocalStore().init()"
```

---

## How It Works

| Component | Cloud Mode | Local Mode |
|-----------|------------|------------|
| **Embeddings** | Google API | Local model (sentence-transformers) |
| **Vector Store** | Supabase (pgvector) | ChromaDB (local) |
| **Knowledge Files** | Git-synced | Local only |

---

## Limitations

- No cross-device sync (files stay on one machine)
- Local embedding models are slower than API
- No collaborative features

---

*See also: [Security Model](SECURITY.md)*
