#!/usr/bin/env python3
"""
Athena Codebase Q&A
Ask natural language questions about your codebase using compressed context.
Uses Gemini with automatic model fallback.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Import our fallback client
sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import get_client

load_dotenv()

# --- Constants ---
DEFAULT_CONTEXT_FILE = Path(".context/cache/scripts_compressed.md")

SYSTEM_PROMPT = """You are an expert code navigator for the Athena AI system. You have access to compressed summaries of all scripts in the codebase.

When answering:
1. Be specific - cite file names and function names
2. Be concise - give direct answers, not essays
3. If you don't know, say so
4. If the question is ambiguous, clarify what you're assuming

The user will provide compressed context followed by their question."""

def main():
    parser = argparse.ArgumentParser(description="Athena Codebase Q&A (Gemini with Fallback)")
    parser.add_argument("question", nargs="*", help="Question about the codebase")
    parser.add_argument("--context", help="Path to compressed context file", default=str(DEFAULT_CONTEXT_FILE))
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    # Load context
    context_path = Path(args.context)
    if not context_path.exists():
        print(f"Error: Context file not found: {context_path}")
        print("Run: python3 .agent/scripts/compress_context.py --dir .agent/scripts --output .context/cache/scripts_compressed.md")
        sys.exit(1)
    
    context = context_path.read_text(encoding="utf-8")
    print(f"📚 Loaded context: {len(context):,} chars from {context_path}")

    # Init Gemini with fallback
    try:
        client = get_client()
        print(f"🔗 Model chain: {' → '.join(client.models.keys())}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    def ask(question: str) -> str:
        """Send question with context to Gemini."""
        prompt = f"""{SYSTEM_PROMPT}

=== COMPRESSED CODEBASE CONTEXT ===
{context}
=== END CONTEXT ===

USER QUESTION: {question}

ANSWER:"""
        
        response = client.generate(prompt)
        return f"{response}\n\n_(Used model: {client.last_successful_model})_"

    # Interactive mode
    if args.interactive:
        print("\n🤖 Athena Codebase Q&A (type 'exit' to quit)\n")
        while True:
            try:
                q = input("❓ ").strip()
                if q.lower() in ('exit', 'quit', 'q'):
                    break
                if not q:
                    continue
                print("\n" + ask(q) + "\n")
            except KeyboardInterrupt:
                break
        print("\n👋")
        return

    # Single question mode
    if args.question:
        question = " ".join(args.question)
        print(f"\n❓ {question}\n")
        print(ask(question))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
