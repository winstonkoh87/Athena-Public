#!/usr/bin/env python3
"""
Protocol Scaffold Generator
Creates new protocol files from a standard template.
Auto-assigns protocol number and registers in SKILL_INDEX.
"""

import os
import sys
import re
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROTOCOLS_DIR = os.path.join(PROJECT_ROOT, ".agent", "skills", "protocols")
SKILL_INDEX_PATH = os.path.join(PROJECT_ROOT, ".agent", "skills", "SKILL_INDEX.md")

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

# Protocol Template
TEMPLATE = '''# {title}

> **Protocol**: {number}  
> **Created**: {date}  
> **Category**: {category}

---

## Summary

{summary}

---

## When to Use

**Trigger**: {trigger}

---

## The Protocol

### Core Principle

{principle}

### Steps

1. **Step 1**: [Description]
2. **Step 2**: [Description]
3. **Step 3**: [Description]

---

## Examples

### Example 1: [Scenario Name]

**Situation**: [Describe situation]

**Application**: [How protocol applies]

**Result**: [Outcome]

---

## Anti-Patterns

| ❌ Wrong | ✓ Correct |
|----------|-----------|
| [Common mistake] | [Correct approach] |

---

## Related Protocols

- [Related Protocol 1](related-protocol.md)
'''


def get_next_protocol_number():
    """Finds the next available protocol number."""
    if not os.path.exists(PROTOCOLS_DIR):
        return 1
    
    files = os.listdir(PROTOCOLS_DIR)
    numbers = []
    
    for f in files:
        match = re.match(r'^(\d+)-', f)
        if match:
            numbers.append(int(match.group(1)))
    
    return max(numbers) + 1 if numbers else 1


def slugify(text):
    """Converts text to slug format."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def add_to_index(filename, title, trigger):
    """Adds the new protocol to SKILL_INDEX.md."""
    if not os.path.exists(SKILL_INDEX_PATH):
        print(f"{YELLOW}⚠️  SKILL_INDEX.md not found. Skipping index update.{RESET}")
        return False
    
    entry = f"| **{title}** | `protocols/{filename}` | {trigger} |\n"
    
    with open(SKILL_INDEX_PATH, "a") as f:
        f.write(entry)
    
    return True


def create_protocol(title, category, summary, trigger, principle):
    """Creates a new protocol file."""
    number = get_next_protocol_number()
    slug = slugify(title)
    filename = f"{number:02d}-{slug}.md"
    filepath = os.path.join(PROTOCOLS_DIR, filename)
    
    # Check if file exists
    if os.path.exists(filepath):
        print(f"{RED}✗ File already exists: {filename}{RESET}")
        return None
    
    # Fill template
    content = TEMPLATE.format(
        title=title,
        number=number,
        date=datetime.now().strftime("%d %B %Y"),
        category=category,
        summary=summary,
        trigger=trigger,
        principle=principle
    )
    
    # Write file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename


def interactive_mode():
    """Interactive protocol creation."""
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}              📋 PROTOCOL SCAFFOLD GENERATOR                    {RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    print(f"{DIM}Create a new protocol file with auto-numbering and indexing.{RESET}\n")
    
    # Get inputs
    title = input(f"{BOLD}Protocol Title:{RESET} ").strip()
    if not title:
        print(f"{RED}✗ Title is required.{RESET}")
        return
    
    print(f"\n{DIM}Categories: Communication, Decision, Pattern, Insight, Framework{RESET}")
    category = input(f"{BOLD}Category:{RESET} ").strip() or "Framework"
    
    summary = input(f"{BOLD}One-line Summary:{RESET} ").strip() or "[To be written]"
    
    trigger = input(f"{BOLD}Trigger (when to use):{RESET} ").strip() or "[Define trigger condition]"
    
    principle = input(f"{BOLD}Core Principle:{RESET} ").strip() or "[To be defined]"
    
    print()
    
    # Create file
    filename = create_protocol(title, category, summary, trigger, principle)
    
    if filename:
        print(f"{GREEN}✓ Created: {filename}{RESET}")
        
        # Add to index
        if add_to_index(filename, title, trigger):
            print(f"{GREEN}✓ Added to SKILL_INDEX.md{RESET}")
        
        print(f"\n{DIM}File location: {PROTOCOLS_DIR}/{filename}{RESET}\n")


def cli_mode(args):
    """CLI protocol creation."""
    if len(args) < 2:
        print(f"{BOLD}Usage:{RESET} python protocol_scaffold.py <title> [category]")
        print(f"{DIM}       python protocol_scaffold.py --interactive{RESET}")
        return
    
    title = args[1]
    category = args[2] if len(args) > 2 else "Framework"
    
    filename = create_protocol(
        title=title,
        category=category,
        summary="[To be written]",
        trigger="[Define trigger condition]",
        principle="[To be defined]"
    )
    
    if filename:
        print(f"{GREEN}✓ Created: {filename}{RESET}")
        add_to_index(filename, title, "[Define trigger]")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            interactive_mode()
        else:
            cli_mode(sys.argv)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
