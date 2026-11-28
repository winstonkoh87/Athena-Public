"""
athena.core.skill_nudge
========================

2-Tier Keyword Matching Engine for Contextual Skill Suggestions.
Adapted from Zeude's UserPromptSubmit hook — simplified for Athena's
local-first, solo-operator architecture.

Architecture:
    User Prompt --> Negative Filter --> Tier 1 (Primary) --> Match!
                                   --> Tier 2 (Secondary, 2+ keywords) --> Match!
                                   --> No Match (return empty)

Usage:
    from athena.core.skill_nudge import match_skills

    results = match_skills("I want to analyze my trading win rate")
    # [{"skill": "Protocol 367", "confidence": 0.9, "hint": "High Win-Rate Supremacy"}]
"""

import re
from dataclasses import dataclass


@dataclass
class SkillMatch:
    """A matched skill with confidence and hint."""

    skill: str
    confidence: float
    hint: str
    tier: int  # 1 = primary (single keyword), 2 = secondary (2+ keywords)
    matched_keywords: list[str]


# =============================================
# KEYWORD REGISTRY
# =============================================
# Each skill has:
#   - primary_keywords: Any ONE of these triggers a match (Tier 1)
#   - secondary_keywords: Need 2+ matches to trigger (Tier 2)
#   - hint: Human-readable suggestion text

SKILL_REGISTRY: dict[str, dict] = {
    # --- Trading ---
    "Protocol 367: High Win-Rate Supremacy": {
        "primary": [
            "win rate",
            "win-rate",
            "winrate",
            "variance drag",
            "kelly criterion",
            "half-kelly",
        ],
        "secondary": [
            "trading",
            "position",
            "risk",
            "rr",
            "reward",
            "bankroll",
            "drawdown",
            "probability",
        ],
        "hint": "Mathematical proof that High WR / Low RR dominates. Use for position sizing analysis.",
    },
    "Protocol 46: Trading Desk Constraints": {
        "primary": ["trading desk", "forex", "fx trading"],
        "secondary": ["trading", "scam", "signal", "broker", "leverage"],
        "hint": "Trading constraint framework. Risk boundaries and broker evaluation.",
    },
    # --- Business ---
    "Protocol 162: PMOD": {
        "primary": ["pmod", "product-market", "product market"],
        "secondary": [
            "marketing",
            "positioning",
            "pricing",
            "value prop",
            "distribution",
            "launch",
        ],
        "hint": "Product-Market Optimization Diagnostic. Use for go-to-market analysis.",
    },
    "Consultancy Framework": {
        "primary": ["consultancy", "consulting", "curriculum", "onboarding"],
        "secondary": ["client", "engagement", "workshop", "retainer", "setup"],
        "hint": "Structure a technical consultancy service offering.",
    },
    # --- AI Systems ---
    "Protocol 133: JIT Routing": {
        "primary": ["jit routing", "query routing", "archetype"],
        "secondary": ["reasoning", "depth", "complexity", "escalation", "think"],
        "hint": "Just-In-Time Knowledge Routing. Scales reasoning to query complexity.",
    },
    "Protocol 75: Synthetic Parallel Reasoning": {
        "primary": ["parallel reasoning", "synthetic reasoning", "spr"],
        "secondary": ["analyze", "strategy", "complex", "framework", "deep"],
        "hint": "Multi-track analysis for complex strategic decisions.",
    },
    "Protocol 52: Deep Research": {
        "primary": ["deep research", "rabbit hole", "exhaustive"],
        "secondary": ["research", "find", "everything", "comprehensive", "audit"],
        "hint": "Exhaustive research loop with citation tracking.",
    },
    # --- Frontend/Design ---
    "Skill: Frontend Design": {
        "primary": ["frontend", "css", "ui design", "ux design"],
        "secondary": [
            "design",
            "layout",
            "responsive",
            "animation",
            "component",
            "pretty",
        ],
        "hint": "Frontend design system and aesthetic guidelines.",
    },
    # --- Ads/Marketing ---
    "Skill: Claude Ads": {
        "primary": ["google ads", "meta ads", "facebook ads", "ppc", "roas"],
        "secondary": [
            "ads",
            "campaign",
            "bidding",
            "conversion",
            "creative",
            "cpc",
            "ctr",
        ],
        "hint": "Comprehensive paid advertising audit and optimization.",
    },
    # --- Psychology & Behavioral Profiling (Protocol 585) ---
    "Protocol 585: Behavioral Investigative Analysis (L1-L5 & FBI Profiling)": {
        "primary": [
            "attachment",
            "emotional-pattern",
            "stress-response",
            "growth",
            "psychological profile",
            "behavioral profile",
            "mo vs signature",
            "l1-l5",
            "fbi profiling",
            "behavioral investigative analysis",
        ],
        "secondary": [
            "psychology",
            "therapy",
            "fantasy",
            "validation",
            "boundary",
            "profile",
            "fbi",
            "signature",
            "staging",
            "counterparty",
            "isomorphism",
            "motive",
        ],
        "hint": "6-Stage FBI Behavioral Investigative Analysis (BIA), MO vs Signature vs Staging, and L1-L5 psyche stack.",
    },
    # --- Sandbox ---
    "Sandbox Execution": {
        "primary": ["sandbox", "docker run", "isolated execution"],
        "secondary": ["docker", "container", "execute", "script", "untrusted"],
        "hint": "Execute untrusted code in an isolated Docker sandbox.",
    },
}

# Words that indicate NO skill should be suggested
NEGATIVE_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    "good morning",
    "good night",
    "how are you",
    "test",
]


# =============================================
# MATCHING ENGINE
# =============================================


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _keyword_in_text(keyword: str, text: str) -> bool:
    """Check if keyword appears in text (substring match for multi-word, word boundary for single)."""
    if " " in keyword:
        return keyword in text
    # Single word: use word boundary
    return bool(re.search(rf"\b{re.escape(keyword)}\b", text))


def match_skills(
    prompt: str,
    max_results: int = 3,
    min_confidence: float = 0.5,
) -> list[dict]:
    """
    Match a user prompt against the skill registry using 2-tier keyword matching.

    Args:
        prompt: The user's prompt or context text.
        max_results: Maximum number of skill suggestions to return.
        min_confidence: Minimum confidence threshold.

    Returns:
        List of dicts: [{"skill": str, "confidence": float, "hint": str, "tier": int}]
        Empty list if no matches or negative keyword detected.
    """
    text = _normalize(prompt)

    # Check negative keywords first — bail immediately
    for neg in NEGATIVE_KEYWORDS:
        if _keyword_in_text(neg, text):
            return []

    matches: list[SkillMatch] = []

    for skill_name, config in SKILL_REGISTRY.items():
        primary = config.get("primary", [])
        secondary = config.get("secondary", [])
        hint = config.get("hint", f"Use {skill_name}")

        # Tier 1: Any single primary keyword matches
        primary_hits = [kw for kw in primary if _keyword_in_text(kw, text)]
        if primary_hits:
            matches.append(
                SkillMatch(
                    skill=skill_name,
                    confidence=0.9,
                    hint=hint,
                    tier=1,
                    matched_keywords=primary_hits,
                )
            )
            continue

        # Tier 2: Need 2+ secondary keyword matches
        secondary_hits = [kw for kw in secondary if _keyword_in_text(kw, text)]
        if len(secondary_hits) >= 2:
            # Confidence scales with number of matches
            conf = min(0.85, 0.5 + (len(secondary_hits) * 0.1))
            matches.append(
                SkillMatch(
                    skill=skill_name,
                    confidence=round(conf, 2),
                    hint=hint,
                    tier=2,
                    matched_keywords=secondary_hits,
                )
            )

    # Sort by confidence descending, then by tier (tier 1 first)
    matches.sort(key=lambda m: (-m.confidence, m.tier))

    # Filter and limit
    results = []
    for m in matches[:max_results]:
        if m.confidence >= min_confidence:
            results.append(
                {
                    "skill": m.skill,
                    "confidence": m.confidence,
                    "hint": m.hint,
                    "tier": m.tier,
                    "matched_keywords": m.matched_keywords,
                }
            )

    return results


def get_registry_summary() -> list[dict]:
    """Return a summary of all registered skills and their keyword counts."""
    summary = []
    for name, config in SKILL_REGISTRY.items():
        summary.append(
            {
                "skill": name,
                "primary_keywords": len(config.get("primary", [])),
                "secondary_keywords": len(config.get("secondary", [])),
                "hint": config.get("hint", ""),
            }
        )
    return summary
