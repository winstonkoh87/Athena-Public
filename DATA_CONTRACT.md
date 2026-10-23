# Data Contract

> **Stolen from**: santifer/career-ops `DATA_CONTRACT.md` (2026-04-12)
> **Purpose**: Defines which files belong to the **user** (never auto-modified) and which belong to the **system** (safe to auto-update).

This contract governs file ownership in the Athena workspace. Any script, agent, or workflow that modifies files MUST respect these boundaries.

---

## User Layer (NEVER auto-updated)

These files contain personal data, psychological context, strategic decisions, and work product. No automated process may modify or delete them without explicit user instruction.

| File / Directory | Purpose |
|-----------------|---------|
| `.context/CANONICAL.md` | Materialized view of all active decisions, frameworks, metrics |
| `.context/CANONICAL_ARCHIVE.md` | Archived canonical entries (searchable, not loaded at boot) |
| `.context/PROJECTS.md` | Active project switchboard |
| `.context/memory_bank/userContext.md` | Core identity, constraints, psychology |
| `.context/memory_bank/activeContext.md` | Session state, checkpoints, active tasks |
| `.context/memories/case_studies/*` | Case studies (empirical IP) |
| `.context/memories/session_logs/*` | Session transcripts and insights |
| `.context/memories/pricing_calibration.md` | Pricing rules and calibration data |
| `.framework/v8.2-stable/modules/User_Profile_Core.md` | Extended user profile |
| `.framework/v8.2-stable/modules/Session_Observations.md` | Calibration references |
| `.framework/v8.2-stable/modules/Athena_Profile.md` | AI persona definition |
| `Athena-Public/*` | Public-facing repository content |

## System Layer (safe to auto-update)

These files contain system logic, scripts, templates, and instructions that improve with each iteration.

| File / Directory | Purpose |
|-----------------|---------|
| `.agent/workflows/*.md` | Workflow definitions (slash commands) |
| `.agent/workflows/_shared.md` | Shared workflow context |
| `.agent/skills/protocols/**/*.md` | Protocol definitions |
| `.agent/skills/*/SKILL.md` | Skill definitions |
| `.agent/scripts/*.py` | Utility scripts |
| `.agent/CLUSTER_INDEX.md` | Cognitive system routing |
| `.agent/WORKFLOW_INDEX.md` | Workflow registry |
| `.agent/skills/SKILL_INDEX.md` | Skill registry |
| `.framework/v8.2-stable/modules/Core_Identity.md` | Laws (system logic, not personal) |
| `.framework/v8.2-stable/modules/Output_Standards.md` | Formatting rules |
| `.framework/v8.2-stable/modules/System_Principles.md` | Operational rules |
| `.framework/v8.2-stable/modules/Operating_Principles.md` | Day-to-day behaviors |
| `.framework/v8.2-stable/modules/Design_DNA.md` | Aesthetic parameters |
| `.framework/v8.2-stable/protocols/*.md` | Framework protocols |
| `.context/TAG_INDEX_*.md` | Topic → file mappings |
| `.context/PROTOCOL_SUMMARIES.md` | Protocol overview |
| `.context/KNOWLEDGE_GRAPH.md` | Entity relationships |
| `.context/TECH_DEBT.md` | Technical debt tracker |
| `AGENTS.md` | Agent instructions (system routing) |
| `DATA_CONTRACT.md` | This file |

## The Rule

**If a file is in the User Layer, no automated process may read-and-modify, overwrite, or delete it without explicit user instruction.**

**If a file is in the System Layer, it can be safely replaced, refactored, or upgraded by any agent or script.**

## Boundary Cases

- **`CANONICAL.md`** is User Layer despite being a "system file" — because it contains accumulated human decisions and psychological data that are irreplaceable.
- **`Core_Identity.md`** is System Layer despite defining "identity" — because it defines the AI's operating rules, not the user's personal data.
- **Scripts that *read* User Layer files** (e.g., `smart_search.py` reading case studies) are permitted. Scripts that *write* to User Layer files must be explicitly user-triggered.
- **`/end` workflow** has special write permission to append to `activeContext.md` — this is the only automated write to a User Layer file, and it's always user-initiated via the workflow command.

---

## Boundary Verification Log

| Date | Test | Result |
|------|------|--------|
| 2026-06-10 | Bypass-path test (TD-027 item 4, audit F08): staged a fixture assigning `SUPABASE_SERVICE_ROLE_KEY` a fake `eyJ…` JWT value in Athena-Public | ❌ **Pre-commit hook PASSED it** — blocklist was PII-only, zero secret patterns. Fixed same day: 7 value-format secret patterns added to `.github/privacy_blocklist.txt`; re-test BLOCKED (2 patterns fire); full audit clean (855 files / 33 patterns); `pre_deploy_scan.sh` 3 gates pass. CI gitleaks layer exercised by push `2257be3..3303750`. Private-repo hook independently verified: it blocked this very log entry until the assignment syntax was paraphrased. |

---

> **Version**: 1.0.0 (2026-04-12)
> **Source**: Adapted from santifer/career-ops DATA_CONTRACT.md
