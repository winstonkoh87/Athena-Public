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

> **Purpose**: Synchronized update of public-facing digital surfaces with autonomous upstream feature delta discovery and sanitized porting.
> **Risk Level**: HIGH — public-facing. Private data leak = reputational ruin (Law #1).
> **Cadence**: Event-driven (on new feature/version releases) or Weekly. NEVER daily mindless date-bumping.
> **Modes**: Interactive (user present, checkpoints active) or Scheduled (unattended, auto-approve safe categories).
> **Hard Invariant**: Zero Zero-Delta Pushes. If no new features, protocols, or content changes exist, DO NOT touch timestamps, DO NOT bump sitemap <lastmod>, DO NOT ping IndexNow, and DO NOT push empty date-bump commits. Search engines penalize artificial date cycling.


---

## Phase 0: Privacy Blocklist (LOADED FIRST — persistent constraint on ALL phases)

> **Hard Rule**: This is not a step. It is a persistent constraint on every write in Phases 2 and 3.
> Every string written to any public surface must pass this filter.

### Private Data Blocklist (NEVER in public text)

| Category | Description of Blocked Content |
|:---|:---|
| P&L / win rates / profit factors | Any realized/unrealized P&L figures, win-rate percentages, profit factors, or Sharpe/Sortino ratios |
| Broker names / tiers / commissions | Commercial brokerage names, private account tier labels, commission rates per lot |
| Leverage ratios | Specific account leverage multiples or margin bracket multipliers |
| Trade fill counts / campaign numbers | Exact lifetime statement fill counts, trade setup tallies, or internal journal IDs |
| Proprietary trading strategy names | Proprietary setup designations, execution zone labels, and edge mechanics |
| Poker / gambling platform names | Platform names, rake structures, and bankroll figures |
| Client assignment numbers / institutions | Commercial assignment IDs, client university names, course module codes |
| Client pricing / retainer amounts | Package pricing, retainers, hourly rate floors, commercial deal figures |
| Personal fitness pricing | Personal trainer package costs, session rates, contract terms |
| Named case study subjects (real identities) | Names of counter-parties, clients, private individuals, or entities |
| Specific return percentages / account sizing | Target yield percentages, notional account balances, tranche allocations |
| EV confidence intervals | Numerical EV calculations with confidence interval bands |
| Personal lifestyle strategy details | Personal living expenses, travel budgets, lease costs, or relocation models |

### Changelog & Release Note Rules

Describe the **TYPE** of work done, not the private content:
```
✅ "Codified Protocol 528 (Sandboxed Execution Modes) and MinMax token efficiency protocol"
✅ "Filed new domain-specific case studies across trading and decision-making domains"
✅ "Updated trading risk parameters and performance tracking infrastructure"

❌ "[Domain] statement deep dive (+S$[Real PnL] / [Real Win Rate])"
❌ "[Broker] [Account Tier] commission audit"
❌ "Assignment [Client ID] deliverables compilation"
```

### Privacy Verification (Gate 2)

Run `.github/scripts/privacy_scan.py --all` before staging or committing any public release.

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
   for repo in ~/Athena-Public ~/Athena-Public.wiki ~/winstonkoh87 ~/winstonkoh87.github.io ~/sg-assignment-helper; do
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
### Delta Gate (Phase 2 to Phase 3 Bridge)

> **Zero-Delta Invariant**: If Phase 2 DELTA_LIST is empty AND canonical `CAPS.json` counts are unchanged AND no local markdown/code edits occurred across subagent repos:
> **TERMINATE IMMEDIATELY**. Output:
> `[STATUS: CLEAN — ZERO DELTA DETECTED. Public surfaces are current; skipping metadata bumps.]`
> Do NOT touch sitemap `<lastmod>`, do NOT ping IndexNow, do NOT push empty date-bump commits.

### Subagent A: Athena-Public Core, Releases & Wiki

**Core README & Docs** (`~/Athena-Public`):
- Update `README.md`, `docs/ARCHITECTURE.md`, `docs/BENCHMARKS.md`, `docs/REFERENCES.md` ONLY when metrics in `CAPS.json` or underlying code/protocols actually changed.
- Add structured changelog entry under `<details>` ONLY when new features or protocols were ported.

**Releases** (`winstonkoh87/Athena-Public`):
- Create a new release tag and release notes ONLY when a new version is declared (e.g. patch/minor/major release with ported features).
- NEVER edit release notes just to bump dates without feature additions.

**Wiki** (`~/Athena-Public.wiki`):
- Update wiki pages ONLY when canonical metrics, architecture, or workflow documentation change.

**Inline Privacy Gate (before commit)**:
```bash
git -C ~/Athena-Public add -A
git -C ~/Athena-Public diff --cached | grep -iE '<Phase 0 regex>' && echo "❌ BLOCKED" && exit 1
```
If clean → commit and push. Same for wiki repo.

### Subagent B: GitHub Profile + Personal Site + Commercial Site

**B.2 — GitHub Profile** (`~/winstonkoh87`):
- Update `README.md` ONLY when CAPS.json counts change or active engineering focus shifts.

**B.3 — Personal Website** (`~/winstonkoh87.github.io`):
- `src/data/site-stats.ts`: Update version and counts when CAPS.json changes.
- `public/sitemap.xml`: Update `<lastmod>` ONLY for URLs whose page source or component actually changed.
- **Build verification**: `cd ~/winstonkoh87.github.io && npm run build` — must exit 0.
- **IndexNow**: Post to `api.indexnow.org` ONLY when pages are added or modified.

**B.4 — Commercial Website** (`~/sg-assignment-helper`):
- `index.html`: Update Schema.org `dateModified` ONLY on genuine copy/service edits.
- `sitemap.xml`: Update `<lastmod>` ONLY for modified content.
- **IndexNow**: Post to `api.indexnow.org` ONLY when content changed.

**Push** (each repo): Commit only when `git diff --cached` has real changes:
`git pull --rebase && git diff --cached --quiet || git commit -m "docs: sync portfolio metadata to [version]" && git push origin main`.


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
