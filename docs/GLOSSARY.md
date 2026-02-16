# Glossary

> **Last Updated**: 16 February 2026

> **Purpose**: Quick reference for Athena-specific terminology. Useful for recruiters, collaborators, or anyone exploring the codebase.

---

## Core Concepts

### Athena

The name of this personal AI operating system. Named after the Greek goddess of wisdom and strategic warfare — fitting for a system designed for knowledge management and decision support.

### Bionic Unit

The human + AI collaboration model. Neither component operates alone — the human provides intent, judgment, and verification; the AI provides speed, recall, and pattern recognition. Together: a "bionic" cognitive unit.

### COS (Committee Operating System)

A prompt engineering pattern where the AI operates as multiple "seats" with different perspectives (Strategist, Skeptic, Guardian, etc.) rather than a single voice. Encourages diverse reasoning before output.

---

## The Laws

Hard-coded decision principles baked into Athena's identity. Non-negotiable.

| Law | Name | Definition |
|-----|------|------------|
| **Law #0** | Subjective Utility | Respect the user's preferences — unless they trigger Law #1 |
| **Law #1** | No Irreversible Ruin | Veto any path with >5% probability of catastrophic, unrecoverable loss (financial, reputational, legal, psychological) |
| **Law #2** | Context > Effort | If the arena is structurally rigged against you, exit — don't "try harder" |
| **Law #3** | Actions > Words | Revealed preferences (what people *do*) outweigh stated preferences (what they *say*) |
| **Law #4** | Modular Architecture | New capabilities must be added as separate files, not bloating core prompts |
| **Law #5** | Epistemic Rigor | All external claims must be cited. No "orphan statistics" or unsourced assertions |

---

## Architecture Terms

### Triple Crown Stack

The core technology stack: **Gemini + Claude** (reasoning) + **Supabase/pgvector** (memory) + **Edge Functions** (orchestration). Named for covering all three layers of a cognitive system.

### Temporal Workflow

The 3-phase operating loop: `/start` (boot) → Execute (conversation) → `/end` (persist). Each session builds on the last, creating continuous context inheritance.

### VectorRAG

Retrieval-Augmented Generation using vector embeddings. Athena stores notes/documents as embeddings in Supabase (pgvector), then retrieves semantically similar content at query time to inject into prompts.

### Protocols

Reusable "thinking patterns" stored as Markdown files. Each protocol codifies a specific reasoning approach (e.g., risk analysis, design critique, negotiation). Currently 198 protocols in the library.

### Edge Functions

Serverless TypeScript/Deno functions hosted on Supabase. Used for automation like: GitHub push → auto-embed new documents → sync to vector database.

---

## Workflows (Slash Commands)

| Command | Purpose |
|---------|---------|
| `/start` | Boot the system, load identity, recall last session, prime semantic memory |
| `/end` | Close session, summarize insights, commit to persistent storage |
| `/think` | Deep reasoning mode — multi-step analysis with structured output |
| `/ultrathink` | Maximum depth — full protocol stack, adversarial stress-testing |
| `/refactor` | Workspace maintenance — diagnostics, orphan fixes, re-indexing |
| `/research` | Deep web research with citations |
| `/diagnose` | Read-only health check of workspace |

---

## Reasoning Modes

Inspired by *Bleach* anime power scaling (for flavor):

| Mode | Trigger | Description |
|------|---------|-------------|
| **Shikai** | `/start` | Default adaptive mode — scales reasoning to query complexity |
| **Bankai** | `/think` | Deliberate multi-track analysis (Domain + Adversarial + Cross-Domain) |
| **Shukai** | `/ultrathink` | Maximum depth — exhaustive simulation and zero-point inversion |

---

## File Structure

| Directory | Purpose |
|-----------|---------|
| `.framework/` | Core identity, laws, reasoning standards ("the soul") |
| `.context/` | Memories, user profile, case studies ("the brain") |
| `.agent/` | Scripts, workflows, protocols ("the hands") |
| `examples/` | Templates and sanitized samples for reference |
| `docs/` | Architecture docs, guides, this glossary |

---

## Key Metrics (Current State)

| Metric | Value |
|--------|-------|
| Sessions logged | 500+ |
| Protocols | 241 |
| Automation scripts | 97 |
| Embedded documents | 800+ |
| Monthly cost | <SGD 30 |

---

## References

- [README](../README.md) — Full project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Technical deep dive
- [VECTORRAG.md](docs/VECTORRAG.md) — Semantic memory system
- [Core Identity Template](examples/templates/core_identity_template.md) — How the AI's personality is defined

---
