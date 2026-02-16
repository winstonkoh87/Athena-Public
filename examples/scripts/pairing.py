#!/usr/bin/env python3
"""
DM Pairing Gate (Protocol 412)

Approval system for unknown senders on messaging channels.

Usage:
    python3 pairing.py list           # List pending requests
    python3 pairing.py approve <code> # Approve a request
    python3 pairing.py revoke <channel> <user_id>  # Revoke access
    python3 pairing.py allowlist      # Show allowlist
"""

import json
import secrets
import sys
from pathlib import Path
from datetime import datetime

PAIRING_DIR = Path.home() / ".athena" / "pairing"
ALLOWLIST_FILE = PAIRING_DIR / "allowlist.json"
PENDING_FILE = PAIRING_DIR / "pending.json"


def ensure_files():
    """Ensure pairing files exist."""
    PAIRING_DIR.mkdir(parents=True, exist_ok=True)
    if not ALLOWLIST_FILE.exists():
        ALLOWLIST_FILE.write_text("{}")
    if not PENDING_FILE.exists():
        PENDING_FILE.write_text("{}")


def generate_pairing_code() -> str:
    """Generate a 6-character pairing code."""
    return secrets.token_hex(3).upper()


def add_pending(
    channel: str, user_id: str, username: str, message_preview: str = ""
) -> str:
    """Add a pending pairing request. Returns the code."""
    ensure_files()

    code = generate_pairing_code()
    pending = json.loads(PENDING_FILE.read_text())

    pending[code] = {
        "channel": channel,
        "user_id": user_id,
        "username": username,
        "requested_at": datetime.now().isoformat(),
        "message_preview": message_preview[:100] if message_preview else "",
    }

    PENDING_FILE.write_text(json.dumps(pending, indent=2))
    return code


def list_pending():
    """List all pending pairing requests."""
    ensure_files()
    pending = json.loads(PENDING_FILE.read_text())

    if not pending:
        print("✅ No pending pairing requests")
        return

    print(f"🔐 Pending Pairing Requests ({len(pending)}):")
    print("-" * 50)

    for code, req in pending.items():
        print(f"  Code: {code}")
        print(f"    Channel:  {req['channel']}")
        print(f"    User:     {req['username']} ({req['user_id']})")
        print(f"    Since:    {req['requested_at']}")
        if req.get("message_preview"):
            print(f"    Preview:  {req['message_preview'][:50]}...")
        print()


def approve(code: str):
    """Approve a pending pairing request."""
    ensure_files()
    pending = json.loads(PENDING_FILE.read_text())

    if code not in pending:
        # Try case-insensitive match
        for c in pending:
            if c.upper() == code.upper():
                code = c
                break
        else:
            print(f"❌ Code '{code}' not found")
            list_pending()
            return

    req = pending.pop(code)

    # Add to allowlist
    allowlist = json.loads(ALLOWLIST_FILE.read_text())
    if req["channel"] not in allowlist:
        allowlist[req["channel"]] = {}

    allowlist[req["channel"]][req["user_id"]] = {
        "username": req["username"],
        "approved_at": datetime.now().isoformat(),
        "approved_by": "owner",
    }

    ALLOWLIST_FILE.write_text(json.dumps(allowlist, indent=2))
    PENDING_FILE.write_text(json.dumps(pending, indent=2))

    print(f"✅ Approved {req['username']} ({req['user_id']}) on {req['channel']}")


def revoke(channel: str, user_id: str):
    """Revoke access for a user."""
    ensure_files()
    allowlist = json.loads(ALLOWLIST_FILE.read_text())

    if channel not in allowlist or user_id not in allowlist[channel]:
        print(f"❌ User {user_id} not found in {channel} allowlist")
        return

    username = allowlist[channel][user_id].get("username", "unknown")
    del allowlist[channel][user_id]

    ALLOWLIST_FILE.write_text(json.dumps(allowlist, indent=2))
    print(f"🚫 Revoked access for {username} ({user_id}) on {channel}")


def show_allowlist():
    """Show the current allowlist."""
    ensure_files()
    allowlist = json.loads(ALLOWLIST_FILE.read_text())

    if not allowlist:
        print("📋 Allowlist is empty")
        return

    print("📋 Allowlist:")
    print("-" * 50)

    for channel, users in allowlist.items():
        print(f"\n  {channel}:")
        for user_id, info in users.items():
            print(f"    • {info.get('username', user_id)} ({user_id})")
            print(f"      Approved: {info.get('approved_at', 'unknown')}")


def is_allowlisted(channel: str, user_id: str) -> bool:
    """Check if a user is allowlisted."""
    ensure_files()
    allowlist = json.loads(ALLOWLIST_FILE.read_text())
    return user_id in allowlist.get(channel, {})


def main():
    if len(sys.argv) < 2:
        print("DM Pairing Gate (Protocol 412)")
        print("")
        print("Usage:")
        print("  pairing.py list             # List pending requests")
        print("  pairing.py approve <code>   # Approve a request")
        print("  pairing.py revoke <ch> <id> # Revoke access")
        print("  pairing.py allowlist        # Show allowlist")
        print("  pairing.py add <ch> <id> <name>  # Add pending (for testing)")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_pending()

    elif command == "approve":
        if len(sys.argv) < 3:
            print("❌ Usage: pairing.py approve <code>")
            sys.exit(1)
        approve(sys.argv[2])

    elif command == "revoke":
        if len(sys.argv) < 4:
            print("❌ Usage: pairing.py revoke <channel> <user_id>")
            sys.exit(1)
        revoke(sys.argv[2], sys.argv[3])

    elif command == "allowlist":
        show_allowlist()

    elif command == "add":
        if len(sys.argv) < 5:
            print("❌ Usage: pairing.py add <channel> <user_id> <username>")
            sys.exit(1)
        code = add_pending(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"🔐 Generated pairing code: {code}")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
