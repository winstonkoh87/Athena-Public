import os
import glob
import time
import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Import GeminiClient for LLM operations
# Assuming this script is run from project root, so we adjust path if needed or assume pythonpath
try:
    from .gemini_client import GeminiClient
except ImportError:
    # Fallback if running as script from .agent/scripts/
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from gemini_client import GeminiClient


class DreamState:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.logs_dir = self.workspace_root / ".context" / "memories" / "session_logs"
        self.canonical_path = self.workspace_root / ".context" / "CANONICAL.md"
        self.episodic_dir = self.workspace_root / ".context" / "memories" / "episodic"
        self.reports_dir = self.workspace_root / ".context" / "reports"

        # Ensure directories exist
        self.episodic_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.client = GeminiClient(
            system_prompt="You are the Nocturnal Consolidation Engine. Your job is to organize memory, detect conflicts, and compress logs."
        )

    def sweep_logs(self, hours: int = 24) -> List[Path]:
        """Find session logs modified in the last N hours."""
        print(f"🧹 Sweeping session logs from last {hours} hours...")
        now = time.time()
        recent_logs = []

        # Recursive search for .md files in session_logs
        for log_file in self.logs_dir.rglob("*.md"):
            mtime = log_file.stat().st_mtime
            if (now - mtime) < (hours * 3600):
                recent_logs.append(log_file)

        print(f"   Found {len(recent_logs)} recent logs.")
        return recent_logs

    def extract_and_check_conflicts(self, log_files: List[Path]) -> Dict:
        """
        Reads logs and checks for conflicts against CANONICAL.md.
        Returns a dict of reports/findings.
        """
        if not log_files:
            return {}

        print("⚖️  Checking for conflicts against CANONICAL.md...")

        # 1. Load Canonical Truth
        canonical_content = ""
        if self.canonical_path.exists():
            canonical_content = self.canonical_path.read_text()
        else:
            print("⚠️  CANONICAL.md not found. Skipping conflict check.")
            return {}

        # 2. Aggregated Analysis
        # We process files in chunks to avoid context limits if necessary,
        # but for now we assume 24h of logs fit in context (Flash model).
        combined_logs = ""
        for log in log_files:
            combined_logs += f"\n=== SESSION LOG: {log.name} ===\n"
            combined_logs += log.read_text()[:20000]  # Cap per log to stay sane

        prompt = f"""
        TASK: Conflict Detection and Fact Extraction
        
        Compare the following NEW SESSION LOGS against the EXISTING CANONICAL MEMORY.
        
        1. Identify any **Strategic Conflicts** (e.g., Log says "Use X", Canonical says "Use Y").
        2. Identify **New Facts** that should be promoted to Canonical.
        3. Identify **Obsolete Facts** in Canonical that should be removed.
        4. Calculate a **Confidence Score** (0-100) for these changes.
        
        === EXISTING CANONICAL DATA ===
        {canonical_content[:30000]}
        
        === NEW SESSION LOGS (LAST 24H) ===
        {combined_logs}
        
        OUTPUT FORMAT (JSON):
        {{
            "conflicts": [
                {{"subject": "...", "canonical_says": "...", "new_log_says": "...", "resolution_suggestion": "..."}}
            ],
            "new_facts": [
                {{"fact": "...", "source_log": "..."}}
            ],
            "obsolete_facts": [
                {{"fact": "...", "reason": "..."}}
            ]
        }}
        """

        try:
            response = self.client.chat_structured(prompt, schema=None)
            # Response should already be a dict if chat_structured works,
            # but gemini_client.py's implementation might need verification.
            # Looking at gemini_client.py, it returns a dict.
            return response
        except Exception as e:
            print(f"❌ Error during conflict check: {e}")
            return {"error": str(e)}

    def compress_episodes(self, log_files: List[Path]) -> List[str]:
        """
        Compresses verbose session logs into a dense episodic summary.
        """
        if not log_files:
            return []

        print("🗜️  Compressing episodic memories...")
        summaries = []

        for log in log_files:
            content = log.read_text()
            prompt = f"""
            TASK: Episodic Compression
            
            Compress the following session log into a concise "Episodic Memory" block.
            - Keep core decisions, insights, and outcomes.
            - Remove chatter, basic tool calls, and verbose reasoning.
            - Format: Markdown bullet points.
            
            === LOG START ===
            {content[:50000]}
            === LOG END ===
            """
            try:
                summary = self.client.generate(prompt)
                filename = f"{datetime.date.today()}_{log.stem}_summary.md"
                save_path = self.episodic_dir / filename
                save_path.write_text(summary)
                summaries.append(f"Compressed {log.name} -> {filename}")
            except Exception as e:
                print(f"❌ Failed to compress {log.name}: {e}")

        return summaries

    def generate_report(self, conflicts: Dict, compression_results: List[str]):
        """Generates the Dream Report."""
        today = datetime.date.today()
        report_path = self.reports_dir / f"daily_dream_report_{today}.md"

        content = f"# 🛌 Daily Dream Report: {today}\n\n"

        content += "## 1. Episodic Compression\n"
        if compression_results:
            for line in compression_results:
                content += f"- {line}\n"
        else:
            content += "- No logs to compress.\n"

        content += "\n## 2. Conflict & Consistency Check\n"
        if "error" in conflicts:
            content += f"⚠️ Error running check: {conflicts['error']}\n"
        else:
            cons = conflicts.get("conflicts", [])
            if cons:
                content += "### 🔴 Detected Conflicts\n"
                for c in cons:
                    content += f"- **Subject**: {c.get('subject')}\n"
                    content += f"  - Canonical: {c.get('canonical_says')}\n"
                    content += f"  - New Log: {c.get('new_log_says')}\n"
                    content += f"  - Suggestion: {c.get('resolution_suggestion')}\n"
            else:
                content += "✅ No conflicts detected.\n"

            new_facts = conflicts.get("new_facts", [])
            if new_facts:
                content += "\n### 🟢 New Facts for Canonical\n"
                for f in new_facts:
                    content += f"- {f.get('fact')} (Source: {f.get('source_log')})\n"

        report_path.write_text(content)
        print(f"📝 Report generated: {report_path}")

    def run(self):
        print("💤 Entering Dream State...")

        # 1. Sweep
        logs = self.sweep_logs(hours=24)
        if not logs:
            print("✨ No new memories to process. Waking up.")
            return

        # 2. Conflict Check
        conflicts = self.extract_and_check_conflicts(logs)

        # 3. Compress
        compression_results = self.compress_episodes(logs)

        # 4. Report
        self.generate_report(conflicts, compression_results)

        print("☀️ Dream State complete.")


if __name__ == "__main__":
    dreamer = DreamState()
    dreamer.run()
