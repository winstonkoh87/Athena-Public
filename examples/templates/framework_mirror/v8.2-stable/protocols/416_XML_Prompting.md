# Protocol 416: XML Prompting (Anti-Degradation Shield)

**Version**: 1.0
**Status**: Active
**Origin**: Stolen from `NullzInc` (r/ClaudeAI, 2026-02-03)
**Trigger**: Model degradation detected OR context adherence failures

---

## 1. Purpose

When LLMs are "lobotomized" (e.g., during pre-launch compute reallocation or A/B testing), they lose the ability to track loose context cues (Markdown, natural language headers).

**XML tags** provide a structural "anchor" that is harder for a degraded model to ignore.

This protocol defines how to structure prompts using XML to maximize instruction adherence during unstable periods.

---

## 2. Core Principle

> **"If the model can't follow vibes, give it rails."**

XML tags (`<task>`, `<context>`, `<constraints>`) create **hard boundaries** in the prompt that are less susceptible to context drift.

---

## 3. The XML Template

### 3.1 Standard Request Format

```xml
<request>
  <context>
    <!-- Background information, files read, prior decisions -->
  </context>
  
  <task>
    <!-- The specific action to perform. One task per request. -->
  </task>
  
  <constraints>
    <!-- Hard rules that MUST be followed -->
    <constraint>Do not modify files outside of /src</constraint>
    <constraint>Preserve existing comments</constraint>
  </constraints>
  
  <output_format>
    <!-- Expected structure of the response -->
    <format>code_block</format>
    <language>python</language>
  </output_format>
</request>
```

### 3.2 Multi-Step Request Format

```xml
<workflow>
  <step id="1">
    <action>Read file</action>
    <target>/path/to/file.py</target>
  </step>
  <step id="2" depends="1">
    <action>Refactor function</action>
    <target>calculate_total</target>
    <constraints>
      <constraint>Maintain existing API signature</constraint>
    </constraints>
  </step>
  <step id="3" depends="2">
    <action>Run tests</action>
    <command>pytest tests/</command>
  </step>
</workflow>
```

---

## 4. When to Activate

| Signal | Action |
|--------|--------|
| Model repeatedly ignores instructions | Switch to XML format |
| Context adherence drops (<70% accuracy) | Activate XML Shield |
| Pre-launch period detected (community chatter) | Preemptive XML |
| Session context exceeds 50k tokens | Hard reset + XML |

---

## 5. XML vs Markdown Comparison

| Aspect | Markdown | XML |
|--------|----------|-----|
| Human Readability | High | Medium |
| Model Adherence (Stable) | High | High |
| Model Adherence (Degraded) | **Low** | **High** |
| Parsing Consistency | Variable | Strict |
| Use Case | Vibes, Creative | Critical, Structured |

---

## 6. Integration with Athena

### 6.1 Prompt Templates

All critical prompt templates (e.g., `identity_prompt`, `tool_dispatch`) should have an **XML variant** that can be activated via flag.

```python
# Example: Dynamic Format Selection
def get_prompt(task: str, xml_mode: bool = False) -> str:
    if xml_mode:
        return f"<task>{task}</task>"
    else:
        return f"## Task\n{task}"
```

### 6.2 Auto-Detection

If the model fails to follow an instruction 2+ times in a row, the system should automatically switch to XML mode for that session.

---

## 7. Caveats

1. **Not a Silver Bullet**: XML helps, but a truly degraded model will still fail.
2. **Token Overhead**: XML tags add ~5-10% token overhead. Acceptable for stability.
3. **Human Readability**: XML is less pleasant for humans. Use sparingly.

---

## 8. References

- [Reddit Thread: Opus 4.5 Degradation](https://old.reddit.com/r/ClaudeAI/) (2026-02-03)
- [Anthropic Docs: Use XML Tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Intel: intel_opus_degradation.md](file:///Users/[AUTHOR]/Desktop/Project%20Athena/.context/research/intel_opus_degradation.md)
