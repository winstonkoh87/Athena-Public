#!/usr/bin/env python3
"""
Grounded Search
Uses Gemini with Google Search grounding for research queries.
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

SYSTEM_PROMPT = """You are a research assistant with access to Google Search. 
When answering:
1. Search for current, accurate information
2. Cite your sources with URLs
3. Be concise but comprehensive
4. Distinguish between facts and opinions
5. Note when information might be outdated"""

def search(query: str) -> str:
    """Perform grounded search using Gemini."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    
    genai.configure(api_key=api_key)
    
    # Configure model with search grounding
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        tools=[{"google_search": {}}]  # Enable grounding
    )
    
    prompt = f"""{SYSTEM_PROMPT}

USER QUERY: {query}

Search the web and provide a well-sourced answer:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback to non-grounded if quota exhausted
        fallback_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        print("⚠️ Search grounding unavailable, using standard model")
        response = fallback_model.generate_content(prompt)
        return response.text

def main():
    parser = argparse.ArgumentParser(description="Grounded web search using Gemini")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--output", help="Save results to file")
    args = parser.parse_args()

    if args.interactive:
        print("🔍 Grounded Search (type 'exit' to quit)\n")
        while True:
            try:
                query = input("❓ ").strip()
                if query.lower() in ('exit', 'quit', 'q'):
                    break
                if not query:
                    continue
                print("\n" + search(query) + "\n")
            except KeyboardInterrupt:
                break
        print("\n👋")
        return

    if args.query:
        query = " ".join(args.query)
        print(f"🔍 Searching: {query}\n")
        result = search(query)
        
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"✅ Saved to {args.output}")
        else:
            print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
