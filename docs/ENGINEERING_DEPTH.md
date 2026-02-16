# Engineering Depth

> **Last Updated**: 16 February 2026
> **Version**: v8.0-Stable

This document demonstrates the technical depth built into Athena over 860+ sessions.

---

## 1. Core Infrastructure

### 1.1 Hybrid Retrieval Pipeline

Athena's search engine fuses 5 retrieval methods using Reciprocal Rank Fusion (RRF):

| Source | Weight | Purpose |
| :----- | -----: | :------ |
| Canonical | 3.0x | Exact filename/path matches |
| GraphRAG | 2.0x | Community-level semantic clustering |
| Vector | 2.0x | Embedding similarity (pgvector) |
| Tag | 1.2x | Hashtag cross-referencing |
| Filename | 1.0x | Fuzzy name matching |

**Formula**:

```text
score = Σ ( weight * (0.5 + doc_score) * (1 / (k + rank)) )
```

---

## 2. Automation Layer

### 2.1 Boot Sequence (`/start`)

1. **Identity Load**: Reads `Core_Identity.md` (~1.5K tokens).
2. **Session Recall**: Retrieves the most recent session summary via semantic search.
3. **Context Grounding**: Injects real-time date/time.
4. **Session Creation**: Generates a new session log file.

**Total Boot Time**: <30 seconds (~2K tokens).

### 2.2 Shutdown Sequence (`/end`)

1. **Harvest Check**: Scans conversation for unlogged insights.
2. **Session Close**: Fills in Key Topics, Decisions, and Action Items.
3. **Git Commit**: Stages and commits all changes with AI-generated message.
4. **Push**: Sends to remote origin.

---

## 3. Protocol Library (150+)

Athena's protocols are modular thinking patterns, organized by domain:

| Category | Count | Examples |
| :------- | ----: | :------- |
| Decision | 22 | Einstein Criterion, Premise Audit |
| Psychology | 22 | Baseline Distortion, Cognitive Inversion |
| Business | 11 | Flywheel, Value Trinity |
| Engineering | 14 | Git Worktree Parallelism, State Freezer |
| Architecture | 10 | Token Hygiene, Latency Levels |

---

## 4. Parallel Execution (Protocol 101)

**Native Swarm** enables Maestro-style parallel agent orchestration:

```bash
python3 examples/scripts/parallel_swarm.py "Audit this codebase" "sec-audit"
```

This spawns 4 isolated Git Worktrees and 4 Terminal windows, each running a specialized reasoning track:

| Track | Role |
| :---- | :--- |
| A | Domain Expert |
| B | Adversarial Skeptic |
| C | Cross-Domain Matcher |
| D | Zero-Point Philosopher |

---

## 5. Memory Insurance (Disaster Recovery)

Supabase serves as a cloud backup of all indexed memories. If local files are lost, the vector database enables full recovery.

| Failure | Recovery Path |
| :------ | :------------ |
| Local disk failure | Pull from Supabase embeddings → reconstruct Markdown |
| Accidental deletion | Re-index from cloud → restore local files |
| Session corruption | Replay from session_logs table |

---

## 6. Governance & Audits

Athena has undergone 2 external red-team audits to ensure:

- **Confidence Scoring**: Percentages require empirical data + falsification checks.
- **Bionic vs Proxy Mode**: Explicit distinction between independent thinking and drafting.
- **Law Enforcement**: Laws #0-#6 are absolute vetoes on agent behavior.

---

*For the full technical breakdown, see [ARCHITECTURE.md](./ARCHITECTURE.md) and [SEMANTIC_SEARCH.md](./SEMANTIC_SEARCH.md).*
