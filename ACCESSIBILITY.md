# Accessibility Statement

This repository documents how **Project Athena** handles accessibility across its Markdown workspace, Python CLI (`athena`), terminal dashboards, and standalone HTML examples.

---

## 1. Accessibility Commitment

Athena is designed around plain-text workflows so users can operate it with their own editor, terminal emulator, font scaling, high-contrast theme, or assistive technology. We treat accessibility barriers as functional defects alongside correctness and security issues.

**Honest Baseline**: Athena has **not** undergone a formal WCAG 2.1/2.2 Level AA audit or systematic manual testing across screen readers (NVDA, JAWS, VoiceOver) and switch/voice-control software. This document describes what is verifiable in the repository today and where real gaps remain.

---

## 2. How Athena Supports Accessibility Today

- **Plain-Text, Tool-Agnostic Knowledge Layer**: Memory files (`.context/`), workflows, examples (`examples/protocols/`), and generated IDE instructions (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules.md`, `.gemini/AGENTS.md`, `.roo/rules/athena.md`) are plain UTF-8 Markdown. Every core artifact can be read, searched, and edited in any accessible text editor, terminal pager, or Braille display without proprietary binary formats.
- **IDE & Terminal Flexibility**: `athena init --ide <target>` supports both terminal-native workflows (Claude Code, Gemini CLI) and GUI editors with built-in zoom, high-contrast themes, keyboard navigation, and screen-reader support (VS Code, Cursor, Antigravity, Roo Code, Kilo Code).
- **Machine-Readable CLI Diagnostics**: `athena doctor --json` outputs structured JSON (`src/athena/cli/doctor.py`) and `athena doctor --quiet` reduces terminal verbosity, making health checks easier to pipe into screen-reader-friendly formatters or custom scripts.
- **Plain-Text Math & Formatting Policy**: Repository guidelines (`CONTRIBUTING.md`) prohibit raw LaTeX/KaTeX delimiters in Markdown and prose in favor of plain ASCII/Unicode notation (for example, `O(N^2)` instead of TeX markup), preventing unrendered banner errors and noisy raw TeX syntax in terminals and screen readers.

---

## 3. Known Limitations & Workarounds

The following barriers are verified in the current codebase:

| Surface | Verified Limitation | Current Workaround |
|:--------|:--------------------|:-------------------|
| **Core CLI & Auditors (`src/athena/core/colors.py`, `src/athena/cli/doctor.py`, `src/athena/auditors/`)** | Hardcoded ANSI escape sequences (`\033[...]`) are emitted directly without checking the `NO_COLOR` environment variable, `TERM`, or TTY status (`sys.stdout.isatty()`). Note that `rich.console.Console()` scripts (`athena_tui.py`, `examples/scripts/athena_cockpit.py`) defer color handling to `rich`. | Use `athena doctor --json` for structured unstyled diagnostics, or strip ANSI codes via downstream pagers/filters when piping CLI output. |
| **Terminal Status Indicators (`src/athena/__main__.py`, `src/athena/tools/athena_tui.py`)** | `athena check` prefixes status lines with emoji alongside text labels, while `athena_tui.py` renders bare status icons (`✅` / `❌`) in its system status table and uses bullet/shield glyphs in headers. Screen readers may announce emoji descriptions verbosely or lack text context in the table status column. | Rely on `athena doctor --json` for status inspection or inspect `.context/` Markdown files directly. |
| **Live TUI Dashboards (`src/athena/tools/athena_tui.py`, `examples/scripts/athena_cockpit.py`)** | Uses `rich.live.Live` polling loops (`screen=True` in `athena_tui.py`, 1 Hz refresh) that overwrite the terminal buffer continuously and provide no interactive keyboard controls beyond `Ctrl+C` to exit. | Avoid the live TUI when using terminal screen readers; run one-shot CLI commands (`athena check`, `athena doctor --json`) or read `.context/memory_bank/activeContext.md` directly. |
| **HTML Demo Pages (`examples/demo.html`, `examples/knowledge_graph_demo.html`)** | `examples/demo.html` uses CSS `fadeIn` and infinite cursor `blink` animations without a `prefers-reduced-motion` media query fallback. `examples/knowledge_graph_demo.html` renders a third-party `vis-network` canvas without `<html lang="...">`, ARIA landmarks, keyboard node navigation, or a non-canvas text fallback. | Both files are illustrative static examples; all underlying architecture and protocol data is documented directly in Markdown under `docs/` and `examples/protocols/`. |
| **Architecture Diagrams (`docs/`, `README.md`)** | Several docs use ASCII flowcharts or Mermaid diagrams without synchronized ARIA descriptions on rendered views. | Accompanying prose and tables in `docs/ARCHITECTURE.md` and `ARCHITECTURE.md` explain the core concepts in linear text. |

---

## 4. Verification Status

- **Automated prose checks**: Link integrity (`.github/scripts/check_links.py`) and Markdown formatting/LaTeX-delimiter tests (`tests/test_latex_leak.py`) run in CI.
- **No automated UI accessibility suite yet**: This repository does not currently run automated WCAG scanners (such as `axe-core` or `pa11y`) on `examples/*.html` or automated screen-reader regression tests on CLI/TUI output.

---

## 5. Reporting Accessibility Barriers & Contributing Fixes

If any file, CLI command, terminal screen, or example blocks you from using or contributing to Athena, please let us know:

- **Report a barrier**: Open a [Bug Report](https://github.com/winstonkoh87/Athena-Public/issues/new?template=bug_report.md) with the `accessibility` context, your OS, terminal or editor, assistive technology (if applicable), and steps to reproduce.
- **Suggest an improvement**: Open a [Feature Request](https://github.com/winstonkoh87/Athena-Public/issues/new?template=feature_request.md) (for example, adding global `NO_COLOR` / `--plain` support to `src/athena/core/colors.py` and auditors, text labels for TUI tables, or `prefers-reduced-motion` and keyboard/text fallbacks in `examples/`).
- **Contribute directly**: Review [CONTRIBUTING.md](CONTRIBUTING.md) and [SUPPORT.md](SUPPORT.md) before opening a pull request. Community interactions are governed by our [Code of Conduct](CODE_OF_CONDUCT.md) and operational guardrails in [SAFETY.md](SAFETY.md).
