---
description: GTO synchronized digital portfolio update — differential feature porting from private to public repo, plus 4-surface metadata refresh with mandatory privacy sanitization
created: 2026-08-26
updated: 2026-08-28
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
> **Cadence**: Daily via scheduled prompt, or on-demand via `/portfolio-refresh` or `/do`.
> **Modes**: Interactive (user present, checkpoints active) or Scheduled (unattended, auto-approve safe categories).

---

## Phase 0: Privacy Blocklist (LOADED FIRST — persistent constraint on ALL phases)

> **Hard Rule**: This is not a step. It is a persistent constraint on every write in Phases 2 and 3.
> Every string written to any public surface must pass this filter.

### Private Data Blocklist (NEVER in public text)

| Category | Examples (BLOCKED) |
|:---|:---|
| P&L / win rates / profit factors | +S$4,581, 85.80% WR, 4.85 PF, -S$1,674, 1.76 Net PF |
| Broker names / tiers / commissions | IC Markets, Raw Pro, Raw Pro+, $3.00/lot, $2.00/lot |
| Leverage ratios | 1:1000 |
| Trade fill counts / campaign numbers | 3,841-fill, 440 campaigns, 19 journal campaigns, 3,574-Trade |
| Proprietary trading strategy names | Duration Decay Law, Spring Coil, Golden Coil Zone, Elastic Snap Zone, Tight Stop Fallacy |
| Poker / gambling platform names | Natural8, Craps (as platform context) |
| Client assignment numbers / institutions | Assignment 73, Assignment 74, NYP BM4307 |
| Client pricing / retainer amounts | $550/10-pack, Package #4 Retainer, rate card floor, Revenue Ledger |
| Personal fitness pricing | Specific dollar amounts for PT packages |
| Named case study subjects (real identities) | Takashi Kotegawa / BNF Capital |
| Specific return percentages / account sizing | +2%/mo, +6% on 1R, USD 10K notional, $500 vs $5K vs $50K |
| EV confidence intervals | +10.91% (95% CI [+7.17%, +14.47%]) |
| Personal lifestyle strategy details | Specific travel arbitrage amounts, destination lists with pricing |

### Changelog & Release Note Rules

Describe the **TYPE** of work done, not the private content:
```
✅ "Codified Protocol 528 (Sandboxed Execution Modes) and MinMax token efficiency protocol"
✅ "Filed new domain-specific case studies across trading and decision-making domains"
✅ "Updated trading risk parameters and performance tracking infrastructure"

❌ "Codified FX Daytrading 3,841-fill macro statement deep dive (+S$4,581.54 net PnL / 85.80% win rate)"
❌ "IC Markets Raw Pro tier codification (saving 57.1% commissions)"
❌ "Assignment 73 Full-Funnel Architecture & 98-slide deck"
```

### Privacy Verification Regex (Gate 2)

```bash
grep -iE '(IC Markets|Natural8|S\$[0-9]{3,}|win.?rate.*[0-9]+%|profit.?factor.*[0-9]|net P.?L.*S\$|Assignment [0-9]{2}|NYP BM|Revenue Ledger|rate card floor|\$[0-9]+/lot|[0-9]+.?fill|[0-9]+ campaigns|lowball offer|poker rake|Takashi Kotegawa|BNF Capital|\+[0-9]+%/mo|USD [0-9]+K notional|Package #[0-9]+ Retainer)'
```

---

## Phase 1: Metric Grounding & Repo Sync

1. Run `python3 .agent/scripts/sync_agents_md.py` in `Project Athena` to regenerate `.agent/config/CAPS.json`.
2. **Commit** any changes to the private repo:
   ```bash
   git -C ~/Project\ Athena add -A && \
   git -C ~/Project\ Athena diff --cached --quiet || \
   git -C ~/Project\ Athena commit -m "chore: sync CAPS.json counts"
   ```
3. Treat `CAPS.json` as the **single source of truth** for ALL counts and version numbers. Never hardcode metrics — always read from CAPS.
4. Pull active engineering focus from `.context/memory_bank/activeContext.md`.
5. **Pre-pull all repos** to prevent merge conflicts (Protocol 413):
   ```bash
   for repo in ~/Athena-Public ~/Athena-Public/Athena-Public.wiki ~/winstonkoh87 ~/winstonkoh87.github.io ~/sg-assignment-helper; do
     [ -d "$repo/.git" ] && git -C "$repo" pull --rebase --quiet 2>/dev/null
   done
   ```
6. **Idempotency check**: Read the latest changelog entry date in `~/Athena-Public/README.md`. If today's date already appears as the most recent entry AND Phase 2 has no delta, skip to a lightweight verification-only pass (Phase 4 gates only).

---

## Phase 2: Differential Feature Port (Auto-skips if no delta)

### 2.1: Delta Detection

Determine the sync anchor and compute what's new:

```bash
cd ~/Athena-Public
LAST_TAG=$(git describe --tags --abbrev=0)
TAG_DATE=$(git log $LAST_TAG -1 --format=%ci)
echo "Last release: $LAST_TAG ($TAG_DATE)"
```

Find new AND significantly modified files in the private repo since that date:

```bash
cd ~/Project\ Athena

# Added files
ADDED=$(git log --since="$TAG_DATE" --diff-filter=A --name-only --format="" -- \
  '.agent/skills/protocols/*.md' \
  '.agent/workflows/*.md' \
  '.agent/workflows/_domain/*.md' \
  '.agent/skills/*/SKILL.md' \
  '.agent/scripts/*.py' \
  'src/athena/**/*.py' | sort -u)

# Modified files with >50 lines changed (significant rewrites)
MODIFIED=$(git log --since="$TAG_DATE" --diff-filter=M --numstat --format="" -- \
  '.agent/skills/protocols/*.md' \
  '.agent/workflows/*.md' \
  '.agent/skills/*/SKILL.md' \
  '.agent/scripts/*.py' \
  'src/athena/**/*.py' | awk '$1+$2 > 50 {print $3}' | sort -u)

DELTA_LIST=$(echo -e "$ADDED\n$MODIFIED" | sort -u | grep -v '^$')
echo "$DELTA_LIST"
```

If DELTA_LIST is empty → skip directly to Phase 3.

### 2.2: Triage (Category-Level Defaults + Per-File Override)

Classify each file in DELTA_LIST:

| Tier | Categories |
|:--|:--|
| **ALWAYS PORT** | `architecture/`, `coding/`, `engineering/`, `memory/`, `meta/`, `quality/`, `reasoning/`, `research/`, `safety/`, `verification/`, `workflow/`, `design/`, `qa/` |
| **ALWAYS REJECT** | `trading/` (unless pure risk math with zero P&L), `psychology/`, `behavioral/`, `case-studies/` with real names |
| **TRIAGE INDIVIDUALLY** | `business/`, `decision/`, `strategy/`, `pattern-detection/`, `creation/`, `communication/`, `marketing/`, `singapore/`, `diagnostics/`, `case-studies/` (generic patterns only) |

**Mode-dependent behavior:**
- **Interactive** (user present): Present triage table `| File | Category | Tier | Reason |` and **[CHECKPOINT] wait for user approval**.
- **Scheduled** (unattended): Auto-approve ALWAYS PORT files, auto-reject ALWAYS REJECT files, **defer TRIAGE INDIVIDUALLY files** — log to `activeContext.md` under `@pending` for next interactive session.

### 2.3: Sanitized Porting

For each approved file:

1. **Copy to correct public destination**:
   - Protocols → `~/Athena-Public/examples/protocols/<category>/`
   - Workflows → `~/Athena-Public/examples/workflows/` (or `_domain/`)
   - Scripts → `~/Athena-Public/scripts/` (production) or `~/Athena-Public/examples/scripts/` (reference)
   - Skills → `~/Athena-Public/examples/skills/<domain>/`

2. **Sanitize content** (ALL of the following — enforce Phase 0 blocklist):
   - Rewrite `` → relative paths
   - Rewrite `` → relative paths
   - Strip ALL content matching the Phase 0 Privacy Blocklist
   - For Tier 2 (Abstract) files: replace private examples with `<!-- Example redacted: [domain] context -->` and keep the framework structure
   - **Run `ruff check --fix` on any ported `.py` files** (CI enforces ruff)

3. **Per-file privacy verification** (before staging):
   - Valid markdown (no broken headers/links)
   - Zero matches against the Phase 0 Privacy Verification Regex
   - Internal cross-references resolve within the public repo

### 2.4: Release Documentation

1. Update `~/Athena-Public/docs/CHANGELOG.md` — describe TYPE of work, never private content.
2. Update `~/Athena-Public/AGENTS.md` Docs Index line if workflow/skill/protocol counts changed.
3. Update `~/Athena-Public/docs/ARCHITECTURE.md` workspace tree if counts changed.
4. Determine version: new tag = patch increment from `git describe --tags --abbrev=0`, or read from `CAPS.json .version.system`.

---

## Phase 3: 4-Surface Metadata Refresh (PARALLEL EXECUTION)

> **Parallelization**: Launch Subagent A (Athena-Public + Wiki + Release) and Subagent B (Profile + Personal Site + Commercial Site) concurrently. They operate on different repositories with zero file overlap.
>
> **Dynamic metrics**: Every subagent reads counts from CAPS.json — never hardcode.
>
> **Privacy**: Every subagent enforces Phase 0 blocklist on all writes.
>
> **IndexNow keys**: Discover from filesystem (look for `*.txt` key verification files in each site's `public/` or root directory). Do NOT hardcode keys in prompts or commit messages.

### Subagent A: Athena-Public Core, Releases & Wiki

**Core README & Docs** (`~/Athena-Public`):
- Update `README.md`, `docs/ARCHITECTURE.md`, `docs/BENCHMARKS.md`, `docs/REFERENCES.md`.
- Sync all metrics from `CAPS.json` and timestamps to today's date.
- Add single-line changelog entry under `<details>`:
  - If Phase 2 ran: `- **[Version] — Feature Port + Portfolio Refresh** ([Date]): Ported [X] new modules to public repo. Updated canonical CAPS counts ([read from CAPS.json]). [Generic domain description].`
  - If Phase 2 skipped: `- **Full Synchronized Digital Portfolio Refresh** ([Date]): Synchronized portfolio update across all public surfaces. Updated canonical CAPS counts ([read from CAPS.json]).`

**Releases** (`winstonkoh87/Athena-Public`):
- If Phase 2 ran (new version tag): create new release with structured sections (Architecture Highlights / New Protocols & Tooling / Canonical Metrics).
- If Phase 2 skipped: edit latest release notes with today's date refresh section.

**Wiki** (`~/Athena-Public/Athena-Public.wiki`):
- Update all 8 pages with current metrics and today's date:
  `Home.md`, `Architecture-Overview.md`, `Getting-Started.md`, `FAQ.md`, `Philosophy.md`, `Use-Cases.md`, `Workflow-Reference.md`, `The-Compounding-Effect.md`.

**Inline Privacy Gate (before commit)**:
```bash
git -C ~/Athena-Public add -A
git -C ~/Athena-Public diff --cached | grep -iE '<Phase 0 regex>' && echo "❌ BLOCKED" && exit 1
```
If clean → commit and push. Same for wiki repo.

### Subagent B: GitHub Profile + Personal Site + Commercial Site

**B.2 — GitHub Profile** (`~/winstonkoh87`):
- Update `README.md` with today's date, CAPS.json metrics, active engineering focus areas.

**B.3 — Personal Website** (`~/winstonkoh87.github.io`):
- `src/data/site-stats.ts`: Read version and counts from CAPS.json.
- `src/layouts/Layout.astro` & `src/pages/index.astro`: Schema.org `dateModified` to today.
- `public/sitemap.xml`: All `<lastmod>` to today.
- `README.md` & `package.json`: Bump timestamps.
- **Build verification**: `cd ~/winstonkoh87.github.io && npm run build` — must exit 0.
- **IndexNow**: Discover key from filesystem, POST to `api.indexnow.org`.

**B.4 — Commercial Website** (`~/sg-assignment-helper`):
- `index.html`: Schema.org JSON-LD `dateModified`.
- `sitemap.xml`: All `<lastmod>` to today.
- `README.md`: Bump timestamp.
- **IndexNow**: Discover key from filesystem, POST to `api.indexnow.org`.

**Push** (each repo): `git pull --rebase && git add -A && git diff --cached --quiet || git commit -m "chore: portfolio refresh [date]" && git push origin main`.

---

## Phase 4: Triple Gate Verification (AFTER all subagents complete)

> Gates run on the FINAL state of each repo, after all commits and pushes.
> This is a verification pass — subagents already ran inline privacy gates before their commits.

### Gate 1: Static Scanner
```bash
bash ~/Athena-Public/scripts/pre_deploy_scan.sh ~/Athena-Public
```
Must exit 0 (warnings OK, violations NOT OK). If violations → revert last commit, fix, re-push.

### Gate 2: CI Verification
```bash
gh run list --repo winstonkoh87/Athena-Public --limit 3
```
All workflows must show `completed / success`. If any failed → diagnose via `gh run view <id> --log-failed`, fix, re-push.

### Gate 3: Cross-Surface Consistency
Verify no stale dates or conflicting version numbers across all surfaces:
```bash
TODAY=$(date +%Y-%m-%d)
for file in \
  ~/Athena-Public/README.md \
  ~/winstonkoh87/README.md \
  ~/winstonkoh87.github.io/public/sitemap.xml \
  ~/sg-assignment-helper/sitemap.xml; do
  grep -q "$TODAY" "$file" && echo "✅ $file" || echo "❌ STALE: $file"
done
```

If all gates pass → output unified execution summary.
If any gate fails → fix and re-run only the failed gate.

---

## Error Recovery

| Failure | Recovery |
|:---|:---|
| Phase 2 porting failure | Discard: `git -C ~/Athena-Public checkout -- .` → skip to Phase 3 |
| Subagent push failure | `git pull --rebase` → retry push. If conflict, resolve minimally. |
| CI failure | `gh run view <id> --log-failed` → fix specific issue → `fix:` commit → re-push |
| Gate violation | Do NOT proceed to other surfaces. Fix failing surface first. |
| Unresolved failure | Log to `.context/memory_bank/activeContext.md` under `@pending` |

---

## Tagging

# workflow #portfolio #public-repo #privacy #feature-port #law1 #daily-scheduled
