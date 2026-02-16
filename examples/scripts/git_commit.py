#!/usr/bin/env python3
"""
Git Auto-Commit Script
Automatically stages and commits changes with a structured message.
Designed for /end workflow integration.
"""

import os
import subprocess
import sys
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def run_git(args, check=True):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else "", e.returncode
    except FileNotFoundError:
        return "", "Git not installed", 1


def check_git_repo():
    """Check if we're in a git repository."""
    stdout, stderr, code = run_git(["rev-parse", "--git-dir"], check=False)
    return code == 0


def get_status():
    """Get git status summary."""
    stdout, stderr, code = run_git(["status", "--porcelain"], check=False)
    if code != 0:
        return None
    
    lines = stdout.split("\n") if stdout else []
    modified = sum(1 for l in lines if l.startswith(" M") or l.startswith("M "))
    added = sum(1 for l in lines if l.startswith("A ") or l.startswith("??"))
    deleted = sum(1 for l in lines if l.startswith(" D") or l.startswith("D "))
    
    return {
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "total": len([l for l in lines if l.strip()]),
        "files": [l[3:] for l in lines if l.strip()]
    }


def generate_commit_message(status, use_ai=False):
    """Generate a structured commit message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Categorize changes
    files = status.get("files", [])
    
    categories = {
        "context": [],
        "framework": [],
        "agent": [],
        "projects": [],
        "other": []
    }
    
    for f in files:
        if ".context/" in f:
            categories["context"].append(f)
        elif ".framework/" in f:
            categories["framework"].append(f)
        elif ".agent/" in f:
            categories["agent"].append(f)
        elif "Projects/" in f:
            categories["projects"].append(f)
        else:
            categories["other"].append(f)
    
    # Build scope
    parts = []
    if categories["context"]:
        parts.append("context")
    if categories["framework"]:
        parts.append("framework")
    if categories["agent"]:
        parts.append("agent")
    if categories["projects"]:
        parts.append("projects")
    
    scope = ", ".join(parts) if parts else "misc"
    
    # AI-powered message generation
    if use_ai and len(files) > 0:
        try:
            ai_message = generate_ai_commit_message(status, scope)
            if ai_message:
                return ai_message
        except Exception as e:
            print(f"{YELLOW}⚠️ AI generation failed: {e}. Using default.{RESET}")
    
    # Default message
    title = f"[{scope}] Session update ({timestamp})"
    
    body_lines = [
        "",
        f"Modified: {status['modified']} | Added: {status['added']} | Deleted: {status['deleted']}",
        ""
    ]
    
    # Add file list (truncated if too long)
    if len(files) <= 10:
        body_lines.append("Files changed:")
        for f in files:
            body_lines.append(f"  - {f}")
    else:
        body_lines.append(f"Files changed: {len(files)} (see git diff for details)")
    
    return title + "\n" + "\n".join(body_lines)


def generate_ai_commit_message(status, scope):
    """Generate semantic commit message using Gemini."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from gemini_client import get_client
    
    # Get diff
    diff_output, _, code = run_git(["diff", "--cached", "--stat"], check=False)
    if not diff_output:
        diff_output, _, _ = run_git(["diff", "--stat"], check=False)
    
    files = status.get("files", [])
    
    prompt = f"""Generate a semantic git commit message for these changes.

Scope: {scope}
Files: {', '.join(files[:20])}

Diff summary:
{diff_output[:2000]}

Rules:
1. First line: type(scope): description (max 72 chars)
   Types: feat, fix, refactor, docs, chore, style, perf
2. Blank line
3. Brief body explaining WHAT and WHY (not HOW)
4. Keep it concise - 3-5 lines max

Output only the commit message, nothing else."""

    client = get_client()
    response = client.generate(prompt)
    
    # Clean up response
    message = response.strip()
    if message.startswith("```"):
        message = message.split("```")[1].strip()
    
    return message


def review_diff():
    """Review staged diff using Gemini for issues."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from gemini_client import get_client
    
    diff_output, _, code = run_git(["diff", "--cached"], check=False)
    if not diff_output:
        return None
    
    prompt = f"""You are a code reviewer. Review this git diff for issues.

Check for:
1. Debug prints/console.logs left in
2. Hardcoded secrets or API keys
3. Obvious bugs or typos
4. Missing error handling
5. Code that could break existing functionality

Diff:
{diff_output[:5000]}

If no issues found, respond with: "✓ No issues found"
If issues found, list them briefly:
- Issue 1
- Issue 2
..."""
    
    try:
        client = get_client()
        return client.generate(prompt)
    except Exception as e:
        return f"Review failed: {e}"


def push_changes():
    """Push changes to remote origin."""
    print(f"{DIM}Pushing to origin...{RESET}")
    stdout, stderr, code = run_git(["push"], check=False)
    
    if code != 0:
        print(f"{RED}✗ Push failed: {stderr}{RESET}\n")
        return False
    else:
        print(f"{GREEN}✓ Pushed to origin successfully! 🚀{RESET}\n")
        return True


def main():
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}              🔄 GIT AUTO-COMMIT & PUSH                        {RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    # Check git repo
    if not check_git_repo():
        print(f"{RED}✗ Not a git repository.{RESET}")
        print(f"{DIM}  Initialize with: git init{RESET}\n")
        sys.exit(1)
    
    # Get status
    status = get_status()
    if status is None:
        print(f"{RED}✗ Failed to get git status.{RESET}\n")
        sys.exit(1)
    
    if status["total"] == 0:
        print(f"{GREEN}✓ Working directory clean. Checking for unpushed commits...{RESET}\n")
        # Optional: Check if we need to push anyway
        push_changes()
        sys.exit(0)
    
    # Show status
    print(f"{BOLD}Changes detected:{RESET}")
    print(f"  Modified: {status['modified']}")
    print(f"  Added:    {status['added']}")
    print(f"  Deleted:  {status['deleted']}")
    print()
    
    # Stage all changes
    print(f"{DIM}Staging changes...{RESET}")
    stdout, stderr, code = run_git(["add", "-A"], check=False)
    if code != 0:
        print(f"{RED}✗ Failed to stage changes: {stderr}{RESET}\n")
        sys.exit(1)
    
    # Generate and show commit message
    message = generate_commit_message(status)
    print(f"{BOLD}Commit message:{RESET}")
    print(f"{DIM}{'─' * 50}{RESET}")
    print(message)
    print(f"{DIM}{'─' * 50}{RESET}\n")
    
    # Commit
    print(f"{DIM}Committing...{RESET}")
    stdout, stderr, code = run_git(["commit", "-m", message], check=False)
    
    if code != 0:
        if "nothing to commit" in stderr or "nothing to commit" in stdout:
            print(f"{GREEN}✓ Nothing to commit (already up to date).{RESET}\n")
            push_changes()
        else:
            print(f"{RED}✗ Commit failed: {stderr}{RESET}\n")
            sys.exit(1)
    else:
        print(f"{GREEN}✓ Committed successfully!{RESET}\n")
        
        # Show short log of last commit
        stdout, stderr, code = run_git(["log", "-1", "--oneline"], check=False)
        if code == 0:
            print(f"  {DIM}Latest: {stdout}{RESET}\n")
            
        # Push
        push_changes()


if __name__ == "__main__":
    main()
