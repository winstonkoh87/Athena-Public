# Semantic Search: Triple-Path Retrieval Architecture

> **Last Updated**: 16 February 2026  
> **Purpose**: How Athena finds and retrieves relevant context using three complementary methods

---

## Executive Summary

Athena employs **Triple-Path Retrieval** to ensure no relevant context is missed. Each method catches what the others miss.

```text
                              USER QUERY
                                  │
                                  ▼
              ┌───────────────────┴───────────────────┐
              │        TRIPLE-PATH RETRIEVAL          │
              └───────────────────┬───────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│    PATH 1     │        │    PATH 2     │        │    PATH 3     │
│               │        │               │        │               │
│  🔮 VECTOR    │        │  🏷️ TAG      │        │  🔎 KEYWORD   │
│   SEARCH      │        │   INDEX       │        │    GREP       │
│               │        │               │        │               │
│  (Semantic)   │        │  (Hashtags)   │        │  (Exact)      │
└───────┬───────┘        └───────┬───────┘        └───────┬───────┘
        │                         │                         │
        ▼                         ▼                         ▼
 "decentralized"          "#leadership"           "Protocol 139"
 → finds related           → finds tagged         → finds exact
   concepts                   entities               matches
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  MERGED CONTEXT │
                        └─────────────────┘
```

---

## Why Three Paths?

| Path | Catches | Misses |
|:-----|:--------|:-------|
| **Vector** | Synonyms, paraphrases, concepts | Exact names, entities |
| **TAG_INDEX** | Explicitly tagged entities | Untagged content |
| **Keyword Grep** | Exact string matches | Semantic variations |

**Example**: Searching for a specific entity name

- **Vector search** might return "decentralized leadership" (semantically related)
- **TAG_INDEX** returns `#entity-name → Protocol 139` (exact entity match)
- **Keyword grep** finds any file mentioning the entity literally

---

## Path 1: Vector Semantic Search (VectorRAG)

> **Full Documentation**: [VECTORRAG.md](docs/VECTORRAG.md)

```bash
# Reference: python3 scripts/supabase_search.py "<query>" --limit 5
```

**How it works**:

1. Query is converted to a 3072-dimension embedding (Gemini API)
2. Cosine similarity search across 11 Supabase tables
3. Returns top matches ranked by semantic similarity

**Strengths**: Finds conceptually related content even with different wording.

---

## Path 2: TAG_INDEX Lookup

```bash
grep -i "<entity>" .context/TAG_INDEX.md
```

**How it works**:

1. `generate_tag_index.py` scans all workspace files
2. Extracts inline `#tags` from markdown files
3. Creates reverse lookup: `#tag → [file1, file2, ...]`

**Example output**:

```text
| #leadership | `protocols/139-decentralized-command.md` |
| #archetype  | `user_profile/Archetype_Example.md` |
```

**Strengths**: Instant lookup for named entities (people, protocols, concepts).

---

## Path 3: Keyword Grep

```bash
grep -ri "<keyword>" .context/ .agent/
```

**How it works**:

- Simple string matching across all files
- Catches content not in Supabase (new files)
- Finds exact phrases

**Strengths**: Zero false negatives for exact matches.

---

## When to Use Each Path

```text
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY TYPE → PATH SELECTION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "What did we discuss about X?"      →  [VECTOR] primary       │
│  "Find Protocol 139"                 →  [GREP] primary         │
│  "Show me files tagged #leadership"  →  [TAG_INDEX] primary    │
│  "User archetype profile"            →  [TAG_INDEX] + [GREP]   │
│  "Complex analysis of leadership"    →  [VECTOR] + all paths   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration: The Search Protocol (§0.7.1)

Per Core Identity, **every query** triggers semantic context retrieval:

```text
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1: Vector Search                                               │
│  # Reference: python3 scripts/supabase_search.py "<query>" --limit 5       │
├──────────────────────────────────────────────────────────────────────┤
│  STEP 2: Entity Lookup (if named entities detected)                  │
│  grep -i "<entity_name>" .context/TAG_INDEX.md                       │
├──────────────────────────────────────────────────────────────────────┤
│  STEP 3: Fallback Grep (if above return sparse results)              │
│  grep -ri "<keyword>" .context/ .agent/                              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## The TAG_INDEX Generator

```bash
# Reference: python3 scripts/generate_tag_index.py
```

**Current Stats** (Dec 2025):

- **1000+ tags** indexed
- **4 directories** scanned (`.context/`, `.agent/`, `examples/protocols/`, `user_profile/`)
- **Extraction methods**: YAML frontmatter + inline `#hashtags`

---

## Comparison: Before vs After Triple-Path

| Scenario | Before (Vector Only) | After (Triple-Path) |
|:---------|:---------------------|:--------------------|
| Search entity name | ❌ Missed related protocol | ✅ Found via TAG_INDEX |
| Search archetype | ❌ Missed profile file | ✅ Found via TAG_INDEX |
| Search "decentralized" | ✅ Found semantically | ✅ Still works |
| New unsynced file | ❌ Not in Supabase yet | ✅ Found via grep |

---

## Related Documentation

- [VECTORRAG.md](docs/VECTORRAG.md) — Deep dive into vector embeddings
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Overall system design

---

`#semantic-search` `#triple-path` `#vectorrag` `#tag-index` `#retrieval`

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](./ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
