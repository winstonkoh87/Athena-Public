#!/usr/bin/env python3
"""
claim_id.py — Atomic Multi-Agent Identifier Lease Allocator
==========================================================

Solves TD-063 identifier namespace collisions (Session S###, Tech Debt TD-###,
Case Study CS-###) across concurrent agents and git worktrees.

Uses SQLite WAL mode with EXCLUSIVE transactions and filesystem scans to
guarantee unique, monotonic, collision-free identifier allocation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_DIR = PROJECT_ROOT / ".agent" / "state"
REGISTRY_DB_PATH = STATE_DIR / "id_registry.db"

# RegEx patterns for discovery
SESSION_PAT = re.compile(r"[Ss](?:ession[-_])?[Ss]?(\d{2,4})[a-z]?")
TD_PAT = re.compile(r"TD-(\d{3,4})")
CS_PAT = re.compile(r"CS-(\d{3,4})")


def get_db_connection() -> sqlite3.Connection:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(REGISTRY_DB_PATH), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS id_leases (
            namespace TEXT NOT NULL,
            id_number INTEGER NOT NULL,
            formatted_id TEXT NOT NULL,
            title TEXT,
            agent_id TEXT,
            claimed_at REAL NOT NULL,
            PRIMARY KEY (namespace, id_number)
        );
        """
    )
    conn.commit()
    return conn


def scan_fs_max_session() -> int:
    session_dir = PROJECT_ROOT / ".context" / "memories" / "session_logs"
    best = 0
    if session_dir.exists():
        for f in session_dir.glob("*.md"):
            for m in SESSION_PAT.finditer(f.name):
                best = max(best, int(m.group(1)))
        archive = session_dir / "archive"
        if archive.exists():
            for f in archive.glob("*.md"):
                for m in SESSION_PAT.finditer(f.name):
                    best = max(best, int(m.group(1)))
    return best


def scan_fs_max_td() -> int:
    td_file = PROJECT_ROOT / ".context" / "TECH_DEBT.md"
    best = 0
    if td_file.exists():
        try:
            content = td_file.read_text(encoding="utf-8")
            for m in TD_PAT.finditer(content):
                best = max(best, int(m.group(1)))
        except Exception:
            pass
    return best


def scan_fs_max_cs() -> int:
    cs_dir = PROJECT_ROOT / ".context" / "memories" / "case_studies"
    best = 0
    if cs_dir.exists():
        for f in cs_dir.glob("*.md"):
            for m in CS_PAT.finditer(f.name):
                best = max(best, int(m.group(1)))
    return best


def get_namespace_fs_max(namespace: str) -> int:
    if namespace == "session":
        return scan_fs_max_session()
    elif namespace == "td":
        return scan_fs_max_td()
    elif namespace == "cs":
        return scan_fs_max_cs()
    return 0


def format_id(namespace: str, num: int) -> str:
    formats = {
        "session": f"S{num}",
        "td": f"TD-{num:03d}",
        "cs": f"CS-{num:03d}",
    }
    return formats.get(namespace, f"{namespace.upper()}-{num}")


def peek_next_id(namespace: str) -> dict[str, Any]:
    fs_max = get_namespace_fs_max(namespace)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT MAX(id_number) FROM id_leases WHERE namespace = ?", (namespace,)
        )
        row = cur.fetchone()
        db_max = row[0] if (row and row[0] is not None) else 0
        next_num = max(fs_max, db_max) + 1
        return {
            "namespace": namespace,
            "next_number": next_num,
            "formatted_id": format_id(namespace, next_num),
            "fs_max": fs_max,
            "db_max": db_max,
        }
    finally:
        conn.close()


def claim_next_id(
    namespace: str, title: str = "", agent_id: str = ""
) -> dict[str, Any]:
    fs_max = get_namespace_fs_max(namespace)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("BEGIN EXCLUSIVE;")
        cur.execute(
            "SELECT MAX(id_number) FROM id_leases WHERE namespace = ?", (namespace,)
        )
        row = cur.fetchone()
        db_max = row[0] if (row and row[0] is not None) else 0

        next_num = max(fs_max, db_max) + 1
        fid = format_id(namespace, next_num)
        now = time.time()
        agent = agent_id or os.getenv("USER", "agent")

        cur.execute(
            """
            INSERT INTO id_leases (namespace, id_number, formatted_id, title, agent_id, claimed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (namespace, next_num, fid, title, agent, now),
        )
        conn.commit()

        return {
            "status": "claimed",
            "namespace": namespace,
            "id_number": next_num,
            "formatted_id": fid,
            "title": title,
            "agent_id": agent,
            "claimed_at": now,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_leases(namespace: str | None = None) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if namespace:
            cur.execute(
                """
                SELECT namespace, id_number, formatted_id, title, agent_id, claimed_at
                FROM id_leases WHERE namespace = ? ORDER BY id_number DESC LIMIT 50
                """,
                (namespace,),
            )
        else:
            cur.execute(
                """
                SELECT namespace, id_number, formatted_id, title, agent_id, claimed_at
                FROM id_leases ORDER BY claimed_at DESC LIMIT 50
                """
            )
        rows = cur.fetchall()
        return [
            {
                "namespace": r[0],
                "id_number": r[1],
                "formatted_id": r[2],
                "title": r[3],
                "agent_id": r[4],
                "claimed_at": r[5],
            }
            for r in rows
        ]
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Athena Atomic Multi-Agent Identifier Lease Allocator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Peek command
    peek_parser = subparsers.add_parser("peek", help="Peek next available ID without claiming")
    peek_parser.add_argument("namespace", choices=["session", "td", "cs"], help="ID namespace")
    peek_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Claim command
    claim_parser = subparsers.add_parser("claim", help="Atomically claim the next ID")
    claim_parser.add_argument("namespace", choices=["session", "td", "cs"], help="ID namespace")
    claim_parser.add_argument("--title", default="", help="Optional title or description")
    claim_parser.add_argument("--agent", default="", help="Agent identifier")
    claim_parser.add_argument("--json", action="store_true", help="Output JSON")

    # List command
    list_parser = subparsers.add_parser("list", help="List recent leases")
    list_parser.add_argument("--namespace", choices=["session", "td", "cs"], default=None)
    list_parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.command == "peek":
        info = peek_next_id(args.namespace)
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(info["formatted_id"])
        return 0

    elif args.command == "claim":
        res = claim_next_id(args.namespace, title=args.title, agent_id=args.agent)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res["formatted_id"])
        return 0

    elif args.command == "list":
        leases = list_leases(args.namespace)
        if args.json:
            print(json.dumps(leases, indent=2))
        else:
            if not leases:
                print("No recorded leases in database.")
            else:
                for lease in leases:
                    print(f"[{lease['formatted_id']}] ({lease['namespace']}) - {lease['title'] or 'No title'} (by {lease['agent_id']})")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
