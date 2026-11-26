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

    _SAFE_ENV_TEMPLATES = frozenset(
        {".env.example", ".env.sample", ".env.template", ".env.dist"}
    )
    _SECRET_BASENAMES = frozenset(
        {
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
    )
    _SECRET_EXTS = (".pem", ".key", ".p12", ".pfx")
    _SECRET_READERS = frozenset(
        {
            "cat",
            "head",
            "tail",
            "less",
            "more",
            "grep",
            "egrep",
            "fgrep",
            "rg",
            "sed",
            "awk",
            "bat",
            "strings",
            "base64",
            "xxd",
            "hexdump",
            "cp",
            "scp",
            "pbcopy",
            "xclip",
        }
    )
    _PATTERN_FIRST_READERS = frozenset({"grep", "egrep", "fgrep", "rg", "sed", "awk"})

    def __init__(self, workspace_root: Path | None = None, capability_level: int = 2):
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        self.capability_level = capability_level  # 1=read, 2=write, 3=admin, 4=dangerous

    @classmethod
    def _is_secret_target_token(cls, token: str) -> bool:
        clean = token.strip("'\"")
        if not clean or clean.startswith("-"):
            return False
        posix_lower = clean.replace("\\", "/").lower()
        base_lower = Path(posix_lower).name
        if base_lower == ".env" or (
            base_lower.startswith(".env.") and base_lower not in cls._SAFE_ENV_TEMPLATES
        ):
            return True
        if base_lower in cls._SECRET_BASENAMES or base_lower.endswith(cls._SECRET_EXTS):
            return True
        return any(seg in posix_lower for seg in ("/.aws/credentials", ".aws/credentials", "/.ssh/id_", ".ssh/id_"))

    @classmethod
    def _extract_reader_file_tokens(cls, cmd_name: str, tokens: list[str]) -> list[str]:
        positionals: list[str] = []
        has_explicit_pattern_flag = False
        skip_next = False
        flags_with_arg = {"-n", "-c", "-m", "-A", "-B", "-C", "-e", "-f", "--regexp", "--file"}
        for tok in tokens[1:]:
            if skip_next:
                skip_next = False
                continue
            if tok.startswith("-"):
                if tok in ("-e", "--regexp"):
                    has_explicit_pattern_flag = True
                if tok in flags_with_arg:
                    skip_next = True
                continue
            positionals.append(tok)

        if cmd_name in cls._PATTERN_FIRST_READERS and not has_explicit_pattern_flag and len(positionals) >= 2:
            return positionals[1:]
        if cmd_name in cls._PATTERN_FIRST_READERS and not has_explicit_pattern_flag:
            return []
        return positionals

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
                if any(x in py_code for x in ("open(", "read_text(", "read_bytes(", "Path(")):
                    py_lower = py_code.lower()
                    for safe in self._SAFE_ENV_TEMPLATES:
                        py_lower = py_lower.replace(safe, "")
                    if any(
                        sec in py_lower
                        for sec in (".env", "secrets.json", "id_rsa", "id_ed25519", "credentials.json", ".pem", ".key", ".p12")
                    ):
                        return False, ["secret_file_shell_access"]

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

        # 3d. Secret-file shell read protection across chained subcommands
        subcommands: list[list[str]] = []
        current_seg: list[str] = []
        for tok in tokens:
            if tok in ("&&", "||", ";", "|"):
                if current_seg:
                    subcommands.append(current_seg)
                    current_seg = []
            else:
                current_seg.append(tok)
        if current_seg:
            subcommands.append(current_seg)

        for seg in subcommands:
            seg_cmd = Path(seg[0]).name.lower()
            if seg_cmd in self._SECRET_READERS:
                for file_tok in self._extract_reader_file_tokens(seg_cmd, seg):
                    if self._is_secret_target_token(file_tok):
                        return False, ["secret_file_shell_access"]

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

        # 5. Path resolution & protected boundary check (deduplicated)
        context_flag = False
        agent_flag = False
        root_flag = False

        paths = self._extract_paths(tokens)
        for path_obj in paths:
            try:
                resolved = path_obj.resolve() if path_obj.is_absolute() else (self.workspace_root / path_obj).resolve()
            except Exception:
                resolved = (self.workspace_root / path_obj)

            context_dir = (self.workspace_root / ".context").resolve()
            agent_dir = (self.workspace_root / ".agent").resolve()

            if str(resolved) == str(context_dir) or str(resolved).startswith(str(context_dir) + "/"):
                context_flag = True
            if str(resolved) == str(agent_dir) or str(resolved).startswith(str(agent_dir) + "/"):
                agent_flag = True
            if resolved == self.workspace_root or str(resolved) == "/":
                root_flag = True

        if context_flag:
            red_flags.append("targets_context_memory")
        if agent_flag:
            red_flags.append("targets_agent_config")
        if root_flag:
            red_flags.append("targets_root_directory")

        # 6. Capability level evaluation
        if self.capability_level >= 4 and len(red_flags) > 0:
            red_flags.append("dangerous_capability_active")

        # 7. Cumulative Veto Decision
        has_destructive_action = bool(
            {"destructive_token", "recursive_force_delete", "dangerous_capability_active"}.intersection(red_flags)
        )
        has_protected_target = bool(
            {"targets_context_memory", "targets_agent_config"}.intersection(red_flags)
        )

        veto = (
            ("targets_root_directory" in red_flags and has_destructive_action)
            or ("recursive_force_delete" in red_flags and has_protected_target)
            or (has_destructive_action and has_protected_target)
            or len([f for f in red_flags if f not in ("targets_context_memory", "targets_agent_config")]) >= 2
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
