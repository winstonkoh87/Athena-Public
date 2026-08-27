---
description: GTO synchronized digital portfolio update — differential feature porting from private to public repo, plus 4-surface metadata refresh with mandatory privacy sanitization
created: 2026-08-26
updated: 2026-08-27
model: default
tools:
  read: true
  write: true
  bash: true
  search: false
---

# /portfolio-refresh — GTO Digital Portfolio Sync & Feature Port

> **Purpose**: Synchronized update of all public-facing digital surfaces to today's date, with autonomous upstream feature delta discovery and sanitized porting.
> **Risk Level**: HIGH — public-facing. Private data leak = reputational ruin (Law #1).
> **Cadence**: On-demand via `/portfolio-refresh` or `/do`.

---

## Phase 0: Metric & Count Grounding (Single Source of Truth)

1. Run `python3 .agent/scripts/sync_agents_md.py` inside `Project Athena` to recalculate canonical inventory counts, update `AGENTS.md`, and write `.agent/config/CAPS.json`.
2. Treat `.agent/config/CAPS.json` as the strict single source of truth for all counts (Protocols: active/total, Workflows: root/domain/total, Skills, Scripts, and Sessions).
3. Pull current active engineering focus from `.context/memory_bank/activeContext.md`.

---

## Phase A: Differential Feature Port (Auto-skips if no delta)

### A.1: Delta Detection

Determine the sync anchor and compute what's new:

```bash
cd ~/Athena-Public
LAST_TAG=$(git describe --tags --abbrev=0)
TAG_DATE=$(git log $LAST_TAG -1 --format=%ci)
echo "Last release: $LAST_TAG ($TAG_DATE)"
```

Then find new files in the private repo since that date:

```bash
cd ~/Project\ Athena
git log --since="$TAG_DATE" --diff-filter=A --name-only --format="" -- \
  '.agent/skills/protocols/*.md' \
  '.agent/workflows/*.md' \
  '.agent/workflows/_domain/*.md' \
  '.agent/skills/*/SKILL.md' \
  '.agent/scripts/*.py' \
  'src/athena/**/*.py' | sort -u
```

If DELTA_LIST is empty → skip directly to Phase B.

### A.2: Triage (Category-Level Defaults + Per-File Override)

Classify each file in DELTA_LIST using these defaults:

**ALWAYS PORT** (generic engineering value, no private data):
`architecture/`, `coding/`, `engineering/`, `memory/`, `meta/`, `quality/`, `reasoning/`, `research/`, `safety/`, `verification/`, `workflow/`, `design/`, `qa/`

**ALWAYS REJECT** (personal/private by nature):
`trading/` (unless pure risk math with zero P&L), `psychology/`, `behavioral/`, `case-studies/` with real names

**TRIAGE INDIVIDUALLY** (read the file, decide per-item):
`business/`, `decision/`, `strategy/`, `pattern-detection/`, `creation/`, `communication/`, `marketing/`, `singapore/`, `diagnostics/`, `case-studies/` (generic patterns only)

Present a triage table to the user:
| File | Category | Tier (Port/Abstract/Reject) | Reason |

**[CHECKPOINT] Wait for user approval before proceeding to A.3.**

### A.3: Sanitized Porting

For each approved file:

1. **Copy to correct public destination**:
   - Protocols → `~/Athena-Public/examples/protocols/<category>/`
   - Workflows → `~/Athena-Public/examples/workflows/` (or `_domain/`)
   - Scripts → `~/Athena-Public/scripts/` (production) or `~/Athena-Public/examples/scripts/` (reference)
   - Skills → `~/Athena-Public/examples/skills/<domain>/`

2. **Sanitize content** (apply ALL of the following):
   - Rewrite `./` → relative paths
   - Rewrite `./` → relative paths
   - Strip content matching the Privacy Blocklist (Phase 0.9)
   - For Tier 2 (Abstract) files: replace private examples with `<!-- Example redacted: [domain] context -->` and keep the framework structure

3. **Verify each ported file**:
   - Valid markdown (no broken headers/links)
   - Zero blocklist matches (`grep -iE` with the Phase 0.9 regex)
   - Internal cross-references resolve within the public repo

### A.4: Release Documentation

1. Update `~/Athena-Public/docs/CHANGELOG.md` with a structured section:
   ```
   ## [Next Version] — Feature Port ([Today's Date])
   - List each ported module with 1-line description
   - System/architecture: describe specifically
   - Domain work: describe generically per blocklist
   ```

2. Update `~/Athena-Public/AGENTS.md` Docs Index line if workflow/skill/protocol counts changed.

3. Update `~/Athena-Public/docs/ARCHITECTURE.md` workspace tree if counts changed.

---

## Phase 0.9: Privacy Sanitization Rules (MANDATORY — applies to ALL public-facing writes)

> **Hard Rule**: NEVER propagate private Exocortex content into public surfaces.

### Private Data Blocklist (NEVER in public text)

| Category | Examples (BLOCKED) |
|:---|:---|
| P&L / win rates / profit factors | Exact dollar amounts, win rate %, profit factors |
| Broker names / tiers / commissions | Specific broker names, account tiers, commission rates |
| Leverage ratios | High-leverage ratios |
| Trade fill counts / campaign numbers | Specific fill counts, campaign identifiers, trade numbers |
| Proprietary trading strategy names | Internal strategy identifiers |
| Poker / gambling platform names | Platform names |
| Client assignment numbers / institutions | Assignment codes, institution names |
| Client pricing / retainer amounts | Package retainer pricing, rate card floor, Revenue Ledger |
| Personal fitness pricing | Specific dollar amounts for PT packages |
| Named case study subjects (real identities) | Real individual names |
| Specific return percentages / account sizing | Specific return %, notional account sizes |
| EV confidence intervals | Specific EV calculation figures |
| Personal lifestyle strategy details | Specific travel arbitrage amounts, destination lists with pricing |

### Changelog & Release Note Rules

Describe the **TYPE** of work done, not the private content:
```
✅ "Codified Protocol 528 (Sandboxed Execution Modes) and MinMax token efficiency protocol"
✅ "Filed new domain-specific case studies across trading and decision-making domains"
✅ "Updated trading risk parameters and performance tracking infrastructure"

❌ "Codified private trading execution statement deep dive (+S$X,XXX net PnL / XX.X% win rate)"
❌ "Proprietary broker tier codification (saving XX.X% commissions)"
❌ "Specific client assignment full-funnel architecture & slide deck"
```

---

## Phase B: 4-Surface Metadata Refresh

### B.1: Athena-Public Core, Releases & Wiki

**Core README & Docs** (`~/Athena-Public`):
- Update `README.md`, `docs/ARCHITECTURE.md`, `docs/BENCHMARKS.md`, `docs/REFERENCES.md`.
- Sync version tags (`v9.9.9`), `CAPS.json` metrics, benchmark tables (Hit@5 0.892, MRR@5 0.769), and header timestamps.
- Add single-line changelog entry under `<details>`:
  - If Phase A ran: `- **[Version] — Feature Port + Portfolio Refresh** ([Date]): Ported [X] new protocols/scripts to public repo. Updated canonical CAPS counts ([counts]). [Generic domain description].`
  - If Phase A skipped: `- **Full Synchronized Digital Portfolio Refresh** ([Date]): Synchronized complete portfolio update across all 4 public surfaces, releases, wiki, and internal docs. Updated canonical CAPS counts ([counts]). [Generic domain description].`

**Releases** (`winstonkoh87/Athena-Public`):
- If Phase A ran: create new release with structured sections (Architecture Highlights / New Protocols & Tooling / Canonical Metrics).
- If Phase A skipped: edit latest release notes with today's date section.

**Wiki** (`~/Athena-Public/Athena-Public.wiki`):
- Pull latest, update all 8 pages with current metrics and today's date:
  `Home.md`, `Architecture-Overview.md`, `Getting-Started.md`, `FAQ.md`, `Philosophy.md`, `Use-Cases.md`, `Workflow-Reference.md`, `The-Compounding-Effect.md`.

**CI Gates**: Run `gh run list --repo winstonkoh87/Athena-Public` to verify all CI workflows pass green.

### B.2: GitHub Profile

Update `~/winstonkoh87/README.md` with today's date in header, current `CAPS.json` metrics in comparison table, and active focus areas.

### B.3: Personal Website (`winstonkoh87.com`)

In `~/winstonkoh87.github.io`:
- `src/data/site-stats.ts`: Update version, active protocol count, session milestone.
- `src/layouts/Layout.astro` & `src/pages/index.astro`: Meta tags, Schema.org `dateModified`, footer.
- `public/sitemap.xml`: All `<lastmod>` to today (`YYYY-MM-DD`).
- `README.md` & `package.json`: Bump timestamps.
- **IndexNow Ping**: `curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d '{"host":"winstonkoh87.com","key":"${INDEXNOW_KEY}","keyLocation":"https://winstonkoh87.com/${INDEXNOW_KEY}.txt","urlList":["https://winstonkoh87.com/"]}'`

### B.4: Commercial Website (`sgassignmenthelp.com`)

In `~/sg-assignment-helper`:
- `index.html`: Schema.org JSON-LD `dateModified`, footer date.
- `sitemap.xml`: All `<lastmod>` to today.
- `README.md`: Bump timestamp.
- **IndexNow Ping**: `curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d '{"host":"sgassignmenthelp.com","key":"${INDEXNOW_KEY}","keyLocation":"https://sgassignmenthelp.com/${INDEXNOW_KEY}.txt","urlList":["https://sgassignmenthelp.com/"]}'`

---

## Phase C: Sanitization, Safety & Push (Triple Gate)

### Gate 1: Pre-Deploy Scan
```bash
bash ~/Athena-Public/scripts/pre_deploy_scan.sh ~/Athena-Public
```

### Gate 2: Content-Level Privacy Verification (MANDATORY)
```bash
git -C ~/Athena-Public diff --cached | grep -iE \
  '(CONFIDENTIAL_BROKER|CONFIDENTIAL_PLATFORM|S\$[0-9]{3,}|win.?rate.*[0-9]+%|profit.?factor.*[0-9]|net P.?L.*S\$|Assignment [0-9]{2}|NYP BM|Revenue Ledger|rate card floor|\$[0-9]+/lot|[0-9]+.?fill|[0-9]+ campaigns|lowball offer|poker rake|CONFIDENTIAL_INDIVIDUAL|CONFIDENTIAL_FUND|\+[0-9]+%/mo|USD [0-9]+K notional|Package #[0-9]+ Retainer)'
```
**If ANY matches are found → sanitize before committing. Do not override.**

### Gate 3: Push & CI Verification
- Commit and push to `main` across all 4 repositories and the wiki repo.
- If Phase A ran: tag the new version (`git tag -a v9.9.X -m "Feature Port [Date]"`) and push tags.
- Verify all public sites reflect zero stale dates or conflicting version numbers.

---

## Tagging

# workflow #portfolio #public-repo #privacy #feature-port #law1

