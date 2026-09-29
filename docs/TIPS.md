# Tips for Getting the Most Out of Athena

## 🎯 Find One Signature Project and Go Deep

The best way to learn Athena (and agentic coding in general) is to **work on a project you actually care about**. Pick one — a portfolio site, a side project, a tool you wish existed — and build it entirely through Athena.

The more you use Athena on a real project, the more you learn about coding, software architecture, and how to work effectively with AI. Tutorials teach theory. Building teaches everything else.

**My approach:** I built a portfolio website showcasing everything I produced with Project Athena, and I keep iterating on it. Every session improves both the project *and* my skills. Find your equivalent and commit to it.

> 👉 Need inspiration? See [PROJECT_IDEAS.md](PROJECT_IDEAS.md) — 9 starter projects from web apps to YouTube channels, each mapped to the Athena capabilities you'll learn.

## 🧩 One Session = One Feature

Athena works best with focused sessions. If your project has ten features, work on them across ten separate sessions — not all at once.

| Session | Focus |
|:--------|:------|
| Session 1 | Authentication system |
| Session 2 | Dashboard UI |
| Session 3 | API integration |
| Session 4 | Search functionality |

Each session gets its own log, its own context, and its own clean thread of reasoning. This creates better memory, cleaner recall, and fewer context collisions in future sessions.

**Bonus:** Each session starts with a fresh ~190K token workspace. One focused feature will typically use 30–80K tokens — well within the budget and well below the point where model quality degrades.

## ☁️ Sync to the Cloud — GitHub + Supabase

Athena syncs to **two layers** — and you control both:

| Layer | What It Syncs | Why |
|:------|:-------------|:----|
| **GitHub** (Cold Storage) | Markdown files — session logs, protocols, memory bank, user profile | **Portability.** Switch laptops, IDEs, or AI models. Clone → `/start` → you're back. |
| **Supabase** (Hot Storage) | Vector embeddings — semantic search index (pgvector) | **Speed.** Hybrid RAG search across your entire history in milliseconds. |

When you run `/end`, Athena can automatically commit and push to GitHub. If you've configured Supabase, embeddings sync via delta updates — only new/changed files get re-embedded.

**You don't need both.** GitHub alone gives you full backup and portability. Supabase adds semantic search superpowers on top. Start with GitHub; add Supabase when you want smarter recall.

> [!TIP]
> If you ever lose your laptop, your entire brain is recoverable: clone from GitHub, reconnect to Supabase, and `/start`. Zero data loss.

## 🏗️ Project Placement

Athena is your **Brain**. Your project is the **Body**. They don't need to live in the same place.

| Mode | Setup | Best For |
|:-----|:------|:---------|
| **Standalone** | Open `Athena/` as your workspace. Navigate to other repos from there. | Personal brain, all-in-one users |
| **Multi-Root (Sidecar)** | Open your project normally → `File → Add Folder to Workspace` → select `Athena/` | Devs with existing repos who want both in one window |
| **Nested** | Drop your project folder inside `Athena/` | Quick prototypes, small projects |

```
# Standalone (recommended)           # Multi-Root (Sidecar)
~/Athena/          ← open this        IDE Workspace:
  .context/                             ├── ~/MyApp/        ← your code
  .agent/                               └── ~/Athena/       ← the brain
  .framework/

# Nested
~/Athena/
  .context/
  .agent/
  MyApp/            ← project inside
```

**Recommendation**: Start with **Standalone**. If you need your project visible in the same window, use **Multi-Root**. All three modes work — pick what feels natural.

## 🤝 Client Data Isolation

Keep Athena as **your personal brain**. Create client folders **outside** the workspace.

```
~/Desktop/
├── Project Athena/       ← YOUR brain (personal context, memory, protocols)
├── Client-A/             ← Client A's project (isolated)
├── Client-B/             ← Client B's project (isolated)
└── Client-C/             ← Client C's project (isolated)
```

**Why?** Your memory bank contains *your* psychology, decision frameworks, and personal history. Client work is temporary and shouldn't pollute that context.

**How it works in practice:**

1. When working on a client project, point Athena to the external folder (e.g., "look at `~/Desktop/Client-A/`")
2. Athena reads the client files while retaining your personal context — best of both worlds
3. When the engagement ends, archive the learnings back into Athena (strip client-specific data) and archive or delete the external folder

**The rule:** Athena keeps the *wisdom*. The client keeps the *execution*.
