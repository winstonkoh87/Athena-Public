#!/usr/bin/env python3
"""
memory_compressor.py
====================
Standalone script to compress raw text into structured atomic facts.
Uses Protocol 104 logic.
"""

import os
import sys
import argparse
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Protocol 104 Prompt
SYSTEM_PROMPT = """
You are a Semantic Compressor (Protocol 104).
Input: Context Log.
Output: A list of ATOMIC FACTS.

Rules:
1. Extract high-value signal (User preferences, decisions, constraints, biographical data).
2. Discard noise (greetings, ephemeral context).
3. Use SVO (Subject-Verb-Object) format where possible.
4. Resolve coreferences (I -> User).
5. Add [Project: X] tag if relevant.

Return ONLY the bulleted list. No intro.
"""


# Robust Auth (Stolen from gemini_client.py)
def get_api_key() -> str:
    """Retrieve API key from env, preferring GEMINI_API_KEY."""
    candidate = os.environ.get("GEMINI_API_KEY")
    if candidate and "your_gemini_api_key_here" not in candidate:
        return candidate
    return os.environ.get("GOOGLE_API_KEY", "")


def compress_text(text):
    """Compresses text using Gemini Flash."""
    api_key = get_api_key()
    if not api_key:
        return "Error: GEMINI_API_KEY/GOOGLE_API_KEY not found."

    import time

    genai.configure(api_key=api_key)
    # Switch to generic alias to avoid specific version quotas
    model = genai.GenerativeModel("gemini-flash-latest")

    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(f"{SYSTEM_PROMPT}\n\nInput:\n{text}")
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                if attempt < retries - 1:
                    sleep_time = 2 ** (attempt + 1)
                    time.sleep(sleep_time)
                    continue
            return f"Error compressing: {e}"
    return "Error: Max retries exceeded."


def main():
    # Attempt to load .env from known locations
    load_dotenv()  # Current dir

    # Try parent dirs if not found
    try:
        from pathlib import Path

        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("input_text", help="Text to compress")
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="If set, append compressed output directly to this file (enables fire-and-forget mode)",
    )
    args = parser.parse_args()

    compressed = compress_text(args.input_text)

    if args.output_file and compressed and "Error" not in compressed:
        # Self-contained mode: write directly to semantic_log.md
        try:
            from pathlib import Path

            out_path = Path(args.output_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "a") as f:
                f.write(
                    f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{compressed}\n"
                )
        except Exception as e:
            print(f"Error writing to {args.output_file}: {e}", file=sys.stderr)
    else:
        print(compressed)


if __name__ == "__main__":
    main()
