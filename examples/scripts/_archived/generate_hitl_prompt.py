#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add src to path
src_path = (Path(__file__).parent.parent.parent / "src").resolve()
sys.path.insert(0, str(src_path))

try:
    from parallel_orchestrator import TRACK_PROMPTS
except ImportError:
    # If we can't import, we just fall back
    pass


def generate_hitl_prompt(query: str, context: str) -> str:
    """Generates the giant prompt for manual Gemini Advanced pasting."""

    prompt = f"""You are executing the ULTRATHINK PARALLEL REASONING PROTOCOL.
I need you to independently simulate 4 distinct reasoning tracks to analyze my query.

# THE QUERY
{query}

# ADDITIONAL CONTEXT
{context}

---

# INSTRUCTIONS
Execute the following 4 tracks sequentially. Do NOT synthesize them yet. Just output each track's full analysis one after the other.

## TRACK A: DOMAIN EXPERT
Your role: Apply domain-specific frameworks and expertise.
1. Identify the domain(s) this problem belongs to
2. Apply relevant frameworks, mental models, and best practices
3. Provide structured analysis with clear recommendations
4. Ground your analysis in the user's actual constraints (Law #1: No Irreversible Ruin, Robustness > Efficiency, FX Trading using Barbell Strategy).

## TRACK B: ADVERSARIAL SKEPTIC
Your role: Challenge every premise, find every flaw, identify every risk.
1. Attack the problem statement itself - is this the right question?
2. Find logical fallacies, hidden assumptions, and blind spots
3. Identify failure modes, edge cases, and worst-case scenarios
4. Specifically check: Does this violate Law #1 (No Irreversible Ruin)?

## TRACK C: CROSS-DOMAIN PATTERN MATCHER
Your role: Find isomorphic patterns from completely different fields.
1. Abstract the core structure of the problem
2. Search your knowledge for similar patterns in unrelated domains (game theory, information theory, military strategy, biological systems)
3. Extract transferable insights from those analogies

## TRACK D: ZERO-POINT FIRST PRINCIPLES
Your role: Question the very nature and reality of the problem.
1. Strip away all assumptions - what remains?
2. Apply inversion: what if the opposite is true?
3. Ask: is there a game above this game?
4. Apply the RETO lens: Where on the Robustness-Efficiency frontier does this decision sit?

---

# FINAL SYNTHESIS
After you have completed all 4 tracks above, synthesize them into a final answer:
1. Identify where tracks AGREE
2. Identify where tracks CONFLICT (and resolve it)
3. Weigh Track B's concerns seriously
4. Produce a final recommendation with a Confidence Level (0-100%).
"""
    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HITL Ultrathink Prompt")
    parser.add_argument("query", help="The user query")
    parser.add_argument("--context-file", default="", help="Path to context file")

    args = parser.parse_args()

    context = ""
    if args.context_file:
        try:
            context = Path(args.context_file).read_text()
        except Exception as e:
            print(f"Error reading context file: {e}", file=sys.stderr)

    print(generate_hitl_prompt(args.query, context))
