---
description: GTO synchronized portfolio refresh across all 4 public surfaces, releases, wiki, and internal docs — with mandatory privacy sanitization
created: 2026-08-26
updated: 2026-08-26
model: default
tools:
  read: true
  write: true
  bash: true
  search: false
---

# /portfolio-refresh — GTO Digital Portfolio Sync

> **Purpose**: Synchronized update of all public-facing digital surfaces to today's date.
> **Risk Level**: HIGH — public-facing. Private data leak = reputational ruin (Law #1).
> **Cadence**: Scheduled or on-demand via `/do`.

---

## Phase 0: Metric & Count Grounding (Single Source of Truth)

1. Run `python3 .agent/scripts/sync_agents_md.py` inside `Project Athena` to recalculate canonical inventory counts, update `AGENTS.md`, and write `.agent/config/CAPS.json`.
2. Treat `.agent/config/CAPS.json` as the strict single source of truth for all counts (Protocols: active/total, Workflows: root/domain/total, Skills, Scripts, and Sessions).
3. Pull current active engineering focus from `.context/memory_bank/activeContext.md`.

---

## Phase 0.5: Privacy Sanitization Rules (MANDATORY — applies to ALL public-facing writes)

> **Hard Rule**: NEVER propagate private Exocortex content into public surfaces.
> This phase is not a scan — it is a compositional constraint that governs every
> word written into any public-facing file during this workflow.

### Private Data Blocklist (NEVER in public text)

| Category | Examples (BLOCKED) |
|:---|:---|
| P&L / win rates / profit factors | Exact currency P&L, Win rates, Profit factors |
| Broker names / tiers / commissions | Specific broker names, custom tiers, commission rates |
| Leverage ratios | High leverage ratios |
| Trade fill counts / campaign numbers | Specific fill counts, trade numbers |
| Proprietary trading strategy names | Proprietary strategy names, internal indicator mechanics |
| Poker / gambling platform names | Commercial platform names |
| Client assignment numbers / institutions | Specific client IDs, module codes, university names |
| Client pricing / retainer amounts | Package pricing figures, Retainer amounts, custom hourly floors |
| Personal fitness pricing | Specific dollar amounts for fitness packages |
| Named case study subjects (real identities) | Real third-party individual or fund names |
| Specific return percentages / account sizing | Explicit return targets, exact bankroll amounts |
| EV confidence intervals | Specific EV percentage intervals |
| Personal lifestyle strategy details | Specific travel arbitrage amounts, destination lists with pricing |

### Changelog & Release Note Rules

Describe the **TYPE** of work done, not the private content:

```
✅ "Filed new domain-specific case studies across trading and decision-making domains"
✅ "Codified new operational codifications and system architecture documentation"
✅ "Updated trading risk parameters and performance tracking infrastructure"

❌ "[Generic Example] Codified specific trade fill statement deep dive (+S$X,XXX net PnL)"
❌ "[Generic Example] Specific broker commission tier optimization"
❌ "[Generic Example] Client assignment deck delivery"
```

**System/architecture changes ARE safe** to describe specifically (e.g. "Zero-Iteration Agent Harness Framework", "GTO Self-RSI Architecture", "Backpressure Circuit Breaker").

**README changelog template**:
```
- **Full Synchronized Digital Portfolio Refresh** ([Date]): Synchronized complete portfolio update across all 4 public surfaces, releases, wiki, and internal docs. Updated canonical CAPS counts ([counts from CAPS.json]). [Generic description of domain work, per Phase 0.5 rules].
```

---

## Phase 1: Athena-Public Core, Releases & Wiki

### Core README & Docs (`~/Athena-Public`)

- Update `README.md`, `docs/ARCHITECTURE.md`, `docs/BENCHMARKS.md`, `docs/REFERENCES.md`.
- Sync all version tags, `CAPS.json` metrics, benchmark tables (Hit@5 0.892, MRR@5 0.769), and header timestamps.
- Add single-line changelog entry using Phase 0.5 template.

### Releases (`winstonkoh87/Athena-Public`)

- Edit latest release notes with today's date section.
- Add ONLY system/architecture changes and generic domain descriptions.
- **NEVER include private trading, financial, or client data.**

### Wiki (`~/Athena-Public/Athena-Public.wiki`)

- Pull latest, update all 8 pages with current metrics and today's date.
- Pages: `Home.md`, `Architecture-Overview.md`, `Getting-Started.md`, `FAQ.md`, `Philosophy.md`, `Use-Cases.md`, `Workflow-Reference.md`, `The-Compounding-Effect.md`.

### CI Gates

- Run `gh run list --repo winstonkoh87/Athena-Public` to verify all CI workflows pass green.

---

## Phase 2: GitHub Profile

- Update `~/winstonkoh87/README.md` with today's date in header, current `CAPS.json` metrics in comparison table, and active focus areas.

---

## Phase 3: Personal Website (`winstonkoh87.com`)

In `~/winstonkoh87.github.io`:

- `src/data/site-stats.ts`: Update version, active protocol count, session milestone.
- `src/layouts/Layout.astro` & `src/pages/index.astro`: Meta tags, Schema.org `dateModified`, footer.
- `public/sitemap.xml`: All `<lastmod>` to today (`YYYY-MM-DD`).
- `README.md` & `package.json`: Bump timestamps.
- **IndexNow Ping**: `curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d '{"host":"winstonkoh87.com","key":"${INDEXNOW_KEY}","keyLocation":"https://winstonkoh87.com/${INDEXNOW_KEY}.txt","urlList":["https://winstonkoh87.com/"]}'`

---

## Phase 4: Commercial Website (`sgassignmenthelp.com`)

In `~/sg-assignment-helper`:

- `index.html`: Schema.org JSON-LD `dateModified`, footer date.
- `sitemap.xml`: All `<lastmod>` to today.
- `README.md`: Bump timestamp.
- **IndexNow Ping**: `curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d '{"host":"sgassignmenthelp.com","key":"${INDEXNOW_KEY}","keyLocation":"https://sgassignmenthelp.com/${INDEXNOW_KEY}.txt","urlList":["https://sgassignmenthelp.com/"]}'`

---

## Phase 5: Sanitization, Safety & Push

### Gate 1: Pre-Deploy Scan

```bash
bash ~/Athena-Public/scripts/pre_deploy_scan.sh ~/Athena-Public
```

### Gate 2: Content-Level Privacy Verification (MANDATORY)

After staging but BEFORE committing, run the privacy scanner on staged diffs:

```bash
python3 .github/scripts/privacy_scan.py --staged
```

**If ANY violations are found → sanitize before committing. Do not override.**

### Gate 3: Push

- Commit and push to `main` across all 4 repositories and the wiki repo.
- Verify all public sites reflect zero stale dates or conflicting version numbers.

---

## Tagging

# workflow #portfolio #public-repo #privacy #scheduled #law1
