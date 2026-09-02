#!/usr/bin/env python3
"""
Deep Research Agent
Multi-turn agentic search using Gemini with Google Search grounding.
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

RESEARCH_DIR = Path(".context/research")
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """You are a deep research agent. Your goal is to thoroughly research a topic by:

1. Breaking down the query into sub-questions
2. Searching for information on each sub-question
3. Synthesizing findings into a comprehensive report
4. Citing sources with URLs

For each research step, clearly state:
- What you're searching for
- What you found
- How it connects to the main query

Format your final output as a research report with:
- Executive Summary (3-5 sentences)
- Key Findings (bullet points)
- Detailed Analysis (organized by subtopic)
- Sources (list of URLs)
- Research Gaps (what couldn't be found)"""


def research(query: str, depth: int = 3) -> str:
    """Perform multi-turn research on a topic."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")

    client = genai.Client(api_key=api_key)

    print(f"🔍 Starting deep research: {query}")
    print(f"   Depth: {depth} iterations\n")

    # Initial research pass
    prompt = f"""{SYSTEM_PROMPT}

RESEARCH QUERY: {query}

Perform comprehensive research on this topic. Search for relevant information, analyze findings, and synthesize a complete report."""

    try:
        # Use model with search grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        return response.text
    except Exception as e:
        # Fallback to non-grounded if search unavailable
        print(f"⚠️ Search grounding unavailable: {e}")
        print("   Falling back to knowledge-based research...")

        fallback_prompt = f"""Based on your knowledge, provide a comprehensive analysis of:

{query}

Include:
- Key facts and concepts
- Different perspectives
- Practical implications
- Areas requiring further research

Note: This is knowledge-based, not live search."""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=fallback_prompt,
        )
        return (
            response.text
            + "\n\n*Note: This report is based on training data, not live search.*"
        )


def main():
    parser = argparse.ArgumentParser(description="Deep research agent with Gemini")
    parser.add_argument("query", nargs="*", help="Research query")
    parser.add_argument("--depth", type=int, default=3, help="Research depth (1-5)")
    parser.add_argument("--output", help="Save report to file")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    args = parser.parse_args()

    if args.interactive:
        print("🔬 Deep Research Agent (type 'exit' to quit)\n")
        while True:
            try:
                query = input("🔍 Research: ").strip()
                if query.lower() in ("exit", "quit", "q"):
                    break
                if not query:
                    continue
                print()
                report = research(query, args.depth)
                print(report + "\n")
            except KeyboardInterrupt:
                break
        print("\n👋")
        return

    if args.query:
        query = " ".join(args.query)
        report = research(query, args.depth)

        if args.output:
            output_path = Path(args.output)
        else:
            # Auto-generate filename
            safe_query = "".join(c if c.isalnum() or c == " " else "" for c in query)[
                :30
            ]
            safe_query = safe_query.replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = RESEARCH_DIR / f"research_{timestamp}_{safe_query}.md"

        full_report = f"# Research Report: {query}\n\n"
        full_report += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        full_report += report

        output_path.write_text(full_report, encoding="utf-8")
        print(f"\n✅ Report saved to {output_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
