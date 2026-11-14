---
description: MinMax Protocol v2.0 — Default latency + token + quality optimization architecture
created: 2026-03-28
last_updated: 2026-11-14
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /minmax — MinMax Protocol v2.0 (Default Architecture)

> **Status**: Active by default in [`/start`](start.md). Reconciles token economy (`v1.0`) with wall-clock latency SLOs and mechanical quality floors (`v2.0`). Use `/ultrastart` (`MaxMax`) only for deliberate full-corpus deep audits.

## Core Optimization Function

`maximize(quality / (latency_s * token_cost))` subject to **hard non-negotiable safety and quality floors**:
- Never skip Law #1 ruin checks (`trading-risk-gate`), Protocol 509 crisis hotlines, Protocol 574 substance decode, or Lambda >= 10 verification (`stop_governance_gate.py`).
- Reduce redundant I/O, serial blocking, duplicate payloads, and unread boilerplate — never reduce reasoning accuracy.

## Mechanical Latency & Token SLO Matrix

| Subsystem | Default MinMax v2.0 Path | Latency / Size SLO | Fallback / Escalation |
|:---|:---|:---|:---|
| **Turn-1 Boot Docs** | `AGENTS.md` + `_shared.md` + `start.md` (UI/routing split into `references/_shared_extended.md`) | `<= 16,000 bytes` (~4K tokens) | JIT-load `_shared_extended.md` on task match |
| **Boot Status Telemetry** | Single concurrent `.agent/scripts/athena-py scripts/boot_status.py` | `< 1.0s`, zero `RuntimeWarning` | Local FTS/sync fallback if API probe `> 0.85s` |
| **SNIPER Retrieval (`Lambda < 10`) & Meta-Patterns** | `vector_mode="local"` (FTS BM25 + Canonical + File/Framework) | `< 50 ms`, zero remote embedding HTTP call | Direct file read or upgrade to `context_gate` if ambiguity rises |
| **STANDARD Light (`Lambda 10-14`, non-personal/non-web)** | `vector_mode="auto"` speculative parallel Local+ONNX vs Remote Vector | `< 0.5s` when >= 2 non-boot hits & ONNX `top_logit >= 1.0` (`>= 2.5` for `< 3` words) | Automatically awaits parallel remote vector if local quality floor fails |
| **STANDARD Deep (`Lambda >= 15` / Personal) & ULTRA (`> 30`)** | `vector_mode="always"` single-wave parallel Local + Vector + conditional Web | `< 2.0s` cold; `< 20 ms` cache hit | Degraded-recall explicit warning + retry on API error |
| **QueryCache & Vectors** | Read-only RAM lookup on hit; embeddings offloaded to SQLite `search_cache_vecs.db` | Zero disk write on read hit | Writes only on cache miss / store |
| **JSONL Telemetry & Stop Hooks** | Tail-seek reader (`<= 64 KB`) + size-based rotation in `shutdown.py` | `O(1)`, `< 15 ms` | Automatic archive rotation when logs exceed threshold |
| **CLI Search (`smart_search.py`)** | In-process execution with `ThreadPoolExecutor` timeout guard | Eliminates ~0.6s subprocess spawn overhead | Timeout message identifies stalled stage |

## Behavioral Rules

1. **Surgical State Boot (`/start`)**: Read `userContext.md`, `productContext.md`, and surgical `activeContext.md` (header + latest checkpoint only). Never bulk-load `CANONICAL_TIER2.md` unless domain matches.
2. **Targeted Slicing**: Read exact line ranges (`<= 150 lines` around symbol matches via `grep -n`) rather than loading whole files or multi-MB logs into context.
3. **Dense Signal Output**: Lead with the answer/diff; prefer compact tables over prose walls; render all formulas, intervals, and currency in ASCII/Unicode (zero LaTeX delimiters).
4. **Coordinated Parallelism**: Launch independent reads/checks/subagents in parallel (`context_gate` Meta-Patterns, `search.py` channels, `boot_status.py`), never serially.
5. **Micro Close Default (`/end`)**: Use compressed checkpoint closes (`shutdown.py --micro`) when sessions involve narrow fixes without new `CANONICAL.md` or `PROJECTS.md` state transitions.

## References

- [`/start`](start.md) — Fast boot execution workflow
- [`_shared_extended.md`](references/_shared_extended.md) — JIT UI, Anti-Abstraction, Swarm, and Cluster Routing specs
- `CANONICAL.md` §194 (Context Density) & §216 (Suggest, Never Impose)

`#workflow` `#minmax` `#performance` `#latency`
