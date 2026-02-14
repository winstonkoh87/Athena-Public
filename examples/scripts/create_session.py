#!/usr/bin/env python3
"""
Create Session Log Script
===========================
Automates the creation of a new session log with the standard MoM template.

Usage: python3 create_session.py
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
SESSION_LOG_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"


def get_next_session_number() -> int:
    """Find the highest session number for today and return the next one."""
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(rf"^{today}-session-(\d+)\.md$")
    
    max_session = 0
    for file in SESSION_LOG_DIR.iterdir():
        match = pattern.match(file.name)
        if match:
            session_num = int(match.group(1))
            max_session = max(max_session, session_num)
    
    return max_session + 1


def create_session_log() -> Path:
    """Create a new session log with the standard template."""
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")
    session_num = get_next_session_number()
    
    filename = f"{today}-session-{session_num:02d}.md"
    filepath = SESSION_LOG_DIR / filename
    
    template = f"""# Session Log: {today} (Session {session_num:02d})

**Date**: {today}
**Time**: {time_now} - ...
**Focus**: ...

---

## 1. Agenda (The Plan)
- [ ] ...

---

## 2. Key Decisions & Insights (The Minutes)
*   **Decision**: ...
*   **Insight**: ...

---

## 3. Action Items (Next Steps)
| Action | Owner | Status |
|--------|-------|--------|
| ... | AI / User | Pending |

---

## 4. Session Performance Review (AAR)
*   **Self-Correction**: ...
*   **Calibration**: ...
*   **Verdict**: ...

---

## 5. Synthetic RLHF Log

### 5.1 User Model Updates
*   **Learned**: ...
*   **Updated in User_Profile.md**: No

### 5.2 AI Calibration
*   **What worked**: ...
*   **What to adjust**: ...

---

## 6. Artifacts & Outputs
*   **Created**: ...
*   **Modified**: ...

---

## 7. Cross-Session Links
*   **Continues from**: ...
*   **Related**: ...

---

## 8. Parking Lot (Deferred)
- [ ] ...

---

## Tagging
#session #...
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(template)
    
    return filepath


def main():
    print(f"{CYAN}Creating new session log...{RESET}")
    
    filepath = create_session_log()
    
    print(f"{GREEN}✅ Created: {filepath.relative_to(PROJECT_ROOT)}{RESET}")
    print(f"   Session: {filepath.stem}")


if __name__ == "__main__":
    main()
