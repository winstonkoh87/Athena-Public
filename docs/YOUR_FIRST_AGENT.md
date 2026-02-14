# Your First Agent

> **Goal**: Build your own AI agent in 5 minutes.

---

## Prerequisites

- [Google Antigravity](https://antigravity.google/) installed (or any terminal/IDE)
- A curious mind

---

## Step 1: Clone the Repo

In Antigravity, open Agent Manager and paste:

```
https://github.com/winstonkoh87/Athena-Public
```

Or via terminal:

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git
cd Athena-Public
pip install -e .
```

---

## Step 2: Ask the AI

Once cloned, simply ask the AI in the chat:

> "What should I do next?"

The AI will read the repo structure and guide you through setup. This is the **self-bootstrapping** feature — the AI teaches itself.

---

## Step 3: Boot Your Agent

Type `/start` in the chat.

This triggers the boot sequence:

1. Loads your Core Identity
2. Retrieves relevant context from memory
3. Initializes the session

Your agent is now awake.

---

## Step 4: Work Together

Do whatever you need — coding, writing, research, planning.

The AI remembers the context of your conversation. Every decision, every insight, every question.

---

## Step 5: Save Your Session

When you're done, type `/end`.

This:

1. Summarizes the session
2. Extracts key decisions
3. Saves to your knowledge store

**Your agent now remembers this session forever.**

---

## Step 6: Customize Your Agent

The real power comes from making it yours.

### Edit Your Core Identity

Open `.framework/v8.6-stable/modules/Core_Identity.md` and customize:

- Your name
- Your values
- Your operating principles

### Add Your Own Protocols

Create decision frameworks in `examples/protocols/`:

- Trading rules
- Writing workflows
- Research patterns

### Train Your Memory

Every session adds to your agent's knowledge. The more you work together, the smarter it gets.

---

## What's Next?

| Level | Goal |
|-------|------|
| **Beginner** | Run 10 sessions with `/start` and `/end` |
| **Intermediate** | Customize your Core Identity |
| **Advanced** | Add your own protocols and workflows |
| **Expert** | Deploy a Gateway for autonomous operations |

---

## Troubleshooting

**Issue**: AI doesn't know what to do

- Make sure you cloned the full repo
- Try asking: "Read the README and tell me the quickstart steps"

**Issue**: `/start` doesn't work

- Ensure the Python SDK is installed: `pip install -e .`
- Check `.agent/workflows/start.md` exists

**Issue**: Session memory not persisting

- Verify Supabase is configured (or use local mode)
- Check `.env` file has correct keys

---

## Get Help

- [GitHub Issues](https://github.com/winstonkoh87/Athena-Public/issues)
- [Discussions](https://github.com/winstonkoh87/Athena-Public/discussions)

---

*Now go build something amazing with your new agent.* 🦞

---

## See Also

- **[What Is an AI Agent?](./WHAT_IS_AN_AI_AGENT.md)** — Understand the basics
- **[Glossary](./GLOSSARY.md)** — Key terms and definitions
- **[Getting Started](./GETTING_STARTED.md)** — Detailed setup guide

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](./ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
