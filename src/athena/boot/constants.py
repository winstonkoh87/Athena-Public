
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
EXPECTED_CORE_HASH = "45b94d296c6d623203aafad440514a37ac58a7dfa137aac12b0f89af5b82929187aedc913e99aa0d2d9ee4b5f4b2cfbd"

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
