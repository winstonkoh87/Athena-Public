# Compatible IDEs

> **Last Updated**: 22 July 2026

Athena works with **any agent that reads Markdown**. For agents that support project-level config, `athena init` generates the native configuration file automatically.

## First-Class Integrations

| Agent | Config File Generated | Init Command |
|:------|:---------------------|:-------------|
| [Antigravity](https://antigravity.google/) | `AGENTS.md` | `athena init --ide antigravity` |
| [Cursor](https://cursor.com) | `.cursor/rules.md` | `athena init --ide cursor` |
| [VS Code + Copilot](https://code.visualstudio.com/) | `.vscode/settings.json` | `athena init --ide vscode` |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `.gemini/AGENTS.md` | `athena init --ide gemini` |
| [Kilo Code](https://kilocode.ai/) | `.kilocode/rules/athena.md` | `athena init --ide kilocode` |
| [Zoo Code](https://github.com/Zoo-Code-Org/Zoo-Code) | `.roo/rules/athena.md` | `athena init --ide zoocode` |

## Generic (No Init Required)

Any AI agent that reads Markdown files from the project directory will work out of the box:

- **Claude Code** — Reads `CLAUDE.md` or `.claude/` directory
- **Windsurf** — Reads project files directly
- **GitHub Copilot Chat** — Reads workspace files
- **Any local LLM** — Point it at the `.framework/` and `.context/` directories

## How It Works

When you run `athena init --ide <name>`, Athena creates:

1. The **standard workspace structure** (`.agent/`, `.context/`, `.framework/`)
2. An **IDE-specific config file** that tells the agent where to find Athena's memory, identity, and workflows

The config file is a Markdown document containing:

- Boot instructions (`/start`, `/end`, `/save`)
- Key directory references
- Session discipline guidelines

## Adding a New IDE

To add support for a new IDE:

1. Determine where the IDE reads its agent rules from (e.g., `.cursor/rules.md`)
2. Add a template constant and handler to `src/athena/cli/init.py`
3. Add the IDE name to the `choices` list in `src/athena/__main__.py`
4. Submit a PR — see [CONTRIBUTING.md](CONTRIBUTING.md)

---

**[Back to README](README.md)**
