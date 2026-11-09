# Declarative Tools

> **Stolen from**: GitClaw's `tools/*.yaml` pattern
> **Status**: V1 — Schema defined, runtime integration pending

## Philosophy

Tools defined as YAML files are **self-documenting and discoverable**. The agent reads the directory, knows what's available, and can invoke them without hardcoded routing.

This complements Athena's existing skill system:

- **Skills** = instruction modules (how to think about a problem)
- **Tools** = executable capabilities (what the agent can do)

## How to Add a Tool

Create a `.yaml` file in this directory:

```yaml
# tools/search_docs.yaml
name: search_docs
description: Search the Exocortex knowledge base
input_schema:
  properties:
    query:
      type: string
      description: Natural language search query
    limit:
      type: number
      description: Maximum results to return
      default: 5
  required: [query]
implementation:
  script: ../scripts/smart_search.py
  runtime: python3
  args: ["{query}", "--limit", "{limit}"]
```

## Schema Reference

| Field | Required | Description |
|:------|:---------|:------------|
| `name` | ✅ | Unique tool identifier |
| `description` | ✅ | What the tool does (shown to agent) |
| `input_schema` | ✅ | JSON Schema for tool arguments |
| `implementation.script` | ✅ | Path to script (relative to tools/) |
| `implementation.runtime` | ❌ | Execution runtime (`python3`, `sh`, `node`) |
| `implementation.args` | ❌ | Argument template with `{param}` substitution |

## Built-in Tools

These are hardcoded in the agent runtime and don't need YAML definitions:

| Tool | Description |
|:-----|:------------|
| `cli` | Shell command execution |
| `read` | File reading with pagination |
| `write` | File creation/modification |
| `search` | Exocortex semantic search |
| `memory` | Quicksave / session logging |
| `browser` | Web page interaction |
