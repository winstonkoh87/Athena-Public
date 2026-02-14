---
protocol_id: 412
title: "DM Pairing Gate"
version: "1.0"
status: ACTIVE
created: 2026-02-02
source: "OpenClaw (openclaw/openclaw)"
category: security
---

# Protocol 412: DM Pairing Gate

> **Origin**: Stolen from OpenClaw's DM pairing security pattern
> **Purpose**: Prevent unauthorized users from interacting with Athena bots

---

## Context

When Athena's Telegram bot is deployed, unknown users can DM it. Without authentication:

- Prompt injection attacks possible
- Resource exhaustion (token costs)
- Privacy leaks

**Solution**: Require pairing code approval before ANY message processing.

## Flow

```
┌─────────────────┐
│ Unknown Sender  │
│ sends message   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Is sender in    │ NO  │ Generate 6-char │
│ allowlist?      ├────►│ pairing code    │
└────────┬────────┘     └────────┬────────┘
         │ YES                   │
         │                       ▼
         │              ┌─────────────────┐
         │              │ Reply: "🔐 Code:│
         │              │ ABC123. Ask     │
         │              │ owner to approve"│
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ Process message │     │ DO NOT PROCESS  │
│ normally        │     │ (Drop silently) │
└─────────────────┘     └─────────────────┘
```

## Implementation

### 1. Allowlist Storage

```python
# ~/.athena/pairing/allowlist.json
{
  "telegram": {
    "123456789": {  # user_id
      "username": "[AUTHOR]",
      "approved_at": "2026-02-02T23:10:00+08:00",
      "approved_by": "owner"
    }
  },
  "discord": {},
  "slack": {}
}
```

### 2. Pending Codes

```python
# ~/.athena/pairing/pending.json
{
  "ABC123": {
    "channel": "telegram",
    "user_id": "987654321",
    "username": "unknown_user",
    "requested_at": "2026-02-02T23:11:00+08:00",
    "message_preview": "Hey can you help me..."
  }
}
```

### 3. Bot Handler

```python
# telegram_bot.py enhancement
import json
import secrets
from pathlib import Path
from datetime import datetime

ALLOWLIST_FILE = Path.home() / ".athena" / "pairing" / "allowlist.json"
PENDING_FILE = Path.home() / ".athena" / "pairing" / "pending.json"

def generate_pairing_code() -> str:
    return secrets.token_hex(3).upper()  # 6-char hex

def is_allowlisted(channel: str, user_id: str) -> bool:
    if not ALLOWLIST_FILE.exists():
        return False
    data = json.loads(ALLOWLIST_FILE.read_text())
    return user_id in data.get(channel, {})

async def handle_dm(update, context):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    
    if not is_allowlisted("telegram", user_id):
        code = generate_pairing_code()
        
        # Save pending
        PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        pending = json.loads(PENDING_FILE.read_text()) if PENDING_FILE.exists() else {}
        pending[code] = {
            "channel": "telegram",
            "user_id": user_id,
            "username": username,
            "requested_at": datetime.now().isoformat(),
            "message_preview": update.message.text[:100]
        }
        PENDING_FILE.write_text(json.dumps(pending, indent=2))
        
        await update.message.reply_text(
            f"🔐 Pairing required.\n\n"
            f"Code: `{code}`\n\n"
            f"Ask the owner to run:\n"
            f"`athena pairing approve {code}`",
            parse_mode="Markdown"
        )
        return  # DO NOT process
    
    # Process normally
    await process_message(update, context)
```

### 4. CLI Commands

```bash
# List pending pairing requests
athena pairing list

# Approve a request
athena pairing approve ABC123

# Revoke access
athena pairing revoke telegram 123456789

# Approve all (dangerous!)
athena pairing approve-all
```

### 5. Approval Script

```python
# .agent/scripts/pairing.py
import argparse
import json
from pathlib import Path
from datetime import datetime

ALLOWLIST_FILE = Path.home() / ".athena" / "pairing" / "allowlist.json"
PENDING_FILE = Path.home() / ".athena" / "pairing" / "pending.json"

def approve(code: str):
    pending = json.loads(PENDING_FILE.read_text()) if PENDING_FILE.exists() else {}
    
    if code not in pending:
        print(f"❌ Code {code} not found")
        return
    
    req = pending.pop(code)
    
    # Add to allowlist
    allowlist = json.loads(ALLOWLIST_FILE.read_text()) if ALLOWLIST_FILE.exists() else {}
    if req['channel'] not in allowlist:
        allowlist[req['channel']] = {}
    
    allowlist[req['channel']][req['user_id']] = {
        "username": req['username'],
        "approved_at": datetime.now().isoformat(),
        "approved_by": "owner"
    }
    
    ALLOWLIST_FILE.write_text(json.dumps(allowlist, indent=2))
    PENDING_FILE.write_text(json.dumps(pending, indent=2))
    
    print(f"✅ Approved {req['username']} ({req['user_id']}) on {req['channel']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("code")
    
    # ... more subcommands
    
    args = parser.parse_args()
    if args.command == "approve":
        approve(args.code)
```

## Security Considerations

- Pairing codes expire after 24 hours
- Rate limit code generation (max 3 per user per hour)
- Log all approval/revocation events
- Owner's Telegram ID auto-allowlisted on bot creation

## DM Policy Modes

| Mode | Behavior |
|------|----------|
| `pairing` (default) | Require code approval |
| `open` | Allow all DMs (dangerous) |
| `closed` | Ignore all DMs |
| `allowlist-only` | Only pre-approved users |

## Related Protocols

- Protocol 413 (Multi-Agent Coordination)
- Law #3 (Protect from Irreversible Ruin)

---

# protocol #security #pairing #authentication #stolen/openclaw
