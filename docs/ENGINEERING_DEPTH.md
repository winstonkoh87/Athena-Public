# Engineering Depth

> **Last Updated**: 20 November 2026
> **Version**: v10.0.6

This document details the retrieval physics, runtime governance, and honest mechanism boundaries built into Athena across 2,100+ sessions.

---

## 1. Core Infrastructure

### 1.1 Hybrid Retrieval Pipeline (`src/athena/tools/search.py`)

Athena fuses five concurrent retrieval channels — SQLite FTS5 BM25, pgvector dense embeddings (backed by a zero-write-on-hit local SQLite cache `search_cache_vecs.db`), canonical/graph headers, filename/tag matchers, and the local learnings channel (`.athena/memory/USER_PROFILE.yaml` + `SYSTEM_LEARNINGS.md`) — using intent-routed Reciprocal Rank Fusion (RRF) followed by local ONNX cross-encoder reranking (`SafeCrossEncoder`).

Each query is classified into one of three intent profiles before fusion:

| Source / Subtype | `GENERAL` | `PERSONALISED_DECISION` | `SYSTEM_KNOWLEDGE` | Decay Policy |
| :--------------- | --------: | ----------------------: | -----------------: | :----------- |
| `protocol` | 3.2x | 2.0x | 3.5x | Timeless (`1.0x`) |
| `capability` (skills) | 3.2x | 1.5x | 3.2x | Timeless (`1.0x`) |
| `case_study` | 2.8x | 2.8x | 2.5x | Continuous exponential (`[0.60, 1.15]`) |
| `session` | 2.5x | 3.0x | 2.0x | Continuous exponential (`[0.60, 1.15]`) |
| `user_profile` | 2.5x | 4.0x | 1.5x | Timeless (`1.0x`) |
| `canonical` | 1.2x | 2.8x | 1.2x | Timeless (`1.0x`) |
| `filename` | 2.5x | 1.8x | 2.5x | Timeless (`1.0x`) |
| `tags` | 2.2x | 2.2x | 2.2x | Timeless (`1.0x`) |
| `system_learnings` | 1.8x | 1.4x | 2.2x | Position recency + status bonus |
| `fts_bm25` | 1.5x | 1.5x | 1.5x | Timeless (`1.0x`) |
| `web_search` | 2.8x | 2.5x | 2.0x | Hour-based freshness (`1.0x` `<1h`, `0.90x` `<24h`, `0.75x` `>=24h`) |

**Fusion Formula**:

```text
score(d) = SUM_c [ weight(c, intent) * score_mod(d) * temporal_mod(d) * (1 / (k + rank_c(d))) ]
score_mod(d) = 0.5 + clip(raw_score(d), 0.0, 1.0)
temporal_mod(d) = 0.60 + 0.55 * (0.5 ^ (age_days(d) / 365.25))   # for session & case_study; 1.0 otherwise
```

- **Continuous Exponential Recency (`compute_temporal_decay`)**: Time-series memories (`session`, `case_study`) decay smoothly with a 1-year (`365.25`-day) half-life from `1.15x` at `age_days = 0` toward an asymptote floor of `0.60x` (`~0.875x` at 1 year, `~0.738x` at 2 years). Extracting full ISO dates (`YYYY-MM-DD`) eliminates the January 1 calendar-year boundary cliff while distinguishing recent same-year sessions from 10-month-old ones (falling back to year-level delta when only a 4-digit year token exists).

#### Comparison Against Park et al. (2023) Generative Agents

Park et al. (2023) rank agent memories by a weighted sum of **Recency**, **Importance**, and **Relevance**, paired with periodic **Reflection**:

| Axis | Athena Implementation | Status & Architectural Trade-off |
| :--- | :-------------------- | :------------------------------- |
| **Recency** | Continuous exponential decay (`compute_temporal_decay`, 365.25-day half-life in `[0.60, 1.15]`) on episodic sources (`session`, `case_study`); timeless `1.0x` on procedural/semantic rules | **Code-enforced** (`src/athena/tools/search.py`, tested in `tests/test_retrieval_reliability.py`) |
| **Relevance** | 5-channel weighted RRF (BM25 + pgvector + headers + filenames + local learnings) + ONNX cross-encoder reranking | **Code-enforced** (`src/athena/tools/search.py`, `src/athena/tools/reranker.py`) |
| **Reflection** | End-of-session `/end` distillation, case-study extraction (`CS-*.md`), and `.agent/scripts/compact_learnings.py` | **Shipped (semi-automated)** — requires periodic `/dream` or `/end` sweeps when pending `SYSTEM_LEARNINGS.md` rows accumulate |
| **Importance (1–10 per memory)** | Approximated via document-type weight priors (`protocol 3.5x` vs. `session 2.0x`), confidence/status bonuses in `learnings.py`, and manual graduation to `CANONICAL.md` / `CS-*.md` | **Intentionally omitted at write time** — avoids an LLM scoring call on every `quicksave`, trading per-episode scalar salience for zero-latency deterministic writes |

---

## 2. Automation & Runtime Governance

### 2.1 Fast Boot Sequence (`/start`)

1. **Surgical Identity & State Load**: Reads `userContext.md` and the latest checkpoint block of `activeContext.md` (~2K tokens).
2. **Single-Pass Concurrent Telemetry**: `scripts/boot_status.py` probes accountability streaks, frame ledger calibration, due decisions, learnings backlog, and FTS/vector index health in parallel (`<1.0s` wall time).
3. **Adaptive Routing**: Queries are classified into `SNIPER` (`Lambda < 10`, local-only), `STANDARD` (`Lambda 10-30`, speculative hybrid search), or `ULTRA` (`Lambda > 30`, hybrid search + web/page verification).

### 2.2 Fail-Closed PreToolUse & Diff-Scoped Stop Hooks

- **PreToolUse Security Guards (`.agent/scripts/security/`)**: `block_secrets.py` (blocks reads/edits of `.env`, private keys, and credential files) and `block_ruin.py` (shlex-tokenized Law #1 blocker for destructive shell commands) run with `"onFailure": "block"` and exit `2` on malformed stdin.
- **Diff-Scoped Stop Verifier (`.agent/scripts/hook_stop_verify.py`)**: Runs a single `git status` pass plus batched `git diff -U0 HEAD` (`<0.5s`) to enforce Protocol 509 crisis referrals, GTO decision receipts (`GTO-xxxxxxxx`), diff-scoped LaTeX delimiter checks (`check_latex_leak.py --diff-only`), secret scans, and Python syntax compilation before the turn completes.

---

## 3. Protocol Library (461 total: 410 active + 51 archived, 26 categories)

Canonical inventory counts are machine-verified against `.agent/config/CAPS.json` and `scripts/check_doc_drift.py`:

| Asset Class | Canonical Count | Scope |
| :---------- | --------------: | :---- |
| **Protocols** | 461 (410 active + 51 archived) | 26 domain directories under `.agent/skills/protocols/` |
| **Skills** | 44 active (17 archived) | 43 conditional (`context_trigger`) + 1 always-on under `.agent/skills/` |
| **Workflows** | 78 (57 root + 21 `_domain/`) | Slash-command execution playbooks under `.agent/workflows/` |
| **Case Studies** | 633 | Empirical pattern dossiers (`CS-*.md`) |

---

## 4. Parallel Execution (Protocol 101)

**Native Swarm** spawns 4 isolated Git Worktrees across specialized reasoning tracks:

| Track | Role |
| :---- | :--- |
| A | Domain Expert |
| B | Adversarial Skeptic |
| C | Cross-Domain Matcher |
| D | Zero-Point First Principles |

---

## 5. Memory Insurance (Disaster Recovery)

Local Markdown and SQLite files are the primary source of truth; Supabase `pgvector` serves as an off-machine encrypted mirror for reconstruction if local storage fails.

---

## 6. Anti-Sycophancy Architecture & Honest Limits

### 6.1 The Empirical Tension

Recent HCI and alignment research shows that persistent personalization and epistemic independence pull in opposite directions:

1. **Profile-Induced Agreement Amplification**: Jain et al. (2026, CHI '26) found that injecting a condensed user memory profile is among the strongest drivers of agreement sycophancy (up to **+45%** on Gemini 2.5 Pro), compounding a **58.19%** overall (**43.52%** progressive / **14.66%** regressive) frontier sycophancy baseline (Fanous et al., 2025, *SycEval*).
2. **Role-Dependent Mitigation**: Kelley & Riedl (2026) demonstrated that while personalization increases affective alignment across the board, its effect on *epistemic independence* depends on role framing: a **social-peer** frame erodes independence, whereas an explicit **advisory** frame strengthens premise challenge.
3. **Interrogative Reframing**: Dubois et al. (2026) showed that question-framed epistemic prompts reduce model capitulation relative to affirmative instructions.

### 6.2 What Is Enforced in Code

- **Domain-General Meta-Awareness Gate (`src/athena/core/gate_meta.py`, `.agent/scripts/hook_meta_awareness_gate.py`)**: Classifies every user prompt across 8 structural act classes (`T1-INBOUND`, `T2-OUTBOUND`, `T3-VERDICT`, `T4-RESOURCE`, `T5-FELT`, `T6-INTAKE-AUTHORITY`, `T7-END-USER-CAPABILITY`, `T8-MULTILINGUAL`). When triggered, it injects a 9-point question-framed anti-mirror kernel (`REMINDER_TEMPLATE`: Arena, Base-Rate Prior, Discriminators, `MP-16` Sign Check, SimToM Receiver Frame, `F != R` Felt-Evidence separator, Payoff Asymmetry, Intake/Operator check, and Revealed-Preference Agency).
- **Cross-Harness MCP Bridge (`src/athena/mcp_server.py::context_gate`)**: Embeds the same meta-awareness directive and `META-TRIAGE` framing checks into `context_gate` responses for IDEs without native prompt-submit hooks.
- **3-Arm Profile-Conditioned Sycophancy Benchmark (`scripts/eval_sycophancy_ab.py`, `tests/eval/sycophancy_holdout.json`, `tests/test_sycophancy_holdout.py`)**: Evaluates 24 frozen cases (`18` profile-conditioned disagreement-bait prompts across `T1`–`T7` + `6` sound technical controls) across three arms (`stateless_baseline`, `profile_only_unmitigated`, and `athena_governed`). Deterministic CI tests enforce **100% (`18/18`)** anti-mirror kernel recall on disagreement-bait prompts and **0% (`0/6`)** false-positive firing on sound controls.

```bash
# Verify 3-arm sycophancy packet assembly and 18/18 gate recall at zero API cost
python3 scripts/eval_sycophancy_ab.py --dry-run
pytest tests/test_sycophancy_holdout.py -v
```

### 6.3 Honest Limits (Why the README Row Stays `Partial Mitigation`)

1. **Hook Coverage Boundary (`code-enforced` vs. `agent-discretion`)**: In Claude Code, `.claude/settings.json` executes `hook_meta_awareness_gate.py` deterministically on every `UserPromptSubmit`. In hookless IDEs, the anti-mirror kernel enters context only when the agent calls `context_gate` or `meta_awareness_check`.
2. **Stateless Red-Team Subagent Boundary**: Invoking a fresh, stateless red-team subagent strips `userContext.md` from the auditor's context window (eliminating direct profile-conditioning taint), but two residual gaps remain:
   - *Selection bias*: Operators invoke red-team audits when uncertain; sycophancy is most dangerous when the operator already feels certain and skips the audit.
   - *Brief framing inheritance*: The stateless subagent reads a task brief written by the primary profiled agent, which can transmit framing bias even when the raw user profile is absent.
3. **Kernel Injection != Downstream Behavioral Proof**: `tests/test_sycophancy_holdout.py` proves that the anti-mirror kernel is deterministically injected on 100% of holdout bait cases, not that every downstream LLM refuses to capitulate. Measuring live regressive-sycophancy delta between `profile_only_unmitigated` and `athena_governed` requires running `python3 scripts/eval_sycophancy_ab.py --provider openai --model <model>` with a live API key.

---

*For the full technical breakdown and academic citations, see [ARCHITECTURE.md](ARCHITECTURE.md), [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md), and [REFERENCES.md](REFERENCES.md).*
