"""
gate.py — Universal AgentGate SDK module.
Provides unified governance interception across IDEs (Claude Code, AG/Antigravity, Cursor, CLI).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from athena.core.gate_meta import REMINDER_TEMPLATE, classify
from athena.core.ruin_structured import StructuredRuinCheck


def get_invocations_path(workspace_root: Path) -> Path:
    """Returns the canonical path to invocations.jsonl."""
    return workspace_root / ".athena" / "invocations.jsonl"


class AgentGate:
    """
    Universal AgentGate.
    Intercepts prompts and tool execution out-of-band or via MCP server.
    """
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        self.config_path = self.workspace_root / ".agent/config/gate_config.json"
        self.config = self._load_config()
        self.ruin_checker = StructuredRuinCheck(self.workspace_root)

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"universal_gate_enabled": True}

    def log_fire(self, fired_classes: list[str], prompt: str | None = None) -> None:
        """Logs gate fire to invocations.jsonl for fire-rate monitoring. Never raises."""
        try:
            invocations_file = get_invocations_path(self.workspace_root)
            invocations_file.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "type": "hook",
                "name": "meta_awareness_gate",
                "classes": fired_classes,
                "trigger": "UserPromptSubmit",
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            with open(invocations_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def intercept_prompt(self, prompt: str) -> str | None:
        """
        Classifies prompt and returns injected system reminder string if triggered, else None.
        Replaces IDE-specific prompt hooks and logs to shared telemetry.
        """
        if not prompt or not self.config.get("universal_gate_enabled", True):
            return None

        fired = classify(prompt)
        if fired:
            self.log_fire(fired, prompt)
            return REMINDER_TEMPLATE.format(classes=", ".join(fired))
        return None

    def intercept_tool(self, tool_name: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Intercepts tool execution calls.
        Returns:
            (allowed: bool, veto_reason: Optional[str])
        """
        if not self.config.get("universal_gate_enabled", True):
            return True, None

        # Execute structured ruin check on command executions or path parameters
        command = args.get("command") or args.get("CommandLine") or args.get("cmd")
        if command and isinstance(command, str):
            allowed, red_flags = self.ruin_checker.check_command(command)
            if not allowed:
                return False, f"Vetoed by StructuredRuinCheck: red flags detected {red_flags}"

        target_path = args.get("path") or args.get("TargetFile") or args.get("AbsolutePath")
        if target_path and isinstance(target_path, str):
            allowed, red_flags = self.ruin_checker.check_command(f"touch {target_path}")
            if not allowed:
                return False, f"Vetoed by StructuredRuinCheck: path targeting prohibited directory {red_flags}"

        return True, None
