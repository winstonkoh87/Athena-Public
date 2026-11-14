# Athena Examples & Protocols

This directory contains executable examples, protocol specifications, templates, and reference workflows designed for Project Athena.

## 📁 Directory Structure

- [protocols/](protocols/) — Public reference protocols across Decision Science, Workflow Orchestration, Engineering, and Risk Management.
- [workflows/](workflows/) — Domain-specific slash-command execution plans and multi-turn workflows.
- [skills/](skills/) — Modular agent skills and `SKILL.md` capability packs.
- [scripts/](scripts/) — Reference automation scripts, gates, evaluators, and orchestration helpers.
- [engine/](engine/) — Minimal executable Python runtime examples and adapters.
- [framework/](framework/) — Core identity, system principles, and output-standard framework references.
- [templates/](templates/) — Structured templates for session logs, task tracking, pattern sheets (`PATTERN_EXAMPLE.md`), and decision registers.
- [agents/](agents/) — Sample autonomous agent configurations and persona cards.
- [case_studies/](case_studies/) — Sanitized case studies (`CASE_STUDY_EXAMPLE.md`) illustrating real-world application of cognitive protocols.
- [concepts/](concepts/) — Reference notes on key frameworks and mental models.
- [guides/](guides/) — Step-by-step setup and workflow adaptation guides.
- [hooks/](hooks/) — Reference IDE hook implementations (`UserPromptSubmit`, `Stop` verification gates).
- [quickstart/](quickstart/) — Minimal starter kits for trying Athena in an isolated folder.
- [tools/](tools/) — Declarative tool definitions and MCP/CLI specs (such as Exocortex search configs).
- [config/](config/) — Reference configuration and manifest templates (`public_manifest.example.yaml`).
- [demos/](demos/) — Interactive HTML demos (`demo.html`, `knowledge_graph_demo.html`), terminal capture script (`DEMO_SCRIPT.md`), analytics report, and visualizations.

## 🚀 Usage

Protocols in Athena are declarative markdown files with structured frontmatter that can be ingested by any LLM or IDE agent harness.

```bash
# Verify published examples syntax integrity
ruff check examples/ --select F821,F822,F823,E9
```
