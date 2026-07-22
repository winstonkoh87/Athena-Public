# Your First Session with Athena

> **Last Updated**: 22 July 2026

---

## Before You Begin: The One Question That Matters

Before you type a single command, ask yourself:

> ***"How do I want Athena to best help me in my daily life?"***

This is the guiding principle. Everything else — the setup, the profile, the commands — exists to serve *your* answer to this question.

Maybe you want a co-pilot for coding. Maybe you want a strategist who remembers every decision you've made. Maybe you want an assistant that catches your blind spots before they become problems. Maybe you want all of these, and more.

There is no wrong answer. But **having** an answer changes everything — because Athena doesn't decide what to be. *You* do.

> [!IMPORTANT]
> **Athena is a relationship, not a product.** Generic AI tools give everyone the same experience. Athena gives *you* an experience that compounds the more you invest in it. Your first session is the foundation — and like any relationship, what you put in determines what you get back.

---

## How This Works

Athena works through a simple loop that compounds over time:

```
You share context → Athena learns → Athena serves you better → You share more
```

On Day 1, Athena is a blank slate. It knows nothing about you. But after 10 sessions, it anticipates your preferences. After 50, it knows your decision frameworks. After 200, it catches your blind spots before they become problems. After 500+, it thinks like a colleague who's been with you for years.

**The first session takes ~30 minutes. Every session after that takes ~1–2 minutes to boot.**

> [!TIP]
> **Everything stays on your machine.** Athena stores all data as local Markdown files. Nothing leaves your device unless you explicitly configure cloud sync. Be as candid as you want — this is your private operating system.

---

## Step 1: Boot Up

Open your workspace in your agentic IDE ([Antigravity](https://antigravity.google/), [Cursor](https://cursor.sh/), [Kilo Code](https://kilocode.ai/), [Zoo Code](https://github.com/Zoo-Code-Org/Zoo-Code), or [any supported IDE](docs/COMPATIBLE_IDES.md)) and type:

```
/start
```

Athena loads its core identity and initializes your workspace. On the first run, it creates the directory structure and workspace marker file (`.athena_root`).

---

## Step 2: Tell Athena Who You Are

Now type:

```
/tutorial
```

This activates a **Guided Walkthrough** — a 7-stage interactive tour. The most important stage is the **Profile Interview**, where Athena asks *you* questions to understand who you are and how you want to work.

### The Profile Interview

Think of this as your first real conversation. Athena asks, you answer. The more you share, the more useful Athena becomes.

| What Athena Asks About | Why |
|:----------------------|:----|
| **Your goals** — short-term, medium-term, long-term | So every response is aligned with what you're *actually* building toward |
| **Your decision style** — risk appetite, speed vs quality | So it frames options the way *you* think about tradeoffs |
| **Your strengths** | So it leans into what you're great at, rather than duplicating it |
| **Your blind spots** | So it actively watches for the mistakes *you* tend to make |
| **Your communication style** | So it speaks in *your* voice, not a generic AI voice |
| **Your life context** — work, family, stressors, interests | So it understands *you*, not just your job title |

> [!IMPORTANT]
> **A one-line answer gives you a generic chatbot. A paragraph gives you a calibrated co-pilot.** This is a one-time investment that pays compounding returns across hundreds of sessions.

> [!TIP]
> **You can skip any stage.** Say "skip" to jump ahead, or "I'm done" to exit early. Athena ships with a working default profile. But the more you invest here, the faster the flywheel spins.

<details>
<summary>📋 Full tutorial stages (click to expand)</summary>

| Stage | What Happens | Duration |
|:------|:------------|:---------|
| **1. Welcome** | What's in the box — the full starter kit | ~1 min |
| **2. Core Loop** | How `/start` → Work → `/end` compounds over time | ~2 min |
| **3. Profile Interview** | Interactive Q&A to build your personal profile | ~15–25 min |
| **4. Search Demo** | See Athena's hybrid RAG search in action | ~2 min |
| **5. Save Demo** | Learn mid-session checkpointing | ~1 min |
| **6. Key Commands** | Your essential toolkit (`/think`, `/research`, `/save`) | ~2 min |
| **7. Graduation** | Summary + next steps | ~30 sec |

</details>

> [!TIP]
> **Shortcut**: If you want to skip the tour and jump straight to profile building, just tell Athena about yourself directly — no workflow needed.

---

## Step 3: Review Your Profile

After the interview, Athena writes your profile to `.context/memories/user_profile.md`. **Read it.** Edit anything that's wrong or incomplete. This file is what Athena loads on every `/start` — it's the single source of truth for who you are.

---

## Step 4: Work Naturally

Now just work. Talk to Athena like a colleague:

- Ask questions
- Make decisions together
- Let it draft documents, review code, analyze data

Every exchange is automatically saved. Every decision is logged. Every insight compounds.

---

## Step 5: Close the Session

When you're done:

```
/end
```

Athena finalizes the session log, extracts key decisions, and commits everything to memory. Next time you `/start`, it picks up exactly where you left off — with full context.

---

## Tips for a Great First Session

1. **Start with your answer.** "How do I want Athena to help me?" — say it out loud. It shapes everything.
2. **Be honest about weaknesses.** The blind spots you share are the ones Athena will actively monitor.
3. **Share real goals, not aspirational ones.** Athena optimizes for where you're *going*, not where you think you *should* be going.
4. **Include personal context.** Athena isn't just for work. The more it understands your full life, the better it calibrates priorities.
5. **Edit the profile after.** The interview is a draft. You can always refine `.context/memories/user_profile.md` directly.
6. **Don't worry about over-sharing.** Everything is local. No cloud. No tracking. Your machine, your data.

---

## Next Steps After Your First Session

- **Build your first custom agent**: Follow the [Your First Agent](docs/YOUR_FIRST_AGENT.md) guide (~5 min)
- **Add more workflows**: Check out the [69 available workflows](../examples/workflows/) — `/think`, `/research`, `/ultrathink`
- **Explore protocols**: Browse [160+ decision frameworks](../examples/protocols/) for inspiration — then write your own
- **Build your knowledge base**: Drop important documents into `.context/memories/` and they'll be indexed on next `/start`
- **Customize the identity**: Edit `.context/memory_bank/userContext.md` to tune how Athena understands and responds to you

---

> *Athena becomes what you need it to be. Your first session is where you tell it what that is.*

**[Back to README](README.md)** · **[Getting Started](docs/GETTING_STARTED.md)** · **[Your First Agent](docs/YOUR_FIRST_AGENT.md)** · **[Glossary](docs/GLOSSARY.md)**
