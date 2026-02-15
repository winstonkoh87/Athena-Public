"""
athena.core.permissions
========================

Permissioning Layer for Project Athena.
Controls tool execution access and data sensitivity.

Three concepts:
    1. Capability Tokens — gate which operations a caller can perform
    2. Sensitivity Labels — classify data flowing through the system
    3. Secret Mode — restrict all output to public-only data

Usage:
    from athena.core.permissions import get_permissions, Permission, Sensitivity

    perms = get_permissions()
    perms.check("smart_search")       # raises PermissionDenied if not allowed
    perms.label("session_content")    # returns Sensitivity.INTERNAL
    perms.set_secret_mode(True)       # activates demo/external mode
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("athena.permissions")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Permission(str, Enum):
    """Tool capability levels (escalating)."""

    READ = "read"  # Can query / read data
    WRITE = "write"  # Can modify session logs, checkpoints
    ADMIN = "admin"  # Can modify config, clear caches, manage sessions
    DANGEROUS = "dangerous"  # Can delete data, run shell commands (future)


class Sensitivity(str, Enum):
    """Data sensitivity classification."""

    PUBLIC = "public"  # Safe for external sharing, demos, GitHub
    INTERNAL = "internal"  # Normal operational data, session logs
    SECRET = "secret"  # API keys, credentials, personal finances, trading


# ---------------------------------------------------------------------------
# Tool Registry — maps tool names to their required permission + sensitivity
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    # MCP Tools
    "smart_search": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Search knowledge base",
    },
    "quicksave": {
        "permission": Permission.WRITE,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Save checkpoint to session log",
    },
    "health_check": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.PUBLIC,
        "description": "System health audit",
    },
    "recall_session": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Read session log content",
    },
    "governance_status": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Triple-Lock compliance state",
    },
    "list_memory_paths": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.PUBLIC,
        "description": "List memory directories",
    },
    # Future tools (pre-registered for when they're added)
    "clear_cache": {
        "permission": Permission.ADMIN,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Clear search cache",
    },
    "update_canonical": {
        "permission": Permission.ADMIN,
        "sensitivity": Sensitivity.SECRET,
        "description": "Modify canonical memory",
    },
    "run_evaluator": {
        "permission": Permission.ADMIN,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Run search quality evaluation",
    },
}


# ---------------------------------------------------------------------------
# Sensitivity patterns — auto-classify content
# ---------------------------------------------------------------------------

SECRET_PATTERNS = [
    "api_key",
    "api-key",
    "apikey",
    "secret_key",
    "secret-key",
    "password",
    "passwd",
    "SUPABASE_KEY",
    "GOOGLE_API_KEY",
    "ANTHROPIC_API_KEY",
    "private_key",
    "access_token",
    "bearer",
    "trading",
    "eurusd",
    "forex",
    "P&L",
    "profit_loss",
    "bank_account",
    "credit_card",
    ".env",
]

INTERNAL_PATTERNS = [
    "session_log",
    "checkpoint",
    "canonical",
    "memory_bank",
    "decision_ledger",
    "user_profile",
    "userContext",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PermissionDenied(Exception):
    """Raised when a tool call lacks required capability."""

    def __init__(self, tool: str, required: Permission, granted: Permission):
        self.tool = tool
        self.required = required
        self.granted = granted
        super().__init__(
            f"Permission denied for '{tool}': requires {required.value}, caller has {granted.value}"
        )


class SecretModeViolation(Exception):
    """Raised when secret data is accessed in public/demo mode."""

    def __init__(self, tool: str, data_sensitivity: Sensitivity):
        self.tool = tool
        self.data_sensitivity = data_sensitivity
        super().__init__(
            f"Secret mode active: '{tool}' returns {data_sensitivity.value} "
            f"data — blocked in demo mode"
        )


# ---------------------------------------------------------------------------
# Permission Engine
# ---------------------------------------------------------------------------

# Permission hierarchy for comparison
_PERMISSION_LEVEL = {
    Permission.READ: 0,
    Permission.WRITE: 1,
    Permission.ADMIN: 2,
    Permission.DANGEROUS: 3,
}


@dataclass
class PermissionEngine:
    """
    Central permissioning engine.

    Manages caller capability level, secret mode state,
    and audit logging of all permission checks.
    """

    # Current caller's maximum permission level
    caller_level: Permission = Permission.WRITE

    # Secret mode — when True, blocks access to INTERNAL and SECRET data
    secret_mode: bool = False

    # Audit log
    audit_log: list[dict] = field(default_factory=list)

    # State file for persistence
    _state_path: Path | None = None

    def __post_init__(self):
        from athena.core.config import PROJECT_ROOT

        self._state_path = PROJECT_ROOT / ".agent" / "state" / "permissions.json"
        self._load_state()

    def _load_state(self):
        """Load persisted state."""
        if self._state_path and self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text())
                self.secret_mode = data.get("secret_mode", False)
                self.caller_level = Permission(data.get("caller_level", "write"))
            except Exception:
                pass

    def _save_state(self):
        """Persist state to disk."""
        if self._state_path:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(
                json.dumps(
                    {
                        "secret_mode": self.secret_mode,
                        "caller_level": self.caller_level.value,
                        "last_updated": datetime.now().isoformat(),
                    },
                    indent=2,
                )
            )

    # --- Core API ---

    def check(self, tool_name: str) -> bool:
        """
        Check if the current caller has permission to execute a tool.
        Raises PermissionDenied if not.
        Returns True if allowed.
        """
        tool_def = TOOL_REGISTRY.get(tool_name)
        if not tool_def:
            # Unknown tool — default to WRITE permission required
            required = Permission.WRITE
        else:
            required = tool_def["permission"]

        allowed = _PERMISSION_LEVEL[self.caller_level] >= _PERMISSION_LEVEL[required]

        self._audit(
            "check",
            tool_name,
            {
                "required": required.value,
                "granted": self.caller_level.value,
                "allowed": allowed,
            },
        )

        if not allowed:
            raise PermissionDenied(tool_name, required, self.caller_level)

        return True

    def check_sensitivity(self, tool_name: str) -> bool:
        """
        Check if tool output is allowed under current sensitivity mode.
        In secret_mode, only PUBLIC tools are allowed.
        Raises SecretModeViolation if blocked.
        """
        if not self.secret_mode:
            return True

        tool_def = TOOL_REGISTRY.get(tool_name)
        if not tool_def:
            sensitivity = Sensitivity.INTERNAL
        else:
            sensitivity = tool_def["sensitivity"]

        if sensitivity != Sensitivity.PUBLIC:
            self._audit(
                "sensitivity_block",
                tool_name,
                {
                    "sensitivity": sensitivity.value,
                    "secret_mode": True,
                },
            )
            raise SecretModeViolation(tool_name, sensitivity)

        return True

    def gate(self, tool_name: str) -> bool:
        """
        Combined gate — checks both permission AND sensitivity.
        This is the main entry point for the MCP middleware.
        """
        self.check(tool_name)
        self.check_sensitivity(tool_name)
        return True

    def label(self, content: str) -> Sensitivity:
        """
        Auto-classify content sensitivity based on pattern matching.
        """
        content_lower = content.lower()

        for pattern in SECRET_PATTERNS:
            if pattern.lower() in content_lower:
                return Sensitivity.SECRET

        for pattern in INTERNAL_PATTERNS:
            if pattern.lower() in content_lower:
                return Sensitivity.INTERNAL

        return Sensitivity.PUBLIC

    def redact(self, content: str) -> str:
        """
        Redact secret patterns from content.
        Used when secret_mode is active but data must still flow.
        """
        if not self.secret_mode:
            return content

        for pattern in SECRET_PATTERNS:
            if pattern.lower() in content.lower():
                content = content.replace(pattern, "[REDACTED]")

        return content

    # --- Mode Control ---

    def set_secret_mode(self, enabled: bool) -> dict:
        """Toggle secret/demo mode."""
        old = self.secret_mode
        self.secret_mode = enabled
        self._save_state()

        self._audit(
            "mode_change",
            "secret_mode",
            {
                "old": old,
                "new": enabled,
            },
        )

        return {
            "secret_mode": enabled,
            "effect": "Only PUBLIC tools accessible"
            if enabled
            else "All tools accessible",
            "blocked_tools": [
                name
                for name, defn in TOOL_REGISTRY.items()
                if defn["sensitivity"] != Sensitivity.PUBLIC
            ]
            if enabled
            else [],
        }

    def set_caller_level(self, level: Permission) -> dict:
        """Set the caller's permission level."""
        old = self.caller_level
        self.caller_level = level
        self._save_state()

        self._audit(
            "level_change",
            "caller_level",
            {
                "old": old.value,
                "new": level.value,
            },
        )

        return {
            "caller_level": level.value,
            "accessible_tools": [
                name
                for name, defn in TOOL_REGISTRY.items()
                if _PERMISSION_LEVEL[level] >= _PERMISSION_LEVEL[defn["permission"]]
            ],
        }

    # --- Introspection ---

    def get_status(self) -> dict:
        """Return current permission state."""
        return {
            "caller_level": self.caller_level.value,
            "secret_mode": self.secret_mode,
            "registered_tools": len(TOOL_REGISTRY),
            "accessible_tools": [
                name
                for name, defn in TOOL_REGISTRY.items()
                if _PERMISSION_LEVEL[self.caller_level]
                >= _PERMISSION_LEVEL[defn["permission"]]
            ],
            "blocked_tools": [
                name
                for name, defn in TOOL_REGISTRY.items()
                if _PERMISSION_LEVEL[self.caller_level]
                < _PERMISSION_LEVEL[defn["permission"]]
            ],
            "audit_entries": len(self.audit_log),
        }

    def get_tool_manifest(self) -> list[dict]:
        """Return the full tool permission manifest."""
        return [
            {
                "tool": name,
                "permission": defn["permission"].value,
                "sensitivity": defn["sensitivity"].value,
                "description": defn["description"],
                "accessible": _PERMISSION_LEVEL[self.caller_level]
                >= _PERMISSION_LEVEL[defn["permission"]],
            }
            for name, defn in TOOL_REGISTRY.items()
        ]

    # --- Audit ---

    def _audit(self, action: str, target: str, details: dict):
        """Record a permission event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            **details,
        }
        self.audit_log.append(entry)

        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]

        # Log only high-level metadata to avoid exposing potentially sensitive details.
        logger.debug(
            "Permission %s: [REDACTED_TARGET] (details recorded in memory only)", action
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: PermissionEngine | None = None


def get_permissions() -> PermissionEngine:
    """Get or create the singleton PermissionEngine."""
    global _instance
    if _instance is None:
        _instance = PermissionEngine()
    return _instance
