---
description: Save/load session presets for consistent configuration (Protocol 411)
---

# Session Preset Workflow

Save and restore session configurations for repeatable setups.

## Usage

```bash
# Save current session as a preset
/preset save <name>

# Load a preset
/preset load <name>

# List available presets
/preset list

# Delete a preset
/preset delete <name>
```

## Steps

### List Presets

// turbo

1. Check existing presets:

```bash
ls -la ~/.athena/presets/
```

### Save Preset

1. When user runs `/preset save <name>`:
   - Capture current session configuration:
     - Model in use
     - Active skills
     - MCP servers
     - Sandbox mode
     - Custom instructions
   - Save to `~/.athena/presets/<name>.json`

// turbo

```bash
cat > ~/.athena/presets/<name>.json << 'EOF'
{
  "name": "<name>",
  "created_at": "$(date -Iseconds)",
  "model": "claude-3-opus",
  "skills": ["trading-executor", "github"],
  "mcp_servers": ["broker-api"],
  "sandbox_mode": "light",
  "custom_instructions": ""
}
EOF
```

### Load Preset

1. When user runs `/preset load <name>`:
   - Read `~/.athena/presets/<name>.json`
   - Apply configuration to current session
   - Report what was loaded

### Preset Structure

```json
{
  "name": "trading",
  "created_at": "2026-02-02T23:20:00+08:00",
  "description": "Trading session with broker integration",
  "model": "claude-3-opus",
  "skills": ["trading-executor", "risk-calculator"],
  "mcp_servers": ["broker-api", "market-data"],
  "sandbox_mode": "light",
  "session_key_prefix": "trading:",
  "environment": {
    "MARKET_ENV": "paper"
  },
  "custom_instructions": "Always confirm before executing trades"
}
```

## Built-in Presets

| Preset | Description |
|--------|-------------|
| `default` | Standard session, no restrictions |
| `client` | Light sandbox, no secrets access |
| `research` | Read-only mode for analysis |
| `coding` | Full access for development |

## Origin

**Stolen from**: Maestro's session templating feature
**Protocol**: 411 (Dynamic Skill Injection)

---

# workflow #preset #session #stolen/maestro
