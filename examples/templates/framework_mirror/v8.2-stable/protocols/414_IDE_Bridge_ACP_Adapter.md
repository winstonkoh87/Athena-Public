---
protocol_id: 414
title: "IDE Bridge (ACP Adapter)"
version: "1.0"
status: DRAFT
created: 2026-02-02
source: "OpenClaw (openclaw/openclaw)"
category: integration
---

# Protocol 414: IDE Bridge (ACP Adapter)

> **Origin**: Stolen from OpenClaw's ACP stdio bridge pattern
> **Purpose**: Use Athena as the backend for IDE AI agents (Zed, Cursor, VSCode)

---

## Context

Modern IDEs have AI agent integration:

- Zed: Agent panel with ACP support
- Cursor: Built-in AI chat
- VSCode: Copilot Chat

OpenClaw's `openclaw acp` command bridges these IDEs to its gateway via stdio. We can do the same.

## Architecture

```
┌─────────────────────────────────────────────┐
│                 IDE (Zed)                   │
│  ┌─────────────────────────────────────┐    │
│  │        Agent Panel / Chat           │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼───────────────────────────┘
                  │ ACP (NDJSON over stdio)
                  ▼
┌─────────────────────────────────────────────┐
│           athena acp (CLI Bridge)           │
│  ┌─────────────────────────────────────┐    │
│  │  • Translate ACP → Athena API       │    │
│  │  • Manage session mapping           │    │
│  │  • Stream responses back            │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼───────────────────────────┘
                  │ HTTP/WebSocket
                  ▼
┌─────────────────────────────────────────────┐
│         Athena Gateway (Future)             │
│  OR                                          │
│         Direct LLM API Call                  │
└─────────────────────────────────────────────┘
```

## ACP Protocol (Minimal Surface)

Messages are NDJSON (newline-delimited JSON) over stdio:

```json
// Request (IDE → athena acp)
{"id": "1", "method": "prompt", "params": {"message": "explain this code"}}

// Response (athena acp → IDE)
{"id": "1", "result": {"content": "This code does..."}}

// Streaming (athena acp → IDE)
{"id": "1", "stream": true, "delta": "This "}
{"id": "1", "stream": true, "delta": "code "}
{"id": "1", "stream": true, "delta": "does..."}
{"id": "1", "done": true}

// Cancel (IDE → athena acp)
{"id": "1", "method": "cancel"}
```

## Implementation

### 1. CLI Entry Point

```bash
# Start ACP bridge
athena acp

# With session key
athena acp --session agent:main:main

# With custom model
athena acp --model claude-3-opus
```

### 2. Bridge Script

```typescript
// .agent/scripts/acp-bridge.ts
import { createInterface } from 'readline';
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();
const rl = createInterface({ input: process.stdin });

rl.on('line', async (line) => {
  const msg = JSON.parse(line);
  
  if (msg.method === 'prompt') {
    // Stream response
    const stream = await client.messages.stream({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      messages: [{ role: 'user', content: msg.params.message }],
      system: loadAthenaSystemPrompt()
    });
    
    for await (const event of stream) {
      if (event.type === 'content_block_delta') {
        console.log(JSON.stringify({
          id: msg.id,
          stream: true,
          delta: event.delta.text
        }));
      }
    }
    
    console.log(JSON.stringify({ id: msg.id, done: true }));
  }
  
  if (msg.method === 'cancel') {
    // Abort current request
    stream.controller.abort();
  }
});

function loadAthenaSystemPrompt(): string {
  // Load Core_Identity.md + relevant protocols
  return fs.readFileSync('.framework/v8.2-stable/modules/Core_Identity.md', 'utf-8');
}
```

### 3. Zed Configuration

```json
// ~/.config/zed/settings.json
{
  "agent_servers": {
    "Athena": {
      "type": "custom",
      "command": "athena",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

## Session Mapping

ACP session IDs map to Athena session keys:

| ACP Session | Athena Session |
|-------------|----------------|
| `acp:<uuid>` | Auto-generated, isolated |
| `agent:main:main` | Primary agent session |
| `agent:code:feature-x` | Feature-specific session |

## Future: Gateway Integration

When Athena has a gateway (like OpenClaw):

```bash
athena acp --url wss://athena.local:18789 --token $ATHENA_TOKEN
```

## Current Limitation

This is a **DRAFT** protocol. Current implementation:

- Direct API calls (no gateway yet)
- Single-session only
- No persistence across IDE restarts

## Related Protocols

- Protocol 166 (Proxy Engine — for multi-agent routing)
- Protocol 410 (Agent Status Broadcasting)

---

# protocol #integration #ide #acp #bridge #stolen/openclaw
