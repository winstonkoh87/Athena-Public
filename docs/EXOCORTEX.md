# 🧠 The Exocortex

> **Status**: Optional Power-Up
> **Size**: ~6GB (Expanded) | ~900MB (Download)
> **Source**: DBPedia / Wikipedia

## What Is It?

The Exocortex is a local, offline copy of Wikipedia's abstract knowledge. It allows Athena to:

1. **Fact-check** hallucinations instantly.
2. **Lookup** technical terms, historical events, and scientific concepts without API calls.
3. **Ground** reasoning in verified data.

It is **not** included in the repo (git is for code, not massive databases). You build it yourself using the included script.

## How to Build It (10-15 mins)

We provide a script that downloads the "Long Abstracts" dump from DBPedia (a structured version of Wikipedia) and compiles it into a high-speed SQLite FTS5 (Full-Text Search) index.

### Step 1: Download (~900MB)

```bash
python3 examples/scripts/exocortex.py download
```

* **Source**: `dbpedia.org` (Official DBPedia Databus)
* **File**: `long-abstracts_lang=en.ttl.bz2`
* **Time**: Depends on your internet speed.

### Step 2: Index (~5-10 mins)

```bash
python3 examples/scripts/exocortex.py index
```

* **Process**: Reads the compressed BZ2 file, parses the TTL triples, and inserts them into a local `exocortex.db`.
* **Result**: A ~6GB SQLite database file in `.context/knowledge/exocortex.db`.

### Step 3: Test

```bash
python3 examples/scripts/exocortex.py search "Project Athena"
```

## Integration

Athena automatically detects if `exocortex.db` exists.
* **If exists**: It will query it during "Deep Think" or specific research tasks.
* **If missing**: It simply skips this step (graceful degradation).

## Why not use the Wikipedia API?

* **Speed**: Local SQL queries take ~0.002s. APIs take 1-2s.
* **Privacy**: No external requests.
* **Reliability**: Works offline.
* **Cost**: Zero.
