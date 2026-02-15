#!/usr/bin/env python3
"""
Swarm Agent — Specialized Reasoning Node
========================================
Runs a single "Thinking Track" (Protocol 75) in an interactive loop.
Designed to be launched by parallel_swarm.py in a separate Terminal window.
"""

import argparse
import sys
import os
import time
from pathlib import Path

# Add script directory to path to import gemini_client
sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

# Track definitions (from Protocol 75)
TRACK_CONFIGS = {
    "A": {
        "name": "DOMAIN EXPERT",
        "color": BLUE,
        "icon": "🏗️",
        "prompt": """You are Track A (Domain Expert).
Your Goal: Apply domain-specific frameworks and expertise to analyze this problem.
1. Identify the domain(s).
2. Apply relevant mental models and best practices.
3. Provide structured recommendations.
Focus on: "What implies success in this domain?"
""",
    },
    "B": {
        "name": "ADVERSARIAL SKEPTIC",
        "color": RED,
        "icon": "🛡️",
        "prompt": """You are Track B (Adversarial Skeptic).
Your Goal: Challenge every premise, find every flaw, identify every risk.
1. Attack the problem statement.
2. Find logical fallacies and hidden assumptions.
3. Identify failure modes and edge cases.
Focus on: "What could go wrong? Where is the ruin?"
""",
    },
    "C": {
        "name": "CROSS-DOMAIN MATCHER",
        "color": YELLOW,
        "icon": "🧬",
        "prompt": """You are Track C (Cross-Domain Matcher).
Your Goal: Find isomorphic patterns from completely different fields.
1. Abstract the core structure of the problem.
2. Search knowledge for similar patterns in unrelated domains (biology, physics, history).
3. Extract transferable insights.
Focus on: "Where have we seen this pattern before?"
""",
    },
    "D": {
        "name": "ZERO-POINT PHILOSOPHER",
        "color": MAGENTA,
        "icon": "🔮",
        "prompt": """You are Track D (Zero-Point Philosopher).
Your Goal: Question the nature of the reality/problem itself.
1. Apply inversion: What if the opposite is true?
2. Apply First Principles: What is irreducibly true?
3. Consider metaphysical dimensions.
Focus on: "Is this the right game to be playing?"
""",
    },
}


def print_banner(role, config, goal):
    """Print the startup banner."""
    color = config["color"]
    icon = config["icon"]
    name = config["name"]

    print(f"\n{color}{BOLD}{'=' * 60}{RESET}")
    print(f"{color}{BOLD} {icon} TRACK {role}: {name} {RESET}")
    print(f"{color}{BOLD}{'=' * 60}{RESET}")
    print(f"\n{BOLD}🎯 GOAL:{RESET} {goal}")
    print(f"{DIM}📍 WORKTREE:{RESET} {os.getcwd()}")
    print(f"{DIM}🤖 MODEL:{RESET} Gemini Pro (via Athena)")
    print(f"\n{color}{'-' * 60}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Swarm Agent")
    parser.add_argument("role", choices=["A", "B", "C", "D"], help="Track Role")
    parser.add_argument("goal", help="The primary objective")
    parser.add_argument("--context", default="", help="Additional context")
    args = parser.parse_args()

    config = TRACK_CONFIGS[args.role]

    print_banner(args.role, config, args.goal)

    # Initialize Client
    system_prompt = config["prompt"] + f"\n\nCURRENT OBJECTIVE: {args.goal}"
    if args.context:
        system_prompt += f"\n\nCONTEXT:\n{args.context}"

    try:
        client = get_client(system_prompt=system_prompt)
        print(f"{GREEN}✓ Agent initialized. Thinking...{RESET}\n")

        # Initial thought
        initial_prompt = f"Analyze the objective: '{args.goal}'. Provide your initial perspective based on your role."
        response = client.chat(initial_prompt)

        print(f"{config['color']}{response}{RESET}\n")

    except Exception as e:
        print(f"{RED}Error initializing agent: {e}{RESET}")
        sys.exit(1)

    # REPL Loop
    while True:
        try:
            print(f"{BOLD}Input for Track {args.role} > {RESET}", end="")
            user_input = input()

            if user_input.lower() in ["exit", "quit"]:
                break

            if not user_input.strip():
                continue

            print(f"\n{DIM}Thinking...{RESET}\n")
            response = client.chat(user_input)
            print(f"{config['color']}{response}{RESET}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")


if __name__ == "__main__":
    main()
