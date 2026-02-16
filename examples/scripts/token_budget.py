#!/usr/bin/env python3
"""
Token Budget Calculator
Estimates token count for Codex files to prevent context overflow.
Uses tiktoken (if available) or word-based approximation.

Latency Architecture:
- BOOT files: Loaded immediately on /start (low latency target)
- ON_DEMAND files: Loaded when triggered by specific query types
"""

import os
import sys

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Files loaded IMMEDIATELY on /start (ultra-lean boot)
BOOT_FILES = [
    ".framework/v7.0/modules/Core_Identity.md",
]

# Files loaded ON-DEMAND during session (adaptive latency)
ON_DEMAND_FILES = [
    (".context/TAG_INDEX.md", "Tag lookup, file search"),
    (".agent/skills/SKILL_INDEX.md", "Protocol/skill request"),
    # User Profile Modules (split from monolithic User_Profile.md)
    (".context/profile/User_Profile_Core.md", "Bio, typology, 'who am I'"),
    (".context/profile/Psychology_L1L5.md", "L1-L5, trauma, therapy, fantasy"),
    (".context/profile/Operating_Principles.md", "Decision frameworks, strategy"),
    (".context/profile/Business_Frameworks.md", "Marketing, SEO, SWOT, pricing"),
    (".context/profile/Session_Observations.md", "Calibration references, cases"),
    (".framework/v7.0/modules/Output_Standards.md", "/think or /ultrathink"),
    (".context/profile/Constraints_Master.md", "Ethical edge case"),
    (".context/System_Manifest.md", "Architecture query"),
]

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"
MAGENTA = "\033[95m"

# Thresholds
# Thresholds
# Pricing Cliff at 200k tokens (Price doubles from $2 to $4 per 1M)
GREEN_ZONE_LIMIT = 150000    # Safe operating zone
WARNING_THRESHOLD = 180000   # Approaching the cliff
CRITICAL_THRESHOLD = 200000  # Price doubles beyond this point (RED ZONE)


def estimate_tokens(text):
    """
    Estimates token count.
    Uses tiktoken if available, otherwise ~4 chars per token approximation.
    """
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))
    except ImportError:
        # Fallback: ~4 characters per token (rough approximation)
        return len(text) // 4


def format_tokens(count):
    """Formats token count with comma separators."""
    return f"{count:,}"


def get_status_indicator(count, is_boot=True):
    """Returns status emoji based on token count."""
    if is_boot:
        if count >= CRITICAL_THRESHOLD:
            return f"{RED}⚠️  HEAVY{RESET}"
        elif count >= WARNING_THRESHOLD:
            return f"{YELLOW}📊 MEDIUM{RESET}"
        else:
            return f"{GREEN}✓  LIGHT{RESET}"
    else:
        # On-demand files have looser thresholds
        if count >= 15000:
            return f"{YELLOW}📊 MEDIUM{RESET}"
        else:
            return f"{GREEN}✓  LIGHT{RESET}"


def analyze_file(relative_path):
    """Analyzes a single file and returns token count."""
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    
    if not os.path.exists(full_path):
        return None, f"File not found"
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return estimate_tokens(content), None
    except Exception as e:
        return None, str(e)


def main():
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}              📊 CODEX TOKEN BUDGET REPORT                      {RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: BOOT FILES (loaded on /start)
    # ═══════════════════════════════════════════════════════════════
    boot_total = 0
    boot_results = []
    
    print(f"{BOLD}{GREEN}⚡ BOOT LOAD (Low Latency Target):{RESET}\n")
    
    for rel_path in BOOT_FILES:
        tokens, error = analyze_file(rel_path)
        filename = os.path.basename(rel_path)
        
        if error:
            print(f"  {RED}✗{RESET} {filename}: {error}")
        else:
            boot_total += tokens
            status = get_status_indicator(tokens, is_boot=True)
            boot_results.append((filename, tokens))
            print(f"  {filename:<35} │ {format_tokens(tokens):>8} tokens  {status}")
    
    print(f"\n{DIM}{'─' * 63}{RESET}")
    print(f"{BOLD}{GREEN}  /start BOOT TOTAL{' ' * 16} │ {format_tokens(boot_total):>8} tokens{RESET}")
    print(f"{DIM}{'─' * 63}{RESET}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: ON-DEMAND FILES (loaded when triggered)
    # ═══════════════════════════════════════════════════════════════
    on_demand_total = 0
    on_demand_results = []
    
    print(f"{BOLD}{MAGENTA}📦 ON-DEMAND RESERVES (Adaptive Loading):{RESET}\n")
    
    for rel_path, trigger in ON_DEMAND_FILES:
        tokens, error = analyze_file(rel_path)
        filename = os.path.basename(rel_path)
        
        if error:
            print(f"  {RED}✗{RESET} {filename}: {error}")
        else:
            on_demand_total += tokens
            status = get_status_indicator(tokens, is_boot=False)
            on_demand_results.append((filename, tokens, trigger))
            print(f"  {filename:<30} │ {format_tokens(tokens):>7} │ {DIM}{trigger}{RESET}")
    
    print(f"\n{DIM}{'─' * 63}{RESET}")
    print(f"{BOLD}{MAGENTA}  ON-DEMAND RESERVE TOTAL{' ' * 10} │ {format_tokens(on_demand_total):>8} tokens{RESET}")
    print(f"{DIM}{'─' * 63}{RESET}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: SUMMARY
    # ═══════════════════════════════════════════════════════════════
    total_all = boot_total + on_demand_total
    PRACTICAL_LIMIT = 200000
    boot_pct = (boot_total / PRACTICAL_LIMIT) * 100
    total_pct = (total_all / PRACTICAL_LIMIT) * 100
    
    print(f"{BOLD}Context Budget:{RESET}")
    print(f"  Boot load:    {format_tokens(boot_total):>8} ({boot_pct:.1f}%)")
    print(f"  + On-demand:  {format_tokens(on_demand_total):>8}")
    print(f"  = Max total:  {format_tokens(total_all):>8} ({total_pct:.1f}%)")
    
    if total_all > CRITICAL_THRESHOLD:
         print(f"\n  {RED}💰 ALERT: CONTEXT > 200K. PRICING HAS DOUBLED ($2 -> $4).{RESET}")
    elif total_all > WARNING_THRESHOLD:
         print(f"\n  {YELLOW}⚠️  WARNING: Approaching 200K Pricing Cliff. Wrap up session soon.{RESET}")
    else:
         print(f"\n  {GREEN}💰 Pricing Tier: Standard ($2/1M input). Safe.{RESET}")
    
    # Progress bar (boot only)
    bar_width = 40
    filled = int(bar_width * min(boot_pct, 100) / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    if boot_pct > 5:
        bar_color = RED
    elif boot_pct > 2:
        bar_color = YELLOW
    else:
        bar_color = GREEN
    
    print(f"\n  Boot: [{bar_color}{bar}{RESET}] {boot_pct:.1f}%\n")
    
    # Verdict
    if boot_total <= 3000:
        print(f"{GREEN}✓ Boot load optimized. Low latency /start achieved.{RESET}\n")
    elif boot_total <= 5000:
        print(f"{YELLOW}⚠️ Boot load acceptable but could be reduced.{RESET}\n")
    else:
        print(f"{RED}⚠️ Boot load too heavy. Consider reducing BOOT_FILES.{RESET}\n")
    
    # Top consumers
    print(f"{BOLD}Heaviest On-Demand Files:{RESET}")
    sorted_on_demand = sorted(on_demand_results, key=lambda x: x[1], reverse=True)
    for i, (name, tokens, trigger) in enumerate(sorted_on_demand[:3], 1):
        pct = (tokens / on_demand_total) * 100 if on_demand_total > 0 else 0
        print(f"  {i}. {name}: {format_tokens(tokens)} ({pct:.0f}%)")
    
    print()


if __name__ == "__main__":
    main()
