---
graphrag_extracted: true
---

# DEAD MAN SWITCH — Athena System Health Canary

> **Purpose**: If this file's audit date becomes stale (>90 days), Athena is clinically dead.
> **Location**: Repository root (always visible)

---

## Current Status

| Metric | Value |
|--------|-------|
| **Last Full Robustness Audit** | 2025-12-29 |
| **Next Canary Check** | 2026-03-29 |
| **Status** | ACTIVE |
| **Role** | Archival Trigger (Legacy Transition) |
| **System Health** | 🟢 OPERATIONAL |

---

## Audit Checklist (Run Every 90 Days)

- [ ] Boot layer: `python3 boot.py --verify` passes
- [ ] Sync layer: `python3 supabase_sync.py --dry-run` shows no errors
- [ ] Semantic prime: Hash matches Core_Identity.md header
- [ ] Protocols: SKILL_INDEX.md matches protocol count
- [ ] Scripts: `python3 diagnose.py --quick` reports no critical issues
- [ ] Offline test: Disconnect network, verify graceful degradation

---

## Quick Runbook (When Signals Trip)

| Signal | Action |
|--------|--------|
| **Boot timeout (90s)** | Run `./safe_boot.sh`, inspect `.athena/crash_reports/<latest>` |
| **Hash mismatch** | STOP. Diff Core_Identity.md. Re-attest only via `update_prime_hash.py --apply` |
| **DEGRADED_MODE active** | Expect grep-only retrieval. Queue writes until Supabase recovers. |
| **Sync lock persists** | Check `.athena/sync.lock` owner + TTL. Clear only if stale (>1hr, no heartbeat). |
| **Audit overdue** | Run `/refactor`. Update this file's dates. Document remediation. |

## Emergency Recovery Procedure

If the "Next Required Audit" date is more than 90 days in the past, assume catastrophic identity drift has occurred.

### Recovery Steps

1. **Preserve State**

   ```bash
   cp -r .context/memories/ ~/athena_backup_$(date +%Y%m%d)/
   cp -r .agent/scripts/ ~/athena_backup_$(date +%Y%m%d)/
   ```

2. **Load Minimal Context**

   ```bash
   ./safe_boot.sh  # Zero-dependency fallback
   ```

3. **Rebuild from First Principles**
   - Load only: `Core_Identity.md`, `project_state.md`, last 3 session logs
   - Re-run: `python3 .agent/scripts/refactor.py`
   - Verify: `python3 .agent/scripts/diagnose.py`

4. **Update This File**
   - Set new audit date
   - Document what was lost and recovered

---

## Reliability Contract

1. **No Silent Failure**: Every failure produces a human-readable message AND a machine-readable artifact.
2. **Recoverability**: Any failed operation has a documented recovery path that does not require network.
3. **Deterministic Degraded Mode**: Offline or outage triggers a consistent, known capability set.

---

## The Rev-9 Constraint

> "When I fail, you fail."

Athena is an extension of Winston. A fragile Athena is a fragile Winston. This file exists to ensure that fragility is detected before it becomes catastrophic.

**Robustness is identity. Everything else is temporary.**

---

# canary #robustness #audit #emergency
