#!/usr/bin/env python3
"""
Scrapling Wrapper for Project Athena (Sovereign Acquisition)
"""

import argparse
import sys
import json
import logging

logging.basicConfig(level=logging.ERROR)


def fetch_url(url: str, headless: bool = True):
    try:
        import scrapling
        from scrapling import StealthyFetcher
    except ImportError as e:
        return {"status": "error", "error": f"Scrapling Import Failed: {e}"}

    try:
        fetcher = StealthyFetcher(headless=headless, disable_resources=True)
        page = fetcher.fetch(url)

        # Handle different return types
        content = ""
        if hasattr(page, "text"):
            content = page.text
        elif hasattr(page, "content"):
            content = page.content.decode("utf-8")
        else:
            content = str(page)

        return {
            "status": "success",
            "url": url,
            "length": len(content),
            "content": content[:500000],
        }
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        print("Running Scrapling stealth test...")
        try:
            import scrapling

            print(f"Scrapling found at: {scrapling.__file__}")
        except Exception as e:
            print(f"Scrapling NOT found: {e}")
            return

        res = fetch_url("https://now.sh/detect")
        if res["status"] == "success":
            print(f"PASS: Fetched ({res['length']} bytes)")
        else:
            print(f"FAIL: {res['error']}")
        return

    if args.url:
        print(json.dumps(fetch_url(args.url)))


if __name__ == "__main__":
    main()
