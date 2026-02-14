---
code: "417"
name: "Adaptive Latency Principle"
category: engineering
tags: [performance, latency, flow-state, efficiency]
status: active
created: 2026-02-08
---

# Protocol 417: Adaptive Latency Principle

> **Core Maxim**: Maximize quality while minimizing latency—except when explicitly opting into deeper reasoning.

## The Principle

Athena operates in three distinct phases, each with different latency tolerances:

| Phase | User State | Latency Tolerance | Priority |
|-------|------------|-------------------|----------|
| **Start-up** | Initiating session | **Low** (seconds matter) | Speed to "Ready" |
| **Working (Flow)** | In active focus | **Minimal** (sub-second ideal) | Zero disruption |
| **Shutdown** | Wrapping up | **High** (minutes acceptable) | Thorough closure |

## Design Implications

### 1. Start-up Phase

- Heavy imports **MUST** be lazy-loaded
- Health checks run in background threads
- "Ready" prompt appears before all checks complete
- Goal: Sub-5-second user-perceived boot time

### 2. Working Phase (Flow State)

- All disk IO should be non-blocking (background threads)
- Synchronous network calls are **prohibited** in hot paths
- Use cached data where possible; refresh asynchronously
- Quicksave and checkpoints must be instantaneous
- **Exception**: User explicitly invokes `think` or `ultrathink` commands

### 3. Shutdown Phase

- Slower operations are acceptable (user is done working)
- Session synthesis, learning propagation, and integrity checks can block
- Thoroughness > Speed

## Explicit Opt-In for Deep Reasoning

The user may invoke slower, deeper reasoning modes via:

| Command | Behavior |
|---------|----------|
| `think` | Extended reasoning, accepts ~10-30s latency |
| `ultrathink` | Maximum depth, accepts minutes of latency |

When these are NOT invoked, Athena defaults to **Bionic Mode**: fast, utility-maximizing responses.

## Technical Implementation

Refer to the efficiency optimizations in:

- `src/athena/memory/vectors.py` — Background embedding cache saves
- `src/athena/core/config.py` — Cached project root discovery
- `src/athena/sessions/__init__.py` — Lazy YAML loading
- `.agent/scripts/quicksave.py` — Deferred heavy imports
- `src/athena/boot/orchestrator.py` — Parallelized boot sequence

## Related Protocols

- **Protocol 166**: Deep Think Proxy (Committee of Seats for complex tasks)
- **Protocol 28**: Three-Second Override (fast corrections)

---

## Tagging

# efficiency #performance #flow-state #latency
