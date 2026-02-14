#!/usr/bin/env python3
"""
athena.tools.content_gen
=======================
Automated Marketing Asset Generator based on SEO Strategy.
Implements Outcome Positioning (CS-240) and Visceral Copywriting (Protocol 272).
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List

# Fix sys.path for SDK access
SDK_PATH = Path(__file__).resolve().parent.parent.parent
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.config import PROJECT_ROOT

# Config
SEO_MASTER = PROJECT_ROOT / ".context" / "marketing" / "SEO_STRATEGY_MASTER.md"
OUTPUT_DIR = PROJECT_ROOT / ".context" / "marketing" / "generated"

PROMPT_TEMPLATE = """
Act as a world-class Direct Response Copywriter (Hormozi / Ogilvy style).
Target Keyword: "{keyword}"

Generate 3 variations of marketing copy:

1. [CAROUSELL] - Outcome-focused, urgency-driven, price-anchored ($1500 upfront / $1500 on delivery).
2. [LINKEDIN] - Authority-focused, mentioning "Bionic Unit" and "Agentic Workflows".
3. [TWITTER/X] - Insight-driven thread hook.

Constraint: Follow Protocol 272 (Visceral triggers) and CS-240 (Outcome framing).
"""

def get_keywords() -> List[str]:
    """Parse keywords from SEO_STRATEGY_MASTER.md."""
    if not SEO_MASTER.exists():
        return []
    
    content = SEO_MASTER.read_text(encoding="utf-8")
    # Matches bullet points like "- `Keyword`"
    keywords = re.findall(r'- `([^`]+)`', content)
    return keywords

def generate_assets(keyword: str):
    """
    Generate assets for a keyword.
    Note: In a full implementation, this calls the LLM. 
    In this SDK shim, we provide a placeholder integration point.
    """
    print(f"🛠️  Generating assets for: {keyword}")
    
    # Placeholder for actual LLM call (e.g. via athena.core.models)
    # Since this is a local tool, we output the prompt for the user to use in the AI chat
    # or implement a simple mock.
    
    output_file = OUTPUT_DIR / f"{keyword.replace(' ', '_').lower()}.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # We output the specific prompt to the user as the 'generated' asset for now,
    # effectively becoming a 'Prompt Scaffolder' for marketing efforts.
    
    final_prompt = PROMPT_TEMPLATE.replace("{keyword}", keyword)
    
    output_file.write_text(final_prompt, encoding="utf-8")
    print(f"  ✅ Prompt Scaffolded: {output_file.relative_to(PROJECT_ROOT)}")

def main():
    parser = argparse.ArgumentParser(description="Athena Marketing Content Generator")
    parser.add_argument("--keyword", help="Specific keyword to target")
    parser.add_argument("--all", action="store_true", help="Generate for all keywords in SEO Master")
    args = parser.parse_args()

    if args.keyword:
        generate_assets(args.keyword)
    elif args.all:
        keywords = get_keywords()
        for kw in keywords:
            generate_assets(kw)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
