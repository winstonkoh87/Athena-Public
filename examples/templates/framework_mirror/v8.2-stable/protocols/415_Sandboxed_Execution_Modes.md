---
protocol_id: 415
title: "Sandboxed Execution Modes"
version: "1.0"
status: ACTIVE
created: 2026-02-02
source: "OpenClaw (openclaw/openclaw)"
category: security
---

# Protocol 415: Sandboxed Execution Modes

> **Origin**: Stolen from OpenClaw's per-session Docker sandbox pattern
> **Purpose**: Isolate untrusted or client work from the main system

---

## Context

Not all contexts are equal:

- **Main session**: Full trust, full access
- **Client work**: Limited trust, scoped access
- **Untrusted requests**: Sandboxed, minimal permissions

OpenClaw runs non-main sessions in Docker containers. We adapt this for Athena.

## Sandbox Modes

| Mode | Trust Level | Access | Use Case |
|------|-------------|--------|----------|
| `none` | Full | Everything | Main agent on personal projects |
| `light` | High | No external API, no secrets | Client work |
| `docker` | Low | Container only, no host | Untrusted code review |
| `readonly` | Minimal | Read only, no writes | Analysis mode |

## Configuration

```yaml
# .athena/settings.yaml
sandbox:
  default_mode: none
  
  rules:
    - match: "client:*"
      mode: light
      deny: [secrets, external_api, git_push]
    
    - match: "untrusted:*"
      mode: docker
      allow: [bash, read, edit]
      deny: [browser, network, git]
    
    - match: "analysis:*"
      mode: readonly
      allow: [read, search]
      deny: [write, bash, git]
```

## Permission Matrix

| Permission | none | light | docker | readonly |
|------------|------|-------|--------|----------|
| File read | ✅ | ✅ | ✅ | ✅ |
| File write | ✅ | ✅ | ✅ | ❌ |
| Bash commands | ✅ | ✅ | ✅ | ❌ |
| Git operations | ✅ | ✅ | ❌ | ❌ |
| Network access | ✅ | ❌ | ❌ | ❌ |
| Secrets access | ✅ | ❌ | ❌ | ❌ |
| Browser | ✅ | ✅ | ❌ | ❌ |
| External APIs | ✅ | ❌ | ❌ | ❌ |

## Implementation

### 1. Mode Detection

```python
# .agent/scripts/sandbox.py
import os
from pathlib import Path
import yaml

def get_sandbox_mode(session_key: str) -> str:
    """Determine sandbox mode for a session."""
    config_path = Path(".athena/settings.yaml")
    if not config_path.exists():
        return "none"  # Default to full access
    
    config = yaml.safe_load(config_path.read_text())
    
    for rule in config.get("sandbox", {}).get("rules", []):
        pattern = rule["match"]
        if fnmatch.fnmatch(session_key, pattern):
            return rule["mode"]
    
    return config.get("sandbox", {}).get("default_mode", "none")
```

### 2. Permission Enforcement

```python
class SandboxEnforcer:
    def __init__(self, mode: str):
        self.mode = mode
        self.permissions = PERMISSION_MATRIX[mode]
    
    def check_permission(self, action: str) -> bool:
        return self.permissions.get(action, False)
    
    def enforce(self, action: str):
        if not self.check_permission(action):
            raise PermissionError(
                f"Action '{action}' denied in sandbox mode '{self.mode}'"
            )
```

### 3. Docker Sandbox (for `docker` mode)

```dockerfile
# .athena/sandbox/Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m sandboxuser
USER sandboxuser
WORKDIR /sandbox

# No network access
# No host volume mounts except /sandbox
# No secrets

COPY --chown=sandboxuser:sandboxuser . /sandbox
CMD ["python3", "-m", "athena.sandbox_runner"]
```

```bash
# Run sandboxed session
docker run --rm -it \
  --network none \
  --read-only \
  --tmpfs /tmp \
  -v $(pwd):/sandbox:ro \
  athena-sandbox
```

## Session Key Patterns

| Pattern | Mode | Notes |
|---------|------|-------|
| `main:*` | none | Full trust |
| `client:*` | light | No secrets/network |
| `untrusted:*` | docker | Container isolation |
| `analysis:*` | readonly | Read-only analysis |
| `proxy:*` | light | Proxy mode drafting |

## Activation

Sandbox mode is determined by:

1. Session key prefix (e.g., `client:leon`)
2. Explicit flag (`--sandbox docker`)
3. Config file rule match

## Integration with Boot

```python
# boot.py enhancement
session_key = get_current_session_key()
sandbox_mode = get_sandbox_mode(session_key)

if sandbox_mode != "none":
    print(f"🔒 Sandbox mode: {sandbox_mode}")
    enforcer = SandboxEnforcer(sandbox_mode)
    inject_enforcer(enforcer)
```

## Related Protocols

- Protocol 412 (DM Pairing Gate — outer defense)
- Protocol 413 (Multi-Agent Coordination — parallel safety)
- Law #3 (Protect from Irreversible Ruin)

---

# protocol #security #sandbox #isolation #stolen/openclaw
