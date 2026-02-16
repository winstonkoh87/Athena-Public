#!/usr/bin/env python3
"""
shutdown.py — Consolidated Shutdown Orchestrator & Session Compiler
====================================================================
Single-call script that runs the entire /end close sequence:
  0. Session log finalization (YAML update, Λ aggregates, R__ generation)
  1. Learnings propagation ([S] → SYSTEM_LEARNINGS.md, [U] → USER_PROFILE.yaml)
  2. Harvest check (detect unfiled insights)
  3. Git commit & push
  4. Protocol compliance report
  5. Compliance reset for next session

Usage:
    python3 .agent/scripts/shutdown.py
    python3 .agent/scripts/shutdown.py --dry-run  # Preview changes without writing

Replaces 4+ separate script calls with 1 orchestrated call.
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from collections import Counter

# Optional: YAML support (graceful degradation if not installed)
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Fix sys.path for SDK access
SDK_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.config import (
    PROJECT_ROOT,
    SESSIONS_DIR,
    MEMORY_DIR,
    SYSTEM_LEARNINGS_FILE,
    USER_PROFILE_FILE,
)
from athena.sessions import (
    get_current_session_log,
    extract_learnings,
    extract_lambda_stats,
    update_session_metadata,
    parse_yaml_frontmatter,
)
from athena.intelligence.sentinel import check_shutdown_sentinel, update_active_context

SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "scripts"


# Stopwords for keyphrase extraction (deterministic, no NLP deps)
STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "under",
    "and",
    "but",
    "or",
    "nor",
    "so",
    "yet",
    "both",
    "either",
    "neither",
    "not",
    "only",
    "own",
    "same",
    "than",
    "too",
    "very",
    "just",
    "also",
    "now",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "what",
    "which",
    "who",
    "whom",
    "updated",
    "added",
    "created",
    "modified",
    "fixed",
    "implemented",
    "session",
    "checkpoint",
    "log",
}

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def divider(title: str):
    """Print a section divider."""
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")


def run_script(
    script_name: str, args: list = None, timeout: int = 60, silent: bool = False
) -> tuple[bool, str]:
    """Run a script and return (success, output)."""
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_name}"

    cmd = ["python3", str(script_path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(PROJECT_ROOT)
        )
        output = result.stdout + result.stderr
        if not silent and output.strip():
            print(output)
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Script timed out: {script_name}"
    except Exception as e:
        return False, f"Error running {script_name}: {e}"


# ============================================================
# PHASE 0: Session Log Finalization (Session Compiler)
# ============================================================

# Logic moved to athena.sessions SDK


def extract_keyphrases(content: str) -> str:
    """Extract dominant topic from checkpoints (deterministic, no NLP)."""
    # Find checkpoint content
    checkpoints = re.findall(
        r"### ⚡ Checkpoint \[.*?\]\n\n?(.*?)(?=\n###|\n## |$)", content, re.DOTALL
    )

    if len(checkpoints) < 2:
        return "General Development"

    # Skip first checkpoint (often warm-up), use rest
    text = " ".join(checkpoints[1:]).lower()

    # Tokenize
    words = re.findall(r"\b[a-z]{3,}\b", text)

    # Remove stopwords
    filtered = [w for w in words if w not in STOPWORDS]

    if not filtered:
        return "General Development"

    # Get most common bigrams
    bigrams = []
    for i in range(len(filtered) - 1):
        bigrams.append(f"{filtered[i]} {filtered[i + 1]}")

    if bigrams:
        counter = Counter(bigrams)
        top_bigram = counter.most_common(1)[0][0]
        return top_bigram.title()

    # Fallback to most common word
    counter = Counter(filtered)
    return counter.most_common(1)[0][0].title()


def extract_tags(content: str) -> list[str]:
    """Extract unique tags from session log."""
    tags = set(re.findall(r"#([\w-]+)", content))
    # Remove common/noise tags
    tags.discard("session")
    tags.discard("...")
    return sorted(list(tags))


def extract_threads(focus: str, tags: list[str], content: str) -> list[str]:
    """
    Auto-detect thread IDs from focus, tags, and content.
    Threads are multi-session arcs on related topics.

    Known threads:
    - TH-001: Athena Architecture
    - TH-002: Portfolio/Resume
    - TH-003: ZenithFX/Trading
    - TH-004: Melvin Portfolio
    - TH-005: Session Logging
    """
    threads = []

    # Keywords for known threads
    THREAD_PATTERNS = {
        "TH-001": [
            "athena",
            "architecture",
            "framework",
            "boot",
            "shutdown",
            "protocol",
            "canonical",
        ],
        "TH-002": ["portfolio", "resume", "linkedin", "github profile", "recruiter"],
        "TH-003": ["zenithfx", "trading", "gatekeeper", "bcm", "risk"],
        "TH-004": ["melvin", "portfolio", "essays"],
        "TH-005": ["session log", "template", "yaml", "migration", "checkpoint"],
    }

    # Combine searchable text
    search_text = f"{focus} {' '.join(tags)} {content[:1000]}".lower()

    for thread_id, keywords in THREAD_PATTERNS.items():
        matches = sum(1 for kw in keywords if kw in search_text)
        if matches >= 2:  # Require at least 2 keyword matches
            threads.append(thread_id)

    return threads[:3]  # Max 3 threads per session


# Logic moved to athena.sessions SDK


def generate_r_block(
    metadata: dict,
    lambda_stats: dict,
    tags: list[str],
    decisions: list[str],
    actions: list[str],
) -> str:
    """Generate the R__ Compressed Context block."""
    decided_str = "; ".join(decisions[:3]) if decisions else "None recorded"
    pending_str = "; ".join(actions[:3]) if actions else "None recorded"
    tags_str = " ".join(f"#{t}" for t in tags[:5]) if tags else "#session"

    return f"""```text
[[ R__ |
@focus: {metadata.get("focus", "General Development")}
@status: {metadata.get("status", "closed")}
@decided: {decided_str}
@pending: {pending_str}
@artifacts: See Section 4
@lambda_peak: {lambda_stats.get("peak", 0)}
@tags: {tags_str}
]]
```"""


def extract_decisions(content: str) -> list[str]:
    """Extract decision bullets from Key Decisions section."""
    decisions = []
    for match in re.findall(r"\*\*Decision\*\*:\s*(.+)", content):
        if match.strip() and match.strip() != "...":
            decisions.append(match.strip())
    return decisions


def extract_pending_actions(content: str) -> list[str]:
    """Extract pending action items."""
    actions = []
    for match in re.findall(r"\| [^|]+ \| ([^|]+) \| [^|]+ \| Pending \|", content):
        if match.strip() and match.strip() != "...":
            actions.append(match.strip())
    return actions


def propagate_system_learnings(
    learnings: list[str], session_id: str, dry_run: bool = False
) -> int:
    """Append system learnings to SYSTEM_LEARNINGS.md."""
    if not learnings:
        return 0

    if not SYSTEM_LEARNINGS_FILE.exists():
        print(f"{YELLOW}⚠️ SYSTEM_LEARNINGS.md not found, skipping propagation{RESET}")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    new_rows = []
    for learning in learnings:
        new_rows.append(f"| {today} | {session_id} | {learning} | ⏳ Pending |")

    if dry_run:
        print(f"{DIM}[DRY-RUN] Would append {len(new_rows)} system learnings{RESET}")
        for row in new_rows:
            print(f"  {DIM}{row}{RESET}")
        return len(new_rows)

    content = SYSTEM_LEARNINGS_FILE.read_text()
    # Find the table and append
    table_end = content.rfind("|")
    if table_end != -1:
        # Find end of that line
        line_end = content.find("\n", table_end)
        if line_end == -1:
            line_end = len(content)
        new_content = (
            content[:line_end] + "\n" + "\n".join(new_rows) + content[line_end:]
        )
        SYSTEM_LEARNINGS_FILE.write_text(new_content)

    return len(new_rows)


def propagate_user_learnings(
    learnings: list[str], session_id: str, dry_run: bool = False
) -> int:
    """Append user learnings to USER_PROFILE.yaml notes section safely."""
    if not learnings:
        return 0

    if not USER_PROFILE_FILE.exists():
        print(f"{YELLOW}⚠️ USER_PROFILE.yaml not found, skipping propagation{RESET}")
        return 0

    if dry_run:
        print(f"{DIM}[DRY-RUN] Would append {len(learnings)} user learnings{RESET}")
        for l in learnings:
            print(f"  {DIM}- {l}{RESET}")
        return len(learnings)

    # Load existing YAML safely
    header_comment = """# User Profile (Machine-Readable Preferences)
# Auto-managed by shutdown.py from session [U] markers.
# Manual edits allowed for corrections.
"""
    try:
        content = USER_PROFILE_FILE.read_text()
        # Remove header comments for parsing if needed, but safe_load usually ignores them
        data = yaml.safe_load(content) or {}
    except Exception as e:
        print(f"{YELLOW}⚠️ Failed to parse USER_PROFILE.yaml: {e}{RESET}")
        return 0

    if "notes" not in data:
        data["notes"] = []

    # Append new learnings
    for learning in learnings:
        data["notes"].append(
            {"learned": learning, "session": session_id, "confidence": "medium"}
        )

    # Write back with header
    try:
        yaml_str = yaml.dump(data, sort_keys=False, allow_unicode=True)
        USER_PROFILE_FILE.write_text(header_comment + "\n" + yaml_str)
    except Exception as e:
        print(f"{YELLOW}⚠️ Failed to write USER_PROFILE.yaml: {e}{RESET}")
        return 0

    return len(learnings)


def finalize_session_log(dry_run: bool = False) -> bool:
    """
    Main session compiler function. Parses, computes, and updates the session log.
    Idempotent: safe to run multiple times.
    """
    log_path = get_current_session_log()
    if not log_path:
        print(f"{YELLOW}⚠️ No session log found to finalize{RESET}")
        return False

    print(f"📋 Compiling session: {log_path.name}")

    content = log_path.read_text()
    metadata, body_start = parse_yaml_frontmatter(content)
    body = content[body_start:]

    if not metadata:
        print(f"{YELLOW}⚠️ No YAML frontmatter found (legacy format){RESET}")
        return False

    session_id = metadata.get("session_id", log_path.stem)

    # Compute derived values
    end_time = datetime.now().astimezone()
    lambda_stats = extract_lambda_stats(content)
    tags = extract_tags(content)
    decisions = extract_decisions(content)
    pending_actions = extract_pending_actions(content)

    # Infer focus if not set
    current_focus = metadata.get("focus", "")
    if not current_focus or current_focus == "...":
        metadata["focus"] = extract_keyphrases(content)

    # Update metadata
    metadata["end"] = end_time.isoformat()
    metadata["status"] = "closed"
    metadata["lambda_peak"] = lambda_stats["peak"]
    metadata["lambda_total"] = lambda_stats["total"]
    metadata["lambda_coverage"] = lambda_stats["coverage"]
    metadata["lambda_coverage_n"] = lambda_stats["coverage_n"]
    metadata["lambda_coverage_d"] = lambda_stats["coverage_d"]
    metadata["tags"] = tags

    # Extract threads (multi-session arcs)
    threads = extract_threads(metadata.get("focus", ""), tags, content)
    metadata["threads"] = threads

    # Calculate duration if start time exists
    start_str = metadata.get("start", "")
    if start_str:
        try:
            start_time = datetime.fromisoformat(start_str)
            duration = (end_time - start_time).total_seconds() / 60
            metadata["duration_min"] = round(duration)
        except (ValueError, TypeError):
            pass

    # Generate R__ block
    r_block = generate_r_block(metadata, lambda_stats, tags, decisions, pending_actions)

    # Extract and propagate learnings
    system_learnings, user_learnings, integration_requests = extract_learnings(content)

    if dry_run:
        print(f"\n{DIM}[DRY-RUN] Session compilation preview:{RESET}")
        print(f"  Focus: {metadata.get('focus')}")
        print(f"  Duration: {metadata.get('duration_min', '?')} min")
        print(
            f"  Λ Peak: {lambda_stats['peak']} | Total: {lambda_stats['total']} | Coverage: {lambda_stats['coverage']}"
        )
        print(f"  Tags: {', '.join(tags[:5])}")
        print(f"  System Learnings: {len(system_learnings)}")
        print(f"  User Learnings: {len(user_learnings)}")
        propagate_system_learnings(system_learnings, session_id, dry_run=True)
        propagate_user_learnings(user_learnings, session_id, dry_run=True)
        return True

    # Build new YAML frontmatter
    if HAS_YAML:
        new_frontmatter = (
            "---\n" + yaml.dump(metadata, sort_keys=False, allow_unicode=True) + "---\n"
        )
    else:
        # Simple fallback
        lines = ["---"]
        for k, v in metadata.items():
            if isinstance(v, list):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {v}")
        lines.append("---\n")
        new_frontmatter = "\n".join(lines)

    # Update R__ block in body
    r_block_pattern = (
        r"## 0\. R__ Compressed Context\n\n>.*?\n\n```text\n\[\[ R__ \|.*?\]\]\n```"
    )
    new_r_section = f"## 0. R__ Compressed Context\n\n> Auto-generated on close by `shutdown.py`. Do not manually edit.\n\n{r_block}"
    body = re.sub(r_block_pattern, new_r_section, body, flags=re.DOTALL)

    # Write updated file
    log_path.write_text(new_frontmatter + body)

    # Propagate learnings
    sys_count = propagate_system_learnings(system_learnings, session_id)
    user_count = propagate_user_learnings(user_learnings, session_id)

    # Sentinel Checks (Protocol 420)
    update_active_context(session_id, dry_run=dry_run)
    sentinel_msg = check_shutdown_sentinel(log_path)

    # Print summary
    print(f"{GREEN}✅ Session compiled{RESET}")
    print(f"   📊 Focus: {metadata.get('focus', 'Unknown')}")
    print(f"   ⏱️  Duration: {metadata.get('duration_min', '?')} min")
    print(
        f"   ⚡ Λ Peak: {lambda_stats['peak']} | Total: {lambda_stats['total']} | Coverage: {lambda_stats['coverage']}"
    )
    if sys_count or user_count:
        print(f"   📚 Learnings propagated: {sys_count} system, {user_count} user")

    if sentinel_msg:
        print(f"\n{YELLOW}{sentinel_msg}{RESET}")

    return True


# ============================================================
# PHASE 1: Harvest Check
# ============================================================


def harvest_check() -> bool:
    """Run harvest check to detect unfiled insights."""
    print("🌾 Checking for unharvested insights...")
    success, output = run_script("harvest_check.py")
    return success


# ============================================================
# PHASE 2: Git Commit & Push
# ============================================================


def git_commit() -> bool:
    """Run git commit script."""
    print("📦 Committing changes...")
    success, output = run_script("git_commit.py", timeout=120)
    return success


# ============================================================
# PHASE 3: Protocol Compliance
# ============================================================


def compliance_report() -> bool:
    """Generate and display compliance report."""
    print("📊 Generating compliance report...")
    success, output = run_script("protocol_compliance.py", ["report"])
    return success


def compliance_reset() -> bool:
    """Reset violations for next session."""
    success, output = run_script("protocol_compliance.py", ["reset"], silent=True)
    if success:
        print(f"{GREEN}✅ Violations reset for next session{RESET}")
    return success


def validate_log_synthesis(content: str) -> bool:
    """
    Check if the session log has been properly synthesized.
    Returns False if placeholders like '...' or '- [ ] ...' are found in key sections.
    """
    # Key sections that MUST be filled
    # We relax the check to only look for specific placeholder strings that indicate
    # the user hasn't filled in the section at all.
    critical_patterns = [
        r"## 1\. Agenda\s*\n\s*- \[ \] \.\.\.",  # Empty agenda item
        r"\*\*Decision\*\*:\s*\.\.\.",  # Empty decision
        r"\*\*Insight\*\*:\s*\.\.\.",  # Empty insight
        r"\| \.\.\. \| AI / User \| Pending \|",  # Empty action item table row
    ]

    for pattern in critical_patterns:
        match = re.search(pattern, content)
        if match:
            print(f"❌ Validation Failed on pattern: {pattern}")
            print(f"   Found match: '{match.group(0)}'")
            return False

    return True


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================


def safe_commit():
    """
    EMERGENCY HATCH: Commits all changes if the main orchestrator fails.
    Ensures no data loss in volatile memory.
    """
    print(f"\n{RED}{BOLD}🚨 EMERGENCY COMMIT TRIGGERED{RESET}")
    print("Attempting to save state despite failure...")
    try:
        run_script("git_commit.py", ["--force"], timeout=60)
        print(f"{GREEN}✅ Emergency Save Complete.{RESET}")
    except Exception as e:
        print(f"{RED}❌ Emergency Save Failed: {e}{RESET}")


def main():
    # Check for --dry-run flag
    dry_run = "--dry-run" in sys.argv

    divider("🔒 ATHENA SHUTDOWN SEQUENCE (Titanium Protocol)")

    exit_code = 0

    try:
        # Phase 0: Session Log Finalization (Session Compiler)
        print(f"{BOLD}📋 Phase 0: Session Compilation{RESET}")

        log_path = get_current_session_log()
        if log_path:
            # Force fresh read from disk to bypass any memory caching
            content = log_path.read_text()

            # [Fail-Safe Validation]
            # Instead of aborting, we warn. Robustness > Correctness.
        if not validate_log_synthesis(content):
            print(f"\n{YELLOW}{BOLD}⚠️ WARNING: Incomplete Session Log detected.{RESET}")
            print(f"{YELLOW}Proceeding with shutdown to preserve data.{RESET}")
            # We do NOT return 1 here anymore. We must save.

        if not finalize_session_log(dry_run=dry_run):
            print(f"{YELLOW}⚠️ Session finalization had issues (skipping step){RESET}")
        print()

        if dry_run:
            print(f"\n{BOLD}{CYAN}[DRY-RUN MODE] No changes written. Exiting.{RESET}\n")
            return 0

        # Phase 1: Harvest check (Background)
        print("🌾 Harvest Check (Background)...")
        try:
            subprocess.Popen(
                ["python3", ".agent/scripts/harvest_check.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            pass

        print()

        # Phase 2: Git commit (The Critical Step - SYNCHRONOUS)
        if not git_commit():
            print(f"{YELLOW}⚠️ Git commit had issues{RESET}")
            exit_code = 1

        print()

        # Phase 3: Compliance
        compliance_report()
        compliance_reset()

        # Phase 4: Semantic Search Compliance
        try:
            from semantic_audit import print_compliance_report

            print_compliance_report()
        except Exception:
            pass

        # Phase 5: Update CANONICAL metrics
        try:
            from update_metrics import main as update_metrics_main

            update_metrics_main()
        except Exception:
            pass

        # Phase 6: Auto-Hygiene (Background)
        print(f"\n{CYAN}🧹 Running Hygiene Protocol (Background)...{RESET}")
        try:
            subprocess.Popen(
                ["python3", ".agent/scripts/compress_sessions.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            print(f"{YELLOW}⚠️  Hygiene trigger failed: {e}{RESET}")

        # Summary
        print(f"\n{BOLD}{'─' * 60}{RESET}")
        time_now = datetime.now().strftime("%H:%M SGT")
        if exit_code == 0:
            print(f"{GREEN}{BOLD}✅ Session closed.{RESET} Time: {time_now}")
        else:
            print(
                f"{YELLOW}{BOLD}⚠️ Session closed with warnings.{RESET} Time: {time_now}"
            )
        print(f"{BOLD}{'─' * 60}{RESET}\n")

        return exit_code

    except Exception as e:
        # GLOBAL CATCH-ALL
        print(f"\n{RED}❌ CRITICAL SHUTDOWN FAILURE: {e}{RESET}")
        print(f"{RED}Traceback available in logs.{RESET}")
        import traceback

        traceback.print_exc()

        # Deploy Emergency Parachute
        if not dry_run:
            safe_commit()

        return 1


if __name__ == "__main__":
    sys.exit(main())
