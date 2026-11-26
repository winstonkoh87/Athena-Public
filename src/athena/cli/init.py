#!/usr/bin/env python3
"""
athena.cli.init
===============

Scaffold a new Athena workspace with directory structure and templates.
Fulfills the "5-Minute Quickstart" promise.

Usage:
    athena init .                     # Initialize full workspace in current directory
    athena init --here                # Same as above
    athena init --here --ide cursor   # Init with Cursor-specific config
    athena init . --profile minimal   # Minimal 3-file Markdown setup + AGENTS.md
    athena init . --profile hooks-only  # PreToolUse secret + ruin guards only
    athena init my-project            # Create new project directory
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# --- Templates ---

CORE_IDENTITY_TEMPLATE = """# Core Identity

> **Created**: {date}

## Who Am I?
An adaptive AI assistant — your strategic co-pilot, not just a chatbot.

## Operating Principles

1. **Memory First**: Log everything. Context is power.
2. **Proactive**: Anticipate needs, don't just react.
3. **Honest**: Challenge flawed assumptions respectfully.
4. **Modular**: One skill = one file. No monoliths.

## Reasoning Standards

- Consider 3+ perspectives before concluding
- Label assumptions explicitly
- Prioritize signal over noise
- Ask clarifying questions when uncertain

## Success Metric

A good conversation contains mutual corrections.
- I challenge your assumptions → you evaluate
- You correct my errors → I improve
- Both get sharper
"""

START_WORKFLOW_TEMPLATE = """---
description: Boot the AI assistant with context
---

# /start — Execution Script

> **Automation**: This workflow runs the Athena SDK boot sequence.

## Execution

// turbo

```bash
athena
```

The boot sequence will:
1. Load Core Identity
2. Recall last session context
3. Create a new session log
4. Confirm ready status

## Manual Override (if SDK unavailable)

- [ ] Read `.framework/modules/Core_Identity.md`
- [ ] Find the latest session log in `.context/memories/session_logs/`
- [ ] Create a new session log: `YYYY-MM-DD-session-XX.md`
- [ ] Output: "⚡ Ready. (Session XX started.)"
"""

END_WORKFLOW_TEMPLATE = """---
description: Close session and save learnings
---

# /end — Session Close

> **Automation**: This workflow runs the Athena SDK shutdown sequence.

## Execution

// turbo

```bash
athena --end
```

The shutdown sequence will:
1. Close the current session log
2. Update session status to "Closed"
3. Optionally trigger Supabase sync

## Manual Override (if SDK unavailable)

- [ ] Read all `### ⚡ Checkpoint` entries from current session log
- [ ] Fill in Key Topics, Decisions Made, Action Items
- [ ] Git add and commit the session log
- [ ] Output: "✅ Session XX closed and committed."
"""

SAVE_WORKFLOW_TEMPLATE = """---
description: Save a checkpoint to the current session
---

# /save — Quicksave Checkpoint

> **Automation**: This workflow runs the Athena SDK save command.

## Execution

// turbo

```bash
athena save "Brief summary of what happened"
```

The save command will append a timestamped checkpoint to the current session log.
"""


DECISIONS_TEMPLATE = """# Decision Log

> **Created**: {date}
> Append durable architectural choices, rejected dead ends, and invariants you do not want re-litigated.

| Date | Decision | Why / Constraint | Status |
|:-----|:---------|:-----------------|:-------|
| {date} | Initialize minimal Athena memory layout | Own plain Markdown state on disk | Active |
"""

MINIMAL_AGENTS_TEMPLATE = """# AGENTS.md — Athena Minimal Workspace

> Read `.context/memory_bank/userContext.md` (stable constraints) and `.context/memory_bank/activeContext.md` (current thread) before starting work.
> Keep answers direct, verify code changes with tests, and use plain ASCII for math and currency.

## Memory Files (3-File Loop)

1. `.context/memory_bank/activeContext.md` — Active focus, in-flight tasks, and latest checkpoint (rewrite regularly).
2. `.context/memory_bank/userContext.md` — Stable preferences, stack invariants, and hard constraints (rarely changes).
3. `.context/memory_bank/decisions.md` — Architectural calls and dead ends not to re-litigate.

## Session Loop

- **Start**: Read `activeContext.md` + `userContext.md`.
- **End**: Summarize only new decisions, open tasks, and dead ends into `activeContext.md` (and append durable rules to `decisions.md`).
"""

# Static PreToolUse file-access guard template (non-sensitive source code, not credential data).
HOOK_FILE_GUARD_TEMPLATE = '''#!/usr/bin/env python3
"""PreToolUse (Read|Edit|Write) guard blocking access to sensitive credential files."""

import json
import sys
from pathlib import Path

GUARDED_NAMES = {
    ".env",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    ".npmrc",
    ".netrc",
    ".pypirc",
    "credentials.json",
    "service-account.json",
}
SAFE_ENV_TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist"}
GUARDED_EXTS = (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore")
GUARDED_SEGMENTS = ("/.aws/credentials", "/.ssh/id_", "/.gnupg/")


def main() -> None:
    try:
        if sys.stdin.isatty():
            return
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("Empty stdin payload")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object on stdin")
        if "toolCall" in data:
            tc = data.get("toolCall")
            if not isinstance(tc, dict):
                raise ValueError("Expected toolCall JSON object")
            tool_input = tc.get("args") or {}
        else:
            tool_input = data.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            raise ValueError("Expected tool_input JSON object")
        file_path = (
            tool_input.get("file_path")
            or tool_input.get("path")
            or tool_input.get("Path")
            or tool_input.get("target_file")
            or tool_input.get("TargetFile")
            or tool_input.get("AbsolutePath")
            or ""
        )
        if not file_path:
            return
        name_lower = Path(file_path).name.lower()
        posix_lower = file_path.replace("\\\\", "/").lower()
        is_dotenv = name_lower == ".env" or (
            name_lower.startswith(".env.") and name_lower not in SAFE_ENV_TEMPLATES
        )
        if (
            is_dotenv
            or name_lower in GUARDED_NAMES
            or name_lower.endswith(GUARDED_EXTS)
            or any(seg in posix_lower for seg in GUARDED_SEGMENTS)
        ):
            reason = f"BLOCKED: Access to {file_path} denied. Sensitive file pattern detected."
            if "toolCall" in data or "hookEventName" in data:
                print(json.dumps({"decision": "deny", "reason": reason}))
                print(reason, file=sys.stderr)
                sys.exit(0)
            print(reason, file=sys.stderr)
            sys.exit(2)
    except Exception as exc:
        print(
            f"BLOCKED (fail-closed): File protection gate error while inspecting input: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
'''

HOOK_BLOCK_RUIN_TEMPLATE = '''#!/usr/bin/env python3
"""PreToolUse (Bash) Law #1 guard blocking canonical destructive shell commands."""

import json
import re
import shlex
import sys

RUIN_PATTERNS = (
    r"rm\\s+-[a-z]*r[a-z]*f[a-z]*\\s+(?:/(?:\\s|$)|\\*|~|\\.context\\b|\\.agent\\b)",
    r"rm\\s+-[a-z]*f[a-z]*r[a-z]*\\s+(?:/(?:\\s|$)|\\*|~|\\.context\\b|\\.agent\\b)",
    r"find\\s+.*(?:\\.context|\\.agent).*\\-(?:delete|exec\\s+rm)",
    r"mv\\s+.*(?:\\.context|\\.agent)\\b",
    r"truncate\\s+-s\\s+0\\s+.*(?:\\.context|\\.agent)",
)


def is_safe_command(command: str) -> bool:
    if not command or not command.strip():
        return True
    try:
        from athena.core.ruin_check import check_command

        return check_command(command)
    except ImportError:
        pass

    for pat in RUIN_PATTERNS:
        if re.search(pat, command, re.IGNORECASE):
            return False

    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    if not tokens:
        return True

    cmd = tokens[0].lower()
    if cmd == "git":
        if "reset" in tokens and any(t in tokens for t in ("--hard", "-hard")):
            return False
        if "push" in tokens and any(t in tokens for t in ("--force", "-f", "--force-with-lease")):
            return False
        if "clean" in tokens and any(t.startswith("-") and "f" in t for t in tokens):
            return False
    if cmd in ("python", "python3") and "-c" in tokens:
        idx = tokens.index("-c")
        if idx + 1 < len(tokens):
            code = tokens[idx + 1]
            if any(x in code for x in ("shutil.rmtree", "os.remove", "os.unlink")) and any(
                t in code for t in (".context", ".agent", "/")
            ):
                return False
    return True


def main() -> None:
    try:
        if sys.stdin.isatty():
            return
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("Empty stdin payload")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object on stdin")
        if "toolCall" in data:
            tc = data.get("toolCall")
            if not isinstance(tc, dict):
                raise ValueError("Expected toolCall JSON object")
            tool_input = tc.get("args") or {}
        else:
            tool_input = data.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            raise ValueError("Expected tool_input JSON object")
        command = (
            tool_input.get("command")
            or tool_input.get("cmd")
            or tool_input.get("CommandLine")
            or ""
        )
        if command and not is_safe_command(command):
            reason = f"BLOCKED by Law #1 (No Irreversible Ruin): {command}"
            if "toolCall" in data or "hookEventName" in data:
                print(json.dumps({"decision": "deny", "reason": reason}))
                print(reason, file=sys.stderr)
                sys.exit(0)
            print(reason, file=sys.stderr)
            sys.exit(2)
    except Exception as exc:
        print(
            f"BLOCKED (fail-closed) by Law #1: Ruin gate failed to parse tool input: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
'''

HOOKS_ONLY_SETTINGS_JSON = """{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$CLAUDE_PROJECT_DIR/.agent/scripts/security/block_secrets.py\\"",
            "timeout": 5,
            "onFailure": "block",
            "statusMessage": "Secret protection gate"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \\"$CLAUDE_PROJECT_DIR/.agent/scripts/security/block_ruin.py\\"",
            "timeout": 5,
            "onFailure": "block",
            "statusMessage": "Ruin protection gate (Law #1)"
          }
        ]
      }
    ]
  }
}
"""

# --- IDE-Specific Templates ---

_WORKFLOW_RULES_SECTION = """
## Problem-Solving & Decision Workflow (MCP)

1. **Pre-Flight Grounding**: Call `context_gate(query)` before solving non-trivial problems (`STANDARD` / `ULTRA`).
2. **Problem Framing**: Before optimizing an assumed sub-problem, call `frame_open(..., lite=True)` (use full strict framing for high-stakes or low-reversibility calls) and verify constraints.
3. **Fail-Closed Decision Screening**: Run `decision_screen(...)` with explicit baseline alternatives, preference provenance, and ruin inputs; apply the Law #1 ruin veto to reject existential or non-ergodic downside regardless of expected value.
4. **Calibration Hygiene**: Periodically inspect `calibration_status()` to track confidence calibration and close overdue frames and predictions.
"""

ANTIGRAVITY_RULES = """# Antigravity Agent Rules — Athena Governance Parity (v9.9.8+)

> Auto-generated by `athena init --ide antigravity`

## Boot Sequence
On `/start`, run: `athena`

## Mandatory Meta-Awareness Protocol (Governance Parity)
> FIDELITY: On EVERY user prompt, call MCP tool `meta_awareness_check(prompt)` FIRST before any other tool or reasoning.
> If it returns injection != null, inject it as system-reminder and answer the 8 kernel questions before responding.
> Telemetry is logged to `.athena/invocations.jsonl`. Skipping is a measurable governance violation.

## Save Sequence
On `/end`, run: `athena --end`

## Quicksave
On `/save`, run: `athena save "summary"`

## Directory Context
- `.framework/` — Core identity and laws
- `.context/` — Session logs and memories
- `.agent/` — Workflows and scripts
""" + _WORKFLOW_RULES_SECTION

CURSOR_RULES = """# Cursor Agent Rules

> Auto-generated by `athena init --ide cursor`

## Context

You are an AI agent operating within an Athena workspace.
Always check `.framework/modules/Core_Identity.md` for your operating principles.

## Key Directories

- `.framework/` — Your identity and laws (read this first)
- `.context/` — Session logs (check for prior context)
- `.agent/workflows/` — Available commands (start.md, end.md, save.md)

## Boot Command

Run `athena` to boot the session system, or manually read the latest session log.

## Session Discipline

1. On session start — run `/start` workflow
2. During work — periodically run `/save` to checkpoint
3. On session end — run `/end` workflow
""" + _WORKFLOW_RULES_SECTION

VSCODE_SETTINGS = """{
  "files.associations": {
    "*.md": "markdown"
  },
  "editor.wordWrap": "on",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "markdown.preview.breaks": true
}
"""

GEMINI_RULES = """# Gemini Agent Rules

> Auto-generated by `athena init --ide gemini`

## Athena Workspace Context

This is an Athena workspace. Key directories:
- `.framework/` — Core identity, read `.framework/modules/Core_Identity.md` first
- `.context/` — Session logs and project state
- `.agent/` — Workflows and automation scripts

## Session Commands

| Command | Action |
|---------|--------|
| `athena` | Boot session |
| `athena save "note"` | Quicksave |
| `athena --end` | Close session |
| `athena check` | Health check |
""" + _WORKFLOW_RULES_SECTION

KILOCODE_RULES = """# Kilo Code Agent Rules

> Auto-generated by `athena init --ide kilocode`

## Context

You are an AI agent operating within an Athena workspace.
Always check `.framework/modules/Core_Identity.md` for your operating principles.

## Key Directories

- `.framework/` — Your identity and laws (read this first)
- `.context/` — Session logs (check for prior context)
- `.agent/workflows/` — Available commands (start.md, end.md, save.md)

## Boot Command

Run `athena` to boot the session system, or manually read the latest session log.

## Session Discipline

1. On session start — run `/start` workflow
2. During work — periodically run `/save` to checkpoint
3. On session end — run `/end` workflow

## Slash Commands

| Command | Action |
|---------|--------|
| `/start` | Boot session — loads identity + JIT routing |
| `/end` | Close session — finalize, sync, commit |
| `/save` | Quicksave checkpoint to session log |
| `/think` | Escalate reasoning depth |
| `/ultrathink` | Maximum depth + full context stack |
""" + _WORKFLOW_RULES_SECTION

ROOCODE_RULES = """# Roo Code Agent Rules

> Auto-generated by `athena init --ide roocode`

## Context

You are an AI agent operating within an Athena workspace.
Always check `.framework/modules/Core_Identity.md` for your operating principles.

## Key Directories

- `.framework/` — Your identity and laws (read this first)
- `.context/` — Session logs (check for prior context)
- `.agent/workflows/` — Available commands (start.md, end.md, save.md)

## Boot Command

Run `athena` to boot the session system, or manually read the latest session log.

## Session Discipline

1. On session start — run `/start` workflow
2. During work — periodically run `/save` to checkpoint
3. On session end — run `/end` workflow

## Slash Commands

| Command | Action |
|---------|--------|
| `/start` | Boot session — loads identity + JIT routing |
| `/end` | Close session — finalize, sync, commit |
| `/save` | Quicksave checkpoint to session log |
| `/think` | Escalate reasoning depth |
| `/ultrathink` | Maximum depth + full context stack |
""" + _WORKFLOW_RULES_SECTION

CLAUDE_RULES = """# CLAUDE.md — Athena Workspace

> Auto-generated by `athena init --ide claude`

## Context

You are an AI agent operating within an Athena workspace.
Always check `.framework/modules/Core_Identity.md` for your operating principles.

## Key Directories

- `.framework/` — Your identity and laws (read this first)
- `.context/` — Session logs (check for prior context)
- `.agent/workflows/` — Available commands (start.md, end.md, save.md)

## Boot Command

Run `athena` to boot the session system, or manually read the latest session log.

## Session Discipline

1. On session start — run `/start` workflow
2. During work — periodically run `/save` to checkpoint
3. On session end — run `/end` workflow

## Slash Commands

| Command | Action |
|---------|--------|
| `/start` | Boot session — loads identity + JIT routing |
| `/end` | Close session — finalize, sync, commit |
| `/save` | Quicksave checkpoint to session log |
| `/think` | Escalate reasoning depth |
| `/ultrathink` | Maximum depth + full context stack |
""" + _WORKFLOW_RULES_SECTION

ACTIVE_CONTEXT_TEMPLATE = """# Active Context

> **Last Updated**: {date}
> **Session State**: S1 (Initial session)

## Current Focus
Workspace initialized. Ready for initial task.

## Active Goals
- [ ] Configure local workflow
- [ ] Run first session (/start)

## Recent Decisions
- Initialized workspace via Athena CLI.
"""

USER_CONTEXT_TEMPLATE = """# User Context

> **Created**: {date}

## Profile
- **Role**: Developer
- **Preferences**: Modular, tested code; low token overhead.
"""

PRODUCT_CONTEXT_TEMPLATE = """# Product Context

> **Created**: {date}

## Philosophy
Local-first context compounding. Rules enforced by hooks, not just prompts.
"""

SYSTEM_PATTERNS_TEMPLATE = """# System Patterns

> **Created**: {date}

## Architecture
- Context lives in plain Markdown under `.context/`
- Workflows live under `.agent/workflows/`
- Laws and principles live under `.framework/`
"""


VALID_PROFILES = ("full", "minimal", "hooks-only")


def _write_template(
    root: Path, rel_path: str, content: str, *, executable: bool = False
) -> None:
    full_path = root / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    if not full_path.exists():
        full_path.write_text(content, encoding="utf-8")
        if executable:
            os.chmod(full_path, 0o755)
        print(f"   ✅ {rel_path}")
    else:
        print(f"   ⏭️  {rel_path} (already exists)")


def _ensure_git_repo(root: Path) -> None:
    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if git_check.returncode != 0:
            subprocess.run(["git", "init"], cwd=root, capture_output=True, text=True)
            print("   ✅ Git repository initialized")
    except Exception:
        pass


def _init_minimal(root: Path, today: str, ide: str | None) -> None:
    print("\n📁 Creating minimal memory structure...")
    (root / ".context" / "memory_bank").mkdir(parents=True, exist_ok=True)
    print("   ✅ .context/memory_bank/")

    marker_path = root / ".athena_root"
    marker_path.write_text(
        f"# Athena Workspace (minimal)\nCreated: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )
    print("   ✅ .athena_root (workspace marker)")

    print("\n📝 Creating 3-file memory templates...")
    for rel_path, content in (
        (".context/memory_bank/activeContext.md", ACTIVE_CONTEXT_TEMPLATE.format(date=today)),
        (".context/memory_bank/userContext.md", USER_CONTEXT_TEMPLATE.format(date=today)),
        (".context/memory_bank/decisions.md", DECISIONS_TEMPLATE.format(date=today)),
        ("AGENTS.md", MINIMAL_AGENTS_TEMPLATE),
    ):
        _write_template(root, rel_path, content)

    _ensure_git_repo(root)

    if ide == "claude":
        print("\n⚙️  Creating claude configuration...")
        claude_path = root / "CLAUDE.md"
        if not claude_path.exists() and not claude_path.is_symlink():
            try:
                os.symlink("AGENTS.md", claude_path)
                print("   ✅ CLAUDE.md -> AGENTS.md (symlink)")
            except OSError:
                shutil.copy2(root / "AGENTS.md", claude_path)
                print("   ✅ CLAUDE.md (copied from AGENTS.md)")
        else:
            print("   ⏭️  CLAUDE.md (already exists)")
    elif ide:
        print(f"\n⚙️  Creating {ide} configuration...")
        _create_ide_config(root, ide)


def _init_hooks_only(root: Path) -> None:
    print("\n🛡️  Installing standalone PreToolUse safety hooks...")
    _write_template(
        root,
        ".agent/scripts/security/block_secrets.py",
        HOOK_FILE_GUARD_TEMPLATE,
        executable=True,
    )
    _write_template(
        root,
        ".agent/scripts/security/block_ruin.py",
        HOOK_BLOCK_RUIN_TEMPLATE,
        executable=True,
    )
    _write_template(
        root,
        ".claude/settings.json",
        HOOKS_ONLY_SETTINGS_JSON,
    )


def _init_full(root: Path, today: str, ide: str | None) -> None:
    directories = [
        ".agent/workflows",
        ".agent/scripts",
        ".agent/skills/protocols",
        ".framework/modules",
        ".context/memory_bank",
        ".context/memories/session_logs",
        ".context/data",
    ]

    print("\n📁 Creating directories...")
    for dir_path in directories:
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}/")

    marker_path = root / ".athena_root"
    marker_path.write_text(
        f"# Athena Workspace\nCreated: {datetime.now().isoformat()}\n", encoding="utf-8"
    )
    print("   ✅ .athena_root (workspace marker)")

    templates = [
        (
            ".framework/modules/Core_Identity.md",
            CORE_IDENTITY_TEMPLATE.format(date=today),
        ),
        (".agent/workflows/start.md", START_WORKFLOW_TEMPLATE),
        (".agent/workflows/end.md", END_WORKFLOW_TEMPLATE),
        (".agent/workflows/save.md", SAVE_WORKFLOW_TEMPLATE),
        (
            ".context/memory_bank/activeContext.md",
            ACTIVE_CONTEXT_TEMPLATE.format(date=today),
        ),
        (
            ".context/memory_bank/userContext.md",
            USER_CONTEXT_TEMPLATE.format(date=today),
        ),
        (
            ".context/memory_bank/productContext.md",
            PRODUCT_CONTEXT_TEMPLATE.format(date=today),
        ),
        (
            ".context/memory_bank/systemPatterns.md",
            SYSTEM_PATTERNS_TEMPLATE.format(date=today),
        ),
    ]

    print("\n📝 Creating template files...")
    for file_path, content in templates:
        _write_template(root, file_path, content)

    _ensure_git_repo(root)

    if ide:
        print(f"\n⚙️  Creating {ide} configuration...")
        _create_ide_config(root, ide)


def init_workspace(
    target_dir: Path | None = None,
    ide: str | None = None,
    profile: str = "full",
) -> bool:
    """
    Initialize an Athena workspace with the required directory structure.

    Args:
        target_dir: Directory to initialize. Defaults to current directory.
        ide: IDE to generate config for (antigravity, claude, cursor, vscode, gemini, kilocode, roocode, zoocode).
        profile: Scaffold profile ('full', 'minimal', or 'hooks-only').

    Returns:
        True if successful, False otherwise.
    """
    if profile not in VALID_PROFILES:
        print(f"❌ Unknown init profile '{profile}'. Expected one of: {', '.join(VALID_PROFILES)}")
        return False

    root = target_dir or Path.cwd()
    root = Path(root).resolve()

    print("🏛️  ATHENA INIT")
    print(f"   Profile: {profile}")
    if ide:
        print(f"   IDE: {ide}")
    print("=" * 60)

    today = datetime.now().strftime("%Y-%m-%d")

    if profile == "minimal":
        _init_minimal(root, today, ide)
    elif profile == "hooks-only":
        _init_hooks_only(root)
    else:
        _init_full(root, today, ide)

    # Summary
    print("\n" + "=" * 60)
    print("✅ ATHENA WORKSPACE INITIALIZED")
    print("=" * 60)
    if profile == "hooks-only":
        print("\n🚀 Next steps:")
        print("   1. Restart Claude Code to activate .claude/settings.json hooks")
        print("   2. Customize .agent/scripts/security/ as needed")
    else:
        print("\n🚀 Next steps:")
        print("   1. Open this folder in your AI IDE")
        print('   2. Type "/start" to boot your agent')
        print('   3. Work with your agent, then type "/end" to save')
    print("\n📚 Docs: https://github.com/winstonkoh87/Athena-Public")

    return True


def _create_ide_config(root: Path, ide: str) -> None:
    """Create IDE-specific configuration files."""

    if ide == "antigravity":
        # Antigravity uses AGENTS.md convention
        agents_path = root / "AGENTS.md"
        if not agents_path.exists():
            agents_path.write_text(ANTIGRAVITY_RULES, encoding="utf-8")
            print("   ✅ AGENTS.md (Antigravity rules)")
        else:
            print("   ⏭️  AGENTS.md (already exists)")

    elif ide == "cursor":
        # Cursor uses .cursorrules
        cursor_dir = root / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        rules_path = cursor_dir / "rules.md"
        if not rules_path.exists():
            rules_path.write_text(CURSOR_RULES, encoding="utf-8")
            print("   ✅ .cursor/rules.md")
        else:
            print("   ⏭️  .cursor/rules.md (already exists)")

    elif ide == "vscode":
        # VS Code uses .vscode/settings.json
        vscode_dir = root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        settings_path = vscode_dir / "settings.json"
        if not settings_path.exists():
            settings_path.write_text(VSCODE_SETTINGS, encoding="utf-8")
            print("   ✅ .vscode/settings.json")
        else:
            print("   ⏭️  .vscode/settings.json (already exists)")

    elif ide == "gemini":
        # Gemini CLI uses AGENTS.md or .gemini/
        gemini_dir = root / ".gemini"
        gemini_dir.mkdir(exist_ok=True)
        rules_path = gemini_dir / "AGENTS.md"
        if not rules_path.exists():
            rules_path.write_text(GEMINI_RULES, encoding="utf-8")
            print("   ✅ .gemini/AGENTS.md")
        else:
            print("   ⏭️  .gemini/AGENTS.md (already exists)")

    elif ide == "kilocode":
        # Kilo Code uses .kilocode/rules/athena.md
        kilocode_dir = root / ".kilocode" / "rules"
        kilocode_dir.mkdir(parents=True, exist_ok=True)
        rules_path = kilocode_dir / "athena.md"
        if not rules_path.exists():
            rules_path.write_text(KILOCODE_RULES, encoding="utf-8")
            print("   ✅ .kilocode/rules/athena.md")
        else:
            print("   ⏭️  .kilocode/rules/athena.md (already exists)")

    elif ide == "roocode" or ide == "zoocode":
        # Roo Code uses .roo/rules/athena.md
        # zoocode is a backward-compatible alias (renamed in PR #43)
        roocode_dir = root / ".roo" / "rules"
        roocode_dir.mkdir(parents=True, exist_ok=True)
        rules_path = roocode_dir / "athena.md"
        if not rules_path.exists():
            rules_path.write_text(ROOCODE_RULES, encoding="utf-8")
            print("   ✅ .roo/rules/athena.md")
        else:
            print("   ⏭️  .roo/rules/athena.md (already exists)")

    elif ide == "claude":
        # Claude Code uses CLAUDE.md convention
        claude_path = root / "CLAUDE.md"
        if not claude_path.exists():
            claude_path.write_text(CLAUDE_RULES, encoding="utf-8")
            print("   ✅ CLAUDE.md (Claude Code rules)")
        else:
            print("   ⏭️  CLAUDE.md (already exists)")


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    init_workspace(target)
