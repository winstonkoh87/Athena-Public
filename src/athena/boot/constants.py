from pathlib import Path

# Paths
# Assuming src/athena/boot/constants.py -> ../../../.. = PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[3]

LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
SUPABASE_SEARCH_SCRIPT = PROJECT_ROOT / ".agent" / "scripts" / "smart_search.py"
PROTOCOLS_JSON = PROJECT_ROOT / ".agent" / "protocols.json"
CORE_IDENTITY = (
    PROJECT_ROOT / ".framework" / "v8.6-stable" / "modules" / "Core_Identity.md"
)
SAFE_BOOT_SCRIPT = PROJECT_ROOT / "safe_boot.sh"

# Configuration
BOOT_TIMEOUT_SECONDS = 90
EXPECTED_CORE_HASH = "9e1938392eb15e253bb06dbdfd87a247818e1828620f884f664f9dc99a370dc63f7098a0c813cf2c2b5d715e7aaef5fc"

# Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
