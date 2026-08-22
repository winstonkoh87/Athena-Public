"""
athena.boot.loaders.token_budget
=================================
15K Hard-Cap Token Budget Gauge for the /start workflow.

Counts tokens loaded at boot, displays an ASCII progress bar,
and triggers auto-compaction of activeContext.md when the budget
is exceeded.

Operating Band:
  10K (post-compact target) ←→ 15K (hard cap, triggers compact)
"""

import sys
from pathlib import Path

from athena.boot.constants import (
    BOLD,
    BOOT_FILES,
    CYAN,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
)

# === Budget Constants ===
HARD_CAP = 20_000  # Tokens — triggers auto-compaction (SPEC_SHEET.md ceiling)
ECL = 200_000  # Effective Context Length (model budget)
BOOT_SCRIPT_ESTIMATE = 2_000  # Fixed estimate for boot.py output overhead
SYSTEM_INSTRUCTIONS_ESTIMATE = 3_000  # Fixed estimate for IDE-injected system prompt
MAX_COMPACT_PASSES = 3  # Safety: max compaction retries


def count_tokens(text: str) -> int:
    """
    Count tokens using tiktoken (cl100k_base).
    Falls back to len(text) // 4 if tiktoken is unavailable.
    """
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except (ImportError, Exception):
        return len(text) // 4


def measure_boot_files() -> dict:
    """
    Read the 3 canonical Memory Bank files and return per-file token counts.
    Also includes fixed estimates for boot.py output and system instructions.

    Returns:
        dict: {"filename": token_count, ...}
    """
    counts = {}
    for name, path in BOOT_FILES.items():
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                counts[name] = count_tokens(content)
            except Exception:
                counts[name] = 0
        else:
            counts[name] = 0

    counts["boot.py output"] = BOOT_SCRIPT_ESTIMATE
    counts["System instructions"] = SYSTEM_INSTRUCTIONS_ESTIMATE
    return counts


def _build_bar(total: int, width: int = 15) -> str:
    """Build an ASCII progress bar from 0K to 20K."""
    fill_ratio = min(total / HARD_CAP, 1.2)  # allow slight overflow for visual
    filled = int(fill_ratio * width)
    filled = max(0, min(filled, width + 2))  # clamp
    bar_filled = "█" * min(filled, width)
    bar_empty = "░" * max(0, width - filled)
    overflow = "██" if filled > width else ""
    return f"{bar_filled}{bar_empty}{overflow}"


def display_gauge(token_counts: dict = None) -> bool:
    """
    Print the token budget gauge.

    Args:
        token_counts: Pre-measured counts. If None, measures automatically.

    Returns:
        True if total >= HARD_CAP (compaction needed), False otherwise.
    """
    if token_counts is None:
        token_counts = measure_boot_files()

    total = sum(token_counts.values())
    over_budget = total >= HARD_CAP
    remaining = ECL - total

    # Header
    print(f"\n{CYAN}{BOLD}📊 Token Budget:{RESET}")

    # Per-file breakdown
    for name, count in token_counts.items():
        indicator = "✅"
        if name == "activeContext.md" and over_budget:
            indicator = "🔴"
        print(f"   {indicator} {name:<25} {count:>6,} tokens")

    # Divider
    print(f"   {'─' * 42}")

    # Total
    color = RED if over_budget else GREEN
    status = " 🔴 OVER CAP" if over_budget else ""
    print(f"   {color}{BOLD}Total: {total:>6,} / {HARD_CAP:,} tokens{status}{RESET}")

    # Bar
    bar = _build_bar(total)
    marker_pos = f"{total / 1000:.1f}K"
    if over_budget:
        print(f"   0K {bar} 20K ← {RED}{marker_pos}{RESET}")
    else:
        print(f"   0K {bar} 20K")

    # Remaining
    remaining_k = remaining // 1000
    print(f"   {DIM}💡 ~{remaining_k}K tokens available for this session.{RESET}")

    return over_budget


def auto_compact_if_needed(token_counts: dict = None) -> dict:
    """
    If boot tokens >= HARD_CAP, trigger compaction and re-measure.

    Args:
        token_counts: Pre-measured counts. If None, measures automatically.

    Returns:
        Final token counts after any compaction.
    """
    if token_counts is None:
        token_counts = measure_boot_files()

    total = sum(token_counts.values())
    if total < HARD_CAP:
        return token_counts

    # Import compact_context
    try:
        from athena.core.config import PROJECT_ROOT
        sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
        from compact_context import compact_active_context
    except ImportError as e:
        print(f"   {RED}❌ Cannot import compact_context: {e}{RESET}")
        return token_counts

    before_tokens = token_counts.get("activeContext.md", 0)

    for attempt in range(1, MAX_COMPACT_PASSES + 1):
        print(
            f"\n   {YELLOW}🔧 Auto-compacting activeContext.md (pass {attempt}/{MAX_COMPACT_PASSES})...{RESET}"
        )

        aggressive = attempt > 1  # first pass normal, subsequent passes aggressive
        compact_active_context(aggressive=aggressive)

        # Re-measure
        token_counts = measure_boot_files()
        new_total = sum(token_counts.values())

        if new_total < HARD_CAP:
            after_tokens = token_counts.get("activeContext.md", 0)
            print(
                f"   {GREEN}✅ Compacted: {before_tokens:,} → {after_tokens:,} tokens{RESET}"
            )
            break
    else:
        print(
            f"   {RED}⚠️  Compaction exhausted ({MAX_COMPACT_PASSES} passes). Boot proceeding over budget.{RESET}"
        )

    return token_counts
