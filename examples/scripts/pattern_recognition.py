#!/usr/bin/env python3
"""
Pattern Recognition Module
Unified analyzer for chats, sessions, and behavioral patterns.
Consolidates: analyze_chat_gemini.py, analyze_chat_json.py,
              analyze_chat_temporal.py, analyze_sessions.py
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

SESSION_LOGS_DIR = Path(".context/memories/session_logs")

DISTRESS_KEYWORDS = [
    r"crisis",
    r"urgent",
    r"escalat",
    r"risk",
    r"alert",
    r"warn",
    r"concern",
    r"critical",
    r"blocked",
]
MODERATION_KEYWORDS = [
    r"flagged",
    r"review",
    r"moderate",
    r"filter",
    r"report",
    r"violation",
    r"policy",
    r"restrict",
    r"block",
]
PSYCH_KEYWORDS = [
    r"fix",
    r"curious",
    r"know",
    r"scared",
    r"fear",
    r"control",
    r"safe",
    r"boring",
    r"ordinary",
    r"game",
    r"test",
    r"experiment",
    r"layer",
    r"mirror",
    r"mask",
    r"detach",
    r"analy",
    r"truth",
]

# ─────────────────────────────────────────────────────────────────────────────
# Chat Analyzer Class
# ─────────────────────────────────────────────────────────────────────────────


class ChatAnalyzer:
    """Unified chat analysis with multiple modes."""

    def __init__(self, chat_file: Path):
        self.chat_file = chat_file
        self.messages = []
        self._load()

    def _load(self):
        """Load chat JSON file."""
        with open(self.chat_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data.get("messages", [])

    def _get_text_messages(self) -> list:
        """Filter to text messages only."""
        return [
            m
            for m in self.messages
            if m.get("type") == "message" and isinstance(m.get("text"), str)
        ]

    def _extract_text(self, msg: dict) -> str:
        """Extract text from message (handles list format)."""
        text = msg.get("text", "")
        if isinstance(text, str):
            return text
        elif isinstance(text, list):
            parts = []
            for entity in text:
                if isinstance(entity, dict):
                    parts.append(entity.get("text", ""))
                elif isinstance(entity, str):
                    parts.append(entity)
            return "".join(parts)
        return ""

    def _sample_messages(self, max_chars: int = 40000) -> str:
        """Sample messages for API analysis."""
        text_messages = self._get_text_messages()
        n = len(text_messages)
        samples = []

        # Early, middle, recent sampling
        samples.extend(text_messages[:20])
        mid_start = n // 3
        samples.extend(text_messages[mid_start : mid_start + 30])
        samples.extend(text_messages[-50:])

        output = []
        total_chars = 0
        for msg in samples:
            if isinstance(msg.get("text"), str):
                line = f"[{msg.get('date', '')}] {msg.get('from', 'Unknown')}: {msg['text']}"
                if total_chars + len(line) > max_chars:
                    break
                output.append(line)
                total_chars += len(line)

        return "\n".join(output)

    def analyze_gemini(self) -> str:
        """Deep psychological analysis using Gemini API."""
        prompt = """You are a forensic psychologist analyzing a chat conversation.
        
Analyze for:
1. Communication Patterns (initiation, response latency, message length)
2. Psychological Dynamics (power, vulnerability, attachment)
3. Key Themes (dominant topics, avoidances, triggers)
4. Behavioral Red Flags (inconsistencies, boundary violations)
5. Profile Synthesis (drivers, attachment style, defenses)

Be clinical and objective. Cite specific message examples.
"""
        text_messages = self._get_text_messages()
        sampled = self._sample_messages()

        full_prompt = f"""{prompt}

=== CHAT SAMPLE ({len(text_messages)} total messages) ===
{sampled}
=== END SAMPLE ===

Provide your analysis:"""

        client = get_client()
        return client.generate(full_prompt)

    def analyze_keywords(self, target_id: str, keywords: Optional[list] = None) -> list:
        """Search messages by keyword patterns."""
        if keywords is None:
            keywords = PSYCH_KEYWORDS

        results = []
        for msg in self.messages:
            if msg.get("type") != "message":
                continue
            if msg.get("from_id") != target_id:
                continue

            text = self._extract_text(msg)
            if not text:
                continue

            lower_text = text.lower()
            if any(re.search(k, lower_text) for k in keywords):
                msg_id = msg.get("id", "N/A")
                sender = msg.get("from", "Unknown")
                results.append(f"[{msg_id}] {sender}: {text}")

        return results

    def analyze_temporal(self, user1_id: str, user2_id: str) -> dict:
        """Analyze response latency, initiation patterns, and hourly trends."""
        user1_latency = []
        user2_latency = []
        hourly_distress = {h: 0 for h in range(24)}
        hourly_moderation = {h: 0 for h in range(24)}
        initiations = {user1_id: 0, user2_id: 0}

        last_timestamp = None
        prev_msg = None

        for msg in self.messages:
            if msg.get("type") != "message":
                continue

            timestamp = datetime.fromtimestamp(int(msg["date_unixtime"]))
            sender_id = msg.get("from_id")

            if last_timestamp:
                delta = (timestamp - last_timestamp).total_seconds()

                # Initiation (gap > 6 hours)
                if delta > 6 * 3600:
                    if sender_id in initiations:
                        initiations[sender_id] += 1

                # Response latency (reply within 1 hour)
                elif delta < 3600 and prev_msg and prev_msg.get("from_id") != sender_id:
                    if sender_id == user1_id:
                        user1_latency.append(delta)
                    elif sender_id == user2_id:
                        user2_latency.append(delta)

            # Content analysis by hour
            text = self._extract_text(msg)
            if sender_id == user1_id:
                hour = timestamp.hour
                lower_text = text.lower()
                if any(re.search(k, lower_text) for k in DISTRESS_KEYWORDS):
                    hourly_distress[hour] += 1
                if any(re.search(k, lower_text) for k in MODERATION_KEYWORDS):
                    hourly_moderation[hour] += 1

            last_timestamp = timestamp
            prev_msg = msg

        avg_user1 = sum(user1_latency) / len(user1_latency) if user1_latency else 0
        avg_user2 = sum(user2_latency) / len(user2_latency) if user2_latency else 0

        return {
            "user1_avg_latency_sec": avg_user1,
            "user2_avg_latency_sec": avg_user2,
            "latency_ratio": avg_user2 / avg_user1 if avg_user1 > 0 else 0,
            "initiations": initiations,
            "hourly_distress": hourly_distress,
            "hourly_moderation": hourly_moderation,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Cost Analyzer Class
# ─────────────────────────────────────────────────────────────────────────────


class CostAnalyzer:
    """Accurate API Replacement Cost Estimator."""

    PRICING = {
        "sonnet": {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
        "opus": {"input": 5.00, "output": 25.00, "cache_read": 0.50, "cache_write": 6.25},
    }
    DEFAULT_CACHE_HIT_RATE = 0.90
    OUTPUT_TOKENS = {"heavy": 4000, "medium": 1500, "light": 600}

    def __init__(self, session_dir: Path = SESSION_LOGS_DIR):
        self.session_dir = session_dir

    def _count_checkpoints(self, content: str) -> int:
        pattern = r"^#{2,4}\s+.*[Cc]heckpoint"
        return len(re.findall(pattern, content, re.MULTILINE))

    def _classify_session(self, content: str, checkpoint_count: int) -> str:
        has_ultrathink = "ultrathink" in content.lower()
        size_chars = len(content)
        if has_ultrathink or checkpoint_count >= 8 or size_chars > 20000:
            return "heavy"
        elif checkpoint_count >= 4 or size_chars > 8000:
            return "medium"
        else:
            return "light"

    def calculate_session_value(
        self, content: str, model: str = "opus", cache_rate: float = 0.90
    ) -> dict:
        rates = self.PRICING.get(model, self.PRICING["opus"])
        checkpoint_count = self._count_checkpoints(content)
        if checkpoint_count == 0:
            checkpoint_count = max(1, len(content) // 3000)

        turns = checkpoint_count
        session_type = self._classify_session(content, checkpoint_count)
        total_tokens = len(content) / 4
        max_context = {"heavy": 50000, "medium": 30000, "light": 15000}[session_type]
        avg_input = min(max_context, total_tokens / 2)
        output_per_turn = self.OUTPUT_TOKENS[session_type]

        cacheable = avg_input * cache_rate
        fresh = avg_input * (1 - cache_rate)

        turn1_in = (cacheable / 1e6) * rates["cache_write"] + (fresh / 1e6) * rates["input"]
        subs_in = (
            (turns - 1) * ((cacheable / 1e6) * rates["cache_read"] + (fresh / 1e6) * rates["input"])
            if turns > 1
            else 0
        )

        total_in = turn1_in + subs_in
        total_out = (turns * output_per_turn / 1e6) * rates["output"]

        return {
            "type": session_type,
            "total_value": turn1_in + subs_in + total_out,
            "checkpoints": checkpoint_count,
            "turns": turns,
        }

    def analyze_all(self, model: str = "opus") -> dict:
        logs = list(self.session_dir.rglob("*.md"))
        results = []
        for log in logs:
            if "Analysis" in log.name or "README" in log.name:
                continue
            try:
                stats = self.calculate_session_value(log.read_text(encoding="utf-8"), model)
                results.append(stats)
            except:
                continue

        total = sum(r["total_value"] for r in results)
        active = [r for r in results if r["checkpoints"] >= 2 or r["total_value"] > 0.05]
        weighted_avg = sum(r["total_value"] for r in active) / len(active) if active else 0
        return {
            "total": total,
            "weighted_avg": weighted_avg,
            "count": len(results),
            "active": len(active),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Session Analyzer Class
# ─────────────────────────────────────────────────────────────────────────────


class SessionAnalyzer:
    """Analyzes Athena session logs for meta-patterns."""

    def __init__(self, session_dir: Path = SESSION_LOGS_DIR):
        self.session_dir = session_dir

    def get_recent_sessions(self, n: int = 10) -> list[tuple[str, str]]:
        """Get N most recent session logs."""
        if not self.session_dir.exists():
            return []

        logs = sorted(self.session_dir.glob("*.md"), reverse=True)
        results = []
        for log in logs[:n]:
            content = log.read_text(encoding="utf-8")
            results.append((log.name, content))
        return results

    def analyze_meta(self, n: int = 10) -> str:
        """Meta-analyze sessions using Gemini."""
        sessions = self.get_recent_sessions(n)
        if not sessions:
            return "No session logs found."

        prompt = """You are a meta-analyst for the Athena AI system.

Analyze these sessions to identify:
1. **Recurring Patterns** - What topics/tasks come up repeatedly?
2. **Common Mistakes** - What errors or backtracking happened?
3. **Workflow Insights** - What optimizations could be made?
4. **User Preferences** - What patterns in how the user works?
5. **Knowledge Gaps** - What areas need more documentation?

Be specific. Cite session dates and examples. Be concise but comprehensive."""

        combined = ""
        for name, content in sessions:
            combined += f"\n\n=== SESSION: {name} ===\n{content[:3000]}\n"

        full_prompt = f"""{prompt}

=== SESSION LOGS ===
{combined[:50000]}
=== END LOGS ===

Generate a meta-analysis report:"""

        client = get_client()
        return client.generate(full_prompt)


# ─────────────────────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Unified Pattern Recognition Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deep chat analysis with Gemini
  python pattern_recognition.py chat --file chat.json --mode gemini
  
  # Keyword search in chat
  python pattern_recognition.py chat --file chat.json --mode keywords --target user123
  
  # Temporal analysis
  python pattern_recognition.py chat --file chat.json --mode temporal --user1 id1 --user2 id2
  
  # Session meta-analysis
  python pattern_recognition.py sessions --num 10
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Analysis type")

    # Chat subcommand
    chat_parser = subparsers.add_parser("chat", help="Analyze chat logs")
    chat_parser.add_argument("--file", "-f", required=True, help="Path to chat JSON")
    chat_parser.add_argument(
        "--mode",
        "-m",
        choices=["gemini", "keywords", "temporal"],
        default="gemini",
        help="Analysis mode",
    )
    chat_parser.add_argument("--target", help="Target user ID (for keywords mode)")
    chat_parser.add_argument("--user1", help="User 1 ID (for temporal mode)")
    chat_parser.add_argument("--user2", help="User 2 ID (for temporal mode)")
    chat_parser.add_argument("--output", "-o", help="Save output to file")

    # Sessions subcommand
    sessions_parser = subparsers.add_parser("sessions", help="Analyze session logs")
    sessions_parser.add_argument("--num", "-n", type=int, default=10, help="Number of sessions")
    sessions_parser.add_argument("--output", "-o", help="Save output to file")

    args = parser.parse_args()

    if args.command == "chat":
        chat_file = Path(args.file)
        if not chat_file.exists():
            print(f"Error: File not found: {chat_file}")
            sys.exit(1)

        analyzer = ChatAnalyzer(chat_file)

        if args.mode == "gemini":
            print(f"🔍 Analyzing with Gemini: {chat_file}")
            result = analyzer.analyze_gemini()
        elif args.mode == "keywords":
            if not args.target:
                print("Error: --target required for keywords mode")
                sys.exit(1)
            print(f"🔍 Keyword search for user: {args.target}")
            matches = analyzer.analyze_keywords(args.target)
            result = f"Found {len(matches)} matches:\n\n" + "\n---\n".join(matches[-50:])
        elif args.mode == "temporal":
            if not args.user1 or not args.user2:
                print("Error: --user1 and --user2 required for temporal mode")
                sys.exit(1)
            print(f"🔍 Temporal analysis...")
            data = analyzer.analyze_temporal(args.user1, args.user2)
            result = json.dumps(data, indent=2)

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"✅ Saved to {args.output}")
        else:
            print("\n" + "=" * 60)
            print(result)
            print("=" * 60)

    elif args.command == "sessions":
        print(f"📊 Analyzing last {args.num} sessions...")
        analyzer = SessionAnalyzer()
        result = analyzer.analyze_meta(args.num)

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"✅ Saved to {args.output}")
        else:
            print("\n" + "=" * 60)
            print(result)
            print("=" * 60)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
