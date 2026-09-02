#!/usr/bin/env python3
"""
Auto-File Insights — Generates case study skeletons from structured analysis output.

Usage:
    python3 auto_file_insights.py \
        --title "Market Analysis Title" \
        --domain "Market Analysis / Platform Economics" \
        --tags "#data-analysis #market" \
        --context "Brief context description" \
        --findings "Finding 1||Finding 2||Finding 3" \
        --patterns "Pattern 1||Pattern 2" \
        --relevance "How this relates to active projects"

Generates a numbered CS-NNN file in .context/memories/case_studies/.
"""

import argparse
import os
from datetime import datetime

CASE_STUDY_DIR = ".context/memories/case_studies"


def get_next_cs_number(base_dir: str) -> int:
    """Find the next available case study number."""
    cs_dir = os.path.join(base_dir, CASE_STUDY_DIR)
    if not os.path.exists(cs_dir):
        return 1

    max_num = 0
    for f in os.listdir(cs_dir):
        if f.startswith("CS-") and f.endswith(".md"):
            try:
                num = int(f.split("-")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass

    return max_num + 1


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:60]


def generate_case_study(
    title: str,
    domain: str,
    tags: str,
    context: str,
    findings: list,
    patterns: list,
    relevance: str,
    source: str = "Athena Data Engine analysis",
    cs_type: str = "Empirical Data Analysis",
    base_dir: str = ".",
) -> str:
    """Generate a case study markdown file and write it to disk."""

    cs_num = get_next_cs_number(base_dir)
    slug = slugify(title)
    filename = f"CS-{cs_num:03d}-{slug}.md"
    filepath = os.path.join(base_dir, CASE_STUDY_DIR, filename)

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Build findings section
    findings_md = ""
    for i, finding in enumerate(findings, 1):
        # Split on first colon for title/body
        if ":" in finding:
            f_title, f_body = finding.split(":", 1)
            findings_md += f"\n### {i}. {f_title.strip()}\n- {f_body.strip()}\n"
        else:
            findings_md += f"\n### {i}. Finding\n- {finding.strip()}\n"

    # Build patterns section
    patterns_md = ""
    for pattern in patterns:
        patterns_md += f"\n> **{pattern.strip()}**\n"

    content = f"""# CS-{cs_num:03d}: {title}

## Classification
- **Type**: {cs_type}
- **Domain**: {domain}
- **Date**: {date_str}
- **Source**: {source}
- **Tags**: {tags}

## Context
{context}

## Key Findings
{findings_md}

## Patterns Extracted
{patterns_md}

## Relevance to Active Projects
{relevance}
"""

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✅ Case study filed: {filepath}")
    print(f"   ID: CS-{cs_num:03d}")
    print(f"   Title: {title}")

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Auto-file analysis insights as Athena case studies",
    )
    parser.add_argument("--title", required=True, help="Case study title")
    parser.add_argument("--domain", default="Data Analysis", help="Domain classification")
    parser.add_argument("--tags", default="#data-analysis", help="Tags (space-separated, prefixed with #)")
    parser.add_argument("--context", required=True, help="Brief context/background")
    parser.add_argument("--findings", required=True, help="Key findings separated by ||")
    parser.add_argument("--patterns", default="", help="Extracted patterns separated by ||")
    parser.add_argument("--relevance", default="", help="Relevance to active projects")
    parser.add_argument("--source", default="Athena Data Engine analysis", help="Data source")
    parser.add_argument("--type", default="Empirical Data Analysis", help="Case study type")
    parser.add_argument("--base-dir", default=".", help="Base directory (Athena workspace root)")

    args = parser.parse_args()

    findings = [f.strip() for f in args.findings.split("||") if f.strip()]
    patterns = [p.strip() for p in args.patterns.split("||") if p.strip()] if args.patterns else []

    generate_case_study(
        title=args.title,
        domain=args.domain,
        tags=args.tags,
        context=args.context,
        findings=findings,
        patterns=patterns,
        relevance=args.relevance,
        source=args.source,
        cs_type=args.type,
        base_dir=args.base_dir,
    )


if __name__ == "__main__":
    main()
