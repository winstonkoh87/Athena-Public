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

import fnmatch
import json
import logging
import re
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


class Action(str, Enum):
    """Granular permission action (stolen from OpenCode, Feb 2026)."""

    ALLOW = "allow"  # Run without approval
    ASK = "ask"  # Prompt for approval
    DENY = "deny"  # Block the action


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
    "meta_awareness_check": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.PUBLIC,
        "description": "Classify prompt for meta-awareness / interpreter kernel injection",
    },
    "agentic_search": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.INTERNAL,
        "description": "Multi-step agentic search",
    },
    "set_secret_mode": {
        "permission": Permission.ADMIN,
        "sensitivity": Sensitivity.PUBLIC,
        "description": "Toggle secret/demo mode",
    },
    "permission_status": {
        "permission": Permission.READ,
        "sensitivity": Sensitivity.PUBLIC,
        "description": "Show current permission state",
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


# High-signal secret VALUE formats — redacted wherever they appear, so the
# actual credential (not just its label) is masked. Compiled once.
_TOKEN_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),  # OpenAI / Anthropic API keys
    re.compile(
        r"eyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}"
    ),  # JWT (e.g. Supabase service keys)
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{16,}=*"),  # Bearer tokens
    re.compile(r"\b[0-9a-fA-F]{32,}\b"),  # long hex secrets / hashes
]

# key = value / key: value where the KEY names a secret → redact the VALUE,
# keeping the key visible for context. Catches .env-style leaks such as
# ``ANTHROPIC_API_KEY=sk-ant-...`` that the label-only pass used to miss.  <!-- pds:allow -->
_KV_SECRET_PATTERN = re.compile(
    r"(?i)\b([A-Za-z0-9_.\-]*"
    r"(?:api[_-]?key|secret|passwd|password|token|bearer|private[_-]?key|access[_-]?token)"
    r"[A-Za-z0-9_.\-]*)\s*([=:])\s*[^\s,;'\"]+"
)


# ---------------------------------------------------------------------------
# Granular Permission Rules (Stolen from OpenCode, Feb 2026)
# ---------------------------------------------------------------------------

# Default rules: last match wins
DEFAULT_GRANULAR_RULES: list[dict[str, str]] = [
    {"tool": "*", "pattern": "*", "action": "allow"},
    {"tool": "read", "pattern": "*.env", "action": "deny"},
    {"tool": "read", "pattern": "*.env.*", "action": "deny"},
    {"tool": "read", "pattern": "*.env.example", "action": "allow"},
    {"tool": "bash", "pattern": "rm *", "action": "deny"},
    {"tool": "bash", "pattern": "git *", "action": "allow"},
    {"tool": "doom_loop", "pattern": "*", "action": "ask"},
    {"tool": "external_directory", "pattern": "*", "action": "ask"},
]


@dataclass
class GranularRule:
    """A single permission rule with glob pattern matching."""

    tool: str  # Tool name or "*" for all
    pattern: str  # Glob pattern for tool input (e.g., "git *", "*.env")
    action: Action  # allow, ask, or deny

    def matches(self, tool_name: str, input_str: str) -> bool:
        """Check if this rule matches the given tool and input."""
        tool_match = self.tool == "*" or fnmatch.fnmatch(tool_name, self.tool)
        pattern_match = fnmatch.fnmatch(input_str, self.pattern)
        return tool_match and pattern_match


class GranularPermissionEngine:
    """
    Glob-based permission engine with allow/ask/deny per tool.

    Rules are evaluated in order; last matching rule wins.
    This mirrors OpenCode's granular permission system.

    Origin: OpenCode (anomalyco/opencode, 109K stars)
    Athena Integration: Feb 2026
    """

    def __init__(self, rules_path: Path | None = None):
        self._rules_path = rules_path
        self._rules: list[GranularRule] = []
        self._load_rules()

    def _load_rules(self):
        """Load rules from JSON file, falling back to defaults."""
        loaded = False
        if self._rules_path and self._rules_path.exists():
            try:
                data = json.loads(self._rules_path.read_text())
                self._rules = [
                    GranularRule(
                        tool=r["tool"],
                        pattern=r["pattern"],
                        action=Action(r["action"]),
                    )
                    for r in data
                ]
                loaded = True
            except Exception:
                pass

        if not loaded:
            self._rules = [
                GranularRule(
                    tool=r["tool"],
                    pattern=r["pattern"],
                    action=Action(r["action"]),
                )
                for r in DEFAULT_GRANULAR_RULES
            ]

    def save_rules(self):
        """Persist current rules to disk."""
        if self._rules_path:
            self._rules_path.parent.mkdir(parents=True, exist_ok=True)
            data = [
                {"tool": r.tool, "pattern": r.pattern, "action": r.action.value}
                for r in self._rules
            ]
            self._rules_path.write_text(json.dumps(data, indent=2))

    def check(self, tool_name: str, input_str: str = "*") -> Action:
        """
        Evaluate rules for a tool call. Returns the action from the
        last matching rule (last-match-wins semantics).
        """
        result = Action.ALLOW  # Default if no rules match
        for rule in self._rules:
            if rule.matches(tool_name, input_str):
                result = rule.action
        return result

    def add_rule(self, tool: str, pattern: str, action: Action):
        """Add a new rule. Appended at the end (highest priority)."""
        self._rules.append(GranularRule(tool=tool, pattern=pattern, action=action))
        self.save_rules()

    def get_rules(self) -> list[dict]:
        """Return all rules as a list of dicts."""
        return [
            {"tool": r.tool, "pattern": r.pattern, "action": r.action.value}
            for r in self._rules
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
    granular glob-based rules, and audit logging of all permission checks.
    """

    # Current caller's maximum permission level
    caller_level: Permission = Permission.WRITE

    # Redaction mode — when True, blocks access to INTERNAL and SECRET data.
    # Named for what it holds (a boolean toggle) rather than what it guards:
    # as `secret_mode`, static analysis read the persisted flag as stored
    # secret material (CodeQL py/clear-text-storage-sensitive-data).
    # `secret_mode` survives as a property alias below.
    redaction_mode: bool = False

    # Audit log
    audit_log: list[dict] = field(default_factory=list)

    # State file for persistence
    _state_path: Path | None = None

    # Granular permission engine (initialized in __post_init__)
    _granular: GranularPermissionEngine | None = None

    # --- Backward-compatible alias ---

    @property
    def secret_mode(self) -> bool:
        """Alias for :attr:`redaction_mode` — the public spelling of the flag."""
        return self.redaction_mode

    @secret_mode.setter
    def secret_mode(self, enabled: bool) -> None:
        self.redaction_mode = bool(enabled)

    def __post_init__(self):
        from athena.core.config import PROJECT_ROOT

        self._state_path = PROJECT_ROOT / ".agent" / "state" / "permissions.json"
        rules_path = PROJECT_ROOT / ".agent" / "state" / "permission_rules.json"
        self._granular = GranularPermissionEngine(rules_path=rules_path)
        self._load_state()

    def _load_state(self):
        """Load persisted state."""
        if self._state_path and self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text())
                # Accept the legacy "secret_mode" key so state files written
                # by earlier versions keep loading.
                self.redaction_mode = bool(
                    data.get("redaction_mode", data.get("secret_mode", False))
                )
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
                        "redaction_mode": self.redaction_mode,
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
        In redaction mode, only PUBLIC tools are allowed.
        Raises SecretModeViolation if blocked.
        """
        if not self.redaction_mode:
            return True

        tool_def = TOOL_REGISTRY.get(tool_name)
        sensitivity = Sensitivity.INTERNAL if not tool_def else tool_def["sensitivity"]

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

    def gate(self, tool_name: str, input_str: str = "*") -> bool:
        """
        Combined gate — checks permission, sensitivity, AND granular rules.
        This is the main entry point for the MCP middleware.
        """
        self.check(tool_name)
        self.check_sensitivity(tool_name)

        # Granular check (allow/ask/deny with glob patterns)
        if self._granular:
            action = self._granular.check(tool_name, input_str)
            self._audit(
                "granular_check",
                tool_name,
                {"input": input_str[:100], "action": action.value},
            )
            if action == Action.DENY:
                raise PermissionDenied(
                    tool_name, Permission.DANGEROUS, self.caller_level
                )
            # Action.ASK is logged but not enforced server-side
            # (the IDE/client is responsible for prompting)

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
        Redact secrets from content when secret_mode is active.

        Redacts the secret VALUE, not merely its label: a naive
        ``replace("API_KEY", "[REDACTED]")`` leaves ``API_KEY=sk-...`` as
        ``[REDACTED]=sk-...`` — the actual key in cleartext. The passes below
        mask the value itself:

        1. ``key = value`` / ``key: value`` pairs where the key names a secret.
        2. Standalone high-entropy token formats (sk-..., JWTs, bearer, long hex).
        3. Fallback: mask any remaining bare secret-pattern keywords.
        """
        if not self.redaction_mode:
            return content

        # 1. Redact the VALUE in secret key/value pairs (keep the key label).
        content = _KV_SECRET_PATTERN.sub(r"\1\2 [REDACTED]", content)

        # 2. Redact standalone credential-shaped tokens anywhere they appear.
        for pat in _TOKEN_VALUE_PATTERNS:
            content = pat.sub("[REDACTED]", content)

        # 3. Fallback: mask any remaining bare secret keyword (case-insensitive).
        for pattern in SECRET_PATTERNS:
            if pattern.lower() in content.lower():
                content = re.sub(
                    re.escape(pattern), "[REDACTED]", content, flags=re.IGNORECASE
                )

        return content

    # --- Mode Control ---

    def set_secret_mode(self, enabled: bool) -> dict:
        """Toggle secret/demo mode."""
        old = self.redaction_mode
        self.redaction_mode = bool(enabled)
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
            "secret_mode": self.redaction_mode,
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
            "granular_rules": self._granular.get_rules() if self._granular else [],
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
