# 🎬 Live Demo Guide

> See Athena in action. This guide walks through a complete session lifecycle.

---

## Prerequisites

1. Clone the repo: `git clone https://github.com/the authorkoh87/Athena-Public.git`
2. Set up environment: `cp .env.example .env` and add your API keys
3. Install dependencies: `pip install -e .`

---

## The Core Loop: `/start` → Work → `/end`

### Step 1: Boot the System

```bash
python3 .agent/scripts/boot.py
```

**What happens:**

```
🚀 ATHENA BOOT SEQUENCE v9.9.9
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/7] ⏱️  Watchdog activated
[2/7] 🔄 System sync complete
[3/7] ✅ Semantic prime verified (SHA-384)
[4/7] 📝 Session created: 2026-01-08-session-01
[5/7] 🧠 Context captured
[6/7] 🔍 Semantic memory primed
[7/7] 🏠 Identity loaded

⚡ ATHENA ONLINE | Session: 2026-01-08-01 | Boot: 4.2s
```

The boot sequence:

- Verifies core identity integrity via SHA-384 hash
- Recalls context from the last session
- Primes semantic memory with relevant protocols
- Creates a new session log

---

### Step 2: Semantic Search (Triple-Lock Step 1)

```bash
python3 .agent/scripts/smart_search.py "decision frameworks risk"
```

**Output:**

```
🔍 SMART SEARCH (Parallel Hybrid RRF): "decision frameworks risk"
============================================================

🏆 TOP 10 RESULTS:

  1. [HIGH] [RRF:0.0892] Protocol 124: SDR Calculator
     📁 .agent/skills/protocols/decision/124-sdr-calculator.md

  2. [HIGH] [RRF:0.0756] Protocol 001: Law of Ruin
     📁 .agent/skills/protocols/safety/001-law-of-ruin.md

  3. [HIGH] [RRF:0.0684] Case Study: CS-226 DCHTOONS Financial Model
     📁 .context/memories/case_studies/CS-226-dchtoons-financial-model.md
...
```

This searches across:

- Supabase pgvector (dense embeddings)
- Keyword/Tag index (exact match)
- Uses RRF (Reciprocal Rank Fusion) to combine results

---

### Step 3: Do Your Work

Interact with the AI using the retrieved context. The system tracks:

- What protocols were invoked
- What decisions were made
- What insights emerged

---

### Step 4: Quicksave (Triple-Lock Step 3)

```bash
python3 .agent/scripts/quicksave.py "Analyzed decision framework options. Selected SDR Calculator for risk assessment."
```

**Output:**

```
✅ Quicksave → 2026-01-08-session-01.md
```

This appends a checkpoint to your session log with timestamp and context.

---

### Step 5: End Session

```bash
python3 .agent/scripts/end_session.py
```

**What happens:**

- Session log finalized with summary
- New insights indexed for future retrieval
- Auto-commit to git (if configured)

---

## Dashboard Check

```bash
python3 .agent/scripts/athena_status.py
```

**Output:**

```
🏛️  PROJECT ATHENA | SYSTEM DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metrics:               Status:
  📂 Protocols:  431     🕒 Last Boot:  2026-06-06 14:06:00
  📝 Sessions:   1,900+  📍 Root:       Project Athena/
  ⚙️  Scripts:    247    🛡️  Integrity:  100%
  ❤️  Health:     98%    📁 Memory:     3,658 files

Recent Sessions:
  • 2026-01-08-session-01.md
  • 2026-01-07-session-21.md
  • 2026-01-07-session-20.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ System Active and Calibrated.
```

---

## Key Concepts Demonstrated

| Concept | What It Shows |
|---------|---------------|
| **Boot Sequence** | Integrity verification + context recall |
| **Semantic Search** | RAG with RRF fusion across multiple data sources |
| **Triple-Lock** | Enforced sequence: Search → Web → Save |
| **Session Logging** | Automatic persistence of decisions and insights |
| **Dashboard** | Real-time system health visibility |

---

## Video Walkthrough

*Coming soon: Loom recording of a full session lifecycle.*

---

*This is real code running in production. Not a mockup.*
