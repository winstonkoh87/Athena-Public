---
created: 2026-02-28
last_updated: 2026-07-22
---

# Protocol 503: Cognitive Clusters (Skill Architecture Pattern)

> **Created**: 2026-02-28
> **Domain**: Architecture / Meta-Cognition
> **Priority**: ⭐⭐⭐ Critical (Structural)
> **Trigger**: Skill/protocol proliferation, "too many things to load", architecture review

---

## Philosophy

> **"Don't build 10 specialists who need to call each other. Build 3 experts who already know each other's work."**

When individual protocols/skills share triggers, inputs, and domain context, maintaining them as separate units creates **routing tax** — the overhead of finding, loading, and chaining related fragments. Cognitive Clusters solve this by pre-merging co-activated knowledge into unified skills.

---

## The Pattern

```
BEFORE (Individual Protocols)          AFTER (Cognitive Cluster)
┌───────────┐                          ┌─────────────────────────┐
│ Skill A   │──triggers──▶             │                         │
│ Skill B   │──triggers──▶  routing    │   CLUSTER SKILL         │
│ Skill C   │──triggers──▶  overhead   │   Phase 1: A            │
│ Skill D   │──triggers──▶  (N calls)  │   Phase 2: B            │
│ Skill E   │──triggers──▶             │   Phase 3: C + D + E    │
└───────────┘                          │   (1 load, 0 chaining)  │
                                       └─────────────────────────┘
```

---

## The SEO Parallel (Cross-Domain Transfer)

This is the **Topic Cluster** model from SEO, applied to AI cognition:

| Concept | SEO (Google) | AI (Athena) |
|:---|:---|:---|
| **Pillar Page** | Comprehensive authority page on a topic | **Capstone Protocol** (P501, P502) |
| **Cluster Pages** | Supporting articles linked to the pillar | **Absorbed Protocols** (archived, content lives in capstone) |
| **Internal Links** | Semantic connections between pages | **Cross-references** between phases |
| **Routing** | Google spider crawls links | **Exocortex** semantic search finds cluster |
| **Authority Signal** | Single authoritative source ranks higher | **One comprehensive skill** routes faster than 5 fragments |

### Why It Works in Both Domains

Google's ranking algorithm and AI skill routing solve the **same structural problem**:

> *Given a query, retrieve the most complete, authoritative coverage with the fewest hops.*

- **SEO**: 1 pillar page with 5 sections > 5 thin pages with overlapping keywords
- **Athena**: 1 clustered skill with 5 phases > 5 individual skills with overlapping triggers

The penalty for fragmentation is identical:

- In SEO: **keyword cannibalization** (pages compete with each other, none ranks well)
- In AI: **trigger cannibalization** (skills compete for the same query, routing becomes noisy)

---

## When to Cluster

| Signal | Example | Action |
|:---|:---|:---|
| **Co-activation rate > 60%** | Asking "should I trade?" triggers 4-5 skills | Merge into lifecycle cluster |
| **Shared input parameters** | 5 skills all need Win Rate + Risk:Reward | Merge — DRY principle |
| **Sequential dependency** | Skill A's output is Skill B's input | Merge into pipeline |
| **Same domain, different verbs** | `diagnose`, `classify`, `calibrate` all in Decision domain | Merge into phased protocol |

### When NOT to Cluster

| Signal | Example | Keep Separate |
|:---|:---|:---|
| **Cross-domain** | `seo-auditor` + `trading-risk-gate` | Different contexts entirely |
| **Different activation frequency** | `circuit-breaker` (rare) + `micro-commit` (every session) | Rare skills shouldn't bloat common ones |
| **Size > 3000 tokens** | Merged skill would exceed target load size | Split into 2 clusters max |

---

## Athena's Cognitive Clusters (Live)

> **Routing Table**: `CLUSTER_INDEX.md` (in `.agent/` — create per [Protocol 503 setup](#when-to-cluster))

| # | Cluster | Capstone | Skills | Domain |
|:---|:---|:---|:---|:---|
| 1 | **Diagnostic** | Protocol 501 | 9 protocols merged | Decision |
| 2 | **Context Lifecycle** | Protocol 502 | 4 protocols merged | Architecture |
| 3 | **Trading Risk** | `trading-risk-gate` | Ruin + Ergodicity + WR Dominance | Trading |
| 4 | **Trading Execution** | `zenith-execution` | Kelly + SL + Monte Carlo + Rebalance | Trading |
| 5 | **Trade Analytics** | `trade-journal-analyzer` | Journal + Drawdown Classification | Trading |
| 6 | **Social Contract** | `power-inversion` | BATNA + Commitment Devices + Consiglieri | Business |
| 7 | **Inner Work** | `therapeutic-ifs` | Schema Deconstruction + IFS | Psychology |
| 8 | **Adversarial QA** | `red-team-review` | Pre-Mortem + Bias Detection + Scoring | Quality |
| 9 | **Strategic Reasoning** | `decision-journal` | Decision Lifecycle + Synthetic Parallel Reasoning | Decision |
| 10 | **Distribution Engine** | `distribution-physics` | Brand Foundations + SEO Auditor | Marketing |
| 11 | **Swarm Orchestrator** | `marketing-swarm` | Marketing Swarm + Git Worktree Swarm | Orchestration |
| 12 | **Research Pipeline** | `deep-research-loop` | Deep Research + Semantic Search | Research |
| 13 | **Build Lifecycle** | `spec-driven-dev` | Spec + Micro-Commit + Visual Verify | Engineering |
| 14 | **Sovereign Safety** | Protocol 514 | Circuit Breaker + Context Compactor | Safety |
| 15 | **Problem-Solving Engine** | Protocol 504 | P504 + P115 + P505 + `red-team-review` + P506 | Reasoning |

---

## The Math

**Before (35 skills → 21 skills → 15 clusters)**:

| Stage | Avg. Skill Loads per Query | Tokens per Query | Tool Calls |
|:---|:---|:---|:---|
| Pre-Cluster (35 skills) | 3.2 | ~2,560 | 3.2 |
| Post-Cluster v1 (21 skills, 9 clusters) | 1.4 | ~1,680 | 1.4 |
| Post-Cluster v2 (15 clusters, co-activation) | **1.1** | **~1,320** | **1.1** |

**Cumulative savings**: ~48% tokens, ~66% tool calls vs original 35-skill architecture.

---

## Cross-Domain Applications

The Cognitive Cluster pattern applies anywhere fragmented knowledge creates routing overhead:

| Domain | Fragment Problem | Cluster Solution |
|:---|:---|:---|
| **SEO** | 20 thin blog posts competing for same keyword | 1 pillar page + internal links |
| **AI Skills** | 10 skills with overlapping triggers | 3 lifecycle clusters |
| **Codebase** | 15 utility functions scattered across files | 1 module with clear API |
| **Documentation** | FAQ spread across 8 pages | 1 comprehensive guide |
| **Education** | Separate courses on related topics | Integrated curriculum |

---

## Tags

# protocol #architecture #cognitive-clusters #meta-cognition #seo-parallel #cross-domain #capstone
