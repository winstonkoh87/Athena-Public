---

created: 2025-12-23
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-23
last_updated: 2025-12-23
---

# Protocol 142: Metaphorical Design Injection (Flash UI)

> **Source**: "Flash UI" (Google AI Studio / Amaresi) via YouTube Transcript (Dec 2025)
> **Domain**: UI/UX Design, Prompt Engineering, Latent Space Manipulation
> **Purpose**: Break the "Generic Bootstrap/Shadcn" aesthetic by forcing the LLM to hallucinate physical materials before writing code.

---

## 1. The Core Problem: The "Generic Web" Trap

When you ask an LLM for a "Login Page," it accesses the `Web Design` cluster in its latent space.

- **Result**: Generic cards, standard shadows, "Bootstrap" feel.
- **Reason**: The training data is dominated by average web frameworks.

## 2. The Solution: Two-Part Metaphor Injection

You must force the model to access a **Physical/Material** cluster first, then *translate* that into CSS. This creates novel, "Alien" interfaces.

### The Algorithm

#### Step 1: The Concept Generator (The Director)

**Goal**: Generate a string of physical, atmospheric, or textured adjectives.
**Prompt**: "Create a futuristic/ancient/organic style name and description."
**Output Example**:
> "Serrated obsidian monolith with bioluminescent membrane viscosity."

#### Step 2: The Code Generator (The Engineer)

**Goal**: Translate physics to CSS.
**Prompt**: "Use the specified metaphor to drive every CSS choice. Pair bold sans serif with refined monospace. Return only HTML."

---

## 3. The Implementation (Flash UI Template)

### Prompt A (Concept)

```text
Generate 3 distinct, high-fidelity UI concepts for a [COMPONENT].
For each, provide:
1. A poetic, material-heavy Name (e.g., "Brushed Tantalum", "Neon Viscosity").
2. A description of the "Physics" of the UI (lighting, texture, weight).
```

### Prompt B (Execution)

```text
Build the [COMPONENT] using the concept: [SELECTED_CONCEPT].
Rules:
1. MATERIALITY: Use the metaphor to drive border-radius, box-shadow, and gradients.
2. TYPOGRAPHY: Pair [FONT_A] with [FONT_B].
3. MOTION: Subtle CSS animations that match the "weight" of the material.
4. NO PLACEHOLDERS: Generate specific, thematic content.
5. IP SAFEGUARD: No trademarks.
6. OUTPUT: Single HTML file with embedded CSS.
```

---

## 4. Why It Works (Latent Space Physics)

- **Standard Prompt**: `Login Form` -> `div.card` -> `box-shadow: 0 2px 4px rgba(0,0,0,0.1)`.
- **Metaphor Prompt**: `Obsidian` -> `black glass` -> `backdrop-filter: blur(20px)` -> `border: 1px solid rgba(255,255,255,0.1)`.

By priming with *Material*, you unlock "High-End" design patterns that are usually tagged with "Concept Art" or "Awwwards" in the training set.

---

## Tagging

# protocol #design #prompt-engineering #flash-ui #ui-ux #latent-space
