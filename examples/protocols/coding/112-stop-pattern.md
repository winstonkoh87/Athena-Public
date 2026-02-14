# Protocol 112: The Stop Pattern

> **Created**: 2026-02-15 (Derived from Claude Code Mastery V5)
> **Type**: Safety / Constraint
> **Tags**: #safety #constraints #behavior #coding

## 1. Core Principle

**"Negative constraints are stronger than positive instructions."**

AI models drift. They hallucinate convenience. They take shortcuts. The only way to prevent this is not to say "Do X," but to say "**If you are about to do Y... STOP.**"

## 2. The Stop Triggers (Universal)

These triggers apply to ALL coding tasks.

### 🛑 Architecture & Scope

* **If you are about to** add a new public method... **STOP**. Check `System_Manifest.md` first.
* **If you are about to** create a new top-level directory... **STOP**. Verify against `structure_map.py`.
* **If you are about to** modify a file >300 lines... **STOP**. Propose a split/refactor first.

### 🛑 Security & Data

* **If you are about to** hardcode a credential (even for testing)... **STOP**. Use `.env`.
* **If you are about to** commit a `.env` file... **STOP**. Check `.gitignore`.
* **If you are about to** bypass a lint error with `// @ts-ignore` or `# type: ignore`... **STOP**. Fix the type.

### 🛑 Deployment & Ops

* **If you are about to** run a destructive command (`rm -rf`, `DROP TABLE`)... **STOP**. Ask for explicit confirmation.
* **If you are about to** deploy to production... **STOP**. Run the full test suite first.

## 3. Implementation in Plans

Every `implementation_plan.md` MUST now include a "Stop: High-Stakes Constraints" section if the task involves significant complexity or risk.

```markdown
## Stop: High-Stakes Constraints
- [ ] If changing auth logic -> STOP and verify session persistence.
- [ ] If deleting database columns -> STOP and check for backup.
```

## 4. The "Check Before Assuming" Pattern

Before writing a fix, verify the failure mode.

* **Missing UI element?** → Check feature flag BEFORE assuming bug.
* **Empty data?** → Check DB connection BEFORE assuming broken query.
* **404 error?** → Check route registration BEFORE adding endpoint.
* **Test failing?** → Read the FULL error message BEFORE changing code.

## 5. Enforcement

**Self-Correction**: If you catch yourself violating a STOP trigger, acknowledge it ("I was about to X, but Protocol 112 prevents it") and correct course immediately.
