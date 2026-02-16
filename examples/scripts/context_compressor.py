#!/usr/bin/env python3
"""
Context Compressor for Project Athena
Protocol: Sovereign Optimization
Core: LLMLingua
"""

import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [ContextCompressor] - %(levelname)s - %(message)s",
)

import re

# Lazy import for LLMLingua to avoid startup cost
PromptCompressor = None


def compress_fast(context: str, budget: int = 500) -> str:
    """
    Fast Heuristic Compression (Regex/Extraction).
    - Preserves headers, lists, and key sentences.
    - Removes fluff.
    - Instant execution.
    """
    # 1. Keep Structure (Headers)
    headers = re.findall(r"^(#+ .*)$", context, re.MULTILINE)

    # 2. Keep Lists (Tasks/todos)
    lists = re.findall(r"^(\s*[-*] .*)$", context, re.MULTILINE)

    # 3. Keep Key Sentences (containing 'must', 'should', 'decision', 'plan')
    sentences = re.split(r"(?<=[.!?])\s+", context)
    key_sentences = [
        s
        for s in sentences
        if any(
            w in s.lower()
            for w in ["must", "should", "decision", "plan", "goal", "error"]
        )
    ]

    # Assemble
    compressed = "\n".join(headers + key_sentences[:20] + lists[:20])

    # Truncate to budget approximation (roughly 4 chars per token)
    return compressed[: budget * 4]


def compress_heavy(context: str, target_token_budget: int = 500) -> str:
    """
    Deep Compression using LLMLingua (Slow, High Quality).
    """
    global PromptCompressor
    if PromptCompressor is None:
        try:
            from llmlingua import PromptCompressor as PC

            PromptCompressor = PC
        except ImportError:
            logging.error("LLMLingua not found. Install via: pip install llmlingua")
            return context[: target_token_budget * 4]

    try:
        # Load model on first use (CPU)
        compressor = PromptCompressor(model_name="microsoft/phi-2", device_map="cpu")

        compressed_prompt = compressor.compress_prompt(
            context,
            target_token=target_token_budget,
            condition_compare=True,
            condition_sep="\n\n",
            instruction="Keep key decisions, user constraints, and specific technical requirements.",
        )

        return compressed_prompt["compressed_prompt"]
    except Exception as e:
        logging.error(f"Compression failed: {e}")
        return context[: target_token_budget * 4]


def main():
    parser = argparse.ArgumentParser(description="Athena Context Compression Unit")
    parser.add_argument("--context", type=str, help="Text to compress")
    parser.add_argument("--budget", type=int, default=500, help="Target token budget")
    parser.add_argument(
        "--heavy", action="store_true", help="Use heavy LLM-based compression (slow)"
    )
    parser.add_argument("--test", action="store_true", help="Run a demo compression")

    args = parser.parse_args()

    if args.test:
        test_text = """
        User Profile: [AUTHOR], loves Sovereign AI.
        Project: Athena.
        Rules: No LangChain, use Rust where possible.
        Detailed History: Long winded conversation about things that happened in 2025 like the coffee shop incident
        where we discussed the Vercel trap and how Cloudflare is better for VPS.
        Decision: We chose to use LightRAG for memory.
        """
        print("Original Length:", len(test_text))
        print("Original Length:", len(test_text))
        if args.heavy:
            print("Mode: HEAVY (LLMLingua)")
            result = compress_heavy(test_text, target_token_budget=50)
        else:
            print("Mode: FAST (Heuristic)")
            result = compress_fast(test_text, budget=50)
        print("Compressed Result:", result)
        return

    if args.context:
        if args.heavy:
            print(compress_heavy(args.context, target_token_budget=args.budget))
        else:
            print(compress_fast(args.context, budget=args.budget))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
