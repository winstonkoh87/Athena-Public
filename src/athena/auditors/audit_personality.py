#!/usr/bin/env python3
"""
Metabolic Scan — Living Docs Update Reminder

Purpose: Enforces Section 4.6 of /end workflow by:
1. Reading the current session log
2. Extracting signals that require Living Doc updates
3. Detecting PERSONALITY DRIFT (MBTI, Big Five, Enneagram shifts)
4. Printing a checklist for the AI to execute

Living Docs (The Metabolic Layer):
- User_Profile_Core.md (Bio/Traits/PERSONALITY SCORES)
- Psychology_L1L5.md (Current State)
- Session_Observations.md (Calibration)
- Operating_Principles.md (New Rules)
"""

import glob
import re
from datetime import datetime
from pathlib import Path

# Paths
CONTEXT_DIR = Path(__file__).parent.parent.parent / ".context"
PROFILE_DIR = CONTEXT_DIR / "profile"
SESSION_LOGS_DIR = CONTEXT_DIR / "memories" / "session_logs"

# Living Docs
LIVING_DOCS = {
    "User_Profile_Core.md": "Bio, traits, typology, PERSONALITY SCORES",
    "Psychology_L1L5.md": "Emotional shifts, schema updates, therapeutic insights",
    "Session_Observations.md": "Calibration references, new vocabulary, case patterns",
    "Operating_Principles.md": "New decision rules, frameworks, constraints",
}

# Signal patterns to detect (regex)
SIGNAL_PATTERNS = {
    "Psychology_L1L5.md": [
        r"(schema|L[1-5]|trauma|trigger|emotional|pattern|insight|mechanism)",
        r"(self-gaslighting|abandonment|invalidation|escalation|dysregulation)",
        r"(therapy|therapeutic|processing|grief|closure)",
    ],
    "Session_Observations.md": [
        r"(calibration|reference|vocabulary|shorthand|case)",
        r"(workflow|system|architecture|pipeline)",
        r"(pattern|anti-pattern|heuristic|rule)",
    ],
    "Operating_Principles.md": [
        r"(principle|rule|law|framework|constraint)",
        r"(protocol \d+|decision|strategy|navigation)",
        r"(always|never|must|gto|optimal)",
    ],
    "User_Profile_Core.md": [
        r"(bio|trait|typology|identity|personality)",
        r"(preference|style|mode|default)",
    ],
}

# ============================================================
# PERSONALITY DRIFT DETECTION
# ============================================================

# Big Five behavioral markers
BIG_FIVE_MARKERS = {
    "Neuroticism": {
        "increase": [
            r"(anxious|worried|stressed|panic|overwhelmed|catastroph)",
            r"(tilt|spiral|trigger|dysregulat|meltdown)",
            r"(can't stop thinking|obsess|rumina)",
        ],
        "decrease": [
            r"(calm|regulated|grounded|stable)",
            r"(handled it well|didn't react|stayed cool)",
            r"(let it go|moved on|accepted)",
        ],
    },
    "Extraversion": {
        "increase": [
            r"(energized by people|social|outgoing|party)",
            r"(want to meet|excited to talk|miss people)",
            r"(bored alone|need company|lonely)",
        ],
        "decrease": [
            r"(drained by people|need space|want to be alone)",
            r"(too much socializing|exhausted after)",
            r"(prefer solitude|recharge alone)",
        ],
    },
    "Openness": {
        "increase": [
            r"(new idea|creative|experiment|curious)",
            r"(what if|imagine|explore|novel)",
            r"(abstract|conceptual|theoretical)",
        ],
        "decrease": [
            r"(stick to what works|practical|concrete)",
            r"(don't need new|prefer routine|traditional)",
        ],
    },
    "Agreeableness": {
        "increase": [
            r"(understand their side|empathy|compassion)",
            r"(maybe I was wrong|their perspective)",
            r"(harmony|cooperat|compromise)",
        ],
        "decrease": [
            r"(don't care what they think|my way)",
            r"(they can deal|not my problem)",
            r"(transactional|what's in it for me)",
        ],
    },
    "Conscientiousness": {
        "increase": [
            r"(organized|systematic|disciplined|structured)",
            r"(plan|schedule|checklist|documented)",
            r"(finish what I start|follow through)",
        ],
        "decrease": [
            r"(wing it|spontaneous|who cares)",
            r"(forgot|procrastinat|lazy)",
            r"(good enough|don't need to be perfect)",
        ],
    },
}

# MBTI function markers
MBTI_MARKERS = {
    "Ni": [r"(long-term|future|vision|pattern|meaning|insight)"],  # Introverted Intuition
    "Te": [r"(efficient|logical|systematic|organized|objective)"],  # Extraverted Thinking
    "Fi": [r"(values|authentic|feel right|personal meaning)"],  # Introverted Feeling
    "Se": [r"(in the moment|sensory|immediate|physical|concrete)"],  # Extraverted Sensing
    "Ne": [r"(possibilities|brainstorm|what if|ideas|options)"],  # Extraverted Intuition
    "Ti": [r"(analyze|understand why|logical framework|categorize)"],  # Introverted Thinking
    "Fe": [r"(harmony|group|social dynamics|others' feelings)"],  # Extraverted Feeling
    "Si": [r"(past experience|tradition|reliable|detailed memory)"],  # Introverted Sensing
}

# Current baseline (from User_Profile_Core.md)
CURRENT_PROFILE = {
    "MBTI": "INTJ-T",
    "Big_Five": {
        "Neuroticism": 85,
        "Extraversion": 65,
        "Openness": 73,
        "Agreeableness": 58,
        "Conscientiousness": 88,
    },
    "Enneagram": "5w4",
}


def get_latest_session_log():
    """Find the most recent session log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = str(SESSION_LOGS_DIR / f"{today}-session-*.md")
    files = sorted(glob.glob(pattern), reverse=True)

    if files:
        return Path(files[0])

    # Fallback: any session log from today
    all_files = sorted(glob.glob(str(SESSION_LOGS_DIR / "*.md")), reverse=True)
    return Path(all_files[0]) if all_files else None


def extract_signals(session_content: str) -> dict:
    """Scan session content for signals requiring Living Doc updates."""
    signals = {doc: [] for doc in LIVING_DOCS}

    for doc, patterns in SIGNAL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, session_content, re.IGNORECASE)
            if matches:
                unique_matches = list({m.lower() if isinstance(m, str) else m[0].lower() for m in matches})
                signals[doc].extend(unique_matches[:5])

    for doc in signals:
        signals[doc] = list(set(signals[doc]))

    return signals


def detect_personality_drift(session_content: str) -> dict:
    """Detect signals that suggest personality score changes."""
    drift = {
        "Big_Five": {},
        "MBTI_functions": {},
        "recommendations": []
    }

    # Check Big Five markers
    for trait, directions in BIG_FIVE_MARKERS.items():
        increase_count = 0
        decrease_count = 0

        for pattern in directions.get("increase", []):
            matches = re.findall(pattern, session_content, re.IGNORECASE)
            increase_count += len(matches)

        for pattern in directions.get("decrease", []):
            matches = re.findall(pattern, session_content, re.IGNORECASE)
            decrease_count += len(matches)

        if increase_count > 3 or decrease_count > 3:
            current = CURRENT_PROFILE["Big_Five"][trait]
            if increase_count > decrease_count:
                drift["Big_Five"][trait] = {"direction": "↑", "signals": increase_count}
                if trait == "Neuroticism":
                    drift["recommendations"].append(f"⚠️  {trait} signals UP ({increase_count}x) — currently {current}. Consider +3-5 points?")
                else:
                    drift["recommendations"].append(f"📊 {trait} signals UP ({increase_count}x) — currently {current}. Consider +3-5 points?")
            elif decrease_count > increase_count:
                drift["Big_Five"][trait] = {"direction": "↓", "signals": decrease_count}
                if trait == "Neuroticism":
                    drift["recommendations"].append(f"✅ {trait} signals DOWN ({decrease_count}x) — currently {current}. Consider -3-5 points?")
                else:
                    drift["recommendations"].append(f"📊 {trait} signals DOWN ({decrease_count}x) — currently {current}. Consider -3-5 points?")

    # Check MBTI function usage
    function_counts = {}
    for func, patterns in MBTI_MARKERS.items():
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, session_content, re.IGNORECASE)
            count += len(matches)
        if count > 2:
            function_counts[func] = count

    if function_counts:
        drift["MBTI_functions"] = function_counts
        # Check for unusual function activation (not Ni-Te for INTJ)
        unusual = [f for f in function_counts if f not in ["Ni", "Te", "Fi", "Se"]]
        if unusual:
            drift["recommendations"].append(f"🔄 Unusual MBTI functions active: {', '.join(unusual)}. Type shift?")

    return drift


def check_living_doc_freshness():
    """Check when each Living Doc was last updated."""
    freshness = {}

    for doc in LIVING_DOCS:
        doc_path = PROFILE_DIR / doc
        if doc_path.exists():
            content = doc_path.read_text()
            match = re.search(r"Last Updated[:\s]*(\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2})", content)
            if match:
                freshness[doc] = match.group(1)
            else:
                freshness[doc] = "Unknown"
        else:
            freshness[doc] = "FILE MISSING"

    return freshness


def main():
    print("=" * 60)
    print("🫀 METABOLIC SCAN — Living Docs Update Check")
    print("=" * 60)
    print()

    # Get latest session
    session_file = get_latest_session_log()
    if not session_file:
        print("❌ No session log found for today.")
        return

    print(f"📄 Session: {session_file.name}")
    print()

    # Read session content
    session_content = session_file.read_text()

    # Extract signals
    signals = extract_signals(session_content)

    # Detect personality drift
    drift = detect_personality_drift(session_content)

    # Check freshness
    freshness = check_living_doc_freshness()

    # ============================================================
    # PERSONALITY DRIFT REPORT
    # ============================================================
    if drift["recommendations"]:
        print("🧬 PERSONALITY DRIFT DETECTED")
        print("-" * 60)
        for rec in drift["recommendations"]:
            print(f"   {rec}")
        print()
        print(f"   Current MBTI: {CURRENT_PROFILE['MBTI']}")
        print(f"   Current Big Five: N={CURRENT_PROFILE['Big_Five']['Neuroticism']}, E={CURRENT_PROFILE['Big_Five']['Extraversion']}, O={CURRENT_PROFILE['Big_Five']['Openness']}, A={CURRENT_PROFILE['Big_Five']['Agreeableness']}, C={CURRENT_PROFILE['Big_Five']['Conscientiousness']}")
        print()
        print("   ➡️  ACTION: Update User_Profile_Core.md if sustained pattern")
        print()

    # ============================================================
    # LIVING DOCS CHECKLIST
    # ============================================================
    print("📋 LIVING DOCS UPDATE CHECKLIST")
    print("-" * 60)

    updates_needed = False

    for doc, description in LIVING_DOCS.items():
        doc_signals = signals.get(doc, [])
        last_updated = freshness.get(doc, "Unknown")

        # Force flag User_Profile_Core.md if personality drift detected
        if doc == "User_Profile_Core.md" and drift["recommendations"]:
            updates_needed = True
            print(f"\n⚠️  {doc} — PERSONALITY DRIFT FLAGGED")
            print(f"   Purpose: {description}")
            print(f"   Last Updated: {last_updated}")
            print("   ➡️  ACTION: Review Big Five / MBTI scores")
        elif doc_signals:
            updates_needed = True
            print(f"\n⚠️  {doc}")
            print(f"   Purpose: {description}")
            print(f"   Last Updated: {last_updated}")
            print(f"   Detected Signals: {', '.join(doc_signals[:8])}")
            print("   ➡️  ACTION: Review and update if new insights found")
        else:
            print(f"\n✅ {doc} — No signals detected")

    print()
    print("-" * 60)

    if updates_needed or drift["recommendations"]:
        print("⚠️  UPDATES MAY BE NEEDED. AI must review session for:")
        print("   • Personality score changes → User_Profile_Core.md")
        print("   • New psychological insights → Psychology_L1L5.md")
        print("   • New calibration references → Session_Observations.md")
        print("   • New decision rules → Operating_Principles.md")
    else:
        print("✅ No obvious updates detected. Verify manually.")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

