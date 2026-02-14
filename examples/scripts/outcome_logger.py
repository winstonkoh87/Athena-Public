#!/usr/bin/env python3
"""
Outcome Logger (The Scoreboard)
===============================
Tracks "Shipping Velocity" by logging high-value events.
Used to calculate the "Slope" of the project.

Events:
- SHIP (+5): Deployment, Release, Final Artifact
- MERGE (+3): PR Merge, Code Integration
- DECIDE (+2): Key Strategic Decision
- META (+0.5): Protocol, Refactor, Planning

Usage:
  python3 outcome_logger.py --event <type> --desc "Description" --link "Link/ID"
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
OUTCOME_LOG = CONTEXT_DIR / "outcomes.log" # Text based log
OUTCOME_DB = CONTEXT_DIR / "outcomes.jsonl" # Structured data

# Scoring Map (Base Points)
SCORES = {
    "SHIP": 5.0,   # Deployment / Final Artifact
    "MERGE": 3.0,  # Code Integration
    "DECIDE": 2.0, # Strategic Decision
    "META": 0.5    # Refactoring / Planning
}

# Scope Multipliers (Prevent trivial spam)
SCOPE_MULTIPLIERS = {
    "small": 1.0,  # Typos, single-file (Default)
    "medium": 2.0, # Feature, Protocol
    "large": 3.0   # Major Release, Architecture Overhaul
}

def log_outcome(event_type: str, description: str, link: str = None, scope: str = "small"):
    """Log an outcome to the ledger."""
    if event_type not in SCORES:
        raise ValueError(f"Invalid event type: {event_type}. Valid: {list(SCORES.keys())}")
    
    if scope not in SCOPE_MULTIPLIERS:
         scope = "small"
         
    # Trust the user. No strict validation.
    # The ledger is a mirror, not a judge.

    base_score = SCORES[event_type]
    multiplier = SCOPE_MULTIPLIERS.get(scope, 1.0) # Default to 1.0 if not found
    
    # Remove artificial caps. If the user says it's a large META task, so be it.
    # if event_type == "META":
    #     multiplier = 1.0 
        
    final_score = base_score * multiplier
    timestamp = datetime.now().isoformat()
    
    entry = {
        "timestamp": timestamp,
        "type": event_type,
        "scope": scope,
        "score": final_score,
        "description": description,
        "link": link
    }
    
    # 1. Append to JSONL (Machine Readable)
    with open(OUTCOME_DB, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        
    # 2. Append to Human Log (Text)
    log_line = f"[{timestamp[:16]}] [{event_type}] ({final_score}) [{scope.upper()}] {description}"
    if link:
        log_line += f" -> {link}"
        
    # Check if we need to create the file (and header)
    if not OUTCOME_LOG.exists():
        OUTCOME_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTCOME_LOG, "w") as f:
            f.write("# Outcome Ledger (The Project Scoreboard)\n")
            f.write(f"# Since: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            
    with open(OUTCOME_LOG, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        
    print(f"✅ Logged Outcome: {event_type} (+{final_score})")
    print(f"   {description}")

def main():
    parser = argparse.ArgumentParser(description="Log a project outcome")
    parser.add_argument("--event", type=str.upper, required=True, choices=SCORES.keys(), help="Event type")
    parser.add_argument("--desc", type=str, required=True, help="Description of what happened")
    parser.add_argument("--link", type=str, help="Link to artifact or PR (Optional)")
    parser.add_argument("--scope", type=str.lower, choices=SCOPE_MULTIPLIERS.keys(), default="small", help="Impact scope (small/medium/large)")
    
    args = parser.parse_args()
    
    log_outcome(args.event, args.desc, args.link, args.scope)

if __name__ == "__main__":
    main()
