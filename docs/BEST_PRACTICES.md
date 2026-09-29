# Best Practices

> **Last Updated**: 22 July 2026

Operational discipline for running Athena sustainably. These aren't features — they're habits that prevent data loss, reduce friction, and keep your system compounding.

---

## 1. Back Up Your Data (The Non-Negotiable)

Your `.context/` folder **is** your brain. Losing it means losing every session, every protocol, every insight you've ever extracted. Treat it like source code — because it is.

### The 3-2-1 Rule

| Layer | What | Why |
|:------|:-----|:----|
| **Local** | Your machine (primary copy) | Speed — instant reads, no latency |
| **Git** (GitHub / GitLab) | Full repo push on every `/end` | **Portability** — clone anywhere, restore in seconds |
| **Cloud DB** (Supabase / ChromaDB) | Vector embeddings + semantic index | **Search** — hybrid RAG across your entire history |

> [!IMPORTANT]
> **At minimum, push to Git.** If your laptop dies tomorrow, `git clone` + `/start` gets you back to 100%. Everything else is acceleration.

### Backup Checklist

- [ ] **Git remote configured** — `git remote -v` shows your GitHub/GitLab URL
- [ ] **Auto-commit on `/end`** — The shutdown orchestrator commits and pushes automatically
- [ ] **`.gitignore` reviewed** — Ensure `.env`, API keys, and `.athenad.pid` are excluded
- [ ] **Cloud sync active** (optional) — Supabase or Google Cloud for embeddings

> [!TIP]
> **Why subscribe to AI Pro?** Beyond the higher rate limits, Pro plans often include priority access during peak hours and longer context windows. For Athena users running 4+ sessions/day, the consistency alone justifies the cost. Think of it as paying for *uptime*, not just *features*.

---

## 2. Session Discipline

### Always `/start` and `/end`

The most common mistake is working without bookends. Without `/start`, there's no session log. Without `/end`, nothing gets committed.

| ✅ Do | ❌ Don't |
|:-------|:---------|
| `/start` → Work → `/end` | Jump straight into asking questions without booting |
| `/save` mid-session for long threads | Rely on the AI to "remember" across sessions |
| One focused topic per session | Cram five unrelated tasks into one thread |

### The One-Feature Rule

Each session should target **one deliverable**. This isn't about being rigid — it's about context coherence. A session that covers authentication, UI design, *and* database schema produces a messy log that's hard to search later.

> **Guideline**: If you can't summarize the session in one sentence, it was probably two sessions.

---

## 3. Memory Hygiene

### Prune `activeContext.md` Regularly

`activeContext.md` is your **working memory** — not your archive. If it grows beyond ~100 lines, it's carrying stale context that wastes tokens on every boot.

| Signal | Action |
|:-------|:-------|
| Completed tasks still listed | Move to session log, mark `[x]`, or delete |
| "Recent Context" older than 1 week | Archive to session logs or compact |
| Duplicate entries | Merge or remove |

### Keep `userContext.md` Lean

Your user profile should contain **stable truths**, not session-specific details. If something changes every week, it belongs in `activeContext.md`, not `userContext.md`.

---

## 4. Git Workflow

### Commit Often, Push Always

| Practice | Rationale |
|:---------|:----------|
| Commit after every `/end` | Atomic, searchable history |
| Use semantic commit messages | `feat:`, `fix:`, `docs:` prefixes make `git log` useful |
| Push to remote same day | Local commits aren't backups — they're drafts |
| Tag major milestones | `git tag v9.2.5` lets you rollback cleanly |

### Branch Strategy (Advanced)

For users maintaining both private (full context) and public (sanitized) repos:

```
main        ← public-facing (Athena-Public)
private     ← full context (.context/, personal protocols)
```

> [!WARNING]
> **Never push `.context/memory_bank/` to a public repo.** It contains personal data (psychology, decisions, constraints). Use `.syncignore` or `.gitignore` to exclude sensitive directories.

---

## 5. Token Budget Awareness

Athena boots at ~10K tokens, leaving ~190K for your session. But token waste adds up:

| Waste Source | Fix |
|:-------------|:----|
| Oversized `activeContext.md` | Prune weekly (see §3) |
| Loading files you don't need | Trust JIT routing — don't `/fullload` unless you need it |
| Repeating context the AI already has | Reference session logs instead of re-explaining |
| Pasting entire files into chat | Point to the file path — let the agent read it |

---

## 6. Multi-Account / Multi-Model Strategy

If you use multiple AI accounts or models:

| Practice | Why |
|:---------|:----|
| **Designate a "primary" for Athena sessions** | Consistency in session logs and memory |
| **Use secondary accounts for research** | Keeps your primary context clean |
| **Run Trilateral Feedback for big decisions** | Cross-validate across Claude, Gemini, GPT |
| **Always return to primary for `/end`** | Ensures the canonical session log is written |

> The Memory Bank means your context is **decoupled from the provider**. Switch models freely — the state lives in your filesystem, not their servers.

---

## 7. Security Basics

| Practice | Details |
|:---------|:--------|
| **Never commit `.env` files** | Use `.env.example` as a template, `.gitignore` the real one |
| **Rotate API keys periodically** | Especially after sharing screens or running demos |
| **Use Secret Mode for demos** | `set_secret_mode(True)` redacts sensitive data |
| **Review agent permissions** | Don't grant filesystem access to `~/.ssh` or credential stores |

> 👉 Full security model: [SECURITY.md](SECURITY.md)

---

## 8. When Things Go Wrong

| Problem | Recovery |
|:--------|:---------|
| **Lost local data** | `git clone` your repo → `/start` → back in business |
| **Corrupted session log** | Check `git log` for the last clean commit → `git checkout` |
| **Boot fails** | Run `python -m athena doctor` to diagnose |
| **Context feels "off"** | Review `activeContext.md` for stale/incorrect entries |
| **Model quality drops mid-session** | You've likely hit ~150K tokens. Run `/save` and start fresh |

---

## Quick Reference

```
✅ Git push after every session
✅ One feature per session
✅ Prune activeContext.md weekly
✅ Keep userContext.md stable
✅ Use /save for long sessions
✅ Review .gitignore before first push
❌ Don't skip /start and /end
❌ Don't push .env or personal memory to public repos
❌ Don't /fullload unless you need deep context
❌ Don't paste entire files — point to paths
```

---

## See Also

- **[Tips](TIPS.md)** — Getting the most out of Athena
- **[Security](SECURITY.md)** — Data residency and permissions
- **[FAQ](FAQ.md)** — Common questions
- **[Your First Session](YOUR_FIRST_SESSION.md)** — Guided walkthrough

---

<div align="center">

**[Back to README](../README.md)**

</div>
