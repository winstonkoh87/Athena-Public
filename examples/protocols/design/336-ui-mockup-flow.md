---
created: 2026-01-07
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: skill-ui-design-mockup
description: Standardized flow for moving from vague UI ideas to polished code via mockups and critiques. Used when "Make it pretty" or "Refactor this panel" is requested.
created: 2026-01-07
last_updated: 2026-01-07
---

# 🎨 Skill: UI Mockup → Code Flow

> **Source**: Inspired by `u/neamtuu` on r/google_antigravity (Jan 2026)

## When to Trigger

- User wants to refactor a "bare-bones" UI.
- New feature requires a specific visual look.
- Request for "polished", "modern", or "premium" aesthetics.

## Core Protocol

### Phase 1: The Design Critique

Don't write code yet. Analyze the current state and identify "vibe gaps":

- Typography (Default vs. Custom)
- Spacing (Cramped vs. Intentional)
- Color Palette (Generic vs. Harmonious)
- Components (Primitive vs. Polished Cards/Modules)

### Phase 2: The Mockup Generation

Use the `generate_image` tool or create an ASCII/Markdown mockup to align on direction.

- **Goal**: Show, don't just tell.
- **Instruction**: "I will generate a mockup of the proposed look. Please review before I implement."

### Phase 3: The Implementation (Opus/Gemini High)

Once the mockup is approved, use the strongest reasoning model available to:

- Implement Vanilla CSS (or Tailwind if requested).
- Ensure responsiveness.
- Add micro-animations (hover transitions, lazy-loading fades).

## Engineering Edge Cases

- **Theme Switching**: Does it work in Dark/Light mode?
- **Mobile Fidelity**: How does it look on a 375px screen?
- **Accessibility**: Are contrast ratios compliant?

## Resources

- See `.agent/skills/protocols/content/221-high-performance-ux-design.md` for architectural principles.

---
**Tags**: #protocol #ui-design #ux-design #frontend-development #mockup #workflow #software-engineering
