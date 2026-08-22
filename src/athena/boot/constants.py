from pathlib import Path

from athena.core.config import (
    AGENT_DIR,
    CONTEXT_DIR,
    FRAMEWORK_DIR,
    PROJECT_ROOT,
    SESSIONS_DIR,
)

LOGS_DIR = SESSIONS_DIR
SUPABASE_SEARCH_SCRIPT = AGENT_DIR / "scripts" / "smart_search.py"
PROTOCOLS_JSON = AGENT_DIR / "protocols.json"
CORE_IDENTITY = (
    FRAMEWORK_DIR / "v8.2-stable" / "modules" / "Core_Identity.md"
)
SAFE_BOOT_SCRIPT = PROJECT_ROOT / "safe_boot.sh"

# Memory Bank (Token Budget)
MEMORY_BANK_DIR = CONTEXT_DIR / "memory_bank"
BOOT_FILES = {
    "userContext.md": MEMORY_BANK_DIR / "userContext.md",
    "productContext.md": MEMORY_BANK_DIR / "productContext.md",
    "activeContext.md": MEMORY_BANK_DIR / "activeContext.md",
}

# Configuration
BOOT_TIMEOUT_SECONDS = 90
EXPECTED_CORE_HASH = "8f2e6f9e248951a84aa48e24e9bfd8239f76c6c8bffd44ee7c9cd854861a8820caed733aafa3b333e8851f372c854d4a"

# Colors (centralized) — re-exported for boot loaders/tests that import from here.
from athena.core.colors import (  # noqa: F401  (intentional re-export)
    BOLD,
    CYAN,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
)
