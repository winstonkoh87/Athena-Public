---
type: protocol
id: 109
title: Cyclic Graph State
created: 2026-02-14
source: LangGraph Architecture
tags: [architecture, agent, state, graph]
author: Athena (via LangGraph)
---

## Protocol 109: Cyclic Graph State

> **Philosophy**: "Agents are not scripts; they are loops."
> **Origin**: Adapted from **LangGraph** (LangChain AI).
> **Purpose**: To model complex agent behaviors (retries, self-correction, human-in-the-loop) as explicit State Graphs.

## 1. The Graph Metaphor

An agent is defined by:

1. **State**: A shared data schema (The "Memory").
2. **Nodes**: Functions that modify the State (The "Actions").
3. **Edges**: Logic that determines the next Node (The "Router").

### 1.1 The State Schema

Every graph MUST define a strictly typed State.

```python
class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    outcome: str | None
    errors: list[str]
    steps: int
```

## 2. Standard Nodes

### The `Agent` Node

- **Input**: Current State.
- **Action**: Calls the LLM to decide the next step.
- **Output**: Returns an `AgentAction` or `AgentFinish`.

### The `Tool` Node

- **Input**: `AgentAction` from the State.
- **Action**: Executes the tool.
- **Output**: Updates `chat_history` with the tool result.

### The `Reflector` Node (Self-Correction)

- **Input**: `outcome` + `errors`.
- **Action**: Analyzes failure.
- **Output**: Updates `input` with correction instructions.

## 3. Standard Edges (The Control Flow)

### The Conditional Edge

Use `router` functions to determine the next node dynamically.

```python
def should_continue(state):
    if state["steps"] > 10:
        return "end"
    if "error" in state:
        return "reflector"
    return "tools"
```

## 4. The Human-in-the-Loop Pattern

To implement Law #4 (User Sovereignty), insert a `HumanCritique` node before critical actions.

1. **Agent** proposes action.
2. **Edge** checks `is_sensitive(action)`.
3. **True** -> Route to `HumanCritique`.
4. **False** -> Route to `Tool`.

## 5. Application

Use this protocol when designing **Autonomous Agents** that need to operate for long periods or handle failure gracefully. Do NOT use for simple one-shot tasks (use Linear Scripts for that).
