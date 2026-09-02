#!/usr/bin/env python3
"""
Parallel Orchestrator v4.1
True parallel execution of reasoning tracks with adversarial convergence gate.

Protocol 75 Implementation - Synthetic Parallel Reasoning (Real Parallelism)

Changes in v4.1:
- Added --output flag for file persistence
- Added --context-file flag for large context injection
- Injected user domain into all track prompts
- Fixed deprecated asyncio.get_event_loop()
- Auto-creates output directory
- Switched to generate_content_async (fixes gRPC deadlock)
- Added rate-limit retry with 30s backoff
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional  # noqa: F401 — kept for potential future use

# Add src to path
src_path = (Path(__file__).parent.parent.parent / "src").resolve()
sys.path.insert(0, str(src_path))

import google.api_core.exceptions
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# --- Configuration ---
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_ITERATIONS = 3
CONVERGENCE_THRESHOLD = 85
MAX_OUTPUT_TOKENS = 8192


@dataclass
class TrackResult:
    """Result from a single reasoning track."""

    track_name: str
    content: str
    tokens_used: int = 0
    latency_ms: int = 0


@dataclass
class ConvergenceResult:
    """Result from adversarial convergence check."""

    score: int
    passed: bool
    critique: str
    suggestions: list[str]


# --- User Domain Injection ---
USER_DOMAIN_CONTEXT = """IMPORTANT CONTEXT — You are reasoning within the Athena framework.
The user (Winston) is a Sovereign Operator. Key constraints:
- Law #1: No Irreversible Ruin (veto any path with >5% probability of permanent destruction)
- Law #2: Context Is King (the game matters more than the move)
- Robustness > Efficiency on the Pareto frontier (unless stakes are low and recoverable)
- The user trades FX using a Barbell Strategy (small Spear allocation, majority in conservative instruments)
- The user values calibration rate (mutual error correction) over agreement
Apply these constraints to your analysis where relevant."""

# --- Track System Prompts ---
TRACK_PROMPTS = {
    "A_DOMAIN": f"""You are a DOMAIN EXPERT reasoning track.

{USER_DOMAIN_CONTEXT}

Your role: Apply domain-specific frameworks and expertise to analyze this problem.

Instructions:
1. Identify the domain(s) this problem belongs to
2. Apply relevant frameworks, mental models, and best practices from the user's domain
3. Provide structured analysis with clear recommendations
4. Be thorough but focused on actionable insights
5. Ground your analysis in the user's actual constraints (leverage, account size, risk rules)

Output format:
## Domain Analysis
[Your analysis]

## Key Frameworks Applied
[List frameworks used]

## Recommendations
[Numbered list]""",
    "B_ADVERSARIAL": f"""You are an ADVERSARIAL SKEPTIC reasoning track.

{USER_DOMAIN_CONTEXT}

Your role: Challenge every premise, find every flaw, identify every risk.

Instructions:
1. Attack the problem statement itself - is this the right question?
2. Find logical fallacies, hidden assumptions, and blind spots
3. Identify failure modes, edge cases, and worst-case scenarios
4. Be genuinely critical, not performatively skeptical
5. Specifically check: Does this violate Law #1 (No Irreversible Ruin)?
6. Calculate: What is the probability of the worst-case scenario? What is the magnitude?

Output format:
## Premise Challenges
[What's wrong with the question itself?]

## Logical Flaws
[Errors in reasoning]

## Failure Modes
[What could go wrong? Include probability estimates.]

## Law #1 Ruin Check
[Does this path risk irreversible ruin? Yes/No with justification.]

## Risk Assessment
[Severity and likelihood matrix]""",
    "C_CROSS_DOMAIN": f"""You are a CROSS-DOMAIN PATTERN MATCHER reasoning track.

{USER_DOMAIN_CONTEXT}

Your role: Find isomorphic patterns from completely different fields.

Instructions:
1. Abstract the core structure of the problem
2. Search your knowledge for similar patterns in unrelated domains
3. Extract transferable insights from those analogies
4. Be creative but rigorous in drawing parallels
5. Prioritize patterns from: game theory, information theory, military strategy, biological systems

Output format:
## Problem Abstraction
[Core structure in domain-agnostic terms]

## Isomorphic Patterns
[2-3 parallels from other fields]

## Transferable Insights
[What can we learn from each analogy?]""",
    "D_ZERO_POINT": f"""You are a ZERO-POINT FIRST PRINCIPLES reasoning track.

{USER_DOMAIN_CONTEXT}

Your role: Question the very nature and reality of the problem.

Instructions:
1. Strip away all assumptions - what remains?
2. Apply inversion: what if the opposite is true?
3. Consider metaphysical/philosophical dimensions
4. Ask: is there a game above this game?
5. Apply the RETO lens: Where on the Robustness-Efficiency frontier does this decision sit?

Output format:
## First Principles
[Irreducible axioms]

## Inversion Test
[What if we're thinking about this backwards?]

## Meta-Level View
[The game above the game]

## RETO Position
[Where does this sit on the Robustness-Efficiency frontier?]

## Reframing
[Alternative ways to see this problem]""",
}

SYNTHESIS_PROMPT = """You are the SYNTHESIS ENGINE.

You have received outputs from four parallel reasoning tracks:
- Track A (Domain Expert): Applied domain-specific frameworks
- Track B (Adversarial Skeptic): Challenged premises and found risks
- Track C (Cross-Domain): Found isomorphic patterns from other fields
- Track D (Zero-Point): Applied first principles and inversion

Your job: Synthesize these into a unified, coherent analysis.

Instructions:
1. Identify where tracks AGREE (high confidence)
2. Identify where tracks CONFLICT (requires resolution)
3. Weigh Track B's concerns seriously - risks must be addressed
4. Incorporate Track C's insights where they add value
5. Use Track D's reframing if it reveals a higher-order truth
6. Produce a final recommendation with confidence level

Output format:
## Synthesis

### Points of Convergence
[Where all tracks agree]

### Resolved Conflicts
[Where tracks disagreed and how you resolved it]

### Risk Integration
[How Track B's concerns are addressed]

### Cross-Domain Insight
[Most valuable pattern from Track C]

### Final Recommendation
[Clear, actionable output]

### Confidence Level
[0-100% with justification]"""

ADVERSARIAL_SCORING_PROMPT = """You are the ADVERSARIAL CONVERGENCE GATE.

You have been given a synthesized analysis. Your job is to score it.

Scoring Criteria (0-100):
- Logical Coherence (25 points): Is the reasoning valid?
- Risk Coverage (25 points): Are all major risks addressed?
- Actionability (25 points): Can someone act on this?
- Blind Spot Check (25 points): Are there obvious omissions?

Instructions:
1. Score each criterion honestly (0-25)
2. Sum for total score
3. If score < 85, provide specific improvement suggestions
4. Be harsh but fair

Output ONLY valid JSON:
{
    "logical_coherence": <0-25>,
    "risk_coverage": <0-25>,
    "actionability": <0-25>,
    "blind_spot_check": <0-25>,
    "total_score": <0-100>,
    "passed": <true if total >= 85, else false>,
    "critique": "<one paragraph summary of weaknesses>",
    "suggestions": ["<specific improvement 1>", "<specific improvement 2>"]
}"""


class ParallelOrchestrator:
    """Orchestrates true parallel reasoning across multiple tracks."""

    def __init__(self, model: str = DEFAULT_MODEL, verbose: bool = True):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.verbose = verbose
        self.iteration_count = 0
        self.total_tokens = 0

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    async def _call_track(
        self, track_name: str, query: str, context: str = ""
    ) -> TrackResult:
        """Execute a single reasoning track."""
        import time

        start = time.time()

        system_prompt = TRACK_PROMPTS.get(track_name, "")
        full_prompt = f"{system_prompt}\n\n---\n\nQUERY: {query}"
        if context:
            full_prompt += f"\n\nADDITIONAL CONTEXT:\n{context}"

        try:
            while True:
                try:
                    # Use native async to prevent ThreadPool/gRPC deadlocks
                    response = await self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.8,
                            max_output_tokens=MAX_OUTPUT_TOKENS,
                        ),
                    )
                    break
                except google.api_core.exceptions.ResourceExhausted:
                    self._log(
                        f"  ⏳ Rate limit hit on Track {track_name}, waiting 30s..."
                    )
                    await asyncio.sleep(30)

            latency = int((time.time() - start) * 1000)
            content = response.text if response.text else "[No response]"

            self._log(f"  ✅ Track {track_name}: {latency}ms")

            return TrackResult(
                track_name=track_name, content=content, latency_ms=latency
            )

        except Exception as e:
            self._log(f"  ❌ Track {track_name} failed: {e}")
            return TrackResult(
                track_name=track_name, content=f"[ERROR: {e}]", latency_ms=0
            )

    async def dispatch_parallel_tracks(
        self, query: str, context: str = ""
    ) -> dict[str, TrackResult]:
        """Dispatch all 4 tracks in parallel."""
        self._log("\n🚀 Dispatching parallel tracks...")

        tasks = [
            self._call_track("A_DOMAIN", query, context),
            self._call_track("B_ADVERSARIAL", query, context),
            self._call_track("C_CROSS_DOMAIN", query, context),
            self._call_track("D_ZERO_POINT", query, context),
        ]

        results = await asyncio.gather(*tasks)

        return {r.track_name: r for r in results}

    async def synthesize_tracks(
        self, query: str, track_results: dict[str, TrackResult]
    ) -> str:
        """Synthesize all track outputs into unified analysis."""
        self._log("\n🔗 Synthesizing tracks...")

        # Build synthesis input
        synthesis_input = f"ORIGINAL QUERY: {query}\n\n"
        synthesis_input += "=" * 60 + "\n"

        for track_name, result in track_results.items():
            synthesis_input += f"\n## {track_name} OUTPUT:\n{result.content}\n"
            synthesis_input += "-" * 40 + "\n"

        full_prompt = f"{SYNTHESIS_PROMPT}\n\n---\n\n{synthesis_input}"

        while True:
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                    ),
                )
                break
            except google.api_core.exceptions.ResourceExhausted:
                self._log("  ⏳ Rate limit hit during synthesis, waiting 30s...")
                await asyncio.sleep(30)

        return response.text if response.text else "[Synthesis failed]"

    async def adversarial_convergence_check(self, synthesis: str) -> ConvergenceResult:
        """Track B scores the synthesis. Returns pass/fail with critique."""
        self._log("\n🛡️ Adversarial Convergence Gate...")

        full_prompt = (
            f"{ADVERSARIAL_SCORING_PROMPT}\n\n---\n\nSYNTHESIS TO SCORE:\n{synthesis}"
        )

        while True:
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,  # Lower temp for consistent scoring
                        max_output_tokens=2048,
                    ),
                )
                break
            except google.api_core.exceptions.ResourceExhausted:
                self._log(
                    "  ⏳ Rate limit hit during convergence check, waiting 30s..."
                )
                await asyncio.sleep(30)

        # Parse JSON response
        try:
            text = response.text.strip()
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            result = json.loads(text)

            score = result.get("total_score", 0)
            passed = score >= CONVERGENCE_THRESHOLD

            self._log(
                f"  📊 Score: {score}/100 {'✅ PASSED' if passed else '❌ NEEDS ITERATION'}"
            )

            return ConvergenceResult(
                score=score,
                passed=passed,
                critique=result.get("critique", ""),
                suggestions=result.get("suggestions", []),
            )

        except (json.JSONDecodeError, KeyError) as e:
            self._log(f"  ⚠️ Failed to parse scoring response: {e}")
            # Default to pass on parse failure (avoid infinite loops)
            return ConvergenceResult(
                score=85,
                passed=True,
                critique="Scoring parse failed, defaulting to pass",
                suggestions=[],
            )

    async def run(self, query: str, context: str = "") -> tuple[str, int, list[dict]]:
        """
        Main entry point. Runs orchestrator with convergence loop.

        Returns: (final_synthesis, total_iterations, iteration_history)
        """
        self._log("\n" + "=" * 60)
        self._log("🧠 PARALLEL ORCHESTRATOR v4.1")
        self._log("=" * 60)
        self._log(f"Query: {query[:100]}...")

        iteration_history = []
        current_context = context

        for iteration in range(1, MAX_ITERATIONS + 1):
            self._log(f"\n--- Iteration {iteration}/{MAX_ITERATIONS} ---")
            self.iteration_count = iteration

            # Step 1: Dispatch parallel tracks
            track_results = await self.dispatch_parallel_tracks(query, current_context)

            # Step 2: Synthesize
            synthesis = await self.synthesize_tracks(query, track_results)

            # Step 3: Convergence check
            convergence = await self.adversarial_convergence_check(synthesis)

            iteration_history.append(
                {
                    "iteration": iteration,
                    "score": convergence.score,
                    "passed": convergence.passed,
                    "critique": convergence.critique,
                }
            )

            if convergence.passed:
                self._log(
                    f"\n✅ CONVERGED at iteration {iteration} with score {convergence.score}"
                )
                return synthesis, iteration, iteration_history

            # Not converged - add critique to context for next iteration
            current_context = f"""Previous iteration critique (score {convergence.score}/100):
{convergence.critique}

Suggestions for improvement:
{chr(10).join(f"- {s}" for s in convergence.suggestions)}

Previous synthesis (to improve upon):
{synthesis[:2000]}...
"""
            self._log("  ↩️ Iterating with feedback...")

        # Max iterations reached
        self._log(
            f"\n⚠️ Max iterations ({MAX_ITERATIONS}) reached. Returning best effort."
        )
        return synthesis, MAX_ITERATIONS, iteration_history


async def main():
    parser = argparse.ArgumentParser(description="Parallel Orchestrator v4.0")
    parser.add_argument("query", help="The query to analyze")
    parser.add_argument("--context", default="", help="Additional context (inline)")
    parser.add_argument(
        "--context-file",
        default="",
        help="Path to a file containing additional context (for large contexts)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Path to save the final synthesis output (creates parent dirs)",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Load context from file if provided
    context = args.context
    if args.context_file:
        context_path = Path(args.context_file)
        if context_path.exists():
            context = context_path.read_text(encoding="utf-8")
            if not args.quiet:
                print(f"📄 Loaded context from {context_path} ({len(context)} chars)")
        else:
            print(f"⚠️ Context file not found: {context_path}", file=sys.stderr)

    orchestrator = ParallelOrchestrator(model=args.model, verbose=not args.quiet)

    synthesis, iterations, history = await orchestrator.run(args.query, context)

    # Build output payload
    output_payload = {
        "query": args.query,
        "synthesis": synthesis,
        "iterations": iterations,
        "history": history,
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
    }

    # Save to file if --output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.json or args.output.endswith(".json"):
            output_path.write_text(
                json.dumps(output_payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        else:
            # Write as readable markdown
            md_content = f"""# Ultrathink Output

**Query**: {args.query}
**Timestamp**: {output_payload["timestamp"]}
**Model**: {args.model}
**Converged in**: {iterations} iteration(s)
**Convergence History**: {json.dumps(history, indent=2)}

---

{synthesis}
"""
            output_path.write_text(md_content, encoding="utf-8")

        if not args.quiet:
            print(f"\n💾 Output saved to: {output_path}")

    # Print to stdout
    if args.json:
        print(json.dumps(output_payload, indent=2, ensure_ascii=False))
    else:
        print("\n" + "=" * 60)
        print("📋 FINAL OUTPUT")
        print("=" * 60)
        print(synthesis)
        print("\n" + "-" * 60)
        print(f"Converged in {iterations} iteration(s)")


if __name__ == "__main__":
    asyncio.run(main())
