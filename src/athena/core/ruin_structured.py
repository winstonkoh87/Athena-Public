"""
ruin_structured.py — Structured command parser & ruin proximity safety check.
Replaces naive regex matching with shlex tokenization, path resolution,
capability-level filtering, and cumulative red-flag scoring.
"""

import shlex
from pathlib import Path


class StructuredRuinCheck:
    """
    Structured Ruin Check Engine.
    Evaluates execution safety against workspace root boundaries and capability levels.
    """
    def __init__(self, workspace_root: Path | None = None, capability_level: int = 2):
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        self.capability_level = capability_level  # 1=read, 2=write, 3=admin, 4=dangerous

    def check_command(self, command: str) -> tuple[bool, list[str]]:
        """
        Parses command string into tokens and evaluates ruin risk.
        Returns:
            (allowed: bool, red_flags: List[str])
        """
        if not command or not command.strip():
            return True, []

        red_flags: list[str] = []
        try:
            tokens = shlex.split(command)
        except Exception:
            # If shlex parsing fails (e.g. malformed quotes), flag suspicious formatting
            tokens = command.split()
            red_flags.append("malformed_shell_syntax")

        if not tokens:
            return True, []

        cmd_name = tokens[0].lower()

        # 0. Shell redirection truncation on protected targets
        if ">" in command:
            for part in command.split(">")[1:]:
                target = part.strip().split()[0] if part.strip() else ""
                clean_target = target.strip("'\"")
                if clean_target in (".context/CANONICAL.md", ".context", ".agent", "CANONICAL.md") or clean_target.startswith((".context/", ".agent/")):
                    return False, ["truncating_redirection_on_protected_path"]

        # 1. Nested interpreters inspection
        if cmd_name in ("bash", "sh", "zsh") and "-c" in tokens:
            idx = tokens.index("-c")
            if idx + 1 < len(tokens):
                sub_allowed, sub_flags = self.check_command(tokens[idx + 1])
                if not sub_allowed:
                    return False, ["nested_shell_veto"] + sub_flags

        if cmd_name in ("python", "python3") and "-c" in tokens:
            idx = tokens.index("-c")
            if idx + 1 < len(tokens):
                py_code = tokens[idx + 1]
                if any(x in py_code for x in ("shutil.rmtree", "os.remove", "os.unlink", "os.rmdir")) and \
                   any(target in py_code for target in (".context", ".agent", "CANONICAL", "PROJECTS", "/")):
                    return False, ["python_destructive_call"]

        # 2. Destructive Git command inspection
        if cmd_name == "git":
            if "reset" in tokens and any(t in tokens for t in ("--hard", "-hard")):
                return False, ["git_reset_hard"]
            if "push" in tokens and any(t in tokens for t in ("--force", "-f", "--force-with-lease")):
                return False, ["git_force_push"]
            if "clean" in tokens and any(t.startswith("-") and "f" in t for t in tokens):
                return False, ["git_clean_force"]
            if ("checkout" in tokens and "--" in tokens and "." in tokens) or ("restore" in tokens and "." in tokens):
                return False, ["git_checkout_all"]

        # 3. Exfiltration detection
        if cmd_name in ("curl", "wget", "nc", "netcat", "socat") and (
            any("@" in tok and any(sec in tok for sec in (".env", "passphrase", "key", "token", "secret", "userContext", "identity")) for tok in tokens) or
            (any(tok in ("-d", "--data", "--data-raw", "--data-binary") for tok in tokens) and any(sec in command for sec in (".env", "passphrase")))
        ):
            return False, ["data_exfiltration_risk"]

        # 3b. Find destructive action detection (-delete, -exec rm)
        if (
            cmd_name == "find"
            and (
                any(t in ("-delete", "delete") for t in tokens)
                or ("-exec" in tokens and any(rm in tokens for rm in ("rm", "unlink", "truncate")))
            )
            and any(p in command for p in (".context", ".agent", "CANONICAL", "PROJECTS"))
        ):
            return False, ["find_destructive_call_on_protected_path"]

        # 3c. Moving/relocating protected memory directories
        if cmd_name == "mv" and len(tokens) >= 3:
            sources = tokens[1:-1]
            for src in sources:
                clean_src = src.strip("'\"").rstrip("/")
                if clean_src in (".context", ".agent") or clean_src.startswith((".context/", ".agent/")):
                    return False, ["moving_protected_memory_path"]

        # 4. Token-level destructive action detection
        destructive_verbs = {"rm", "unlink", "truncate", "shred", "dd"}
        if cmd_name in destructive_verbs or any(tok in ("rm", "delete", "truncate", "overwrite") for tok in tokens):
            red_flags.append("destructive_token")

        # Check dangerous flags in rm command
        if cmd_name == "rm":
            has_recursive = any(tok.startswith("-") and ("r" in tok or "R" in tok) for tok in tokens)
            has_force = any(tok.startswith("-") and "f" in tok for tok in tokens)
            if has_recursive and has_force:
                red_flags.append("recursive_force_delete")

        # 5. Path resolution & protected boundary check
        paths = self._extract_paths(tokens)
        for path_obj in paths:
            try:
                resolved = path_obj.resolve() if path_obj.is_absolute() else (self.workspace_root / path_obj).resolve()
            except Exception:
                resolved = (self.workspace_root / path_obj)

            context_dir = (self.workspace_root / ".context").resolve()
            agent_dir = (self.workspace_root / ".agent").resolve()

            if str(resolved) == str(context_dir) or str(resolved).startswith(str(context_dir) + "/"):
                red_flags.append("targets_context_memory")
            if str(resolved) == str(agent_dir) or str(resolved).startswith(str(agent_dir) + "/"):
                red_flags.append("targets_agent_config")
            if resolved == self.workspace_root or str(resolved) == "/":
                red_flags.append("targets_root_directory")

        # 6. Capability level evaluation
        if self.capability_level >= 4 and len(red_flags) > 0:
            red_flags.append("dangerous_capability_active")

        # 7. Cumulative Veto Decision
        veto = (
            "targets_root_directory" in red_flags
            or ("recursive_force_delete" in red_flags and ("targets_context_memory" in red_flags or "targets_agent_config" in red_flags))
            or len(red_flags) >= 2
        )

        return (not veto), red_flags

    def _extract_paths(self, tokens: list[str]) -> list[Path]:
        """Helper to extract non-flag tokens as potential file/directory paths."""
        paths = []
        for token in tokens[1:]:
            if token.startswith("-"):
                continue
            # Basic validation to skip subcommands like 'checkout', 'commit', etc.
            if "/" in token or token.startswith(".") or token in (".context", ".agent"):
                paths.append(Path(token))
        return paths
