#!/usr/bin/env python3
"""
shutdown.py — Consolidated Shutdown Orchestrator & Session Compiler
====================================================================
Single-call script that runs the entire /end close sequence.

Supports two modes:
  --micro    Fast-path: git commit only. Skips compilation, compliance, harvest.
  (default)  Full-path: Session compilation + harvest + git + compliance.

Usage:
    python3 .agent/scripts/shutdown.py           # Full close
    python3 .agent/scripts/shutdown.py --micro    # Micro close (~3s)
    python3 .agent/scripts/shutdown.py --dry-run  # Preview only

Phases (Full Mode):
  0. Session Log Finalization (Session Compiler)
  1. Harvest Check (background — fire-and-forget)
  2. Git Commit & Push (inlined, fast)
  3. Protocol Compliance (inlined)
  4. Auto-Hygiene (background — fire-and-forget)

v2.0 — GTO Rewrite (2026-03-09)
  - Added --micro fast-path
  - Removed dead semantic audit phase
  - Tightened git timeouts (10s → 5s)
  - Moved compliance imports to top-level
  - Made Phase 0 skip cleanly when no session log found
"""

from __future__ import annotations

import re
import sys
import subprocess
from datetime import datetime
from collections import Counter
from pathlib import Path

# --- YAML (optional) ---
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# --- SDK imports ---
SDK_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.config import (
    PROJECT_ROOT,
    SYSTEM_LEARNINGS_FILE,
    USER_PROFILE_FILE,
)
from athena.sessions import (
    get_current_session_log,
    extract_learnings,
    extract_lambda_stats,
    parse_yaml_frontmatter,
)
from athena.intelligence.sentinel import check_shutdown_sentinel

# --- Compliance imports (top-level, not runtime) ---
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "scripts"
SYNC_SCRIPT = SCRIPTS_DIR / "sync_agents_md.py"
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from protocol_compliance import generate_report as compliance_generate_report
    from protocol_compliance import update_markdown_log as compliance_update_log
    from protocol_compliance import reset_violations as compliance_reset

    HAS_COMPLIANCE = True
except ImportError:
    HAS_COMPLIANCE = False


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

# Git timeout (tightened from 10s → 5s)
GIT_TIMEOUT = 5
# Push talks to the remote — give it more headroom than local git ops, but still
# bounded so a hang can't block session close.
PUSH_TIMEOUT = 20


def divider(title: str):
    """Print a section divider."""
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")


# ============================================================
# GIT (Shared by both micro and full paths)
# ============================================================


def _run_git(args, timeout=GIT_TIMEOUT):
    """Run a git command directly. Returns (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1


def git_push_verified() -> bool:
    """Push HEAD to origin/main, fast-forward-only, and verify it landed.

    Replaces the old fire-and-forget `git push` (bare, no refspec), which was a
    silent no-op on worktree branches that have no upstream tracking ref — commits
    committed fine but never reached the remote, while close still reported success.

    Strategy (no --force ever):
      1. Try `git push origin HEAD:main`. Git fast-forwards main if HEAD is ahead,
         and rejects (non-fast-forward) if main diverged — its own safety net does
         the divergence check, so no separate fetch/merge-base is needed.
      2. If rejected as non-fast-forward, main has moved independently. Don't clobber
         it — push the working branch instead so the commit is at least on the remote,
         and WARN that main needs a manual merge/PR.
      3. Any failure (auth, network, rejection) prints a visible WARNING. Push is
         bounded by PUSH_TIMEOUT so it can't hang the close, but it never fails silently.
    """
    out, err, code = _run_git(["push", "origin", "HEAD:main"], timeout=PUSH_TIMEOUT)
    detail = (err or out).strip()

    if code == 0:
        if "up-to-date" in detail.lower():
            print(f"{GREEN}✓ Push → origin/main (already up-to-date).{RESET}")
        else:
            print(f"{GREEN}✓ Pushed → origin/main.{RESET}")
        return True

    non_ff = any(s in detail.lower() for s in ("non-fast-forward", "fetch first", "rejected", "behind"))
    if non_ff:
        # origin/main moved independently. Attempt ONE safe auto-reconcile before
        # giving up: fetch + rebase (autostash) onto origin/main, then re-push.
        # This handles the common multi-machine case (a few commits behind, no
        # conflicts). If the rebase hits conflicts, abort cleanly (tree restored)
        # and fall through to the branch-push fallback — never a half-merged tree,
        # never a --force.
        _run_git(["fetch", "origin", "main"], timeout=PUSH_TIMEOUT)
        _, _rb_err, rb_code = _run_git(["rebase", "--autostash", "origin/main"], timeout=PUSH_TIMEOUT)
        if rb_code == 0:
            out_r, err_r, code_r = _run_git(["push", "origin", "HEAD:main"], timeout=PUSH_TIMEOUT)
            if code_r == 0:
                print(f"{GREEN}✓ origin/main had moved — auto-rebased and pushed.{RESET}")
                return True
            detail = (err_r or out_r).strip()  # updated reason for the fallback warning
        else:
            _run_git(["rebase", "--abort"], timeout=GIT_TIMEOUT)
            print(f"{YELLOW}⚠️ Auto-rebase hit conflicts — aborted (tree restored). "
                  f"Falling back to branch push; reconcile main manually.{RESET}")
        branch, _, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if branch and branch != "HEAD":
            out2, err2, code2 = _run_git(["push", "origin", f"HEAD:{branch}"], timeout=PUSH_TIMEOUT)
            if code2 == 0:
                print(f"{YELLOW}⚠️ origin/main diverged — did NOT touch it. "
                      f"Pushed branch '{branch}' instead. Merge/PR to main manually.{RESET}")
                return True
            print(f"{RED}❌ Push FAILED — commit is LOCAL ONLY. "
                  f"main diverged and branch push also failed: {(err2 or out2).strip()[:200]}{RESET}")
            return False
        print(f"{RED}❌ Push FAILED — origin/main diverged and HEAD is detached. "
              f"Commit is LOCAL ONLY. Resolve manually.{RESET}")
        return False

    # Auth / network / other.
    print(f"{RED}❌ Push FAILED — commit is LOCAL ONLY (not on remote). "
          f"Run `git push origin HEAD:main` manually. Reason: {detail[:200]}{RESET}")
    return False


def check_ci_status() -> None:
    """Checks the GitHub Actions CI status for the repository (TD-053)."""
    import json
    try:
        # Get current local head SHA
        git_sha_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=3, cwd=str(PROJECT_ROOT)
        )
        current_sha = git_sha_proc.stdout.strip() if git_sha_proc.returncode == 0 else ""
        if not current_sha:
            return

        # Run gh run list to get the latest 5 runs
        proc = subprocess.run(
            ["gh", "run", "list", "--limit", "5", "--json", "conclusion,status,url,headSha,name"],
            capture_output=True, text=True, timeout=5, cwd=str(PROJECT_ROOT)
        )
        if proc.returncode != 0:
            return
        
        runs = json.loads(proc.stdout)
        if not runs:
            return
        
        print(f"\n{BOLD}{CYAN}🔔 CI Status Integration (TD-053):{RESET}")
        
        # 1. Search for current commit's run
        current_run = None
        for run in runs:
            if run.get("headSha") == current_sha:
                current_run = run
                break
        
        if current_run:
            status = current_run.get("status", "unknown")
            url = current_run.get("url", "")
            conclusion = current_run.get("conclusion")
            name = current_run.get("name", "CI")
            
            if status == "completed":
                if conclusion == "success":
                    print(f"   ✅ Current Commit CI: {GREEN}success{RESET} ({name})")
                else:
                    print(f"   ❌ Current Commit CI: {RED}{conclusion}{RESET} ({name}) -> {url}")
            else:
                print(f"   ⚙️  Current Commit CI: {YELLOW}{status}{RESET} ({name}) -> {url}")
        else:
            print("   ⚙️  Current Commit CI: Queued / Starting on GitHub...")
            
        # 2. Search for the last completed CI run
        last_completed = None
        for run in runs:
            if run.get("status") == "completed" and run != current_run:
                last_completed = run
                break
                
        if last_completed:
            conclusion = last_completed.get("conclusion")
            url = last_completed.get("url")
            name = last_completed.get("name", "CI")
            
            if conclusion == "success":
                print(f"   ✅ Previous CI Run: {GREEN}success{RESET} ({name})")
            else:
                print(f"   ⚠️  Previous CI Run: {RED}{conclusion}{RESET} ({name}) -> {url}")
                    
    except Exception as e:
        print(f"{DIM}   ⚠️ CI status check skipped: {e}{RESET}")


def git_commit(commit_msg: str | None = None, push: bool = False) -> bool:
    """Git add + commit (synchronous) + optional verified push."""
    print("📦 Committing changes...")

    # Stage all
    _, stderr, code = _run_git(["add", "-A"])
    if code != 0:
        print(f"{YELLOW}⚠️ Git add failed: {stderr}{RESET}")
        return False

    # Check if anything to commit
    stdout, _, _ = _run_git(["status", "--porcelain"])
    if not stdout.strip():
        print(f"{GREEN}✓ Working directory clean.{RESET}")
    else:
        # Commit
        if not commit_msg:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_msg = f"chore(session): close {time_str}"
        _, stderr, code = _run_git(["commit", "-m", commit_msg])
        if code != 0 and "nothing to commit" not in stderr:
            print(f"{YELLOW}⚠️ Git commit failed: {stderr}{RESET}")
            return False
        print(f"{GREEN}✓ Committed locally.{RESET}")

    # Optional verified push (bounded, fast-forward-only, never silent on failure).
    if push:
        git_push_verified()
    else:
        print(f"{DIM}ℹ️ Remote push skipped (local commit only; pass --push to push to remote).{RESET}")

    return True


# ============================================================
# MICRO PATH — Git-only close (~3s)
# ============================================================


def micro_close(push: bool = False) -> int:
    """Fast-path shutdown: git commit only. No compilation, no compliance."""
    divider("🔒 ATHENA SHUTDOWN (MICRO)")

    if not git_commit("chore(session): close (micro)", push=push):
        print(f"{YELLOW}⚠️ Git commit had issues{RESET}")

    time_now = datetime.now().strftime("%H:%M SGT")
    print(f"\n{GREEN}{BOLD}✅ Session closed (micro).{RESET} Time: {time_now}")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
    return 0


# ============================================================
# SESSION COMPILATION (Phase 0) — Full path only
# ============================================================


def extract_keyphrases(content: str) -> str:
    """Extract dominant topic from checkpoints (deterministic, no NLP)."""
    checkpoints = re.findall(
        r"### ⚡ Checkpoint \[.*?\]\n\n?(.*?)(?=\n###|\n## |$)", content, re.DOTALL
    )

    if len(checkpoints) < 2:
        return "General Development"

    text = " ".join(checkpoints[1:]).lower()
    words = re.findall(r"\b[a-z]{3,}\b", text)
    filtered = [w for w in words if w not in STOPWORDS]

    if not filtered:
        return "General Development"

    bigrams = []
    for i in range(len(filtered) - 1):
        bigrams.append(f"{filtered[i]} {filtered[i + 1]}")

    if bigrams:
        counter = Counter(bigrams)
        top_bigram = counter.most_common(1)[0][0]
        return top_bigram.title()

    counter = Counter(filtered)
    return counter.most_common(1)[0][0].title()


def extract_tags(content: str) -> list[str]:
    """Extract unique tags from session log."""
    tags = set(re.findall(r"#([\w-]+)", content))
    tags.discard("session")
    tags.discard("...")
    return sorted(list(tags))


def extract_threads(focus: str, tags: list[str], content: str) -> list[str]:
    """Auto-detect thread IDs from focus, tags, and content."""
    threads = []
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

    search_text = f"{focus} {' '.join(tags)} {content[:1000]}".lower()
    for thread_id, keywords in THREAD_PATTERNS.items():
        matches = sum(1 for kw in keywords if kw in search_text)
        if matches >= 2:
            threads.append(thread_id)

    return threads[:3]


def generate_r_block(metadata, lambda_stats, tags, decisions, actions) -> str:
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


def propagate_system_learnings(learnings, session_id, dry_run=False) -> int:
    """Append system learnings to SYSTEM_LEARNINGS.md."""
    if not learnings:
        return 0
    if not SYSTEM_LEARNINGS_FILE.exists():
        print(f"{YELLOW}⚠️ SYSTEM_LEARNINGS.md not found, skipping{RESET}")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    new_rows = [f"| {today} | {session_id} | {l} | ⏳ Pending |" for l in learnings]

    if dry_run:
        print(f"{DIM}[DRY-RUN] Would append {len(new_rows)} system learnings{RESET}")
        return len(new_rows)

    content = SYSTEM_LEARNINGS_FILE.read_text()
    table_end = content.rfind("|")
    if table_end != -1:
        line_end = content.find("\n", table_end)
        if line_end == -1:
            line_end = len(content)
        new_content = (
            content[:line_end] + "\n" + "\n".join(new_rows) + content[line_end:]
        )
        SYSTEM_LEARNINGS_FILE.write_text(new_content)

    return len(new_rows)


def propagate_user_learnings(learnings, session_id, dry_run=False) -> int:
    """Append user learnings to USER_PROFILE.yaml notes section safely."""
    if not learnings or not HAS_YAML:
        return 0
    if not USER_PROFILE_FILE.exists():
        print(f"{YELLOW}⚠️ USER_PROFILE.yaml not found, skipping{RESET}")
        return 0

    if dry_run:
        print(f"{DIM}[DRY-RUN] Would append {len(learnings)} user learnings{RESET}")
        return len(learnings)

    header_comment = """# User Profile (Machine-Readable Preferences)
# Auto-managed by shutdown.py from session [U] markers.
# Manual edits allowed for corrections.
"""
    try:
        content = USER_PROFILE_FILE.read_text()
        data = yaml.safe_load(content) or {}
    except Exception as e:
        print(f"{YELLOW}⚠️ Failed to parse USER_PROFILE.yaml: {e}{RESET}")
        return 0

    if "notes" not in data:
        data["notes"] = []

    for learning in learnings:
        data["notes"].append(
            {"learned": learning, "session": session_id, "confidence": "medium"}
        )

    try:
        yaml_str = yaml.dump(data, sort_keys=False, allow_unicode=True)
        USER_PROFILE_FILE.write_text(header_comment + "\n" + yaml_str)
    except Exception as e:
        print(f"{YELLOW}⚠️ Failed to write USER_PROFILE.yaml: {e}{RESET}")
        return 0

    return len(learnings)


def propagate_local_learnings(learnings, session_id, dry_run=False) -> int:
    """Append local codebase learnings to LESSONS.md if the file exists in PROJECT_ROOT."""
    if not learnings:
        return 0
    lessons_file = PROJECT_ROOT / "LESSONS.md"
    if not lessons_file.exists():
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    new_rows = [f"- **{today} ({session_id})**: {l}" for l in learnings]

    if dry_run:
        print(f"{DIM}[DRY-RUN] Would append {len(new_rows)} local codebase learnings to LESSONS.md{RESET}")
        return len(new_rows)

    try:
        content = lessons_file.read_text(encoding="utf-8")
        if not content.endswith("\n"):
            content += "\n"
        content += "\n".join(new_rows) + "\n"
        lessons_file.write_text(content, encoding="utf-8")
        print(f"   📝 Appended {len(new_rows)} local lessons to LESSONS.md")
    except Exception as e:
        print(f"{YELLOW}⚠️ Failed to write local lessons to LESSONS.md: {e}{RESET}")
        return 0

    return len(new_rows)



def validate_log_synthesis(content: str) -> bool:
    """Check if session log has placeholder content. Returns False if found."""
    critical_patterns = [
        r"## 1\. Agenda\s*\n\s*- \[ \] \.\.\.",
        r"\*\*Decision\*\*:\s*\.\.\.",
        r"\*\*Insight\*\*:\s*\.\.\.",
        r"\| \.\.\. \| AI / User \| Pending \|",
    ]
    for pattern in critical_patterns:
        if re.search(pattern, content):
            return False
    return True


def finalize_session_log(dry_run: bool = False) -> bool:
    """Main session compiler. Parses, computes, and updates the session log. Idempotent."""
    log_path = get_current_session_log()
    if not log_path:
        print(f"{DIM}No session log found — skipping compilation.{RESET}")
        return True  # Not an error — just nothing to do

    print(f"📋 Compiling session: {log_path.name}")
    content = log_path.read_text()
    metadata, body_start = parse_yaml_frontmatter(content)
    body = content[body_start:]

    if not metadata:
        print(f"{YELLOW}Legacy session log format detected — synthesizing frontmatter...{RESET}")
        today = datetime.now().strftime("%Y-%m-%d")
        metadata = {
            "session_id": log_path.stem,
            "date": today,
            "start": datetime.now().astimezone().isoformat(),
            "end": None,
            "duration_min": None,
            "status": "in_progress",
            "verdict": None,
            "prev_session": None,
            "next_session": None,
            "focus": extract_keyphrases(content),
            "threads": [],
            "tags": extract_tags(content),
            "lambda_peak": None,
            "lambda_total": None,
            "lambda_coverage": None,
            "lambda_coverage_n": None,
            "lambda_coverage_d": None,
        }
        body = content
        body_start = 0

    session_id = metadata.get("session_id", log_path.stem)
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
    metadata["threads"] = extract_threads(metadata.get("focus", ""), tags, content)

    # Calculate duration
    start_str = metadata.get("start", "")
    if start_str:
        try:
            start_time = datetime.fromisoformat(start_str)
            duration = (end_time - start_time).total_seconds() / 60
            metadata["duration_min"] = round(duration)
        except (ValueError, TypeError):
            pass

    r_block = generate_r_block(metadata, lambda_stats, tags, decisions, pending_actions)

    # Extract and propagate learnings
    system_learnings, user_learnings, integration_requests, local_learnings = extract_learnings(content)

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
        print(f"  Local Learnings: {len(local_learnings)}")
        propagate_system_learnings(system_learnings, session_id, dry_run=True)
        propagate_user_learnings(user_learnings, session_id, dry_run=True)
        propagate_local_learnings(local_learnings, session_id, dry_run=True)
        return True

    # Build new YAML frontmatter
    if HAS_YAML:
        new_frontmatter = (
            "---\n" + yaml.dump(metadata, sort_keys=False, allow_unicode=True) + "---\n"
        )
    else:
        lines = ["---"]
        for k, v in metadata.items():
            lines.append(f"{k}: {v}")
        lines.append("---\n")
        new_frontmatter = "\n".join(lines)

    # Update R__ block in body
    r_block_pattern = (
        r"## 0\. R__ Compressed Context\n\n>.*?\n\n```text\n\[\[ R__ \|.*?\]\]\n```"
    )
    new_r_section = f"## 0. R__ Compressed Context\n\n> Auto-generated on close by `shutdown.py`. Do not manually edit.\n\n{r_block}"
    body = re.sub(r_block_pattern, new_r_section, body, flags=re.DOTALL)

    log_path.write_text(new_frontmatter + body)

    # Propagate learnings
    sys_count = propagate_system_learnings(system_learnings, session_id)
    user_count = propagate_user_learnings(user_learnings, session_id)
    local_count = propagate_local_learnings(local_learnings, session_id)

    # Sentinel Check (Protocol 420) — shutdown sentinel only, no activeContext write
    sentinel_msg = check_shutdown_sentinel(log_path)

    print(f"{GREEN}✅ Session compiled{RESET}")
    print(f"   📊 Focus: {metadata.get('focus', 'Unknown')}")
    print(f"   ⏱️  Duration: {metadata.get('duration_min', '?')} min")
    print(
        f"   ⚡ Λ Peak: {lambda_stats['peak']} | Total: {lambda_stats['total']} | Coverage: {lambda_stats['coverage']}"
    )
    if sys_count or user_count or local_count:
        print(f"   📚 Learnings propagated: {sys_count} system, {user_count} user, {local_count} local")
    if sentinel_msg:
        print(f"\n{YELLOW}{sentinel_msg}{RESET}")

    return True


# ============================================================
# HARVEST CHECK (Phase 1)
# ============================================================


def harvest_check_background():
    """Fire-and-forget harvest check."""
    try:
        subprocess.Popen(
            ["python3", str(SCRIPTS_DIR / "harvest_check.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception:
        pass


def reflexion_harvest_background():
    """Fire-and-forget Reflexion harvest (P515). Self-throttled to weekly; idempotent."""
    try:
        subprocess.Popen(
            ["python3", str(SCRIPTS_DIR / "reflexion_harvester.py"),
             "--apply", "--if-stale", "7", "--min-count", "3", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception:
        pass


# ============================================================
# COMPLIANCE (Phase 3)
# ============================================================


def run_compliance():
    """Generate compliance report and reset. Uses top-level imports."""
    if not HAS_COMPLIANCE:
        return

    try:
        report = compliance_generate_report()
        if report:
            print(report)
        compliance_update_log()
        compliance_reset()
        print(f"{GREEN}✅ Violations reset for next session{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ Compliance failed: {e}{RESET}")


# ============================================================
# PRE-COMPACTION STATE FLUSH (Phase 4a — OpenClaw Pattern)
# ============================================================


def flush_critical_state():
    """Flush critical state to protected sections BEFORE any compaction.

    The 'OpenClaw' pattern from research: before ANY compactor runs,
    extract and protect the current working state so it survives
    summarization. This prevents the 'I just forgot what I was doing'
    failure mode.

    Protected sections (## Current Focus, ## Active Tasks, ## System Status)
    are left in place. This function ensures they contain the latest state.
    """
    context_file = PROJECT_ROOT / ".context" / "memory_bank" / "activeContext.md"
    if not context_file.exists():
        return

    try:
        content = context_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        line_count = len(lines)

        # Only flush if the file is large enough to warrant compaction
        # Trigger rule: > 100 lines (token check requires tiktoken, skip here)
        if line_count <= 100:
            return

        # Ensure ## System Status has the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M SGT")
        status_marker = "## System Status"

        if status_marker in content:
            # Find the line after ## System Status and update the health timestamp
            sections = content.split(status_marker)
            status_body = sections[1] if len(sections) > 1 else ""

            # Add/update a last-compaction timestamp
            flush_line = f"- **Last State Flush**: {timestamp}"
            if "**Last State Flush**" in status_body:
                # Replace existing flush line
                import re

                status_body = re.sub(
                    r"- \*\*Last State Flush\*\*:.*",
                    flush_line,
                    status_body,
                )
            else:
                # Insert after the first line of the status section
                first_newline = status_body.find("\n")
                if first_newline != -1:
                    next_newline = status_body.find("\n", first_newline + 1)
                    if next_newline != -1:
                        status_body = (
                            status_body[:next_newline]
                            + "\n"
                            + flush_line
                            + status_body[next_newline:]
                        )

            content = sections[0] + status_marker + status_body
            context_file.write_text(content, encoding="utf-8")
            print(f"{DIM}💾 State flush → activeContext.md ({line_count} lines){RESET}")

    except Exception as e:
        # Non-fatal — don't break shutdown if flush fails
        print(f"{DIM}⚠️ State flush skipped: {e}{RESET}")


# ============================================================
# AUTO-HYGIENE (Phase 4b — background)
# ============================================================


def auto_hygiene_background():
    """Fire-and-forget session compression."""
    try:
        subprocess.Popen(
            ["python3", str(SCRIPTS_DIR / "compress_sessions.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception:
        pass


# ============================================================
# MEMORY RECONCILIATION (Phase 4c — background)
# ============================================================


def reconcile_memory_background():
    """Fire-and-forget memory reconciliation."""
    try:
        subprocess.Popen(
            ["python3", str(SCRIPTS_DIR / "reconcile_memory.py"), "--execute"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception:
        pass


# ============================================================
# RETRIEVAL EVALUATION (Phase 4d — background)
# ============================================================


def evaluator_background():
    """Fire-and-forget retrieval evaluation."""
    try:
        subprocess.Popen(
            ["python3", str(SCRIPTS_DIR / "evaluator.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception:
        pass


def vector_sync_background():
    """Fire-and-forget delta vector sync.

    Root cause of the 2026-07-03 retrieval regression: NOTHING automated
    supabase_sync.py, so the semantic index silently drifted 13 days behind the
    corpus (149 session logs unembedded). Session close is the natural sync
    point — the delta manifest makes repeat runs cheap (mtime-based skip).
    Logged to .agent/telemetry/vector_sync.log so drift is diagnosable.

    Refreshes the cross-domain report-up digests FIRST (sync_domain_digest.py)
    so the delta sync embeds current life-area state (finance, malaysia, …),
    not last session's. Fast, no network; guarded so it can never block the sync.
    """
    try:
        subprocess.run(
            ["python3", str(SCRIPTS_DIR / "sync_domain_digest.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
    except Exception:
        pass

    try:
        log_path = PROJECT_ROOT / ".agent" / "telemetry" / "vector_sync.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as log_file:
            log_file.write(f"\n--- sync @ {datetime.now().isoformat()} ---\n")
            log_file.flush()
            subprocess.Popen(
                ["python3", str(SCRIPTS_DIR / "supabase_sync.py")],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=str(PROJECT_ROOT),
                start_new_session=True,
            )
    except Exception:
        pass


# ============================================================
# EMERGENCY HATCH
# ============================================================


def safe_commit():
    """Emergency commit if main orchestrator fails."""
    print(f"\n{RED}{BOLD}🚨 EMERGENCY COMMIT TRIGGERED{RESET}")
    try:
        _run_git(["add", "-A"])
        _run_git(["commit", "-m", "emergency: save state on shutdown failure"])
        subprocess.Popen(
            ["git", "push"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
        print(f"{GREEN}✅ Emergency Save Complete.{RESET}")
    except Exception as e:
        print(f"{RED}❌ Emergency Save Failed: {e}{RESET}")


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Athena Shutdown Orchestrator & Session Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--micro",
        action="store_true",
        help="Fast-path: git commit only (skips compilation, compliance, harvest).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview shutdown sequence without making mutations.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push git commit to remote repository.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Athena Shutdown Orchestrator v2.0",
    )

    args = parser.parse_args()

    dry_run = args.dry_run
    micro = args.micro
    push = args.push

    # Deterministic /end telemetry (TD-057): the prompt hook only fires on
    # slash-prefixed prompts in Claude Code, so shutdown.py is the reliable producer.
    if not dry_run:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from log_invocation import log_invocation

            log_invocation("workflow", "end", trigger="auto: shutdown.py")
        except Exception:
            pass

    # MICRO PATH — git-only close
    if micro:
        return micro_close(push=push)

    # FULL PATH — complete shutdown sequence
    divider("🔒 ATHENA SHUTDOWN SEQUENCE (Titanium Protocol v2)")

    exit_code = 0

    try:
        # Phase 0: Session Compilation
        print(f"{BOLD}📋 Phase 0: Session Compilation{RESET}")

        log_path = get_current_session_log()
        if log_path:
            content = log_path.read_text()
            if not validate_log_synthesis(content):
                print(
                    f"\n{YELLOW}{BOLD}⚠️ WARNING: Incomplete Session Log detected.{RESET}"
                )
                print(f"{YELLOW}Proceeding with shutdown to preserve data.{RESET}")

        if not finalize_session_log(dry_run=dry_run):
            print(f"{YELLOW}⚠️ Session finalization had issues (skipping){RESET}")
        print()

        if dry_run:
            print(f"\n{BOLD}{CYAN}[DRY-RUN MODE] No changes written. Exiting.{RESET}\n")
            return 0

        # Phase 1: Harvest check (background)
        harvest_check_background()
        reflexion_harvest_background()  # P515 failure-delta mining (weekly self-throttle)

        # Phase 1.5: CAPS→AGENTS.md sync (TD-028)
        try:
            if SYNC_SCRIPT.exists():
                result = subprocess.run(
                    ["python3", str(SYNC_SCRIPT)],
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_ROOT),
                    timeout=5,
                )
                if result.returncode == 0:
                    # Only print if patches were applied (not "already in sync")
                    for line in result.stdout.strip().split("\n"):
                        if "[PATCH]" in line or "patched" in line:
                            print(f"{GREEN}{line.strip()}{RESET}")
        except Exception as e:
            print(f"{DIM}⚠️ CAPS sync skipped: {e}{RESET}")

        # Phase 2: Git commit + optional push
        if git_commit(push=push):
            if push:
                check_ci_status()
        else:
            print(f"{YELLOW}⚠️ Git commit had issues{RESET}")
            exit_code = 1

        # Phase 3: Compliance (inlined, top-level imports)
        run_compliance()

        # Phase 4a: Pre-compaction state flush (in-process, fast)
        flush_critical_state()

        # Phase 4b: Auto-Hygiene (background)
        auto_hygiene_background()

        # Phase 4c: Memory Reconciliation (background)
        reconcile_memory_background()

        # Phase 4d: Vector index delta sync (background) — BEFORE the evaluator
        # so freshly filed session logs are embedded by the time eval runs next.
        vector_sync_background()

        # Phase 4e: Retrieval Evaluation (background)
        evaluator_background()

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
        print(f"\n{RED}❌ CRITICAL SHUTDOWN FAILURE: {e}{RESET}")
        import traceback

        traceback.print_exc()

        if not dry_run:
            safe_commit()

        return 1


if __name__ == "__main__":
    sys.exit(main())
