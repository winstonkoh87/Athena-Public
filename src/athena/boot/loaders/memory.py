import sys
import subprocess
from datetime import datetime
from pathlib import Path
from athena.boot.constants import (
    PROJECT_ROOT,
    LOGS_DIR,
    SUPABASE_SEARCH_SCRIPT,
    GREEN,
    YELLOW,
    RED,
    BOLD,
    DIM,
    RESET,
)


class MemoryLoader:
    @staticmethod
    def recall_last_session() -> str:
        """Display summary of last session with context handoff."""
        if not LOGS_DIR.exists():
            return ""

        files = sorted(LOGS_DIR.glob("*-session-*.md"))
        if not files:
            return ""

        latest_file = files[-1]
        filename = latest_file.name
        print(f"⏮️  Last Session: {BOLD}{filename}{RESET}")

        try:
            content = latest_file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("**Focus**:"):
                    focus = line.replace("**Focus**:", "").strip()
                    if focus and focus != "...":
                        print(f"   Focus: {focus}")
                    break

            # Deferred items logic
            deferred_items = []
            if "## 3. Action Items" in content or "## Action Items" in content:
                in_action = False
                for line in content.split("\n"):
                    if "Action Items" in line and line.startswith("#"):
                        in_action = True
                        continue
                    if in_action and line.startswith("#"):
                        break
                    if in_action and "Pending" in line and "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 3 and parts[1] and parts[1] != "Action":
                            deferred_items.append(f"📋 {parts[1]}")

            if deferred_items:
                print(f"\n   {YELLOW}📌 Deferred from last session:{RESET}")
                for item in deferred_items[:3]:
                    print(f"      {item}")

        except Exception:
            pass

        return filename

    @staticmethod
    def create_session() -> str:
        """Create a new session log."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
            import create_session as cs

            session_path = cs.create_session_log()
            session_id = session_path.stem
            print(f"{GREEN}✅ Created: {session_id}{RESET}")
            return session_id
        except Exception as e:
            print(f"{RED}❌ Failed to create session: {e}{RESET}")
            sys.exit(1)

    @staticmethod
    def capture_context():
        """Output current date/time context."""
        now = datetime.now()
        date_str = now.strftime("%d %B %Y")
        time_str = now.strftime("%H:%M")
        day_of_week = now.strftime("%A")
        week_num = now.isocalendar()[1]
        print(f"📅 Date: {BOLD}{day_of_week}, {date_str}{RESET}")
        print(f"   Time: {time_str} SGT | Week {week_num}")

    @staticmethod
    def prime_semantic():
        """Run semantic search silently."""
        if not SUPABASE_SEARCH_SCRIPT.exists():
            print(f"{YELLOW}⚠️ Semantic search skipped (script not found){RESET}")
            return False

        try:
            result = subprocess.run(
                ["python3", str(SUPABASE_SEARCH_SCRIPT), "recent session context"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"{GREEN}✅ Semantic memory primed{RESET}")
                return True
            else:
                print(f"{YELLOW}⚠️ Semantic search returned non-zero{RESET}")
                return False
        except Exception as e:
            print(f"{YELLOW}⚠️ Semantic search error: {e}{RESET}")
            return False

    @staticmethod
    def prewarm_search_cache():
        """Pre-run common queries to populate the search cache."""
        try:
            from athena.tools.search import run_search

            hot_queries = ["protocol", "session", "user profile"]
            for query in hot_queries:
                try:
                    run_search(query, limit=5, json_output=True)
                except Exception:
                    pass  # Best effort
            print(
                f"{GREEN}🔥 Search cache pre-warmed ({len(hot_queries)} queries){RESET}"
            )
        except Exception as e:
            print(f"{YELLOW}⚠️ Cache pre-warm skipped: {e}{RESET}")

    @staticmethod
    def display_learnings_snapshot():
        """Show recent user preferences and learning snapshots."""
        memory_dir = PROJECT_ROOT / ".athena" / "memory"
        user_profile = memory_dir / "USER_PROFILE.yaml"
        system_learnings = memory_dir / "SYSTEM_LEARNINGS.md"

        if user_profile.exists():
            try:
                content = user_profile.read_text()
                prefs = []
                if "wants_idempotent_compilers: true" in content:
                    prefs.append("idempotent compilers")
                if "prefers_deterministic_inference: true" in content:
                    prefs.append("deterministic inference")
                if "likes_enforcement_warnings: true" in content:
                    prefs.append("enforcement warnings")
                if prefs:
                    print(f"\n{DIM}📋 User Prefs: {', '.join(prefs[:3])}{RESET}")
            except Exception:
                pass

        if system_learnings.exists():
            try:
                content = system_learnings.read_text()
                rows = [
                    line for line in content.split("\n") if line.startswith("| 202")
                ]
                if rows:
                    recent = rows[-2:]
                    print(f"{DIM}📚 Recent Learnings:{RESET}")
                    for row in recent:
                        parts = [p.strip() for p in row.split("|")]
                        if len(parts) >= 4:
                            learning = (
                                parts[3][:60] + "..."
                                if len(parts[3]) > 60
                                else parts[3]
                            )
                            print(f"   {DIM}• {learning}{RESET}")
            except Exception:
                pass
