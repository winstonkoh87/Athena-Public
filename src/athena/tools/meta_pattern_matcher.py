"""
Meta-Pattern Matcher for Project Athena.
========================================

Provides fast (<5ms) deterministic heuristic mapping from user queries to
Athena's 20 core Meta-Patterns (.context/META_PATTERNS.md).
Enables multi-hop retrieval to surface cross-domain structural insights
(e.g., connecting a used car inspection query to MP-16 short-gamma / MP-18 diagnostic gap)
without polluting the token window.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["detect_latent_meta_patterns", "META_PATTERN_CATALOG"]

META_PATTERN_CATALOG: dict[str, dict[str, Any]] = {
    "MP-1": {
        "name": "Sharecropping Law",
        "description": "If you don't own the arena, you subsidize someone else's asset appreciation with your labor.",
        "search_terms": "MP-1 Sharecropping arena ownership platform extraction risk rent vs own",
        "patterns": [
            r"\bplatform\b", r"\bmiddleman\b", r"\btake[\s-]rate\b", r"\bcommission\b",
            r"\blandlord\b", r"\bcarousell\b", r"\bupwork\b", r"\bshopee\b", r"\bgrab\b",
            r"\brent(ing)?\b", r"\bsharecrop(ping)?\b", r"\barena ownership\b",
            r"\bhawker\b", r"\bkopitiam\b", r"\bcoffee\s?shop\b", r"\bstall\b",
            r"\bfranchise(e|or)?\b", r"\btenancy\b", r"\blease\s+renewal\b",
        ],
    },
    "MP-2": {
        "name": "Efficiency-Survival Inversion",
        "description": "The strategy that looks most efficient in hindsight kills you going forward.",
        "search_terms": "MP-2 Efficiency-Survival Inversion fragility redundancy ergodicity",
        "patterns": [
            r"\bover[\s-]optimi[zs]\w*", r"\blean\b", r"\bfragil\w*",
            r"\bsingle point of failure\b", r"\bergodicit\w*", r"\bmargin of safety\b",
        ],
    },
    "MP-3": {
        "name": "Distribution Supremacy",
        "description": "Product quality is necessary but never sufficient. Distribution determines survival.",
        "search_terms": "MP-3 Distribution Supremacy CAC channel model audience acquisition",
        "patterns": [
            r"\bdistribution\b", r"\bchannel\b", r"\bcac\b", r"\baudience\b",
            r"\bacquisition\b", r"\bpaid ads\b", r"\bmarketing\b", r"\bgrowth channel\b",
        ],
    },
    "MP-4": {
        "name": "Price Ceiling Vise",
        "description": "Rising costs + capped revenue = mathematical ruin.",
        "search_terms": "MP-4 Price Ceiling Vise margin compression inflation squeeze",
        "patterns": [
            r"\bprice ceiling\b", r"\bmargin compression\b", r"\brising costs?\b",
            r"\bcapped (revenue|income|price)\b", r"\bcost squeeze\b",
        ],
    },
    "MP-5": {
        "name": "Form-Substance Gap",
        "description": "What it looks like != what it actually is. Stated narrative vs operative reality.",
        "search_terms": "MP-5 Form-Substance Gap substance decode official narrative cui bono",
        "patterns": [
            r"\bhidden (meaning|agenda|reason)\b", r"\breal reason\b", r"\bofficial (story|statement|narrative)\b",
            r"\boptics\b", r"\breading between the lines\b", r"\bform vs substance\b",
            r"\bpress release\b", r"\bwhat does this mean\b",
        ],
    },
    "MP-6": {
        "name": "Compounding vs Linear (Hand-Stop-Mouth-Stop)",
        "description": "Build compounding assets, not linear sweat-equity income streams where stopping for 6 months drops revenue to zero.",
        "search_terms": "MP-6 Compounding vs Linear hand stop mouth stop sweat equity passive asset",
        "patterns": [
            r"\bhand\s+stop\b", r"\bsweat\s+equity\b", r"\blinear\s+(?:income|labor|model|trap)\b",
            r"\bactive\s+income\b", r"\btrading\s+time\s+for\s+money\b",
            r"\bcarnot\s+(?:engine|trap|ceiling)\b", r"\bstop\s+working\s+for\s+6\s+months\b",
        ],
    },
    "MP-7": {
        "name": "Structural Protection",
        "description": "Survivors are structurally protected, not more talented. Ruin barriers and firewalls.",
        "search_terms": "MP-7 Structural Protection circuit breaker firewall ruin barrier insulation",
        "patterns": [
            r"\bcircuit breaker\b", r"\bfirewall\b", r"\bruin\b", r"\bliabilit(y|ies)\b",
            r"\bindemni(ty|fication)\b", r"\bwarrant(y|ies)\b", r"\bguarantee\b",
            r"\bstructural protection\b", r"\blegal insulation\b",
        ],
    },
    "MP-9": {
        "name": "Leverage Inversion & Red/Blue Curve Arena Selection",
        "description": "Everyone pushes hard; the difference is where the fulcrum sits (DEC-131 Red/Blue Curve, STR-42 Serf vs King, PAT-34 Table Selection).",
        "search_terms": "MP-9 Leverage Inversion DEC-131 Red Curve Blue Curve STR-42 PAT-34 table selection arena shift",
        "patterns": [
            r"\bred\s+curve\b", r"\bblue\s+curve\b", r"\bwrong\s+(?:game|table|arena)\b",
            r"\bright\s+(?:game|table|arena)\b", r"\btable\s+selection\b",
            r"\barena\s+(?:selection|shift|physics)\b", r"\bboxer'?s?\s+fallacy\b",
            r"\bserf'?s?\s+fallacy\b", r"\breposition(?:ing)?\s+the\s+lever\b",
        ],
    },
    "MP-10": {
        "name": "Information-Action Gap",
        "description": "Knowing != doing; the gap is structural, not cognitive. External forcing functions win.",
        "search_terms": "MP-10 Information-Action Gap accountability forcing function execution",
        "patterns": [
            r"\baccountabilit(y|ies)\b", r"\bprocrastinat\w*", r"\bknowing vs doing\b",
            r"\bforcing function\b", r"\bexecution friction\b", r"\bfollow[\s-]through\b",
        ],
    },
    "MP-13": {
        "name": "Principal-Agent Misalignment",
        "description": "Delegated execution drifts toward the agent's incentive, not the principal's welfare.",
        "search_terms": "MP-13 Principal-Agent Misalignment incentive drift contractor conflict",
        "patterns": [
            r"\bcontractor\b", r"\boutsource\w*", r"\bagent incentive\b",
            r"\bmisalignment\b", r"\bconflict of interest\b", r"\bpartner conflict\b",
        ],
    },
    "MP-16": {
        "name": "Variance vs Edge (Short-Gamma / Base Rate Distortion)",
        "description": "Hot streaks != edge. Asymmetric variance, short-gamma traps, and Kelly sizing bounds.",
        "search_terms": "MP-16 Variance vs Edge short gamma sizing ghost tail risk kelly variance",
        "patterns": [
            r"\bshort[\s-]gamma\b", r"\bvariance\b", r"\bedge\b", r"\bstreak\b",
            r"\bdrawdown\b", r"\bsizing ghost\b", r"\btail risk\b", r"\bmonte carlo\b",
            r"\bkelly\b", r"\bwipeout\b", r"\bwin rate\b", r"\btrade pnl\b",
        ],
    },
    "MP-17": {
        "name": "Iceberg Price Principle",
        "description": "The quoted price is the tip; the lifecycle cost is the iceberg.",
        "search_terms": "MP-17 Iceberg Price Principle total cost of ownership cheapness illusion",
        "patterns": [
            r"\bcheapness illusion\b", r"\bhidden cost\b", r"\blifecycle cost\b",
            r"\btotal cost of ownership\b", r"\btco\b", r"\biceberg\b",
        ],
    },
    "MP-18": {
        "name": "Diagnostic Gap & License-Use Arbitrage",
        "description": "Tacit street diagnosis vs explicit theory. Profit in the license vs use gap.",
        "search_terms": "MP-18 Diagnostic Gap tacit street knowledge obd-ii inspection license-use",
        "patterns": [
            r"\blicense[\s-]use\b", r"\bdiagnostic gap\b", r"\btacit knowledge\b",
            r"\bstreet knowledge\b", r"\bobd[\s-]ii\b", r"\binspection\b",
            r"\bpaint[\s-]depth\b", r"\bverification bridge\b", r"\bused car\b",
        ],
    },
    "MP-19": {
        "name": "Observable Liquidity Invariant",
        "description": "Never invent demand or educate indifferent markets; locate visible high-frequency cash.",
        "search_terms": "MP-19 Observable Liquidity Invariant high-frequency cash demand validation",
        "patterns": [
            r"\bobservable liquidity\b", r"\bexisting demand\b", r"\bhigh[\s-]frequency cash\b",
            r"\btransaction volume\b", r"\bmarket gap\b", r"\bp2p arbitrage\b",
        ],
    },
    "MP-20": {
        "name": "Brian Balfour's Four Fits",
        "description": "Market-Product, Product-Channel, Channel-Model, Model-Market vertical alignment.",
        "search_terms": "MP-20 Four Fits Balfour product channel model market monetization",
        "patterns": [
            r"\bfour fits\b", r"\bbalfour\b", r"\bproduct[\s-]channel\b",
            r"\bchannel[\s-]model\b", r"\bmodel[\s-]market\b", r"\barpu\b",
        ],
    },
}


def detect_latent_meta_patterns(query: str, max_patterns: int = 2) -> list[dict[str, Any]]:
    """Scan a query for latent Meta-Pattern triggers.

    Returns a list of matched Meta-Pattern descriptors, sorted by match count.
    """
    if not query:
        return []

    query_lower = query.lower()
    matches: list[tuple[str, int, dict[str, Any]]] = []

    for mp_id, meta in META_PATTERN_CATALOG.items():
        hits = 0
        for pat in meta["patterns"]:
            if re.search(pat, query_lower):
                hits += 1
        if hits > 0:
            matches.append((mp_id, hits, meta))

    # Sort descending by hit count
    matches.sort(key=lambda x: x[1], reverse=True)

    results = []
    for mp_id, hit_count, meta in matches[:max_patterns]:
        results.append({
            "id": mp_id,
            "name": meta["name"],
            "description": meta["description"],
            "search_terms": meta["search_terms"],
            "hit_count": hit_count,
        })

    return results
