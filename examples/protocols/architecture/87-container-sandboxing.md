---

created: 2025-12-16
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-16
last_updated: 2026-01-11
---

# Protocol 87: Container Sandboxing

> **Source**: Harvested from `ykdojo/claude-code-tips` (Dec 2025)
> **Use Case**: Long-running, risky, or autonomous tasks

---

## Core Philosophy

> "Running with dangerous permissions is like unprotected sex. Use a condo... I mean container."

Containerization provides:

- **Isolation**: Mistakes don't escape the sandbox
- **Reproducibility**: Same environment every time
- **Disposability**: Nuke and restart cleanly

---

## When to Use

| Scenario | Container? |
|----------|-----------|
| Risky automated scripts | ✅ Yes |
| GraphRAG reindexing | 🟡 Optional |
| Multi-model orchestration | ✅ Yes |
| Normal development | ❌ No |
| Research with unknown APIs | ✅ Yes |

---

## Architecture Pattern

```
┌─────────────────────────────────────────┐
│  Host Machine                           │
│  ┌───────────────────────────────────┐  │
│  │  Docker Container                 │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  AI Agent (autonomous)      │  │  │
│  │  │  - Full permissions         │  │  │
│  │  │  - Can't escape sandbox     │  │  │
│  │  └─────────────────────────────┘  │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  tmux (orchestration layer) │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Host AI ←── Controls container via     │
│              tmux send-keys / capture   │
└─────────────────────────────────────────┘
```

---

## Implementation

### Basic Dockerfile

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    python3 python3-pip git tmux curl
# Add AI CLI tools as needed
WORKDIR /workspace
```

### Orchestration via tmux

```bash
# Start container with tmux
docker run -it --name sandbox my-ai-container

# From host, send commands:
docker exec sandbox tmux send-keys "python script.py" Enter

# Capture output:
docker exec sandbox tmux capture-pane -p
```

---

## Multi-Model Orchestration

Use containers to run different AI CLIs:

- Primary AI orchestrates
- Secondary AI (Gemini, Codex, etc.) runs in container
- Primary sends tasks via tmux → captures results

**Pattern**: Hub-and-spoke with container isolation.

---

## Safety Rules

## Safety Rules (Hardened by OpenClaw Patterns)

1. **Mount only necessary volumes**: Never mount `$HOME`. Mount specific workspace subdirs only.
2. **Network Isolation**:
    - **High Risk** (Malware analysis, unknown script): `--network none`
    - **Medium Risk** (Web scraping): Whitelist specific domains (if possible) or use a sidecar proxy.
3. **Resource Limits**:
    - `--memory=512m` (Prevent OOM denial of service)
    - `--cpus="1.0"` (Prevent CPU starvation of host)
4. **Session Isolation (The OpenClaw Rule)**:
    - Each "risky" session gets its *own* ephemeral container.
    - Container dies when session ends.
    - Shared state must be explicitly "committed" via API back to the host; everything else in the container is wiped.
5. **Syscall Filtering**: Use seccomp profiles to block dangerous syscalls in untrusted containers.

---

## Integration

- Works with: Infrastructure & Continuity Hub (Exponential Backoff for monitoring)
- Complements: Protocol 85 (Token Hygiene — containers can run while you start fresh)

---

## Tags

# container #docker #sandboxing #automation #harvested

---

## Tagging

# protocol #framework #process #87-container-sandboxing
