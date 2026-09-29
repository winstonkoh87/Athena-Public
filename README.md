<div align="center">

# Athena

**Local-first memory and guardrails for AI agents in your IDE.**

Your context lives in plain Markdown on your disk, works across Claude Code,
Antigravity, Cursor, Gemini CLI and VS Code — and the rules are enforced by
hooks, not just prompts.

[![CI](https://github.com/winstonkoh87/Athena-Public/actions/workflows/ci.yml/badge.svg)](https://github.com/winstonkoh87/Athena-Public/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/v10.0.1-10b981?style=flat-square&label=Version)](docs/CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/athena-agent?style=flat-square&color=10b981)](https://pypi.org/project/athena-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/winstonkoh87/Athena-Public?style=flat-square&logo=github)](https://github.com/winstonkoh87/Athena-Public/stargazers)

![20-second demo: /start recalls last session → work → /end](docs/demo.gif)

[Quickstart](#quickstart) · [How It Works](#how-it-works) · [Docs](docs/GETTING_STARTED.md) · [Why Athena?](docs/WHY_ATHENA.md) · [Safety](SAFETY.md)

</div>

---

## The Problem

You've spent months training ChatGPT to understand you. Then a model update resets the personality. You switch to Claude or Gemini — you start from zero.

Platform memory is unreliable, opaque, and locked to one provider. You don't own it and you can't take it with you.

Athena moves the memory layer to **your machine**: plain Markdown files that you own, version-control, and point at any model. The model is just whoever's on shift.

## Quickstart

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git && cd Athena-Public
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[local]"               # lightweight — no cloud deps
athena init --ide claude                # or: antigravity, cursor, gemini, vscode, kilocode, roocode
athena doctor                           # expect 0 failures
```

Then type `/start` in your IDE's AI chat panel. Work normally. Type `/end` to save.

> **Full install** (cloud sync + reranking): `pip install -e ".[full]"`
> See [Getting Started](docs/GETTING_STARTED.md) for Windows, advanced config, and Supabase setup.

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  Your IDE (Claude Code / Antigravity / Cursor / …)  │
└───────────────────┬─────────────────────────────────┘
                    │ hooks (code-enforced, not prompt-based)
                    ▼
┌─────────────────────────────────────────────────────┐
│  Athena SDK                                         │
│  ├── Lifecycle: /start loads ~2K tokens, /end saves │
│  ├── Memory: session logs + canonical facts         │
│  ├── Search: hybrid (keyword + optional vectors)    │
│  └── Guardrails: ruin check, secret scan, grounding │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  Your Disk (plain Markdown — git-versioned)         │
│  └── Optional: Supabase pgvector for cloud sync     │
└─────────────────────────────────────────────────────┘
```

**Three modes, one loop:**

| Mode | Boot | Token Cost | When |
|:-----|:-----|:-----------|:-----|
| Lightweight | Just chat, then `/end` | ~500 | Quick questions |
| Standard | `/start` → work → `/end` | ~2K–10K | Daily use |
| Deep | `/ultrastart` → work → `/ultraend` | ~20K | Complex planning |

### What's enforced in code vs. by prompt

> *Most AI-agent READMEs state every claim in the same confident voice. This one doesn't.*

| Claim | Status | Evidence |
|:------|:-------|:---------|
| **Storage & retrieval** — memories stored and surfaced when relevant | ✅ Shipped | Hybrid RAG with cross-encoder rerank, hardened through [production failures](docs/CHANGELOG.md) |
| **Portability** — Markdown on your disk, movable across models | ✅ Shipped | Structural — inspect the repo |
| **Governed autonomy** — hooks block destructive commands and secrets | ✅ Shipped (partial) | Ruin check blocks 14/16 destructive commands; 2 bypasses are [known and tracked](docs/TECH_DEBT.md) |
| **Compounding personalization** — session 500 recalls session 5 | 🟡 N=1 evidence | 1,900+ sessions by the author; no multi-user study |
| **Anti-sycophancy** — personalization doesn't silently increase agreement | 🟡 Partial mitigation | Code-enforced meta-awareness gate (Claude Code only); see [honest limits](docs/ENGINEERING_DEPTH.md) |

> **Why publish this table?** Because the failure mode of this product category is self-mythologizing — describing aspirations in the present tense. Athena's own convention ([Epistemic Status](examples/workflows/_shared.md#epistemic-status-convention-anti-self-mythologizing)) requires labeling every mechanism as `code-enforced`, `agent-discretion`, or `aspirational`. This table is that convention applied to the README.

## Measured, Not Claimed

```bash
# Run the tests yourself
pytest tests/ -v --tb=short

# Run the retrieval evaluator yourself (requires Supabase keys)
python examples/scripts/evaluator.py --gold-set .agent/eval/gold_set.json
```

| Metric | Value | Verification Command |
|:-------|:------|:---------------------|
| **Retrieval Hit@5 (Strict)** | **0.569** (37 / 65) | `python examples/scripts/evaluator.py` |
| **Retrieval MRR@5 (Strict)** | **0.472** | `python examples/scripts/evaluator.py` |
| *Retrieval Hit@5 (Lenient)* | *0.892 (deprecated)* | *Partial substring match (inflated)* |
| **Unit & Integration Tests** | 558 passed (100%) | `pytest tests/` |
| **Secret Leaks (1,248 commits)** | 0 detected | Gitleaks in CI |
| **Code Quality & Lints** | 0 ruff findings | `ruff check src/` |

> **Anti-Goodhart Invariant**: Why did our reported Hit@5 shift from 0.89 to 0.57? Lenient substring matchers count partial word overlaps as "hits," inflating benchmark scores by ~36% without improving retrieval. We killed the lenient matcher because vanity metrics mask regressions. See the full breakdown: [Anti-Goodhart Benchmarking in RAG](docs/BENCHMARKS.md#the-anti-goodhart-shift-why-we-published-lower-numbers).

## Agent Compatibility

| IDE | Config file | Tested |
|:----|:------------|:-------|
| Claude Code | `CLAUDE.md` | ✅ |
| Antigravity | `AGENTS.md` | ✅ |
| Cursor | `.cursor/rules.md` | ✅ |
| Gemini CLI | `.gemini/AGENTS.md` | ✅ |
| VS Code + Copilot | `.vscode/settings.json` | ✅ |
| Kilo Code | `.kilocode/rules/athena.md` | ✅ |
| Roo Code | `.roo/rules/athena.md` | ✅ |

## Documentation

| Doc | What it covers |
|:----|:---------------|
| [Getting Started](docs/GETTING_STARTED.md) | Install, configure, first session |
| [Your First Session](docs/YOUR_FIRST_SESSION.md) | 20-minute guided tutorial |
| [How It Works](docs/ARCHITECTURE.md) | Architecture and search pipeline |
| [Why Athena?](docs/WHY_ATHENA.md) | Philosophy, use cases, cost analysis |
| [Engineering Depth](docs/ENGINEERING_DEPTH.md) | Technical deep dives |
| [CLI Reference](docs/CLI.md) | All commands |
| [FAQ](docs/FAQ.md) | Common questions |
| [Safety](SAFETY.md) | Limitations and responsible use |
| [Changelog](docs/CHANGELOG.md) | Release history |

## Contributing

PRs welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

The codebase uses `ruff` for linting, `pytest` for tests, and CI must pass before merge.

---

<div align="center">

**MIT License** · [Contributing](CONTRIBUTING.md) · [Safety](SAFETY.md) · [Security](docs/SECURITY.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

Built and battle-tested solo across 1,900+ sessions by [Winston Koh](https://winstonkoh87.com).

*Clone it. Boot it. Make it yours.*

</div>
