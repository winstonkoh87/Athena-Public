"""
lambda_scorer.py — Deterministic Risk Tier & Compute Allocator
=============================================================

Replaces subjective 'Lambda is vibes' with an objective, feature-based
risk scoring engine (<5ms runtime). Evaluates query complexity, financial stakes,
irreversibility, and existential ruin risks to compute an integer Lambda score (0-100)
and map it strictly to RiskLevel (SNIPER <10, STANDARD 10-30, ULTRA >30).

Part of Phase C1 (Computed Lambda + Hard Pre-Answer Gate).
"""

from __future__ import annotations

import re
from typing import Any

from athena.core.governance import RiskLevel

__all__ = ["compute_lambda", "LambdaResult", "CRISIS_REFERRAL_TEXT", "assess_intel_posture"]

CRISIS_REFERRAL_TEXT = (
    "🚨 HARD STOP — Referral Gate (Protocol 509)\n\n"
    "Active crisis, severe distress, or self-harm signals detected.\n"
    "Athena is an AI assistant, not a clinician. Please connect immediately with professional human support:\n\n"
    "• SOS (Samaritans of Singapore): 1-767 (24h Hotline) or WhatsApp 9151 1767\n"  # pds:allow
    "• IMH (Institute of Mental Health) Emergency Helpline: 6389 2222 (24h)\n"
    "• Emergency Medical Services: 995 (Ambulance / SCDF) or 999 (Police)\n"
    "• International Support: https://findahelpline.com"
)

TRIVIAL_PATTERNS = [
    r"^(hi|hello|hey|yo|morning|afternoon|evening)\b",
    r"^(thanks|thank you|ty|cheers|got it|noted|ok|okay|cool|nice|good)\b",
    r"^(yes|no|proceed|continue|agree|approved|lgtm|looks good)\b",
    r"^(bye|goodbye|cya|see you)\b",
]

FINANCIAL_STAKES_PATTERNS = [
    (r"(s\$|\$|usd|sgd|¥)\s*\d+[\d,]*(\.\d+)?", "currency_amount"),
    (r"\b(margin|liquidation|pnl|deposit|burn rate|pricing|invoice|paynow|capital|drawdown)\b", "financial_concept"),
    (r"\b\d{5,}\b", "large_bare_number"),
    # Spelled-out large amounts (paraphrase robustness)
    (r"\b(hundred|thousand|million|billion)\s+(dollar|buck|pound|euro|sgd)", "currency_spelled"),
    (r"\b(four|five|six|seven|eight|nine|ten)\s+(hundred|thousand|million)\b", "large_amount_spelled"),
]

IRREVERSIBILITY_PATTERNS = [
    (r"\b(sign|quit|resign|terminate|terminated|laid off|retrenchment|pip|lawsuit|sue|charged|court|contract)\b", "irreversible_action"),
    (r"\b(marriage|wedding|banquet|ang[\s-]bao)\b", "high_stakes_social"),
    (r"\b(guarantee|indemnification|indemnity|warranties|warranty)\b", "legal_liability"),
    # Paraphrase-robust job exit
    (r"\b(hand(ed)? in|give(n)?|submit(ted)?|tender(ed)?)\b.{0,15}\b(notice|resignation|letter)\b", "job_exit_paraphrase"),
    (r"\b(leaving|quitting|left)\b.{0,15}\b(my job|work|career)\b", "career_exit"),
    # Paraphrase-robust legal exposure
    (r"\b(on the hook|personally liable|personal liability|lose everything)\b", "legal_exposure_paraphrase"),
    # Medical irreversibility
    (r"\b(surgery|operation|procedure|amputation|transplant|biopsy|mastectomy|hysterectomy)\b", "medical_irreversible"),
    # Custody / family law
    (r"\b(custody|divorce|separation|annulment|maintenance order|access.{0,10}(kids?|children))\b", "family_law"),
    # Multilingual irreversibility (Mandarin / Malay / French)
    (r"(签|合同|辞职|离婚|破产|贷款)", "multilingual_irreversible_zh"),
    (r"\b(tandatangan|kontrak|berhenti|cerai|bankrap|muflis|pinjaman)\b", "multilingual_irreversible_ms"),
    (r"\b(signer|contrat|démissionner|faillite|prêt)\b", "multilingual_irreversible_fr"),
]

CRISIS_IDIOM_EXCLUSIONS = [
    re.compile(r"\b(suicide squad|suicide squeeze|suicide run|suicide doors|process suicide|suicide thread|suicide call)\b", re.I),
    re.compile(r"\bkilling myself\s+(at the gym|working out|laughing|rn|lol|lmao|with work|on this code|with python|trying to)\b", re.I),
    re.compile(r"\bkms\s+(lol|lmao|haha)\b", re.I),
    re.compile(r"\bkilling me\s+(softly|with)\b", re.I),
]

CRISIS_CORE_PATTERNS = [
    re.compile(r"\b(want to die|wanna die|wish i were dead|wish i was dead|wish i hadn'?t been born)\b", re.I),
    re.compile(r"\b(better off dead|better off without me|everyone would be better off|everyone would be happier if i (was|were) gone)\b", re.I),
    re.compile(r"\b(end(ing)? (it all|my life|things)|take my (own )?life|kill(ing)? myself|suicid\w*)\b", re.I),
    re.compile(r"\b(kms|unaliv(e|ed|es|ing)( myself)?)\b", re.I),
    re.compile(r"\b(giving (away )?my (stuff|belongings|things)|writing (goodbye )?letters to (everyone|people)|won'?t be around (much longer|anymore))\b", re.I),
    re.compile(r"\b(don'?t want to (live|be here|exist|wake up)|can'?t go on (living|anymore)|no (point|reason) (in |to )?(living|going on)|tired of living|what'?s the point of living)\b", re.I),
    re.compile(r"\b(want to disappear (forever|completely)|wanna disappear (forever|completely)|wish i could sleep and never wake up)\b", re.I),
    re.compile(r"\b(plan to end (it|things|my life)|thinking about ending (things|it|it all))\b", re.I),
    re.compile(r"\b(took a bunch of pills|swallowed a bunch of pills|overdose[d]?|taking pills to end)\b", re.I),
    re.compile(r"\b(been cutting myself|cut(ting)? myself again|slit(ting)? my wrists?)\b", re.I),
    re.compile(r"\b(jump(ing)? off (my |the |a )?(hdb|block|building|bridge|roof|balcony|ledge))\b", re.I),
    re.compile(r"\b(hang(ing)? myself|shoot(ing)? myself|drown(ing)? myself)\b", re.I),
    re.compile(r"\b(suicide note|goodbye note)\b", re.I),
    re.compile(r"(想死|不想活了|不想在这世界|想自杀|轻生|跳楼|割腕|吞安眠药|活着没意思|活着好累|大家没有我更好)"),
    re.compile(r"\b(nak mati|tak nak hidup|bunuh diri|potong tangan)\b", re.I),
    re.compile(r"\b(burnout stage|complete(ly)? (broken|shattered|destroyed)|lost (the will|all hope|everything)|can'?t (take it|do this anymore))\b", re.I),
]


def detect_crisis_signal(text: str) -> bool:
    """Robust Protocol 509 crisis and self-harm detector.

    Filters out benign idioms while capturing direct, indirect, and multilingual signals.
    """
    if any(ex.search(text) for ex in CRISIS_IDIOM_EXCLUSIONS):
        acute_methods = [
            re.compile(r"\b(took a bunch of pills|overdose[d]?|cutting myself again|jumping off)\b", re.I),
            re.compile(r"(想死|想自杀|跳楼|割腕)")
        ]
        if not any(m.search(text) for m in acute_methods):
            return False
    return any(p.search(text) for p in CRISIS_CORE_PATTERNS)


RUIN_RISK_PATTERNS = [
    (r"\b(ruin|guillotine|wipeout|short[\s-]gamma|circuit breaker|law of ruin|tail risk)\b", "ruin_risk"),
    (r"\b(go(ing)? all[\s-]in|all[\s-]in|sell everything)\b", "all_in_ruin_risk"),
    # Plain-language total loss
    (r"\b(lose everything|lost everything|nothing left|wiped out|blown? up|blow up my)\b", "total_loss_plain"),
]

STRATEGIC_PATTERNS = [
    (r"\b(strategy|architecture|portfolio|allocation|asymmetry|monte carlo|kelly|audit|deep dive|comprehensive)\b", "strategic_depth"),
    (r"\b(prove me wrong|red team|counter[\s-]argument|cui bono|hidden meaning|substance decode)\b", "adversarial_reasoning"),
]

ENTITY_PATTERNS = [
    (r"\b(a\d+|s\d{2,4}|cs-\d+|pat-\d+|td-\d+|cc\d{4})\b", "athena_entity_code"),
]


class LambdaResult(dict):
    score: int
    tier: str
    risk_level: RiskLevel
    features: list[dict[str, Any]]


def compute_lambda(
    query: str,
    intent: str = "GENERAL",
    web_required: bool = False,
    underspec_opt: bool = False,
) -> dict[str, Any]:
    """Compute an objective risk Lambda score (0-100) and assign RiskLevel.

    Args:
        query: User's raw or cleaned prompt text.
        intent: Classified intent ('GENERAL', 'SYSTEM_KNOWLEDGE', 'PERSONALISED_DECISION', etc.).
        web_required: Whether external web search is triggered.
        underspec_opt: Whether the query is an underspecified optimization problem.

    Returns:
        dict with score (int), tier (str), risk_level (RiskLevel), and features (list).
    """
    cleaned = query.strip()
    if not cleaned:
        return {
            "score": 0,
            "tier": RiskLevel.SNIPER.name,
            "risk_level": RiskLevel.SNIPER,
            "features": [{"name": "empty_query", "weight": 0}],
            "is_crisis": False,
            "crisis_referral": None,
        }

    query_lower = cleaned.lower()
    words = query_lower.split()
    word_count = len(words)

    # 0. Crisis & Self-Harm Screen (Protocol 509 — Non-Negotiable Gate)
    # MUST evaluate before trivial patterns to prevent "no point in living" matching "^no"
    if detect_crisis_signal(cleaned):
        return {
            "score": 40,
            "tier": RiskLevel.ULTRA.name,
            "risk_level": RiskLevel.ULTRA,
            "features": [
                {"name": "base_standard", "weight": 10},
                {"name": "protocol_509_crisis", "weight": 30},
            ],
            "is_crisis": True,
            "crisis_referral": CRISIS_REFERRAL_TEXT,
        }

    # 1. Check for trivial conversational greeting
    if word_count <= 4 and any(re.search(p, query_lower) for p in TRIVIAL_PATTERNS):
        return {
            "score": 2,
            "tier": RiskLevel.SNIPER.name,
            "risk_level": RiskLevel.SNIPER,
            "features": [{"name": "trivial_conversational", "weight": 2}],
            "is_crisis": False,
            "crisis_referral": None,
        }

    score = 10  # Baseline default is STANDARD (10-30)
    features: list[dict[str, Any]] = [{"name": "base_standard", "weight": 10}]
    is_crisis = False

    # 2. Ruin & Existential Risk (+30)
    for pat, label in RUIN_RISK_PATTERNS:
        if re.search(pat, query_lower):
            score += 30
            features.append({"name": label, "weight": 30})
            if label in ("psychological_ruin", "existential_crisis"):
                is_crisis = True
            break

    # 3. Irreversibility & Legal Liability (+25)
    for pat, label in IRREVERSIBILITY_PATTERNS:
        if re.search(pat, query_lower):
            score += 25
            features.append({"name": label, "weight": 25})
            break

    # 4. Financial Stakes & Capital (+20)
    for pat, label in FINANCIAL_STAKES_PATTERNS:
        if re.search(pat, query_lower):
            score += 20
            features.append({"name": label, "weight": 20})
            break

    # 5. Strategic & Adversarial Markers (+15)
    for pat, label in STRATEGIC_PATTERNS:
        if re.search(pat, query_lower):
            score += 15
            features.append({"name": label, "weight": 15})
            break

    # 6. Entity Codes (+10)
    for pat, label in ENTITY_PATTERNS:
        if re.search(pat, query_lower):
            score += 10
            features.append({"name": label, "weight": 10})
            break

    # 7. Underspecified Optimization (+10)
    if underspec_opt:
        score += 10
        features.append({"name": "underspec_optimization", "weight": 10})

    # 8. Web Search Required (+5)
    if web_required:
        score += 5
        features.append({"name": "web_required", "weight": 5})

    # 9. Query Length Modifiers
    if word_count > 25:
        score += 10
        features.append({"name": "long_query_length", "weight": 10})
    elif word_count <= 5 and intent == "SYSTEM_KNOWLEDGE" and not web_required and not underspec_opt:
        # Factual short system queries demote to SNIPER
        score -= 8
        features.append({"name": "short_system_fact", "weight": -8})

    # Cap score at 100 max, 0 min
    score = max(0, min(100, score))

    # 10. Anti-stuffing coherence gate (red-team probe remediation)
    # Prevents keyword noise from forcing ULTRA by requiring structural
    # decision-making intent when the score exceeds ULTRA threshold.
    # NEVER suppress genuine crisis signals.
    if score > 30 and not is_crisis:
        # Rule 1: Bare nouns (1-2 words) are never genuine ULTRA decisions.
        # A single word like "contract" is a factual lookup, not a decision.
        if word_count <= 2:
            score = min(score, 30)
            features.append({"name": "anti_stuffing_bare_noun", "weight": 0})
        else:
            # Rule 2: When 4+ independent scoring categories fire,
            # require at least one decision-frame signal to confirm the
            # query is a genuine ask, not keyword salad.
            category_count = len([f for f in features
                                  if f["name"] != "base_standard"
                                  and f["weight"] > 0])
            if category_count >= 4:
                DECISION_FRAME = [
                    r"\?",                                           # question mark
                    r"\b(should|shall|must|need to|have to)\b",      # modal obligation
                    r"\b(whether|if i)\b",                           # conditional ask
                    r"\b(worth|worthwhile)\b",                       # evaluative
                    r"\b(advice|thoughts|recommend|suggest|opinion)\b",  # solicitation
                    r"\b(decide|decision|choice|option)\b",          # decision frame
                    r"\bwhat (should|would|do you think|can i|do i)\b",
                    r"\bhow (should|would|do i|can i)\b",
                    r"\b(can i|may i|is it (ok|safe|wise|risky))\b",
                    # Imperative task verbs as first word (legitimate commands)
                    r"^(audit|review|check|analyze|evaluate|assess|verify|help|tell|explain|show|prove|calculate|compare)\b",
                ]
                if not any(re.search(p, query_lower) for p in DECISION_FRAME):
                    score = min(score, 30)
                    features.append({"name": "anti_stuffing_no_decision_frame", "weight": 0})

    # Map to RiskLevel
    if score < 10:
        tier = RiskLevel.SNIPER
    elif score <= 30:
        tier = RiskLevel.STANDARD
    else:
        tier = RiskLevel.ULTRA

    return {
        "score": score,
        "tier": tier.name,
        "risk_level": tier,
        "features": features,
        "is_crisis": is_crisis,
        "crisis_referral": CRISIS_REFERRAL_TEXT if is_crisis else None,
    }


_MULTI_OPTION_RE = re.compile(
    r"\b(?:or|vs\.?|versus|compare|comparison|option|options|alternative|alternatives|"
    r"trade[-\s]?off|tradeoff|choice|launch|should (?:i|we)|which|better to|strategy)\b",
    re.I,
)
_HIGH_STAKES_RE = re.compile(
    r"\b(?:irreversible|lock[-\s]?up|lockup|capital|ruin|kelly|drawdown|leverage|contract|"
    r"lawsuit|legal|equity|retaliation|competitor|pricing|deploy|migration|production)\b|S?\$[0-9,]+",
    re.I,
)
_RECON_NEEDED_RE = re.compile(
    r"\b(?:latest|current|recent|today|202[56]|osint|research|investigate|check online|competitor|pricing|market)\b",
    re.I,
)


def assess_intel_posture(
    query: str,
    lambda_res: LambdaResult | dict[str, Any] | None = None,
    intent: str = "GENERAL",
) -> dict[str, Any]:
    """Classify 3-stage Intel Officer posture deterministically (< 0.5 ms, zero I/O).

    Stage 1 (Recon/OSINT) -> Stage 2 (Meta-Frame check) -> Stage 3 (MCDA/Pairwise Recommendation).
    Fast SNIPER_DIRECT bypasses heavy stages for trivial or simple baseline lookups.
    """
    cleaned = query.strip()
    lam = lambda_res if lambda_res is not None else compute_lambda(cleaned, intent=intent)
    score = int(lam.get("score", 0))
    tier = str(lam.get("tier", "STANDARD"))
    is_crisis = bool(lam.get("is_crisis", False))
    features = lam.get("features") or []

    multi_option = bool(_MULTI_OPTION_RE.search(cleaned))
    high_stakes = bool(_HIGH_STAKES_RE.search(cleaned))
    recon_needed = bool(_RECON_NEEDED_RE.search(cleaned))
    non_base_risk = any(
        isinstance(f, dict) and f.get("name") != "base_standard" and int(f.get("weight", 0)) > 0
        for f in features
    )

    reasons: list[str] = [f"lambda_tier:{tier}", f"lambda_score:{score}", f"intent:{intent}"]
    if multi_option:
        reasons.append("multi_option")
    if high_stakes:
        reasons.append("high_stakes")
    if recon_needed:
        reasons.append("recon_needed")

    if is_crisis:
        reasons.append("crisis_override")
        return {
            "posture": "CRISIS_HARD_STOP",
            "recon_required": False,
            "meta_frame_required": False,
            "recommend_required": False,
            "reasons": reasons,
        }

    is_baseline_lookup = (
        score <= 10
        and not non_base_risk
        and not multi_option
        and not high_stakes
        and not recon_needed
        and intent in ("GENERAL", "SYSTEM_KNOWLEDGE")
    )
    if (tier == "SNIPER" and not (multi_option and high_stakes)) or is_baseline_lookup:
        if is_baseline_lookup:
            reasons.append("baseline_factual_direct")
        return {
            "posture": "SNIPER_DIRECT",
            "recon_required": False,
            "meta_frame_required": False,
            "recommend_required": False,
            "reasons": reasons,
        }

    if score >= 25 or tier == "ULTRA" or (multi_option and high_stakes):
        return {
            "posture": "STRATEGIC_INTEL_OFFICER",
            "recon_required": True,
            "meta_frame_required": True,
            "recommend_required": True,
            "reasons": reasons,
        }

    meta_frame_required = bool(
        score >= 15 or multi_option or high_stakes or intent in ("RESEARCH", "PERSONALISED_DECISION")
    )
    recommend_required = bool(score >= 15 or multi_option)
    return {
        "posture": "RECON_AND_FRAME",
        "recon_required": True,
        "meta_frame_required": meta_frame_required,
        "recommend_required": recommend_required,
        "reasons": reasons,
    }
