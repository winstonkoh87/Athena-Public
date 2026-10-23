"""
athena.core.config
==================

Centralized configuration and path discovery.
"""

import os
from pathlib import Path

# Global Cache for PROJECT_ROOT
_PROJECT_ROOT_CACHE: Path | None = None


def set_project_root(root: Path | str | None) -> Path:
    """Explicitly set or reset the project root path and update global path constants."""
    global _PROJECT_ROOT_CACHE, PROJECT_ROOT, AGENT_DIR, CONTEXT_DIR, FRAMEWORK_DIR
    global PUBLIC_DIR, SCRIPTS_DIR, MEMORIES_DIR, SESSIONS_DIR, MEMORY_DIR, STATE_DIR
    global MANIFEST_PATH, SYSTEM_LEARNINGS_FILE, USER_PROFILE_FILE, INPUTS_DIR, ATHENA_DB
    global TAG_INDEX_PATH, TAG_INDEX_AM_PATH, TAG_INDEX_NZ_PATH, CANONICAL_PATH, CORE_DIRS, EXTENDED_DIRS

    if root is not None:
        _PROJECT_ROOT_CACHE = Path(root).resolve()
    else:
        _PROJECT_ROOT_CACHE = None

    PROJECT_ROOT = get_project_root()
    AGENT_DIR = PROJECT_ROOT / ".agent"
    CONTEXT_DIR = PROJECT_ROOT / ".context"
    FRAMEWORK_DIR = PROJECT_ROOT / ".framework"
    PUBLIC_DIR = PROJECT_ROOT / "Athena-Public"
    SCRIPTS_DIR = AGENT_DIR / "scripts"
    MEMORIES_DIR = CONTEXT_DIR / "memories"
    SESSIONS_DIR = MEMORIES_DIR / "session_logs"
    MEMORY_DIR = PROJECT_ROOT / ".athena" / "memory"
    STATE_DIR = AGENT_DIR / "state"
    MANIFEST_PATH = STATE_DIR / "sync_manifest.json"
    SYSTEM_LEARNINGS_FILE = MEMORY_DIR / "SYSTEM_LEARNINGS.md"
    USER_PROFILE_FILE = MEMORY_DIR / "USER_PROFILE.yaml"
    INPUTS_DIR = CONTEXT_DIR / "inputs"
    ATHENA_DB = AGENT_DIR / "inputs" / "athena.db"
    TAG_INDEX_PATH = CONTEXT_DIR / "TAG_INDEX.md"
    TAG_INDEX_AM_PATH = CONTEXT_DIR / "TAG_INDEX_A-M.md"
    TAG_INDEX_NZ_PATH = CONTEXT_DIR / "TAG_INDEX_N-Z.md"
    CANONICAL_PATH = CONTEXT_DIR / "CANONICAL.md"

    CORE_DIRS = {
        "sessions": SESSIONS_DIR,
        "case_studies": MEMORIES_DIR / "case_studies",
        "protocols": AGENT_DIR / "skills" / "protocols",
        "capabilities": AGENT_DIR / "skills" / "capabilities",
        "workflows": AGENT_DIR / "workflows",
        "system_docs": FRAMEWORK_DIR / "v8.2-stable" / "modules",
    }
    EXTENDED_DIRS = [
        (PROJECT_ROOT / "docs", "system_docs"),
        (PROJECT_ROOT / "examples", "system_docs"),
        (PROJECT_ROOT / ".athena", "system_docs"),
        (CONTEXT_DIR / "research", "case_studies"),
        (CONTEXT_DIR / "specs", "system_docs"),
    ]

    # Invalidate session service singleton if active so it rebinds to new sessions_dir
    try:
        import athena.lifecycle.session_service as ss_module
        ss_module._session_service = None
    except Exception:
        pass

    # Synchronize boot constants if loaded
    try:
        import sys
        if "athena.boot.constants" in sys.modules:
            bconst = sys.modules["athena.boot.constants"]
            bconst.PROJECT_ROOT = PROJECT_ROOT
            bconst.AGENT_DIR = AGENT_DIR
            bconst.CONTEXT_DIR = CONTEXT_DIR
            bconst.FRAMEWORK_DIR = FRAMEWORK_DIR
            bconst.SESSIONS_DIR = SESSIONS_DIR
            bconst.LOGS_DIR = SESSIONS_DIR
            bconst.SUPABASE_SEARCH_SCRIPT = AGENT_DIR / "scripts" / "smart_search.py"
            bconst.PROTOCOLS_JSON = AGENT_DIR / "protocols.json"
            bconst.CORE_IDENTITY = FRAMEWORK_DIR / "v8.2-stable" / "modules" / "Core_Identity.md"
            bconst.SAFE_BOOT_SCRIPT = PROJECT_ROOT / "safe_boot.sh"
            bconst.MEMORY_BANK_DIR = CONTEXT_DIR / "memory_bank"
            bconst.BOOT_FILES = {
                "userContext.md": bconst.MEMORY_BANK_DIR / "userContext.md",
                "productContext.md": bconst.MEMORY_BANK_DIR / "productContext.md",
                "activeContext.md": bconst.MEMORY_BANK_DIR / "activeContext.md",
            }
    except Exception:
        pass

    return PROJECT_ROOT


def get_project_root() -> Path:
    """
    Discover project root with precedence:
    1. Cached value (_PROJECT_ROOT_CACHE) if explicitly set
    2. Environment variable ATHENA_ROOT
    3. Look up from Path.cwd() for .athena_root or .context markers
    4. Path.cwd() if it contains pyproject.toml or .git
    5. Developer fallback: walk up from __file__ to pyproject.toml
    """
    global _PROJECT_ROOT_CACHE
    if _PROJECT_ROOT_CACHE is not None:
        return _PROJECT_ROOT_CACHE

    # 1. Environment variable override
    env_root = os.getenv("ATHENA_ROOT")
    if env_root:
        _PROJECT_ROOT_CACHE = Path(env_root).resolve()
        return _PROJECT_ROOT_CACHE

    # 2. Look up from CWD for workspace root markers (.athena_root, .context)
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".athena_root").exists():
            _PROJECT_ROOT_CACHE = parent
            return _PROJECT_ROOT_CACHE
        if (parent / ".context").exists() and (parent / ".agent").exists():
            _PROJECT_ROOT_CACHE = parent
            return _PROJECT_ROOT_CACHE

    for parent in [cwd, *cwd.parents]:
        if (parent / ".context").exists():
            _PROJECT_ROOT_CACHE = parent
            return _PROJECT_ROOT_CACHE

    # 3. Check if CWD itself is a project root
    if (cwd / "pyproject.toml").exists() or (cwd / ".git").exists():
        _PROJECT_ROOT_CACHE = cwd
        return _PROJECT_ROOT_CACHE

    # 4. Fallback for internal package development: walk up from __file__
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / ".context").exists():
            _PROJECT_ROOT_CACHE = parent
            return _PROJECT_ROOT_CACHE

    _PROJECT_ROOT_CACHE = cwd
    return _PROJECT_ROOT_CACHE


PROJECT_ROOT = get_project_root()

# Key Directories
AGENT_DIR = PROJECT_ROOT / ".agent"
CONTEXT_DIR = PROJECT_ROOT / ".context"
FRAMEWORK_DIR = PROJECT_ROOT / ".framework"
PUBLIC_DIR = PROJECT_ROOT / "Athena-Public"
SCRIPTS_DIR = AGENT_DIR / "scripts"
MEMORIES_DIR = CONTEXT_DIR / "memories"
SESSIONS_DIR = MEMORIES_DIR / "session_logs"
MEMORY_DIR = PROJECT_ROOT / ".athena" / "memory"
STATE_DIR = AGENT_DIR / "state"
MANIFEST_PATH = STATE_DIR / "sync_manifest.json"
SYSTEM_LEARNINGS_FILE = MEMORY_DIR / "SYSTEM_LEARNINGS.md"
USER_PROFILE_FILE = MEMORY_DIR / "USER_PROFILE.yaml"
INPUTS_DIR = CONTEXT_DIR / "inputs"
# Unified path for the local SQLite metadata index (written by athenad, read by search).
# Bug fix (S870): athenad.py wrote to .agent/inputs/athena.db while search.py read from
# .context/inputs/athena.db (which never existed). Both now use this single constant.
ATHENA_DB = AGENT_DIR / "inputs" / "athena.db"

# === UNIFIED MEMORY CONFIGURATION ===
# These directories are the "Active Memory" for VectorRAG and local search.

CORE_DIRS = {
    "sessions": SESSIONS_DIR,
    "case_studies": MEMORIES_DIR / "case_studies",
    "protocols": AGENT_DIR / "skills" / "protocols",
    "capabilities": AGENT_DIR / "skills" / "capabilities",
    "workflows": AGENT_DIR / "workflows",
    "system_docs": FRAMEWORK_DIR / "v8.2-stable" / "modules",
}

# Extended Memory (Silos mapped to logical tables)
EXTENDED_DIRS = [
    (PROJECT_ROOT / "docs", "system_docs"),
    (PROJECT_ROOT / "examples", "system_docs"),
    (PROJECT_ROOT / ".athena", "system_docs"),
    (CONTEXT_DIR / "research", "case_studies"),
    (CONTEXT_DIR / "specs", "system_docs"),
]


def get_active_memory_paths():
    """Returns a deduplicated list of all active memory directory Paths."""
    paths = [p for p in CORE_DIRS.values() if p.exists()]
    paths.extend([p for p, _ in EXTENDED_DIRS if p.exists()])
    return sorted(set(paths))


# Key Files (Sharded for token efficiency)
TAG_INDEX_PATH = (
    CONTEXT_DIR / "TAG_INDEX.md"
)  # Legacy monolithic (for backwards compat)
TAG_INDEX_AM_PATH = CONTEXT_DIR / "TAG_INDEX_A-M.md"
TAG_INDEX_NZ_PATH = CONTEXT_DIR / "TAG_INDEX_N-Z.md"
CANONICAL_PATH = CONTEXT_DIR / "CANONICAL.md"


def get_current_session_log() -> Path | None:
    """
    Find the most recent session log file.
    Matches both legacy (YYYY-MM-DD-session-XX.md and YYYY-MM-DD-session-SXX.md) and new (SXXX_YYYYMMDD_desc.md) formats.
    """
    if not SESSIONS_DIR.exists():
        return None

    import re

    pattern_legacy = re.compile(r"^(\d{4}-\d{2}-\d{2})-session-(S?\d{2,4})\.md$")
    pattern_new = re.compile(r"^S(\d{3})_(\d{8})_.*\.md$")
    session_files = []

    for f in SESSIONS_DIR.glob("*.md"):
        match_leg = pattern_legacy.match(f.name)
        if match_leg:
            date_str, session_num_str = match_leg.groups()
            # Strip potential 'S' prefix before converting to integer
            session_num = int(session_num_str.lstrip('S'))
            session_files.append((date_str, session_num, f))
            continue

        match_new = pattern_new.match(f.name)
        if match_new:
            session_num_str, date_raw = match_new.groups()
            date_str = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
            session_files.append((date_str, int(session_num_str), f))

    if not session_files:
        return None

    # Sort by date then session number descending
    session_files.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return session_files[0][2]
