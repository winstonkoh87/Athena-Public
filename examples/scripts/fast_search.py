#!/usr/bin/env python3
"""
Fast Search (Tier 1 Reflex)
---------------------------
Exclusively for exact ID lookups, tags, and known filenames.
Optimized for <200ms latency.
"""

import argparse
import re
import subprocess
import sys


def run_fast_search(query, root_dir="."):
    """
    Executes a tiered grep/find strategy.
    1. Exact filename match
    2. Exact ID match (if query looks like a UUID or ID)
    3. Tag match (if query starts with #)
    """
    results = []

    # 1. Exact Filename Match (mdfind is instant on macOS)
    try:
        # Check if mdfind is available (macOS only)
        subprocess.run(["which", "mdfind"], capture_output=True, check=True)
        # mdfind is globally indexed, so we filter by current directory path
        pattern = f"kMDItemFSName == '*{query}*' && kMDItemPath == '{root_dir}*'"
        cmd = ["mdfind", "-onlyin", root_dir, query]
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback to fd or find
        try:
            subprocess.run(["fd", "--version"], capture_output=True, check=True)
            cmd = ["fd", "-t", "f", "-H", "-I", query, root_dir]
        except (FileNotFoundError, subprocess.CalledProcessError):
            cmd = ["find", root_dir, "-name", f"*{query}*"]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.strip().split("\n"):
                results.append(f"[FILE] {line}")
    except Exception:
        pass

    # 2. Tag Search (grep)
    if query.startswith("#"):
        tag_word = query[1:].strip()
        # Search for "# tag_word" or "#tag_word"
        pattern = f"#[ ]?{tag_word}"

        # Strategy: Ripgrep -> mdfind (Mac Content) -> find|grep
        try:
            # ripgrep is preferred
            subprocess.run(["rg", "--version"], capture_output=True, check=True)
            cmd = [
                "rg",
                "--hidden",
                "--no-heading",
                "--line-number",
                "--color=never",
                pattern,
                root_dir,
            ]
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                # mdfind (Spotlight) is instant for content
                subprocess.run(["which", "mdfind"], capture_output=True, check=True)
                cmd = ["mdfind", "-onlyin", root_dir, query]  # Matches tags in content
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Fallback to find -> grep (bulletproof but slow)
                cmd = [
                    "find",
                    root_dir,
                    "-type",
                    "f",
                    "-exec",
                    "grep",
                    "-H",
                    "-n",
                    pattern,
                    "{}",
                    "+",
                ]

        try:
            # Longer timeout for find fallback
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout.strip():
                # Filter out binary matches and limit to 5
                lines = [
                    line
                    for line in proc.stdout.strip().split("\n")
                    if "Binary file" not in line
                ][:5]
                for line in lines:
                    results.append(f"[TAG] {line}")
        except Exception:
            pass

    # 3. ID Search (Regex for UUID or specific ID formats)
    # Heuristic: If it looks like a hash or ID
    if re.match(r"^[a-fA-F0-9-]{8,}$", query):
        try:
            subprocess.run(["rg", "--version"], capture_output=True, check=True)
            cmd = ["rg", "--hidden", "--files-with-matches", query, root_dir]
        except (FileNotFoundError, subprocess.CalledProcessError):
            cmd = [
                "find",
                root_dir,
                "-type",
                "f",
                "-exec",
                "grep",
                "-l",
                query,
                "{}",
                "+",
            ]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout.strip():
                lines = proc.stdout.strip().split("\n")[:5]
                for line in lines:
                    results.append(f"[ID_REF] {line}")
        except Exception:
            pass

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Fast Search (Reflex Tier)")
    parser.add_argument("query", help="Search query")
    args = parser.parse_args()

    hits = run_fast_search(args.query)

    if hits:
        print(f"⚡ Reflex Hit ({len(hits)}):")
        for hit in hits:
            print(hit)
        sys.exit(0)
    else:
        print("Build miss.")
        sys.exit(1)
