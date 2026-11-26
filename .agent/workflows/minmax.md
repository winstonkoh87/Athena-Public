---
description: MinMax Protocol v2.2 — Default latency, round-trip Amdahl law, token economy, and quality optimization architecture
created: 2026-03-28
last_updated: 2026-11-21
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /minmax — MinMax Protocol v2.2 (Default Architecture)

> **Status**: Active by default in [`/start`](start.md). Reconciles token economy (`v1.0`), wall-clock latency SLOs (`v2.0`), and Round-Trip Amdahl + non-blocking external timeout caps (`v2.2`). Use `/ultrastart` (`MaxMax`) only for deliberate full-corpus deep audits.

## Core Optimization Function

`maximize(quality / (latency_s * token_cost))` subject to **hard non-negotiable safety and quality floors**:
- Never skip Law #1 ruin checks (`trading-risk-gate`), Protocol 509 crisis hotlines, Protocol 574 substance decode, or Lambda >= 10 verification (`context_gate`).
- Reduce redundant I/O, serial blocking, duplicate payloads, and unread boilerplate — never reduce reasoning accuracy.
- **Round-Trip Amdahl Law (v2.2)**: Sequential LLM round-trips dominate sub-second local Python latency by `10x-50x`. Minimize sequential tool waves first (0-1 wave Turn-1 boot), enforce hard non-blocking external caps second (`INTERACTIVE_EXTRA_TIMEOUT_S = 5.5s`, interactive `get_embedding(..., max_retries=1, timeout=4.0, floor_delay=0.0)`), and optimize local milliseconds third.

## Mechanical Latency & Token SLO Matrix

| Subsystem | Default MinMax v2.2 Path | Latency / Size SLO | Fallback / Escalation |
|:---|:---|:---|:---|
| **Turn-1 Boot Docs** | `AGENTS.md` + `_shared.md` + `start.md` (`_shared.md`, `start.md`, and `.framework/` skipped on normal Turn 1) | `<= 16,000 bytes` (~4K tokens) | JIT-load `_shared_extended.md` on task match; `/ultrastart` for deep loads |
| **Boot Status Telemetry** | Single concurrent `.agent/scripts/athena-py scripts/boot_status.py --bundle` (1-call status + latest checkpoint + `userContext.md`) | `< 1.0s`, zero `RuntimeWarning` | Local FTS/sync fallback if API probe `> 0.85s` |
| **SNIPER Retrieval (`Lambda < 10`) & Meta-Patterns** | `vector_mode="local"` (FTS BM25 + Canonical + File/Framework); `rerank=False` on secondary MP hops | `< 50 ms`, zero remote embedding HTTP call | Direct file read or upgrade to `context_gate` if ambiguity rises |
| **STANDARD Speculative (`Lambda <= 25`, non-personal/non-web)** | `vector_mode="auto"` speculative parallel Local+ONNX vs Remote Vector (`top_logit >= 1.0`, or `>= 0.0` + `CONFIDENCE_MED` RRF for `>= 3` words) | `< 0.5s` on local fast-path hit | Awaits parallel remote vector capped at `INTERACTIVE_EXTRA_TIMEOUT_S = 5.5s` |
| **STANDARD High (`> 25` / Personal / Web) & ULTRA (`> 30`)** | `vector_mode="always"` single-wave parallel Local + Vector (`max_retries=1, timeout=4.0s, floor_delay=0.0s`) + non-blocking `wait_on_exit=False` on timeout | `<= 5.5s` hard wall cap; `< 20 ms` cache hit | Degraded-recall explicit warning + immediate `executor.shutdown(wait=False)` |
| **ONNX Reranker & `QueryCache` Vectors** | Length-sorted mini-batches (`MAX_LENGTH=256`, `batch_size=8`, `intra_op=4`, `allow_spinning=0`) + single-key `QueryCache._save_vecs_to_db(upsert_key=...)` | `< 0.5s` for 50 candidates; zero disk write on hit | CrossEncoder fallback only if ONNX assets absent |
| **Embedding Cache Self-Heal** | `PersistentEmbeddingCache._quarantine_and_recreate()` on malformed SQLite | `< 50 ms` automatic quarantine & clean DB recreate | Disables disk cache cleanly for process if recreation fails |
| **JSONL Telemetry & Rotation** | Tail-seek reader (`<= 64 KB`) + size-based rotation in `shutdown.py` | `O(1)`, `< 15 ms` | Automatic archive rotation when logs exceed threshold |
| **CLI Search (`smart_search.py`)** | In-process execution with `ThreadPoolExecutor` timeout guard | Eliminates ~0.6s subprocess spawn overhead | Timeout message identifies stalled stage |

## Behavioral Rules

1. **One-Wave Boot (`/start`)**: SNIPER openers skip boot reads entirely (`0` reads, `0` MCP calls). Substantive Turn-1 calls `boot_status.py --bundle` in parallel with `context_gate(query, limit=8)` in Wave 1 — never read `_shared.md`, `start.md`, `.framework/` modules, or full `activeContext.md` on normal Turn 1.
2. **Targeted Slicing**: Read exact line ranges (`<= 150 lines` around symbol matches via `grep -n`) rather than loading whole files or multi-MB logs into context.
3. **Dense Signal Output**: Lead with the answer/diff; prefer compact tables over prose walls; render all formulas, intervals, and currency in ASCII/Unicode (zero LaTeX delimiters).
4. **Coordinated Parallelism & Round-Trip Cap**: Target `<= 2` tool waves on Turn-1 Q&A by batching independent reads/checks/subagents in parallel (`context_gate` Meta-Patterns with `rerank=False`, `search.py` channels, `boot_status.py --bundle`), pass `compact_follow_up=True` on follow-up turns, and skip `quicksave.py` on exploratory Turn-1 Q&A.
5. **Micro Close Default (`/end`)**: Use compressed checkpoint closes (`shutdown.py --micro`) when sessions involve narrow fixes without new `CANONICAL.md` or `PROJECTS.md` state transitions.

## References

- [`/start`](start.md) — Fast boot execution workflow
- [`_shared_extended.md`](references/_shared_extended.md) — JIT UI, Anti-Abstraction, Swarm, and Cluster Routing specs
- `CANONICAL.md` §194 (Context Density) & §216 (Suggest, Never Impose)

`#workflow` `#minmax` `#performance` `#latency`
