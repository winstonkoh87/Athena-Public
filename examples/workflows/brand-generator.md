---created: 2025-12-31
last_updated: 2026-01-30
---

---description: The "Agency Killer" workflow. Replicates a $10k Branding Package in ~20 minutes using AI.
created: 2025-12-31
last_updated: 2026-01-05
---

# Brand Generator Workflow (Agency Arbitrage)

> **Purpose**: Deconstruct and replicate the output of a "Full Branding Agency" (Strategy + Identity + Assets) using the Bionic Stack.  
> **Value**: $10,000 (Agency Rate) vs ~$0 (AI Rate).  
> **Time**: ~20 Minutes.

---

## Phase 0: Brand DNA Extraction (Optional - Pomelli Method)

> **Source**: [CS-212 (Google Pomelli)](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS-212-google-pomelli-brand-dna.md)
> **Best for**: Existing businesses needing a refresh.

**Goal**: Extract "Business DNA" from an existing URL.
**Tool**: Google Labs (Pomelli)

1. **Input**: Enter client URL into Pomelli.
2. **Output**: Auto-generated Brand DNA (Colors, Font, Tone).
3. **Action**: Copy this DNA into Phase 1 below.

---

## Phase 1: Strategic DNA (The "Director")

**Goal**: Generate the intellectual IP (Mission, Values, Voice, Archetype).  
**Tool**: Athena (Claude 3.5 Sonnet / Gemini 1.5 Pro).

**Prompt**:
> "Act as a world-class Brand Strategist (Ogilvy/Pentagram level). I am building a brand called [NAME] for [AUDIENCE]. It needs to feel [VIBE].
>
> Generate a comprehensive **Brand DNA Document**:
>
> 1. **Brand Archetype**: (e.g., The Ruler, The Magician)
> 2. **Mission Statement**: Analysis of the 'Why'.
> 3. **Voice & Tone**: 3 adjectives with 'Do/Don't' examples.
> 4. **Visual Direction**: A precise prompts for a logo designer (minimalist, geometry, color palette in Hex codes)."

---

## Phase 2: Visual Synthesis (The "Designer")

**Goal**: Generate high-fidelity logo concepts.  
**Tool**: Athena (`generate_image`) or Midjourney / Flux.

**Action**:
Take the **Visual Direction** from Phase 1 and run:

> "Generate a vector-style logo for [NAME]. [VISUAL DIRECTION]. Minimalist flat design, white background, high contrast, Paul Rand style. No text, just the mark."

* *Tip*: Generate 4-8 variations. Pick the best one.

---

## Phase 3: Asset Refining (The "Technician")

**Goal**: Turn a "dumb" pixel image into a "professional" vector asset.  
**Tool**: [Vectorizer.ai](https://vectorizer.ai) (Free Beta) or Illustrator.

**Steps**:

1. Save the chosen logo image.
2. Upload to **Vectorizer.ai**.
3. Download as **SVG** (Scalable Vector Graphic).
4. *Optional*: Use **Recraft.ai** to generate matching icon sets.

---

## Phase 4: The Brand Book (The "Deliverable")

**Goal**: Package it into the $10k PDF.  
**Tool**: Gamma.app (AI Slides) or Canva.

**Steps**:

1. Go to **Gamma.app**.
2. Paste the **Brand DNA** (Phase 1) text.
3. Upload the **Logo** (Phase 3).
4. Prompt: "Create a minimalist, luxury Brand Guideline document."
5. Export as **PDF**.

---

## Summary of Arbitrage

| Component | Agency Timeline | Agency Cost | Your Timeline | Your Cost |
| :--- | :--- | :--- | :--- | :--- |
| Strategy | 1 Week | $3,000 | 5 Mins | $0 |
| Logo Design | 2 Weeks | $4,000 | 5 Mins | $0 |
| Vector Assets | 3 Days | $1,500 | 2 Mins | $0 |
| Brand Book | 1 Week | $1,500 | 5 Mins | $0 |
| **TOTAL** | **4 Weeks** | **$10,000** | **~20 Mins** | **$0** |
