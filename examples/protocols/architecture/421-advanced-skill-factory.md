---
created: 2026-02-13
last_updated: 2026-02-13
tags: [architecture, skill-engineering, protocols, mcp]
---

# Protocol 421: Advanced Skill Factory (The Claude Standard)

> **Source**: "The Complete Guide to Building Skills for Claude" (Anthropic, 2025)
> **Status**: ACTIVE
> **Purpose**: Professional standard for high-complexity skill engineering.

---

## 1. The Philosophy: "Containment & Hooks"

Simple prompts remain in `.agent/prompts/`.
**Skills** are full-fledged software modules. They must be:

1. **contained**: All resources (templates, lists, data) live with the skill.
2. **driven**: Logic is separated from data.
3. **hooked**: Automation triggers (MCP, pre/post) are explicit.

---

## 2. The Four-Part Anatomy

A "Professional Skill" is not just a Markdown file. It is a directory structure (conceptual or physical).

### 2.1 Logic (`SKILL.md`)

The "Brain". Pure instructions.

- **DO**: "Read `resources/template.json` and fill it."
- **DON'T**: "Here is the template: { ... }" (Waste of tokens).

### 2.2 Resources (`/resources`)

The "Body". Static assets loaded *on demand*.

- Templates (Jinja2, Handlebars)
- Reference lists (CSV, JSON)
- Few-shot examples (txt)

### 2.3 Interfaces (`/interfaces`)

The "Hands". How it touches the world.

- **MCP Server Config**: `mcp_config.json` snippet.
- **API Schemas**: OpenAPI specs.

### 2.4 Hooks (`/hooks`)

The "Nerves". Automation triggers.

- `pre-tool`: Validate input before sending.
- `post-tool`: Log output or trigger follow-up.

---

## 3. The Directory Standard

For complex skills, create a dedicated folder in `.agent/skills/<domain>/<skill-name>/`:

```text
.agent/skills/
└── domain/
    └── my-complex-skill/
        ├── SKILL.md          # Entry point (The "Instruction")
        ├── README.md         # Context for the Agent
        ├── resources/        # Static files (Load via read_file)
        │   ├── template.j2
        │   └── examples.json
        ├── interfaces/       # Connectors
        │   └── mcp-server/   # Source code or config
        └── hooks/            # Automation
            └── validate.py
```

---

## 4. The "Hydration" Workflow (How to Build)

**Goal**: Transform a vague request into a shipping container of capability.

### Step 1: define the `interface` (Capabilities)

What tools does this require?

- Existing tools? (Search, File Ops)
- New MCP tools? (Database, API) -> **Define Schema first.**

### Step 2: Extract `resources` (Context)

What static data is bloating the prompt?

- Move long examples to `resources/examples.md`.
- Move strict formats to `resources/schema.json`.
- **Rule**: If it doesn't change, it doesn't belong in the logic flow.

### Step 3: Write the `logic` (SKILL.md)

The orchestration layer.
"To execute [Skill]:

1. Read `resources/schema.json`.
2. Call tool `mcp_server_tool` with arguments matching schema.
3. Validate result using `hooks/validate.py`."

### Step 4: Bind `hooks` (Automation)

- **Pre-execution**: Check auth, check safety.
- **Post-execution**: Log to `memory_bank`, auto-format output.

---

## 5. Integration with MCP (Model Context Protocol)

When a skill requires an MCP server, strict binding is required.

**In `SKILL.md`**:

```markdown
## Tool Requirements
This skill requires the `sqlite` MCP server.
See `interfaces/mcp_config.json` for installation.
```

**In `interfaces/mcp_config.json`**:
Standard MCP configuration block to be merged into global config.

---

## 6. Maintenance & Versioning

- **Version**: Semantic (1.0.0).
- **Changelog**: Keep inside `README.md`.
- **Deprecation**: specific `DEPRECATED` flag in frontmatter.

---

## Tagging

# architecture #skill-engineering #mcp #standard
