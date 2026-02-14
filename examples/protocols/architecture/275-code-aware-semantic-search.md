---
created: 2026-01-21
last_updated: 2026-01-30
graphrag_extracted: true
---

---id: 275
title: Code-Aware Semantic Search
category: architecture
status: draft
source: CS-374 (GrepAI Pattern)
tags: [semantic-search, code, efficiency, tokens]
created: 2026-01-21
last_updated: 2026-01-21
---

# Protocol 275: Code-Aware Semantic Search

## Purpose

Extend Athena's semantic search capabilities to code repositories, reducing token consumption by 90%+ when exploring unfamiliar codebases.

## Core Problem

Standard code exploration uses brute-force:

```
grep/glob → List files → Read each → Filter → Repeat
```

This is O(n) token consumption where n = codebase size.

## Solution Layers

### Layer 1: Semantic Code Search (Current Priority)

Use embeddings to find code by *meaning*, not keywords.

```bash
# Instead of:
grep -r "authentication" ./src

# Use:
smart_search.py "user login flow" --scope ./src
```

**Implementation**: Extend `supabase_sync.py` to index code files (.py, .js, .ts, .astro).

### Layer 2: Call Graph Analysis (Future)

Trace function dependencies:

```
function A → calls B → calls C
```

When searching for A, also surface B and C as contextually relevant.

**Implementation**: AST parsing + graph storage.

### Layer 3: PageRank for Code Importance (Future)

Rank files by connectivity:

- Most imported/called = most important
- Entry points and utilities surface first

**Reference**: Aider repomap (<https://aider.chat/docs/repomap.html>)

## Execution Heuristic

When exploring a new codebase:

1. **First**: Check for existing index files (README, docs/, ARCHITECTURE.md)
2. **Second**: Run semantic search with intent keywords
3. **Third**: If code repo, trace imports/calls from discovered files
4. **Avoid**: Brute-force grep unless semantic search returns nothing

## Token Economics

| Approach | Tokens (155k line repo) | Relative |
|----------|-------------------------|----------|
| grep + read all | ~51,000 | 100% |
| Semantic search | ~1,300 | **2.5%** |

97% reduction validated (GrepAI benchmark on Excalidraw).

## Integration Points

| System | How It Integrates |
|--------|-------------------|
| `smart_search.py` | Add `--code` flag for code-specific search |
| `supabase_sync.py` | Extend to index .py, .js, .ts, .astro files |
| Boot sequence | Auto-detect if working in code repo vs knowledge repo |

## Current Status

- [x] Semantic search on knowledge (protocols, sessions, case studies)
- [ ] Extend sync to code files
- [ ] Call graph extraction (AST parsing)
- [ ] PageRank ranking

## Related

- [CS-374: GrepAI Token Efficiency](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS-374-grepai-token-efficiency.md)
- [Protocol 133: JIT Knowledge Routing](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/protocols/architecture/133-query-archetype-routing.md)

## Tags

# architecture #semantic-search #efficiency #code #tokens
