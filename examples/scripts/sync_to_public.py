#!/usr/bin/env python3
"""
sync_to_public.py (Blacklist Mode - Rich Examples)

Purpose:
    Sync content to Athena-Public with MAXIMUM coverage.
    Only EXCLUDE explicitly sensitive categories.
    - Maps internal folders to public `examples/` structure.
    - Sanitizes PII and Secrets.
    - Rewrites internal absolute links to relative public links.
    - NO PURGE: Only adds/updates files, never deletes.
"""

import os
import shutil
import re

# --- Configuration ---

SOURCE_ROOT = os.getcwd()
DEST_ROOT = os.path.join(SOURCE_ROOT, "Athena-Public")

# Directory Mappings (Source -> Dest relative to roots)
DIR_MAP = {
    ".agent/scripts": "examples/scripts",
    ".agent/workflows": "examples/workflows",
    # ".agent/skills/protocols": "examples/protocols", # DISABLED: Contains private strategies
    # ".context/memories/case_studies": "examples/case_studies", # DISABLED: Contains sensitive info
    ".framework": "examples/templates/framework_mirror",
    "src": "src",
}

# --- BLACKLIST (Explicit Exclusions Only) ---

# Protocol categories to EXCLUDE (sensitive/personal)
EXCLUDED_PROTOCOL_DIRS = {
    "trading",  # Financial strategies
    "psychology",  # Personal mental health
    "health",  # Medical/biometric
    "family",  # Personal relationships
    "singapore",  # Location-specific personal
}

# Specific files to EXCLUDE (known toxic/sensitive)
EXCLUDE_FILES = {
    ".DS_Store",
    "__pycache__",
    "session_telemetry.py",  # Contains API usage
    "audit_personality.py",  # Personal analysis
    "audit_velocity.py",  # Personal metrics
    "53-adventure-mode.md",  # TOXIC content
    "67-cross-pollination.md",  # TOXIC content
    "rename_audit.py",
    "rename_audit.log",
}

# Directories to always skip
EXCLUDE_DIRS = {
    "__pycache__",
    "chroma_db",
    "archive",
    "private",
    "metrics",
    "memories_archived",
    "graphrag",  # Local DB files
}

# Case studies to EXCLUDE (personal/client-specific)
EXCLUDED_CASE_STUDIES = {
    # Add specific CS-XXX filenames here if needed
    # e.g., "CS-999-personal-finance.md"
}

# PII / Secret Regex Patterns (Always applied)
PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_OPENAI_KEY]"),
    (r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_GOOGLE_KEY]"),
    (
        r'(?i)(api[_\-]?key)["\']\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        r'\1: "[REDACTED_GENERIC_KEY]"',
    ),
    (r"\b(\+?65[\s-]?)?[89]\d{3}[\s-]?\d{4}\b", "[REDACTED_PHONE_SG]"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
    # Winston-specific patterns
    (r"(?i)winston\s*koh", "[AUTHOR]"),
    (r"(?i)[AUTHOR]87", "[AUTHOR_HANDLE]"),
]


def sanitize_content(content):
    """Redact secrets and PII."""
    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content)
    return content


def fix_links(content, source_file_path, dest_file_path):
    """Rewrite absolute internal links to relative public links."""
    root_pattern = re.escape(SOURCE_ROOT)

    def replacer(match):
        full_link = match.group(0)
        label = match.group(1)
        url = match.group(2)

        clean_url = url.replace("file://", "")

        if clean_url.startswith(SOURCE_ROOT):
            rel_path_from_root = os.path.relpath(clean_url, SOURCE_ROOT)

            target_public_path = None

            for src_dir, dest_dir in DIR_MAP.items():
                if rel_path_from_root.startswith(src_dir):
                    sub_path = rel_path_from_root[len(src_dir) :].lstrip("/")

                    # Check if target is blacklisted
                    is_safe_link = True

                    if src_dir == ".agent/skills/protocols":
                        category = sub_path.split("/")[0] if "/" in sub_path else ""
                        if category in EXCLUDED_PROTOCOL_DIRS:
                            is_safe_link = False

                    if is_safe_link:
                        target_public_path = os.path.join(dest_dir, sub_path)
                    break

            if target_public_path:
                current_file_rel_public = os.path.relpath(dest_file_path, DEST_ROOT)
                current_dir_rel_public = os.path.dirname(current_file_rel_public)
                final_rel_link = os.path.relpath(
                    target_public_path, current_dir_rel_public
                )
                return f"[{label}]({final_rel_link})"
            else:
                return f"[{label}]([Private-Content])"

        return full_link

    link_regex = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    return link_regex.sub(replacer, content)


def is_allowed(rel_path, src_base_dir):
    """Check if a file is allowed (not blacklisted)."""
    filename = os.path.basename(rel_path)

    # Global file exclusions
    if filename in EXCLUDE_FILES or filename.startswith("."):
        return False

    # Protocol category check
    if src_base_dir == ".agent/skills/protocols":
        parts = rel_path.split(os.sep)
        if len(parts) > 0:
            category = parts[0]
            if category in EXCLUDED_PROTOCOL_DIRS:
                return False

    # Case study check
    if src_base_dir == ".context/memories/case_studies":
        if filename in EXCLUDED_CASE_STUDIES:
            return False

    # Everything else is allowed
    return True


def main():
    print("🚀 Starting BLACKLIST Sync (Rich Examples Mode)...")
    print("   Only explicitly sensitive content will be excluded.\n")

    files_synced = 0
    files_skipped = 0

    for src_dir_rel, dest_dir_rel in DIR_MAP.items():
        src_path = os.path.join(SOURCE_ROOT, src_dir_rel)
        dest_path = os.path.join(DEST_ROOT, dest_dir_rel)

        if not os.path.exists(src_path):
            continue

        print(f"🔄 Syncing: {src_dir_rel} -> {dest_dir_rel}")

        for root, dirs, files in os.walk(src_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            rel_in_block = os.path.relpath(root, src_path)

            for file in files:
                full_rel_path = os.path.join(rel_in_block, file)
                if full_rel_path.startswith("./"):
                    full_rel_path = full_rel_path[2:]

                if is_allowed(full_rel_path, src_dir_rel):
                    src_file_abs = os.path.join(root, file)
                    dest_file_abs = os.path.join(dest_path, full_rel_path)

                    os.makedirs(os.path.dirname(dest_file_abs), exist_ok=True)

                    try:
                        is_binary = file.endswith(
                            (
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".gif",
                                ".ico",
                                ".pdf",
                                ".zip",
                                ".pyc",
                            )
                        )
                        if is_binary:
                            shutil.copy2(src_file_abs, dest_file_abs)
                        else:
                            with open(
                                src_file_abs, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                            content = sanitize_content(content)
                            content = fix_links(content, src_file_abs, dest_file_abs)
                            with open(dest_file_abs, "w", encoding="utf-8") as f:
                                f.write(content)
                        files_synced += 1
                    except Exception as e:
                        print(f"   ❌ Error syncing {file}: {e}")
                else:
                    files_skipped += 1

    print(f"\n✅ Sync Complete!")
    print(f"   📦 Files synced: {files_synced}")
    print(f"   🚫 Files skipped (blacklisted): {files_skipped}")
    print(f"\n💡 Note: No purge performed. Existing files preserved.")


if __name__ == "__main__":
    main()
