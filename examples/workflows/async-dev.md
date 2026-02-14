---created: 2026-01-03
last_updated: 2026-01-30
---

---description: Async AI Development Workflow (The Sleeper Agent Protocol)
created: 2026-01-03
last_updated: 2026-01-03
---

# /async-dev — Async AI Development

> **Latency Profile**: LOW (Planning) -> HIGH (Execution)
> **Philosophy**: Plan by day, build by night.

## 1. Overview

This workflow operationalizes the "Sleeper Agent" model (Case Study 237). It decouples **Design/Review** (Human) from **Execution** (AI), allowing for unsupervised "deep work" runs.

## 2. Command Chain

### Phase 1: Wake Up & Scaffold (Human)

Start a new feature branch with isolated state.

```bash
# Creates .context/features/{feature-name}/STATUS.md
python3 .agent/scripts/scaffold_feature.py "feature-name" "Description"
```

### Phase 2: Research & Plan (Human + AI)

Run this block to generate the plan.
**Tag**: `#planning`

1. **Context**: `python3 .agent/scripts/supabase_search.py "keywords"`
2. **Research**: Create `CODE_RESEARCH.md` in the feature directory.
3. **Plan**: Create `IMPLEMENTATION_PLAN.md`.

### Phase 3: The Sleeper Run (AI Unsupervised)

**Trigger**: When the plan is solid, tag the prompt with `#async` or `#sleeper`.
**Condition**: `SafeToAutoRun: true` allowed for execution steps.

**The Loop**:

1. Read `IMPLEMENTATION_PLAN.md`.
2. Execute step.
3. Run tests.
4. Update `STATUS.md`.
5. Repeat.

### Phase 4: Morning Review (Human)

1. Read `STATUS.md`.
2. Review code changes.
3. Run `python3 .agent/scripts/verify_feature.py` (Future).

## 3. Artifacts

* `STATUS.md`: The brain of the feature. Single Source of Truth.
* `CODE_RESEARCH.md`: The "Why" and "How".
* `IMPLEMENTATION_PLAN.md`: The "What" and "When".

## 4. Example Usage

```text
User: /async-dev "refactor-auth-layer"
AI: Scaffolding feature... Done.
User: Research Auth0 vs Supabase Auth for this.
AI: (Generates CODE_RESEARCH.md)
User: Looks good. Plan it.
AI: (Generates IMPLEMENTATION_PLAN.md)
User: #sleeper Execute the plan.
AI: (Runs overnight)
```
