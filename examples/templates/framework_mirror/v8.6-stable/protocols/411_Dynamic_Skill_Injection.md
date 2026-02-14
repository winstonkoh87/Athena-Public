---
protocol_id: 411
title: "Dynamic Skill Injection"
version: "2.0"
status: ACTIVE
created: 2026-02-02
updated: 2026-02-04
source: "Maestro (its-maestro-baby/maestro) + Vercel AGENTS.md Research"
category: skills
---

# Protocol 411: Dynamic Skill Injection (v2.0)

> **Origin**: Stolen from Maestro's plugin symlink injection pattern
> **Update v2.0**: Integrated Vercel's "Passive Context" findings (Jan 2026)
> **Purpose**: Load skills dynamically per-session without bloating base context

---

## Critical Insight (Vercel Research)

> **"Skills aren't being triggered reliably."**
> In Vercel's evals, agents failed to invoke skills 56% of the time even when available.
> **Root Cause**: Agents don't know **when** or **why** to use skills.
> **Solution**: Mandatory 5W1H metadata + Passive Context indexing.

---

## 5W1H Skill Metadata (MANDATORY)

Every skill MUST include explicit answers to these questions in its `SKILL.md`:

| Question | Frontmatter Key | Purpose |
| :------- | :-------------- | :------ |
| **Who** | `target_agent` | Which agent type should use this? |
| **What** | `description` | What exactly does this skill do? |
| **When** | `trigger_conditions` | Under what EXACT conditions should this be invoked? |
| **Where** | `file_paths` | What files does this skill reference/modify? |
| **Why** | `rationale` | Why is this skill better than training data? |
| **How** | `invocation_example` | What's the exact invocation pattern? |

### Example SKILL.md (5W1H Compliant)

```yaml
---
name: trading-executor
version: "1.0"
status: ACTIVE

# WHO: Target agent type
target_agent: "Any agent handling financial transactions"

# WHAT: Description
description: "Execute trades on various exchanges with risk management"

# WHEN: Trigger conditions (be EXHAUSTIVE)
trigger_conditions:
  - "User mentions: buy, sell, long, short + any ticker symbol"
  - "User asks to execute a trade or position"
  - "User mentions: DCA, dollar cost average"
  - "Context contains: trading strategy, portfolio rebalance"
  - "Slash command: /trade"

# WHERE: File paths this skill touches
file_paths:
  - ".context/trades/"
  - ".context/portfolio.json"
  - "protocols/301_Risk_Assessment.md"

# WHY: Rationale for using this skill
rationale: |
  Training data does not include:
  - Current exchange API schemas
  - User's specific risk parameters
  - Live position data
  Skill provides real-time, user-specific execution logic.

# HOW: Invocation example
invocation_example: |
  User: "Buy 0.1 BTC at market"
  Agent: [Detects trigger: "buy" + "BTC"]
  Agent: [Loads trading-executor skill]
  Agent: [Reads user's risk parameters from .context/]
  Agent: [Executes trade via MCP broker-api]

dependencies:
  - protocols/301_Risk_Assessment.md
  - protocols/302_Position_Sizing.md
mcp_servers:
  - broker-api
---

# Trading Executor Skill

[Full skill content here...]
```

---

## Passive Context Integration (AGENTS.md)

Per Vercel research, skills perform better when agents don't need to *decide* to use them.

### Strategy 1: Skill Index in AGENTS.md

Add compressed skill index to `AGENTS.md`:

```text
[Athena Skills Index]|root: .agent/skills
|IMPORTANT: Check trigger_conditions before invoking any skill.
|trading-executor:{SKILL.md,scripts/execute_trade.py}|triggers:buy,sell,trade,DCA
|moltbook:{SKILL.md}|triggers:/moltbook,post to moltbook
|fantasy-detection:{SKILL.md}|triggers:unknown framework,new library
```

### Strategy 2: Trigger Conditions in Boot Context

During `/start`, inject trigger conditions summary:

```text
## Active Skills & Triggers

| Skill | Invoke When... |
|:------|:---------------|
| trading-executor | User mentions buy/sell/trade + ticker |
| moltbook | User mentions posting to social network |
| fantasy-detection | Unknown framework mentioned |
```

---

## Implementation

### 1. Skill Discovery (Updated)

```python
# .agent/scripts/skill_loader.py
def discover_skills():
    """Discover all available skills with 5W1H metadata."""
    skills = {}
    for base in SKILL_PATHS:
        for skill_dir in base.glob("*/"):
            manifest = skill_dir / "SKILL.md"
            if manifest.exists():
                content = manifest.read_text()
                if content.startswith("---"):
                    _, fm, body = content.split("---", 2)
                    meta = yaml.safe_load(fm)
                    
                    # Validate 5W1H compliance
                    required = ['target_agent', 'description', 'trigger_conditions', 
                                'file_paths', 'rationale', 'invocation_example']
                    missing = [k for k in required if k not in meta]
                    if missing:
                        print(f"⚠️  Skill {meta.get('name', skill_dir)} missing: {missing}")
                    
                    skills[meta['name']] = {
                        **meta,
                        'path': str(manifest),
                        'compliant': len(missing) == 0
                    }
    return skills
```

### 2. Trigger Detection (Enhanced)

```python
def detect_skills_for_message(message: str, skills: dict) -> list:
    """Return skills whose trigger_conditions match the message."""
    matched = []
    for name, skill in skills.items():
        for condition in skill.get('trigger_conditions', []):
            if condition.startswith('/'):
                # Slash command
                if message.strip().startswith(condition):
                    matched.append(name)
            elif condition.lower() in message.lower():
                # Keyword match
                matched.append(name)
    return list(set(matched))
```

### 3. Injection at Runtime

When skill detected:

1. Load `SKILL.md` content into context
2. Spawn any required MCP servers
3. Load dependency protocols

```python
def inject_skill(skill_name: str, context: list) -> list:
    """Inject skill content into agent context."""
    skill = SKILLS[skill_name]
    skill_content = Path(skill['path']).read_text()
    
    # Add to context with explicit invocation guidance
    context.append({
        "role": "system",
        "content": f"""# Skill Activated: {skill_name}

## Trigger Rationale
{skill.get('rationale', 'N/A')}

## How to Use
{skill.get('invocation_example', 'N/A')}

---

{skill_content}"""
    })
    
    # Load dependencies
    for dep in skill.get('dependencies', []):
        dep_content = Path(dep).read_text()
        context.append({
            "role": "system",
            "content": dep_content
        })
    
    return context
```

---

## Directory Structure

```
.agent/skills/
├── trading-executor/
│   ├── SKILL.md          # Must be 5W1H compliant
│   ├── scripts/
│   │   └── execute_trade.py
│   └── examples/
├── moltbook/
│   ├── SKILL.md
│   └── ...
└── SKILL_INDEX.md        # Auto-generated index
```

---

## Skill Index Auto-Generation

```bash
# Regenerate skill index with 5W1H validation
python3 .agent/scripts/skill_loader.py --index > .agent/skills/SKILL_INDEX.md

# Validate all skills for 5W1H compliance
python3 .agent/scripts/skill_loader.py --validate
```

---

## Anti-Patterns (Avoid)

| ❌ Don't | ✅ Do Instead |
| :------- | :------------ |
| Vague triggers: "trading" | Explicit triggers: "buy + ticker, sell + ticker" |
| Missing rationale | Explain WHY this beats training data |
| No invocation example | Show exact user→agent flow |
| Rely on agent to "figure it out" | Prescribe exact conditions |

---

## Related Protocols

- Protocol 400 (Semantic Search — finds relevant protocols)
- Protocol 410 (Agent Status — broadcasts skill loading)
- AGENTS.md (Passive context for skill awareness)

---

## Changelog

- **v2.0** (2026-02-04): Added 5W1H mandatory metadata, Vercel research integration
- **v1.0** (2026-02-02): Initial version from Maestro pattern

---

# protocol #skills #injection #dynamic #stolen/maestro #5W1H #vercel
