---

created: 2026-01-11
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-11
last_updated: 2026-01-11
---

# Protocol: Development Execution Standard

> **Purpose**: Unified discipline for high-integrity, anti-fragile code production.
> **Triggers**: Any coding or app building task.

---

## 1. Shipping Discipline

### 1.1 Micro-Commit Protocol (Development Execution Standard)

- **Principle**: Feature A → ✅ Commit → Feature B → ✅ Commit.
- **Rules**: One feature per session. No feature stacking. Commit after each working unit.
- **Gate**: AI asks "Is current feature committed?" before proposing next.

### 1.2 The Silent Validator (Development Execution Standard)

- **Mechanism**: Run background lint/test/build after every file edit WITHOUT being asked.
- **Feedback**: Only report failures. "Lints/Tests passed" is silent.

---

## 2. Verification & Safety

### 2.1 The TDD & Spec Mandate (Development Execution Standard / 307)

- **Rule**: Write the acceptance test/spec BEFORE the implementation.
- **Constraint**: No PR/Code Output without a corresponding verification plan.

### 2.2 Visual & State Verification (Development Execution Standard / 99)

- **Visual**: Use browser tools to verify UI against mockups. Screenshot comparison.
- **State**: Use "State Freezer" (checkpointing) before high-risk database/file mutations.

### 2.3 Git Worktree Parallelism (Development Execution Standard)

- **Strategy**: Keep main branch clean. Run experiments in disposable worktrees.
- **Handover**: Only merge back when Vibe Audit passes.

---
# engineering #development #TDD #git #verification #discipline
