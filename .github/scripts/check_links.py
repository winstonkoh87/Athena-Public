#!/usr/bin/env python3
"""Internal Markdown link integrity checker.

Resolves every relative Markdown link against both the source file's directory
and the repo root. Fails (exit 1) if any internal link is dead.

Intentionally skips:
  - External links (http/https/mailto/tel)
  - Pure anchors (#section)
  - file:// links (covered by the private-path-leak step)
  - Wiki-style links (no extension, no slash, e.g. [FAQ](Getting-Started)) —
    these resolve on the rendered GitHub wiki, not as repo files.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "#", "file://")


def is_wiki_style(target: str) -> bool:
    base = os.path.basename(target)
    return "." not in base and "/" not in target.strip("#")


def resolves(src_md: str, target: str) -> bool:
    path = target.split("#")[0].split("?")[0]
    if not path:
        return True  # pure anchor
    if path.startswith("/"):
        from_root = os.path.normpath(os.path.join(ROOT, path.lstrip("/")))
        return os.path.exists(from_root)
    from_dir = os.path.normpath(os.path.join(os.path.dirname(src_md), path))
    return os.path.exists(from_dir)


def main() -> int:
    broken = []
    checked = 0
    for dp, dn, fn in os.walk(ROOT):
        if os.sep + ".git" in dp:
            continue
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            try:
                txt = open(p, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            for m in LINK.finditer(txt):
                tgt = m.group(2).strip()
                if tgt.lower().startswith(SKIP_PREFIX):
                    continue
                if is_wiki_style(tgt):
                    continue
                checked += 1
                if not resolves(p, tgt):
                    broken.append((os.path.relpath(p, ROOT), tgt))

    print(f"Checked {checked} internal Markdown links.")
    if broken:
        print(f"\nFound {len(broken)} dead internal link(s):\n")
        for src, tgt in sorted(broken):
            print(f"  {src}  ->  {tgt}")
        print("\nFix: update the path to the renamed/moved file, or remove the link.")
        return 1
    print("No dead internal links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
