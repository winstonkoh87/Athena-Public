#!/usr/bin/env python3
import sys
import argparse

def assess_complexity(task_description):
    """
    Analyzes a task description and returns a complexity score (L1-L5)
    based on keywords and implied scope, following Protocol 330.
    """
    task = task_description.lower()
    
    # Keyword Heuristics
    l5_keywords = ["enterprise", "scalability", "migration", "security review", "audit", "full lifecycle", "platform", "rewrite"]
    l4_keywords = ["system", "architecture", "design", "module", "integration", "workflow", "database", "api", "breaking change"]
    l3_keywords = ["feature", "component", "function", "update", "refactor", "page", "endpoint", "test"]
    l2_keywords = ["tweak", "adjust", "minor", "style", "css", "content", "copy"]
    l1_keywords = ["typo", "fix", "bug", "error", "patch", "quick"]

    # Deduce Level
    level = "L3" # Default
    score = 3
    rationale = "Standard feature complexity presumed."

    if any(k in task for k in l5_keywords):
        level = "L5"
        score = 5
        rationale = "Detected enterprise/system-wide keywords."
    elif any(k in task for k in l4_keywords):
        level = "L4"
        score = 4
        rationale = "Detected architectural/system keywords."
    elif any(k in task for k in l3_keywords):
        level = "L3"
        score = 3
        rationale = "Detected standard feature keywords."
    elif any(k in task for k in l2_keywords):
        level = "L2"
        score = 2
        rationale = "Detected minor adjustment keywords."
    elif any(k in task for k in l1_keywords):
        level = "L1"
        score = 1
        rationale = "Detected quick fix keywords."

    # Heuristic Tweaks based on length (Proxy for detail/scope)
    if len(task.split()) > 50 and score < 4:
        score += 1
        level = f"L{score}"
        rationale += " + Complexity bumped due to detailed description."

    return level, rationale

def get_recommendation(level):
    if level == "L5":
        return "CRITICAL: Use `/ultrathink`. Full architecture & security review required."
    elif level == "L4":
        return "HIGH: Use `/research` then `/think`. Design doc required."
    elif level == "L3":
        return "STANDARD: Use `/brief` if unclear, then `/think`. PRD recommended."
    elif level == "L2":
        return "LOW: Direct execution. Single session."
    elif level == "L1":
        return "MINIMAL: Just do it. No planning artifact needed."
    return "Unknown level."

def main():
    parser = argparse.ArgumentParser(description="Assess task complexity (BMAD Protocol 330)")
    parser.add_argument("task", nargs="+", help="Task description")
    args = parser.parse_args()

    task_text = " ".join(args.task)
    level, rationale = assess_complexity(task_text)
    recommendation = get_recommendation(level)

    print(f"🎯 Complexity Assessment: {level}")
    print(f"🤔 Rationale: {rationale}")
    print(f"📋 Recommendation: {recommendation}")

if __name__ == "__main__":
    main()
