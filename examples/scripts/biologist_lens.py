#!/usr/bin/env python3
"""
athena.core.creation.biologist_lens
===================================
Lateral Innovation Engine (Protocol 052) - The Biologist Lens

Demonstrates "Computer-Aided Creativity" by forcing cross-domain retrieval.
1. Abstracts a concrete problem (e.g., Marketing) into a System Problem (e.g., Signaling).
2. Retrieves biologically analogous concepts (e.g., Handicap Principle).
3. Synthesizes a radical solution.

Usage:
    python3 biologist_lens.py "How to market a high-end tuition center"
"""

import sys
import time

# --- MOCK LLM & RETRIEVAL LOGIC ---


def llm_abstract(problem: str) -> str:
    """
    Step 1: The Bridge.
    Strip away industry jargon. Convert to Systems Theory / Evolutionary Biology terms.
    """
    print(f"🧠 [LLM] Abstracting problem: '{problem}'...")
    time.sleep(1.0)

    # Mock Abstraction Logic based on keywords
    if "tuition" in problem.lower() or "school" in problem.lower():
        return "Optimize trust, growth, and symbiotic retention in a competitive, high-stakes ecosystem."
    if "aesthetic" in problem.lower() or "beauty" in problem.lower():
        return "Honest signaling of extensive resources (fitness) in a crowded mating market."

    return "Optimize resource acquisition and competition in a saturating niche."


def lateral_retrieval(abstraction: str, domain="biology"):
    """
    Step 2: The Lateral Search.
    Search the 'Biologist Lens' Index using the abstract terms.
    """
    print(f"🔍 [VECTOR_DB] Searching '{domain.upper()}' index for: '{abstraction}'...")
    time.sleep(1.0)

    results = []

    if "symbiotic" in abstraction.lower():
        results.append(
            {
                "concept": "Mycorrhizal Networks (Wood Wide Web)",
                "definition": "Fungi connect trees to share nutrients and warnings. Trees pay sugar (carbon) for this service.",
                "principle": "Symbiosis: Interconnected systems survive better than isolated ones.",
            }
        )
        results.append(
            {
                "concept": "Companion Planting (Three Sisters)",
                "definition": "Corn, beans, and squash grow better together. Corn provides structure, beans fix nitrogen, squash blocks weeds.",
                "principle": "Synergy: Diversity creates resilience and yield.",
            }
        )

    elif "signaling" in abstraction.lower():
        results.append(
            {
                "concept": "The Handicap Principle (Amotz Zahavi)",
                "definition": "Reliable signals must be costly to the signaler. If a signal is cheap, it can be faked.",
                "principle": "Costly Signaling: Wasteful display proves genetic quality (e.g., Peacock Tail).",
            }
        )
        results.append(
            {
                "concept": "Aposematism (Warning Coloration)",
                "definition": "Bright colors signal toxicity to predators. Avoiding conflict saves energy for both parties.",
                "principle": "Honest Warning: Don't waste energy fighting if you can signal danger.",
            }
        )

    else:
        results.append(
            {
                "concept": "K-Selection Strategy",
                "definition": "Invest heavily in few offspring (Quality > Quantity). High survival rate.",
                "principle": "Quality over Quantity: Focus on high-value, long-term investments.",
            }
        )

    return results


def llm_synthesize(problem: str, concepts: list) -> str:
    """
    Step 3: The Forced Connection.
    Apply the biological concept back to the industry problem.
    """
    print(f"⚡ [LLM] Forcing connections between Biology and '{problem}'...")
    print("-" * 60)

    concept = concepts[0]  # Take the top result
    c_name = concept["concept"]
    c_principle = concept["principle"]

    insight = ""

    if "Handicap" in c_name:
        insight = f"""
        **The Biologist's Strategy: The 'Painful' Price Tag**
        
        **Biological Concept**: {c_name}
        **Principle**: {c_principle}
        
        **Application**:
        Your problem is that your marketing is "Cheap Talk." Anyone can say "We are the best."
        To prove quality, you must incur a COST that fakers cannot afford.
        
        **Radical Idea**: 
        Stop offering discounts. Instead, introduce a **Non-Refundable 'Audit Fee' ($50)** just to speak to you.
        - In nature, only a fit peacock can afford a heavy tail.
        - In business, only a confident expert can charge for a sales call.
        
        This filters 'tyre-kickers' (energy parasites) and signals 'High Status' (fitness) instantly.
        """

    elif "Mycorrhizal" in c_name:
        insight = f"""
        **The Biologist's Strategy: The 'Root Network' Referral**
        
        **Biological Concept**: {c_name}
        **Principle**: {c_principle}
        
        **Application**:
        Tuition centers usually treat students as isolated units. Nature does not.
        Trees survive because they are PLUGGED IN to a fungal network.
        
        **Radical Idea**:
        Create a **"Symbiosis Pricing" Model**.
        - Solo student: $500/mo.
        - "Grafted" Pair (must sign up together): $350/mo each.
        - diverse Group (3 students from DIFFERENT schools): $300/mo each.
        
        Why? You are mimicking a Mycelial Network. You force students to build the network FOR you.
        Mixing students from different schools (genetic diversity) prevents 'school-specific' blind spots and creates a stronger learning super-organism.
        """

    else:
        insight = f"""
        **The Biologist's Strategy: K-Selection (The Whale Strategy)**
        
        **Biological Concept**: {c_name}
        **Principle**: {c_principle}
        
        **Application**:
        Stop trying to be a fly (r-selection: millions of eggs, low survival).
        Be a Whale (K-selection: one calf, massive investment).
        
        **Radical Idea**:
        Fire the bottom 50% of your customers who pay the least and complain the most.
        Take that freed-up energy and OVER-INVEST in the top 10%.
        """

    return insight


# --- MAIN EXECUTION ---


def run_biologist_lens(problem: str):
    print(f"\n🔬 ACTIVATING BIOLOGIST LENS for: '{problem}'\n")

    # 1. Abstraction
    abstract_query = llm_abstract(problem)
    print(f'   => Abstraction: "{abstract_query}"\n')

    # 2. Lateral Retrieval
    concepts = lateral_retrieval(abstract_query)
    print(f"   => Retrieved Concepts: {[c['concept'] for c in concepts]}")

    # 3. Synthesis
    final_output = llm_synthesize(problem, concepts)
    print(final_output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:])
        run_biologist_lens(problem)
    else:
        # Default Demo
        run_biologist_lens("How to market a high-end aesthetic clinic")
        print("\n" + "=" * 60 + "\n")
        run_biologist_lens("How to improve retention in a tuition center")
