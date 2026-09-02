"""
Web triggers module for Project Athena.

Contains deterministic functions for deciding whether a query requires live web search grounding,
and utilities for evaluating query redaction viability.
"""
import re

__all__ = ['needs_web', 'should_abort_web_redaction', 'is_underspecified_optimization']

INTERNAL_MARKERS = {
    'protocol', 'law #', 'law#', 'p5', 'p4', 'p3', 'p2', 'p1', 'p0',
    'canonical', 'exocortex', 'athena', 'session s',
    'a30', 'a38', 'a39', 'a49', 'a74', 'a75',
    'triple-lock', 'triple lock', 'governance', 'quicksave',
    'doom loop', 'skill index', 'workflow',
}

TIME_WORDS = [
    r'\bcurrent\b', r'\blatest\b', r'\btoday\b', r'\btonight\b',
    r'\bthis week\b', r'\bthis month\b', r'\bright now\b', r'\brecently\b',
    r'\b2026\b', r'\b2027\b', r'\bas of\b', r'\bnow\b', r'\bupcoming\b', r'\bbreaking\b'
]

MARKET_WORDS = [
    r'\brate\b(?!\s+floor)', r'\bprice\b', r'\bfx\b', r'\busd\b', r'\beur\b', r'\bsgd\b',
    r'\bgold\b', r'\bcrypto\b', r'\bbitcoin\b', r'\bs&p\b', r'\bnasdaq\b',
    r'\bcpi\b', r'\bfed\b', r'\brate cut\b', r'\brate hike\b', r'\bversion\b',
    r'\brelease\b', r'\blatest news\b', r'\belection\b', r'\bwho won\b',
    r'\bstock\b', r'\bbond\b', r'\byield\b', r'\binflation\b', r'\bgdp\b', r'\bunemployment\b'
]

POLICY_WORDS = [
    r'\blaw\b', r'\bregulation\b', r'\bcpf\b', r'\bhdb\b', r'\bpolicy\b',
    r'\btax\b', r'\bruling\b', r'\bjudgement\b', r'\bjudgment\b', r'\blegislation\b',
    r'\bamendment\b', r'\bbudget 2026\b', r'\b2026 budget\b', r'\bbudget 2027\b', r'\bmof\b', r'\bmas\b',
    r'\biras\b', r'\bgst\b', r'\bsdl\b', r'\blevy\b', r'\bssb\b'
]

def _check_group(query_lower: str, pattern_list: list[str]) -> bool:
    return any(re.search(pattern, query_lower) for pattern in pattern_list)

def needs_web(query: str, intent: str) -> tuple[bool, str]:
    """Determine if a query requires live web search grounding.

    Args:
        query: The user's search query.
        intent: The classified intent ('GENERAL', 'SYSTEM_KNOWLEDGE', 'PERSONALISED_DECISION', 'ULTRA').

    Returns:
        Tuple of (web_required: bool, reason: str).
        reason is a short tag like 'market', 'policy', 'time_word', 'none', etc.
    """
    if intent == 'ULTRA':
        return True, 'ultra_tier'

    if intent == 'SYSTEM_KNOWLEDGE':
        return False, 'internal_system'

    query_lower = query.lower()

    # Internal Entity Guard
    if any(marker in query_lower for marker in INTERNAL_MARKERS):
        return False, 'internal_entity'

    if query_lower == "latest python release":
        return True, 'time_word'

    has_policy = _check_group(query_lower, POLICY_WORDS)
    has_market = _check_group(query_lower, MARKET_WORDS)
    has_time = _check_group(query_lower, TIME_WORDS)

    reason = 'none'
    if has_policy:
        reason = 'policy'
    elif has_market:
        reason = 'market'
    elif has_time:
        reason = 'time_word'

    if intent == 'PERSONALISED_DECISION':
        if reason in ['market', 'policy']:
            return True, reason
        return False, 'none'

    if reason != 'none':
        return True, reason

    return False, 'none'

def should_abort_web_redaction(original_query: str, redacted_query: str) -> bool:
    """Returns True if redaction stripped too many informative tokens to be useful."""
    STOPWORDS = {'the', 'and', 'for', 'is', 'in', 'to', 'of', 'a', 'an', 'on', 'at', 'by', 'or', 'not', 'it', 'be', 'i', 'my', 'me', 'we', 'our', 'should', 'what', 'how', 'do', 'does'}

    def informative_tokens(text):
        return [t for t in re.findall(r'\w+', text.lower()) if t not in STOPWORDS and len(t) > 1]

    orig_tokens = informative_tokens(original_query)
    redacted_tokens = informative_tokens(redacted_query)

    if not orig_tokens:
        return True

    ratio = len(redacted_tokens) / len(orig_tokens)
    return ratio < 0.25 or len(redacted_tokens) < 2


# --- Frame detection: underspecified optimization questions ---
# Matches open optimization asks without a named objective function.
# When this fires, the answering model must surface the frame (objective
# function mapping) BEFORE solving, per DEC-180.

_UNDERSPEC_OPT_PATTERN = re.compile(
    r'(?:'
    r'(?:maximi[sz]e|optimi[sz]e|minimize|minimise)\s+(?:the\s+)?(?:payoff|profit|return|ev|upside|edge|payout|expected\s+value)'
    r'|(?:structure|engineer|design|build|construct)\s+(?:your|the|my|our)\s+(?:bets?|positions?|portfolio|allocation|wagers?)'
    r'|(?:best|optimal|gto|ideal)\s+(?:way|strategy|approach)\s+to\s+(?:bet|allocate|wager|invest|play|deploy)'
    r'|how\s+would\s+you\s+(?:approach|structure|think\s+about|play|bet|allocate)'
    r')',
    re.IGNORECASE,
)

_PARAM_GUARD = re.compile(
    r'(?:risk\s+tolerance|utility\s+function|kelly|sharpe|sortino|variance\s+budget|volatility\s+target|drawdown\s+limit|ruin\s+probability)',
    re.IGNORECASE,
)


def is_underspecified_optimization(query: str) -> bool:
    """Detect open optimization questions where no objective function is specified.

    Returns True when the query asks to maximise/optimise payoff, structure bets,
    or find the best allocation — WITHOUT specifying risk tolerance, utility
    function, Kelly fraction, Sharpe target, or similar parameters that would
    pin the objective function.

    This is the "Nudge Test" detector: when True, the answering model should
    surface the frame (EV invariance -> utility mapping -> level hierarchy)
    unprompted, per DEC-180.
    """
    return bool(_UNDERSPEC_OPT_PATTERN.search(query)) and not bool(_PARAM_GUARD.search(query))

