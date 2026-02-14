---created: 2025-12-18
last_updated: 2026-01-30
---

---description: Read-only workspace diagnostics — safe to run frequently
created: 2025-12-18
last_updated: 2025-12-26
---

# /diagnose — Workspace Diagnostics

> **Latency Profile**: MEDIUM (~3-5 min)
> **Philosophy**: "See everything. Touch nothing."
> **Use Case**: Quick health check without commits.

---

## Phase 0: Dependency Check (~5s)

// turbo

```bash
python3 -c "from supabase import create_client; print('✅ Supabase SDK OK')" 2>/dev/null || echo '⚠️ Missing supabase - run: pip install supabase'
```

> **Gate**: If dependencies missing, warn but continue.

---

## Phase 1-3: Parallel Diagnostics (~60s)

> **Goal**: Run all read-only scans. Use orchestrator for fastest execution.

// turbo

```bash
python3 .agent/scripts/diagnose.py
```

**What it runs**:

1. Dependency check (supabase, dotenv)
2. Batch audit (orphans, links)
3. Structure map
4. Echo chamber check

**Analysis** (from logs):

- **Orphans**: `/tmp/diag_batch.log`
- **Structure**: `/tmp/diag_structure.log`
- **Secrets**: `/tmp/diag_secrets.log`
- **Protocol Usage**: `/tmp/diag_protocols.log`

---

## Phase 4: Echo Chamber Check (~10s)

> **Goal**: Detect if AI is just agreeing with everything.

// turbo

```bash
DISAGREE_COUNT=$(grep -rciE "actually|incorrect|disagree|not quite|I'd push back" .context/memories/session_logs/*.md 2>/dev/null | tail -10 | awk -F: '{s+=$2} END {print s+0}')
echo "🔍 Disagreement signals in last 10 sessions: $DISAGREE_COUNT"
if [ "$DISAGREE_COUNT" -lt 3 ]; then
  echo "⚠️ ECHO CHAMBER RISK: <3 disagreements detected. Challenge more."
else
  echo "✅ Healthy dialectic: $DISAGREE_COUNT disagreement signals."
fi
```

---

## Phase 5: Fragility Audit (~2 min)

> **Goal**: Identify single points of failure.
> **Mode**: `// manual`

**Checklist**:

1. **Script Dependencies**: Which scripts break the workflow if they fail?
2. **File Dependencies**: Which files, if deleted, cause cascading failures?
3. **Knowledge Concentration**: Is critical knowledge in only ONE file?
4. **External Dependencies**: Which workflows require external APIs?

---

## Phase 6: Deep Validity Audit (Capped: 15 min)

> **Goal**: Verify key claims. No hallucinations.
> **Mode**: `// manual` — **TIME CAPPED**

1. **Extract** Max 3 claims from recent sessions.
2. **Verify** via `/search` (Max 5 mins per claim).
3. If inaccurate → **DEBUNK & CORRECT**.

---

## Output Summary

> **Rule**: No commits. Report only.

**Confirm**: "✅ /diagnose complete. [X] issues found. [Y] require remediation."

---

## Quick Reference

| Command | Effect | Time |
|---------|--------|------|
| `/diagnose` | Read-only diagnostics | ~3-5 min |
| `/refactor` | Full optimization (calls /diagnose first) | ~10-15 min |
| `/audit` | Cross-model validation | ~5 min |

---

## Tagging

`#workflow` `#automation` `#diagnostics`
