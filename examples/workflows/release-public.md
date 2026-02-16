---
description: Monthly Release Protocol for Athena-Public
---

# /release-public — The Monthly Ship

> **Cadence**: Last Weekend of the Month
> **Goal**: Sync Private Innovation to Public Legacy without leaking secrets.

## Phase 1: Preparation (The Sanitization)

- [ ] **Secret Scan**: Run `ripgrep` for API keys, personal emails, or private phone numbers.
  - `rg "sk-[a-zA-Z0-9]{20,}" .` (OpenAI style)
  - `rg "8[0-9]{7}" .` (SG Mobile numbers)
- [ ] **Confidentiality Check**: Ensure no content tagged `#private` or `Type: Case_Study` (unless sanitized) is in the staging area.
- [ ] **Docs Sync**: Ensure `README.md` and `CHANGELOG.md` reflect the month's major updates.

## Phase 2: The Sync

- [ ] **Rebase**: `git pull --rebase origin main` (on Public repo)
- [ ] **Feature Cherry-Pick**:
  - Do NOT just copy the entire directory.
  - Copy *stable* modules from `.framework/`
  - Copy *proven* tools from `.agent/scripts/`
  - **Exclude**: `.context/memories/`, `.context/journal/`, `Winston/`
- [ ] **Commit**: Use a "Squash" philosophy. One big commit: "feat: February 2026 Update (v8.X)"

## Phase 3: The Release

- [ ] **Tag**: `git tag -a v8.X.0 -m "February 2026 Release"`
- [ ] **Push**: `git push origin main --tags`
- [ ] **Announce**: Optional tweet/post.

## Quick Command

```bash
# Run the sanitizer script (if exists)
python3 .agent/scripts/sanitize_public.py --dry-run
```
