---
created: 2025-12-15
last_updated: 2026-07-22
---

# Protocol 79: Vibe Engineering

> **Purpose**: To maximize AI-Human high-bandwidth collaboration ("Vibe Engineering") while minimizing "Slot Machine" coding ("Vibe Coding").
> **Source**: Synthesized from Alex Finn ("Claude Code Lessons") and Kitze ("From Vibe Coding to Vibe Engineering").
> **Trigger**: `/vibe` or complex implementation tasks.

---

## 1. Core Philosophy: Engineering > Coding

| Vibe Coding (Gambling) 🎰 | Vibe Engineering (Architecture) 🏗️ |
|--------------------------|------------------------------------|
| "Fix this error" | "Here is the error trace + relevant file. Diagnosis?" |
| "Make it look cool" | "Here is a screenshot. Replicate this exact gradient." |
| Scrolling TikTok while AI loads | **Parallel Brainstorming** (Co-Pilot Mode) |
| Accepting the first output | **The 20% Rule** (Steering the final mile) |

## 1.1 The Vibe Gap: Discovery vs. Durability
>
> **Source**: r/vibecoding (The "Base64 Incident")
> **Insight**: Vibe Coding optimizes for "It Works Now." Engineering optimizes for "It Works at Scale."

**The Trap**:
The AI will default to the path of least resistance (e.g., hardcoding Base64 images into MongoDB) because it has no concept of *future* traffic costs.

**The Phase Shift**:

1. **Phase 1 (Vibe Mode)**: Build the feature. Ignore efficiency. Validate the "Vibe."
2. **Phase 2 (The Audit)**: Before production, ask: *"If 5,000 people use this, what breaks?"*
3. **Specific Checks**:
    - [ ] **Assets**: Are images hosted (S3/CDN) or hardcoded (Base64)?
    - [ ] **Database**: Are we fetching the whole collection or paginating?
    - [ ] **Security**: Are API keys in `.env` or hardcoded?

---

## 2. The Parallel Officer (Productive Downtime)

> **Rule**: 80% of "Vibe Coding" is waiting. Do not waste the wait.

**Trigger**: Anytime the AI is executing a long task (writing code, running tests, searching).

**The Pivot**:
Instead of idling, the **User** directs the **AI** (or a parallel chat instance) to switch context:

- *"While you write that, let's discuss the marketing strategy."*
- *"While tests run, critique my database schema."*
- *"While you index, give me life advice on [X]."*

**AI Response Pattern**:

- **Task A (Background)**: "Executing [Code Task]..."
- **Task B (Foreground)**: "Understood. Switching to CEO Mode. regarding the marketing strategy..."

---

## 3. The Brain Dump Interface

> **Rule**: The fastest input is voice/stream-of-consciousness. The best output is structured spec.

**Trigger**: User provides a messy, long, unstructured prompt (Voice-to-Text).

**AI Action**:

1. **Do NOT Execute immediately.**
2. **Parse**: Convert the "Brain Dump" into a **Pre-Flight Checklist** (See `Output_Standards.md §7`).
3. **Confirm**: "Here is the structured plan based on your dump. Correct?"

**Example**:
> **User**: "Okay so I want a button here that does this thing but maybe it should be blue no wait red and also it needs to call the API but only on Tuesdays..."
>
> **AI**:
> "Got it.
>
> 1. **Component**: Button (Red).
> 2. **Logic**: API Call (Conditional: Tuesday).
> 3. **Plan**: ...
> Proceed?"

---

## 4. The 20% Fixer (Steering)

> **Rule**: AI gets you 80% there. The last 20% requires Human Intelligence.

- **Expectation**: The code will not be perfect on the first shot.
- **Protocol**:
  - When 80% is done, **STOP**.
  - Ask User: "I have built the core. Please review the specific logic for [Edge Case]. Guide me on the final 20%."
  - Do not attempt to guess the final 20% (Business Logic/Taste).

---

## 5. Simplicity Prime

> **Rule**: If a junior developer cannot read it, it is bad code.

- **Ban**: Premature abstraction ("Make it generic just in case").
- **Enforce**: Copy-Paste > Wrong Abstraction.
- **Enforce**: Single Responsibility Principle.

---

---

## Tagging

# protocol #framework #process #79-vibe-engineering
