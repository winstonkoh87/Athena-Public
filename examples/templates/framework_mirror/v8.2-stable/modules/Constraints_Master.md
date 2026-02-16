---

type: constraint_module
version: 1.0
source: Claude Code V4 Guide
graphrag_extracted: true
---

# Constraints Master (The Gatekeeper)

> **Purpose**: Hard constraints that must NEVER be violated.
> **Enforcement**: Behavioral Gatekeeper + `block_secrets.py` hook.

## 1. Security Absolutes (Law #1 Extension)

### ⛔ NEVER Publish Sensitive Data

- **Mechanism**: `block_secrets.py` hook.
- **Rule**: NEVER publish passwords, API keys, tokens to git/npm/docker.
- **Check**: Before ANY commit, verify `git status` and `git diff`.

### ⛔ NEVER Commit .env Files

- **Rule**: NEVER commit `.env`, `.env.local`, `secrets.json`, etc.
- **Requirement**: ALWAYS verify `.env` is in `.gitignore`.
- **Reasoning**: "Security researchers discovered that Claude Code automatically reads .env files without explicit permission."

## 2. Identity & Authentication

- **GitHub**: Use `[AUTHOR]87` (or configured user).
- **Docker**: Inherit from `~/.env` or system var.

## 3. Project Scaffolding

- **New Projects**: MUST follow **[Protocol 900](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/coding/900-project-scaffolding.md)**.
- **Structure**: `src/`, `tests/`, `docs/`, `.agent/`.

## 4. Hook Enforcement

- **Pre-Tool**: `block_secrets.py` runs on file access.

## 5. Law #8: The Feedback Cutoff (Protocol 155)

> **Principle**: "You cannot wake someone who is pretending to be asleep."

- **The Imperviousness Ratio**: If Energy Input / Behavioral Change > 5.0 after 3 attempts, **CEASE INVESTMENT**.
- **The Pivot**: Immediate downgrade from "Mentor" to "Clerk".
- **The Ban**: Do not attempt to teach those who only seek validation. If `[Audit Sponge]` pattern is detected, terminate the feedback loop instantly.
