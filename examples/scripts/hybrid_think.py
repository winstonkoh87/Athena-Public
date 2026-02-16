#!/usr/bin/env python3
import os
import sys
import glob
import textwrap
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
MODEL_NAME = "gemini-3-flash-preview"  # SOTA Priority
CONTEXT_WINDOW_LIMIT = 500_000  # Conservative limit for preview
SESSION_HISTORY_COUNT = 20  # Number of recent sessions to load

# --- Setup ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment.")
    print("   Please run: export GOOGLE_API_KEY='your_key'")
    sys.exit(1)

genai.configure(api_key=api_key)


def read_file(path, label="FILE"):
    """Reads a file and wraps it in a tagged block."""
    if not os.path.exists(path):
        return f"[{label} MISSING: {path}]"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            return f"\n--- START {label}: {path} ---\n{content}\n--- END {label} ---\n"
    except Exception as e:
        return f"[{label} READ ERROR: {e}]"


def get_recent_sessions(count=SESSION_HISTORY_COUNT):
    """Retrieves the N most recent session logs."""
    # Pattern to match: .context/memories/session_logs/YYYY-MM-DD-session-XX.md
    # We look in the standard location
    files = glob.glob(".context/memories/session_logs/20*-session-*.md")
    files.sort()  # ISO dates sort correctly alphabetically
    return files[-count:]


def build_payload():
    """Assembles the Context Payload."""
    payload = []

    print(f"⚡ Assembling Payload for {MODEL_NAME}...")

    # 1. Core State (The "Brain")
    print("   + Loading Project State...")
    payload.append(read_file(".context/project_state.md", "PROJECT_STATE"))
    payload.append(read_file(".agent/TAG_INDEX.md", "TAG_INDEX"))
    payload.append(read_file(".context/PROTOCOL_SUMMARIES.md", "PROTOCOL_INDEX"))

    # 2. Recent History (The "Stream")
    sessions = get_recent_sessions()
    print(f"   + Loading {len(sessions)} recent sessions...")
    for sess in sessions:
        payload.append(read_file(sess, "SESSION_LOG"))

    return "\n".join(payload)


def think(query):
    """Executes the Tier 3 Reasoning Loop."""

    # 1. Build Context
    context_block = build_payload()

    # 2. Construct Prompt
    system_instruction = """
    You are Project Athena's 'Tier 3' Turbo Intelligence.
    Your goal is HOLISTIC REASONING based on the provided long-context history.
    
    CONTEXT PROVIDED:
    1. Project State: The single source of truth for status.
    2. Tag Index: The map of all available concepts.
    3. Session Logs: The recent conversational history.
    
    DIRECTIVES:
    - Do not assume; verify against the logs.
    - If a pattern emerges across sessions, highlight it.
    - Be concise, executive, and dense.
    """

    full_prompt = (
        f"{system_instruction}\n\nCONTEXT:\n{context_block}\n\nUSER QUERY:\n{query}"
    )

    # 3. Call API
    print(f"⚡ Transmitting to Cloud ({len(full_prompt)} chars)...")
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(full_prompt)

        print("\n" + "=" * 60)
        print(f"🤖 {MODEL_NAME} RESPONSE")
        print("=" * 60 + "\n")
        print(response.text)
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ API Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 hybrid_think.py "<your query>"')
        sys.exit(1)

    query = sys.argv[1]
    think(query)
