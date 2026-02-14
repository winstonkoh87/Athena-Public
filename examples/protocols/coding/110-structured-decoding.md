---
type: protocol
id: 110
title: Structured Decoding
created: 2026-02-14
source: SGLang Architecture
tags: [coding, generation, schema, validation]
author: Athena (via SGLang)
---

## Protocol 110: Structured Decoding

> **Philosophy**: "Output is not creating text; it is filling a form."
> **Origin**: Adapted from **SGLang** (Safe Generation Language).
> **Purpose**: To guarantee type safety and structural correctness of LLM outputs, replacing "Prompt Hope" with "Schema Enforcement".

## 1. The Schema Principle

Never ask for free-form text when the downstream consumer is a machine. Always define a Schema.

### Bad (Free-form)
>
> "Identify the sentiment of this text." -> "I think it is positive." (Difficult to parse)

### Good (Structured)
>
> "Identify the sentiment as JSON." -> `{"sentiment": "POSITIVE", "confidence": 0.95}` (Easy to parse)

## 2. Implementation Strategies

### 2.1 JSON Mode (Soft Constraint)

Most models support `response_format={"type": "json_object"}`.

- **Rule**: Always include the JSON schema in the system prompt.
- **Rule**: Use Pydantic or TypeScript interfaces to define the schema.

### 2.2 Grammar-Constrained Sampling (Hard Constraint)

For local models (llama.cpp, vLLM) or advanced providers (OpenAI Structured Outputs), use Context-Free Grammars (CFG) or Regex.

```python
# SGLang Example Pattern
s += "The sentiment is: "
s += select("sentiment", options=["positive", "negative", "neutral"])
```

## 3. The Decoding Pipeline

1. **Define**: Create a Pydantic model / TypeScript interface for the desired output.
2. **Prompt**: Explicitly inject the schema definition into the context.
3. **Constrain**: Use API parameters (`response_format`, `tools`) to force adherence.
4. **Validate**: Parse the output immediately. If it fails validation, **Retrying with Error Message** is mandatory (Self-Correction).

## 4. Standard Schemas

### Action Schema

```json
{
  "action": "run_command",
  "args": {
    "command": "ls -la"
  },
  "justification": "Checking directory contents."
}
```

### Reasoning Schema

```json
{
  "thought_process": "Step 1... Step 2...",
  "conclusion": "The error is in line 42.",
  "confidence_score": 0.8
}
```

## 5. When to Use

- **Always** for Tool Calls.
- **Always** for API responses.
- **Always** for critical logic decisions (e.g., Protocol 133 Routing).
- **Never** for creative writing or chat.
