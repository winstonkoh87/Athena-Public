---
created: 2026-01-02
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: document-sharding
description: Splitting large documentation into semantic chunks to save context window (90% savings).
tags: [optimization, context, bmad, sharding]
created: 2026-01-02
last_updated: 2026-01-02
---

# Protocol 334: Document Sharding

> **Source**: BMAD-METHOD v6 Integration. Integrated 02 January 2026.  
> **Purpose**: Load only relevant sections of large files to optimize context window usage.

---

## The Problem

Large documentation files (e.g., framework docs, long logs) consume massive tokens.

- **Full Load**: 5000+ lines → 20k+ tokens.
- **Result**: Context window filled, higher cost, slower reasoning.

## The Solution: Semantic Sharding

Split documents by headers (`#`, `##`) into distinct, meaningful chunks.
Load only the specific chunk required for the task.

**Efficiency**: ~90% token reduction (viewing 1 chunk of 10 vs full file).

---

## Tool: Shard Document Utility

**Script**: `.agent/scripts/shard_document.py`

### Usage

1. **Shard the file**:

   ```bash
   python3 .agent/scripts/shard_document.py "path/to/large_file.md"
   ```

   *Output*: Generates parts in `.context/shards/` and prints an index.

2. **Read Index**:
   Review the output table to find relevant parts.

3. **Load Chunk**:
   Use `view_file` on the specific shard or use the line numbers from the index on the original file.

### Example

**Input**: `Framework_Documentation.md` (2000 lines)
**Command**: `python3 .agent/scripts/shard_document.py Framework_Documentation.md`
**Output**:

- `part_00_Intro.md` (50 lines)
- `part_01_Auth.md` (300 lines) ← **Need this**
- `part_02_Database.md` (400 lines)
...

**Action**: Read `part_01_Auth.md` only.

---

## Autonomic Trigger

- **Condition**: File > 500 lines AND only specific info needed.
- **Action**: Run sharding script automatically.

---

## Integration with Supabase

Athena's `supabase_sync.py` automatically shards files into 4000-char chunks for semantic search.
This protocol is for **active, manual context loading** during a session.

---

## Tagging

# protocol #optimization #context #sharding #bmad
