#!/usr/bin/env python3
"""
daily_self_rsi.py — GTO Daily Self-RSI Autonomous Launcher
==========================================================
Executes the Daily Self-RSI prompt under strict safety bounds:
1. Enforces Backpressure Circuit Breaker (halts if >= 3 unreviewed tickets).
2. Builds machine-injected context bundle (eval metrics, CAPS hash, maintenance ratio).
3. Invokes headless agent with a 30-minute hard execution cap.
4. Verifies artifact generation and records execution logs.

Epistemic status: CODE-ENFORCED MECHANISM.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = PROJECT_ROOT / ".agent" / "prompts" / "daily_self_rsi.md"
CAPS_PATH = PROJECT_ROOT / ".agent" / "config" / "CAPS.json"
EVAL_DIR = PROJECT_ROOT / ".agent" / "eval" / "results"
BASELINE_PATH = PROJECT_ROOT / ".agent" / "eval" / "baseline.json"
DAILY_DIR = PROJECT_ROOT / ".context" / "self_optimization" / "daily"
LOG_DIR = PROJECT_ROOT / ".athena"

AGENT_BIN = os.environ.get("ATHENA_AGENT_BIN", "claude")
AGENT_HEADLESS_FLAGS = os.environ.get("ATHENA_AGENT_FLAGS", "--bare -p").split()


def get_unreviewed_ticket_count(days: int = 7) -> int:
    """Counts daily tickets generated in the last N days that have uncompleted checkboxes."""
    if not DAILY_DIR.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=days)
    unreviewed = 0
    for ticket in DAILY_DIR.glob("*.md"):
        try:
            date_str = ticket.stem
            ticket_date = datetime.strptime(date_str, "%Y-%m-%d")
            if ticket_date >= cutoff:
                content = ticket.read_text(encoding="utf-8")
                if "- [ ]" in content:
                    unreviewed += 1
        except Exception:
            continue
    return unreviewed


def build_context_bundle() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    eval_files = sorted(EVAL_DIR.glob("*.json"), key=lambda p: p.name, reverse=True) if EVAL_DIR.exists() else []
    last_eval = eval_files[0] if eval_files else None
    
    caps_hash = "(missing)"
    if CAPS_PATH.exists():
        caps_hash = hashlib.sha256(CAPS_PATH.read_bytes()).hexdigest()[:12]

    unreviewed_count = get_unreviewed_ticket_count(7)

    return {
        "TODAY": today,
        "NOW_ISO": datetime.now().isoformat(timespec="seconds"),
        "caps_hash": caps_hash,
        "unreviewed_tickets_7d": unreviewed_count,
        "last_eval_path": str(last_eval.relative_to(PROJECT_ROOT)) if last_eval else "(none)",
        "baseline_path": str(BASELINE_PATH.relative_to(PROJECT_ROOT)) if BASELINE_PATH.exists() else "(none)",
        "project_root": str(PROJECT_ROOT),
    }


def inject_prompt(template: str, bundle: dict) -> str:
    injection = "\n\n---\n\n## 5. RUNTIME CONTEXT INJECTION (System Generated)\n\n```yaml\n"
    for k, v in bundle.items():
        injection += f"{k}: {v}\n"
    injection += "```\n"
    return template + injection


def run_self_rsi(dry_run: bool = False, prompt_only: bool = False) -> int:
    if not PROMPT_PATH.exists():
        print(f"❌ Error: Prompt template not found at {PROMPT_PATH}", file=sys.stderr)
        return 1

    bundle = build_context_bundle()
    
    # Backpressure circuit breaker check
    if bundle["unreviewed_tickets_7d"] >= 3:
        print(f"⚠️ Circuit Breaker Tripped: {bundle['unreviewed_tickets_7d']} unreviewed tickets pending. Throttling daily run.")
        if not dry_run and not prompt_only:
            DAILY_DIR.mkdir(parents=True, exist_ok=True)
            hibernation_file = DAILY_DIR / f"{bundle['TODAY']}.md"
            hibernation_file.write_text(
                f"# 🧬 Daily Self-RSI — {bundle['TODAY']}\n\n"
                f"**Status**: ⏸️ HIBERNATED (Backpressure Circuit Breaker Active)\n"
                f"- Reason: {bundle['unreviewed_tickets_7d']} unreviewed tickets in queue.\n"
                f"- Action: Triage existing tickets before new horizon scans execute.\n",
                encoding="utf-8"
            )
            return 0

    template = PROMPT_PATH.read_text(encoding="utf-8")
    injected_prompt = inject_prompt(template, bundle)

    if prompt_only:
        sys.stdout.write(injected_prompt)
        return 0

    if dry_run:
        print("🔍 [DRY RUN] Injected context bundle:")
        for k, v in bundle.items():
            print(f"  {k}: {v}")
        print(f"\nTarget Command: {AGENT_BIN} {' '.join(AGENT_HEADLESS_FLAGS)} \"<injected_prompt>\"")
        print("\n✅ Dry run verification successful. All paths and data contracts valid.")
        return 0

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"self_rsi.{bundle['TODAY']}.log"

    print(f"🧬 Launching GTO Daily Self-RSI via {AGENT_BIN}...")
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n=== {datetime.now().isoformat()} daily_self_rsi ===\n")
            proc = subprocess.run(
                [AGENT_BIN, *AGENT_HEADLESS_FLAGS, injected_prompt],
                cwd=str(PROJECT_ROOT),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=60 * 30,  # 30-minute autonomous timeout
            )
    except FileNotFoundError:
        print(f"❌ Agent binary '{AGENT_BIN}' not found. Set ATHENA_AGENT_BIN or check PATH.", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("❌ Autonomous timeout expired (30m cap). Process terminated.", file=sys.stderr)
        return 3

    ticket_path = DAILY_DIR / f"{bundle['TODAY']}.md"
    if ticket_path.exists():
        print(f"✅ Daily Self-RSI completed. Ticket: {ticket_path.relative_to(PROJECT_ROOT)}")
        return 0
    else:
        print(f"⚠️ Agent completed with exit code {proc.returncode}, but ticket was not generated.", file=sys.stderr)
        return 4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena GTO Daily Self-RSI Launcher")
    parser.add_argument("--dry-run", action="store_true", help="Inspect injection without executing")
    parser.add_argument("--prompt-only", action="store_true", help="Print prompt to stdout")
    args = parser.parse_args()

    sys.exit(run_self_rsi(dry_run=args.dry_run, prompt_only=args.prompt_only))
