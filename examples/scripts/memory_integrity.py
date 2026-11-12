import os
import re

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROTOCOLS_DIR = os.path.join(PROJECT_ROOT, ".agent", "skills", "protocols")
PUBLIC_PROTOCOLS_DIR = os.path.join(PROJECT_ROOT, "examples", "protocols")
SKILL_INDEX_PATH = os.path.join(PROJECT_ROOT, ".agent", "skills", "SKILL_INDEX.md")
_IGNORED_FILENAMES = {"README.md", "INDEX.md"}
_IGNORED_DIRNAMES = {"archive", "_archived"}

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def log(type, message):
    if type == "INFO":
        print(f"{GREEN}[INFO]{RESET} {message}")
    elif type == "WARN":
        print(f"{YELLOW}[WARN]{RESET} {message}")
    elif type == "ERROR":
        print(f"{RED}[ERROR]{RESET} {message}")

def _iter_protocol_dirs():
    """Return populated protocol directories in priority order."""
    candidates = [PROTOCOLS_DIR, PUBLIC_PROTOCOLS_DIR]
    fw_root = os.path.join(PROJECT_ROOT, ".framework")
    if os.path.isdir(fw_root):
        for entry in sorted(os.listdir(fw_root)):
            pdir = os.path.join(fw_root, entry, "protocols")
            if os.path.isdir(pdir):
                candidates.append(pdir)
    return [d for d in candidates if os.path.isdir(d)]


def scan_protocols():
    """Scans for protocol files and ensures they are in SKILL_INDEX.md"""
    protocol_dirs = _iter_protocol_dirs()
    if not protocol_dirs:
        log("ERROR", f"Protocols directory not found: {PROTOCOLS_DIR}")
        return

    # 1. Collect protocol files recursively, ignoring archives and index stubs
    actual_files: list[tuple[str, str]] = []
    for base_dir in protocol_dirs:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = sorted(d for d in dirs if d not in _IGNORED_DIRNAMES)
            for fname in sorted(files):
                if not fname.endswith(".md") or fname in _IGNORED_FILENAMES:
                    continue
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, base_dir)
                actual_files.append((rel_path, full_path))

    # 2. Read SKILL_INDEX.md
    if not os.path.exists(SKILL_INDEX_PATH):
        log("ERROR", f"SKILL_INDEX.md not found: {SKILL_INDEX_PATH}")
        return

    with open(SKILL_INDEX_PATH) as f:
        index_content = f.read()

    # 3. Check for missing protocols
    missing_protocols = []
    for rel_path, full_path in actual_files:
        fname = os.path.basename(full_path)
        if fname not in index_content:
            missing_protocols.append((rel_path, full_path))

    # 4. Fix missing protocols
    if missing_protocols:
        log("WARN", f"Found {len(missing_protocols)} protocols missing from index.")
        with open(SKILL_INDEX_PATH, "a") as f:
            f.write("\n")
            for rel_path, full_path in missing_protocols:
                fname = os.path.basename(full_path)
                title = fname.replace(".md", "").replace("-", " ").title()
                try:
                    with open(full_path) as pf:
                        first_line = pf.readline().strip()
                        if first_line.startswith("# "):
                            title = first_line[2:].strip()
                except Exception:
                    pass

                entry = f"| **{title}** | `protocols/{rel_path}` | Auto-indexed by Integrity Script |\n"
                f.write(entry)
                log("INFO", f"Added to Index: {rel_path}")
    else:
        log("INFO", "SKILL_INDEX is in sync with protocols folder.")

def validate_links():
    """Scans .md files for broken relative links"""
    log("INFO", "Starting Link Validation...")

    # Pattern to match [text](path)
    # Ignores http links, mailto, etc.
    link_pattern = re.compile(r'\[.*?\]\((?!http|mailto)(.*?)\)')

    broken_links = 0
    scanned_files = 0

    # Directories to scan
    scan_dirs = [
        os.path.join(PROJECT_ROOT, ".context"),
        os.path.join(PROJECT_ROOT, ".agent"),
        os.path.join(PROJECT_ROOT, ".framework")
    ]

    for root_dir in scan_dirs:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".md"):
                    scanned_files += 1
                    file_path = os.path.join(root, file)

                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    matches = link_pattern.findall(content)
                    for link in matches:
                        # cleanup anchors
                        clean_link = link.split('#')[0].strip()
                        if not clean_link:
                            continue

                        # Handle file:// prefix
                        if clean_link.startswith("file://"):
                            clean_link = clean_link.replace("file://", "")

                        # URL Decode (properties like %20)
                        try:
                            from urllib.parse import unquote
                            clean_link = unquote(clean_link)
                        except:
                            pass

                        # Absolute path handling (if user used absolute path in MD)
                        if clean_link.startswith("/Users/"):
                             target_path = clean_link
                        # Relative path handling
                        elif clean_link.startswith("/"):
                            # Assuming / relates to project root (rare in standard MD, but possible)
                            target_path = os.path.join(PROJECT_ROOT, clean_link[1:])
                        else:
                            target_path = os.path.join(os.path.dirname(file_path), clean_link)

                        # Check existence
                        if not os.path.exists(target_path):
                            log("WARN", f"Broken Link in {os.path.basename(file)}: '{link}' (Resolved: {target_path})")
                            broken_links += 1

    log("INFO", f"Scanned {scanned_files} files. Found {broken_links} broken links.")

if __name__ == "__main__":
    print("----------------------------------------------------------------")
    print("  MEMORY INTEGRITY SYSTEM (BIONIC AUDIT)  ")
    print("----------------------------------------------------------------")
    scan_protocols()
    validate_links()
    print("----------------------------------------------------------------")
