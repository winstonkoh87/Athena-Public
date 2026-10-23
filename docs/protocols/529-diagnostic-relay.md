---
created: 2026-01-31
status: active
category: architecture
---

# Protocol 500: Self-Diagnostic Feedback Relay

> **Philosophy**: Federated Telemetry with Sovereignty (Privacy-First).

## Purpose

Enable Athena instances to self-diagnose framework errors and generate **sanitized GitHub issue drafts** for human-in-the-loop submission.

This transforms every production crash into a framework contribution while **respecting user privacy**.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Athena Instance (Local)                  │
├─────────────────────────────────────────────────────────────┤
│  1. Error Occurs → try/except catches exception             │
│  2. Diagnostic Capture → traceback + context                │
│  3. PII Sanitization → regex scrubber removes:              │
│     • /Users/<username>/ paths                              │
│     • Email addresses                                       │
│     • API keys (sk-*, supabase_*)                           │
│     • IP addresses                                          │
│  4. Issue Draft → Markdown file in .agent/diagnostics/      │
│  5. User Gate → Human reviews and decides to submit         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼ (Manual submission by user)
┌─────────────────────────────────────────────────────────────┐
│              GitHub: Athena-Public Issues                   │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Option 1: Decorator (Recommended)

```python
from athena.core.diagnostic_relay import diagnostic_wrapper

@diagnostic_wrapper("sync.py")
def sync_file_to_supabase(file_path, table_name):
    # If this raises, a diagnostic is auto-generated
    ...
```

### Option 2: Manual Relay

```python
from athena.core.diagnostic_relay import relay_error

try:
    risky_operation()
except Exception as e:
    relay_error(
        e,
        context={"table_name": "sessions", "file_path": "example.md"},
        module_name="sync.py"
    )
    raise  # Re-raise after capturing
```

## Output

Diagnostics are saved to:

```
.agent/diagnostics/issue-YYYYMMDD-HHMMSS-ExceptionType.md
```

Each file contains:

- Athena version
- Python version & OS
- Sanitized exception message
- Sanitized traceback
- Context (table name, etc.)

## Privacy Guarantees

The following patterns are automatically redacted:

| Pattern | Example | Replacement |
|---------|---------|-------------|
| User paths | `/Users/winston/` | `/Users/<REDACTED>/` |
| Emails | `user@example.com` | `<EMAIL_REDACTED>` |
| API Keys | `sk-abc123...` | `<API_KEY_REDACTED>` |
| IP Addresses | `192.168.1.1` | `<IP_REDACTED>` |

## Air-Gapped by Default

**No data is auto-transmitted.**

The diagnostic is saved locally. The user must:

1. Review the draft
2. Copy/paste to GitHub Issues
3. Or delete if they prefer not to share

This preserves **Sovereignty** while enabling **Swarm Intelligence**.

---

**Tags**: #protocol #architecture #privacy #diagnostics
