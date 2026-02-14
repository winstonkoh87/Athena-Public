import os
import re
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE_ROOT = Path(".")
# Patterns for common keys
PATTERNS = {
    "OpenAI": r"sk-[a-zA-Z0-9]{48}",
    "Anthropic": r"sk-ant-[a-zA-Z0-9]{80,}",
    "Gemini/Google": r"AIza[0-9A-Za-z-_]{35}",
    "GitHub": r"ghp_[a-zA-Z0-9]{36}",
    "Generic Private Key": r"-----BEGIN PRIVATE KEY-----",
}

# Directories to ignore
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".agent/clawbot",
    "__pycache__",
    ".DS_Store",
}

# Files to ignore (e.g., this script itself)
IGNORE_FILES = {
    "nurse_security.py",
    ".env",  # We expect secrets here
    "secrets.js",
}


def scan_file(file_path):
    try:
        content = file_path.read_text(errors="ignore")
        findings = []
        for name, pattern in PATTERNS.items():
            if re.search(pattern, content):
                findings.append(name)
        return findings
    except Exception:
        return []


def main():
    print(f"🔒 Nurse Sentry: Scanning {WORKSPACE_ROOT.resolve()} for leaks...")
    leaks = []

    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Filter directories inplace
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES:
                continue

            path = Path(root) / file

            # Skip binary/large files by extension heuristic
            if path.suffix in [".png", ".jpg", ".pyc", ".zip", ".enc"]:
                continue

            findings = scan_file(path)
            if findings:
                leaks.append((path, findings))

    # Report
    print(f"\n🔍 Scan Complete.")
    if leaks:
        print(f"⚠️  WARNING: POTENTIAL LEAKS FOUND IN {len(leaks)} FILES:")
        for path, what in leaks:
            print(f"   - {path} : {what}")
        print("\nRecommendation: Review these files immediately.")
    else:
        print("✅ No hardcoded secrets found in source code.")


if __name__ == "__main__":
    main()
