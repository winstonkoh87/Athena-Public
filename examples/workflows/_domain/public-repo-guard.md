---
description: Mandatory guard protocol when working on the Athena-Public repository
created: 2026-02-24
---

# Public Repo Guard — Mandatory Protocol

> **Scope**: This workflow applies whenever the AI agent performs ANY git operation inside `Athena-Public/`.
> **Severity**: Law #1 (Irreversible Ruin — reputational).

## Rules

### 1. Before `git add`

```bash
# Verify you are inside Athena-Public, NOT the parent Project Athena
pwd  # Must show .../Athena-Public
git remote -v  # Must show ONLY Athena-Public.git
```

// turbo

### 2. Before `git commit`

The pre-commit hook will auto-scan, but the agent MUST also:

- **Never stage `.env` files** — these contain API keys
- **Never stage files from the parent directory** — `../../.context/`, `../../.framework/`, etc.
- **Review `git diff --cached --stat`** — if >50 files, stop and confirm with user

### 3. Before `git push`

```bash
# MANDATORY: Verify remote target
git remote -v
# Must show: origin  https://github.com/winstonkoh87/Athena-Public.git
```

// turbo

The pre-push hook will auto-validate, but the agent MUST:

- **Never run `git push` to any remote other than `origin`** (which is `Athena-Public.git`)
- **Always run `git push --dry-run` first** if >20 files changed
- **Never use `--force` without explicit user permission**

### 4. After `git push`

- Confirm the push succeeded
- Report the GitHub URL to the user

## Prohibited Actions

| Action | Reason |
|--------|--------|
| `git remote add` pointing to `Athena.git` | Re-introduces the private remote landmine |
| `git push --no-verify` | Bypasses all safety hooks |
| `git push --force` without user permission | Can overwrite public history |
| Staging files from parent `Project Athena/` | Leaks private content |
| Committing `.env`, `.key`, `.pem` files | Exposes secrets |

## Tagging

# workflow #security #public-repo #law1
