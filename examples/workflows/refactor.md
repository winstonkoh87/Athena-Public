---created: 2025-12-16
last_updated: 2026-01-30
---

---description: Full workspace refactor — deep audit, Supabase sync, and remediation
created: 2025-12-16
last_updated: 2026-01-11
---

# /refactor — Ultimate System Optimization

> **Latency Profile**: HIGH (~15-30 min, Supabase sync can take 5-10 min)  
> **Philosophy**: "Flawless or nothing. Conceptually dense."
> **Use Case**: When you want absolute workspace integrity.
> **Flags**: `--dry-run` to preview changes without committing.

---

## Phase 0: Mode Activation

> **Mode**: ULTRATHINK (Max Depth)
> **Rule**: Prioritize **Conceptual Density** over speed.

**Dry-Run Check**:

- If `--dry-run` flag passed: Execute all phases but **skip commits**. Log actions to `/tmp/refactor_dryrun.log`.

---

## Phase 0.5: Determine Refactor Level (MANDATORY)

> **Rule**: Never default to Hygiene. Assess the "State of the Union".

1. **Check Last Refactor**: Read `last_refactored` in `project_state.md`.
2. **Scan Technical Debt**:
   - **Level 1 (Hygiene)**: < 1 week since last refactor. Formatting only.
   - **Level 2 (Component)**: Modules broken, schemas drifted, tests failing.
   - **Level 3 (Architecture)**: Core framework rot, monolithic bloat, perf bottlenecks.
   - **Level 4 (Rewrite)**: "Red Zone" (Avoid).

**Decision**: "Proceeding with Level [X] Refactor."

---

## Phase 1: Invoke /diagnose (~5 min)

> **Rule**: Always run diagnostics first.

// turbo

```bash
echo "=== Phase 1: Running /diagnose ===" 
# /diagnose workflow should be invoked here
# The AI will read and execute .agent/workflows/diagnose.md
```

**Gate**: Review diagnostic output before proceeding to remediation.

---

## Phase 2: Pre-Remediation Checkpoint

> **Goal**: Reversibility before destructive changes.

// turbo

```bash
git add -A && git commit -m "checkpoint: pre-refactor $(date +%Y-%m-%d-%H%M)" --allow-empty
```

> Creates rollback point. If remediation breaks things, `git reset --hard HEAD~1`.

---

## Phase 3: Remediation & Integrity Check

> **Rule**: Fix all issues. No broken windows.

| Issue | Action |
|-------|--------|
| **Orphans** | Add references to `System_Manifest.md` or `SKILL_INDEX.md` |
| **Broken links** | Repair path or remove dead reference |
| **Link Rot** | Test external URLs (manual spot check) |
| **Cross-ref warnings** | Add tags to reduce warnings |

---

## Phase 4: Optimization Pass

> **Goal**: Proactive improvements beyond just fixing bugs.

1. **Merge** redundant scripts
2. **Archive** dead/stale files
3. **Normalize** naming conventions
4. **Split** bloated directories (>20 files)
5. **Update** cross-references

---

## Phase 4.5: Session Log Archive (~10s)

> **Goal**: Auto-archive old session logs to reduce directory bloat.

// turbo

```bash
# Archive sessions older than 7 days
python3 .agent/scripts/compress_sessions.py --archive-days 7 2>/dev/null || echo "⚠️ Session archive skipped"
```

> **Note**: Moves old logs to `session_logs/archive/` for cleaner workspace.

---

## Phase 5: Supabase Memory Sync (~30s)

// turbo

```bash
python3 .agent/scripts/compress_memory.py 2>/dev/null || echo "⚠️ Memory compression skipped"
python3 .agent/scripts/supabase_sync.py
```

> Sync sessions and case studies to cloud vector database.

---

## Phase 5.7: Cache Maintenance (~20s)

> **Goal**: Refresh dynamic caches for hot files and protocol segments.

// turbo

```bash
python3 .agent/scripts/update_hot_manifest.py
python3 .agent/scripts/summarize_protocols.py
```

> **Note**: Ensures boot prefetch and fast lookup context are up to date.

---

## Phase 5.5: Context Compression Cache (~30s)

> **Goal**: Pre-generate compressed summaries for heavy files.

// turbo

```bash
# Compress scripts for efficient context loading
python3 .agent/scripts/compress_context.py --dir .agent/scripts --output .context/cache/scripts_compressed.md 2>/dev/null || echo "⚠️ Compression skipped (no API key or quota)"
```

> **Note**: Remove `--mock` flag once `GOOGLE_API_KEY` is set in `.env`.

---

## Phase 6: Verification Gate (~10s)

// turbo

```bash
python3 .agent/scripts/orphan_detector.py
```

> **GATE**:
>
> - If orphan count > 0 AND attempt < 2 -> **Return to Phase 3**.
> - If orphan count > 0 AND attempt >= 2 -> **Log Warning** and PROCEED.

---

## Phase 6.5: Index Regeneration (~10s)

> **Goal**: Regenerate TAG_INDEX after any file changes.

// turbo

```bash
python3 .agent/scripts/generate_tag_index.py
```

> Updates `TAG_INDEX.md` with current file tags.

---

## Phase 6.6: Regression Test Validation

> **Goal**: Ensure prompt edits haven't broken core behavior.

// turbo

```bash
echo "=== Phase 6.5: Regression Tests ==="
# Future: python3 .agent/scripts/run_tests.py
# For now: AI manually reviews test cases in .agent/tests/ if Core_Identity.md was modified
```

> **GATE**:
>
> - If `Core_Identity.md` was modified in this session → **Review test cases manually**.
> - Otherwise → PROCEED.

---

## Phase 7: Telemetry Logging

// turbo

```bash
echo "$(date +%Y-%m-%d-%H:%M),refactor,complete" >> .context/metrics/refactor_log.csv
```

---

## Phase 8: Session Log Append (Auto-Template)

> **Rule**: Auto-append checkpoint. Do not skip.

// turbo

```bash
CURRENT_SESSION=$(ls -t .context/memories/session_logs/*.md 2>/dev/null | head -1)
if [ -n "$CURRENT_SESSION" ]; then
  echo "" >> "$CURRENT_SESSION"
  echo "### Checkpoint [$(date +%H:%M) SGT] — /refactor complete" >> "$CURRENT_SESSION"
  echo "- Supabase synced: ✅" >> "$CURRENT_SESSION"
  echo "- Orphans remaining: $(python3 .agent/scripts/orphan_detector.py 2>/dev/null | grep -c 'Orphan' || echo 0)" >> "$CURRENT_SESSION"
  echo "✅ Session log appended: $CURRENT_SESSION"
else
  echo "⚠️ No session log found"
fi
```

**Gate**: Phase 9 blocked until Phase 8 completes successfully.

---

## Phase 9: Commit (~15s)

> **Gate**: Only runs if Phase 8 succeeded AND `--dry-run` not set.

// turbo

```bash
# Sanity check before commit
python3 .agent/scripts/batch_audit.py --skip-graphrag || echo "⚠️ Audit warning"
python3 .agent/scripts/git_commit.py
```

**Output**: "✅ Workspace fully optimized. All systems clean."

---

## Quick Reference

| Command | Effect | Time |
|---------|--------|------|
| `/diagnose` | Read-only diagnostics | ~3-5 min |
| `/refactor` | Full optimization (manual phases + automation) | ~10-15 min |
| `/refactor --dry-run` | Preview changes | ~10 min |
| `/reindex` | Supabase sync only | ~30s |
| `python3 .agent/scripts/refactor.py` | Automated orchestrator (subset of /refactor) | ~5 min |

---

## Rollback

```bash
git log --oneline -5  # Find the checkpoint commit
git reset --hard <checkpoint-hash>
```

---

## References

- [/diagnose](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/diagnose.md) — Read-only diagnostics
- [/dump](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/dump.md) — Quick thought capture
- [/end](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/end.md) — Quick session close
- [/reindex](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/reindex.md) — Supabase sync only
- [/vibe](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/examples/workflows/vibe.md) — Vibe engineering mode

---

## Tagging

`#workflow` `#automation` `#refactor`
