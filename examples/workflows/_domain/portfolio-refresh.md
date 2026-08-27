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

| Category | What to Block |
|:---|:---|
| P&L / win rates / profit factors | Exact dollar figures, win/loss rates, profit factor numbers |
| Broker names / tiers / commissions | Specific broker names, tier details, commission rates |
| Leverage ratios | Exact leverage numbers |
| Trade fill counts / campaign numbers | Specific fill counts, campaign totals |
| Proprietary trading strategy names | Internal strategy names or mechanics |
| Gambling platform names | Platform names in gambling context |
| Client identifiers / institutions | Assignment numbers, institution names |
| Client pricing / retainer amounts | Specific pricing, rate cards, revenue entries |
| Personal fitness pricing | Specific dollar amounts for packages |
| Named case study subjects | Real identities of case study subjects |
| Specific return percentages / sizing | Monthly return %, account sizing details |
| EV confidence intervals | Specific statistical intervals |
| Personal lifestyle strategy details | Travel arbitrage amounts, destination pricing |

### Changelog & Release Note Rules

Describe the **TYPE** of work done, not the private content:
```
✅ "Codified Protocol 528 (Sandboxed Execution Modes) and MinMax token efficiency protocol"
✅ "Filed new domain-specific case studies across trading and decision-making domains"

❌ Specific P&L figures, broker names, client details, or strategy internals
```
System/architecture changes ARE safe to describe specifically.

### Privacy Verification Regex (Gate 2)

Define a project-specific regex pattern for your blocklist terms. Run it against every staged diff before committing:

```bash
git diff --cached | grep -iE '<your_blocklist_regex>'
```

---

## Phase 1: Metric Grounding & Repo Sync

1. Run your canonical count regeneration script to produce a single-source-of-truth config file (e.g., `CAPS.json`).
2. **Commit** any changes to the private repo.
3. Treat the config file as the **single source of truth** for ALL counts and version numbers. Never hardcode metrics — always read from config.
4. Pull active engineering focus from your session state / context files.
5. **Pre-pull all repos** to prevent merge conflicts:
   ```bash
   for repo in <list_of_all_target_repos>; do
     [ -d "$repo/.git" ] && git -C "$repo" pull --rebase --quiet 2>/dev/null
   done
   ```
6. **Idempotency check**: Read the latest changelog entry date. If today's date already appears as the most recent entry AND Phase 2 has no delta, skip to a lightweight verification-only pass (Phase 4 gates only).

---

## Phase 2: Differential Feature Port (Auto-skips if no delta)

### 2.1: Delta Detection

Determine the sync anchor and compute what's new:

```bash
cd <public_repo>
LAST_TAG=$(git describe --tags --abbrev=0)
TAG_DATE=$(git log $LAST_TAG -1 --format=%ci)
echo "Last release: $LAST_TAG ($TAG_DATE)"
```

Find new AND significantly modified files in the private repo since that date:

```bash
cd <private_repo>

# Added files
ADDED=$(git log --since="$TAG_DATE" --diff-filter=A --name-only --format="" -- \
  '<portworthy_paths>' | sort -u)

# Modified files with >50 lines changed (significant rewrites)
MODIFIED=$(git log --since="$TAG_DATE" --diff-filter=M --numstat --format="" -- \
  '<portworthy_paths>' | awk '$1+$2 > 50 {print $3}' | sort -u)

DELTA_LIST=$(echo -e "$ADDED\n$MODIFIED" | sort -u | grep -v '^$')
```

If DELTA_LIST is empty → skip directly to Phase 3.

### 2.2: Triage (Category-Level Defaults + Per-File Override)

Classify each file in DELTA_LIST:

| Tier | Categories |
|:--|:--|
| **ALWAYS PORT** | Generic engineering value, no private data (architecture, coding, engineering, quality, reasoning, research, safety, verification, workflow, design, QA) |
| **ALWAYS REJECT** | Personal/private by nature (trading P&L, psychology, behavioral, case-studies with real names) |
| **TRIAGE INDIVIDUALLY** | Read the file, decide per-item (business, decision, strategy, pattern-detection, diagnostics, generic case studies) |

**Mode-dependent behavior:**
- **Interactive** (user present): Present triage table and **[CHECKPOINT] wait for user approval**.
- **Scheduled** (unattended): Auto-approve ALWAYS PORT, auto-reject ALWAYS REJECT, **defer TRIAGE INDIVIDUALLY** — log to context file under pending for next interactive session.

### 2.3: Sanitized Porting

For each approved file:

1. **Copy to correct public destination** (maintain category directory structure).

2. **Sanitize content** (ALL of the following — enforce Phase 0 blocklist):
   - Rewrite absolute private paths → relative paths
   - Strip ALL content matching the Phase 0 Privacy Blocklist
   - For Tier 2 (Abstract) files: replace private examples with `<!-- Example redacted: [domain] context -->` and keep the framework structure
   - **Run linter** on any ported code files (CI enforces lint rules)

3. **Per-file privacy verification** (before staging):
   - Valid markdown (no broken headers/links)
   - Zero matches against the Phase 0 Privacy Verification Regex
   - Internal cross-references resolve within the public repo

### 2.4: Release Documentation

1. Update changelog — describe TYPE of work, never private content.
2. Update docs index if counts changed.
3. Update architecture docs if workspace tree counts changed.
4. Determine version bump from current tag or config.

---

## Phase 3: Multi-Surface Metadata Refresh (PARALLEL EXECUTION)

> **Parallelization**: Launch independent subagents for each surface group. They operate on different repositories with zero file overlap.
>
> **Dynamic metrics**: Every subagent reads counts from the config file — never hardcode.
>
> **Privacy**: Every subagent enforces Phase 0 blocklist on all writes.
>
> **API keys**: Discover from filesystem. Do NOT hardcode keys in prompts or commit messages.

### Subagent A: Public Repo Core, Releases & Wiki

- Update README, architecture docs, benchmarks, references with metrics from config and today's date.
- Add changelog entry (conditional on whether Phase 2 ran).
- Update releases (new or edit latest).
- Update wiki pages with current metrics.
- **Inline Privacy Gate** (before commit): run Phase 0 regex against staged diff. If any match → sanitize.
- Commit and push.

### Subagent B: Profile + Websites

For each additional public surface:
- Update metrics, Schema.org `dateModified`, sitemaps, README timestamps.
- **Build verification** for static site generators (e.g., `npm run build` must exit 0).
- **IndexNow**: Discover key from filesystem, POST to `api.indexnow.org`.
- `git pull --rebase` → commit → push.

---

## Phase 4: Triple Gate Verification (AFTER all subagents complete)

> Gates run on the FINAL state of each repo, after all commits and pushes.
> Subagents already ran inline privacy gates before their commits.

### Gate 1: Static Scanner
```bash
bash <public_repo>/scripts/pre_deploy_scan.sh <public_repo>
```
Must exit 0 (warnings OK, violations NOT OK). If violations → revert, fix, re-push.

### Gate 2: CI Verification
```bash
gh run list --repo <owner>/<public_repo> --limit 3
```
All workflows must show `completed / success`. If any failed → diagnose via `gh run view <id> --log-failed`, fix, re-push.

### Gate 3: Cross-Surface Consistency
```bash
TODAY=$(date +%Y-%m-%d)
for file in <key_files_across_all_surfaces>; do
  grep -q "$TODAY" "$file" && echo "✅ $file" || echo "❌ STALE: $file"
done
```

If all gates pass → output unified execution summary.

---

## Error Recovery

| Failure | Recovery |
|:---|:---|
| Phase 2 porting failure | Discard: `git checkout -- .` → skip to Phase 3 |
| Subagent push failure | `git pull --rebase` → retry push. If conflict, resolve minimally. |
| CI failure | `gh run view <id> --log-failed` → fix → `fix:` commit → re-push |
| Gate violation | Do NOT proceed to other surfaces. Fix failing surface first. |
| Unresolved failure | Log to context file under `@pending` for next interactive session |

---

## Tagging

# workflow #portfolio #public-repo #privacy #feature-port #law1 #daily-scheduled
