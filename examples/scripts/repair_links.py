import sys
import os
import re
from pathlib import Path

# Add project root and src/ to sys.path
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT_DIR / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from athena.core.config import PROJECT_ROOT
WORKSPACE = PROJECT_ROOT
WORKSPACE_URI = f"file://{WORKSPACE}"
PROTOCOLS_DIR = WORKSPACE / ".agent" / "skills" / "protocols"

def build_protocol_map():
    """Build mapping from protocol filename to actual path."""
    protocol_map = {}
    for root, dirs, files in os.walk(PROTOCOLS_DIR):
        # Skip graphrag_env
        if 'graphrag_env' in root:
            continue
        for f in files:
            if f.endswith('.md'):
                full_path = Path(root) / f
                # Map both the basename and the old flat path
                protocol_map[f] = full_path
    return protocol_map

def fix_links_in_file(filepath: Path, protocol_map: dict) -> int:
    """Fix broken links in a single file. Returns count of fixes."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except:
        return 0
    
    original = content
    fixes = 0
    
    # Pattern: file:///.../.agent/skills/protocols/XX-name.md (old flat path)
    # Should become: file:///.../.agent/skills/protocols/category/XX-name.md
    
    def fix_protocol_link(match):
        nonlocal fixes
        full_match = match.group(0)
        filename = match.group(1)
        
        if filename in protocol_map:
            new_path = protocol_map[filename]
            rel_path = new_path.relative_to(WORKSPACE)
            new_link = f"{WORKSPACE_URI}/{rel_path}"
            if new_link != full_match:
                fixes += 1
                return new_link
        return full_match
    
    
    # Fix file:// links to protocols (regex needs dynamic handling if we want perfection, but strict old path logic is fine)
    # We will relax the pattern to catch any file://.../protocols
    pattern = r'file://.*?/\.agent/skills/protocols/([0-9]+-[a-z0-9-]+\.md)'
    content = re.sub(pattern, fix_protocol_link, content)
    
    # Also fix relative paths like ./agent/skills/protocols/XX-name.md
    def fix_relative_link(match):
        nonlocal fixes
        filename = match.group(1)
        if filename in protocol_map:
            new_path = protocol_map[filename]
            rel_path = new_path.relative_to(WORKSPACE)
            new_link = f"{WORKSPACE_URI}/{rel_path}"
            fixes += 1
            return new_link
        return match.group(0)
    
    pattern2 = r'\./agent/skills/protocols/([0-9]+-[a-z0-9-]+\.md)'
    content = re.sub(pattern2, fix_relative_link, content)
    
    # Fix .context/profile/ -> Winston/profile/ path migration
    old_profile_path = '.context/profile/'
    new_profile_path = 'Winston/profile/'
    if old_profile_path in content:
        count = content.count(old_profile_path)
        content = content.replace(old_profile_path, new_profile_path)
        fixes += count
    
    # Fix .context/psychology/ -> Winston/psychology/ path migration
    old_psych_path = '.context/psychology/'
    new_psych_path = 'Winston/psychology/'
    if old_psych_path in content:
        count = content.count(old_psych_path)
        content = content.replace(old_psych_path, new_psych_path)
        fixes += count
    
    # Fix archived session log paths: session_logs/2025-12-12-* -> session_logs/archive/2025-12-12-*
    import re as re_inner
    def fix_archived_session(m):
        nonlocal fixes
        date = m.group(1)
        session = m.group(2)
        # Only 2025-12-12 to 2025-12-18 are archived
        archived_dates = ['2025-12-12', '2025-12-13', '2025-12-14', '2025-12-15', 
                          '2025-12-16', '2025-12-17', '2025-12-18']
        if date in archived_dates:
            fixes += 1
            return f'session_logs/archive/{date}-session-{session}'
        return m.group(0)
    
    pattern_session = r'session_logs/(2025-12-\d{2})-session-(\d+)'
    content = re_inner.sub(pattern_session, fix_archived_session, content)
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
    
    return fixes

def main():
    print("=" * 60)
    print("  LINK REPAIR SCRIPT")
    print("=" * 60)
    
    # Build protocol map
    protocol_map = build_protocol_map()
    print(f"\n[INFO] Found {len(protocol_map)} protocols in themed folders")
    
    # Find all markdown files to scan
    total_fixes = 0
    files_fixed = 0
    
    for root, dirs, files in os.walk(WORKSPACE):
        # Skip certain directories
        skip = ['graphrag_env', '.git', 'node_modules', 'chroma_db', '__pycache__']
        if any(s in root for s in skip):
            continue
        
        for f in files:
            if f.endswith('.md'):
                filepath = Path(root) / f
                fixes = fix_links_in_file(filepath, protocol_map)
                if fixes > 0:
                    print(f"  ✓ Fixed {fixes} links in {filepath.relative_to(WORKSPACE)}")
                    total_fixes += fixes
                    files_fixed += 1
    
    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Files modified: {files_fixed}")
    print(f"  Links repaired: {total_fixes}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
