# Zero-Code 3-File Starter (ChatGPT / Claude / Gemini Web)

If you just want portable cross-chat memory without cloning a repo, installing Python, or running an IDE CLI, copy these three Markdown files into a folder on your desktop:

1. **`active_context.md`** — Current project focus, in-flight tasks, and recent session state (rewrite often).
2. **`rules.md`** — Stable constraints, formatting rules, and communication preferences (rarely changes).
3. **`decisions.md`** — Architectural decisions and rejected dead ends you do not want to re-litigate.

## How to Use

1. **Start of a chat**: Drag or paste `active_context.md` and `rules.md` (and `decisions.md` when starting a non-trivial design) into a fresh ChatGPT, Claude, or Gemini session.
2. **Work normally**: The model uses your disk files as memory instead of platform lock-in memory.
3. **End of a chat**: Ask the model:
   > "Summarize only the new decisions, open tasks, and dead ends we hit in at most 10 bullets so I can update `active_context.md` and `decisions.md`."
4. **Overwrite `active_context.md`** (and append durable calls to `decisions.md`).

When you outgrow manual drag-and-drop, install the SDK and run `athena init --profile minimal` or `athena init --ide claude`.
